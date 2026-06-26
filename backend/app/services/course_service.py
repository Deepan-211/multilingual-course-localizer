"""Course upload and management business logic."""

import io
from datetime import UTC, datetime, timedelta
from uuid import UUID

from fastapi import HTTPException, UploadFile, status
from pypdf import PdfReader

from app.schemas.course import CourseCreateResponse, CourseResponse, RecentCourseResponse
from app.schemas.localization import ActivityDayResponse, DashboardStatsResponse
from app.services.supabase_service import SupabaseService


class CourseService:
    """Course CRUD and content extraction."""

    ALLOWED_EXTENSIONS = {".pdf", ".mp4", ".mov", ".avi", ".webm", ".mkv"}

    def __init__(self) -> None:
        self.db = SupabaseService()

    async def upload_course(
        self,
        user_id: UUID,
        title: str,
        source_language: str,
        content_type: str,
        file: UploadFile,
    ) -> CourseCreateResponse:
        """Upload a course file and persist metadata."""
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="File name is required",
            )

        ext = "." + file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
        if ext not in self.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Unsupported file type. Allowed: {', '.join(self.ALLOWED_EXTENSIONS)}",
            )

        file_bytes = await file.read()
        if not file_bytes:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Uploaded file is empty",
            )

        local_path, public_url = await self.db.upload_file(file_bytes, file.filename, user_id)

        course = await self.db.insert(
            "courses",
            {
                "user_id": str(user_id),
                "title": title,
                "source_language": source_language,
                "content_type": content_type,
                "file_url": public_url,
                "file_name": file.filename,
                "file_size": len(file_bytes),
                "local_file_path": local_path,
            },
        )

        text = await self.extract_text(content_type, file_bytes, file.filename)
        if text.strip():
            from app.services.claude_service import ClaudeService

            blocks = ClaudeService.split_into_blocks(text)
            for idx, block_text in enumerate(blocks, start=1):
                await self.db.insert(
                    "content_blocks",
                    {
                        "course_id": course["id"],
                        "block_number": idx,
                        "original_text": block_text,
                    },
                )

        return CourseCreateResponse(course_id=course["id"])

    async def extract_text(self, content_type: str, file_bytes: bytes, filename: str) -> str:
        """Extract text from uploaded PDF or video placeholder."""
        if content_type == "pdf" or filename.lower().endswith(".pdf"):
            return await self._extract_pdf_text(file_bytes)
        return (
            f"[Video content: {filename}]\n\n"
            "This course video has been uploaded for localization. "
            "Transcription content will be processed during localization."
        )

    async def _extract_pdf_text(self, file_bytes: bytes) -> str:
        """Extract text from a PDF file."""

        def _read() -> str:
            reader = PdfReader(io.BytesIO(file_bytes))
            pages = [page.extract_text() or "" for page in reader.pages]
            return "\n\n".join(pages)

        from app.database import run_sync

        return await run_sync(_read)

    async def list_courses(self, user_id: UUID) -> list[CourseResponse]:
        """Return all courses for a user."""
        courses = await self.db.select(
            "courses",
            {"user_id": str(user_id)},
            order_by="created_at",
            ascending=False,
        )
        result = []
        for course in courses:
            locs = await self.db.select(
                "localizations",
                {"course_id": course["id"]},
                order_by="created_at",
                ascending=False,
                limit=1,
            )
            loc_status = locs[0]["status"] if locs else None
            result.append(
                CourseResponse(
                    id=course["id"],
                    title=course["title"],
                    source_language=course["source_language"],
                    content_type=course["content_type"],
                    file_url=course.get("file_url"),
                    file_name=course.get("file_name"),
                    file_size=course.get("file_size"),
                    created_at=course["created_at"],
                    localization_status=loc_status,
                )
            )
        return result

    async def get_course(self, user_id: UUID, course_id: UUID) -> CourseResponse:
        """Return a single course if owned by the user."""
        course = await self.db.select_one(
            "courses",
            {"id": str(course_id), "user_id": str(user_id)},
        )
        if not course:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

        locs = await self.db.select(
            "localizations",
            {"course_id": str(course_id)},
            order_by="created_at",
            ascending=False,
            limit=1,
        )
        return CourseResponse(
            id=course["id"],
            title=course["title"],
            source_language=course["source_language"],
            content_type=course["content_type"],
            file_url=course.get("file_url"),
            file_name=course.get("file_name"),
            file_size=course.get("file_size"),
            created_at=course["created_at"],
            localization_status=locs[0]["status"] if locs else None,
        )

    async def delete_course(self, user_id: UUID, course_id: UUID) -> dict[str, str]:
        """Delete a course and related records."""
        course = await self.db.select_one(
            "courses",
            {"id": str(course_id), "user_id": str(user_id)},
        )
        if not course:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

        local_path = course.get("local_file_path")
        if local_path:
            await self.db.delete_local_file(local_path)

        locs = await self.db.select("localizations", {"course_id": str(course_id)})
        for loc in locs:
            await self.db.delete("translated_blocks", {"localization_id": loc["id"]})

        await self.db.delete("localizations", {"course_id": str(course_id)})
        await self.db.delete("content_blocks", {"course_id": str(course_id)})
        await self.db.delete("courses", {"id": str(course_id)})

        return {"message": "Course deleted successfully"}

    async def get_dashboard_stats(self, user_id: UUID) -> DashboardStatsResponse:
        """Compute dashboard summary statistics."""
        courses = await self.db.select("courses", {"user_id": str(user_id)})
        course_ids = [c["id"] for c in courses]

        if not course_ids:
            return DashboardStatsResponse(
                total_courses=0,
                languages_processed=0,
                localizations_completed=0,
                processing_in_queue=0,
            )

        all_locs: list[dict] = []
        for cid in course_ids:
            locs = await self.db.select("localizations", {"course_id": cid})
            all_locs.extend(locs)

        languages = {loc["target_language"] for loc in all_locs}
        completed = sum(1 for loc in all_locs if loc["status"] in ("completed", "approved"))
        queued = sum(1 for loc in all_locs if loc["status"] in ("queued", "processing"))

        return DashboardStatsResponse(
            total_courses=len(courses),
            languages_processed=len(languages),
            localizations_completed=completed,
            processing_in_queue=queued,
        )

    async def get_activity(self, user_id: UUID) -> list[ActivityDayResponse]:
        """Return localization counts per day for the last 7 days."""
        courses = await self.db.select("courses", {"user_id": str(user_id)})
        course_ids = {c["id"] for c in courses}

        today = datetime.now(UTC).date()
        days = [(today - timedelta(days=i)) for i in range(6, -1, -1)]
        counts = {d.isoformat(): 0 for d in days}

        for cid in course_ids:
            locs = await self.db.select("localizations", {"course_id": cid})
            for loc in locs:
                created = loc.get("created_at", "")[:10]
                if created in counts:
                    counts[created] += 1

        return [ActivityDayResponse(date=d, count=counts[d]) for d in counts]

    async def get_recent_courses(self, user_id: UUID, limit: int = 5) -> list[RecentCourseResponse]:
        """Return the most recently created courses with status."""
        courses = await self.db.select(
            "courses",
            {"user_id": str(user_id)},
            order_by="created_at",
            ascending=False,
            limit=limit,
        )
        result = []
        for course in courses:
            locs = await self.db.select(
                "localizations",
                {"course_id": course["id"]},
                order_by="created_at",
                ascending=False,
                limit=1,
            )
            result.append(
                RecentCourseResponse(
                    id=course["id"],
                    title=course["title"],
                    source_language=course["source_language"],
                    content_type=course["content_type"],
                    status=locs[0]["status"] if locs else "not_started",
                    created_at=course["created_at"],
                )
            )
        return result

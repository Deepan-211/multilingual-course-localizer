"""Localization job processing and workspace management."""

import asyncio
import io
from datetime import UTC, datetime
from uuid import UUID

from fastapi import HTTPException, status
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from app.schemas.localization import (
    AIStatusResponse,
    BlockUpdateRequest,
    ContentBlockResponse,
    ExportFormat,
    LibraryItemResponse,
    LibrarySearchResponse,
    LocalizationStartRequest,
    LocalizationStartResponse,
    LocalizationStatusResponse,
    ProgressItemResponse,
    TranslatedBlockResponse,
    WorkspaceBlockPair,
    WorkspaceResponse,
)
from app.services.claude_service import ClaudeService
from app.services.supabase_service import SupabaseService

# Track background tasks to avoid garbage collection
_background_tasks: set[asyncio.Task] = set()


class LocalizationService:
    """Orchestrates localization jobs, workspace, library, and exports."""

    def __init__(self) -> None:
        self.db = SupabaseService()
        self.claude = ClaudeService()

    async def _verify_course_owner(self, user_id: UUID, course_id: UUID) -> dict:
        """Ensure the course belongs to the user."""
        course = await self.db.select_one(
            "courses",
            {"id": str(course_id), "user_id": str(user_id)},
        )
        if not course:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
        return course

    async def start_localization(
        self, user_id: UUID, payload: LocalizationStartRequest
    ) -> LocalizationStartResponse:
        """Create localization jobs and process them in the background."""
        course = await self._verify_course_owner(user_id, payload.course_id)

        blocks = await self.db.select(
            "content_blocks",
            {"course_id": str(payload.course_id)},
            order_by="block_number",
            ascending=True,
        )
        if not blocks:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="No content blocks found. Re-upload the course or ensure text was extracted.",
            )

        localization_ids: list[UUID] = []
        for target_language in payload.target_languages:
            loc = await self.db.insert(
                "localizations",
                {
                    "course_id": str(payload.course_id),
                    "target_language": target_language,
                    "ai_model": payload.ai_model,
                    "status": "queued",
                    "progress_percentage": 0,
                },
            )
            localization_ids.append(loc["id"])

            task = asyncio.create_task(
                self._process_localization(
                    loc["id"],
                    course,
                    blocks,
                    target_language,
                    payload.ai_model,
                )
            )
            _background_tasks.add(task)
            task.add_done_callback(_background_tasks.discard)

        return LocalizationStartResponse(localization_ids=localization_ids)

    async def _process_localization(
        self,
        localization_id: UUID,
        course: dict,
        blocks: list[dict],
        target_language: str,
        ai_model: str,
    ) -> None:
        """Background task: translate all blocks for a localization job."""
        try:
            await self.db.update(
                "localizations",
                {"id": str(localization_id)},
                {"status": "processing", "progress_percentage": 0},
            )

            total = len(blocks)
            context = ""

            for idx, block in enumerate(blocks):
                result = await self.claude.translate_block(
                    text=block["original_text"],
                    source_language=course["source_language"],
                    target_language=target_language,
                    context=context,
                )
                context = result["translated_text"][:300]

                await self.db.insert(
                    "translated_blocks",
                    {
                        "block_id": block["id"],
                        "localization_id": str(localization_id),
                        "translated_text": result["translated_text"],
                        "confidence_score": result["confidence"],
                        "is_approved": False,
                    },
                )

                progress = int(((idx + 1) / total) * 100)
                await self.db.update(
                    "localizations",
                    {"id": str(localization_id)},
                    {"progress_percentage": progress},
                )

            await self.db.update(
                "localizations",
                {"id": str(localization_id)},
                {
                    "status": "completed",
                    "progress_percentage": 100,
                    "completed_at": datetime.now(UTC).isoformat(),
                },
            )
       except Exception as e:
            import traceback
            print("=========================================")
            print("🚨 CRITICAL TRANSLATION ERROR 🚨")
            traceback.print_exc() 
            print("=========================================")
            
            await self.db.update(
                "localizations",
                {"id": str(localization_id)},
                {"status": "failed"},
            )
            
            raise e

    async def get_status(self, user_id: UUID, localization_id: UUID) -> LocalizationStatusResponse:
        """Return processing status for a localization job."""
        loc = await self._get_owned_localization(user_id, localization_id)
        remaining_blocks = 100 - loc["progress_percentage"]
        estimated = remaining_blocks * 3 if loc["status"] == "processing" else 0

        return LocalizationStatusResponse(
            localization_id=loc["id"],
            status=loc["status"],
            progress_percentage=loc["progress_percentage"],
            estimated_time_seconds=estimated if estimated > 0 else None,
            target_language=loc["target_language"],
        )

    async def _get_owned_localization(self, user_id: UUID, localization_id: UUID) -> dict:
        """Fetch localization and verify ownership via course."""
        loc = await self.db.select_one("localizations", {"id": str(localization_id)})
        if not loc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Localization not found")

        await self._verify_course_owner(user_id, UUID(loc["course_id"]))
        return loc
    async def get_workspace(
        self, user_id: UUID, course_id: UUID, target_language: str | None = None
    ) -> WorkspaceResponse:
        """Return source and translated blocks side by side."""
        course = await self._verify_course_owner(user_id, course_id)

        content_blocks = await self.db.select(
            "content_blocks",
            {"course_id": str(course_id)},
            order_by="block_number",
            ascending=True,
        )

        loc_filters = {"course_id": str(course_id)}
        if target_language:
            loc_filters["target_language"] = target_language

        locs = await self.db.select(
            "localizations",
            loc_filters,
            order_by="created_at",
            ascending=False,
            limit=1,
        )

        translations_by_block: dict[str, dict] = {}
        if locs:
            translated = await self.db.select(
                "translated_blocks",
                {"localization_id": locs[0]["id"]},
            )
            translations_by_block = {t["block_id"]: t for t in translated}

        pairs: list[WorkspaceBlockPair] = []
        for block in content_blocks:
            source = ContentBlockResponse(
                id=block["id"],
                block_number=block["block_number"],
                original_text=block["original_text"],
            )
            trans_data = translations_by_block.get(block["id"])
            translation = None
            if trans_data:
                translation = TranslatedBlockResponse(
                    id=trans_data["id"],
                    block_id=trans_data["block_id"],
                    translated_text=trans_data["translated_text"],
                    confidence_score=trans_data["confidence_score"],
                    is_approved=trans_data.get("is_approved", False),
                )
            pairs.append(
                WorkspaceBlockPair(
                    block_number=block["block_number"],
                    source=source,
                    translation=translation,
                )
            )

        localization_id = locs[0]["id"] if locs else None

        return WorkspaceResponse(
            course_id=course["id"],
            course_title=course["title"],
            source_language=course["source_language"],
            localization_id=localization_id,
            blocks=pairs,
        )
    async def update_block(
        self, user_id: UUID, block_id: UUID, payload: BlockUpdateRequest
    ) -> TranslatedBlockResponse:
        """Manually update a translated block."""
        block = await self.db.select_one("translated_blocks", {"id": str(block_id)})
        if not block:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Block not found")

        await self._get_owned_localization(user_id, UUID(block["localization_id"]))
        updated = await self.db.update(
            "translated_blocks",
            {"id": str(block_id)},
            {"translated_text": payload.translated_text},
        )
        if not updated:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Block not found")

        return TranslatedBlockResponse(
            id=updated["id"],
            block_id=updated["block_id"],
            translated_text=updated["translated_text"],
            confidence_score=updated["confidence_score"],
            is_approved=updated.get("is_approved", False),
        )

    async def approve_localization(self, user_id: UUID, localization_id: UUID) -> dict[str, str]:
        """Approve all blocks and mark localization complete."""
        loc = await self._get_owned_localization(user_id, localization_id)

        blocks = await self.db.select("translated_blocks", {"localization_id": str(localization_id)})
        for block in blocks:
            await self.db.update(
                "translated_blocks",
                {"id": block["id"]},
                {"is_approved": True},
            )

        await self.db.update(
            "localizations",
            {"id": str(localization_id)},
            {
                "status": "approved",
                "progress_percentage": 100,
                "completed_at": loc.get("completed_at") or datetime.now(UTC).isoformat(),
            },
        )
        return {"message": "Localization approved and marked complete"}

    async def export_localization(
        self, user_id: UUID, localization_id: UUID, export_format: ExportFormat
    ) -> tuple[bytes, str, str]:
        """Export localized content as PDF or plain text."""
        loc = await self._get_owned_localization(user_id, localization_id)
        course = await self.db.select_one("courses", {"id": loc["course_id"]})

        blocks = await self.db.select(
            "translated_blocks",
            {"localization_id": str(localization_id)},
            order_by="created_at",
            ascending=True,
        )

        content_blocks = await self.db.select(
            "content_blocks",
            {"course_id": loc["course_id"]},
            order_by="block_number",
            ascending=True,
        )
        block_order = {b["id"]: b["block_number"] for b in content_blocks}
        blocks.sort(key=lambda b: block_order.get(b["block_id"], 0))

        text_parts = [b["translated_text"] for b in blocks]
        full_text = "\n\n".join(text_parts)
        title = course["title"] if course else "localized_course"
        safe_title = "".join(c if c.isalnum() or c in "-_" else "_" for c in title)

        if export_format == ExportFormat.TEXT:
            header = f"# {title}\nLanguage: {loc['target_language']}\n\n"
            return (header + full_text).encode("utf-8"), f"{safe_title}.txt", "text/plain"

        pdf_bytes = self._generate_pdf(title, loc["target_language"], full_text)
        return pdf_bytes, f"{safe_title}.pdf", "application/pdf"

    def _generate_pdf(self, title: str, language: str, content: str) -> bytes:
        """Generate a simple PDF from translated text."""
        buffer = io.BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        y = height - 72

        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(72, y, title[:80])
        y -= 24
        pdf.setFont("Helvetica", 10)
        pdf.drawString(72, y, f"Language: {language}")
        y -= 36

        pdf.setFont("Helvetica", 11)
        for line in content.split("\n"):
            if y < 72:
                pdf.showPage()
                pdf.setFont("Helvetica", 11)
                y = height - 72
            pdf.drawString(72, y, line[:90])
            y -= 14

        pdf.save()
        buffer.seek(0)
        return buffer.read()

    async def get_library(self, user_id: UUID) -> LibrarySearchResponse:
        """Return all completed localizations for the user."""
        return await self.search_library(user_id)

    async def search_library(
        self,
        user_id: UUID,
        query: str | None = None,
        language: str | None = None,
        status_filter: str | None = None,
    ) -> LibrarySearchResponse:
        """Search completed localizations with optional filters."""
        courses = await self.db.select("courses", {"user_id": str(user_id)})
        course_map = {c["id"]: c for c in courses}

        items: list[LibraryItemResponse] = []
        for course_id, course in course_map.items():
            if query and query.lower() not in course["title"].lower():
                continue

            locs = await self.db.select("localizations", {"course_id": course_id})
            for loc in locs:
                if language and loc["target_language"].lower() != language.lower():
                    continue
                if status_filter and loc["status"] != status_filter:
                    continue
                if loc["status"] not in ("completed", "approved") and not status_filter:
                    continue

                items.append(
                    LibraryItemResponse(
                        localization_id=loc["id"],
                        course_id=course["id"],
                        course_title=course["title"],
                        target_language=loc["target_language"],
                        status=loc["status"],
                        completed_at=loc.get("completed_at"),
                        created_at=loc["created_at"],
                    )
                )

        items.sort(key=lambda x: x.created_at, reverse=True)
        return LibrarySearchResponse(items=items, total=len(items))

    async def download_localization(
        self, user_id: UUID, localization_id: UUID
    ) -> tuple[bytes, str, str]:
        """Download localized content as text."""
        return await self.export_localization(user_id, localization_id, ExportFormat.TEXT)

    async def get_progress(self, user_id: UUID) -> list[ProgressItemResponse]:
        """Return active and queued localizations with progress."""
        courses = await self.db.select("courses", {"user_id": str(user_id)})
        items: list[ProgressItemResponse] = []

        for course in courses:
            locs = await self.db.select("localizations", {"course_id": course["id"]})
            for loc in locs:
                if loc["status"] in ("queued", "processing"):
                    items.append(
                        ProgressItemResponse(
                            localization_id=loc["id"],
                            course_id=course["id"],
                            course_title=course["title"],
                            target_language=loc["target_language"],
                            status=loc["status"],
                            progress_percentage=loc["progress_percentage"],
                            created_at=loc["created_at"],
                        )
                    )

        return items

    async def get_ai_status(self) -> AIStatusResponse:
        """Return Claude API health metrics."""
        data = ClaudeService.get_ai_status()
        return AIStatusResponse(**data)

        

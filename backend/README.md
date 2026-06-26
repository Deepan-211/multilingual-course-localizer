# Multilingual Content Localization Engine — Backend API

Production-ready FastAPI backend for AI-powered multilingual localization of skill course content.

## Tech Stack

- **Python 3.11+**
- **FastAPI** — async REST API
- **Supabase** — PostgreSQL database & file storage
- **Anthropic Claude** (`claude-sonnet-4-6`) — AI translation
- **JWT** — authentication (`python-jose`)
- **Passlib** — password hashing (bcrypt)
- **Pydantic v2** — request/response validation

## Quick Start

### 1. Clone and install

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

| Variable | Description |
|----------|-------------|
| `SUPABASE_URL` | Supabase project URL |
| `SUPABASE_KEY` | Supabase anon key |
| `SUPABASE_SERVICE_KEY` | Service role key (recommended for server) |
| `ANTHROPIC_API_KEY` | Anthropic API key |
| `JWT_SECRET` | Secret for signing JWT tokens |
| `FRONTEND_URL` | Frontend origin for CORS |

### 3. Set up Supabase

Run the SQL in [`supabase/schema.sql`](supabase/schema.sql) in the Supabase SQL Editor.

Create a storage bucket named `course-files` in the Supabase Dashboard.

### 4. Run the server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API docs: http://localhost:8000/docs

Health check: http://localhost:8000/health

## API Endpoints

### Auth (`/auth`)
| Method | Path | Description |
|--------|------|-------------|
| POST | `/auth/register` | Register (name, email, password) → JWT |
| POST | `/auth/login` | Login → JWT |
| GET | `/auth/me` | Current user profile |
| PUT | `/auth/profile` | Update name, avatar |
| POST | `/auth/change-password` | Change password |

### Dashboard (`/dashboard`)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/dashboard/stats` | Summary statistics |
| GET | `/dashboard/activity` | 7-day activity chart |
| GET | `/dashboard/recent` | Last 5 courses |

### Courses (`/courses`)
| Method | Path | Description |
|--------|------|-------------|
| POST | `/courses/upload` | Upload PDF/video (multipart) |
| GET | `/courses/` | List user courses |
| GET | `/courses/{course_id}` | Course details |
| DELETE | `/courses/{course_id}` | Delete course |

### Localization (`/localize`)
| Method | Path | Description |
|--------|------|-------------|
| POST | `/localize/start` | Start AI translation job |
| GET | `/localize/{id}/status` | Job status & progress |

### Workspace (`/workspace`)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/workspace/{course_id}` | Side-by-side editor view |
| PUT | `/workspace/block/{block_id}` | Edit translation |
| POST | `/workspace/{id}/approve` | Approve & complete |
| POST | `/workspace/{id}/export` | Export PDF or text |

### Library (`/library`)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/library` | Completed localizations |
| GET | `/library/search` | Search with filters |
| GET | `/library/{id}/download` | Download content |

### Progress (`/progress`)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/progress` | Active/queued jobs |
| GET | `/progress/ai-status` | Claude API metrics |

### Settings (`/settings`)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/settings` | User preferences |
| PUT | `/settings/language` | Default languages |
| PUT | `/settings/notifications` | Email preferences |

## Authentication

Protected routes require:

```
Authorization: Bearer <jwt_token>
```

## Project Structure

```
app/
  main.py              # FastAPI app, CORS, error handlers
  config.py            # Environment settings
  database.py          # Supabase client
  models/              # Domain models
  schemas/             # Pydantic request/response schemas
  routers/             # API route handlers
  services/            # Business logic
  middleware/          # JWT auth dependencies
supabase/schema.sql    # Database schema
requirements.txt
.env.example
```

## Error Responses

All errors return:

```json
{"detail": "Error message"}
```

| Status | Meaning |
|--------|---------|
| 401 | Unauthorized |
| 404 | Not found |
| 422 | Validation error |
| 500 | Server error |

## License

MIT

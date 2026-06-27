const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface DashboardStats {
  total_courses: number;
  languages_processed: number;
  localizations_completed: number;
  processing_in_queue: number;
}

export interface ActivityDay {
  date: string;
  count: number;
}

export interface DashboardActivity {
  activity: ActivityDay[];
}

export interface RecentCourse {
  id: string;
  title: string;
  source_language: string;
  content_type: string;
  status: string;
  created_at: string;
}

export interface AIStatus {
  status: string;
  avg_response_time_ms: number;
  current_load: number;
  model: string;
}

export interface HealthStatus {
  status: string;
  service: string;
}

export interface LibraryItem {
  localization_id: string;
  course_id: string;
  course_title: string;
  target_language: string;
  status: string;
  completed_at: string | null;
  created_at: string;
}

export interface LibraryResponse {
  items: LibraryItem[];
  total: number;
}

export interface ProgressItem {
  localization_id: string;
  course_id: string;
  course_title: string;
  target_language: string;
  status: string;
  progress_percentage: number;
  created_at: string;
}

async function parseResponse<T>(res: Response): Promise<T> {
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const detail = typeof data.detail === "string" ? data.detail : "Request failed";
    throw new Error(detail);
  }
  return data as T;
}

async function fetchWithAuth<T>(path: string, token: string): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return parseResponse<T>(res);
}

export const api = {
  // Auth
  register: async (name: string, email: string, password: string) => {
    const res = await fetch(`${API_URL}/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, email, password }),
    });
    return res.json();
  },

  login: async (email: string, password: string) => {
    const res = await fetch(`${API_URL}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    return res.json();
  },

  // Dashboard
  getStats: (token: string) => fetchWithAuth<DashboardStats>("/dashboard/stats", token),

  getActivity: (token: string) => fetchWithAuth<DashboardActivity>("/dashboard/activity", token),

  getRecentCourses: (token: string) =>
    fetchWithAuth<RecentCourse[]>("/dashboard/recent", token),

  getAiStatus: (token: string) => fetchWithAuth<AIStatus>("/progress/ai-status", token),

  getHealth: async () => {
    const res = await fetch(`${API_URL}/health`);
    return parseResponse<HealthStatus>(res);
  },

  getLibrary: (token: string) => fetchWithAuth<LibraryResponse>("/library", token),

  getProgress: (token: string) => fetchWithAuth<ProgressItem[]>("/progress", token),
};

export default API_URL;
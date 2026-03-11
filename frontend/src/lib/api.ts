const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function fetchApi<T>(
  path: string,
  options?: RequestInit
): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export async function sendChatMessage(
  userId: number,
  message: string,
  onChunk: (text: string) => void
): Promise<void> {
  const res = await fetch(`${API_BASE}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_id: userId, message }),
  });

  if (!res.ok) throw new Error(`Chat error: ${res.status}`);

  const reader = res.body?.getReader();
  if (!reader) return;

  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() || "";

    for (const line of lines) {
      if (line.startsWith("data: ")) {
        try {
          const data = JSON.parse(line.slice(6));
          if (data.type === "text") {
            onChunk(data.content);
          }
        } catch {
          // ignore parse errors
        }
      }
    }
  }
}

export interface User {
  id: number;
  role: string;
  patient_name: string | null;
  caregiver_name: string | null;
  diagnosis: string | null;
  doctor_name: string | null;
  clinic_name: string | null;
  onboarding_complete: boolean;
}

export interface CalendarDay {
  date: string;
  day_type: string;
  label: string | null;
  drug_name: string | null;
}

export interface WellbeingScore {
  id: number;
  score_type: string;
  score: number;
  notes: string | null;
  recorded_at: string;
}

export interface Appointment {
  id: number;
  user_id: number;
  appointment_date: string;
  appointment_type: string | null;
  doctor_name: string | null;
  prep_summary: string | null;
}

export async function createUser(
  role: string = "patient"
): Promise<User> {
  return fetchApi<User>("/api/users", {
    method: "POST",
    body: JSON.stringify({ role }),
  });
}

export async function getUser(userId: number): Promise<User> {
  return fetchApi<User>(`/api/users/${userId}`);
}

export async function getCalendar(
  userId: number,
  month?: number,
  year?: number
): Promise<CalendarDay[]> {
  const params = new URLSearchParams();
  if (month) params.set("month", month.toString());
  if (year) params.set("year", year.toString());
  return fetchApi<CalendarDay[]>(
    `/api/calendar/${userId}?${params.toString()}`
  );
}

export async function getWellbeing(
  userId: number,
  scoreType?: string,
  days: number = 30
): Promise<WellbeingScore[]> {
  const params = new URLSearchParams({ days: days.toString() });
  if (scoreType) params.set("score_type", scoreType);
  return fetchApi<WellbeingScore[]>(
    `/api/wellbeing/${userId}?${params.toString()}`
  );
}

export async function getAppointments(
  userId: number
): Promise<Appointment[]> {
  return fetchApi<Appointment[]>(`/api/appointments/${userId}`);
}

export async function getAppointmentPrep(
  userId: number,
  appointmentId: number
): Promise<{ prep_summary: string | null }> {
  return fetchApi<{ prep_summary: string | null }>(
    `/api/appointments/${userId}/${appointmentId}/prep`
  );
}

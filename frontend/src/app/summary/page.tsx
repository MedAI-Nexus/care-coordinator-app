"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Sidebar from "@/components/layout/Sidebar";
import ReactMarkdown from "react-markdown";
import {
  getAppointments,
  getAppointmentPrep,
  Appointment,
} from "@/lib/api";
import { FileText, Calendar, Loader2 } from "lucide-react";

export default function SummaryPage() {
  const [userId, setUserId] = useState<number | null>(null);
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [selectedPrep, setSelectedPrep] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [loadingPrep, setLoadingPrep] = useState(false);
  const router = useRouter();

  useEffect(() => {
    const id = localStorage.getItem("neuronav_user_id");
    if (!id) {
      router.push("/");
      return;
    }
    setUserId(parseInt(id));
  }, [router]);

  useEffect(() => {
    if (!userId) return;
    setLoading(true);
    getAppointments(userId)
      .then(setAppointments)
      .catch(() => setAppointments([]))
      .finally(() => setLoading(false));
  }, [userId]);

  const handleViewPrep = async (apt: Appointment) => {
    if (!userId) return;
    setLoadingPrep(true);
    try {
      const data = await getAppointmentPrep(userId, apt.id);
      setSelectedPrep(
        data.prep_summary ||
          "No prep summary available yet. Chat with NeuroNav to generate one."
      );
    } catch {
      setSelectedPrep("Failed to load prep summary.");
    } finally {
      setLoadingPrep(false);
    }
  };

  return (
    <div className="flex h-screen">
      <Sidebar />
      <main className="flex-1 overflow-y-auto bg-gray-50">
        <div className="border-b border-gray-200 bg-white px-6 py-4">
          <h1 className="text-lg font-semibold text-gray-900">
            Appointment Preparation
          </h1>
          <p className="text-sm text-gray-500">
            Review summaries to prepare for your upcoming appointments
          </p>
        </div>
        <div className="p-6 max-w-4xl mx-auto space-y-6">
          <div className="bg-white rounded-2xl border border-gray-200 p-6">
            <h2 className="text-base font-semibold text-gray-900 mb-4">
              Upcoming Appointments
            </h2>
            {loading ? (
              <div className="text-center py-6 text-gray-400">Loading...</div>
            ) : appointments.length === 0 ? (
              <div className="text-center py-6 text-gray-400">
                <Calendar className="w-8 h-8 mx-auto mb-2 opacity-50" />
                <p>No upcoming appointments.</p>
                <p className="text-xs mt-1">
                  Chat with NeuroNav to add appointments.
                </p>
              </div>
            ) : (
              <div className="space-y-3">
                {appointments.map((apt) => (
                  <div
                    key={apt.id}
                    className="flex items-center justify-between p-4 rounded-xl border border-gray-200 hover:border-indigo-200 transition-colors"
                  >
                    <div>
                      <p className="font-medium text-gray-900">
                        {apt.appointment_type || "Appointment"}
                      </p>
                      <p className="text-sm text-gray-500">
                        {apt.appointment_date}
                        {apt.doctor_name ? ` — Dr. ${apt.doctor_name}` : ""}
                      </p>
                    </div>
                    <button
                      onClick={() => handleViewPrep(apt)}
                      className="flex items-center gap-2 px-4 py-2 text-sm rounded-lg bg-indigo-50 text-indigo-700 hover:bg-indigo-100 transition-colors"
                    >
                      <FileText className="w-4 h-4" />
                      View Prep
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          {selectedPrep && (
            <div className="bg-white rounded-2xl border border-gray-200 p-6">
              <h2 className="text-base font-semibold text-gray-900 mb-4">
                Appointment Prep Summary
              </h2>
              {loadingPrep ? (
                <div className="flex items-center justify-center py-6 text-gray-400">
                  <Loader2 className="w-5 h-5 animate-spin mr-2" />
                  Loading...
                </div>
              ) : (
                <div className="prose prose-sm max-w-none">
                  <ReactMarkdown>{selectedPrep}</ReactMarkdown>
                </div>
              )}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

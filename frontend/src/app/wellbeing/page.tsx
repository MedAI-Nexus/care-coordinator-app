"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Sidebar from "@/components/layout/Sidebar";
import MoodChart from "@/components/wellbeing/MoodChart";
import BurnoutScore from "@/components/wellbeing/BurnoutScore";
import { useWellbeing } from "@/hooks/useWellbeing";

export default function WellbeingPage() {
  const [userId, setUserId] = useState<number | null>(null);
  const router = useRouter();
  const { scores, loading } = useWellbeing(userId);

  useEffect(() => {
    const id = localStorage.getItem("neuronav_user_id");
    if (!id) {
      router.push("/");
      return;
    }
    setUserId(parseInt(id));
  }, [router]);

  return (
    <div className="flex h-screen">
      <Sidebar />
      <main className="flex-1 overflow-y-auto bg-gray-50">
        <div className="border-b border-gray-200 bg-white px-6 py-4">
          <h1 className="text-lg font-semibold text-gray-900">
            Wellbeing Trends
          </h1>
          <p className="text-sm text-gray-500">
            Track mood, stress, and caregiver burnout over time
          </p>
        </div>
        <div className="p-6 max-w-4xl mx-auto space-y-6">
          <div className="bg-white rounded-2xl border border-gray-200 p-6">
            <h2 className="text-base font-semibold text-gray-900 mb-4">
              Current Scores
            </h2>
            <BurnoutScore scores={scores} />
          </div>

          <div className="bg-white rounded-2xl border border-gray-200 p-6">
            <h2 className="text-base font-semibold text-gray-900 mb-4">
              Trends Over Time
            </h2>
            {loading ? (
              <div className="text-center py-10 text-gray-400">Loading...</div>
            ) : (
              <MoodChart scores={scores} />
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

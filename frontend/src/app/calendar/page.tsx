"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Sidebar from "@/components/layout/Sidebar";
import TreatmentCalendar from "@/components/calendar/TreatmentCalendar";
import { useCalendar } from "@/hooks/useCalendar";

export default function CalendarPage() {
  const [userId, setUserId] = useState<number | null>(null);
  const router = useRouter();
  const { days, month, year, loading, prevMonth, nextMonth } =
    useCalendar(userId);

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
            Treatment Calendar
          </h1>
          <p className="text-sm text-gray-500">
            Your treatment schedule with drug days, rest days, and appointments
          </p>
        </div>
        <div className="p-6 max-w-4xl mx-auto">
          <div className="bg-white rounded-2xl border border-gray-200 p-6">
            <TreatmentCalendar
              days={days}
              month={month}
              year={year}
              loading={loading}
              onPrevMonth={prevMonth}
              onNextMonth={nextMonth}
            />
          </div>
        </div>
      </main>
    </div>
  );
}

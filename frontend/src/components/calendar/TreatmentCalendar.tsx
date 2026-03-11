"use client";

import { CalendarDay } from "@/lib/api";
import { ChevronLeft, ChevronRight } from "lucide-react";
import CycleLegend from "./CycleLegend";

const WEEKDAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

const DAY_COLORS: Record<string, string> = {
  drug: "bg-blue-100 border-blue-400 text-blue-800",
  rest: "bg-white border-gray-100 text-gray-500",
  bloodwork: "bg-orange-100 border-orange-400 text-orange-800",
  appointment: "bg-green-100 border-green-400 text-green-800",
  none: "bg-white border-gray-100 text-gray-400",
};

interface TreatmentCalendarProps {
  days: CalendarDay[];
  month: number;
  year: number;
  loading: boolean;
  onPrevMonth: () => void;
  onNextMonth: () => void;
}

const MONTH_NAMES = [
  "January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December",
];

export default function TreatmentCalendar({
  days,
  month,
  year,
  loading,
  onPrevMonth,
  onNextMonth,
}: TreatmentCalendarProps) {
  const firstDayOfMonth = new Date(year, month - 1, 1).getDay();
  const blanks = Array(firstDayOfMonth).fill(null);
  const today = new Date().toISOString().split("T")[0];

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <button
          onClick={onPrevMonth}
          className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
        >
          <ChevronLeft className="w-5 h-5" />
        </button>
        <h2 className="text-lg font-semibold text-gray-900">
          {MONTH_NAMES[month - 1]} {year}
        </h2>
        <button
          onClick={onNextMonth}
          className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
        >
          <ChevronRight className="w-5 h-5" />
        </button>
      </div>

      <CycleLegend />

      {loading ? (
        <div className="text-center py-10 text-gray-400">Loading...</div>
      ) : (
        <div className="grid grid-cols-7 gap-1.5">
          {WEEKDAYS.map((day) => (
            <div
              key={day}
              className="text-center text-xs font-medium text-gray-500 py-2"
            >
              {day}
            </div>
          ))}

          {blanks.map((_, i) => (
            <div key={`blank-${i}`} />
          ))}

          {days.map((day) => {
            const dateNum = new Date(day.date + "T00:00:00").getDate();
            const isToday = day.date === today;
            const isImportant = day.day_type !== "rest" && day.day_type !== "none";
            const colorClass = DAY_COLORS[day.day_type] || DAY_COLORS.none;

            return (
              <div
                key={day.date}
                className={`border rounded-lg p-2 min-h-[80px] ${colorClass} transition-colors relative ${
                  isToday ? "ring-2 ring-indigo-500 ring-offset-1" : ""
                } ${isImportant ? "border-2 shadow-sm" : ""}`}
                title={day.label || ""}
              >
                <div className={`text-xs font-medium ${isToday ? "text-indigo-600 font-bold" : ""}`}>
                  {dateNum}
                  {isToday && <span className="ml-1 text-[9px] text-indigo-500">today</span>}
                </div>
                {isImportant && day.label && (
                  <div className="text-[10px] mt-1 leading-tight font-medium">
                    {day.label}
                  </div>
                )}
                {day.day_type === "rest" && day.label && (
                  <div className="text-[9px] mt-1 text-gray-400">
                    {day.label}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

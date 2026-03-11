"use client";

import { useState, useEffect, useCallback } from "react";
import { getCalendar, CalendarDay } from "@/lib/api";

export function useCalendar(userId: number | null) {
  const [days, setDays] = useState<CalendarDay[]>([]);
  const [month, setMonth] = useState(new Date().getMonth() + 1);
  const [year, setYear] = useState(new Date().getFullYear());
  const [loading, setLoading] = useState(false);

  const fetchCalendar = useCallback(async () => {
    if (!userId) return;
    setLoading(true);
    try {
      const data = await getCalendar(userId, month, year);
      setDays(data);
    } catch {
      setDays([]);
    } finally {
      setLoading(false);
    }
  }, [userId, month, year]);

  useEffect(() => {
    fetchCalendar();
  }, [fetchCalendar]);

  const prevMonth = () => {
    if (month === 1) {
      setMonth(12);
      setYear(year - 1);
    } else {
      setMonth(month - 1);
    }
  };

  const nextMonth = () => {
    if (month === 12) {
      setMonth(1);
      setYear(year + 1);
    } else {
      setMonth(month + 1);
    }
  };

  return { days, month, year, loading, prevMonth, nextMonth, refetch: fetchCalendar };
}

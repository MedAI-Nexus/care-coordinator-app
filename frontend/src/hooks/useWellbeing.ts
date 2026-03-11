"use client";

import { useState, useEffect, useCallback } from "react";
import { getWellbeing, WellbeingScore } from "@/lib/api";

export function useWellbeing(userId: number | null) {
  const [scores, setScores] = useState<WellbeingScore[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchScores = useCallback(
    async (scoreType?: string, days: number = 30) => {
      if (!userId) return;
      setLoading(true);
      try {
        const data = await getWellbeing(userId, scoreType, days);
        setScores(data);
      } catch {
        setScores([]);
      } finally {
        setLoading(false);
      }
    },
    [userId]
  );

  useEffect(() => {
    fetchScores();
  }, [fetchScores]);

  return { scores, loading, refetch: fetchScores };
}

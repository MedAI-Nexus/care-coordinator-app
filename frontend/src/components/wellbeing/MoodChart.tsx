"use client";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { WellbeingScore } from "@/lib/api";
import { format, parseISO } from "date-fns";

interface MoodChartProps {
  scores: WellbeingScore[];
}

export default function MoodChart({ scores }: MoodChartProps) {
  if (scores.length === 0) {
    return (
      <div className="text-center py-10 text-gray-400">
        No wellbeing data yet. Chat with NeuroNav to start tracking.
      </div>
    );
  }

  // Group scores by date and type
  const dateMap = new Map<
    string,
    { date: string; mood?: number; stress?: number; zarit_burnout?: number }
  >();

  for (const score of scores) {
    const dateStr = format(parseISO(score.recorded_at), "MM/dd");
    const existing = dateMap.get(dateStr) || { date: dateStr };
    existing[score.score_type as "mood" | "stress" | "zarit_burnout"] =
      score.score;
    dateMap.set(dateStr, existing);
  }

  const data = Array.from(dateMap.values());

  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
        <XAxis dataKey="date" fontSize={12} />
        <YAxis domain={[0, 10]} fontSize={12} />
        <Tooltip />
        <Legend />
        <Line
          type="monotone"
          dataKey="mood"
          stroke="#6366f1"
          strokeWidth={2}
          name="Mood"
          dot={{ r: 4 }}
          connectNulls
        />
        <Line
          type="monotone"
          dataKey="stress"
          stroke="#f97316"
          strokeWidth={2}
          name="Stress"
          dot={{ r: 4 }}
          connectNulls
        />
        <Line
          type="monotone"
          dataKey="zarit_burnout"
          stroke="#ef4444"
          strokeWidth={2}
          name="Burnout"
          dot={{ r: 4 }}
          connectNulls
        />
      </LineChart>
    </ResponsiveContainer>
  );
}

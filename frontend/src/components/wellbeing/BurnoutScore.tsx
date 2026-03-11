"use client";

import { WellbeingScore } from "@/lib/api";

interface BurnoutScoreProps {
  scores: WellbeingScore[];
}

export default function BurnoutScore({ scores }: BurnoutScoreProps) {
  const burnoutScores = scores.filter((s) => s.score_type === "zarit_burnout");
  const latestBurnout = burnoutScores[burnoutScores.length - 1];
  const moodScores = scores.filter((s) => s.score_type === "mood");
  const latestMood = moodScores[moodScores.length - 1];
  const stressScores = scores.filter((s) => s.score_type === "stress");
  const latestStress = stressScores[stressScores.length - 1];

  const cards = [
    {
      label: "Mood",
      value: latestMood?.score,
      color: "text-indigo-600",
      bg: "bg-indigo-50",
      desc: "higher is better",
    },
    {
      label: "Stress",
      value: latestStress?.score,
      color: "text-orange-600",
      bg: "bg-orange-50",
      desc: "lower is better",
    },
    {
      label: "Burnout",
      value: latestBurnout?.score,
      color: "text-red-600",
      bg: "bg-red-50",
      desc: "lower is better",
    },
  ];

  return (
    <div className="grid grid-cols-3 gap-4">
      {cards.map((card) => (
        <div
          key={card.label}
          className={`${card.bg} rounded-xl p-4 text-center`}
        >
          <p className="text-sm text-gray-500 mb-1">{card.label}</p>
          <p className={`text-3xl font-bold ${card.color}`}>
            {card.value != null ? `${card.value}/10` : "—"}
          </p>
          <p className="text-xs text-gray-400 mt-1">{card.desc}</p>
        </div>
      ))}
    </div>
  );
}

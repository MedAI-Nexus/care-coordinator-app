const LEGEND_ITEMS = [
  { color: "bg-blue-300", label: "Drug Day" },
  { color: "bg-gray-300", label: "Rest Day" },
  { color: "bg-orange-300", label: "Bloodwork" },
  { color: "bg-green-300", label: "Appointment" },
];

export default function CycleLegend() {
  return (
    <div className="flex flex-wrap gap-4 mb-4">
      {LEGEND_ITEMS.map((item) => (
        <div key={item.label} className="flex items-center gap-2">
          <div className={`w-3 h-3 rounded ${item.color}`} />
          <span className="text-xs text-gray-600">{item.label}</span>
        </div>
      ))}
    </div>
  );
}

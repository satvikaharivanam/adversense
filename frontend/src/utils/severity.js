export const SEVERITY_CONFIG = {
  critical: { label: "CRITICAL", bg: "bg-red-600",    text: "text-red-600",    border: "border-red-600",    hex: "#dc2626", icon: "🔴", order: 0 },
  high:     { label: "HIGH",     bg: "bg-orange-500", text: "text-orange-500", border: "border-orange-500", hex: "#ea580c", icon: "🟠", order: 1 },
  medium:   { label: "MEDIUM",   bg: "bg-yellow-500", text: "text-yellow-500", border: "border-yellow-500", hex: "#ca8a04", icon: "🟡", order: 2 },
  low:      { label: "LOW",      bg: "bg-blue-500",   text: "text-blue-500",   border: "border-blue-500",   hex: "#2563eb", icon: "🔵", order: 3 },
  none:     { label: "PASS",     bg: "bg-gray-500",   text: "text-gray-400",   border: "border-gray-500",   hex: "#6b7280", icon: "✅", order: 4 },
};

export function getSeverityConfig(severity) {
  return SEVERITY_CONFIG[severity?.toLowerCase()] ?? SEVERITY_CONFIG.none;
}

export function sortBySeverity(findings) {
  return [...findings].sort(
    (a, b) =>
      (SEVERITY_CONFIG[a.severity]?.order ?? 99) -
      (SEVERITY_CONFIG[b.severity]?.order ?? 99)
  );
}

export const EVENT_CONFIG = {
  start:              { icon: "🚀", color: "text-green-400",  label: "START"    },
  reasoning:          { icon: "🧠", color: "text-gray-300",   label: "THINK"    },
  tool_call:          { icon: "🔧", color: "text-blue-400",   label: "TOOL"     },
  tool_result:        { icon: "↩️",  color: "text-gray-400",   label: "RESULT"   },
  finding:            { icon: "⚠️",  color: "text-red-400",    label: "FINDING"  },
  iteration_start:    { icon: "📋", color: "text-purple-400", label: "ITER"     },
  iteration_complete: { icon: "✔️",  color: "text-purple-300", label: "DONE"     },
  complete:           { icon: "🎉", color: "text-green-400",  label: "COMPLETE" },
  error:              { icon: "💥", color: "text-red-500",    label: "ERROR"    },
};

export function getEventConfig(type) {
  return EVENT_CONFIG[type] ?? { icon: "·", color: "text-gray-500", label: type };
}
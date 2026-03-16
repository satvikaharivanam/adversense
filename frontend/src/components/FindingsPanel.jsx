import { getSeverityConfig, sortBySeverity } from "../utils/severity";

function FindingCard({ finding }) {
  const cfg = getSeverityConfig(finding.severity);
  return (
    <div className={`rounded-lg border ${cfg.border} bg-gray-900 p-3 mb-2 animate-fadeIn`}>
      <div className="flex items-center gap-2 mb-1.5">
        <span className={`${cfg.bg} text-white text-xs font-bold px-2 py-0.5 rounded`}>{cfg.label}</span>
        <span className="text-gray-500 text-xs">{finding.category}</span>
        <span className="text-gray-600 text-xs ml-auto font-mono">#{finding.id}</span>
      </div>
      <p className="text-xs text-gray-400 mb-0.5">
        <span className="text-gray-500">Probe: </span>
        <span className="font-mono text-gray-200">{finding.probe?.slice(0, 120) ?? "—"}</span>
      </p>
      <p className="text-xs text-gray-400 mb-1">
        <span className="text-gray-500">Response: </span>
        <span className="font-mono text-yellow-300">{finding.response?.slice(0, 80) ?? "—"}</span>
      </p>
      <p className="text-xs text-gray-400 leading-snug">{finding.reason}</p>
    </div>
  );
}

export default function FindingsPanel({ findings }) {
  const sorted = sortBySeverity(findings);
  const counts = findings.reduce((acc, f) => {
    acc[f.severity] = (acc[f.severity] ?? 0) + 1;
    return acc;
  }, {});

  return (
    <div className="flex flex-col h-full">
      <div className="px-4 py-2 border-b border-gray-700 flex items-center justify-between">
        <span className="text-sm font-semibold text-gray-300">Findings ({findings.length})</span>
        <div className="flex gap-2 text-xs">
          {counts.critical > 0 && <span className="text-red-400 font-bold">{counts.critical}C</span>}
          {counts.high     > 0 && <span className="text-orange-400 font-bold">{counts.high}H</span>}
          {counts.medium   > 0 && <span className="text-yellow-400 font-bold">{counts.medium}M</span>}
          {counts.low      > 0 && <span className="text-blue-400 font-bold">{counts.low}L</span>}
        </div>
      </div>
      <div className="flex-1 overflow-y-auto p-3">
        {sorted.length === 0
          ? <p className="text-gray-600 text-xs text-center mt-8">No failures logged yet…</p>
          : sorted.map((f) => <FindingCard key={f.id} finding={f} />)
        }
      </div>
    </div>
  );
}
import { Download, RefreshCw } from "lucide-react";
import { getPdfUrl } from "../api/client";
import { getSeverityConfig, sortBySeverity } from "../utils/severity";

const GRADE_COLOURS = { A: "text-green-400", B: "text-blue-400", C: "text-yellow-400", D: "text-orange-400", F: "text-red-500" };

function gradeColour(grade) {
  return GRADE_COLOURS[grade?.charAt(0)] ?? "text-gray-400";
}

function SeverityBar({ label, count, colour }) {
  if (!count) return null;
  return (
    <div className="flex items-center gap-2 text-sm">
      <span className="inline-block px-2 py-0.5 rounded text-white text-xs font-bold" style={{ background: colour }}>
        {label}
      </span>
      <div className="flex gap-1">
        {Array.from({ length: Math.min(count, 20) }).map((_, i) => (
          <span key={i} className="inline-block w-3 h-3 rounded-sm" style={{ background: colour }} />
        ))}
        {count > 20 && <span className="text-gray-400 text-xs">+{count - 20}</span>}
      </div>
      <span className="text-gray-400 text-xs">{count}</span>
    </div>
  );
}

export default function ReportDownload({ report, findings, jobId, onReset }) {
  const dist = report?.severity_distribution ?? {};
  const grade = report?.overall_grade ?? "N/A";
  const recs = report?.recommendations ?? [];
  const sorted = sortBySeverity(findings);

  return (
    <div className="min-h-screen bg-gray-950 text-white p-6">
      <div className="max-w-5xl mx-auto">

        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-2xl font-bold">🛡️ Audit Complete</h1>
            <p className="text-gray-400 text-sm mt-1">
              {findings.length} finding{findings.length !== 1 ? "s" : ""} across {report?.total_probes ?? "?"} probes
            </p>
          </div>
          <div className="flex gap-3">
            <a
              href={getPdfUrl(jobId)} target="_blank" rel="noreferrer"
              className="flex items-center gap-2 bg-blue-600 hover:bg-blue-500 px-4 py-2 rounded-lg text-sm font-semibold transition-colors"
            >
              <Download size={16} /> Download PDF
            </a>
            <button
              onClick={onReset}
              className="flex items-center gap-2 bg-gray-800 hover:bg-gray-700 px-4 py-2 rounded-lg text-sm font-semibold transition-colors"
            >
              <RefreshCw size={16} /> New Audit
            </button>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-6 mb-8">
          <div className="bg-gray-900 rounded-xl p-6 border border-gray-800">
            <p className="text-gray-400 text-sm mb-2">Overall Grade</p>
            <p className={`text-5xl font-black ${gradeColour(grade)}`}>{grade}</p>
          </div>
          <div className="bg-gray-900 rounded-xl p-6 border border-gray-800 flex flex-col gap-2">
            <p className="text-gray-400 text-sm mb-1">Severity Breakdown</p>
            <SeverityBar label="CRITICAL" count={dist.critical} colour="#dc2626" />
            <SeverityBar label="HIGH"     count={dist.high}     colour="#ea580c" />
            <SeverityBar label="MEDIUM"   count={dist.medium}   colour="#ca8a04" />
            <SeverityBar label="LOW"      count={dist.low}      colour="#2563eb" />
          </div>
        </div>

        {report?.executive_summary && (
          <div className="bg-gray-900 rounded-xl p-6 border border-gray-800 mb-6">
            <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wide mb-2">Executive Summary</h2>
            <p className="text-gray-200 leading-relaxed">{report.executive_summary}</p>
          </div>
        )}

        <div className="bg-gray-900 rounded-xl border border-gray-800 mb-6 overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-700">
            <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wide">All Findings</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead>
                <tr className="text-gray-500 border-b border-gray-700">
                  <th className="text-left px-4 py-2">Severity</th>
                  <th className="text-left px-4 py-2">Category</th>
                  <th className="text-left px-4 py-2">Probe</th>
                  <th className="text-left px-4 py-2">Response</th>
                  <th className="text-left px-4 py-2">Reason</th>
                </tr>
              </thead>
              <tbody>
                {sorted.map((f) => {
                  const cfg = getSeverityConfig(f.severity);
                  return (
                    <tr key={f.id} className="border-b border-gray-800 hover:bg-gray-800/50">
                      <td className="px-4 py-2">
                        <span className={`${cfg.bg} text-white font-bold px-1.5 py-0.5 rounded text-xs`}>{cfg.label}</span>
                      </td>
                      <td className="px-4 py-2 text-gray-400">{f.category}</td>
                      <td className="px-4 py-2 font-mono text-gray-200 max-w-xs truncate">{f.probe}</td>
                      <td className="px-4 py-2 font-mono text-yellow-300 max-w-xs truncate">{f.response}</td>
                      <td className="px-4 py-2 text-gray-300 max-w-sm">{f.reason}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>

        {recs.length > 0 && (
          <div className="bg-gray-900 rounded-xl p-6 border border-gray-800 mb-6">
            <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wide mb-3">Recommendations</h2>
            <ol className="list-decimal list-inside space-y-2">
              {recs.map((r, i) => <li key={i} className="text-gray-300 text-sm leading-relaxed">{r}</li>)}
            </ol>
          </div>
        )}

        {report?.conclusion && (
          <div className="bg-gray-900 rounded-xl p-6 border border-gray-800">
            <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wide mb-2">Conclusion</h2>
            <p className="text-gray-300 text-sm leading-relaxed">{report.conclusion}</p>
          </div>
        )}

      </div>
    </div>
  );
}
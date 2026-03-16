import { Shield } from "lucide-react";
import AgentFeed from "./components/AgentFeed";
import FindingsPanel from "./components/FindingsPanel";
import ReportDownload from "./components/ReportDownload";
import SubmitForm from "./components/SubmitForm";
import { useAgentStream } from "./hooks/useAgentStream";
import { useAuditJob } from "./hooks/useAuditJob";

function RunningView({ jobId, findings }) {
  const { events, isConnected } = useAgentStream(jobId);

  const iterationEvents = events.filter((e) => e.type === "iteration_start");
  const latestIter = iterationEvents.at(-1)?.iteration ?? 1;
  const probeCount = events.filter(
    (e) => e.type === "tool_call" && e.tool === "query_model"
  ).length;

  return (
    <div className="min-h-screen bg-gray-950 flex flex-col">
      <div className="flex items-center justify-between px-6 py-3 border-b border-gray-800 bg-gray-900">
        <div className="flex items-center gap-2">
          <Shield className="text-blue-500" size={20} />
          <span className="text-white font-semibold text-sm">AdverSense</span>
          <span className="text-gray-500 text-xs ml-2">Running audit…</span>
        </div>
        <div className="flex items-center gap-4 text-xs text-gray-400">
          <span>Iteration {latestIter}</span>
          <span>{probeCount} probes sent</span>
          <span>{findings.length} findings</span>
        </div>
      </div>

      <div className="flex-1 flex overflow-hidden" style={{ height: "calc(100vh - 49px)" }}>
        <div className="w-[55%] border-r border-gray-800 flex flex-col overflow-hidden">
          <AgentFeed events={events} isConnected={isConnected} jobId={jobId} />
        </div>
        <div className="w-[45%] flex flex-col overflow-hidden">
          <FindingsPanel findings={findings} />
        </div>
      </div>
    </div>
  );
}

function ErrorView({ error, onReset }) {
  return (
    <div className="min-h-screen bg-gray-950 flex items-center justify-center p-6">
      <div className="bg-gray-900 border border-red-800 rounded-xl p-8 max-w-md w-full text-center">
        <p className="text-4xl mb-4">💥</p>
        <h2 className="text-white font-bold text-lg mb-2">Audit Failed</h2>
        <p className="text-red-400 text-sm mb-6 font-mono">{error}</p>
        <button
          onClick={onReset}
          className="bg-blue-600 hover:bg-blue-500 text-white px-6 py-2 rounded-lg text-sm font-semibold"
        >
          Try Again
        </button>
      </div>
    </div>
  );
}

export default function App() {
  const { state, jobId, findings, report, error, submit, reset } = useAuditJob();

  if (state === "idle" || state === "submitting") {
    return <SubmitForm onSubmit={submit} isSubmitting={state === "submitting"} />;
  }
  if (state === "running") {
    return <RunningView jobId={jobId} findings={findings} />;
  }
  if (state === "complete") {
    return <ReportDownload report={report} findings={findings} jobId={jobId} onReset={reset} />;
  }
  if (state === "failed") {
    return <ErrorView error={error} onReset={reset} />;
  }
  return null;
}
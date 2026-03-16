import { useEffect, useRef } from "react";
import { getEventConfig } from "../utils/severity";

function FeedItem({ event }) {
  const cfg = getEventConfig(event.type);
  const isIteration = event.type === "iteration_start" || event.type === "iteration_complete";

  let text = event.text ?? "";
  if (event.type === "tool_call") {
    const inputPreview = event.input
      ? Object.entries(event.input)
          .map(([k, v]) => `${k}=${JSON.stringify(v).slice(0, 40)}`)
          .join(", ")
      : "";
    text = `${event.tool}(${inputPreview})`;
  } else if (event.type === "tool_result") {
    text = `← ${event.tool}: ${String(event.result ?? "").slice(0, 120)}`;
  }

  return (
    <div className={`flex items-start gap-2 py-1.5 px-1 animate-fadeIn ${isIteration ? "border-t border-gray-700 mt-2 pt-3" : ""}`}>
      <span className="text-sm flex-shrink-0 mt-0.5">{cfg.icon}</span>
      <span className={`text-xs font-mono ${cfg.color} break-words min-w-0 flex-1`}>
        {text || JSON.stringify(event).slice(0, 120)}
      </span>
    </div>
  );
}

export default function AgentFeed({ events, isConnected }) {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [events.length]);

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center justify-between px-4 py-2 border-b border-gray-700">
        <span className="text-sm font-semibold text-gray-300">Agent Activity</span>
        <span className="flex items-center gap-1.5 text-xs text-gray-400">
          <span className={`inline-block w-2 h-2 rounded-full ${isConnected ? "bg-green-500" : "bg-gray-500"}`} />
          {isConnected ? "Live" : "Polling"}
        </span>
      </div>
      <div className="flex-1 overflow-y-auto p-3 font-mono text-xs">
        {events.length === 0
          ? <p className="text-gray-600 text-center mt-8">Waiting for agent…</p>
          : events.map((evt) => <FeedItem key={evt._id} event={evt} />)
        }
        <div ref={bottomRef} />
      </div>
    </div>
  );
}
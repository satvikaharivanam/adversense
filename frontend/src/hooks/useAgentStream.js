import { useCallback, useEffect, useRef, useState } from "react";
import { openStream, pollLog } from "../api/client";

const POLL_INTERVAL_MS = 1500;

export function useAgentStream(jobId) {
  const [events, setEvents] = useState([]);
  const [isConnected, setIsConnected] = useState(false);
  const wsRef = useRef(null);
  const pollTimerRef = useRef(null);
  const logCursorRef = useRef(0);

  const pushEvent = useCallback((evt) => {
    setEvents((prev) => [...prev, { ...evt, _id: Date.now() + Math.random() }]);
  }, []);

  useEffect(() => {
    if (!jobId) return;

    let wsWorking = false;

    try {
      const ws = openStream(jobId);
      wsRef.current = ws;

      ws.onopen = () => {
        setIsConnected(true);
        wsWorking = true;
      };

      ws.onmessage = (e) => {
        try { pushEvent(JSON.parse(e.data)); } catch (_) {}
      };

      ws.onerror = () => {
        ws.close();
        if (!wsWorking) startPolling();
      };

      ws.onclose = () => setIsConnected(false);

      // If WS doesn't open within 2s, fall back to polling
      setTimeout(() => {
        if (!wsWorking) startPolling();
      }, 2000);

    } catch (_) {
      startPolling();
    }

    function startPolling() {
      pollTimerRef.current = setInterval(async () => {
        try {
          const { events: newEvents, total } = await pollLog(jobId, logCursorRef.current);
          if (newEvents.length > 0) {
            newEvents.forEach(pushEvent);
            logCursorRef.current = total;
          }
        } catch (_) {}
      }, POLL_INTERVAL_MS);
    }

    return () => {
      wsRef.current?.close();
      clearInterval(pollTimerRef.current);
    };
  }, [jobId, pushEvent]);

  return { events, isConnected };
}
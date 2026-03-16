import { useCallback, useEffect, useRef, useState } from "react";
import { createAudit, getFindings, getReport, getStatus } from "../api/client";

const POLL_MS = 3000;

export function useAuditJob() {
  const [state, setState] = useState("idle");
  const [jobId, setJobId] = useState(null);
  const [findings, setFindings] = useState([]);
  const [report, setReport] = useState(null);
  const [error, setError] = useState(null);
  const pollRef = useRef(null);

  const submit = useCallback(async (formData) => {
    setState("submitting");
    setError(null);
    setFindings([]);
    setReport(null);
    try {
      const { job_id } = await createAudit(formData);
      setJobId(job_id);
      setState("running");
    } catch (err) {
      setError(err?.response?.data?.detail ?? err.message ?? "Submission failed");
      setState("failed");
    }
  }, []);

  useEffect(() => {
    if (state !== "running" || !jobId) return;

    pollRef.current = setInterval(async () => {
      try {
        const status = await getStatus(jobId);

        if (status.status === "completed" || status.status === "complete") {
          const fresh = await getFindings(jobId);
          setFindings(fresh);
        }

       if (status.status === "completed" || status.status === "complete") {
  clearInterval(pollRef.current);
  const [fullReport, allFindings] = await Promise.all([
    getReport(jobId),
    getFindings(jobId),
  ]);
  setReport(fullReport);
  setFindings(allFindings);
  setState("complete");
} else if (status.status === "failed") {
          clearInterval(pollRef.current);
          setError(status.error ?? "Audit failed on the server.");
          setState("failed");
        }
      } catch (_) {}
    }, POLL_MS);

    return () => clearInterval(pollRef.current);
  }, [state, jobId]); // eslint-disable-line

  const reset = useCallback(() => {
    clearInterval(pollRef.current);
    setJobId(null);
    setFindings([]);
    setReport(null);
    setError(null);
    setState("idle");
  }, []);

  return { state, jobId, findings, report, error, submit, reset };
}
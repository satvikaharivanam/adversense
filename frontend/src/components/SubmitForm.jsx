import { useState } from "react";
import { Shield } from "lucide-react";

const MODEL_TYPES = [
  { value: "text_classifier", label: "Text Classifier" },
  { value: "llm_chat",        label: "LLM / Chat Model" },
  { value: "image_tagger",    label: "Image Tagger" },
  { value: "other",           label: "Other" },
];

const DEPTH_LABELS = { 1: "Quick (~15 probes)", 2: "Standard (~30 probes)", 3: "Deep (~60 probes)" };

export default function SubmitForm({ onSubmit, isSubmitting }) {
  const [form, setForm] = useState({
    model_url: "",
    model_description: "",
    model_type: "text_classifier",
    probe_depth: 2,
    auth_header: "",
  });

  const canSubmit =
    !isSubmitting &&
    form.model_url.trim().length > 0 &&
    form.model_description.trim().length >= 10;

  function handleChange(e) {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  }

  function handleSubmit() {
    if (!canSubmit) return;
    const payload = { ...form, probe_depth: Number(form.probe_depth) };
    if (!payload.auth_header) delete payload.auth_header;
    onSubmit(payload);
  }

  return (
    <div className="min-h-screen bg-gray-950 flex items-center justify-center p-6">
      <div className="w-full max-w-xl bg-gray-900 rounded-2xl shadow-2xl p-8 border border-gray-800">

        <div className="flex items-center gap-3 mb-8">
          <Shield className="text-blue-500" size={32} />
          <div>
            <h1 className="text-2xl font-bold text-white">AdverSense</h1>
            <p className="text-gray-400 text-sm">Autonomous AI Robustness Auditor</p>
          </div>
        </div>

        <div className="mb-5">
          <label className="block text-sm font-medium text-gray-300 mb-1">
            Model API URL <span className="text-red-400">*</span>
          </label>
          <input
            type="url" name="model_url" value={form.model_url} onChange={handleChange}
            placeholder="https://router.huggingface.co/hf-inference/models/..."
            className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2.5
                       text-white placeholder-gray-500 text-sm
                       focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div className="mb-5">
          <label className="block text-sm font-medium text-gray-300 mb-1">
            Model Description <span className="text-red-400">*</span>
          </label>
          <textarea
            name="model_description" value={form.model_description} onChange={handleChange}
            rows={3}
            placeholder="A binary sentiment classifier that labels text as POSITIVE or NEGATIVE."
            className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2.5
                       text-white placeholder-gray-500 text-sm resize-none
                       focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <p className="text-xs text-gray-500 mt-1">Min 10 characters</p>
        </div>

        <div className="flex gap-4 mb-5">
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-300 mb-1">Model Type</label>
            <select
              name="model_type" value={form.model_type} onChange={handleChange}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2.5
                         text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {MODEL_TYPES.map((t) => (
                <option key={t.value} value={t.value}>{t.label}</option>
              ))}
            </select>
          </div>

          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-300 mb-1">
              Probe Depth — <span className="text-blue-400">{DEPTH_LABELS[form.probe_depth]}</span>
            </label>
            <input
              type="range" name="probe_depth" min={1} max={3} step={1}
              value={form.probe_depth} onChange={handleChange}
              className="w-full mt-3 accent-blue-500"
            />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>Quick</span><span>Standard</span><span>Deep</span>
            </div>
          </div>
        </div>

        <div className="mb-7">
          <label className="block text-sm font-medium text-gray-300 mb-1">
            Auth Header <span className="text-gray-500">(optional)</span>
          </label>
          <input
            type="text" name="auth_header" value={form.auth_header} onChange={handleChange}
            placeholder="Bearer hf_xxxxxxxxxxxx"
            className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2.5
                       text-white placeholder-gray-500 text-sm font-mono
                       focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <button
          onClick={handleSubmit}
          disabled={!canSubmit}
          className={`w-full py-3 rounded-lg font-semibold text-white text-sm transition-all
            ${canSubmit
              ? "bg-blue-600 hover:bg-blue-500 cursor-pointer"
              : "bg-gray-700 cursor-not-allowed text-gray-500"
            }`}
        >
          {isSubmitting ? "Starting audit…" : "Start Audit →"}
        </button>

      </div>
    </div>
  );
} 
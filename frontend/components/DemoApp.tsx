"use client";

import { AlertCircle, CheckCircle2, CloudOff, Image as ImageIcon, Upload } from "lucide-react";
import { ChangeEvent, useEffect, useMemo, useState } from "react";

import type { ClassInfo, DemoData, SampleInfo, SplitMetrics } from "../lib/demo-data";

type UploadState =
  | { status: "idle"; message: string }
  | { status: "loading"; message: string }
  | { status: "success"; message: string; overlayUrl: string; classesPresent: number[]; disclaimer: string }
  | { status: "error"; message: string };

type PredictResponse = {
  prediction: {
    overlay_png_base64: string;
    classes_present: number[];
  };
  disclaimer: string;
};

const demoDisclaimer = "Model prediction for demonstration only; not authoritative geospatial analysis.";
const missingApiMessage = "Live inference is not configured. Curated samples remain available.";

function apiBaseUrl() {
  return process.env.NEXT_PUBLIC_INFERENCE_API_URL?.replace(/\/$/, "") ?? "";
}

function formatMetric(value: number | null) {
  if (value === null) {
    return "Pending";
  }
  return `${(value * 100).toFixed(1)}%`;
}

function splitSummary(label: string, metrics: SplitMetrics) {
  if (metrics.status === "not_run") {
    return `${label} evaluation has not been run. ${metrics.reason ?? "Regenerate metrics before quoting model scores."}`;
  }
  return `${label}: mean IoU ${formatMetric(metrics.meanIou)}, pixel accuracy ${formatMetric(metrics.pixelAccuracy)}.`;
}

function classColor(item: ClassInfo) {
  return `rgb(${item.rgb[0]}, ${item.rgb[1]}, ${item.rgb[2]})`;
}

function SampleButtons({
  samples,
  selected,
  onSelect,
}: {
  samples: SampleInfo[];
  selected: SampleInfo;
  onSelect: (sample: SampleInfo) => void;
}) {
  return (
    <div className="sample-tabs" aria-label="Curated samples">
      {samples.map((sample) => (
        <button
          className={sample.id === selected.id ? "sample-tab sample-tab-active" : "sample-tab"}
          key={sample.id}
          onClick={() => onSelect(sample)}
          type="button"
        >
          <ImageIcon aria-hidden="true" size={17} />
          <span>{sample.id}</span>
        </button>
      ))}
    </div>
  );
}

function Legend({ classes }: { classes: ClassInfo[] }) {
  return (
    <section className="legend" aria-labelledby="legend-heading">
      <h2 id="legend-heading">Class Legend</h2>
      <div className="legend-grid">
        {classes.map((item) => (
          <div className="legend-item" key={item.id}>
            <span className="swatch" style={{ background: classColor(item) }} />
            <span>{item.name}</span>
            {item.ignored ? <span className="muted">ignored</span> : null}
          </div>
        ))}
      </div>
    </section>
  );
}

function MetricsPanel({ data }: { data: DemoData }) {
  const rows = data.validation.perClassIou.map((validationItem) => {
    const testItem = data.test.perClassIou.find((item) => item.classId === validationItem.classId);
    return {
      className: validationItem.className,
      validation: validationItem.iou,
      test: testItem?.iou ?? null,
    };
  });

  return (
    <section className="metrics" aria-labelledby="metrics-heading">
      <div>
        <p className="eyebrow">Evaluation</p>
        <h2 id="metrics-heading">Model Evidence</h2>
      </div>
      <div className="metric-cards">
        <article>
          <h3>Validation</h3>
          <p>{splitSummary("Validation", data.validation)}</p>
        </article>
        <article>
          <h3>Test</h3>
          <p>{splitSummary("Test", data.test)}</p>
        </article>
      </div>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Class</th>
              <th>Validation IoU</th>
              <th>Test IoU</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.className}>
                <td>{row.className}</td>
                <td>{formatMetric(row.validation)}</td>
                <td>{formatMetric(row.test)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="artifact-note">
        Metrics and samples are loaded from synced generated artifacts. Current sample predictions are marked as
        placeholders until model-backed artifacts are regenerated.
      </p>
    </section>
  );
}

function UploadPanel({
  disabled,
  uploadState,
  onUpload,
}: {
  disabled: boolean;
  uploadState: UploadState;
  onUpload: (event: ChangeEvent<HTMLInputElement>) => void;
}) {
  const statusIcon = uploadState.status === "error" ? <CloudOff aria-hidden="true" size={18} /> : <Upload aria-hidden="true" size={18} />;

  return (
    <section className="upload-panel" aria-labelledby="upload-heading">
      <div>
        <p className="eyebrow">Optional Upload</p>
        <h2 id="upload-heading">Try Live Inference</h2>
      </div>
      <label className={disabled ? "upload-target upload-target-disabled" : "upload-target"}>
        <Upload aria-hidden="true" size={22} />
        <span>Upload a satellite-style image</span>
        <input accept="image/*" aria-label="Upload a satellite-style image" disabled={disabled} onChange={onUpload} type="file" />
      </label>
      <div className={`upload-status upload-${uploadState.status}`}>
        {statusIcon}
        <span>{uploadState.message}</span>
      </div>
      {"overlayUrl" in uploadState ? (
        <div className="upload-result">
          <img alt="Uploaded model prediction" src={uploadState.overlayUrl} />
          <p>{uploadState.disclaimer}</p>
        </div>
      ) : null}
    </section>
  );
}

export default function DemoApp({ data }: { data: DemoData }) {
  const configuredApiBaseUrl = apiBaseUrl();
  const [selectedSample, setSelectedSample] = useState(data.samples[0]);
  const [backendUnavailable, setBackendUnavailable] = useState(!configuredApiBaseUrl);
  const [uploadState, setUploadState] = useState<UploadState>({
    status: "idle",
    message: configuredApiBaseUrl
      ? "Choose an image to request a model prediction from the configured backend."
      : missingApiMessage,
  });

  useEffect(() => {
    if (!configuredApiBaseUrl) {
      return;
    }

    let cancelled = false;

    async function checkHealth() {
      try {
        const response = await fetch(`${configuredApiBaseUrl}/health`, { method: "GET" });
        const payload = await response.json().catch(() => ({}));
        if (cancelled || response.ok) {
          return;
        }

        const reason = typeof payload.error === "string" && payload.error ? ` ${payload.error}` : "";
        setBackendUnavailable(true);
        setUploadState({
          status: "error",
          message: `Backend health check failed.${reason} Curated samples remain available.`,
        });
      } catch {
        if (cancelled) {
          return;
        }
        setBackendUnavailable(true);
        setUploadState({
          status: "error",
          message: "Backend health check failed. Curated samples remain available.",
        });
      }
    }

    void checkHealth();

    return () => {
      cancelled = true;
    };
  }, [configuredApiBaseUrl]);

  const sampleContext = useMemo(() => {
    if (selectedSample.predictionSource === "generated_placeholder") {
      return "This curated sample uses a generated placeholder prediction. Treat it as a UI artifact until model-backed predictions are regenerated.";
    }
    return "This curated sample is backed by generated model prediction artifacts.";
  }, [selectedSample.predictionSource]);

  async function handleUpload(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) {
      return;
    }

    const baseUrl = apiBaseUrl();
    if (!baseUrl) {
      setUploadState({
        status: "error",
        message: "Live inference is not configured. Set NEXT_PUBLIC_INFERENCE_API_URL to enable upload predictions.",
      });
      return;
    }
    if (backendUnavailable) {
      setUploadState({
        status: "error",
        message: missingApiMessage,
      });
      return;
    }

    const body = new FormData();
    body.append("file", file);
    setUploadState({ status: "loading", message: "Requesting model prediction..." });

    try {
      const response = await fetch(`${baseUrl}/predict`, { method: "POST", body });
      const payload = await response.json();
      if (!response.ok) {
        throw new Error(payload.detail ?? "Inference request failed.");
      }
      const prediction = payload as PredictResponse;
      setUploadState({
        status: "success",
        message: "Upload prediction returned by the configured backend.",
        overlayUrl: `data:image/png;base64,${prediction.prediction.overlay_png_base64}`,
        classesPresent: prediction.prediction.classes_present,
        disclaimer: prediction.disclaimer || demoDisclaimer,
      });
    } catch (error) {
      setUploadState({
        status: "error",
        message: error instanceof Error ? error.message : "Inference request failed.",
      });
    }
  }

  return (
    <main className="shell">
      <section className="demo-hero" aria-labelledby="demo-heading">
        <div className="hero-copy">
          <p className="eyebrow">Dubai Satellite Imagery</p>
          <h1 id="demo-heading">Satellite Segmentation Demo</h1>
          <p>
            Inspect curated imagery, compare the predicted segmentation overlay, and keep model evidence close to the
            interaction. Outputs are model predictions, not ground truth or authoritative geospatial analysis.
          </p>
        </div>
        <div className="status-strip">
          <CheckCircle2 aria-hidden="true" size={18} />
          <span>{demoDisclaimer}</span>
        </div>
      </section>

      <section className="workspace" aria-label="Interactive segmentation workspace">
        <div className="sample-panel">
          <SampleButtons samples={data.samples} selected={selectedSample} onSelect={setSelectedSample} />
          <div className="image-grid">
            <figure>
              <img alt={`Original imagery for ${selectedSample.id}`} src={selectedSample.originalUrl} />
              <figcaption>Original imagery</figcaption>
            </figure>
            <figure>
              <img alt={`Model prediction overlay for ${selectedSample.id}`} src={selectedSample.overlayUrl} />
              <figcaption>Model prediction overlay</figcaption>
            </figure>
          </div>
          <div className="context-callout">
            <AlertCircle aria-hidden="true" size={18} />
            <p>
              <strong>{selectedSample.id}</strong>: {sampleContext} {selectedSample.notes}
            </p>
          </div>
        </div>
        <aside className="side-rail">
          <Legend classes={data.classes} />
          <UploadPanel disabled={backendUnavailable || uploadState.status === "loading"} uploadState={uploadState} onUpload={handleUpload} />
        </aside>
      </section>

      <MetricsPanel data={data} />
    </main>
  );
}

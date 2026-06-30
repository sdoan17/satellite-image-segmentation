import fs from "node:fs";
import path from "node:path";

export type ClassInfo = {
  id: number;
  name: string;
  rgb: [number, number, number];
  ignored: boolean;
};

export type SampleInfo = {
  id: string;
  sourceImage: string;
  originalUrl: string;
  predictionUrl: string;
  overlayUrl: string;
  predictionSource: string;
  notes: string;
};

export type SplitMetrics = {
  status: string;
  reason?: string;
  pixelAccuracy: number | null;
  meanIou: number | null;
  perClassIou: Array<{
    classId: number;
    className: string;
    iou: number | null;
    intersection: number;
    union: number;
  }>;
};

export type DemoData = {
  generatedAt: string;
  modelArtifactName: string;
  classes: ClassInfo[];
  samples: SampleInfo[];
  validation: SplitMetrics;
  test: SplitMetrics;
};

type RawClassFile = {
  classes: ClassInfo[];
};

type RawSampleFile = {
  generated_at: string;
  samples: Array<{
    id: string;
    source_image: string;
    original: string;
    prediction: string;
    overlay: string;
    prediction_source: string;
    notes: string;
  }>;
};

type RawMetricSplit = {
  status: string;
  reason?: string;
  pixel_accuracy: number | null;
  mean_iou: number | null;
  per_class_iou: Array<{
    class_id: number;
    class_name: string;
    iou: number | null;
    intersection: number;
    union: number;
  }>;
};

type RawMetricsFile = {
  generated_at: string;
  model_artifact_name: string;
  validation: RawMetricSplit;
  test: RawMetricSplit;
};

function readJson<T>(filePath: string): T {
  return JSON.parse(fs.readFileSync(filePath, "utf8")) as T;
}

function splitMetrics(raw: RawMetricSplit): SplitMetrics {
  return {
    status: raw.status,
    reason: raw.reason,
    pixelAccuracy: raw.pixel_accuracy,
    meanIou: raw.mean_iou,
    perClassIou: raw.per_class_iou.map((item) => ({
      classId: item.class_id,
      className: item.class_name,
      iou: item.iou,
      intersection: item.intersection,
      union: item.union,
    })),
  };
}

export function getDemoData(): DemoData {
  const evaluationDir = path.join(process.cwd(), "public", "evaluation");
  const classes = readJson<RawClassFile>(path.join(evaluationDir, "classes.json"));
  const samples = readJson<RawSampleFile>(path.join(evaluationDir, "samples", "metadata.json"));
  const metrics = readJson<RawMetricsFile>(path.join(evaluationDir, "metrics.json"));

  return {
    generatedAt: metrics.generated_at || samples.generated_at,
    modelArtifactName: metrics.model_artifact_name,
    classes: classes.classes,
    samples: samples.samples.map((sample) => ({
      id: sample.id,
      sourceImage: sample.source_image,
      originalUrl: `/evaluation/samples/${sample.original}`,
      predictionUrl: `/evaluation/samples/${sample.prediction}`,
      overlayUrl: `/evaluation/samples/${sample.overlay}`,
      predictionSource: sample.prediction_source,
      notes: sample.notes,
    })),
    validation: splitMetrics(metrics.validation),
    test: splitMetrics(metrics.test),
  };
}

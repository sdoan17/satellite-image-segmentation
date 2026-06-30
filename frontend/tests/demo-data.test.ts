import { describe, expect, it } from "vitest";

import { getDemoData } from "../lib/demo-data";

describe("getDemoData", () => {
  it("loads curated sample, class, and evaluation artifacts from the synced public data", () => {
    const data = getDemoData();

    expect(data.samples).toHaveLength(2);
    expect(data.samples[0]).toMatchObject({
      id: "01-image1",
      originalUrl: "/evaluation/samples/01-image1-original.jpg",
      predictionUrl: "/evaluation/samples/01-image1-prediction.png",
      overlayUrl: "/evaluation/samples/01-image1-overlay.png",
      predictionSource: "generated_placeholder",
    });
    expect(data.classes.map((item) => item.name)).toEqual([
      "building",
      "land",
      "road",
      "vegetation",
      "water",
      "unlabeled",
    ]);
    expect(data.validation.status).toBe("not_run");
    expect(data.test.status).toBe("not_run");
  });
});

import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import DemoApp from "../components/DemoApp";
import { getDemoData } from "../lib/demo-data";

const data = getDemoData();

function makeFile() {
  return new File(["satellite pixels"], "tile.png", { type: "image/png" });
}

describe("DemoApp", () => {
  beforeEach(() => {
    vi.unstubAllEnvs();
    vi.restoreAllMocks();
  });

  it("opens on a curated sample with imagery, prediction, legend, and model-evidence context", () => {
    render(<DemoApp data={data} />);

    expect(screen.getByRole("heading", { name: /satellite segmentation demo/i })).toBeInTheDocument();
    expect(screen.getByRole("img", { name: /original imagery for 01-image1/i })).toHaveAttribute(
      "src",
      "/evaluation/samples/01-image1-original.jpg",
    );
    expect(screen.getByRole("img", { name: /model prediction overlay for 01-image1/i })).toHaveAttribute(
      "src",
      "/evaluation/samples/01-image1-overlay.png",
    );
    expect(within(screen.getByRole("region", { name: /class legend/i })).getByText(/building/i)).toBeInTheDocument();
    expect(screen.getByText(/not ground truth or authoritative geospatial analysis/i)).toBeInTheDocument();
    expect(screen.getByText(/validation evaluation has not been run/i)).toBeInTheDocument();
  });

  it("switches curated samples without needing an upload", async () => {
    const user = userEvent.setup();
    render(<DemoApp data={data} />);

    await user.click(screen.getByRole("button", { name: /02-image2/i }));

    expect(screen.getByRole("img", { name: /original imagery for 02-image2/i })).toHaveAttribute(
      "src",
      "/evaluation/samples/02-image2-original.jpg",
    );
  });

  it("shows a clear disabled upload state when no inference API URL is configured", async () => {
    const user = userEvent.setup();
    render(<DemoApp data={data} />);

    await user.upload(screen.getByLabelText(/upload a satellite-style image/i), makeFile());

    expect(screen.getByText(/live inference is not configured/i)).toBeInTheDocument();
    expect(screen.getByRole("img", { name: /original imagery for 01-image1/i })).toBeInTheDocument();
  });

  it("uploads to the configured inference API and renders returned prediction imagery", async () => {
    vi.stubEnv("NEXT_PUBLIC_INFERENCE_API_URL", "https://api.example.test");
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        input: { width: 16, height: 12 },
        prediction: {
          format: "png_base64",
          mask_png_base64: "bWFzaw==",
          overlay_png_base64: "b3ZlcmxheQ==",
          classes_present: [0, 4],
          resized: false,
        },
        classes: data.classes,
        disclaimer: "Model prediction for demonstration only; not authoritative geospatial analysis.",
      }),
    });
    vi.stubGlobal("fetch", fetchMock);
    const user = userEvent.setup();
    render(<DemoApp data={data} />);

    await user.upload(screen.getByLabelText(/upload a satellite-style image/i), makeFile());

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledWith("https://api.example.test/predict", expect.any(Object));
    });
    expect(screen.getByRole("img", { name: /uploaded model prediction/i })).toHaveAttribute(
      "src",
      "data:image/png;base64,b3ZlcmxheQ==",
    );
  });

  it("keeps curated samples available when upload inference fails", async () => {
    vi.stubEnv("NEXT_PUBLIC_INFERENCE_API_URL", "https://api.example.test");
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: false,
        json: async () => ({ detail: "Model is not loaded; inference is unavailable." }),
      }),
    );
    const user = userEvent.setup();
    render(<DemoApp data={data} />);

    await user.upload(screen.getByLabelText(/upload a satellite-style image/i), makeFile());

    expect(await screen.findByText(/model is not loaded/i)).toBeInTheDocument();
    expect(screen.getByRole("img", { name: /original imagery for 01-image1/i })).toBeInTheDocument();
  });
});

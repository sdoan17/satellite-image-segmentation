import fs from "node:fs";
import path from "node:path";
import { describe, expect, it } from "vitest";

describe("responsive CSS contract", () => {
  it("keeps mobile layout single-column and contains wide metric tables", () => {
    const css = fs.readFileSync(path.join(process.cwd(), "app", "globals.css"), "utf8");

    expect(css).toContain("@media (max-width: 900px)");
    expect(css).toContain("@media (max-width: 620px)");
    expect(css).toContain(".workspace,\n  .metric-cards {\n    grid-template-columns: 1fr;");
    expect(css).toContain(".image-grid {\n    grid-template-columns: 1fr;");
    expect(css).toContain(".table-wrap");
    expect(css).toContain("overflow-x: auto;");
  });
});

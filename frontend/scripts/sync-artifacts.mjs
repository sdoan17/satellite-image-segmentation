import { cp, mkdir, rm } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const frontendRoot = path.resolve(scriptDir, "..");
const repoRoot = path.resolve(frontendRoot, "..");
const source = path.join(repoRoot, "docs", "evaluation");
const target = path.join(frontendRoot, "public", "evaluation");

await rm(target, { force: true, recursive: true });
await mkdir(path.dirname(target), { recursive: true });
await cp(source, target, { recursive: true });

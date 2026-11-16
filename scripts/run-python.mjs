import { spawnSync } from "node:child_process";
import { existsSync } from "node:fs";
import { resolve } from "node:path";
import { fileURLToPath } from "node:url";

const repositoryRoot = fileURLToPath(new URL("../", import.meta.url));
const virtualenvPython =
  process.platform === "win32"
    ? resolve(repositoryRoot, ".venv", "Scripts", "python.exe")
    : resolve(repositoryRoot, ".venv", "bin", "python");
const python = process.env.PYTHON || (existsSync(virtualenvPython) ? virtualenvPython : "python");
const result = spawnSync(python, process.argv.slice(2), {
  cwd: repositoryRoot,
  stdio: "inherit",
});

if (result.error) {
  console.error(`Could not start Python interpreter "${python}": ${result.error.message}`);
  process.exitCode = 1;
} else {
  process.exitCode = result.status ?? 1;
}

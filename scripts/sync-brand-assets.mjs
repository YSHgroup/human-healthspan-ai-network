import { cp, mkdir, readdir } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const source = path.join(root, "public", "brand");
const applications = ["apps/social-web", "apps/personal-web", "apps/researcher-web", "apps/admin"];
const files = await readdir(source);

if (files.length === 0) {
  throw new Error(`No shared brand assets found in ${source}`);
}

for (const application of applications) {
  const destination = path.join(root, application, "public", "brand");
  await mkdir(destination, { recursive: true });

  for (const file of files) {
    await cp(path.join(source, file), path.join(destination, file));
  }
}

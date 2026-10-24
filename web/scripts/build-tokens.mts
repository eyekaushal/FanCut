// Writes src/app/tokens.css from src/design/tokens.ts. Run with `npm run tokens`.
import { writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

import { tokensCss } from "../src/design/tokens.ts";

const out = fileURLToPath(new URL("../src/app/tokens.css", import.meta.url));
writeFileSync(out, tokensCss());
console.log(`wrote ${out}`);

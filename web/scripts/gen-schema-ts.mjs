// Converts the Pydantic-emitted JSON Schema (lib/web_export.py's
// build_json_schema()) into web/types/schema.ts. Regenerate with:
//   python -m lib.web_export && node web/scripts/gen-schema-ts.mjs
import { compile } from "json-schema-to-typescript";
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const schemaPath = path.join(__dirname, "_generated-schema.json");
const outPath = path.join(__dirname, "..", "types", "schema.ts");

const schema = JSON.parse(readFileSync(schemaPath, "utf-8"));

const banner = `/**
 * AUTO-GENERATED from lib/transforms/schema.py (the Pydantic DataPoint /
 * SegmentFile models) via lib/web_export.py + web/scripts/gen-schema-ts.mjs.
 * Do not hand-edit — a schema change should surface here as a compile error,
 * not a silent bug. See web/types/bundle.ts for the flattened "Figure" shape
 * actually shipped in the JSON bundle (produced by _context.py's _fmt()).
 */
`;

const ts = await compile(schema, "SegmentFile", {
  bannerComment: "",
  additionalProperties: false,
});

mkdirSync(path.dirname(outPath), { recursive: true });
writeFileSync(outPath, banner + "\n" + ts);
console.log(`Wrote ${outPath}`);

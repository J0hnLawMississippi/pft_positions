import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import Ajv2020 from "ajv/dist/2020.js";
import addFormats from "ajv-formats";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const schemaPath = path.resolve(__dirname, "../schema/position-snapshot.v0.schema.json");
const examplesDir = path.resolve(__dirname, "../schema/examples");

const schema = JSON.parse(fs.readFileSync(schemaPath, "utf8"));

const ajv = new Ajv2020({ allErrors: true, strict: false });
addFormats(ajv);

const validate = ajv.compile(schema);

const exampleFiles = [
  "delta-one.example.json",
  "option.example.json",
  "yield.example.json"
];

let failures = 0;

for (const file of exampleFiles) {
  const payloadPath = path.join(examplesDir, file);
  const payload = JSON.parse(fs.readFileSync(payloadPath, "utf8"));

  const ok = validate(payload);
  if (!ok) {
    failures += 1;
    console.error(`FAIL ${file}`);
    for (const err of validate.errors ?? []) {
      console.error(`  - ${err.instancePath || "/"} ${err.message}`);
    }
  } else {
    console.log(`PASS ${file}`);
  }
}

if (failures > 0) {
  process.exit(1);
}

console.log("All example payloads validated successfully.");

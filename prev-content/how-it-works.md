 ## 1) Planner flow (abstract, semantic)

  The planner does not hardcode column names or schemas. It declares slots and entity schemas that describe intent. Example step graph:

  1. Fetch data
      - Output slot: raw_files
      - Entity: generic.file_download_result (or generic.source_manifest if multiple)
      - Kind: file.binary or file.text
  2. Normalize to rows
      - Input slot: raw_files
      - Output slot: normalized_rows
      - Entity: generic.table_row (generic rows)
      - Kind: table.json_rows
  3. Transform for charts
      - Input: normalized_rows
      - Output: aggregated_rows
      - Entity: generic.table_row or a chart‑specific entity (domain pack dependent)
      - Kind: dataset.aggregated_rows
  4. Render website
      - Input: aggregated_rows
      - Output: site_bundle
      - Entity: web.site_bundle
      - Kind: web.bundle.static

  Planner focuses on slots and entities, not column lists.

  ———

  ## 2) Compiler flow (concrete resolution)

  The compiler:

  - Picks the concrete profile IDs for each slot.
  - Inserts adapters if needed (CSV → json_rows).
  - Builds the compiled contract (compiled_step_contract_v1) for runtime enforcement.

  This is where compatibility is resolved, not in the planner.

  ———

  ## 3) Where do “15 fields” live?

  The fields are not hardcoded into the planner output. They land in the schema contract that the normalizer emits, or in the adapter output.

  Two patterns:

  ### A) “Known schema” profile

  If the domain pack has a specific profile (e.g. finance.table.json_rows.ledger_entries.v1), the contract profile already declares the required fields. The compiler binds to that profile,
  and runtime enforces required fields.

  ### B) “Dynamic schema” profile

  If it’s a user‑specified API with unknown fields, the planner uses a generic rows profile. Then the normalizer step emits a schema profile artifact (or a schema envelope) describing the
  fields it actually found. That schema artifact becomes the single source of truth for downstream steps.

  This is how we allow dynamic columns without forcing the planner to hardcode them.

  ———

  ## 4) How does the planner know which fields are used?

  It doesn’t. It states intent, and the system infers actual fields in the normalization step, then locks them into an artifact contract.

  If the user says “extract fields A, B, C,” the planner puts those in the normalizer step objective and the compiled contract enforces that those columns appear in the output. That is the
  only place fields are explicitly named.

  ———

  ## 5) Example dynamic data path (CSV with 15 columns)

  1. Normalize CSV → json_rows
      - Output contract: generic.table.json_rows.normalized_rows.v1
      - Required fields: only what the user requested explicitly (A, B, C)
      - Optional fields: the rest (auto‑included, allowed)
  2. Schema profile artifact
      - Output: output/schema_profile.json
      - Captures full field list + types
      - Runtime enforces consistency for downstream steps

  ———

  ## 6) Why this works

  - Planner remains abstract.
  - Compiler resolves concrete profiles and adapters.
  - Normalizer converts unknowns into explicit schema artifacts.
  - Runtime enforces the compiled contract.
  - Single source of truth stays in the contract library + emitted schema artifacts.

  ———

  # Example: Website + Charts from API (Simple Explanation)

  User asks:
  “Build a two‑page website with tabs and charts from an API. First extract these fields, normalize into objects, then render the charts.”

  How the system responds:

  1. Fetch the data
     Download the API response as a raw file.
  2. Normalize the data
     Convert the raw API data into structured rows (JSON rows).
     This is where we extract the requested fields (e.g., date, revenue, region).
  3. Transform for charts
     Aggregate or reshape the rows to the exact format needed for charts/tables.
  4. Render the website
     Use the transformed dataset to build a two‑page site with tabs and charts.

  Key point:
  The planner doesn’t hardcode every field.
  It says “normalize rows,” and the normalizer step produces a schema profile that lists the actual fields it found.

  ———

  # Planner Output (Abstract, Slot‑Based)

  This is what the planner emits: it’s semantic and does not rely on filenames.

  {
    "mission": "Build a two-page website with charts from API data",
    "steps": [
      {
        "label": "Fetch API data",
        "objective": "Download API data for charts",
        "success_criteria": "Raw API data file exists",
        "domain_pack_ids": ["website-build", "research-synthesis"],
        "workflow_pack_ids": ["file-acquisition"],
        "policy_profile_id": "strict.allow-normalizers.v1",
        "abstract_outputs": [
          {
            "slot": "raw_files",
            "entity_schema_id": "generic.file_download_result",
            "preferred_kind_keys": ["file.text", "file.binary"],
            "provenance_policy": "preferred",
            "path_hint": "output/raw_api.json"
          }
        ]
      },
      {
        "label": "Normalize rows",
        "objective": "Extract fields date, revenue, region and normalize to rows",
        "success_criteria": "Normalized row table exists",
        "domain_pack_ids": ["data-merge-transform"],
        "workflow_pack_ids": ["normalize-transform"],
        "policy_profile_id": "strict.allow-normalizers.v1",
        "abstract_inputs": [
          {
            "slot": "raw_files",
            "required": true,
            "entity_schema_id": "generic.file_download_result",
            "accepted_kind_keys": ["file.text", "file.binary"],
            "provenance_policy": "preferred"
          }
        ],
        "abstract_outputs": [
          {
            "slot": "normalized_rows",
            "entity_schema_id": "generic.table_row",
            "preferred_kind_keys": ["table.json_rows"],
            "provenance_policy": "required",
            "path_hint": "output/normalized_rows.json"
          }
        ]
      },
      {
        "label": "Prepare chart data",
        "objective": "Aggregate rows for charts and tables",
        "success_criteria": "Aggregated dataset exists",
        "domain_pack_ids": ["data-merge-transform"],
        "workflow_pack_ids": ["analyze-score-rank"],
        "policy_profile_id": "strict.allow-normalizers.v1",
        "abstract_inputs": [
          {
            "slot": "normalized_rows",
            "required": true,
            "entity_schema_id": "generic.table_row",
            "accepted_kind_keys": ["table.json_rows"]
          }
        ],
        "abstract_outputs": [
          {
            "slot": "aggregated_rows",
            "entity_schema_id": "generic.table_row",
            "preferred_kind_keys": ["dataset.aggregated_rows"],
            "path_hint": "output/aggregated_rows.json"
          }
        ]
      },
      {
        "label": "Render website",
        "objective": "Create two-page website with tabs and charts",
        "success_criteria": "Website bundle exists",
        "domain_pack_ids": ["website-build"],
        "workflow_pack_ids": ["render-website"],
        "policy_profile_id": "deploy.human-review-required.v1",
        "abstract_inputs": [
          {
            "slot": "aggregated_rows",
            "required": true,
            "entity_schema_id": "generic.table_row",
            "accepted_kind_keys": ["dataset.aggregated_rows"]
          }
        ],
        "abstract_outputs": [
          {
            "slot": "site_bundle",
            "entity_schema_id": "web.site_bundle",
            "preferred_kind_keys": ["web.bundle.static"],
            "path_hint": "output/site_bundle.zip"
          }
        ]
      }
    ]
  }

  ———

  # What the Compiler Does (Concrete Resolution)

  The compiler resolves actual profile IDs and inserts adapters if needed. Example results:

  - raw_files → generic.file_download_result.v1
  - normalized_rows → generic.table.json_rows.normalized_rows.v1
  - aggregated_rows → generic.dataset.aggregated_rows.aggregated_rows.v1
  - site_bundle → web.web.bundle.static.site_bundle.v1

  If the API output is CSV, the compiler inserts this adapter automatically:

  adapter.table-csv.__to__.generic.table.json_rows.normalized_rows.v1

  ———

  # How “15 fields” are handled (Simple answer)

  - The planner doesn’t list all 15 fields.
  - The normalizer step extracts fields requested by the user (e.g., date, revenue, region).
  - The normalizer emits a schema profile artifact that lists all 15 fields it found.
  - Downstream steps use that schema profile as the single source of truth.

  So the fields are dynamic, but still enforced.
---



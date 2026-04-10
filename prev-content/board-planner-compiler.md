Yes — now that the schemas/tables exist, the next critical piece is exactly what you’re asking for:

1. **a planner/compiler resolution algorithm**, and
2. **small but important planner + operator prompt changes** so the system stops inferring structure from filenames/paths and starts reasoning from explicit contracts instead. That is exactly the gap your board brief identified. 

## Short answer

My recommendation is:

* **Planner = abstract contract intent**
* **Compiler = concrete profile/adapters resolution**
* **Runtime = enforcement**

And for prompts:

* **Planner prompt must change materially**
* **Operator prompt needs only a small contract-aware delta**, not a full rewrite

So: **not fully transparent**, but also **not a giant behavioral change** for the operator.

---

# 1) Recommended split: planner vs compiler vs runtime

Your board brief asked whether profile assignment should be planner-driven, compiler-driven, or hybrid. I recommend a **hybrid model**. 

## Planner responsibilities

The planner should choose:

* **domain packs**
* **workflow packs**
* **step purpose / role**
* **semantic intent** of inputs/outputs
* **slot names**
* **policy strictness hints**
* optionally a **preferred representation family** (e.g. `table.json_rows`, `report.html`)

The planner should **not** be the final authority on:

* exact `profile_id`
* adapter insertion
* compatibility resolution
* fallback behavior

That belongs in the compiler.

## Compiler responsibilities

The compiler should:

* resolve abstract planner intents into **concrete `profile_id`s**
* choose **compatible producers/consumers**
* insert **adapter/normalizer steps** if allowed by policy
* fail closed if no safe connection exists
* emit a **compiled step I/O contract** for runtime

## Runtime responsibilities

Runtime should:

* validate actual produced artifacts against compiled contracts
* reject mismatches
* attach artifact manifests to downstream inputs
* never let a consumer infer shape from filename/path alone

---

# 2) The core planning object you need: abstract I/O declarations

The planner should no longer emit only:

* role
* task
* payload

It should emit **step contracts** in abstract form.

## Recommended planner output per step

```json
{
  "step_id": "reconcile_time_to_invoice",
  "role": "ai_autonomous_worker",
  "purpose": "Compare normalized time entries to invoice lines and identify discrepancies",
  "domain_packs": ["billing-audit"],
  "workflow_packs": ["normalize-transform", "reconcile-compare"],
  "inputs": [
    {
      "slot": "time_entries",
      "required": true,
      "entity_schema_id": "billing.time_entry",
      "accepted_kind_keys": ["table.json_rows", "table.csv"],
      "preferred_profile_ids": ["billing.table.json_rows.time_entries.v1"],
      "row_grain": "one row per time entry",
      "provenance_policy": "preferred"
    },
    {
      "slot": "invoice_lines",
      "required": true,
      "entity_schema_id": "billing.invoice_line_item",
      "accepted_kind_keys": ["table.json_rows", "table.csv"],
      "preferred_profile_ids": ["billing.table.json_rows.invoice_line_items.v1"],
      "row_grain": "one row per invoice line",
      "provenance_policy": "preferred"
    }
  ],
  "outputs": [
    {
      "slot": "discrepancy_rows",
      "required": true,
      "entity_schema_id": "billing.discrepancy_row",
      "preferred_kind_keys": ["table.json_rows"],
      "preferred_profile_ids": ["billing.table.json_rows.discrepancy_rows.v1"],
      "row_grain": "one row per discrepancy",
      "provenance_policy": "required"
    }
  ],
  "policy_profile_id": "strict.allow-normalizers.v1"
}
```

This is the key change.
The planner should think in terms of:

* **what semantic entity is needed**
* **what representation families are acceptable**
* **what slot names connect steps**
* **what policy governs adaptation**

Not just “take file X and do Y.”

---

# 3) The compiler resolution algorithm (prescriptive)

This is the exact algorithm I would recommend you implement.

---

## Phase A — Build the contract universe for this run

### Inputs to compiler

* active artifact kinds
* active contract profiles
* active domain packs
* active workflow packs
* active policy profiles
* active adapter/normalizer profiles
* current artifact inventory (uploaded files, prior step outputs, batch manifests, KB refs, etc.)
* planner abstract plan

### Build `ArtifactInventory`

For every available artifact, normalize into a compiler-friendly inventory row:

```json
{
  "artifact_id": "art_123",
  "path": "uploads/time_entries.csv",
  "kind_key": "table.csv",
  "profile_id": null,
  "entity_schema_id": null,
  "row_grain": null,
  "domain_tags": ["billing"],
  "source_step_id": null,
  "producer_confidence": 0.0,
  "sha256": "..."
}
```

If an input artifact already has a validated profile, populate it. If not, it enters as **untyped / weakly typed** and must usually pass through normalization before strong consumers use it.

---

## Phase B — Resolve candidate packs (lightweight)

If the planner already chose packs, use them.
If not, infer a shortlist from:

1. explicit user nouns/verbs
2. input artifact MIME/path heuristics
3. prior session context / mission type
4. known connectors

### Example

For “audit these resumes and rank candidates”:

* domain packs:

  * `resume-audit`
  * maybe `research-synthesis`
* workflow packs:

  * `file-batch-load`
  * `normalize-transform`
  * `analyze-score-rank`
  * `render-report`

This shortlist limits compiler search space.

---

## Phase C — Resolve each step in topological order

For each step:

### Step C1 — Resolve inputs per slot

For each input slot, score candidate producers in this order:

### Rank 1 — Exact profile match

* same `profile_id`
* same `entity_schema_id`
* same `kind_key`
* same or acceptable row grain

### Rank 2 — Same semantic entity, acceptable representation

* `entity_schema_id` matches
* `kind_key` is in accepted kinds
* no adapter needed

### Rank 3 — Same semantic entity, adapter available

* `entity_schema_id` matches
* representation differs
* adapter exists from producer kind/profile → accepted input family

### Rank 4 — Generic compatible profile

* generic profile acceptable under current domain/workflow policy
* only if policy allows generic fallback

### Rank 5 — Incompatible

* no compatible producer
* compiler must either insert a normalizer or fail

---

### Step C2 — If no compatible producer exists, insert adapter if allowed

If policy profile allows normalizers/adapters:

* choose the cheapest safe adapter
* insert an explicit step before the consumer

Example:

* producer = `table.csv`
* consumer wants `billing.table.json_rows.time_entries.v1`
* compiler inserts:

  * `adapter.csv_to_json_rows.time_entries.v1`

The critical rule:
**adaptation must be explicit in the graph**.
Never silently coerce.

---

### Step C3 — Resolve output profile

For each output slot:

1. Start with planner’s `preferred_profile_ids`
2. If none, filter profiles by:

   * domain pack
   * workflow pack
   * `entity_schema_id`
   * preferred kind family
3. Rank profiles:

   * exact domain+workflow fit
   * generic profile with same entity
   * generic profile with same kind only (only if policy allows)

Then freeze:

* `output_profile_id`
* `output_kind_key`
* `output_entity_schema_id`
* `row_grain`
* provenance requirements

---

### Step C4 — Emit compiled step contract

Compiler emits a fully concrete contract:

```json
{
  "step_id": "reconcile_time_to_invoice",
  "role": "ai_autonomous_worker",
  "inputs": [
    {
      "slot": "time_entries",
      "artifact_id": "art_norm_time_entries",
      "profile_id": "billing.table.json_rows.time_entries.v1"
    },
    {
      "slot": "invoice_lines",
      "artifact_id": "art_norm_invoice_lines",
      "profile_id": "billing.table.json_rows.invoice_line_items.v1"
    }
  ],
  "outputs": [
    {
      "slot": "discrepancy_rows",
      "profile_id": "billing.table.json_rows.discrepancy_rows.v1"
    }
  ],
  "policy_profile_id": "strict.allow-normalizers.v1"
}
```

This is what the runtime passes to the step executor.

---

## Phase D — Global DAG validation

After all steps are compiled, run a final graph check:

* every required input slot is bound
* all inserted adapters are legal under policy
* no two producers bind the same slot ambiguously
* no consumer expects fields absent from its chosen producer profile
* no filename/path-only inference remained in the graph

If this fails, compiler fails closed before runtime.

---

# 4) Compatibility semantics (explicit rules)

Your brief asked for producer/consumer compatibility guidance. Here’s the version I would adopt. 

## Case A — Producer stronger than consumer

Example:

* producer profile has more fields than consumer needs
* same entity, same grain

**Result:** compatible
Extra fields are okay if consumer policy allows them.

## Case B — Consumer stronger than producer

Example:

* consumer requires `employee_id`, producer lacks it

**Result:** incompatible
Needs adapter/normalizer or fail closed.

## Case C — Same entity, different representation

Example:

* producer = CSV time entries
* consumer = JSON rows time entries

**Result:** compatible only through adapter
No silent coercion.

## Case D — Same entity, different grain

Example:

* producer = daily summary by employee
* consumer = one row per time entry

**Result:** incompatible
Unless a specific grain adapter exists (usually impossible in this direction).

## Case E — Producer finer grain than consumer

Example:

* producer = time entry rows
* consumer = employee-day aggregate

**Result:** compatible only through explicit aggregation adapter

## Case F — Partial compatibility

Example:

* fields mostly overlap, but provenance or required columns differ

**Result:** adapter or fail
Never “close enough.”

---

# 5) What must change in the planner prompt

This is where you need the biggest prompt delta.

---

## Add section: “CONTRACT-AWARE PLANNING”

The planner must be told:

* never infer semantic structure from filename/path
* plan using **slot semantics**
* choose domain/workflow packs
* declare abstract I/O requirements
* let compiler choose concrete profiles

### Ready-to-paste planner prompt addition

```md
## CONTRACT-AWARE PLANNING

You are planning a graph of steps that will be compiled against a contract library.

### Rules

1. Do NOT assume semantic structure from filenames or file extensions alone.
   - A path like `schema_profile.json` or `report.csv` is only a locator, not a semantic guarantee.

2. For each step, declare abstract I/O requirements using:
   - `slot`
   - `entity_schema_id`
   - acceptable or preferred `kind_key`
   - optional preferred `profile_id`
   - `row_grain`
   - `provenance_policy`

3. Prefer choosing:
   - relevant `domain_packs`
   - relevant `workflow_packs`
   - semantic intent
   instead of hardcoding profile IDs unless the fit is obvious.

4. Assume a compiler will:
   - resolve concrete profile IDs
   - insert adapters/normalizers if policy allows
   - reject incompatible handoffs

5. Keep slot names stable and semantically meaningful.
   Good examples:
   - `source_manifest`
   - `raw_files`
   - `document_spans`
   - `normalized_rows`
   - `joined_rows`
   - `findings`
   - `report_artifact`
   - `site_spec`
   - `site_bundle`
   - `change_set`
   - `validation_results`
```

---

## Add section: “WHEN TO REQUEST NORMALIZATION”

```md
If an input artifact is weakly typed (uploaded file, generic CSV, unknown JSON object), prefer an explicit normalization step before any strong consumer step.

Examples:
- generic CSV -> canonical time entries
- batch file load -> document manifest
- extracted document spans -> legal clause findings
```

---

## Change planner output schema

Your planner should emit **step I/O declarations**, not just `payload.deliverable` style instructions for all steps.

You can still keep `payload`, but add `inputs[]` and `outputs[]` in the abstract contract form.

---

# 6) What should change in the operator-executor prompt

Short answer: **mostly transparent, but not fully transparent**.

If runtime/compiler do their job, the operator does not need to know the full registry.
But it **does** need a few new rules so it consumes compiled contracts correctly.

---

## Minimal operator-executor prompt delta

### Add section: “CONTRACT CONSUMPTION RULES”

```md
## CONTRACT CONSUMPTION RULES

When a step arrives with compiled input/output contracts:

1. Treat the compiled contract as authoritative.
   - Use `profile_id`, `kind_key`, `entity_schema_id`, `row_grain`, and declared slots as the source of truth.

2. Do NOT infer semantic structure from:
   - filename
   - extension
   - generic path names
   - previous assumptions about similarly named artifacts

3. If the actual artifact contents appear incompatible with the compiled contract:
   - stop
   - report the mismatch clearly
   - do not “make it work” by guessing
   - request a normalizer or fail closed

4. Produce outputs that match the declared output contract.
   - If auxiliary artifacts are created, clearly distinguish them from the primary output slot.
```

---

## Add to execution protocol

Before the step does real work:

```md
- Read the compiled input contract first.
- Confirm what each slot semantically contains.
- Validate that the expected structure matches the task before writing code or transforming data.
```

---

## Add anti-error

```md
- Never infer JSON/object/row structure from a filename or path.
- Never silently adapt incompatible input shapes.
```

---

# 7) Should the operator know about packs?

Usually: **no**.

The operator should mainly consume:

* compiled slot bindings
* concrete `profile_id`s
* maybe policy strictness

It does **not** need the full pack list unless:

* you want it to explain reasoning/debugging,
* or it needs to emit a derived work item with contract hints.

So for the operator prompt, packs are mostly **transparent**.
Profiles and compiled slot contracts are **not** transparent.

---

# 8) Example: resume auditing (batch file loading)

This is a great example of why you need both workflow packs and compiler resolution.

## Planner abstract plan

Step 1:

* `domain_packs`: `resume-audit`
* `workflow_packs`: `file-batch-load`
* output slot:

  * `batch_manifest`
  * entity: `resume.document_ref`
  * preferred kind: `file.batch_manifest`

Step 2:

* `domain_packs`: `resume-audit`
* `workflow_packs`: `ingest-materialize`, `analyze-score-rank`
* input: `batch_manifest`
* output: `candidate_profiles`

  * entity: `resume.candidate_profile`
  * preferred kind: `table.json_rows`

Step 3:

* output: `candidate_score_rows`
* entity: `resume.candidate_score_row`

Step 4:

* output: `report_artifact`
* preferred kind: `report.html`

## Compiler then resolves

* exact manifest profile
* candidate row profile
* score row profile
* HTML report profile
* adapters if resumes come as mixed PDF/DOCX/plaintext

This is exactly the system you want.

---

# 9) Governor recommendation

## Do this now

1. Implement the **hybrid planner/compiler model**
2. Update planner prompt to emit **abstract I/O contracts**
3. Add a **contract consumption block** to operator-executor
4. Keep most of operator behavior unchanged otherwise
5. Make compiler the only place that:

   * resolves concrete profile ids
   * inserts adapters
   * decides compatibility

## Do not do this

* do not make planner memorize the full registry
* do not make operator infer shapes from paths
* do not silently adapt mismatches at runtime

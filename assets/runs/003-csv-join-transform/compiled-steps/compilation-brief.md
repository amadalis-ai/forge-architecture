# Execution Plan Narrative: CSV Consolidation to JSON

## 1. Compilation Overview

This execution plan orchestrates the transformation of two CSV datasets into a consolidated JSON structure. The plan was compiled to meet a specific objective: **profile two input CSV files, validate their schemas, then perform a join operation to produce a single enriched JSON output**.

**Governance Posture:** The plan operates under a **strict output-binding enforcement model** with immutable artifact declarations. No policy profile is explicitly assigned, meaning the plan defaults to baseline validation and repair strategies. The system enforces declared outputs at compile time and validates their presence and format at runtime.

**What Was Compiled:**
- **2 sequential steps** with explicit artifact dependencies
- **4 required capabilities** per step (profiling, joining, schema validation, JSON serialization)
- **Strict validator rules** requiring declared outputs and input artifact references
- **Repair strategies** allowing up to 6 retries per step before failure

---

## 2. Domain & Workflow Packs

### Current State
**No domain or workflow packs are bound to this plan.**

This is a **minimal, self-contained execution model**. The plan does not leverage pre-built domain expertise (e.g., financial data handling, HR workflows) or reusable workflow templates. Instead, each step is defined as a standalone task with explicit capability requirements.

**Implication:** The execution engine will rely entirely on the **sandbox.session backend** and the **skills bound at step level** (see Section 7) to fulfill the required capabilities. There is no abstraction layer for common patterns like "CSV profiling" or "data joining"—these must be implemented inline within each step's execution context.

---

## 3. Governance & Policy

### Policy Profile Assignment
**No explicit policy profile is assigned** (`policy_profile_id: null` for both steps).

### Default Governance Behavior

When no policy profile is specified, the plan inherits the **baseline validation and repair posture**:

| Aspect | Behavior |
|--------|----------|
| **Output Validation** | `fail_on_missing_outputs: true` — any missing declared output causes step failure |
| **Input Enforcement** | `require_input_artifact_refs: true` — steps must declare artifact dependencies |
| **Output Binding** | `enforce_compiled_output_bindings: true` — outputs must match compiled declarations exactly |
| **Repair Strategy** | `retry_same_contract` — failed steps retry with identical execution parameters (up to 6 times) |
| **Immutability** | `immutable_output_bindings: true` — output paths cannot be changed after compilation |

### Execution Constraints

- **Timeout ceiling:** 1,800,000 ms (30 minutes) per step
- **Tool call limit:** 3 calls per step (e.g., read CSV, validate schema, write JSON)
- **Retry ceiling:** 6 attempts per step before declaring failure

---

## 4. Execution Contracts

### Step 1: Profile Input CSVs

**Step ID:** `ps-0-profile-input-csvs`

| Attribute | Value |
|-----------|-------|
| **Execution Mode** | `hybrid` — combines tool invocation and inline logic |
| **Backend** | `sandbox.session` — isolated execution environment |
| **Step Kind** | `hybrid_task` — flexible execution pattern |
| **Execution Contract Pattern** | `other` — custom pattern not matching standard templates |
| **Step Nature** | `HYBRID` — may involve both deterministic and exploratory logic |

#### Repair Strategy
**Pattern:** `retry_with_small_fix`

If the step fails (e.g., CSV file not found, schema parsing error):
1. The system retries the same execution contract up to 6 times
2. Between retries, it may apply **small fixes** (e.g., adjust file path, handle encoding issues)
3. If all retries exhaust, the plan fails and blocks Step 2

#### Tool Limits
- **Allowed tools:** `sandbox.session` only
- **Call budget:** 3 tool calls (e.g., read time_entries.csv, read rates.csv, write schema_profile2.json)

#### Success Criteria
The step succeeds **only if**:
- `output/schema_profile2.json` is created as valid JSON
- The profile contains results for **both** input CSVs
- It explicitly reports **753 rows** for `attachments/time_entries.csv`
- It reports a numeric row count for `attachments/rates.csv`
- It records schema mismatches, nulls, and type mismatches **without silently correcting them**

---

### Step 2: Join Entries to Rates

**Step ID:** `ps-1-join-entries-to-rates`

| Attribute | Value |
|-----------|-------|
| **Execution Mode** | `code` — script-based execution |
| **Backend** | `sandbox.session` — isolated execution environment |
| **Step Kind** | `code_task` — deterministic code execution |
| **Execution Contract Pattern** | `single_shot_artifact_production` — one execution, one output artifact |
| **Step Nature** | `DETERMINISTIC` — repeatable, no randomness or exploration |

#### Repair Strategy
**Pattern:** `replace_prior_script_on_primary_output_failure`

If the step fails (e.g., join logic error, missing schema profile):
1. The system retries the same execution contract up to 6 times
2. If the primary output (`output/joined_entries2.json`) is missing or invalid, the system may **replace the prior script** with a corrected version
3. This allows for logic fixes (e.g., correcting the join condition) without re-running Step 1

#### Tool Limits
- **Allowed tools:** `sandbox.session` only
- **Call budget:** 3 tool calls (e.g., read schema profile, read CSVs, write joined output)

#### Success Criteria
The step succeeds **only if**:
- `output/joined_entries2.json` is created as valid JSON
- The join uses the condition: `contract_ref = contract_id`
- The step **reads** `output/schema_profile2.json` before joining (dependency on Step 1)
- Every joined row includes a boolean `rate_match` field
- `rate_match` is `true` if `billed_rate` equals `hourly_rate`, `false` otherwise

---

## 5. Artifact Flow

### Data Movement Between Steps

```
Step 1: Profile Input CSVs
├── Input: attachments/time_entries.csv (753 rows)
├── Input: attachments/rates.csv (unknown row count)
└── Output: output/schema_profile2.json
    └── Contains: row counts, column names, types, null flags, mismatches

Step 2: Join Entries to Rates
├── Input: output/schema_profile2.json (from Step 1)
├── Input: attachments/time_entries.csv (re-read)
├── Input: attachments/rates.csv (re-read)
└── Output: output/joined_entries2.json
    └── Contains: joined rows with rate_match boolean
```

### Artifact Roles & Locations

| Artifact | Role | Location | Step | Mutability |
|----------|------|----------|------|-----------|
| `output/schema_profile2.json` | Schema profile (primary) | Workspace | 1 → 2 | Immutable after Step 1 |
| `output/joined_entries2.json` | Joined dataset (primary) | Workspace | 2 | Immutable after Step 2 |
| `output/step_result.json` | Metadata (secondary) | Sandbox | 1, 2 | Ephemeral |
| `meta/mcp-tools/journal.ndjson` | Execution log | Sandbox | 1 | Ephemeral |
| `meta/mcp-tools/calls.tar.gz` | Tool call archive | Sandbox | 1 | Ephemeral |

**Key Dependency:** Step 2 **must** read the schema profile from Step 1 before performing the join. If Step 1 fails or produces invalid JSON, Step 2 is blocked.

---

## 6. Validation & Safety

### Validator Rules (Applied to Both Steps)

| Rule | Enforcement | Consequence |
|------|-------------|------------|
| `fail_on_missing_outputs` | **Strict** | If any declared output is missing, the step fails immediately |
| `require_declared_outputs` | **Strict** | All outputs must be declared in the plan; undeclared outputs are ignored |
| `require_input_artifact_refs` | **Strict** | Steps must explicitly reference input artifacts; implicit file reads are rejected |
| `enforce_compiled_output_bindings` | **Strict** | Output paths must match compiled declarations exactly (no runtime path changes) |

### Repair Policies

#### Step 1 Repair Policy
```
strategy: retry_same_contract
max_retries: 6
block_on_missing_inputs: true
immutable_output_bindings: true
```

- **Behavior:** If profiling fails, retry up to 6 times with the same execution parameters
- **Blocking:** If input CSVs are missing, do not retry; fail immediately
- **Output Paths:** Cannot be changed after compilation; `output/schema_profile2.json` is fixed

#### Step 2 Repair Policy
```
strategy: retry_same_contract
max_retries: 6
block_on_missing_inputs: true
immutable_output_bindings: true
```

- **Behavior:** If joining fails, retry up to 6 times with the same execution parameters
- **Blocking:** If `output/schema_profile2.json` is missing (Step 1 failure), do not retry; fail immediately
- **Output Paths:** Cannot be changed after compilation; `output/joined_entries2.json` is fixed

### Safety Guarantees

1. **No Silent Corrections:** Step 1 explicitly records schema issues instead of auto-correcting them
2. **Immutable Outputs:** Once compiled, output paths cannot be changed at runtime
3. **Dependency Blocking:** Step 2 cannot execute until Step 1 produces valid output
4. **Audit Trail:** All tool calls and execution logs are captured in `meta/mcp-tools/`

---

## 7. Skill & Tool Bindings

### Step 1: Profile Input CSVs

#### Recommended Skills
**None explicitly bound** (`recommended_skill_ids: []`)

#### Required Capabilities
The step must provide these capabilities through the execution backend:

| Capability | Purpose |
|-----------|---------|
| `csv profiling` | Read CSV files and extract metadata (row count, column names) |
| `schema validation` | Verify column types and structure |
| `null detection` | Identify and count null/missing values |
| `type checking` | Detect type mismatches (e.g., numeric column with text values) |
| `json serialization` | Write profile results as valid JSON |

#### Tool Bindings
- **Allowed tools:** `sandbox.session` (single tool)
- **Capability:** Provides a sandboxed Python/Node.js environment with file I/O and JSON libraries

**What This Enables:**
- Read both CSV files from the workspace
- Parse headers and sample rows
- Count rows and detect nulls
- Serialize results to JSON without external dependencies

---

### Step 2: Join Entries to Rates

#### Recommended Skills
```
- skill.system.sandbox
- skill.data.transform
```

These skills are **recommended** but not required. They provide:

| Skill | Capability |
|-------|-----------|
| `skill.system.sandbox` | Optimized sandbox execution (faster startup, better resource isolation) |
| `skill.data.transform` | Pre-built join and transformation logic (optional acceleration) |

#### Required Capabilities
The step must provide these capabilities:

| Capability | Purpose |
|-----------|---------|
| `csv join` | Perform inner/left join on contract_ref = contract_id |
| `schema-aware transformation` | Use schema profile from Step 1 to guide join logic |
| `boolean derivation` | Compute rate_match = (billed_rate == hourly_rate) for each row |
| `json serialization` | Write joined dataset as valid JSON |

#### Tool Bindings
- **Allowed tools:** `sandbox.session` (single tool)
- **Capability:** Provides a sandboxed environment with CSV/JSON libraries and data transformation functions

**What This Enables:**
- Load schema profile from Step 1
- Read both input CSVs
- Perform the join on the specified key
- Compute the `rate_match` boolean column
- Serialize the result to JSON

---

## Summary: Execution Governance

| Dimension | Configuration |
|-----------|---------------|
| **Compilation Model** | Strict output-binding enforcement; no policy profile override |
| **Execution Pattern** | Sequential (Step 1 → Step 2); Step 2 blocked until Step 1 succeeds |
| **Repair Strategy** | Retry-same-contract with up to 6 attempts per step |
| **Tool Isolation** | Single backend (`sandbox.session`) for both steps |
| **Skill Leverage** | Step 1 uses baseline capabilities; Step 2 optionally uses data transformation skills |
| **Safety Posture** | Immutable outputs, explicit error recording, dependency blocking |
| **Audit Trail** | All tool calls and logs captured in `meta/mcp-tools/` |

This plan prioritizes **correctness and auditability** over flexibility. The immutable output bindings and strict validator rules ensure that the final artifacts (`schema_profile2.json` and `joined_entries2.json`) are produced reliably and can be traced back to their execution context.
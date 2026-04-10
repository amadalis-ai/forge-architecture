# Execution Plan Narrative: JSONPlaceholder Data Retrieval, Analysis & Reporting

## 1. Compilation Overview

This execution plan orchestrates a **four-step data pipeline** that fetches, normalizes, analyzes, and renders insights from the JSONPlaceholder public API. The plan was compiled with a **permissive governance posture** (generic inference allowed) suitable for exploratory data work, with deterministic execution contracts and automatic retry-on-failure repair strategies.

**Objective Summary:**  
Retrieve user, post, comment, album, and todo data from JSONPlaceholder; establish relational mappings; compute per-user quality metrics; and deliver two artifacts: a JSON dataset and a styled HTML report with rankings, post-comment associations, and summary statistics.

**Governance Posture:**  
- **Policy Profile:** `generic.inference-allowed.v1` (applied to Step 2 only; other steps use default permissive validation)
- **Validation Strictness:** Relaxed input/output binding enforcement on Steps 1–2; strict enforcement on Steps 3–4
- **Repair Strategy:** Uniform retry-on-failure with up to 6 retries per step
- **Tool Isolation:** All steps execute within `sandbox.session` (isolated, time-limited execution environment)

---

## 2. Domain & Workflow Packs

### Workflow Pack: `file-acquisition` (Step 1)

**Purpose:**  
Acquire and stage raw source material before downstream processing. This pack governs the initial data-fetching phase where external APIs are called and responses are persisted.

**What It Does:**  
Step 1 ("Fetch core data from JSONPlaceholder API") uses this pack to:
- Make HTTP requests to JSONPlaceholder endpoints (`/users`, `/users/{id}/posts`, `/users/{id}/todos`, `/users/{id}/albums`, `/posts?_limit=20`, `/comments?_limit=20`, `/posts/1/comments`, `/albums/1/photos`)
- Collect responses into a unified JSON structure (`raw_api_data.json`)
- Validate that all expected entities are present (10 users, 20 posts, 20 comments, etc.)

**Why It Matters:**  
Without reliable data acquisition, downstream normalization and analysis cannot proceed. This pack ensures that raw API responses are fetched once, cached in a transport slot, and available for reuse across subsequent steps.

**Typical Slots:**  
- **Inputs:** `source_manifest` (implicit—the API endpoints themselves)
- **Outputs:** `raw_files`, `batch_manifest` (in this case, a single unified `raw_api_data.json`)

---

### Workflow Pack: `normalize-transform` (Step 2)

**Purpose:**  
Canonicalize, reshape, and join structured data. This pack handles the conversion of flat API responses into relational structures with parent–child associations.

**What It Does:**  
Step 2 ("Establish entity relationships") uses this pack to:
- Read the raw API data from Step 1
- Map comments to posts via `postId` field
- Map photos to albums via `albumId` field
- Nest posts, todos, and albums under their parent users
- Produce `relational_data.json` with enriched hierarchies

**Why It Matters:**  
The JSONPlaceholder API returns flat lists; downstream analysis and rendering require hierarchical structures. This step bridges the gap, enabling Step 3 to compute per-user metrics and Step 4 to render posts with their associated comments.

**Typical Slots:**  
- **Inputs:** `normalized_rows` (raw API data)
- **Outputs:** `joined_rows`, `aggregated_rows` (in this case, relational structures with nested arrays)

---

### Workflow Pack: `render-report` (Step 4)

**Purpose:**  
Transform findings, metrics, and data rows into human-readable report artifacts (HTML, Markdown, PDF, etc.).

**What It Does:**  
Step 4 ("Render HTML user rankings page") uses this pack to:
- Read enriched user metrics from Step 3 (`enriched-users.json`)
- Read relational data from Step 2 (posts with comments)
- Compose three sections:
  1. **User Rankings Table** — 10 users sorted by quality score, with rank, name, email, post count, completion rate (%), and quality score
  2. **Posts with Comments Table** — 20 posts with truncated bodies and nested comment lists
  3. **Summary Statistics** — aggregate counts and average quality score
- Embed CSS styling (alternating row colors, responsive layout, clean typography)
- Write `user-rankings.html` as a self-contained, single-file deliverable

**Why It Matters:**  
Raw JSON is not actionable for stakeholders. This pack converts computed metrics and relationships into a polished, browsable report suitable for sharing, printing, or PDF export.

**Typical Slots:**  
- **Inputs:** `findings`, `normalized_rows` (enriched users and posts with comments)
- **Outputs:** `report_artifact` (single HTML file with embedded CSS)

---

## 3. Governance & Policy

### Policy Profile: `generic.inference-allowed.v1`

**Applied to:** Step 2 only (Establish entity relationships)

**Plain-Language Explanation:**  
This profile permits the compiler to bind **generic, loosely-typed profiles** when domain-specific schemas are unavailable. It is designed for exploratory or draft workflows where approximate structural compatibility is acceptable, and where the user has explicitly requested "best-effort" handling of heterogeneous inputs.

**Compiler Rules:**
| Rule | Meaning |
|------|---------|
| `allow_generic_inference` | Compiler may bind generic profiles (e.g., `generic.table.json_rows`) when semantic specificity is absent |
| `allow_normalizers` | Compiler may apply generic normalizer functions to reshape data |
| `require_explicit_adapter` | **False** — no explicit type adapter required; generic inference is sufficient |
| `fail_on_ambiguous_binding` | **False** — ambiguous bindings are tolerated and annotated |
| `annotate_inferred_bindings` | **True** — all inferred bindings are marked in metadata for transparency |
| `fail_on_unbound_required_input` | **True** — missing required inputs still cause failure |

**Runtime Policy:**
- No human review required before deployment
- Source artifact IDs are optional (not enforced)
- Missing provenance does not block publication

**Why This Profile?**  
Step 2 performs data joining and reshaping on JSON structures that do not have strict domain-specific schemas. The profile allows flexible binding while maintaining safety guardrails (required inputs must still be present).

### Default Governance (Steps 1, 3, 4)

**Validation Strictness:**
- **Steps 1–2:** Relaxed (`fail_on_missing_outputs: false`, `require_declared_outputs: false`)
- **Steps 3–4:** Strict (`fail_on_missing_outputs: true`, `require_declared_outputs: true`, `enforce_compiled_output_bindings: true`)

**Rationale:**  
Steps 1–2 are exploratory data acquisition and transformation; exact output schemas are less critical. Steps 3–4 produce user-facing deliverables; strict validation ensures data integrity and completeness.

---

## 4. Execution Contracts

An **execution contract** defines how a step will be run, what happens if it fails, and what constraints apply. All four steps use deterministic or hybrid contracts with automatic retry repair.

### Step 1: Fetch Core Data

| Aspect | Value |
|--------|-------|
| **Pattern** | `single_shot_artifact_production` |
| **Nature** | `DETERMINISTIC` (same inputs → same outputs) |
| **Repair Strategy** | `replace_prior_script_on_primary_output_failure` |
| **Timeout** | 30 minutes (1,800,000 ms) |
| **Max Tool Calls** | 3 |
| **Max Retries** | 6 |

**Execution Flow:**
1. Execute the step once (single shot)
2. If `raw_api_data.json` is not produced or is invalid JSON, retry the entire step up to 6 times
3. On each retry, replace the prior execution script with a corrected version
4. If all 6 retries fail, the step fails and downstream steps are blocked

**Tool Limits:**  
The step may call `sandbox.session` up to 3 times (e.g., one call per batch of API requests, or one call per retry attempt). This prevents runaway tool invocations.

---

### Step 2: Establish Entity Relationships

| Aspect | Value |
|--------|-------|
| **Pattern** | `single_shot_artifact_production` |
| **Nature** | `DETERMINISTIC` |
| **Repair Strategy** | `replace_prior_script_on_primary_output_failure` |
| **Timeout** | 30 minutes |
| **Max Tool Calls** | 3 |
| **Max Retries** | 6 |

**Execution Flow:**
1. Read `raw_api_data.json` from Step 1 (implicit input dependency)
2. Execute transformation logic once
3. If `relational_data.json` is invalid or incomplete, retry up to 6 times with script replacement
4. Success criteria: `enriched_users` has 10 entries with nested posts/todos/albums; `first_20_posts_with_comments` has 20 entries with comment arrays; `summary_counts.total_users == 10`

**Policy Binding:**  
This step is bound to `generic.inference-allowed.v1`, permitting flexible schema binding during the join operation.

---

### Step 3: Compute Per-User Metrics and Save Enriched JSON

| Aspect | Value |
|--------|-------|
| **Pattern** | `single_shot_artifact_production` |
| **Nature** | `DETERMINISTIC` |
| **Repair Strategy** | `replace_prior_script_on_primary_output_failure` |
| **Timeout** | 30 minutes |
| **Max Tool Calls** | 3 |
| **Max Retries** | 6 |

**Execution Flow:**
1. Read `relational_data.json` from Step 2 (implicit input dependency)
2. For each of 10 users, compute:
   - `post_count` — count of posts
   - `avg_body_length` — mean character length of post bodies
   - `todo_completion_rate` — fraction of todos with `completed: true` (range [0.0, 1.0])
   - `quality_score` — `(post_count * 0.4) + (todo_completion_rate * 0.6)`
3. Write `enriched-users.json` as a bare JSON array of 10 objects
4. Each object contains exactly: `id`, `name`, `email`, `company_name`, `post_count`, `avg_body_length`, `todo_completion_rate`, `quality_score`

**Strict Validation:**  
- `fail_on_missing_outputs: true` — if `enriched-users.json` is not written, the step fails
- `require_declared_outputs: true` — all declared outputs must be present
- `enforce_compiled_output_bindings: true` — output paths must match compiled bindings exactly
- `block_on_missing_inputs: true` — if Step 2 fails, this step is blocked

---

### Step 4: Render HTML User Rankings Page

| Aspect | Value |
|--------|-------|
| **Pattern** | `single_shot_render` |
| **Nature** | `HYBRID` (deterministic data processing + creative rendering) |
| **Repair Strategy** | `retry_with_small_fix` |
| **Timeout** | 30 minutes |
| **Max Tool Calls** | 3 |
| **Max Retries** | 6 |

**Execution Flow:**
1. Read `enriched-users.json` from Step 3 and relational data from Step 2
2. Sort users by `quality_score` descending; assign ranks
3. Format completion rates as percentages
4. Truncate post bodies to 100 characters
5. Build three HTML sections:
   - **User Rankings Table** (10 rows, 6 columns)
   - **Posts with Comments Table** (20 rows, with nested comment lists)
   - **Summary Statistics** (4 key metrics)
6. Embed CSS with alternating row colors, responsive layout, clean typography
7. Write `user-rankings.html` as a single self-contained file (no external stylesheets or JS)

**Repair Strategy Nuance:**  
Unlike Steps 1–3, this step uses `retry_with_small_fix` instead of full script replacement. If HTML generation fails (e.g., malformed table structure), the system attempts targeted fixes (e.g., correcting tag nesting) before full retry.

**Strict Validation:**  
- `fail_on_missing_outputs: true`
- `require_declared_outputs: true`
- `require_input_artifact_refs: true` — inputs from Steps 2 and 3 must be explicitly referenced
- `enforce_compiled_output_bindings: true`
- `block_on_missing_inputs: true`

---

## 5. Artifact Flow

Artifacts are versioned, named data objects that flow between steps. The plan defines a **linear dependency chain**:

```
Step 1 (Fetch)
    ↓ raw_api_data.json
Step 2 (Normalize & Join)
    ↓ relational_data.json
    ├─→ Step 3 (Compute Metrics)
    │       ↓ enriched-users.json
    │       ↓
    └─→ Step 4 (Render HTML) ←─ enriched-users.json
            ↓ user-rankings.html
```

### Artifact Definitions

| Step | Artifact | Role | Format | Purpose |
|------|----------|------|--------|---------|
| 1 | `raw_api_data.json` | Primary (transport slot) | JSON | Raw API responses: users, posts, todos, albums, comments, photos |
| 2 | `relational_data.json` | Primary (transport slot) | JSON | Hierarchical structure: users with nested posts/todos/albums; posts with nested comments; album with nested photos |
| 3 | `enriched-users.json` | User-deliverable dataset | JSON array | 10 user objects with computed metrics (post_count, avg_body_length, todo_completion_rate, quality_score) |
| 4 | `user-rankings.html` | User-deliverable report | HTML + embedded CSS | Styled report with 3 tables and summary statistics |

### Metadata Artifacts (All Steps)

Each step also produces metadata artifacts:
- `output/step_result.json` — execution summary (status, timing, error logs)
- `meta/mcp-tools/journal.ndjson` — newline-delimited JSON log of tool calls
- `meta/mcp-tools/calls.tar.gz` — compressed archive of detailed tool call traces

These are used for debugging and audit trails but are not consumed by downstream steps.

---

## 6. Validation & Safety

### Validator Rules

**Steps 1–2 (Relaxed):**
```
fail_on_missing_outputs: false
require_declared_outputs: false
require_input_artifact_refs: false
enforce_compiled_output_bindings: false
```
These steps are exploratory; missing outputs do not immediately fail the plan. However, if a downstream step requires their output, that step will be blocked.

**Steps 3–4 (Strict):**
```
fail_on_missing_outputs: true
require_declared_outputs: true
require_input_artifact_refs: true (Step 4 only)
enforce_compiled_output_bindings: true
```
These steps produce user-facing deliverables. All declared outputs must be present and must match compiled bindings exactly.

### Repair Policies

| Step | Strategy | Max Retries | Block on Missing Inputs | Immutable Bindings |
|------|----------|-------------|------------------------|-------------------|
| 1 | `retry_same_contract` | 6 | false | true |
| 2 | `retry_same_contract` | 6 | false | true |
| 3 | `retry_same_contract` | 6 | **true** | true |
| 4 | `retry_same_contract` | 6 | **true** | true |

**Key Differences:**
- **Steps 1–2:** Missing inputs do not block execution (best-effort acquisition)
- **Steps 3–4:** Missing inputs block execution (strict dependency enforcement)
- **All Steps:** Output bindings are immutable—once compiled, output paths cannot change during retries

### Success Criteria (Validation Checkpoints)

**Step 1:**
- `raw_api_data.json` is valid JSON
- Contains `users` array of
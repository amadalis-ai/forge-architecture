# Billing Audit Execution Plan — Technical Narrative

## 1. Compilation Overview

This execution plan compiles a **9-step billing audit workflow** designed to reconcile 753 professional services time entries against contract terms, rate cards, and invoices. The plan was built under the **`strict.allow-normalizers.v1`** policy profile, which permits explicit schema adapters and normalizers while maintaining strict producer/consumer contract enforcement.

**Governance Posture:**
- **Fail-closed on unbound inputs**: Missing required artifacts block execution.
- **Immutable output bindings**: Once a step declares an output artifact, its path and role cannot change.
- **Deterministic execution**: All steps are deterministic (no randomness or external API calls except the mock finance endpoint in Step 7).
- **Cross-validation required**: Totals in JSON artifacts must match across phases before report generation.

**Scope:** All 753 time entries are processed end-to-end. No sampling, no silent drops. Unmatched entries are explicitly flagged as `UNMATCHED_ENTRY` exceptions, not discarded.

---

## 2. Domain & Workflow Packs

### Domain Pack: `billing-audit`

**Purpose:** Reconcile time, rates, contracts, and invoice lines to determine billing accuracy and discrepancies.

**Why it matters for this task:**
- The objective is explicitly a **billing audit** — matching time entries to contracts and rate cards.
- The domain pack provides semantic vocabulary for billable time, rate cards, discrepancies, and T&M (time & materials) reconciliation.
- It anchors the mission: *"What should have been billed vs. what was actually billed?"*

**Entity schemas provided:**
- `billing.time_entry` — time_entry_id, hours_logged, billed_rate, billed_amount
- `billing.rate_card` — contract_id, role_code, hourly_rate, effective_date
- `billing.invoice_line_item` — invoice_id, invoice_status, customer_id, invoice_total
- `billing.discrepancy_row` — time_entry_id, discrepancy_types[], rate_delta, amount_delta
- `billing.billing_summary` — totals_by_type, grand_total_dollar_impact

---

### Workflow Packs Used

| Workflow | Steps | Purpose |
|----------|-------|---------|
| **normalize-transform** | 2, 5, 6 | Canonicalize CSV fields, reshape into normalized rows, aggregate exceptions by type. |
| **reconcile-compare** | 3, 4 | Join time entries to contracts and rates (composite key matching); compute discrepancies by comparing billed vs. expected amounts. |
| **analyze-score-rank** | 6, 7 | Score correction candidates against business rules ($100 max, $25 approval threshold); rank and classify for submission. |
| **render-report** | 8, 9 | Generate HTML audit report from JSON findings; convert to PDF. |

**Why these workflows:**
- **normalize-transform** handles the heterogeneous CSV inputs (different schemas, date formats, numeric precision).
- **reconcile-compare** is essential for the core audit logic: matching time entries to contracts via composite keys, then comparing billed rates to rate-card rates.
- **analyze-score-rank** applies business rules (policy thresholds) to determine which corrections are eligible, require approval, or must be rejected.
- **render-report** transforms structured JSON findings into human-readable deliverables.

---

## 3. Governance & Policy

### Policy Profile: `strict.allow-normalizers.v1`

**Plain-language explanation:**

This profile enforces **strict contracts** between steps but allows **explicit adapters** to bridge schema mismatches. It is neither permissive nor rigid:

- ✅ **Allowed:** If Step A produces `normalized_rows` and Step B consumes `normalized_rows`, the compiler inserts a declared adapter automatically.
- ❌ **Blocked:** If Step A produces `raw_csv_text` and Step B expects `normalized_rows` with no registered adapter, execution fails.
- ❌ **Blocked:** Silent type coercion or semantic inference beyond declared adapters.

**Compiler behavior:**
- `allow_normalizers: true` — Adapters may be inserted automatically.
- `allow_generic_inference: false` — No guessing about field mappings.
- `fail_on_ambiguous_binding: true` — If two adapters could apply, fail rather than guess.
- `fail_on_unbound_required_input: true` — Missing inputs block the step.

**Runtime behavior:**
- `require_source_artifact_ids: true` — Every artifact must declare its source step.
- `block_publish_on_missing_provenance: true` — No artifact is published without a clear lineage.

**Why this profile for billing audit:**
- Billing is high-stakes: incorrect reconciliation can lead to revenue leakage or customer disputes.
- The input CSVs are heterogeneous (different date formats, nullable fields, inconsistent enums).
- Explicit normalization is acceptable (and expected) because the business rules are clear.
- Silent coercion would be dangerous: a missed rate mismatch could hide a $10k overcharge.

---

## 4. Execution Contracts — Per Step

Each step declares a **contract** that governs how it executes, what happens if it fails, and how many retries are permitted.

### Step 1: Profile All Source Inputs

| Attribute | Value |
|-----------|-------|
| **Pattern** | `single_shot_artifact_production` |
| **Nature** | DETERMINISTIC |
| **Repair Strategy** | `replace_prior_script_on_primary_output_failure` |
| **Timeout** | 30 minutes |
| **Max Tool Calls** | 3 |
| **Max Retries** | 6 |

**What it does:**
- Reads all five CSV files from `attachments/`.
- Profiles each: row count, column names, inferred types, null counts, distinct values for key columns.
- Outputs `schema_profile_simone.json` with metadata for all 753 time entries, 7 contracts, 7 rates, 6 invoices, and 1 policy file.

**Repair strategy:**
- If the output JSON is malformed or missing, the step is re-executed with the same script (no modification).
- After 6 retries, the step fails and blocks downstream execution.

**Why this contract:**
- Profiling is deterministic: same input always produces same output.
- A single shot is sufficient; no iterative refinement needed.
- Failure is unrecoverable without human intervention (e.g., corrupted CSV).

---

### Step 2: Normalize and Validate Source Data

| Attribute | Value |
|-----------|-------|
| **Pattern** | `single_shot_artifact_production` |
| **Nature** | DETERMINISTIC |
| **Repair Strategy** | `replace_prior_script_on_primary_output_failure` |
| **Timeout** | 30 minutes |
| **Max Tool Calls** | 3 |
| **Max Retries** | 6 |

**What it does:**
- Parses all CSVs using the schema profile from Step 1.
- Converts date columns to ISO 8601 (YYYY-MM-DD).
- Coerces numeric fields (hours_logged, billed_rate, billed_amount, hourly_rate, monthly_hours_cap, invoice_total) to JSON numbers.
- Flags rows with nulls or type errors (but does not drop them).
- Outputs `normalized_sources.json` with all 753 time entries, 7 contracts, 7 rates, 6 invoices in canonical form.

**Repair strategy:**
- If normalization fails (e.g., unparseable date), the step retries with the same script.
- Validation flags are recorded but do not block output.

**Why this contract:**
- Normalization is deterministic and idempotent.
- Errors are expected (nulls, type mismatches) and are recorded, not fatal.

---

### Step 3: Resolve Contract Applicability for All Entries

| Attribute | Value |
|-----------|-------|
| **Pattern** | `single_shot_artifact_production` |
| **Nature** | DETERMINISTIC |
| **Repair Strategy** | `replace_prior_script_on_primary_output_failure` |
| **Timeout** | 30 minutes |
| **Max Tool Calls** | 3 |
| **Max Retries** | 6 |

**What it does:**
- **Join 1 (Composite Key):** For each time entry, matches `contract_ref` and `employee_id` against the contracts table. If both match, the entry is linked to a contract.
- **Join 2 (Rate Card Lookup):** For each time entry, finds all rate rows where `rates.contract_id = time_entries.contract_ref`. Then matches the rate row whose `hourly_rate` equals `billed_rate`. This identifies which role was billed.
  - If no rate matches `billed_rate`, the entry is flagged as `unmatched_rate` (rate not in card).
- **Expiration Check:** Compares `work_date` to `contract.expiration_date`. If work_date > expiration_date, marks `is_expired = true`.
- Outputs `contract_applicability_simone.json` with exactly 753 records (one per time entry), each containing:
  - `time_entry_id`, `resolved_contract_id`, `contract_status`, `expiration_date`, `matched_hourly_rate`, `is_expired`, `linkage_status`

**Repair strategy:**
- If the output has fewer than 753 records, the step retries.
- If any `linkage_status` is invalid (not one of: matched, unmatched_contract, unmatched_rate, expired), the step retries.

**Why this contract:**
- The join logic is deterministic but complex (composite keys, rate card matching).
- All 753 entries must be present in the output; missing entries are a critical failure.
- This step is the foundation for discrepancy detection; errors here cascade downstream.

---

### Step 4: Compute Billing Discrepancies for All Entries

| Attribute | Value |
|-----------|-------|
| **Pattern** | `single_shot_artifact_production` |
| **Nature** | DETERMINISTIC |
| **Repair Strategy** | `replace_prior_script_on_primary_output_failure` |
| **Timeout** | 30 minutes |
| **Max Tool Calls** | 3 |
| **Max Retries** | 6 |

**What it does:**
- For each of the 753 time entries, checks three categories of discrepancies:

  1. **Rate Check:** Compares `billed_rate` to `matched_hourly_rate` (from Step 3).
     - If different, computes `rate_delta = billed_rate - matched_hourly_rate` and `overcharge_amount = rate_delta × hours_logged`.
     - Flags as `RATE_OVERCHARGE` (if billed_rate > matched_hourly_rate) or `RATE_UNDERCHARGE` (if billed_rate < matched_hourly_rate).

  2. **Amount Check:** Computes `expected_amount = hours_logged × billed_rate`. Compares to `billed_amount`.
     - If different, flags as `AMOUNT_MISMATCH` with `amount_delta = billed_amount - expected_amount`.

  3. **Cap Check:** For each (contract_id, employee_id, month), sums all `hours_logged`. Compares to `monthly_hours_cap`.
     - If total exceeds cap, flags all entries in that group as `CAP_OVERRUN` with `hours_over = total_hours - monthly_hours_cap`.

- Also flags:
  - `EXPIRED_CONTRACT`: entries where `is_expired = true`.
  - `UNMATCHED_ENTRY`: entries where contract or rate linkage failed.
  - `LOCKED_INVOICE`: entries referencing an invoice with `invoice_status = "paid_locked"`.

- Outputs `discrepancies_simone.json` as a **bare JSON array** (not wrapped in an object). Only rows with at least one discrepancy are included. Each row contains:
  - `time_entry_id`, `employee_id`, `contract_ref`, `invoice_id`, `work_date`, `billed_rate`, `matched_hourly_rate`, `billed_amount`, `expected_amount`, `hours_logged`, `discrepancy_types[]` (array of applicable codes), `rate_delta`, `amount_delta`, `hours_over_cap`.

**Repair strategy:**
- If the output is not a bare array, the step retries.
- If any row has an empty `discrepancy_types` array, the step retries.

**Why this contract:**
- Discrepancy detection is deterministic but computationally intensive (753 entries × 3 checks + monthly aggregation).
- The output is a filtered subset of the input (only flagged rows), so row count is variable.
- The bare array format (not wrapped in an object) is intentional for downstream aggregation.

---

### Step 5: Summarize Exceptions by Type

| Attribute | Value |
|-----------|-------|
| **Pattern** | `single_shot_artifact_production` |
| **Nature** | DETERMINISTIC |
| **Repair Strategy** | `replace_prior_script_on_primary_output_failure` |
| **Timeout** | 30 minutes |
| **Max Tool Calls** | 3 |
| **Max Retries** | 6 |

**What it does:**
- Aggregates discrepancies from Step 4 by type.
- For each of the 8 discrepancy types (RATE_OVERCHARGE, RATE_UNDERCHARGE, AMOUNT_MISMATCH, EXPIRED_CONTRACT, CAP_OVERRUN, LOCKED_INVOICE, UNMATCHED_ENTRY, RATE_NOT_IN_CARD), computes:
  - `count`: number of entries with this type.
  - `total_dollar_impact`: sum of overcharge/undercharge/mismatch amounts.
  - `affected_invoices[]`: distinct invoice_ids.
  - `affected_employees[]`: distinct employee_ids.
- Also computes grand totals: `grand_total_discrepancies` (sum of all counts) and `grand_total_dollar_impact`.
- Outputs `exception_summary_simone.json` with structure:
  ```json
  {
    "totals_by_type": { "RATE_OVERCHARGE": 42, "RATE_UNDERCHARGE": 5, ... },
    "total_exceptions": 123,
    "totals_by_invoice_status": { "draft": 50, "paid_locked": 30, ... },
    "by_type": {
      "RATE_OVERCHARGE": { "count": 42, "total_dollar_impact": 5000.00, "affected_invoices": [...], "affected_employees": [...] },
      ...
    },
    "grand_total_discrepancies": 123,
    "grand_total_dollar_impact": 12345.67
  }
  ```

**Repair strategy:**
- If the output is missing any of the 8 type keys, the step retries.
- If `grand_total_discrepancies` does not equal the sum of `totals_by_type` values, the step retries.

**Why this contract:**
- Aggregation is deterministic and idempotent.
- This step is critical for the executive summary in the final report.
- Cross-validation (totals matching) is enforced at the contract level.

---

### Step 6: Build Correction Candidates with Business Rules

| Attribute | Value |
|-----------|-------|
| **Pattern** | `single_shot_artifact_production` |
| **Nature** | DETERMINISTIC |
| **Repair Strategy** | `replace_prior_script_on_primary_output_failure` |
| **Timeout** | 30 minutes |
| **Max Tool Calls** | 3 |
| **Max Retries** | 6 |

**What it does:**
- For each discrepancy where a correction is possible (rate overcharges, amount mismatches), builds a correction payload.
- Aggregates corrections per invoice (one correction per invoice per reason_code).
- Applies business rules from `finance_policy.md`:
  - `max_correction = 100`: If a single correction exceeds $100, mark as `status: "rejected"` with `rejection_reason: "exceeds_max_correction"`.
  - `approval_threshold = 25`: If correction is between $25 and $100, mark `approval_required: true`.
  - `locked_statuses = ["paid_locked"]`: If the invoice has status "
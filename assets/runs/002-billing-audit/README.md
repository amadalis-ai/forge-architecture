# Run 002 — Billing Audit: Professional Services Time Entry Reconciliation

## User Message (Input)

> Audit billing accuracy for professional services time entries. Reconcile every time entry against its contract terms, rate card, and invoice using the workspace files described below.

### Source Files

| File | Rows | Columns |
|------|------|---------|
| `attachments/time_entries.csv` | 753 | time_entry_id, employee_id, contract_ref, work_date, hours_logged, billed_rate, billed_amount, invoice_id, project_code |
| `attachments/contracts.csv` | 7 | contract_id, customer_id, employee_id, contract_status, billing_type, effective_date, expiration_date, monthly_hours_cap, currency |
| `attachments/rates.csv` | 7 | contract_id, role_code, hourly_rate, effective_date, expiration_date |
| `attachments/invoices.csv` | 6 | invoice_id, invoice_status, customer_id, invoice_total, period_start, period_end |
| `attachments/finance_policy.md` | — | Business rules for correction thresholds and approval logic |

### Data Model — Exact Join Logic

**Join 1: time_entries -> contracts**
- Composite key: `time_entries.contract_ref = contracts.contract_id AND time_entries.employee_id = contracts.employee_id`
- No match -> classify as `UNMATCHED_ENTRY`

**Join 2: time_entries -> rates (via contract)**
- `time_entries.csv` has no `role_code` column — cannot join directly
- Match via: `rates.contract_id = time_entries.contract_ref` where `rates.hourly_rate = time_entries.billed_rate`
- No match -> `RATE_NOT_IN_CARD`

**Join 3: time_entries -> invoices**
- `time_entries.invoice_id = invoices.invoice_id`

### Work Phases

The user specified 9 sequential phases:

| Phase | Task | Output |
|-------|------|--------|
| 1 | Profile inputs — row counts, column types, null counts, distinct values | `output/schema_profile_simone.json` |
| 2 | Normalize & validate — ISO dates, numeric types, flag errors, keep all 753 rows | (validated in-memory) |
| 3 | Resolve contract applicability — apply joins, classify linkage status for all 753 entries | `output/contract_applicability_simone.json` |
| 4 | Compute billing discrepancies — rate check, amount check, cap check, expired/unmatched/locked flags | `output/discrepancies_simone.json` |
| 5 | Summarize exceptions — aggregate by type with counts, dollar impact, affected invoices/employees | `output/exception_summary_simone.json` |
| 6 | Build correction candidates — per-invoice correction payloads with business rule enforcement ($100 max, $25 approval threshold, locked invoice rejection) | `output/correction_candidates_simone.json` |
| 7 | Simulate correction submissions — mock finance API with acceptance/rejection/approval logic | `output/correction_submission_result_simone.json` |
| 8 | Generate audit report (HTML) — executive summary, discrepancy breakdown, detail table, correction outcomes | `reports/billing_audit_report_simone.html` |
| 9 | Convert to PDF | `reports/billing_audit_report_simonetesting.pdf` |

### Critical Rules (from user message)

- Process ALL 753 time entries — no sampling, no skipping
- Phase 3 output must contain exactly 753 records
- Discrepancies output contains only flagged rows
- Never silently drop unmatched entries — record as UNMATCHED_ENTRY
- Report totals must match JSON artifacts exactly — cross-validate
- If a correction violates business rules, record the rejection and continue

---

## Why this run matters for the proof bundle

This is a fundamentally different class of work from Run 001:

| Dimension | Run 001 (JSONPlaceholder) | Run 002 (Billing Audit) |
|-----------|--------------------------|------------------------|
| Domain | Generic data analysis | `billing-audit` domain pack |
| Data sources | External API (JSONPlaceholder) | Workspace file attachments (CSV) |
| Complexity | 4 plan steps | 9 phases -> compiled into N plan steps |
| Join logic | Simple nested API responses | Composite keys, indirect rate matching, cross-table reconciliation |
| Business rules | None | $100 max correction, $25 approval threshold, locked invoice rejection |
| Validation | Schema inference | Cross-phase numeric consistency (report totals must match JSON artifacts) |
| Output types | JSON + HTML | 6 JSON artifacts + HTML report + PDF conversion |
| Skill binding | html-report-generator | html-report-generator + data analysis |

This run proves the system handles:
- Real enterprise data with composite join keys
- Business rule enforcement at execution time
- Multi-phase data pipelines where each phase builds on the previous
- Mock API simulation within the sandbox
- Cross-artifact consistency validation
- Domain-specific work (billing audit) driven by domain pack semantics

---

## Proof chain

| # | Artifact | Location | What it proves |
|---|----------|----------|---------------|
| 1 | User message | This README (above) | A complex, multi-phase billing audit specification in natural language |
| 2 | Compiled plan | `plan/` | How the compiler decomposed 9 phases into compiled steps with contracts |
| 3 | Compiled sub-steps | `compiled-steps/` | The model-generated code for each phase: joins, calculations, business rules |
| 4 | Deliverables | `deliverables/` | All output JSON artifacts + HTML report + PDF |
| 5 | Screenshots | `screenshots/` | Visual evidence from the workspace UI |

---

## Directories

```
002-billing-audit/
├── README.md              <- you are here
├── plan/                  <- compiled plan steps and contracts
├── compiled-steps/        <- sub-steps with model-generated code
├── deliverables/          <- JSON artifacts, HTML report, PDF
└── screenshots/           <- workspace UI during/after the run
```

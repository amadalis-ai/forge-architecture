# Run 003 — CSV Profile & Join Transform

## User Message (Input)

> Transform the CSV files in this workspace into a single consolidated JSON dataset.
>
> **Workspace Files**
>
> - `attachments/time_entries.csv` — 753 rows. Columns: time_entry_id, employee_id, contract_ref, work_date, hours_logged, billed_rate, billed_amount, invoice_id, project_code
> - `attachments/rates.csv` — Columns: contract_id, role_code, hourly_rate, effective_date, expiration_date
>
> **Step 1:** Profile both CSVs — read each file, validate schemas, count rows, flag nulls or type mismatches. Save the profile to `output/schema_profile2.json`.
>
> **Step 2:** Using the profile from step 1, join time_entries to rates on contract_ref=contract_id. For each joined row, add a column `rate_match` (true/false comparing billed_rate to hourly_rate). Save the joined dataset to `output/joined_entries2.json`.
>
> No reports. No corrections. Just the two output files.
>
> **Required Outputs:**
> - `output/schema_profile2.json`
> - `output/joined_entries2.json`

---

## Why this run matters for the proof bundle

This is a deliberately simple run — two steps, two outputs, no reports. It shows the compiler handles lightweight data transformation tasks with the same structural rigor as complex multi-phase audits.

| Dimension | Run 001 (API Analysis) | Run 002 (Billing Audit) | Run 003 (CSV Join) |
|-----------|----------------------|------------------------|-------------------|
| Complexity | 4 steps | 9 phases | 2 steps |
| Data sources | External API | 5 workspace CSVs | 2 workspace CSVs |
| Domain | Generic | billing-audit | data-merge-transform |
| Join logic | Nested API responses | Composite keys, indirect rate matching | Single key join |
| Outputs | JSON + HTML | 6 JSON + HTML + PDF | 2 JSON files |

The contrast matters: the same compilation pipeline, the same contract verification, the same preflight/postflight receipts, the same traceability — whether the task is 2 steps or 400.

---

## Proof chain

| # | Artifact | Location | What it proves |
|---|----------|----------|---------------|
| 1 | User message | This README (above) | A simple, constrained data transformation request |
| 2 | Compiled plan | `plan/` | How the compiler decomposed 2 steps with contracts |
| 3 | Compiled sub-steps | `compiled-steps/` | The model-generated code for profiling and joining |
| 4 | Deliverables | `deliverables/` | schema_profile2.json + joined_entries2.json |
| 5 | Screenshots | `screenshots/` | Visual evidence from the workspace UI |

---

## Directories

```
003-csv-join-transform/
├── README.md              ← you are here
├── plan/                  ← compiled plan steps and contracts
├── compiled-steps/        ← sub-steps with model-generated code
├── deliverables/          ← schema_profile2.json, joined_entries2.json
└── screenshots/           ← workspace UI during/after the run
```

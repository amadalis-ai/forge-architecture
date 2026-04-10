# Forge — A Compiler for Autonomous Work

> Autonomous AI should be compiled, not merely interpreted.

This repository contains the public research, proof artifacts, and execution evidence behind Forge — a compilation architecture for autonomous AI work built by [Simone Coelho](https://amadalis.ai/about).

---

## Where to start

**If you want the story** — what I built, why, and how I got here:

- [**Founder Research Note**](docs/founder-research-note-v2.md) — the discovery arc, the architectural claim, and the evidence. ~8,000 words.

**If you want the full technical deep-dive** — the compilation pipeline, type system, validation ladder, executor, capsules, governance:

- [**Architecture Thesis**](docs/forge-architecture-thesis.md) — the canonical system reference. ~20,000 words.

**If you want to go straight to the proof** — real compiled execution runs with everything from user message to verified deliverables:

- [Run 001 — JSONPlaceholder Data Analysis](#run-001--jsonplaceholder-data-analysis) — 4-step API fetch, transform, compute, render
- [Run 002 — Billing Audit](#run-002--billing-audit) — 9-phase enterprise reconciliation of 753 time entries
- [Run 003 — CSV Join Transform](#run-003--csv-join-transform) — 2-step lightweight data profiling and join

**If you want to see the platform** — screenshots of the workspace, execution views, prompt engineering, governance:

- [Platform Screenshots](#platform-screenshots)

---

## How to read the execution runs

Each run in `assets/runs/` is a self-contained proof chain. You can follow the full lifecycle from a natural language user message to verified deliverables. Here is what each run contains and how to read it:

### The proof chain

```
User message (natural language intent)
    ↓
Compiled plan (the blueprint — steps, dependencies, contracts)
    ↓
Compilation brief (AI-generated analysis of the compiler's decisions)
    ↓
Compiled sub-steps (the actual code the model generated + the harness around it)
    ↓
Attempt records (every execution attempt with forensics — timing, retries, repairs)
    ↓
Deliverables (the verified output files — JSON, HTML, PDF)
    ↓
Screenshots (the workspace UI showing the run in progress or completed)
```

### What each file is

| File | What it is | Why it matters |
|------|-----------|----------------|
| **README.md** | The user's original message and a walkthrough of what the compiler did with it | Start here — see what the user asked for and how the system responded |
| **plan/*.json** | The compiled execution plan — every step with dependencies, contracts, artifact bindings, and SHA-256 hashes | This is the blueprint. Every step was validated before execution started. |
| **compiled-steps/compilation-brief.md** | An AI-generated technical analysis of the compiler's decisions — why it chose specific domain packs, how it wired contracts, what routing decisions it made, and what governance was applied | **Read this to understand the compiler's reasoning.** This is the document that explains how a natural language message became a governed execution plan. |
| **compiled-steps/all-compiled-steps-*.json** | Every sub-step the model executed — including the actual Python code it wrote, exit codes, durations, and container identity | This is the code. The model invented these programs to fulfill its contracts. You can read every line. |
| **compiled-steps/all-attempts-*.json** | Every execution attempt with full forensics — timing, sandbox identity, persisted paths, retry evidence, repair context | This is the audit trail. If a step failed and recovered, the evidence is here. |
| **deliverables/** | The final output files — the artifacts the system produced and verified | These are the receipts. The system verified they exist, parse correctly, and match the declared contracts. |
| **screenshots/** | Workspace UI screenshots showing the plan, execution progress, and compilation brief | Visual evidence that this is a running system, not a paper architecture. |

### How to follow a proof chain

1. **Start with the README** — read the user's message. Understand what they asked for.
2. **Open the compilation brief** (`compiled-steps/compilation-brief.md`) — read how the compiler decomposed and governed the request. This is the most important technical artifact in each run.
3. **Open the compiled plan** (`plan/*.json`) — see the step graph with dependencies and contracts.
4. **Browse the compiled sub-steps** (`compiled-steps/all-compiled-steps-*.json`) — see the actual code the model generated for each step.
5. **Check the deliverables** (`deliverables/`) — verify the outputs. Open the HTML reports. Read the JSON.
6. **Look at the screenshots** — see the workspace UI during execution.

---

## Execution Runs

### Run 001 — JSONPlaceholder Data Analysis

**User message:** Fetch data from a public API, build a relationship graph, compute per-user quality metrics, render a styled HTML ranking page.

**Complexity:** 4 compiled steps, each decomposed into 8-14 sub-steps. Model-generated Python scripts call 35+ API endpoints, join data structures, compute weighted scores, and render HTML.

**What to look at first:**
- [Compilation Brief](assets/runs/001-jsonplaceholder-analysis/compiled-steps/compilation-brief.md) — how the compiler decomposed a multi-paragraph request into 4 contracted steps
- [HTML Deliverable](assets/runs/001-jsonplaceholder-analysis/deliverables/user-rankings.html) — the final rendered report
- [Workspace Screenshot](assets/runs/001-jsonplaceholder-analysis/screenshots/ws-runtime.png) — the platform during execution

| Artifact | Link |
|----------|------|
| Full README | [001-jsonplaceholder-analysis/README.md](assets/runs/001-jsonplaceholder-analysis/README.md) |
| Compiled plan | [compiled-full-plan.json](assets/runs/001-jsonplaceholder-analysis/plan/compiled-full-plan.json) |
| Compilation brief | [compilation-brief.md](assets/runs/001-jsonplaceholder-analysis/compiled-steps/compilation-brief.md) |
| All compiled sub-steps | [all-compiled-steps-*.json](assets/runs/001-jsonplaceholder-analysis/compiled-steps/) |
| All attempts | [all-attempts-*.json](assets/runs/001-jsonplaceholder-analysis/compiled-steps/) |
| Deliverables | [deliverables/](assets/runs/001-jsonplaceholder-analysis/deliverables/) |
| Screenshots | [screenshots/](assets/runs/001-jsonplaceholder-analysis/screenshots/) |

---

### Run 002 — Billing Audit

**User message:** Audit billing accuracy for 753 professional services time entries. Reconcile against contracts, rate cards, and invoices. Profile inputs, normalize, resolve contract applicability, compute discrepancies, classify exceptions, build correction candidates, simulate API submissions, generate HTML report and PDF.

**Complexity:** 9 phases compiled into multiple steps. Composite join keys, indirect rate matching, business rule enforcement ($100 max correction, $25 approval threshold, locked invoice rejection), cross-phase consistency validation.

**What to look at first:**
- [Compilation Brief](assets/runs/002-billing-audit/compiled-steps/compilation-brief.md) — how the compiler handled a 9-phase enterprise audit with business rules
- [HTML Report](assets/runs/002-billing-audit/deliverables/billing_audit_report_simone.html) — the final audit report with executive summary, discrepancy tables, and correction outcomes
- [Discrepancies JSON](assets/runs/002-billing-audit/deliverables/discrepancies_simone.json) — every flagged entry with rate deltas, amount mismatches, and cap violations

| Artifact | Link |
|----------|------|
| Full README | [002-billing-audit/README.md](assets/runs/002-billing-audit/README.md) |
| Compiled plan | [full-plan-unfiltered-*.json](assets/runs/002-billing-audit/plan/) |
| Compilation brief | [compilation-brief.md](assets/runs/002-billing-audit/compiled-steps/compilation-brief.md) |
| All compiled sub-steps | [all-compiled-steps-*.json](assets/runs/002-billing-audit/compiled-steps/) |
| All attempts | [all-attempts-*.json](assets/runs/002-billing-audit/compiled-steps/) |
| Deliverables (8 files) | [deliverables/](assets/runs/002-billing-audit/deliverables/) |
| Screenshots | [screenshots/](assets/runs/002-billing-audit/screenshots/) |

---

### Run 003 — CSV Join Transform

**User message:** Profile two CSVs, validate schemas, join time_entries to rates on contract_ref=contract_id, add a rate_match column. Two output files, no reports.

**Complexity:** 2 steps. Deliberately simple — proves the compiler handles lightweight tasks with the same structural rigor as complex multi-phase audits.

**What to look at first:**
- [Compilation Brief](assets/runs/003-csv-join-transform/compiled-steps/compilation-brief.md) — how the compiler handles a minimal 2-step data task
- [Joined Entries JSON](assets/runs/003-csv-join-transform/deliverables/joined_entries2.json) — the output dataset with rate_match flags

| Artifact | Link |
|----------|------|
| Full README | [003-csv-join-transform/README.md](assets/runs/003-csv-join-transform/README.md) |
| Compiled plan | [full-plan-unfiltered-*.json](assets/runs/003-csv-join-transform/plan/) |
| Compilation brief | [compilation-brief.md](assets/runs/003-csv-join-transform/compiled-steps/compilation-brief.md) |
| All compiled sub-steps | [all-compiled-steps-*.json](assets/runs/003-csv-join-transform/compiled-steps/) |
| All attempts | [all-attempts-*.json](assets/runs/003-csv-join-transform/compiled-steps/) |
| Deliverables | [deliverables/](assets/runs/003-csv-join-transform/deliverables/) |
| Screenshots | [screenshots/](assets/runs/003-csv-join-transform/screenshots/) |

---

## Platform Screenshots

Screenshots of the running platform — workspaces, execution views, prompt engineering, governance, observability.

| Screenshot | What it shows |
|-----------|---------------|
| [Workspace Runtime](assets/runs/001-jsonplaceholder-analysis/screenshots/ws-runtime.png) | Full workspace view during a compiled execution run |
| [Execution Plan](assets/runs/001-jsonplaceholder-analysis/screenshots/plan.png) | Compiled plan with step dependencies and status badges |
| [Plan Step Instructions](assets/runs/001-jsonplaceholder-analysis/screenshots/plan-step-instructions.png) | Compiled step contract with objectives and constraints |
| [Step Journal / Sandbox Pipeline](assets/platform-screenshots/step-journal-sandbox-pipeline.png) | Per-step forensic view: sub-steps, code, receipts |
| [Compilation Brief View](assets/runs/001-jsonplaceholder-analysis/screenshots/compilation-brief.png) | AI-generated analysis of compiler decisions |
| [Billing Report](assets/runs/002-billing-audit/screenshots/billing-report.png) | Rendered HTML audit report from a 9-phase billing reconciliation |
| [Workspace File Browser](assets/platform-screenshots/workspace-file-browser.png) | Workspace file system with human and agent-produced files |
| [Prompt Registry](assets/platform-screenshots/prompt-registry.png) | Versioned prompt management with publishing lifecycle |
| [Prompt Editor + Versioning](assets/platform-screenshots/prompt-editor-versioning.png) | Side-by-side prompt editing with version history |
| [Prompt Workbench](assets/platform-screenshots/prompt-workbench.png) | Interactive prompt testing and iteration |
| [Skills — Code View](assets/platform-screenshots/skills-code.png) | Skill package code editor |
| [Skills — File Browser](assets/platform-screenshots/skills-files.png) | Skill package file structure |
| [Sandbox Profiles](assets/platform-screenshots/sandboxes.png) | Execution environment configuration |
| [Sandbox Settings](assets/platform-screenshots/admin-sandbox-settings.png) | Admin sandbox configuration |
| [API Templates / Serialization](assets/platform-screenshots/api-templates-serialization.png) | The bidirectional serializer — template imprinting in action |
| [Blueprint Wizard](assets/platform-screenshots/blueprint-wizard.png) | Guided workspace creation |
| [Sessions](assets/platform-screenshots/sessions.png) | AI conversation sessions |
| [Sessions — Developer View](assets/platform-screenshots/sessions-developer.png) | Session forensics for debugging |
| [Session Continuity](assets/platform-screenshots/session-continuity.png) | Cross-session memory and context |
| [Memory](assets/platform-screenshots/memory.png) | Workspace memory system |
| [AI Settings](assets/platform-screenshots/settings-ai.png) | Per-consumer AI model and reasoning configuration |
| [Observability](assets/platform-screenshots/obeservability.png) | Distributed tracing and system metrics |
| [Logs](assets/platform-screenshots/logs.png) | Log search and analysis |
| [Message Hub](assets/platform-screenshots/message-hub.png) | Enterprise messaging and routing |
| [Message Hub — Operations Console](assets/platform-screenshots/message-hub-operations-console.png) | Message delivery monitoring |
| [Traditional QuickJS Agents](assets/platform-screenshots/tradional-quickjs-agents.png) | Legacy agent execution (pre-compilation) |

---

## Documentation

| Document | What it is |
|----------|-----------|
| [Founder Research Note](docs/founder-research-note-v2.md) | The discovery arc and architectural claim (~8,000 words) |
| [Architecture Thesis](docs/forge-architecture-thesis.md) | The full system reference (~20,000 words) |
| [Execution Profiles](docs/execution-profiles.md) | Per-phase model bindings, validation manifests, skill policy, budgets |
| [HTML Report Generator Skill](docs/html-report-generator/) | A complete skill package — 21 files: scripts, templates, themes, schemas |

---

## Core principles

- Structure before execution
- Discovery before binding
- Contracts before runtime
- Fresh context for each step
- Verification before trust
- Replay as a first-class outcome

## Proof standard

Every claim should be traceable:

```
user message → compiled plan → compilation brief → step contracts → model-generated code → verified deliverables
```

That is the standard this repository is organized around.

---

**Simone Coelho** — [amadalis.ai](https://amadalis.ai) — compiler engineer turned systems architect, building a compiler for autonomous AI work.

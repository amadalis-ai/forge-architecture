# Forge — A Compiler for Autonomous Work

> Autonomous AI should be compiled, not merely interpreted.

This repository contains the public research and proof artifacts behind Forge — a compilation architecture for autonomous AI work built by [Simone Coelho](https://amadalis.ai/about).

## Start here

| Document | What it is |
|----------|-----------|
| [**Founder Research Note**](docs/founder-research-note-v2.md) | The discovery arc: from failed API schemas to a compiler. ~7,000 words. |
| [**Architecture Thesis**](docs/forge-architecture-thesis.md) | The full system treatment: pipeline, type system, validation, executor, capsules, governance. ~18,000 words. |

Both documents are also available on [amadalis.ai](https://amadalis.ai).

## Proof artifacts

| Artifact | What it proves |
|----------|---------------|
| [Dispatch packet](prev-content/dispatch-packets.md) | Complete compilation output for a 4-step run with sub-steps, receipts, and retry evidence |
| [Planner template](prev-content/imprint-template-sample.md) | The imprinting protocol — self-describing templates that drive plan generation |
| [Domain & workflow packs](prev-content/Autonomy_Seed_Packs_v2_Enriched.json) | 12 domain packs, 12 workflow packs, 24 artifact kinds, 15 slots, 5 policy profiles |
| [Contract schemas](prev-content/contract-schemas.md) | Three JSON schemas: planner abstract, compiler compiled, operator envelope |
| [Execution profiles](docs/execution-profiles.md) | Per-phase model bindings, validation manifests, skill policy, budget overrides |
| [Skill package](docs/html-report-generator/) | Full HTML report generator — 21 files: scripts, templates, themes, schemas |

## What this repo is

This is a **public evidence surface**, not a source code dump. It contains:

- The architectural claim and the reasoning behind it
- Real execution artifacts from a running system
- The type system that makes compilation possible
- Proof that the claims are backed by working infrastructure

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
objective → compiled plan → step contract → execution receipt → verified deliverable
```

## Author

**Simone Coelho** — [amadalis.ai](https://amadalis.ai) — compiler engineer turned systems architect, building a compiler for autonomous AI work on nights and weekends.

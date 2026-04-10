# Public proof bundle template

This folder should hold **one** canonical public proof chain.

Do not publish noisy internals. Publish a curated chain that a technical reader can inspect end to end.

## Minimum recommended contents

- `objective.txt` — the original user objective, sanitized if needed
- `compiled-plan.json` — the compiled plan overview
- `step-contract-example.json` — one representative compiled step contract
- `receipts/` — selected preflight or postflight receipts
- `screenshots/` — compiled plan view, execution trace, artifact verification view
- `deliverable/` — the final user-facing artifact from the run

## Publication rules

### Remove
- secrets
- internal URLs
- tenant identifiers
- private customer data
- unstable implementation details you do not want public yet

### Keep
- deterministic IDs when useful
- manifests and contract hashes when safe
- execution evidence
- verification outputs
- the exact shape of the proof chain

## The goal

A reader should be able to say:

> I can see what the user asked for, how the system compiled it, what one step was required to do, what the runtime verified, and what artifact came out the other side.

That is enough to establish credibility.

# Run 001 — JSONPlaceholder Data Analysis & Reporting

## User Message (Input)

> Using the JSONPlaceholder API (https://jsonplaceholder.typicode.com), perform the following data retrieval, analysis, and rendering tasks:
>
> **Step 1 — Fetch Core Data**
>
> Fetch all users from /users. Then, for each user, fetch:
> - Their posts: /users/{id}/posts
> - Their todos: /users/{id}/todos
> - Their albums: /users/{id}/albums
>
> Additionally, fetch:
> - The first 20 posts from /posts (use ?_limit=20)
> - The first 20 comments from /comments (use ?_limit=20)
> - Comments for post 1: /posts/1/comments
> - Photos for album 1: /albums/1/photos
>
> **Step 2 — Establish Relationships**
>
> Map comments to their parent posts using the postId field on each comment. Build a data structure where each post contains its associated comments. Do the same for photos to albums and albums/posts/todos to users.
>
> **Step 3 — Compute Per-User Metrics**
>
> For each user, calculate:
> - post_count — total number of posts authored
> - avg_body_length — average character length of their post bodies
> - todo_completion_rate — fraction of their todos where completed is true (value between 0.0 and 1.0)
> - quality_score — weighted composite: (post_count * 0.4) + (todo_completion_rate * 0.6)
>
> **Step 4 — Save JSON Output**
>
> Write output/enriched-users.json containing an array of objects, one per user, with fields: id, name, email, company_name, post_count, avg_body_length, todo_completion_rate, quality_score.
>
> **Step 5 — Render HTML Tables**
>
> Write output/user-rankings.html — a styled HTML page containing:
>
> 1. User Rankings Table — all users ranked by quality_score descending, showing: rank, name, email, post count, completion rate (as percentage), and quality score.
> 2. Posts with Comments Table — the first 20 posts, each row showing post title, body (truncated to 100 chars), and a nested list of associated comments (author name and comment body). Posts with no comments should show "No comments."
> 3. Summary Statistics — total users, total posts fetched, total comments fetched, average quality score across all users.
>
> Style the HTML with clean, readable CSS (alternating row colors, proper headings, responsive table layout).

---

## What the compiler produced

The system received this natural language message and compiled it through the 5-pass pipeline:

### Pass A — Structural Planning

The planner decomposed the user's multi-paragraph request into **4 plan steps** with a linear dependency chain:

| Step | Label | Depends On | Expected Output |
|------|-------|-----------|-----------------|
| ps-0 | Fetch API datasets | — | `raw_api_data.json` |
| ps-1 | Assemble relationship graph | ps-0 | `related_data_graph.json` |
| ps-2 | Compute user metrics | ps-1 | `enriched-users.json` |
| ps-3 | Render ranking HTML | ps-2 | `user-rankings.html` |

Note: The user described 5 conceptual steps. The planner merged them into 4 compiled steps — combining "save JSON output" into the compute step, since the output is a natural byproduct of the computation.

### Pass C — Compilation

Each step received a compiled contract with:
- SHA-256 contract hash (immutable specification)
- Declared input artifacts (wired to upstream output paths)
- Declared output artifacts (with artifact kind and schema requirements)
- Repair policy (`retry_same_contract`, `max_retries: 6`, `immutable_output_bindings: true`)
- Execution backend routing (`sandbox.session`)

### Pass D — Skill Resolution

Step 3 (render HTML) was bound to the `html-report-generator` skill package — a versioned package containing rendering scripts, CSS templates, themes, and a charting library.

### Execution

Each step was decomposed into 8-14 compiled sub-steps:

1. Prepare workspace directories
2. Materialize upstream inputs into sandbox
3. Symlink input paths to contract-declared locations
4. Generate preflight receipt (hash inputs, infer schemas)
5. Verify required inputs exist
6. **Execute business logic** (model-generated Python code)
7. Generate postflight receipt (hash outputs, validate, infer schemas)
8. Verify expected outputs exist and are non-empty
9. Persist outputs to workspace storage

The model wrote sub-step 6. The compiler generated the other eight.

### Failures and Recovery

Two real failures occurred during this run:

1. **Infrastructure failure (Step 0):** Sandbox returned HTTP 500. System tried fresh handle (failed), provisioned entirely new container, replayed identical code. Model never knew.

2. **Logic failure (Step 2):** Model's own validation caught an extra `rank` field not in the contract. System retried under same immutable contract. Second attempt generated correct code.

---

## Proof chain

Follow the artifacts in order:

| # | Artifact | Location | What it proves |
|---|----------|----------|---------------|
| 1 | User message | This README (above) | The natural language input |
| 2 | Compiled plan | `plan/` | The 4-step plan with dependencies and contracts |
| 3 | Compiled sub-steps | `compiled-steps/` | The code the model generated + the harness around it |
| 4 | Deliverables | `deliverables/` | The final outputs: enriched-users.json + user-rankings.html |
| 5 | Screenshots | `screenshots/` | Visual evidence from the workspace UI |

---

## Directories

```
001-jsonplaceholder-analysis/
├── README.md              ← you are here
├── plan/                  ← compiled plan steps and contracts
├── compiled-steps/        ← sub-steps with model-generated code
├── deliverables/          ← final output files
└── screenshots/           ← workspace UI during/after the run
```

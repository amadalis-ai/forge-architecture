# Architecture Diagrams — Draft

> Review these Mermaid diagrams before placing them in documents.
> GitHub renders Mermaid natively in markdown. For the website, we'll need to decide rendering approach.

---

## Diagram 1: The Compilation Pipeline

Shows the 5-pass flow from user intent to governed execution.

```mermaid
flowchart LR
    U["👤 User Objective\n(natural language)"]
    A["Pass A\nStructural\nPlanning"]
    B["Pass B\nIntent\nResolution"]
    C["Pass C\nCompilation"]
    D["Pass D\nSkill\nResolution"]
    E["Pass E\nFreeze &\nDispatch"]

    U --> A
    A --> B
    B --> C
    C --> D
    D --> E

    style A fill:#1e2028,stroke:#c8a44e,color:#e8e9ed
    style B fill:#1e2028,stroke:#c8a44e,color:#e8e9ed
    style C fill:#1e2028,stroke:#c8a44e,color:#e8e9ed
    style D fill:#1e2028,stroke:#c8a44e,color:#e8e9ed
    style E fill:#1e2028,stroke:#c8a44e,color:#e8e9ed
    style U fill:#0a0b0f,stroke:#9498a8,color:#e8e9ed

    A -.- A1["🧠 Frontier model\nExtended thinking\nStep graph + dependencies"]
    B -.- B1["🧠 Fast model\nDomain packs\nWorkflow packs\nPolicy profiles"]
    C -.- C1["⚙️ Deterministic\nSlot bindings\nAdapter insertion\nContract hashes"]
    D -.- D1["🧠 Fast model\nTool selection\nSkill binding\nExecution mode"]
    E -.- E1["⚙️ Platform\nProfile snapshot\nLedger write\nQueue dispatch"]
```

---

## Diagram 2: The Step Harness — General Architecture

The executor's code is not limited to one pattern. It can compute, iterate, call governed evaluators, write files, adapt — whatever the contract requires. The harness wraps it with verification.

```mermaid
flowchart LR
    subgraph PRE["Pre-execution Harness"]
        direction TB
        H1["1. Prepare workspace"]
        H2["2. Materialize inputs"]
        H3["3. Project paths"]
        H4["4. Preflight receipt"]
        H5["5. Verify inputs"]
        H1 --> H2 --> H3 --> H4 --> H5
    end

    subgraph EXEC["6. Executor Model's Code"]
        direction TB
        E1["Read contracted inputs"]
        E2["Write code to fulfill\nthe step contract"]
        E3["Iterate, compute,\ntransform, build,\ncall governed tools"]
        E4["Write outputs that\nsatisfy the contract"]

        E1 --> E2 --> E3 --> E4
    end

    subgraph POST["Post-execution Harness"]
        direction TB
        H7["7. Postflight receipt"]
        H8["8. Verify outputs"]
        H9["9. Persist"]
        H7 --> H8 --> H9
    end

    PRE --> EXEC --> POST

    style PRE fill:#0a0b0f,stroke:#2a2d38,color:#9498a8
    style EXEC fill:#161920,stroke:#c8a44e,color:#e8e9ed
    style POST fill:#0a0b0f,stroke:#2a2d38,color:#9498a8
    style E3 fill:#1e2028,stroke:#c8a44e,color:#c8a44e,stroke-width:2px
```

---

## Diagram 2a: Example — Resume Screening (1,000 candidates)

The executor loops over candidates, assembles per-item evidence bundles, and calls a governed evaluator model per item.

```mermaid
flowchart LR
    subgraph LOOP["Executor iterates over 1,000 candidates"]
        direction TB
        R1["Extract resume\nsource text"]
        R2["Write extracted\nprofile JSON"]
        R3["Assemble evidence bundle\n(source + profile + rubric)"]
        R4["🧠 Call governed\nevaluator model\nvia tool bridge"]
        R5["Write proof-backed\ncandidate card"]
        R6{"More\ncandidates?"}

        R1 --> R2 --> R3 --> R4 --> R5 --> R6
        R6 -->|Yes| R1
    end

    AGG["Aggregate cards\ninto batch rankings\n→ global merge\n→ top-N re-eval"]

    R6 -->|No| AGG

    style LOOP fill:#161920,stroke:#c8a44e,color:#e8e9ed
    style R4 fill:#1e2028,stroke:#c8a44e,color:#c8a44e,stroke-width:2px
    style AGG fill:#0a0b0f,stroke:#c8a44e,color:#c8a44e
```

---

## Diagram 2b: Example — Building a Website (500 pages)

The executor iterates over a page manifest, generates each page individually, and optionally calls a governed evaluator for quality verification.

```mermaid
flowchart LR
    subgraph LOOP["Executor iterates over page manifest"]
        direction TB
        W1["Read page spec\nfrom manifest"]
        W2["Generate page HTML\nusing skill scripts +\ntheme assets"]
        W3["Validate structure\n(navigation, links,\nrequired components)"]
        W4{"Needs semantic\nreview?"}
        W5["🧠 Call governed\nevaluator model\n(content quality)"]
        W6["Write verified page\nto output"]
        W7{"More\npages?"}

        W1 --> W2 --> W3 --> W4
        W4 -->|No| W6
        W4 -->|Yes| W5 --> W6
        W6 --> W7
        W7 -->|Yes| W1
    end

    OUT["Assemble site bundle\nnavigation index\nasset manifest"]

    W7 -->|No| OUT

    style LOOP fill:#161920,stroke:#c8a44e,color:#e8e9ed
    style W5 fill:#1e2028,stroke:#c8a44e,color:#c8a44e,stroke-width:2px
    style OUT fill:#0a0b0f,stroke:#c8a44e,color:#c8a44e
```

---

## Diagram 2c: Example — Billing Audit (753 entries)

The executor iterates over time entries, performs computational reconciliation, and calls the governed evaluator for complex judgment items.

```mermaid
flowchart LR
    subgraph LOOP["Executor iterates over 753 time entries"]
        direction TB
        B1["Read entry +\nmatched contract +\nrate card"]
        B2["Compute rate delta,\namount check,\ncap check"]
        B3{"Discrepancy\nfound?"}
        B4["Write discrepancy\nrecord with\ncomputation proof"]
        B5{"Complex\njudgment?"}
        B6["🧠 Call governed\nevaluator model\n(exception classification)"]
        B7["Write audit result"]
        B8{"More\nentries?"}

        B1 --> B2 --> B3
        B3 -->|No| B8
        B3 -->|Yes| B4 --> B5
        B5 -->|No| B7
        B5 -->|Yes| B6 --> B7
        B7 --> B8
        B8 -->|Yes| B1
    end

    RPT["Build correction\ncandidates\n→ simulate submissions\n→ generate report"]

    B8 -->|No| RPT

    style LOOP fill:#161920,stroke:#c8a44e,color:#e8e9ed
    style B6 fill:#1e2028,stroke:#c8a44e,color:#c8a44e,stroke-width:2px
    style RPT fill:#0a0b0f,stroke:#c8a44e,color:#c8a44e
```

---

## Diagram 2d: Example — Customer Onboarding

Mix of deterministic steps (sealed capsule segments) and adaptive steps where the executor queries data mid-workflow and adjusts.

```mermaid
flowchart LR
    subgraph SEALED["Deterministic (Sealed)"]
        direction TB
        S1["Apply branding\n& theming"]
        S2["Load base\nconfiguration"]
        S3["Create user\naccounts & roles"]
        S1 --> S2 --> S3
    end

    subgraph ADAPTIVE["Adaptive (Executor loops)"]
        direction TB
        A1["Query customer\ndata source"]
        A2["Analyze schema\n& data quality"]
        A3{"Data issues?"}
        A4["🧠 Call evaluator\nfor remediation\nrecommendation"]
        A5["Transform &\nload data"]
        A6["Configure\nintegrations"]
        A7["Run validation\nchecks"]

        A1 --> A2 --> A3
        A3 -->|No| A5
        A3 -->|Yes| A4 --> A5
        A5 --> A6 --> A7
    end

    subgraph VERIFY["Governed Verification"]
        direction TB
        V1["🧠 Call evaluator:\nonboarding completeness\nagainst checklist"]
        V2["Generate onboarding\nreport"]
        V1 --> V2
    end

    SEALED --> ADAPTIVE --> VERIFY

    style SEALED fill:#0a0b0f,stroke:#2a2d38,color:#9498a8
    style ADAPTIVE fill:#161920,stroke:#c8a44e,color:#e8e9ed
    style VERIFY fill:#0a0b0f,stroke:#c8a44e,color:#c8a44e
    style A4 fill:#1e2028,stroke:#c8a44e,color:#c8a44e,stroke-width:2px
    style V1 fill:#1e2028,stroke:#c8a44e,color:#c8a44e,stroke-width:2px
```

---

## Diagram 3: Governed Evaluator — The Tool Bridge

Shows how the sandbox executor calls the evaluator model through the platform's governed tool bridge.

```mermaid
sequenceDiagram
    participant S as Sandbox Executor<br/>(model-generated code)
    participant B as Governed Tool Bridge<br/>(platform)
    participant E as Evaluator Model<br/>(separate AI)
    participant P as Proof Store<br/>(R2 + Postgres)

    S->>S: Extract source text
    S->>S: Write derived JSON
    S->>S: Assemble evidence bundle

    S->>B: call("operator.artifact.evaluate",<br/>{path: bundle, rubric, enforcement: "block"})

    B->>B: Validate against budget
    B->>B: Load bundle contents
    B->>B: Build bounded model context

    B->>E: Evaluate evidence bundle<br/>against rubric

    E->>E: Semantic judgment:<br/>faithful? grounded?<br/>hallucinations? omissions?

    E->>B: Evaluation result + verdict

    B->>P: Persist proof:<br/>model_call_id, bundle_sha256,<br/>verdict, evidence

    B->>S: Return result to sandbox

    S->>S: Write per-item audit card
    S->>S: Continue to next item
```

---

## Diagram 4: Hierarchical Processing at Scale

Shows how 1,000 items are processed through iteration, not context stuffing.

```mermaid
flowchart TB
    DS["📋 Dataset Manifest\n1,000 items"]

    subgraph BATCHES["Batch Processing"]
        B1["Batch 1\n(items 1-20)"]
        B2["Batch 2\n(items 21-40)"]
        BN["Batch N\n(items 981-1000)"]
    end

    subgraph ITEM["Per-Item Processing (× 1,000)"]
        I1["Extract source\nrepresentation"]
        I2["Write derived\nJSON / ranking"]
        I3["Assemble evidence\nbundle"]
        I4["🧠 Governed evaluator\nmodel call"]
        I5["Proof-backed\ncandidate card"]

        I1 --> I2 --> I3 --> I4 --> I5
    end

    subgraph AGG["Aggregation"]
        A1["Batch rankings\nfrom audited cards"]
        A2["Global merge\nacross batches"]
        A3["Top-N re-evaluation\nagainst source bundles"]
        A4["📄 Final ranked\nreport"]

        A1 --> A2 --> A3 --> A4
    end

    DS --> BATCHES
    B1 --> ITEM
    B2 --> ITEM
    BN --> ITEM
    ITEM --> AGG

    style I4 fill:#1e2028,stroke:#c8a44e,color:#c8a44e,stroke-width:2px
    style DS fill:#0a0b0f,stroke:#9498a8,color:#e8e9ed
    style A4 fill:#0a0b0f,stroke:#c8a44e,color:#c8a44e
```

---

## Diagram 5: Executor + Evaluator — Separation of Concerns

Shows this as an architectural principle, not a sandbox implementation detail.

```mermaid
flowchart LR
    subgraph COMPILE["Compilation Phase"]
        P["Planner\n🧠 Plans the work"]
        C["Compiler\n⚙️ Freezes contracts"]
    end

    subgraph EXECUTE["Execution Phase"]
        EX["Executor\n🧠 Does the work\nWrites code\nOwns the loop"]
        EV["Evaluator\n🧠 Judges the work\nSemantic verification\nEvidence bundles"]
    end

    subgraph GOVERN["Governance Layer"]
        TB["Tool Bridge\nBudgets, tracing,\nproof persistence"]
        RE["Receipts\nSHA-256 hashes\nSchema inference"]
    end

    P --> C
    C -->|"Frozen\ncontracts"| EX

    EX -->|"Calls via\ntool bridge"| TB
    TB -->|"Governed\nmodel call"| EV
    EV -->|"Verdict +\nproof"| TB
    TB -->|"Result"| EX

    EX -->|"Outputs"| RE

    style COMPILE fill:#0a0b0f,stroke:#2a2d38,color:#9498a8
    style EXECUTE fill:#0a0b0f,stroke:#c8a44e,color:#e8e9ed
    style GOVERN fill:#0a0b0f,stroke:#2a2d38,color:#9498a8
    style EX fill:#161920,stroke:#c8a44e,color:#e8e9ed
    style EV fill:#161920,stroke:#c8a44e,color:#c8a44e
    style TB fill:#161920,stroke:#c8a44e,color:#9498a8
```

---

## Diagram 6: Evidence Bundle Structure

Shows what the evaluator model actually receives.

```mermaid
flowchart TB
    subgraph BUNDLE["Evidence Bundle (one item)"]
        direction TB
        SRC["Source Evidence"]
        DRV["Derived Evidence"]
        RUB["Rubric"]

        SRC --- S1["resume_source_text.md\n(original extracted text)"]
        SRC --- S2["resume_page_001.png\n(scanned page image)"]

        DRV --- D1["extracted_profile.json\n(candidate fields)"]
        DRV --- D2["ranking_judgment.json\n(scoring + rationale)"]

        RUB --- R1["Criteria:\n- no invented facts\n- no omitted evidence\n- rationale cites source\n- uncertainty flagged"]
    end

    EVAL["🧠 Evaluator Model"]
    PROOF["Proof Record\nmodel_call_id\nbundle_sha256\nverdict\nper-criterion results"]

    BUNDLE --> EVAL
    EVAL --> PROOF

    style BUNDLE fill:#161920,stroke:#2a2d38,color:#9498a8
    style EVAL fill:#1e2028,stroke:#c8a44e,color:#c8a44e
    style PROOF fill:#1e2028,stroke:#c8a44e,color:#9498a8
```

---

## Where these diagrams should go

| Diagram | Document | Location |
|---------|----------|----------|
| 1. Compilation Pipeline | Thesis Part V, Section 5.1 | After the text pipeline overview |
| 2. Step Harness with Loop | Thesis Part VI, Section 6.3 | Replace the text-only harness description |
| 3. Governed Tool Bridge | Thesis Part VI, new section 6.x | Between executor and verification |
| 4. Hierarchical Processing | Thesis Part X-b | In the resume screening use case |
| 5. Executor + Evaluator | Thesis Part VI, Section 6.1 or new section | Architectural elevation of the evaluator concept |
| 6. Evidence Bundle | Thesis Part VI or new section | Alongside the governed evaluator description |

For the **founder note**, diagrams 3 (tool bridge sequence) and 5 (executor + evaluator separation) are the most relevant — they show the architecture without overwhelming a shorter document.

For the **landing page**, diagram 5 could be simplified into a visual on the page, but Mermaid won't render in Astro without a plugin. We'd need to render it as an SVG or image.

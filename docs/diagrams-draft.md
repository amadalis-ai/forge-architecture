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

## Diagram 2: The Step Harness with Executor Loop

Shows the 9-step harness and expands step 6 to reveal the executor's iteration and governed evaluator calls.

```mermaid
flowchart TB
    subgraph HARNESS["Compiler-Generated Harness"]
        H1["1. Prepare\nworkspace"]
        H2["2. Materialize\ninputs"]
        H3["3. Project\ninput paths"]
        H4["4. Preflight\nreceipt"]
        H5["5. Verify\nrequired inputs"]
        H7["7. Postflight\nreceipt"]
        H8["8. Verify\nexpected outputs"]
        H9["9. Persist\noutputs"]
    end

    subgraph EXEC["6. Executor Model's Code"]
        direction TB
        E1["Read contracted inputs"]
        E2{"Iterate over\nitems?"}
        E3["Process item:\nextract, transform,\nwrite intermediate files"]
        E4["Assemble evidence\nbundle for item"]
        E5["Call governed\nevaluator model\nvia tool bridge"]
        E6["Write per-item\naudit result"]
        E7["More items?"]
        E8["Aggregate results\nWrite final output"]

        E1 --> E2
        E2 -->|"Single item\nor computation"| E8
        E2 -->|"Dataset\niteration"| E3
        E3 --> E4
        E4 --> E5
        E5 --> E6
        E6 --> E7
        E7 -->|Yes| E3
        E7 -->|No| E8
    end

    H1 --> H2 --> H3 --> H4 --> H5 --> EXEC --> H7 --> H8 --> H9

    style HARNESS fill:#0a0b0f,stroke:#2a2d38,color:#9498a8
    style EXEC fill:#161920,stroke:#c8a44e,color:#e8e9ed
    style E5 fill:#1e2028,stroke:#c8a44e,color:#c8a44e,stroke-width:2px
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

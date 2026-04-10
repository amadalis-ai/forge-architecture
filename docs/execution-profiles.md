# Execution Profiles

> **Version**: 2026-04-09 v2.0
> **Section**: Govern > Execution Profiles
> **Route**: `/admin/workspaces/:workspace_id/execution-profiles`
> **Backend**: `___new_mcp_server/src/services/execution-profiles/`
> **Schema**: `execution_profile.manifest.v1`

## What Execution Profiles Are

An execution profile is a **reusable configuration envelope** that controls how the platform plans, executes, and validates AI-driven runs. It is the single artifact that determines which AI model is called, what prompt it receives, how much time and budget it gets, what reasoning strategy it uses, which skills are available, and how outputs are validated -- all swappable at runtime without changing any code.

Every operator, builder, or research run resolves to exactly one execution profile before the first AI call is made. That profile is frozen into an immutable snapshot at run start, guaranteeing that mid-flight configuration changes cannot affect an in-progress run.

Profiles are versioned, publishable, and bindable at multiple scopes. An enterprise can define a single "high-reasoning operator" profile, publish it, bind it as the tenant default, and every workspace inherits it. A specific workspace can override that default with a cost-optimized profile. A specific run can override both with an explicit profile reference. This cascade gives enterprises full control over AI behavior from the broadest scope down to individual runs.

---

## Why Execution Profiles Matter for Enterprise

**Model Flexibility.** Swap AI models without touching code. A profile bound to Claude Opus for high-stakes financial analysis can be cloned and rebound to Claude Sonnet for routine data processing. Each profile carries its own model selection, reasoning depth, token budget, and temperature -- so the same pipeline produces different cost/quality tradeoffs based solely on which profile is active.

**Governance at Scale.** Tenant administrators define default profiles that apply to all workspaces. Workspace owners can override with workspace-specific profiles. Individual runs can override further. This hierarchy means governance policies (model selection, validation strictness, timeout ceilings) flow downward from organizational defaults while allowing targeted exceptions.

**Reproducibility.** Every run freezes its profile into an immutable snapshot. When investigating why a run produced a specific result, the snapshot tells you exactly which model, which prompt version, which validation rules, and which parameter overrides were in effect -- even if the profile has since been updated.

**Skill Curation.** Profiles can pin specific skills (data analysis libraries, visualization tools, domain-specific helpers) and deny others. A compliance-focused profile might pin only approved data handling skills and deny general-purpose web research. A creative profile might enable everything.

**Validation Control.** Each profile declares how strictly outputs are validated at every phase of the pipeline -- from plan generation through final output. Validation can block (hard fail), report (log without failing), or be turned off entirely. This lets enterprises run strict validation in production and relaxed validation during development.

---

## Profile Families

Every profile belongs to exactly one family. The family determines which runtime consumers (planner, executor, validator) the profile governs.

| Family | Purpose | Consumers Governed |
|--------|---------|-------------------|
| `operator` | Multi-step task execution -- plan, compile, execute in sandbox | Planner (4 phases), executor (4 backends), intent normalizer, skill resolver |
| `builder` | Structured workflow runs -- deterministic step replay | Planner, executor |
| `research` | Research-oriented runs -- extended reasoning, deep analysis | Planner, executor |

Families are closed -- adding a new family requires a schema migration. This prevents profile sprawl and ensures the runtime knows exactly which consumers to configure for each family.

---

## The Manifest

The manifest (`ManifestJson`) is the complete specification stored inside each profile version. It is the single document that the runtime reads to configure every aspect of a run. Schema version: `execution_profile.manifest.v1`.

### Identity

```json
{
  "schema_version": "execution_profile.manifest.v1",
  "identity": {
    "family": "operator",
    "profile_key": "high-reasoning-analyst",
    "display_name": "High-Reasoning Analyst"
  }
}
```

The identity section is enforced coherent with the profile header -- the `family` and `profile_key` in the manifest must match the profile's database record. This prevents a manifest from being copied into an incompatible profile.

---

### Consumer Bindings

A consumer binding tells the runtime **which prompt to use, which model to call, and what parameters to apply** for a specific consumer (planner, executor, etc.). This is the core mechanism that makes profiles powerful.

```typescript
interface ExecutionProfileConsumerBinding {
  consumer_key: string;          // Which consumer: 'operator_planner', 'operator_step_executor', etc.
  prompt_binding_ref: string;    // Prompt template reference: 'workspace.operator.planner.system'
  model_binding_ref?: string;    // Model override: 'anthropic:claude-opus-4-6'
  runtime_profile_ref?: string;  // Reserved for future runtime profile references
  persona_ref?: string;          // Reserved for persona context injection
  runtime_overrides?: ExecutionProfileRuntimeOverrides;
}
```

**`consumer_key`** identifies which runtime consumer this binding configures. The platform supports 14 named consumers:

| Consumer Key | Role |
|-------------|------|
| `operator_planner` | Generates the abstract execution plan |
| `operator_intent_resolver` | Selects domain packs and policy profiles |
| `operator_skill_resolver` | Selects tools, skills, and execution mode per step |
| `operator_step_executor` | Executes individual steps in the sandbox |
| `wizard_planner` | Interactive wizard-style planning |
| `router_classifier` | Classifies intent to select routing |
| `intent_normalizer` | Preflight intent normalization |
| `docs_summarizer` | Document summarization |
| `chat_distillation` | Chat context distillation |
| `assist_distillation` | Assistant context distillation |
| `agent_distillation` | Agent context distillation |
| `plan_brief_summarizer` | Plan brief generation |
| `compilation_brief_summarizer` | Compilation brief generation |

**`prompt_binding_ref`** is a reference to a versioned prompt template stored in the prompt registry. The reference can take three forms:

- **Bare template ID**: `workspace.operator.planner.system` -- resolves to the currently published version
- **Pinned version**: `workspace.operator.planner.system@v3` -- resolves to exactly version 3
- **Version row ID**: `pv_abc123` -- resolves to a specific version by its database ID

Prompt resolution is fail-closed: if the reference cannot resolve to a published prompt, the run fails. There is no silent fallback to hardcoded defaults.

**`model_binding_ref`** directly overrides which AI model is used for this consumer. When set, it bypasses the governed settings model resolution entirely. Format is `provider:model-id`, for example:

- `anthropic:claude-opus-4-6` -- Anthropic Claude Opus
- `anthropic:claude-sonnet-4-6` -- Anthropic Claude Sonnet
- `openai:gpt-4o` -- OpenAI GPT-4o
- `openai:o3` -- OpenAI o3

When `model_binding_ref` is not set, model selection falls through to governed settings:
1. `ai.consumers.{consumer_key}.model_alias` (consumer-specific governed setting)
2. `ai.utility_model` (shared utility model)
3. `'utility_model'` literal (provider mux resolves to the actual model)

---

### Runtime Overrides

Runtime overrides are the parameters that control how the AI model behaves during inference. They can be set at the consumer binding level within a profile, giving fine-grained control over each phase of execution.

```typescript
interface ExecutionProfileRuntimeOverrides {
  // Inference parameters
  timeout_ms?: number;              // Model call timeout (milliseconds)
  max_tokens?: number;              // Maximum output tokens
  temperature?: number;             // Sampling temperature (0.0 = deterministic, higher = creative)

  // Reasoning parameters (provider-specific, automatically filtered)
  reasoning_effort?: string;        // 'minimal' | 'low' | 'medium' | 'high' | 'xhigh'
  use_extended_thinking?: boolean;  // Anthropic extended thinking mode
  thinking_budget_tokens?: number;  // Anthropic thinking budget (minimum 1024)
  use_responses_reasoning?: boolean;// OpenAI Responses API reasoning
  reasoning_summary?: string;       // 'auto' | 'concise' | 'detailed'
  max_think_ms?: number;            // Thinking time limit (provider-agnostic)

  // Network-level timeouts
  provider_timeouts?: {
    request_timeout_ms?: number;              // Overall request timeout
    stream_first_token_timeout_ms?: number;   // Time to first token (streaming)
    stream_inter_chunk_timeout_ms?: number;   // Inter-chunk stall timeout (streaming)
  };
}
```

#### How Runtime Overrides Cascade

Runtime overrides follow a strict priority chain. Higher layers override lower layers:

```
Priority (lowest → highest):

1. Consumer built-in defaults
   └─ Hardcoded per consumer type (e.g., operator_step_executor: 120s timeout, 4096 max_tokens, 0.1 temp)

2. Governed settings: consumer_defaults
   └─ ai.consumer_defaults.timeout_ms, ai.consumer_defaults.temperature, etc.

3. Governed settings: consumer-specific
   └─ ai.consumers.operator_step_executor.timeout_ms, etc.

4. Workspace-level overrides
   └─ Per-workspace consumer config (consumer_defaults + consumer-specific)

5. Execution profile runtime_overrides  ← HIGHEST PRIORITY
   └─ Profile manifest consumer binding runtime_overrides
```

This means a profile's `runtime_overrides` always win. If a profile sets `temperature: 0.0` on the executor binding, that value is used regardless of what governed settings or workspace overrides say.

#### Reasoning Parameters by Provider

The platform automatically filters reasoning parameters based on the resolved provider. Unsupported parameters are dropped before the API call, not rejected:

| Parameter | Anthropic | OpenAI | Workers AI | Gemini |
|-----------|-----------|--------|------------|--------|
| `reasoning_effort` | -- | Yes | -- | -- |
| `use_extended_thinking` | Yes | -- | -- | -- |
| `thinking_budget_tokens` | Yes (min 1024) | -- | -- | -- |
| `use_responses_reasoning` | -- | Yes | -- | -- |
| `reasoning_summary` | Yes | Yes | -- | -- |
| `max_think_ms` | Yes | Yes | Yes | Yes |

Global reasoning governance in governed settings provides additional controls:
- `ai.reasoning.anthropic_thinking_enabled` -- master switch for Anthropic thinking
- `ai.reasoning.anthropic_budget_tokens` -- global Anthropic thinking budget ceiling
- `ai.reasoning.anthropic_visibility` -- how thinking is surfaced: `policy_safe`, `summary_only`, or `raw_ui`
- `ai.reasoning.openai_responses_enabled` -- master switch for OpenAI reasoning
- `ai.reasoning.gemini_thinking_enabled` -- master switch for Gemini thinking

---

### Planner Phase Bindings

The operator pipeline has four distinct planning phases, each of which can have its own consumer binding -- meaning each phase can use a **different model, different prompt, and different parameters**.

```json
{
  "planner_phase_bindings": {
    "pass_a": {
      "consumer_key": "operator_planner",
      "prompt_binding_ref": "workspace.operator.planner.system",
      "model_binding_ref": "anthropic:claude-opus-4-6",
      "runtime_overrides": {
        "temperature": 0.7,
        "max_tokens": 8192,
        "use_extended_thinking": true,
        "thinking_budget_tokens": 4096
      }
    },
    "pass_b": {
      "consumer_key": "operator_intent_resolver",
      "prompt_binding_ref": "workspace.operator.intent_resolver.system",
      "model_binding_ref": "anthropic:claude-sonnet-4-6",
      "runtime_overrides": {
        "temperature": 0.3,
        "max_tokens": 4096
      }
    },
    "pass_c": {
      "consumer_key": "operator_skill_resolver",
      "prompt_binding_ref": "workspace.operator.skill_resolver.system",
      "model_binding_ref": "anthropic:claude-sonnet-4-6",
      "runtime_overrides": {
        "temperature": 0.2,
        "max_tokens": 4096
      }
    },
    "repair": {
      "consumer_key": "operator_planner",
      "prompt_binding_ref": "workspace.operator.planner.repair.system",
      "model_binding_ref": "anthropic:claude-opus-4-6",
      "runtime_overrides": {
        "temperature": 0.1,
        "use_extended_thinking": true,
        "thinking_budget_tokens": 8192
      }
    }
  }
}
```

| Phase | Purpose | Typical Model Strategy |
|-------|---------|----------------------|
| `pass_a` | Initial plan generation -- abstract step graph with objectives | High capability model with extended thinking for complex planning |
| `pass_b` | Intent resolution -- selects domain packs and policy profiles | Faster model sufficient for retrieval-augmented classification |
| `pass_c` | Skill resolution -- selects tools, skills, and execution mode | Faster model sufficient for tool selection |
| `repair` | Re-planning after validation failure | High capability model with extended thinking for error correction |

This is a key enterprise capability: use an expensive, high-reasoning model for the initial plan and repair phases where quality matters most, and a faster, cheaper model for the mechanical resolution phases. A single profile controls this entire strategy.

---

### Executor Backend Bindings

The executor supports four backends, each of which can have its own consumer binding:

```json
{
  "executor_by_backend": {
    "tool_loop": {
      "consumer_key": "operator_step_executor",
      "prompt_binding_ref": "workspace.operator.step_executor.system",
      "model_binding_ref": "anthropic:claude-sonnet-4-6",
      "runtime_overrides": { "temperature": 0.1, "max_tokens": 4096 }
    },
    "code.execute": {
      "consumer_key": "operator_step_executor",
      "prompt_binding_ref": "workspace.operator.step_executor.system",
      "model_binding_ref": "anthropic:claude-sonnet-4-6",
      "runtime_overrides": { "temperature": 0.1, "max_tokens": 4096 }
    },
    "sandbox.session": {
      "consumer_key": "operator_step_executor",
      "prompt_binding_ref": "workspace.operator.step_executor.system",
      "model_binding_ref": "anthropic:claude-opus-4-6",
      "runtime_overrides": {
        "temperature": 0.1,
        "max_tokens": 8192,
        "use_extended_thinking": true,
        "thinking_budget_tokens": 4096
      }
    },
    "edge_isolate": {
      "consumer_key": "operator_step_executor",
      "prompt_binding_ref": "workspace.operator.step_executor.system",
      "model_binding_ref": "anthropic:claude-sonnet-4-6",
      "runtime_overrides": { "temperature": 0.0, "max_tokens": 4096 }
    }
  }
}
```

| Backend | Purpose | Typical Strategy |
|---------|---------|-----------------|
| `tool_loop` | Simple tool invocations without sandbox | Faster model, lower cost |
| `code.execute` | Direct code execution | Faster model, lower cost |
| `sandbox.session` | Full sandbox session with file I/O, package installation, multi-step execution | Higher capability model with extended thinking |
| `edge_isolate` | Edge-optimized JS/TS execution on Cloudflare Workers | Deterministic settings (temperature 0.0) |

A legacy scalar `executor` binding is supported for backward compatibility. When present, it applies to all backends. The canonical form is `executor_by_backend`, which is always materialized on write.

---

### Validation Manifest

The validation manifest controls how strictly the platform validates outputs at each phase of the pipeline.

```json
{
  "validation": {
    "schema_version": "execution_profile.validation.v1",
    "ceiling_policy_ref": "valpack.operator.ceiling@v1",
    "phases": {
      "planner_candidate": {
        "pack_ref": "valpack.operator.generic.planner@v1",
        "mode": "report"
      },
      "compiled_plan": {
        "pack_ref": "valpack.operator.generic.compiled@v1",
        "mode": "block"
      },
      "step_input": {
        "pack_ref": "valpack.operator.generic.step-input@v1",
        "mode": "block"
      },
      "step_output": {
        "default_pack_ref": "valpack.operator.generic.step-output@v1",
        "matchers": [
          { "artifact_path": "*.json", "pack_ref": "valpack.operator.json-schema@v1" },
          { "artifact_path": "*.html", "pack_ref": "valpack.operator.html-report@v1" }
        ],
        "mode": "block"
      },
      "final_output": {
        "pack_ref": "valpack.operator.generic.final@v1",
        "mode": "report"
      }
    },
    "allowed_overrides": ["step_output.mode", "final_output.mode"]
  }
}
```

| Phase | When It Runs | What It Validates |
|-------|-------------|-------------------|
| `planner_candidate` | After plan generation (pass_a) | Plan structure, step dependencies, objective clarity |
| `compiled_plan` | After compilation (pass_c) | Compiled step contracts, I/O bindings, artifact schemas |
| `step_input` | Before each step executes | Input availability, path resolution, schema compliance |
| `step_output` | After each step completes | Output existence at declared paths, schema validation, formula checks |
| `final_output` | After all steps complete | End-to-end output completeness and quality |

Each phase operates in one of three modes:

| Mode | Behavior |
|------|----------|
| `block` | Validation failure stops the run. Used for critical correctness requirements. |
| `report` | Validation failure is logged but the run continues. Used for quality monitoring. |
| `off` | Phase is skipped entirely. Used during development or for trusted pipelines. |

The `step_output` phase supports **artifact-pattern matchers** -- different validation packs can be applied based on the output file extension. JSON outputs might be validated against a strict schema while HTML outputs are validated for structural completeness.

The `ceiling_policy_ref` sets the maximum validation strictness. Individual phases cannot exceed the ceiling. The `allowed_overrides` list declares which phase settings can be overridden at runtime (e.g., relaxing `step_output.mode` from `block` to `report` for debugging).

---

### Skill Policy

The skill policy controls which skills (data analysis, visualization, web research, domain-specific tools) are available during a run.

```json
{
  "skill_policy": {
    "pinned_skills": [
      {
        "skill_id": "html-report-generator",
        "priority": "required",
        "scope": "executor",
        "version_id": null
      },
      {
        "skill_id": "data-analysis-toolkit",
        "priority": "preferred",
        "scope": "both"
      }
    ],
    "denied_skills": ["general-web-research"],
    "autoload_mode": "profile_plus_discovery"
  }
}
```

**Pinned Skills** are automatically loaded at the highest priority before any dynamic discovery occurs. Each pinned skill has:

| Field | Options | Meaning |
|-------|---------|---------|
| `priority` | `required` / `preferred` | Required: run fails if skill cannot resolve. Preferred: best-effort, run continues without it. |
| `scope` | `planner` / `executor` / `both` | Where the skill's context is injected. |
| `version_id` | version ID or null | Pin to a specific version, or use the current published version. |

**Denied Skills** are explicitly blocked. Denial overrides dynamic discovery -- even if the system would normally discover and suggest a denied skill, it is excluded. Useful when a domain-specific pinned skill replaces a generic one.

**Autoload Mode** controls how pinning interacts with dynamic discovery:

| Mode | Behavior |
|------|----------|
| `profile_plus_discovery` (default) | Pinned skills + dynamically discovered skills. Pinned take priority on conflicts. |
| `profile_only` | Only pinned skills. Discovery disabled entirely. Maximum control. |
| `discovery_only` | Profile skill_policy ignored. Normal dynamic discovery. |

---

### Budget Overrides

Budget overrides in the profile override tenant-level governed settings for timeout and resource limits.

```json
{
  "budgets": {
    "max_steps": 25,
    "window_size": 6,
    "sandbox_session_dispatch_timeout_ms": 600000,
    "operator_step_attempt_dispatch_timeout_ms": 300000,
    "operator_step_attempt_dispatch_stall_timeout_ms": 300000,
    "operator_step_attempt_activity_stall_timeout_ms": 30000,
    "attempt_stale_heartbeat_timeout_ms": 120000,
    "heartbeat_emission_interval_ms": 15000,
    "materialize_timeout_ms": 240000,
    "file_overwrite_policy": "archive"
  }
}
```

| Budget | Range | Default | Purpose |
|--------|-------|---------|---------|
| `max_steps` | 1-100 | governed | Maximum steps per operator plan |
| `window_size` | 1-12 | governed | Model steps per sandbox window |
| `sandbox_session_dispatch_timeout_ms` | 60,000-1,800,000 | 600,000 | Wall-clock timeout for sandbox dispatch |
| `operator_step_attempt_dispatch_timeout_ms` | 60,000-1,800,000 | 300,000 | DO-owned step attempt dispatch timeout |
| `operator_step_attempt_dispatch_stall_timeout_ms` | 30,000-1,800,000 | 300,000 | DO-owned dispatch stall timeout |
| `operator_step_attempt_activity_stall_timeout_ms` | 10,000-1,800,000 | 30,000 | No-activity stall timeout |
| `attempt_stale_heartbeat_timeout_ms` | 30,000-600,000 | 120,000 | Stale heartbeat reap timeout |
| `heartbeat_emission_interval_ms` | 5,000-1,800,000 | governed | Heartbeat emission interval |
| `materialize_timeout_ms` | 5,000-1,800,000 | 240,000 | Container allocation + file write timeout |
| `file_overwrite_policy` | archive/timestamp_new/overwrite/reject | governed | How existing output files are handled |

---

### Routing Hints

Routing hints override the tenant's default execution routing mode, controlling which execution backend is preferred.

```json
{
  "routing_hints": {
    "execution_routing_mode": "sandbox_first"
  }
}
```

| Mode | Behavior |
|------|----------|
| `auto` | Platform selects backend based on step requirements |
| `sandbox_first` | Prefer sandbox.session backend for all steps that support it |
| `tool_loop_first` | Prefer tool_loop backend (simpler, faster, no container) |

---

### Planning Guidance

Planning guidance provides additional context to the planner through prompt templates and skill documentation.

```json
{
  "planning_guidance": {
    "discovery_seed_mode": "planning_assets_plus_profile_skills",
    "assets": [
      {
        "asset_type": "prompt_template",
        "ref": "workspace.operator.planner.financial_analysis_guidance",
        "scope": "pass_a",
        "required": true,
        "order": 1
      },
      {
        "asset_type": "skill_md",
        "ref": "skill.sandbox.data_analysis_toolkit",
        "scope": "all",
        "required": false,
        "order": 2
      }
    ]
  }
}
```

| Discovery Seed Mode | Behavior |
|--------------------|----------|
| `none` | No additional context. Planner uses only its system prompt. |
| `profile_skills_only` | Inject pinned skill documentation into planner context. |
| `planning_assets_plus_profile_skills` | Inject both planning guidance assets and pinned skill documentation. |

Assets can be scoped to specific planner phases (`pass_a`, `pass_b`, `pass_c`, `repair`) or `all` phases.

---

### Intent Normalizer

An optional preflight consumer that normalizes user intent before planning begins. This is a separate consumer from the planner -- it runs before the planning pipeline.

```json
{
  "intent_normalizer": {
    "consumer_key": "intent_normalizer",
    "prompt_binding_ref": "workspace.operator.intent_normalizer.system",
    "model_binding_ref": "anthropic:claude-haiku-4-5",
    "runtime_overrides": {
      "temperature": 0.0,
      "max_tokens": 2048,
      "timeout_ms": 8000
    }
  }
}
```

---

## Versioning and Publishing

Execution profiles use an immutable versioning model. Manifests are never edited in place -- each change creates a new version.

### Lifecycle

```
CREATE profile (v1 draft)
    │
    ├── PUBLISH v1 → profile becomes 'active', v1 becomes 'published'
    │       │
    │       ├── CREATE v2 (draft) ← edits to the manifest
    │       │       │
    │       │       └── PUBLISH v2 → v1 becomes 'deprecated', v2 becomes 'published'
    │       │               │
    │       │               └── All bindings auto-advance to v2
    │       │
    │       └── Profile still serves v1 to all runs until v2 publishes
    │
    └── ARCHIVE profile → soft delete, bindings must be cleared first
```

| Profile Status | Meaning |
|---------------|---------|
| `draft` | Profile created but no version published yet. Cannot be bound. |
| `active` | At least one version published. Available for binding and runs. |
| `archived` | Soft-deleted. Cannot be bound. Existing snapshots remain for audit. |

| Version Status | Meaning |
|---------------|---------|
| `draft` | Version created but not yet published. Can be edited. |
| `published` | Active version. Only one published version per profile at any time. |
| `deprecated` | Previously published version. Replaced by a newer published version. |

Each version includes a `manifest_hash` (SHA-256 of the canonical manifest) for integrity verification and diff detection. A `parent_version_id` tracks the version chain for audit trails.

---

## Binding System

Bindings connect profiles to organizational scopes -- making a profile the default for a tenant or a specific workspace.

### Scope Types

| Scope | Uniqueness Constraint | Purpose |
|-------|----------------------|---------|
| `tenant_default` | One per family per tenant | Organization-wide default for all workspaces |
| `workspace_default` | One per family per workspace per tenant | Workspace-specific override of the tenant default |

### Binding Strategies

A binding can reference a profile in two ways:

**Follow Latest (by `profile_id`):** The binding resolves to whatever version is currently published. When a new version is published, all bindings following that profile automatically advance. No manual rebinding required.

```json
{ "profile_id": "prof_abc123", "profile_version_id": null }
```

**Pin Specific Version (by `profile_version_id`):** The binding is locked to an exact version. Publishing a new version does not affect this binding. Used when stability is more important than staying current.

```json
{ "profile_id": null, "profile_version_id": "pv_def456" }
```

When both `profile_id` and `profile_version_id` are provided, `profile_id` takes precedence (follow-latest strategy).

### Automatic Binding Advancement

When a new version is published on a profile, the system automatically advances all bindings that reference that profile to the new version. This is the key mechanism that makes "follow latest" work: publish once, all bound workspaces pick up the change immediately.

---

## Resolution Cascade

When a run starts, the platform resolves which execution profile to use through a six-tier precedence chain. The first tier that produces a match wins.

```
TIER 1: Explicit version ID
  └─ Run requests a specific profile_version_id
       └─ Returns immediately if found and family matches

TIER 2: Explicit profile ID
  └─ Run requests a specific profile_id
       └─ Resolves to the profile's current published version

TIER 3: Workspace default binding
  └─ Workspace has a binding for this family
       └─ Follows the binding's strategy (follow-latest or pin-specific)

TIER 4: Tenant default binding
  └─ Tenant has a binding for this family
       └─ Follows the binding's strategy (follow-latest or pin-specific)

TIER 5: System fallback
  └─ Platform-wide system profile: '{family}.default' (e.g., operator.default)
       └─ Owned by system tenant (__platform__), shared across all tenants

TIER 6: No profile resolved
  └─ Run proceeds with governed settings only (no profile overrides)
```

The resolution produces a full audit trace recording which tier was attempted, whether it hit or missed, and why. This trace is persisted with the run snapshot for debugging.

### Drift Detection

When a run provides an `expected_profile_version_id`, the resolver compares it against the actually resolved version. If they differ, a drift is recorded -- indicating the profile was updated between when the user configured the run and when it actually executed. This is surfaced in diagnostics for troubleshooting "it worked yesterday" scenarios.

---

## Runtime Snapshot Freezing

At run start, the resolved profile is **frozen into an immutable snapshot**. The snapshot captures the complete effective state:

| Snapshot Field | Content |
|---------------|---------|
| `effective_manifest_json` | Full manifest at time of resolution |
| `effective_prompt_bindings_json` | Resolved prompt references for all consumers |
| `effective_runtime_json` | Resolved model selections and parameter overrides |
| `effective_validation_json` | Frozen validation pack resources (synonyms, schemas, rules, formulas) |
| `effective_skill_policy_json` | Skill pinning/denial policy |
| `effective_tool_policy_json` | Tool allowlist policy |
| `effective_sandbox_policy_json` | Sandbox configuration |
| `resolution_trace_json` | Audit trail of tier-by-tier resolution |
| `validation_resolution_trace_json` | Audit trail of validation pack resolution |

The snapshot is persisted to Neon Postgres and is uniquely constrained per `run_id` -- a run can only be frozen once. After freezing, all subsequent executor decisions read from the snapshot, not from the live profile. This guarantees that publishing a new profile version mid-run cannot affect an in-progress execution.

---

## Complete Override Priority Reference

For any given model call during execution, parameters are resolved through this complete priority chain:

```
                              ┌──────────────────────────────────────┐
                              │ EXECUTION PROFILE                    │ ← Highest priority
                              │ consumer binding runtime_overrides   │
                              └──────────────┬───────────────────────┘
                                             │ overrides
                              ┌──────────────┴───────────────────────┐
                              │ WORKSPACE OVERRIDES                  │
                              │ consumer-specific + consumer_defaults │
                              └──────────────┬───────────────────────┘
                                             │ overrides
                              ┌──────────────┴───────────────────────┐
                              │ GOVERNED SETTINGS                    │
                              │ ai.consumers.{key} + consumer_defaults│
                              └──────────────┬───────────────────────┘
                                             │ overrides
                              ┌──────────────┴───────────────────────┐
                              │ CONSUMER BUILT-IN DEFAULTS           │ ← Lowest priority
                              │ Hardcoded per consumer type          │
                              └──────────────────────────────────────┘
```

For model selection specifically:

```
1. Profile consumer binding model_binding_ref     ← WINS if set
2. Governed settings: ai.consumers.{key}.model_alias
3. Governed settings: ai.utility_model
4. Literal 'utility_model' (ProviderMux resolves)
```

For step-level timeouts, the execution contract's `timeout_ceiling_ms` can further constrain the resolved timeout (capped at 30 minutes absolute maximum).

---

## Enterprise Configuration Examples

### Example 1: Cost-Optimized Batch Processing

Use a fast, cheap model for all phases. No extended thinking. Strict validation.

```json
{
  "schema_version": "execution_profile.manifest.v1",
  "identity": {
    "family": "operator",
    "profile_key": "batch-cost-optimized",
    "display_name": "Cost-Optimized Batch Processing"
  },
  "planner": {
    "consumer_key": "operator_planner",
    "prompt_binding_ref": "workspace.operator.planner.system",
    "model_binding_ref": "anthropic:claude-sonnet-4-6",
    "runtime_overrides": { "temperature": 0.3, "max_tokens": 4096, "timeout_ms": 30000 }
  },
  "executor_by_backend": {
    "sandbox.session": {
      "consumer_key": "operator_step_executor",
      "prompt_binding_ref": "workspace.operator.step_executor.system",
      "model_binding_ref": "anthropic:claude-sonnet-4-6",
      "runtime_overrides": { "temperature": 0.1, "max_tokens": 4096 }
    }
  },
  "validation": {
    "schema_version": "execution_profile.validation.v1",
    "ceiling_policy_ref": "valpack.operator.ceiling@v1",
    "phases": {
      "step_output": { "default_pack_ref": "valpack.operator.generic.step-output@v1", "mode": "block" },
      "final_output": { "pack_ref": "valpack.operator.generic.final@v1", "mode": "block" }
    },
    "allowed_overrides": []
  },
  "budgets": { "max_steps": 10 }
}
```

### Example 2: High-Reasoning Financial Analysis

Opus for planning and execution with extended thinking enabled. Sonnet for mechanical resolution phases. Generous budgets.

```json
{
  "schema_version": "execution_profile.manifest.v1",
  "identity": {
    "family": "operator",
    "profile_key": "financial-analysis-premium",
    "display_name": "Financial Analysis (Premium)"
  },
  "planner": {
    "consumer_key": "operator_planner",
    "prompt_binding_ref": "workspace.operator.planner.system",
    "model_binding_ref": "anthropic:claude-opus-4-6",
    "runtime_overrides": {
      "temperature": 0.5,
      "max_tokens": 8192,
      "use_extended_thinking": true,
      "thinking_budget_tokens": 8192,
      "timeout_ms": 120000
    }
  },
  "planner_phase_bindings": {
    "pass_b": {
      "consumer_key": "operator_intent_resolver",
      "prompt_binding_ref": "workspace.operator.intent_resolver.system",
      "model_binding_ref": "anthropic:claude-sonnet-4-6",
      "runtime_overrides": { "temperature": 0.2, "max_tokens": 4096 }
    },
    "pass_c": {
      "consumer_key": "operator_skill_resolver",
      "prompt_binding_ref": "workspace.operator.skill_resolver.system",
      "model_binding_ref": "anthropic:claude-sonnet-4-6",
      "runtime_overrides": { "temperature": 0.2, "max_tokens": 4096 }
    }
  },
  "executor_by_backend": {
    "sandbox.session": {
      "consumer_key": "operator_step_executor",
      "prompt_binding_ref": "workspace.operator.step_executor.system",
      "model_binding_ref": "anthropic:claude-opus-4-6",
      "runtime_overrides": {
        "temperature": 0.1,
        "max_tokens": 8192,
        "use_extended_thinking": true,
        "thinking_budget_tokens": 4096
      }
    }
  },
  "validation": {
    "schema_version": "execution_profile.validation.v1",
    "ceiling_policy_ref": "valpack.operator.ceiling@v1",
    "phases": {
      "step_output": {
        "default_pack_ref": "valpack.operator.generic.step-output@v1",
        "matchers": [
          { "artifact_path": "*.json", "pack_ref": "valpack.operator.json-schema@v1" }
        ],
        "mode": "block"
      },
      "final_output": { "pack_ref": "valpack.operator.generic.final@v1", "mode": "block" }
    },
    "allowed_overrides": []
  },
  "skill_policy": {
    "pinned_skills": [
      { "skill_id": "data-analysis-toolkit", "priority": "required", "scope": "both" }
    ],
    "denied_skills": ["general-web-research"],
    "autoload_mode": "profile_plus_discovery"
  },
  "budgets": {
    "max_steps": 50,
    "sandbox_session_dispatch_timeout_ms": 900000,
    "window_size": 8
  }
}
```

### Example 3: Development/Debug Profile

Relaxed validation, verbose output, lower budgets for fast iteration.

```json
{
  "schema_version": "execution_profile.manifest.v1",
  "identity": {
    "family": "operator",
    "profile_key": "development-debug",
    "display_name": "Development & Debug"
  },
  "planner": {
    "consumer_key": "operator_planner",
    "prompt_binding_ref": "workspace.operator.planner.system",
    "model_binding_ref": "anthropic:claude-sonnet-4-6",
    "runtime_overrides": { "temperature": 0.5, "max_tokens": 4096 }
  },
  "executor_by_backend": {
    "sandbox.session": {
      "consumer_key": "operator_step_executor",
      "prompt_binding_ref": "workspace.operator.step_executor.system",
      "model_binding_ref": "anthropic:claude-sonnet-4-6",
      "runtime_overrides": { "temperature": 0.1, "max_tokens": 4096 }
    }
  },
  "validation": {
    "schema_version": "execution_profile.validation.v1",
    "ceiling_policy_ref": "valpack.operator.ceiling@v1",
    "phases": {
      "planner_candidate": { "pack_ref": "valpack.operator.generic.planner@v1", "mode": "report" },
      "step_output": { "default_pack_ref": "valpack.operator.generic.step-output@v1", "mode": "report" },
      "final_output": { "pack_ref": "valpack.operator.generic.final@v1", "mode": "off" }
    },
    "allowed_overrides": ["step_output.mode", "final_output.mode"]
  },
  "budgets": { "max_steps": 5 }
}
```

---

## API Surface

All endpoints require admin role. Tenant-scoped via URL path.

**Base Path**: `/_mcp/{tenant}/v1/admin/workspaces/{workspace_id}`

### Profile CRUD

| Method | Path | Description |
|--------|------|-------------|
| GET | `/execution-profiles` | List profiles (supports `family`, `q` search, `include_archived`, `include_versions`, pagination) |
| POST | `/execution-profiles` | Create profile with initial version (optionally auto-publish) |
| GET | `/execution-profiles/{profile_id}` | Get profile with optional versions and bindings |
| POST | `/execution-profiles/{profile_id}/versions` | Create new version (optionally auto-publish) |
| POST | `/execution-profiles/{profile_id}/publish` | Publish a draft version (deprecates previous, auto-advances bindings) |
| POST | `/execution-profiles/{profile_id}/archive` | Archive profile (fails if any bindings reference it) |

### Binding Management

| Method | Path | Description |
|--------|------|-------------|
| GET | `/execution-profile-bindings` | List bindings (optionally filter by `family`) |
| POST | `/execution-profile-bindings` | Set tenant or workspace default binding |
| DELETE | `/execution-profile-bindings/{binding_id}` | Remove a binding |

### Capabilities

The API returns role-based capabilities with list responses:

| Capability | Requires | Allows |
|-----------|----------|--------|
| `viewer` | Any authenticated user | Read profiles and bindings |
| `editor` | Any authenticated user | Create and edit draft versions |
| `publisher` | Admin role | Publish versions |
| `binding_admin` | Admin role | Set and clear bindings |

---

## Database Schema

Profiles are stored in three Neon Postgres tables:

### `execution_profiles`

| Column | Type | Description |
|--------|------|-------------|
| `profile_id` | TEXT PK | `prof_` + 16-char hex (`prof_abc123def456`) |
| `tenant_id` | TEXT | Owning tenant |
| `scope` | TEXT | `'system'` or `'tenant'` |
| `family` | TEXT | `'operator'`, `'builder'`, or `'research'` |
| `profile_key` | TEXT | Unique key within family (`high-reasoning-analyst`) |
| `display_name` | TEXT | Human-readable name |
| `description` | TEXT | Optional description |
| `status` | TEXT | `'draft'`, `'active'`, or `'archived'` |
| `published_version_id` | TEXT | FK to current published version |
| `created_by` | TEXT | Actor user ID |
| `created_at` / `updated_at` | BIGINT | Unix timestamps |

Unique constraint: `(tenant_id, family, profile_key)` -- one profile per key per family per tenant.

### `execution_profile_versions`

| Column | Type | Description |
|--------|------|-------------|
| `profile_version_id` | TEXT PK | `pv_` + 16-char hex (`pv_def456ghi789`) |
| `profile_id` | TEXT FK | Parent profile |
| `tenant_id` | TEXT | Owning tenant |
| `version_number` | INTEGER | Sequential per profile (1, 2, 3...) |
| `status` | TEXT | `'draft'`, `'published'`, or `'deprecated'` |
| `manifest_json` | JSONB | Complete manifest (`ManifestJson`) |
| `schema_version` | TEXT | Always `'execution_profile.manifest.v1'` |
| `manifest_hash` | TEXT | SHA-256 for integrity/diff detection |
| `parent_version_id` | TEXT | Previous version in chain |
| `published_at` / `deprecated_at` | BIGINT | Lifecycle timestamps |
| `created_by` | TEXT | Actor user ID |
| `created_at` / `updated_at` | BIGINT | Unix timestamps |

Unique constraint: `(profile_id, version_number)` -- sequential version numbering.

### `execution_profile_bindings`

| Column | Type | Description |
|--------|------|-------------|
| `binding_id` | TEXT PK | `bind_` + 16-char hex |
| `tenant_id` | TEXT | Owning tenant |
| `scope_type` | TEXT | `'tenant_default'` or `'workspace_default'` |
| `workspace_id` | TEXT | NULL for tenant-level bindings |
| `family` | TEXT | Profile family |
| `profile_id` | TEXT | FK (follow-latest strategy) |
| `profile_version_id` | TEXT | FK (pin-specific strategy) |
| `priority` | INTEGER | Reserved for future multi-binding support |
| `created_by` | TEXT | Actor user ID |
| `created_at` / `updated_at` | BIGINT | Unix timestamps |

Partial unique indexes enforce one binding per family per scope:
- `(tenant_id, family) WHERE scope_type = 'tenant_default'`
- `(tenant_id, workspace_id, family) WHERE scope_type = 'workspace_default'`

---

## Profile Scoping

| Scope | Owner | Visibility | Purpose |
|-------|-------|-----------|---------|
| `system` | Platform (`__platform__` tenant) | All tenants | Platform-wide defaults (e.g., `operator.default`) |
| `tenant` | Individual tenant | Tenant only | Tenant-specific profiles for their workspaces |

System profiles provide the tier-5 fallback in the resolution cascade. They ensure every run has a profile even if the tenant has not configured any. Tenants cannot modify system profiles -- they can only override them via bindings.

---

## Source Files

| File | Purpose |
|------|---------|
| `___new_mcp_server/src/services/execution-profiles/types.ts` | Type contracts: ManifestJson, consumer bindings, validation, skill policy |
| `___new_mcp_server/src/services/execution-profiles/ExecutionProfileResolverService.ts` | 6-tier resolution cascade, snapshot freezing, binding resolution |
| `___new_mcp_server/src/services/execution-profiles/ExecutionProfilesRepositoryPg.ts` | CRUD, versioning, publishing, binding operations (Neon Postgres) |
| `___new_mcp_server/src/services/execution-profiles/ExecutionProfileManifestCanonicalizer.ts` | Manifest normalization (legacy → canonical executor bindings) |
| `___new_mcp_server/src/services/execution-profiles/manifest-validator.ts` | Manifest structure and content validation |
| `___new_mcp_server/src/services/ai/ConsumerRuntimeConfigResolver.ts` | Consumer parameter resolution (built-in → governed → profile cascade) |
| `___new_mcp_server/src/policy/GovernedSettings.ts` | Multi-layer governed settings (global → tier → tenant cascade) |
| `___new_mcp_server/src/cloudflare/handlers/admin/execution-profiles.ts` | API handlers for profile CRUD and binding management |
| `___new_mcp_server/src/cloudflare/infra/execution-profiles-pg-schema.ts` | Postgres DDL for all three tables |
| `___new_mcp_server/src/services/uab/OperatorStepExecutorService.ts` | Executor: reads snapshot bindings, resolves model, applies overrides |
| `___new_mcp_server/src/services/prompts/PromptBindingResolver.ts` | Prompt reference resolution (bare ID, pinned version, row ID) |

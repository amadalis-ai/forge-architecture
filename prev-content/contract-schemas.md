Blow is the **concrete schema set** I would recommend you adopt first. These schemas are designed to implement exactly what your board brief is asking for: make contracts explicit at planning time, resolve them concretely at compile time, and prevent downstream executors from inferring structure from filenames or paths. That directly addresses the failure mode your brief described. 

I’m giving you **three schemas**:

1. **Planner Abstract Step Contract**
2. **Compiler Compiled Step Contract**
3. **Minimal Operator Input Envelope** (backward-compatible with your current `work_item.payload` pattern)

---

# 1) Planner Abstract Step Contract v1

## Purpose

This is what the **planner** emits.

It should be:

* **abstract**
* **semantic**
* **pack-aware**
* **slot-based**

It should **not** bind concrete artifact IDs or silently assume a specific file shape.

## JSON Schema

```json
{
  "$id": "https://optim.ai/schemas/planner-abstract-step-contract.v1.json",
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "PlannerAbstractStepContractV1",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "step_id",
    "role",
    "purpose",
    "inputs",
    "outputs"
  ],
  "properties": {
    "step_id": {
      "type": "string",
      "pattern": "^[a-zA-Z0-9._:-]{1,128}$"
    },
    "role": {
      "type": "string",
      "minLength": 1,
      "maxLength": 120
    },
    "purpose": {
      "type": "string",
      "minLength": 1,
      "maxLength": 2000
    },
    "domain_pack_ids": {
      "type": "array",
      "items": {
        "type": "string",
        "pattern": "^[a-z0-9]+(?:-[a-z0-9]+)*$"
      },
      "default": []
    },
    "workflow_pack_ids": {
      "type": "array",
      "items": {
        "type": "string",
        "pattern": "^[a-z0-9]+(?:-[a-z0-9]+)*$"
      },
      "default": []
    },
    "policy_profile_id": {
      "type": ["string", "null"],
      "pattern": "^[a-z0-9][a-z0-9._-]{2,127}$"
    },
    "dependencies": {
      "type": "array",
      "items": {
        "type": "string",
        "pattern": "^[a-zA-Z0-9._:-]{1,128}$"
      },
      "default": []
    },
    "inputs": {
      "type": "array",
      "items": { "$ref": "#/$defs/abstractInputSlot" },
      "default": []
    },
    "outputs": {
      "type": "array",
      "minItems": 1,
      "items": { "$ref": "#/$defs/abstractOutputSlot" }
    },
    "execution_hints": {
      "$ref": "#/$defs/executionHints"
    }
  },
  "$defs": {
    "grainSpec": {
      "type": "object",
      "additionalProperties": false,
      "required": ["grain_type"],
      "properties": {
        "grain_type": {
          "type": "string",
          "enum": [
            "record",
            "row",
            "document",
            "page",
            "clause",
            "line_item",
            "time_entry",
            "ledger_entry",
            "day",
            "week",
            "month",
            "batch",
            "bundle",
            "file",
            "custom"
          ]
        },
        "custom_label": {
          "type": ["string", "null"],
          "maxLength": 120
        },
        "cardinality": {
          "type": "string",
          "enum": ["one", "many"],
          "default": "many"
        },
        "notes": {
          "type": ["string", "null"],
          "maxLength": 500
        }
      }
    },
    "abstractInputSlot": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "slot",
        "required",
        "entity_schema_id"
      ],
      "properties": {
        "slot": {
          "type": "string",
          "pattern": "^[a-z][a-z0-9_]{0,63}$"
        },
        "required": {
          "type": "boolean"
        },
        "entity_schema_id": {
          "type": "string",
          "pattern": "^[a-z0-9]+(?:\\.[a-z0-9_]+)+$"
        },
        "accepted_kind_keys": {
          "type": "array",
          "items": {
            "type": "string",
            "pattern": "^[a-z0-9]+(?:\\.[a-z0-9_]+)+$"
          },
          "default": []
        },
        "preferred_profile_ids": {
          "type": "array",
          "items": {
            "type": "string",
            "pattern": "^[a-z0-9][a-z0-9._-]{2,127}$"
          },
          "default": []
        },
        "row_grain": {
          "oneOf": [
            { "$ref": "#/$defs/grainSpec" },
            { "type": "null" }
          ]
        },
        "provenance_policy": {
          "type": "string",
          "enum": ["none", "preferred", "required"],
          "default": "preferred"
        },
        "notes": {
          "type": ["string", "null"],
          "maxLength": 500
        }
      }
    },
    "abstractOutputSlot": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "slot",
        "entity_schema_id"
      ],
      "properties": {
        "slot": {
          "type": "string",
          "pattern": "^[a-z][a-z0-9_]{0,63}$"
        },
        "entity_schema_id": {
          "type": "string",
          "pattern": "^[a-z0-9]+(?:\\.[a-z0-9_]+)+$"
        },
        "preferred_kind_keys": {
          "type": "array",
          "items": {
            "type": "string",
            "pattern": "^[a-z0-9]+(?:\\.[a-z0-9_]+)+$"
          },
          "default": []
        },
        "preferred_profile_ids": {
          "type": "array",
          "items": {
            "type": "string",
            "pattern": "^[a-z0-9][a-z0-9._-]{2,127}$"
          },
          "default": []
        },
        "row_grain": {
          "oneOf": [
            { "$ref": "#/$defs/grainSpec" },
            { "type": "null" }
          ]
        },
        "provenance_policy": {
          "type": "string",
          "enum": ["none", "preferred", "required"],
          "default": "preferred"
        },
        "path_hint": {
          "type": ["string", "null"],
          "maxLength": 512
        },
        "notes": {
          "type": ["string", "null"],
          "maxLength": 500
        }
      }
    },
    "executionHints": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "preferred_mode": {
          "type": "string",
          "enum": ["assist", "operator", "orchestrator"]
        },
        "allow_adapter_insertion_hint": {
          "type": "boolean",
          "default": true
        },
        "requires_artifact_output": {
          "type": "boolean",
          "default": false
        },
        "notes": {
          "type": ["string", "null"],
          "maxLength": 500
        }
      }
    }
  }
}
```

---

# 2) Compiler Compiled Step Contract v1

## Purpose

This is what the **compiler** emits after resolving:

* profile IDs
* actual bound inputs
* adapters/normalizers
* concrete output profile

This is the object the runtime should treat as authoritative.

## JSON Schema

```json
{
  "$id": "https://optim.ai/schemas/compiler-compiled-step-contract.v1.json",
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "CompilerCompiledStepContractV1",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "step_id",
    "role",
    "purpose",
    "inputs",
    "outputs"
  ],
  "properties": {
    "step_id": {
      "type": "string",
      "pattern": "^[a-zA-Z0-9._:-]{1,128}$"
    },
    "role": {
      "type": "string",
      "minLength": 1,
      "maxLength": 120
    },
    "purpose": {
      "type": "string",
      "minLength": 1,
      "maxLength": 2000
    },
    "domain_pack_ids": {
      "type": "array",
      "items": {
        "type": "string",
        "pattern": "^[a-z0-9]+(?:-[a-z0-9]+)*$"
      },
      "default": []
    },
    "workflow_pack_ids": {
      "type": "array",
      "items": {
        "type": "string",
        "pattern": "^[a-z0-9]+(?:-[a-z0-9]+)*$"
      },
      "default": []
    },
    "policy_profile_id": {
      "type": ["string", "null"],
      "pattern": "^[a-z0-9][a-z0-9._-]{2,127}$"
    },
    "dependencies": {
      "type": "array",
      "items": {
        "type": "string",
        "pattern": "^[a-zA-Z0-9._:-]{1,128}$"
      },
      "default": []
    },
    "compiler_decisions": {
      "$ref": "#/$defs/compilerDecisions"
    },
    "inputs": {
      "type": "array",
      "items": { "$ref": "#/$defs/compiledInputSlot" },
      "default": []
    },
    "outputs": {
      "type": "array",
      "minItems": 1,
      "items": { "$ref": "#/$defs/compiledOutputSlot" }
    }
  },
  "$defs": {
    "grainSpec": {
      "type": "object",
      "additionalProperties": false,
      "required": ["grain_type"],
      "properties": {
        "grain_type": {
          "type": "string",
          "enum": [
            "record",
            "row",
            "document",
            "page",
            "clause",
            "line_item",
            "time_entry",
            "ledger_entry",
            "day",
            "week",
            "month",
            "batch",
            "bundle",
            "file",
            "custom"
          ]
        },
        "custom_label": {
          "type": ["string", "null"],
          "maxLength": 120
        },
        "cardinality": {
          "type": "string",
          "enum": ["one", "many"],
          "default": "many"
        },
        "notes": {
          "type": ["string", "null"],
          "maxLength": 500
        }
      }
    },
    "artifactBinding": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "artifact_id",
        "profile_id",
        "kind_key",
        "entity_schema_id"
      ],
      "properties": {
        "artifact_id": {
          "type": "string",
          "pattern": "^[a-zA-Z0-9._:-]{1,128}$"
        },
        "profile_id": {
          "type": "string",
          "pattern": "^[a-z0-9][a-z0-9._-]{2,127}$"
        },
        "kind_key": {
          "type": "string",
          "pattern": "^[a-z0-9]+(?:\\.[a-z0-9_]+)+$"
        },
        "entity_schema_id": {
          "type": "string",
          "pattern": "^[a-z0-9]+(?:\\.[a-z0-9_]+)+$"
        },
        "row_grain": {
          "oneOf": [
            { "$ref": "#/$defs/grainSpec" },
            { "type": "null" }
          ]
        },
        "path": {
          "type": ["string", "null"],
          "maxLength": 1024
        },
        "sha256": {
          "type": ["string", "null"],
          "pattern": "^[A-Fa-f0-9]{64}$"
        },
        "row_count": {
          "type": ["integer", "null"],
          "minimum": 0
        },
        "source_step_id": {
          "type": ["string", "null"],
          "pattern": "^[a-zA-Z0-9._:-]{1,128}$"
        },
        "source_slot": {
          "type": ["string", "null"],
          "pattern": "^[a-z][a-z0-9_]{0,63}$"
        },
        "source_artifact_ids": {
          "type": "array",
          "items": {
            "type": "string",
            "pattern": "^[a-zA-Z0-9._:-]{1,128}$"
          },
          "default": []
        }
      }
    },
    "compiledInputSlot": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "slot",
        "required",
        "entity_schema_id",
        "resolved_profile_id",
        "resolved_kind_key",
        "bindings"
      ],
      "properties": {
        "slot": {
          "type": "string",
          "pattern": "^[a-z][a-z0-9_]{0,63}$"
        },
        "required": {
          "type": "boolean"
        },
        "entity_schema_id": {
          "type": "string",
          "pattern": "^[a-z0-9]+(?:\\.[a-z0-9_]+)+$"
        },
        "resolved_profile_id": {
          "type": "string",
          "pattern": "^[a-z0-9][a-z0-9._-]{2,127}$"
        },
        "resolved_kind_key": {
          "type": "string",
          "pattern": "^[a-z0-9]+(?:\\.[a-z0-9_]+)+$"
        },
        "row_grain": {
          "oneOf": [
            { "$ref": "#/$defs/grainSpec" },
            { "type": "null" }
          ]
        },
        "adapter_chain": {
          "type": "array",
          "items": {
            "type": "string",
            "pattern": "^[a-z0-9][a-z0-9._-]{2,127}$"
          },
          "default": []
        },
        "bindings": {
          "type": "array",
          "minItems": 1,
          "items": { "$ref": "#/$defs/artifactBinding" }
        },
        "provenance_requirements": {
          "$ref": "#/$defs/provenanceRequirements"
        }
      }
    },
    "compiledOutputSlot": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "slot",
        "entity_schema_id",
        "profile_id",
        "kind_key"
      ],
      "properties": {
        "slot": {
          "type": "string",
          "pattern": "^[a-z][a-z0-9_]{0,63}$"
        },
        "entity_schema_id": {
          "type": "string",
          "pattern": "^[a-z0-9]+(?:\\.[a-z0-9_]+)+$"
        },
        "profile_id": {
          "type": "string",
          "pattern": "^[a-z0-9][a-z0-9._-]{2,127}$"
        },
        "kind_key": {
          "type": "string",
          "pattern": "^[a-z0-9]+(?:\\.[a-z0-9_]+)+$"
        },
        "row_grain": {
          "oneOf": [
            { "$ref": "#/$defs/grainSpec" },
            { "type": "null" }
          ]
        },
        "path_hint": {
          "type": ["string", "null"],
          "maxLength": 1024
        },
        "artifact_role": {
          "type": "string",
          "enum": ["primary", "auxiliary"],
          "default": "primary"
        },
        "required_validations": {
          "type": "array",
          "items": {
            "type": "string",
            "enum": [
              "shape",
              "required_fields",
              "row_grain",
              "primary_keys",
              "provenance"
            ]
          },
          "default": ["shape", "required_fields"]
        },
        "provenance_requirements": {
          "$ref": "#/$defs/provenanceRequirements"
        }
      }
    },
    "provenanceRequirements": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "require_source_artifact_ids": {
          "type": "boolean",
          "default": false
        },
        "require_citation_ids": {
          "type": "boolean",
          "default": false
        },
        "require_evidence_card_ids": {
          "type": "boolean",
          "default": false
        }
      }
    },
    "compilerDecisions": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "resolution_mode": {
          "type": "string",
          "enum": ["exact_match", "adapter_inserted", "generic_fallback", "manual_override"]
        },
        "compatibility_status": {
          "type": "string",
          "enum": ["compatible", "adapter_required", "incompatible"]
        },
        "warnings": {
          "type": "array",
          "items": { "type": "string", "maxLength": 500 },
          "default": []
        }
      }
    }
  }
}
```

---

# 3) Minimal Operator Input Envelope v1

## Purpose

This is the **runtime-delivered execution envelope** for the operator/worker.

This version is deliberately **backward-compatible** with your current model:

* keep `workspace_id`, `ledger_id`, `run_id`, `goal_text`, `rolling_digest`, `runtime_policy`
* keep `work_item.kind`, `work_item.dedupe_key`, `work_item.payload`
* add `compiled_contract` under `work_item.payload`

That way the operator prompt only needs a **small contract-aware delta**, not a full redesign.

## JSON Schema

```json
{
  "$id": "https://optim.ai/schemas/operator-step-input-envelope.v1.json",
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "OperatorStepInputEnvelopeV1",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "workspace_id",
    "ledger_id",
    "run_id",
    "runtime_policy",
    "work_item"
  ],
  "properties": {
    "workspace_id": {
      "type": "string",
      "minLength": 1,
      "maxLength": 128
    },
    "ledger_id": {
      "type": "string",
      "minLength": 1,
      "maxLength": 128
    },
    "run_id": {
      "type": "string",
      "minLength": 1,
      "maxLength": 128
    },
    "goal_text": {
      "type": ["string", "null"],
      "maxLength": 20000
    },
    "rolling_digest": {
      "type": ["string", "null"],
      "maxLength": 50000
    },
    "runtime_policy": {
      "type": "object"
    },
    "work_item": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "kind",
        "dedupe_key",
        "payload"
      ],
      "properties": {
        "kind": {
          "type": "string",
          "pattern": "^[a-z0-9]+(?:\\.[a-z0-9_]+)+$"
        },
        "dedupe_key": {
          "type": "string",
          "minLength": 1,
          "maxLength": 256
        },
        "payload": {
          "type": "object",
          "additionalProperties": false,
          "required": [
            "compiled_contract"
          ],
          "properties": {
            "deliverable": {
              "type": ["string", "null"],
              "maxLength": 2000
            },
            "constraints": {
              "type": ["object", "null"]
            },
            "compiled_contract": {
              "$ref": "https://optim.ai/schemas/compiler-compiled-step-contract.v1.json"
            }
          }
        }
      }
    }
  }
}
```

---

# 4) Runtime rules to attach to these schemas

These are just as important as the schemas themselves.

## Rule 1 — Planner emits abstract, compiler emits concrete

* planner schema must not contain concrete `artifact_id`s
* compiled schema must not contain unresolved `accepted_kind_keys`
* operator input envelope must only carry the **compiled** contract, never the unresolved abstract one

## Rule 2 — Runtime fails closed on mismatch

If actual input artifact metadata does not match `compiled_contract.inputs[*].resolved_profile_id`:

* stop
* report mismatch
* do not let operator infer around it

## Rule 3 — No filename/path inference

The executor must never treat:

* `schema_profile.json`
* `report.csv`
* `results.json`

as semantic truth.
Only `profile_id`, `kind_key`, `entity_schema_id`, and validated artifact manifest are authoritative. That is exactly the failure your brief is trying to eliminate. 

---

# 5) One compact end-to-end example (resume audit)

This example shows the difference between planner intent and compiled execution.

## Planner abstract step

```json
{
  "step_id": "score_candidates",
  "role": "ai_autonomous_worker",
  "purpose": "Score normalized candidate profiles against the job rubric",
  "domain_pack_ids": ["resume-audit"],
  "workflow_pack_ids": ["analyze-score-rank"],
  "inputs": [
    {
      "slot": "candidate_profiles",
      "required": true,
      "entity_schema_id": "resume.candidate_profile",
      "accepted_kind_keys": ["table.json_rows", "table.csv"],
      "preferred_profile_ids": ["resume.table.json_rows.candidate_profiles.v1"],
      "provenance_policy": "preferred"
    },
    {
      "slot": "job_rubric",
      "required": true,
      "entity_schema_id": "resume.job_rubric",
      "accepted_kind_keys": ["object.json", "file.text"],
      "preferred_profile_ids": ["resume.object.json.job_rubric.v1"],
      "provenance_policy": "none"
    }
  ],
  "outputs": [
    {
      "slot": "candidate_score_rows",
      "entity_schema_id": "resume.candidate_score_row",
      "preferred_kind_keys": ["table.json_rows"],
      "preferred_profile_ids": ["resume.table.json_rows.candidate_score_rows.v1"],
      "provenance_policy": "required",
      "path_hint": "artifacts/candidate_scores.json"
    }
  ]
}
```

## Compiler compiled step

```json
{
  "step_id": "score_candidates",
  "role": "ai_autonomous_worker",
  "purpose": "Score normalized candidate profiles against the job rubric",
  "domain_pack_ids": ["resume-audit"],
  "workflow_pack_ids": ["analyze-score-rank"],
  "policy_profile_id": "strict.allow-normalizers.v1",
  "compiler_decisions": {
    "resolution_mode": "exact_match",
    "compatibility_status": "compatible",
    "warnings": []
  },
  "inputs": [
    {
      "slot": "candidate_profiles",
      "required": true,
      "entity_schema_id": "resume.candidate_profile",
      "resolved_profile_id": "resume.table.json_rows.candidate_profiles.v1",
      "resolved_kind_key": "table.json_rows",
      "bindings": [
        {
          "artifact_id": "art_candidate_profiles",
          "profile_id": "resume.table.json_rows.candidate_profiles.v1",
          "kind_key": "table.json_rows",
          "entity_schema_id": "resume.candidate_profile",
          "path": "artifacts/candidate_profiles.json",
          "sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
          "row_count": 47,
          "source_step_id": "normalize_resumes",
          "source_slot": "candidate_profiles",
          "source_artifact_ids": ["art_resume_batch_manifest"]
        }
      ],
      "provenance_requirements": {
        "require_source_artifact_ids": true,
        "require_citation_ids": false,
        "require_evidence_card_ids": false
      }
    },
    {
      "slot": "job_rubric",
      "required": true,
      "entity_schema_id": "resume.job_rubric",
      "resolved_profile_id": "resume.object.json.job_rubric.v1",
      "resolved_kind_key": "object.json",
      "bindings": [
        {
          "artifact_id": "art_job_rubric",
          "profile_id": "resume.object.json.job_rubric.v1",
          "kind_key": "object.json",
          "entity_schema_id": "resume.job_rubric",
          "path": "inputs/job_rubric.json",
          "sha256": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
          "row_count": null,
          "source_step_id": null,
          "source_slot": null,
          "source_artifact_ids": []
        }
      ],
      "provenance_requirements": {
        "require_source_artifact_ids": false,
        "require_citation_ids": false,
        "require_evidence_card_ids": false
      }
    }
  ],
  "outputs": [
    {
      "slot": "candidate_score_rows",
      "entity_schema_id": "resume.candidate_score_row",
      "profile_id": "resume.table.json_rows.candidate_score_rows.v1",
      "kind_key": "table.json_rows",
      "path_hint": "artifacts/candidate_scores.json",
      "artifact_role": "primary",
      "required_validations": ["shape", "required_fields", "provenance"],
      "provenance_requirements": {
        "require_source_artifact_ids": true,
        "require_citation_ids": false,
        "require_evidence_card_ids": false
      }
    }
  ]
}
```

## Operator input envelope

```json
{
  "workspace_id": "ws_123",
  "ledger_id": "ledger_123",
  "run_id": "run_123",
  "goal_text": "Audit uploaded resumes against the role rubric and rank candidates",
  "rolling_digest": "Previous steps loaded the resume batch and normalized candidate profiles.",
  "runtime_policy": {
    "max_new_per_finding": 3
  },
  "work_item": {
    "kind": "resume.audit.score",
    "dedupe_key": "resume.audit.score:candidate_ranking",
    "payload": {
      "deliverable": "Score candidate profiles and produce ranked score rows",
      "constraints": {
        "must_include_fields": ["candidate_id", "total_score", "top_reasons"]
      },
      "compiled_contract": {
        "step_id": "score_candidates",
        "role": "ai_autonomous_worker",
        "purpose": "Score normalized candidate profiles against the job rubric",
        "domain_pack_ids": ["resume-audit"],
        "workflow_pack_ids": ["analyze-score-rank"],
        "policy_profile_id": "strict.allow-normalizers.v1",
        "compiler_decisions": {
          "resolution_mode": "exact_match",
          "compatibility_status": "compatible",
          "warnings": []
        },
        "inputs": [],
        "outputs": []
      }
    }
  }
}
```

---

# 6) What to change in the prompts

## Planner prompt

Yes — change it materially:

* add **contract-aware planning**
* emit **abstract I/O declarations**
* stop assuming filenames imply semantics

## Operator prompt

Only a **small delta**:

* “treat compiled contract as authoritative”
* “never infer structure from path/name”
* “fail closed on mismatch”

So the operator is **mostly transparent as usual**, but only after the runtime/compiler have done the hard contract resolution work. That is the right split. 


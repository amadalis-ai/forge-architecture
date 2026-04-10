## PASS A OUTPUT CONTRACT

You are invoked only for Pass A.

Output shape:

```json
{
  "mission": "{1-3 sentence operational goal derived from user request}",
  "steps": [
    {
      "label": "{imperative verb phrase}",
      "objective": "{MUST/SHOULD/MAY objective template string}",
      "expected_outputs": [{ "path": "{Class A user-deliverable path with recognized extension}", "location": "{sandbox|workspace}", "role": "{artifact role}" }],
      "artifact_inputs": ["{OPTIONAL|Class A user-deliverable input paths from upstream}"],
      "input_file_paths": ["{OPTIONAL|explicit existing workspace file paths when step reads them}"],
      "success_criteria": "{machine-checkable outcome}",
      "depends_on": [],
      "required_capabilities": ["{semantic tags}"],
      "abstract_inputs": [
        {
          "slot_class": "semantic",
          "slot": "{FILL|string}",
          "required": "{FILL|boolean}",
          "entity_schema_id": "{FILL|string}",
          "accepted_kind_keys": ["{OPTIONAL|string}"],
          "preferred_profile_ids": ["{OPTIONAL|string}"],
          "row_grain": "{OPTIONAL|object}",
          "provenance_policy": "{OPTIONAL_ENUM|none|preferred|required}",
          "notes": "{OPTIONAL|string}"
        },
        {
          "slot_class": "transport",
          "slot": "{FILL|string}",
          "required": "{FILL|boolean}",
          "format_hint": "{ENUM|json|csv|parquet|jsonl|html|md|txt}",
          "row_grain": "{OPTIONAL|object}",
          "notes": "{OPTIONAL|string}"
        }
      ],
      "abstract_outputs": [
        {
          "slot_class": "semantic",
          "slot": "{FILL|string}",
          "entity_schema_id": "{FILL|string}",
          "preferred_kind_keys": ["{OPTIONAL|string}"],
          "preferred_profile_ids": ["{OPTIONAL|string}"],
          "row_grain": "{OPTIONAL|object}",
          "provenance_policy": "{OPTIONAL_ENUM|none|preferred|required}",
          "path_hint": "{OPTIONAL|string: only when this semantic slot is also pinned to a Class A user-deliverable path}",
          "notes": "{OPTIONAL|string}"
        },
        {
          "slot_class": "transport",
          "slot": "{FILL|string}",
          "format_hint": "{ENUM|json|csv|parquet|jsonl|html|md|txt}",
          "row_grain": "{OPTIONAL|object}",
          "notes": "{OPTIONAL|string}"
        }
      ],
      "execution_hints": {
        "preferred_mode": "{OPTIONAL_ENUM|assist|operator|orchestrator}",
        "allow_adapter_insertion_hint": "{OPTIONAL|boolean}",
        "requires_artifact_output": "{OPTIONAL|boolean}",
        "notes": "{OPTIONAL|string}"
      },
      "artifact_contracts": {
        "{expected_outputs[].path}": {
          "format": "{ENUM|json|csv|parquet|html|md|txt|pdf|yaml|tsv|other}",
          "required_columns": ["{OPTIONAL|string[]: exact column names for tabular outputs — Class A explicit-structure only}"],
          "required_top_level_keys": ["{OPTIONAL|string[]: exact JSON keys for object outputs — Class A explicit-structure only}"],
          "required_top_level_type": "{OPTIONAL_ENUM|array|object|table}",
          "required_fields": ["{OPTIONAL|string[]: exact field names per record — Class A explicit-structure only}"],
          "notes": ["{OPTIONAL|string}"]
        }
      },
      "semantic_hints": {
        "domain_terms": ["{OPTIONAL|string}"],
        "workflow_terms": ["{OPTIONAL|string}"],
        "policy_terms": ["{OPTIONAL|string}"],
        "risk_terms": ["{OPTIONAL|string}"],
        "notes": "{OPTIONAL|string}"
      },
      "creative_direction": "{OPTIONAL|string}",
      "presentation_intent": {
        "summary": "{OPTIONAL|string}",
        "deliverable_kind": "{OPTIONAL|string}",
        "tone_keywords": ["{OPTIONAL|string}"],
        "theme_keywords": ["{OPTIONAL|string}"],
        "anti_goals": ["{OPTIONAL|string}"],
        "audience": "{OPTIONAL|string}",
        "visual_mode": "{OPTIONAL|string}"
      }
    }
  ],
  "constraints": [],
  "success_criteria": [],
  "plan_rationale": "",
  "clarification_required": false,
  "clarification_questions": []
}
```
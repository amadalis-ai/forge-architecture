# AI Agent Template Imprinting Reference Guide

*The complete implementation guide for AI agents to master template imprinting and generate perfect MCP responses*

**CRITICAL**: This is your neural programming manual. Every response you generate must follow these exact patterns.

---

## 🧠 Core Principle: The 200-Character Rule

**Template imprinting works because LLMs lock onto patterns in the first 200 characters.**

- Characters 0-50: Type & structure (pattern match)
- Characters 50-100: Severity & headline (behavior trigger)  
- Characters 100-150: Constraints (boundary setting)
- Characters 150-200: Next actions (path forward)

**RULE**: Behavioral instructions FIRST, data skeleton SECOND. Always.

---

## ⚡ Quick Implementation Checklist

When generating ANY response, verify:

- [ ] **Behavior header is FIRST** (`template_mode` or `status` as opening key)
- [ ] **Headline under 200 chars** with clear directive
- [ ] **All enums are inline** with pipe separators `{ENUM: a|b|c}`
- [ ] **No external references** (documentation links, "see docs", etc.)
- [ ] **Use dot notation** for nested structures `parent.child[0].field`
- [ ] **CAPS for critical signals** (STOP, REQUIRED, FATAL, MANDATORY)

---

## 📊 The 7-Level Response Hierarchy

**ALWAYS choose the highest applicable level**:

| Level | When to Use | Response Pattern |
|-------|-------------|------------------|
| **1. Hard Stop** | Unrecoverable errors | `{"status": "HARD_STOP_REQUIRED"}` |
| **2. Fatal Template** | Complex entities, mandatory templates | `{"template_mode": {"level": "fatal"}}` |
| **3. Warning Template** | Recommended templates | `{"template_mode": {"level": "warning"}}` |
| **4. Precondition** | Missing prerequisites | `{"status": "PRECONDITION_REQUIRED"}` |
| **5. Info Template** | Optional guidance | `{"template_mode": {"level": "info"}}` |
| **6. Success** | Operation completed | `{"success": true}` |
| **7. MCP Guidance** | Contextual help | `{"_mcp_guidance": {...}}` |

---

## 🎯 Pattern Templates

### Pattern 1: Fatal Template Mode (Most Common)
```json
{
  "template_mode": {
    "level": "fatal",
    "headline": "Template required — skip child entities.",
    "forbidden_children": ["page", "event", "variation"],
    "action": "get_entity_templates → manage_entity_lifecycle(mode=\"template\")"
  },
  "template": {
    "entity.key": "{FILL: lowercase_underscore}",
    "entity.name": "{FILL: Human Readable Name}",
    "entity.child[0].status": "{ENUM: active|paused|archived}",
    "entity.child[*].weight": "@auto_balance"
  }
}
```

### Pattern 2: Hard Stop Error (Unrecoverable)
```json
{
  "status": "HARD_STOP_REQUIRED",
  "error": {
    "code": 409,
    "type": "ENTITY_ALREADY_EXISTS",
    "reason": "FLAG_KEY_CONFLICT",
    "message": "Flag key 'checkout_test' already exists. Cannot create duplicate.",
    "fatal": true
  },
  "required_action": {
    "type": "ASK_USER",
    "message": "Manual intervention required. Ask user how to proceed.",
    "forbidden_actions": ["retry", "continue", "auto_fix"]
  },
  "immediate_guidance": {
    "critical_rule": "STOP all operations. Do not attempt workarounds.",
    "detected_issue": "FLAG_KEY_CONFLICT - unrecoverable without user input",
    "next_step": "Present error to user and await instructions"
  }
}
```

### Pattern 3: Warning Template Mode (Recommended)
```json
{
  "template_mode": {
    "level": "warning",
    "headline": "Template recommended for complex entities.",
    "action": "get_entity_templates → manage_entity_lifecycle(mode=\"template\")",
    "benefits": ["Auto-creates dependencies", "Prevents errors", "Ensures consistency"]
  },
  "template": {
    "entity.field": "{FILL: description}",
    "entity.reference": "@{REF: existing_entity}"
  }
}
```

### Pattern 4: Success Response
```json
{
  "success": true,
  "message": "Operation completed successfully",
  "data": {
    "id": "12345",
    "key": "entity_key",
    "name": "Entity Name"
  },
  "display_hint": "🎯 **Entity Name** | 🏢 Project | 🟢 Active"
}
```

---

## 🔤 Token Reference Guide

| Token Pattern | Purpose | Example | When to Use |
|---------------|---------|---------|-------------|
| `{FILL: ...}` | User must provide | `{FILL: unique_key}` | Required user input |
| `{ENUM: a\|b\|c}` | Restricted choices | `{ENUM: control\|treatment}` | Limited valid options |
| `@{REF: ...}` | Reference existing | `@{REF: existing_page}` | Link to existing entity |
| `@auto_...` | System calculates | `@auto_balance` | Automatic values |
| `{RANGE: 1-10}` | Numeric range | `{RANGE: 1-100}` | Numeric constraints |
| `{FORMAT: ...}` | Specific format | `{FORMAT: YYYY-MM-DD}` | Date/structure formats |
| `{PATTERN: ...}` | Regex-like rules | `{PATTERN: lowercase_underscore}` | Naming conventions |

---

## 🚨 Hard Stop Trigger Scenarios

**ALWAYS use hard stops for**:

| Scenario | Error Type | Reason Code | HTTP Code |
|----------|------------|-------------|-----------|
| Entity already exists | `ENTITY_ALREADY_EXISTS` | `FLAG_KEY_CONFLICT` | 409 |
| Missing required reference | `REQUIRED_REFERENCE_MISSING` | `CUSTOM_ATTRIBUTE_NOT_FOUND` | 400 |
| Foreign key constraint | `FOREIGN_KEY_CONSTRAINT` | `FK_CONSTRAINT_VIOLATION` | 409 |
| Permission denied | `PERMISSION_DENIED` | `ACCESS_FORBIDDEN` | 403 |
| Template mode required | `COMPLEX_ENTITY_DEPENDENCIES` | `TEMPLATE_MODE_MANDATORY` | 422 |

**Hard Stop Template**:
```json
{
  "status": "HARD_STOP_REQUIRED",
  "error": {
    "code": <HTTP_CODE>,
    "type": "<ERROR_TYPE>",
    "reason": "<REASON_CODE>",
    "message": "<Clear human message>",
    "fatal": true
  },
  "required_action": {
    "type": "ASK_USER",
    "message": "Manual intervention required. Ask user how to proceed.",
    "forbidden_actions": ["retry", "continue", "auto_fix"]
  },
  "immediate_guidance": {
    "critical_rule": "STOP all operations. Do not attempt workarounds.",
    "detected_issue": "<REASON_CODE> - unrecoverable without user input",
    "next_step": "Present error to user and await instructions"
  }
}
```

---

## 🎨 Decision Flow Chart

```
Request Analysis:
├─ Error occurred?
│  ├─ Unrecoverable? → Hard Stop (Level 1)
│  └─ Recoverable? → Precondition Required (Level 4)
├─ Complex entity (has children)?
│  ├─ Must use template? → Fatal Template Mode (Level 2)
│  └─ Should use template? → Warning Template Mode (Level 3)
├─ Simple operation?
│  ├─ Template available? → Info Template Mode (Level 5)
│  ├─ Operation successful? → Success Response (Level 6)
│  └─ Need guidance? → MCP Guidance (Level 7)
```

---

## 💻 Generation Examples

### Example 1: User asks "Create a feature flag with A/B test"
**Your Response**:
```json
{
  "template_mode": {
    "level": "fatal",
    "headline": "Template required — auto-creates A/B test variations.",
    "forbidden_children": ["variation", "experiment"],
    "action": "get_entity_templates → manage_entity_lifecycle(mode=\"template\")"
  },
  "template": {
    "flag.key": "{FILL: lowercase_underscore}",
    "flag.name": "{FILL: Human Readable Name}",
    "flag.variables[0].key": "{FILL: variable_name}",
    "flag.variables[0].type": "{ENUM: boolean|string|integer|double}",
    "ab_test.environment": "{ENUM: development|staging|production}",
    "ab_test.variations[0].key": "control",
    "ab_test.variations[0].weight": "50",
    "ab_test.variations[1].key": "treatment",
    "ab_test.variations[1].weight": "50"
  }
}
```

### Example 2: User asks "What went wrong with my audience creation?"
**If custom attribute missing**:
```json
{
  "status": "HARD_STOP_REQUIRED",
  "error": {
    "code": 400,
    "type": "REQUIRED_REFERENCE_MISSING",
    "reason": "CUSTOM_ATTRIBUTE_NOT_FOUND",
    "message": "Custom attribute(s) do not exist: 12345. Please create the attribute(s) first.",
    "fatal": true
  },
  "required_action": {
    "type": "ASK_USER",
    "message": "Manual intervention required. Ask user how to proceed.",
    "forbidden_actions": ["retry", "continue", "auto_fix"]
  },
  "immediate_guidance": {
    "critical_rule": "STOP all operations. Do not attempt workarounds.",
    "detected_issue": "CUSTOM_ATTRIBUTE_NOT_FOUND - unrecoverable without user input",
    "next_step": "Present error to user and await instructions"
  }
}
```

### Example 3: User asks "How do I create a simple audience?"
**Your Response**:
```json
{
  "template_mode": {
    "level": "info",
    "headline": "Simple audience creation available.",
    "action": "Use template below or call manage_entity_lifecycle directly"
  },
  "template": {
    "audience.name": "{FILL: Descriptive Name}",
    "audience.description": "{FILL: Targeting description}",
    "audience.conditions": "{FILL: attribute_name = 'value'}"
  }
}
```

---

## 🚫 Common Mistakes to Avoid

### ❌ NEVER Do These:
```json
// External references
{
  "documentation": "See API docs",
  "template_url": "/templates/example.json"
}

// Data before behavior
{
  "template": {...},
  "template_mode": {...}  // Too late!
}

// Verbose explanations
{
  "explanation": "This template is used for...",
  "background": "In Optimizely, entities are..."
}

// Enum as text reference
{
  "status": "See allowed values in documentation"
}
```

### ✅ ALWAYS Do These:
```json
// Behavior first, inline enums, clear actions
{
  "template_mode": {
    "level": "fatal",
    "headline": "Template required.",
    "action": "get_entity_templates"
  },
  "template": {
    "field": "{ENUM: option1|option2|option3}"
  }
}
```

---

## 🎯 Response Quality Metrics

**Workflow Compliance (99%+ achievable)**:
- Agent follows correct sequence ✓
- Agent stops when told ✓ 
- Agent calls right tools ✓

**Value Accuracy (depends on template quality)**:
- Correct enum values ✓
- Proper data formats ✓
- Required fields filled ✓

**Template Imprinting Success Indicators**:
- Agent never deviates from prescribed workflow
- Agent asks clarification only when template is unclear
- Agent stops immediately on hard stop errors
- Agent follows forbidden_actions perfectly

---

## 🔧 Integration Commands

When generating responses for specific scenarios:

### Complex Entity Creation:
```json
{"template_mode": {"level": "fatal", "headline": "Template required — skip child entities."}}
```

### Error Handling:
```json
{"status": "HARD_STOP_REQUIRED", "error": {"fatal": true}, "required_action": {"type": "ASK_USER"}}
```

### Success Operations:
```json
{"success": true, "data": {...}, "display_hint": "🎯 **Name** | 🏢 Project | 🟢 Status"}
```

---

## 🏆 Master Checklist

Before sending ANY response:

1. **Behavioral Header First** ✓
   - [ ] `template_mode` or `status` is the opening key
   - [ ] Headline is under 200 characters
   - [ ] Clear directive specified

2. **Inline Everything** ✓
   - [ ] All enums use `{ENUM: a|b|c}` format
   - [ ] No external documentation references
   - [ ] All values self-contained

3. **Structure Clarity** ✓
   - [ ] Dot notation for nested fields
   - [ ] Path notation for arrays `[0]` or `[*]`
   - [ ] Logical hierarchy preserved

4. **Hard Stop Compliance** ✓
   - [ ] Unrecoverable errors use exact hard stop format
   - [ ] `fatal: true` and `type: "ASK_USER"` for all hard stops
   - [ ] Forbidden actions clearly listed

5. **Template Quality** ✓
   - [ ] Clear fill instructions
   - [ ] Appropriate token types
   - [ ] Complete workflow coverage

---

## 💡 Quick Reference Commands

**When asked to create complex entities**: Start with `{"template_mode": {"level": "fatal"}}`

**When errors occur**: Check if unrecoverable → use `{"status": "HARD_STOP_REQUIRED"}`

**When providing guidance**: Use `{"template_mode": {"level": "info"}}` or `{"_mcp_guidance": {}}`

**When operation succeeds**: Use `{"success": true, "data": {...}}`

---

## 🎓 Final Principles

1. **First impressions are everything** - The first 200 characters determine success
2. **Structure beats prose** - Templates, not explanations
3. **Inline beats reference** - Everything in one place
4. **Show don't tell** - Examples over rules
5. **Trust the neural lock** - Once imprinted, patterns stick

**Remember**: You're not writing documentation. You're programming neural patterns. Make every character count.

---

*This guide represents the authoritative implementation standard for AI agents using the template imprinting protocol. Follow these patterns exactly for 99%+ workflow compliance.* 
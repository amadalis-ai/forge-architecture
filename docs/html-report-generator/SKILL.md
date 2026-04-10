---
name: skill.sandbox.html_report_builder
description: >
  Generate professional styled HTML pages — reports, summary pages, overview pages,
  dashboards, executive briefs, and one-pagers — with template-driven layouts, customizable
  themes, and brand identity support. Supports 5 layout templates (standard document,
  executive brief with cover page, KPI dashboard, side-by-side comparison, multi-column
  newsletter), 5+ color themes, tenant-uploadable custom CSS, logo embedding, and
  programmatic chart generation from data. Content is authored as structured JSON with
  markdown — the renderer handles all HTML generation, CSS containment, and visual
  consistency. Produces self-contained single-file HTML with embedded CSS, inline images,
  and interactive charts. Use for business reports, executive briefs, performance dashboards,
  analysis summaries, compliance documents, status updates, summary pages, overview pages,
  styled HTML pages, or any styled HTML deliverable meant for browser viewing or PDF export.
  For creative or experimental one-off pages where visual novelty matters more than
  structural consistency, remain inside the renderer unless an explicit system-owned
  render strategy contract authorizes free-form HTML.
license: Proprietary
compatibility: Requires Python 3.11+, Jinja2, markdown, wkhtmltopdf, Pillow. All pre-installed in workbench-v1.
metadata:
  author: platform-team
  version: "3.1"
  category: document-production
  wave: "1"
  tags: html report document styled charts tables dashboard branded template theme executive newsletter comparison kpi metrics markdown self-contained pdf business-report status-update escalation compliance analysis summary page summary-page overview overview-page one-pager styled-page styled-html html-page deliverable
allowed-tools: code.execute sandbox.session workspace.files.put
scripts:
  - name: render_report.py
    purpose: render_html_report
    invocation: "python3 {path} --content {content_path} --theme {theme} --output {output_path}"
  - name: render_report.py
    purpose: render_html_report_branded
    invocation: "python3 {path} --content {content_path} --theme {theme} --brand {brand_path} --output {output_path}"
  - name: render_report.py
    purpose: render_html_report_templated
    invocation: "python3 {path} --content {content_path} --theme {theme} --template {template} --output {output_path}"
  - name: validate_report.py
    purpose: validate_html_report
    invocation: "python3 {path} {html_path}"
  - name: html_to_pdf.py
    purpose: render_pdf
    invocation: "python3 {path} --input {html_path} --output {pdf_path} --page-size A4 --margin 20mm"
---

# HTML Report Generator v2

> **⚠️  CONTRACT ADHERENCE RULE (CRITICAL)**
>
> This skill provides templates, themes, and rendering capabilities. However:
>
> 1. **The step objective contains a CONTRACT (MUST) section with hard requirements** (record counts, required fields, output formats, styling requirements, row counts, color specifications).
>
> 2. **YOU MUST respect all CONTRACT constraints exactly.** If the CONTRACT says "exactly 20 rows", render exactly 20 rows. If it says "rows 1-10 light blue, rows 11-20 light pink", apply that exact styling. If it says "fetch 5 items", use exactly 5 items, not 10, not 100.
>
> 3. **Skill templates and examples are GUIDANCE. The CONTRACT is LAW.** If the CONTRACT conflicts with a skill template or theme, the CONTRACT wins. Adapt the template.
>
> 4. **Do NOT "enhance" by adding more data, more features, or more complexity than the CONTRACT specifies.** "Exactly N" means exactly N, not approximately N, not "at least N", not "up to N".
>
> 5. **When in doubt**: Prefer a simple output that meets all CONTRACT requirements over a complex output that violates even one CONTRACT constraint.

---

You are producing a professional HTML deliverable using a **structured renderer pipeline**. You provide content as a JSON contract. The renderer handles ALL HTML generation, CSS theming, layout, and visual containment. You MUST NOT write raw HTML yourself.

---

## INTEGRITY RULE (Non-Negotiable)

**The renderer is the single source of HTML.** You produce structured content JSON. The renderer produces HTML. You NEVER write `<div>`, `<table>`, `<p>`, or any HTML tags in your content JSON body fields. Body fields contain **markdown text only** — the renderer converts markdown to properly styled, themed, contained HTML.

This is the most important rule in this skill. Every visual quality issue in production has traced back to the model bypassing the renderer and writing raw HTML in body fields.

---

## When to Use This Skill

Use this skill when the task requires producing a **self-contained HTML document** — a report, brief, dashboard, analysis summary, status update, or any styled deliverable intended for browser viewing or PDF conversion.

Do NOT use this skill for:
- Raw data dumps (use data analysis tools directly)
- Markdown-only output (just write markdown)
- Interactive web applications (use `web-artifacts-builder`)
- Slide decks (use `presentation-builder`)
- Word documents (use `word-document-builder`)

### Structured Renderer vs. Free-Form HTML

**Default to the structured renderer.** Use it when:
- The deliverable needs professional consistency (branded colors, matching typography)
- The content is data-driven (tables, charts, KPI metrics, status lists)
- The output needs theme/brand support applied automatically
- Multiple sections need consistent formatting

Free-form HTML (writing your own `<style>` and HTML) requires an explicit system-owned
`render_strategy` or equivalent governance contract that authorizes renderer bypass for
this step. Creative direction alone is not enough.

When in doubt, use the renderer.

### Honoring creative direction

If the step packet includes a `creative_direction` field, or the step objective contains explicit creative or stylistic intent, use that direction to make bolder choices **within the renderer pipeline**:

- **Theme**: Pick the most expressive theme that matches the user's intent. If existing themes feel too conservative, use a high-contrast or vibrant variant.
- **Template**: Choose the layout template that best serves the creative vision (e.g., executive brief for dramatic impact, newsletter for visual variety, dashboard for data-forward boldness).
- **Section composition**: Use richer, more varied section types. Favor charts, callout boxes, and visual elements over plain text paragraphs.
- **Content tone**: Let the user's creative direction shape the voice and density of the content JSON — bolder headings, more expressive descriptions, stronger visual hierarchy.
- **Brand config**: If the user's direction conflicts with conservative brand defaults, lean toward the user's stated preference within the theme's custom properties.

Creative direction does not mean bypassing the renderer. It means configuring the renderer to produce more expressive, visually ambitious output.

---

## Execution Workflow

### Step 1: Discover available themes

```bash
cat /skills/skill.sandbox.html_report_builder/assets/theme-manifest.json
```

Read the manifest BEFORE choosing a theme. Each theme has `id`, `name`, `description`, and `character`. Pick the theme matching the audience and tone.

### Step 2: Check for brand config (optional)

```bash
test -f /skills/skill.sandbox.html_report_builder/brand/config.json && \
  cat /skills/skill.sandbox.html_report_builder/brand/config.json
```

If present, pass it to the renderer with `--brand`.

### Step 3: Build the content JSON

Create a `content.json` file following the **Content JSON Contract** below. This is the critical step — every field must follow the contract exactly.

### Step 4: Run the renderer

```bash
python3 /skills/skill.sandbox.html_report_builder/scripts/render_report.py \
  --content /workspace/work/content.json \
  --theme technical \
  --output /workspace/output/report.html
```

### Step 5: Validate

```bash
python3 /skills/skill.sandbox.html_report_builder/scripts/validate_report.py \
  /workspace/output/report.html
```

MUST pass all checks. If any check fails, fix the content JSON and re-render.

### Step 6: Convert to PDF (if requested)

```bash
python3 /skills/skill.sandbox.html_report_builder/scripts/html_to_pdf.py \
  --input /workspace/output/report.html \
  --output /workspace/output/report.pdf \
  --page-size A4 --margin 20mm
```

---

## Content JSON Contract (MUST Follow Exactly)

The content JSON is a strict contract. The renderer expects specific fields in specific formats. Deviations produce broken output.

### Top-Level Structure

```json
{
  "theme": "technical",
  "metadata": {
    "title": "Report Title",
    "subtitle": "Optional subtitle",
    "date": "2026-03-18",
    "author": "Author Name",
    "confidentiality": "Internal"
  },
  "sections": [ ... ],
  "footer": "Optional footer text"
}
```

- `theme`: MUST match a theme ID from `theme-manifest.json`
- `metadata.title`: REQUIRED — appears in header and `<title>` tag
- `sections`: REQUIRED — array of section objects, each with a `type` field

### Section Type Contract

Every section object MUST have a `type` field. The renderer dispatches to a type-specific renderer based on this field. There are exactly 10 section types. Use the right type for the right content.

**CRITICAL**: Each section type has a specific JSON shape. Do NOT put table data in a `section` type. Do NOT put narrative text in a `table` type. The renderer has dedicated renderers for each type that produce correct CSS classes, wrapper elements, and layout.

---

## Section Types Reference

### `section` — Narrative Text

For headings + paragraphs + lists + subheadings. The most common type.

```json
{
  "type": "section",
  "heading": "Section Title",
  "level": 1,
  "body": "**Bold text** and *italic*.\n\n- Bullet one\n- Bullet two\n\n### Subheading\n\nMore content here."
}
```

**`body` field rules (CRITICAL):**
- MUST contain **markdown text only**
- MUST NOT contain HTML tags (`<div>`, `<table>`, `<p>`, `<ul>`, `<span>`, etc.)
- Use markdown formatting: `**bold**`, `*italic*`, `- bullets`, `1. numbered`, `### subheadings`, `` `code` ``, `[links](url)`
- The renderer converts markdown to styled HTML with the correct CSS classes
- `level`: 1, 2, or 3 — maps to `<h1>`, `<h2>`, `<h3>`

### `executive_summary` — Highlighted Summary Block

For key findings at the start of a report. Rendered with left border accent and larger font.

```json
{
  "type": "executive_summary",
  "body": "Three critical findings require immediate attention:\n\n1. Finding one\n2. Finding two\n3. Finding three"
}
```

- `body`: Markdown text only (same rules as `section`)

### `table` — Structured Data Table

For tabular data. The renderer produces overflow-contained tables with header styling, alternating row colors, and conditional cell highlighting.

```json
{
  "type": "table",
  "heading": "Staffing Overview",
  "caption": "As of March 2026",
  "columns": ["Role", "Headcount", "Projects"],
  "rows": [
    ["EM", "12", "117"],
    ["SA", "11", "128"],
    ["SC", "17", "83"]
  ],
  "highlight_rules": {
    "Projects": { "117": "danger", "128": "danger" }
  },
  "footnotes": ["*AI utilization expected to reduce concurrent projects"]
}
```

- `columns`: Array of column header strings
- `rows`: Array of arrays — each inner array is one row of cell values (strings)
- `highlight_rules`: Column name → { cell value → "danger"|"warning"|"success"|"info" }
- `footnotes`: Array of strings rendered below the table

**CRITICAL**: NEVER put table data inside a `section` body as raw HTML. ALWAYS use `type: "table"` with `columns` and `rows` arrays. The renderer wraps tables in `.table-wrapper` for overflow containment, applies `.data-table` styling, handles header colors, alternating rows, and conditional highlighting. Raw `<table>` in a body field gets none of this.

### `status_list` — Color-Coded Status Items

For escalation lists, risk registers, project trackers.

```json
{
  "type": "status_list",
  "heading": "Current Escalations",
  "items": [
    {
      "name": "Customer A",
      "status": "red",
      "summary": "Integration delayed 3 weeks",
      "action": "Escalated to VP Engineering"
    }
  ]
}
```

- `status`: "red" | "yellow" | "green" | "blue" | "gray"
- `action`: Optional action callout with accent styling

### `metrics_row` — KPI Strip

For performance metrics, scorecards, summary statistics. Rendered as a horizontal card strip.

```json
{
  "type": "metrics_row",
  "heading": "Portfolio Summary",
  "metrics": [
    { "value": "94%", "label": "Compliance Score", "trend": "up", "variant": "success" },
    { "value": "3", "label": "Open Findings", "trend": "down" },
    { "value": "$1.2M", "label": "Risk Exposure", "percentage": "12%", "variant": "warning" }
  ]
}
```

- `trend`: "up" | "down" | "flat" — arrow indicator
- `variant`: "success" | "warning" | "danger" — colors the card border and value
- `percentage`: Optional sub-label below the value

### `chart` — Programmatic Chart from Data

For visualizations. Charts are generated as interactive Chart.js canvases from data.

**Bar / grouped bar:**
```json
{
  "type": "chart",
  "chart_type": "grouped_bar",
  "heading": "Sales by Quarter",
  "caption": "Sold vs Live — prior 4 quarters",
  "data": {
    "labels": ["Q1 '25", "Q2 '25", "Q3 '25", "Q4 '25"],
    "datasets": [
      { "label": "Sold", "values": [3, 13, 6, 12], "color": "primary" },
      { "label": "Live", "values": [0, 5, 0, 0], "color": "success" }
    ]
  },
  "options": { "y_axis_label": "Count" }
}
```

**Pie / doughnut (simplified format):**
```json
{
  "type": "chart",
  "chart_type": "doughnut",
  "heading": "Stage Distribution",
  "data": {
    "labels": ["Complete", "Kicked-off", "Stalled"],
    "values": [7, 15, 5],
    "colors": ["success", "primary", "warning"]
  }
}
```

**Available chart types:** `bar`, `grouped_bar`, `stacked_bar`, `horizontal_bar`, `line`, `area`, `pie`, `doughnut`, `radar`

**Color names:** Use semantic names that resolve to theme colors: `primary`, `secondary`, `accent`, `success`, `warning`, `danger`

### `callout` — Highlighted Box

For key takeaways, action items, warnings, important notes.

```json
{
  "type": "callout",
  "variant": "warning",
  "title": "Action Required",
  "body": "Three findings require immediate remediation before Q2 audit."
}
```

- `variant`: "info" | "warning" | "success" | "danger"
- `body`: Markdown text only

**CRITICAL**: NEVER put callout content inside a `section` body as `<div class="callout">`. ALWAYS use `type: "callout"` with `variant` and `body`. The renderer produces the correct CSS classes (`callout callout-warning`), title styling, and background colors. Raw HTML callouts use class names that may not exist in the theme.

### `comparison` — Side-by-Side Columns

For option analysis, before/after, vendor evaluations.

```json
{
  "type": "comparison",
  "heading": "Option Analysis",
  "left": { "heading": "Option A: Build", "body": "**Pros:**\n- Full control\n- Custom fit" },
  "right": { "heading": "Option B: Buy", "body": "**Pros:**\n- Faster time-to-market\n- Lower cost" }
}
```

- `left.body` and `right.body`: Markdown text only

### `divider` — Section Separator

```json
{ "type": "divider", "style": "banner", "text": "Operational Updates" }
```

- `style`: "line" (horizontal rule) or "banner" (full-width colored bar with text)

### `page_break` — PDF Page Break

```json
{ "type": "page_break" }
```

---

## Layout Templates

The renderer auto-selects the layout based on content:

| Content pattern | Template selected | Layout behavior |
|---|---|---|
| Has `cover` object in content JSON | `executive-brief` | Cover page + exec summary + body sections |
| Has `metrics_row` sections (no cover) | `dashboard` | KPI strip at top + chart/table grid + body |
| Has `comparison` sections | `comparison` | Header + side-by-side content columns |
| Default | `standard` | Header + auto-generated TOC + linear sections + footer |

Override by adding `"template": "newsletter"` to content JSON for multi-column layout with sidebar.

---

## Available Themes

Read `theme-manifest.json` at runtime for the current list. Platform defaults:

| Theme | Character | Best for |
|---|---|---|
| `executive` | Formal, navy/gold/serif | C-suite, board reports, client deliverables |
| `technical` | Professional, slate/cyan/sans-serif | Engineering docs, architecture reviews, technical audits |
| `compliance` | Formal, dark blue/teal/serif | Legal, regulatory, audit, compliance documents |
| `modern` | Casual, indigo/pink/system-ui | Customer-facing, product updates, team reports |
| `minimal` | Neutral, monochrome/whitespace | Design-conscious, clean presentations |

---

## ANTI-PATTERNS (Common Failures — Do NOT Do These)

### Anti-Pattern 1: Raw HTML in body fields

**WRONG** — Produces broken layout (tables without overflow containment, missing theme styles, paragraphs wrapping block elements):
```json
{
  "type": "section",
  "heading": "Runtime Comparison",
  "body": "<table><thead><tr><th>Runtime</th><th>Status</th></tr></thead><tbody><tr><td>Workers</td><td>Supported</td></tr></tbody></table>"
}
```

**RIGHT** — Use the `table` section type:
```json
{
  "type": "table",
  "heading": "Runtime Comparison",
  "columns": ["Runtime", "Status"],
  "rows": [["Workers", "Supported"]]
}
```

### Anti-Pattern 2: HTML callouts in body fields

**WRONG** — CSS class names may not match theme, no variant styling:
```json
{
  "type": "section",
  "body": "<div class=\"callout warning\"><strong>Warning:</strong> This is important.</div>"
}
```

**RIGHT** — Use the `callout` section type:
```json
{
  "type": "callout",
  "variant": "warning",
  "title": "Warning",
  "body": "This is important."
}
```

### Anti-Pattern 3: HTML grid/layout divs in body fields

**WRONG** — `grid`, `kv-grid`, `note` are not defined CSS classes:
```json
{
  "type": "section",
  "body": "<div class=\"grid\"><div>Column 1</div><div>Column 2</div></div>"
}
```

**RIGHT** — Use the `comparison` section type for side-by-side:
```json
{
  "type": "comparison",
  "heading": "Comparison",
  "left": { "heading": "Column 1", "body": "Content for left side" },
  "right": { "heading": "Column 2", "body": "Content for right side" }
}
```

### Anti-Pattern 4: HTML lists in body fields

**WRONG** — Double-converted by markdown processor:
```json
{
  "type": "section",
  "body": "<ul><li>Item one</li><li>Item two</li></ul>"
}
```

**RIGHT** — Use markdown list syntax:
```json
{
  "type": "section",
  "body": "- Item one\n- Item two"
}
```

### Anti-Pattern 5: Embedding multiple content types in one section

**WRONG** — A section body containing a mix of narrative, table HTML, and callout HTML:
```json
{
  "type": "section",
  "heading": "Findings",
  "body": "Overview text.\n<table>...</table>\n<div class='callout'>...</div>\nMore text."
}
```

**RIGHT** — Split into separate sections with correct types:
```json
[
  { "type": "section", "heading": "Findings", "level": 1, "body": "Overview text." },
  { "type": "table", "heading": "Finding Details", "columns": [...], "rows": [...] },
  { "type": "callout", "variant": "warning", "title": "Action Required", "body": "..." },
  { "type": "section", "level": 2, "body": "More text." }
]
```

### Anti-Pattern 6: Inventing CSS class names

**WRONG** — Using CSS classes not defined in base.css:
```json
{
  "type": "section",
  "body": "<span class='badge badge-vendor-doc'>vendor_doc</span>"
}
```

The renderer's base.css defines a specific set of classes. Using undefined classes produces unstyled elements. If you need a visual pattern, use a section type that provides it (callout for highlighted boxes, status_list for badges, table for structured data).

### Anti-Pattern 7: Passing pre-built HTML body to render_report.py

**WRONG** — Building HTML yourself and passing it as a section body for the renderer to wrap:
```python
html_body = '<p>' + esc(text) + '</p>'
sections.append({'type': 'section', 'body': html_body})
```

**RIGHT** — Pass markdown text, let the renderer convert:
```python
sections.append({'type': 'section', 'body': text})
```

---

## PRESCRIPTIVE RULES (Must Follow)

### Rule 1: One Concern Per Section

Each section object represents ONE content element. A table is one section. A callout is one section. A paragraph of narrative is one section. Do NOT combine multiple content types in a single section body.

### Rule 2: Use the Most Specific Section Type

Map your content to the most specific type available:
- Tabular data → `table` (not `section` with markdown table or raw HTML)
- Key finding / warning → `callout` (not `section` with bold text)
- KPI numbers → `metrics_row` (not `section` with bold numbers)
- Side-by-side analysis → `comparison` (not `section` with HTML columns)
- Status tracker → `status_list` (not `table` with color columns)
- Chart → `chart` (not an image or SVG)

### Rule 3: Body Fields Are Markdown Only

Every `body` field in every section type MUST contain markdown text. The renderer handles HTML conversion. The only exception is if the renderer's HTML detection safety net catches raw HTML and passes it through — but this is a fallback, not an intended path.

### Rule 4: Validate Before Delivering

Always run `validate_report.py` on the output. Check for:
- `PASS` on all checks
- `WARN` on `containment_tables` means raw tables escaped the wrapper — fix the content JSON
- `WARN` on `no_block_in_p` means HTML was double-converted — you passed raw HTML in a body field
- `WARN` on `css_class_coverage` means you used CSS classes not defined in the theme

### Rule 5: Semantic Colors for Charts

Use semantic color names (`primary`, `secondary`, `accent`, `success`, `warning`, `danger`) in chart data, NOT hex values. The renderer resolves them to the active theme's colors. This ensures charts match the theme automatically.

### Rule 6: Let the Renderer Choose the Layout

Do NOT set `"template"` unless you have a specific reason. The renderer infers the best layout from your content (cover → executive-brief, metrics → dashboard, etc.). Manual override is for edge cases only.

---

## Decision Framework: Choosing Section Types

When you receive content that needs to appear in the report, use this decision tree:

```
Is this tabular data (rows × columns)?
  YES → type: "table" with columns[] and rows[]

Is this a key metric / KPI number?
  YES → type: "metrics_row" with metrics[]

Is this a warning, note, or key takeaway?
  YES → type: "callout" with variant

Is this a status/risk item with a color indicator?
  YES → type: "status_list" with items[]

Is this numerical data that should be visualized?
  YES → type: "chart" with chart_type and data

Is this a side-by-side comparison (2 options, before/after)?
  YES → type: "comparison" with left and right

Is this narrative text (paragraphs, bullets, subheadings)?
  YES → type: "section" with markdown body
```

If content doesn't fit any type above, use `type: "section"` with a markdown body. Do NOT invent new section types or use HTML to create custom layouts.

---

## Composition with Other Skills

This skill is typically the **final step** in a multi-skill pipeline:

- **After data analysis**: Analysis results → chart data + table data → content JSON sections
- **After web research**: Research evidence → synthesis narrative → section + callout + table sections
- **After investigation**: Findings → status list + table + executive summary sections

The upstream skill produces structured data. This skill consumes it as content JSON. Do NOT pass upstream HTML through this skill's body fields.

---

## Defensive Input Consumption (CRITICAL)

When your glue code reads upstream JSON files to build content.json sections, you MUST validate the data shape before aggregating. The runtime does NOT validate input file content — your code is the last line of defense.

### Rule: Validate numeric maps before summing

Upstream JSON files (e.g., `exception_summary.json`, `kpi_summary.json`, `audit_results.json`) may contain maps intended to be `string → integer`. Before calling `sum()`, `max()`, `min()`, or any arithmetic on `.values()`, verify every value is a scalar number.

**Defensive pattern (MUST use when aggregating map values):**

```python
import json

def safe_load_json(path: str) -> dict:
    """Load JSON with basic structural validation."""
    with open(path) as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError(f"Expected dict from {path}, got {type(data).__name__}")
    return data

def safe_numeric_map(mapping: dict, field_name: str) -> dict:
    """Validate that a map contains only scalar numeric values.
    Raises on nested dicts/lists instead of crashing in sum()."""
    if not isinstance(mapping, dict):
        raise ValueError(f"{field_name} is not a dict: {type(mapping).__name__}")
    clean = {}
    for k, v in mapping.items():
        if isinstance(v, (dict, list)):
            raise ValueError(
                f"{field_name}['{k}'] is {type(v).__name__}, expected int. "
                f"Upstream data has nested structures — cannot aggregate."
            )
        if not isinstance(v, (int, float)):
            raise ValueError(
                f"{field_name}['{k}'] = {v!r}, expected numeric value"
            )
        clean[k] = int(v)
    return clean

# Usage in glue code:
data = safe_load_json('/workspace/output/exception_summary.json')
totals_by_type = safe_numeric_map(data.get('totals_by_type', {}), 'totals_by_type')
total_exceptions = sum(totals_by_type.values())  # now safe — all values are int
```

### Why this matters

The executor service resolves input file **paths** but does not validate input file **content**. If an upstream step produced malformed JSON (e.g., nested dicts where integers were expected), your code will crash with `TypeError: unsupported operand type(s) for +: 'int' and 'dict'` inside `sum()`. This is the most common render-step crash in billing audit pipelines.

### Failure modes to catch before they crash

| Upstream defect | What happens without defense | What your guard should do |
|----------------|------------------------------|--------------------------|
| `totals_by_type` has nested dicts | `sum()` → TypeError | `safe_numeric_map()` raises with clear message |
| `totals_by_type` is `None` or missing | `None.values()` → AttributeError | Default to `{}`, warn in report |
| `totals_by_type` has string values | `sum()` → TypeError | `safe_numeric_map()` raises with the offending key |
| Entire JSON file is malformed | `json.load()` → JSONDecodeError | Catch, report in a callout section, skip the table |

### When to apply this defense

Apply `safe_numeric_map()` or equivalent validation **every time** your glue code reads an upstream JSON file and aggregates its values into metrics, tables, or chart data for content.json. This includes:
- Exception summary maps (`totals_by_type`, `totals_by_invoice_status`)
- KPI summaries (`revenue_by_region`, `counts_by_status`)
- Any map where you call `sum()`, `max()`, `min()`, or iterate `.values()` for arithmetic

---

## Quick Reference: Content JSON Shape

```json
{
  "theme": "executive | technical | compliance | modern | minimal",
  "metadata": {
    "title": "REQUIRED",
    "subtitle": "optional",
    "date": "YYYY-MM-DD",
    "author": "optional",
    "confidentiality": "optional"
  },
  "cover": { "headline": "optional", "tagline": "optional" },
  "sections": [
    { "type": "executive_summary", "body": "markdown" },
    { "type": "callout", "variant": "info|warning|success|danger", "title": "optional", "body": "markdown" },
    { "type": "metrics_row", "heading": "optional", "metrics": [{ "value": "...", "label": "...", "trend": "up|down|flat", "variant": "success|warning|danger" }] },
    { "type": "section", "heading": "...", "level": 1, "body": "markdown" },
    { "type": "table", "heading": "...", "columns": [], "rows": [[]], "highlight_rules": {}, "footnotes": [] },
    { "type": "chart", "chart_type": "bar|line|pie|...", "heading": "...", "data": { "labels": [], "datasets": [] } },
    { "type": "status_list", "heading": "...", "items": [{ "name": "...", "status": "red|yellow|green|blue|gray", "summary": "...", "action": "..." }] },
    { "type": "comparison", "heading": "...", "left": { "heading": "...", "body": "markdown" }, "right": { "heading": "...", "body": "markdown" } },
    { "type": "divider", "style": "line|banner", "text": "optional" },
    { "type": "page_break" }
  ],
  "footer": "optional footer text"
}
```

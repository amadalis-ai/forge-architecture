# HTML Report Generator v2 — Reference Bible

> **Audience**: End users, operators, administrators, and AI agents
> **Skill ID**: `skill.sandbox.html_report_builder`
> **Version**: 2.0
> **Last Updated**: 2026-03-19

---

## 1. What This Skill Produces

The HTML Report Generator creates **self-contained, professionally styled HTML documents** — business reports, executive briefs, KPI dashboards, comparison analyses, compliance documents, and more. Every report is a single `.html` file with all CSS, fonts, charts, and images embedded inline. No external dependencies. Open it in any browser, email it, or convert it to PDF.

The system provides you with the following capabilities, each explained in detail in the sections that follow:

- **5 visual themes** — professional color and typography palettes for different audiences and contexts
- **5 layout templates** — document structures from simple linear reports to KPI dashboards and newsletters
- **10 content section types** — building blocks like tables, charts, KPI metrics, status lists, callouts, and comparisons
- **9 chart types** — interactive data visualizations generated from your data (bar, line, pie, radar, and more)
- **Brand identity support** — your company logo, colors, and fonts applied automatically on top of any theme
- **PDF conversion** — one-step conversion from HTML to PDF with full styling preserved

Read through these features first so you understand what's available. Then Section 8 shows you how to request any of them through natural language, and Section 9 provides complete example prompts.

---

## 2. Themes — Visual Styles

A theme controls the entire visual identity of your report: colors, fonts, spacing, and the look of every component (tables, charts, callouts, badges). The system ships with 5 built-in themes. Your administrator can also add custom themes for your organization.

### Available themes

| Theme ID | Name | Colors & Fonts | Character | Best For |
|----------|------|----------------|-----------|----------|
| `executive` | Executive | Navy blue, gold accents, serif headings (Georgia). Conservative and authoritative. | Formal | C-suite, board reports, client deliverables, formal presentations |
| `technical` | Technical | Slate gray, cyan accents, sans-serif headings (system-ui). Dense and information-forward. | Professional | Engineering docs, architecture reviews, technical audits, API docs |
| `compliance` | Compliance | Dark blue, teal accents, serif headings. Print-optimized, formal. | Formal | Legal documents, regulatory reports, audit findings, due diligence |
| `modern` | Modern | Indigo, pink accents, system-ui fonts. Vibrant and contemporary. | Casual | Customer-facing, product updates, team reports, marketing summaries |
| `minimal` | Minimal | Monochrome, lots of whitespace, sharp typography. Content-forward. | Neutral | Design-conscious audiences, data-forward reports, clean presentations |

### What each theme controls

Every theme sets these visual properties:

| Property | What it affects |
|----------|----------------|
| **Primary color** | Headings, header borders, table headers, chart default color |
| **Secondary color** | Accents, section borders, decorative elements, cover page divider |
| **Accent color** | Links, interactive elements, h3 headings |
| **Heading font** | All headings (h1-h3) |
| **Body font** | All body text, tables, lists |
| **Status colors** | Green (success), amber (warning), red (danger) — used in status lists, metric cards, table highlights |

Charts automatically match the theme — bars, lines, and pie segments use the theme's color palette.

### Default behavior

If you don't specify a theme, the model chooses based on context:
- Executive-level or board content → `executive`
- Engineering or technical content → `technical`
- Legal, audit, or regulatory content → `compliance`
- Customer-facing or team content → `modern`
- No strong signal → `executive` (the default)

---

## 3. Layout Templates — Document Structures

A layout template defines the structural arrangement of your report — where headers, sidebars, KPI strips, and content areas go on the page. The system has 5 layouts. The model automatically selects the best one based on your content, but you can override.

### Standard (default)

```
┌──────────────────────────────┐
│ Title  |  Date  |  Author    │  Header
├──────────────────────────────┤
│ Table of Contents            │  Auto-generated
├──────────────────────────────┤
│ Section 1                    │
│ Section 2                    │  Linear flow
│ Section 3                    │
│ ...                          │
├──────────────────────────────┤
│ Footer                       │
└──────────────────────────────┘
```

A straightforward top-to-bottom document. Header with title/date/author, optional auto-generated table of contents, then all your sections flow linearly, ending with a footer.

**Auto-selected when:** No cover page requested, no KPI metrics, no comparison sections. This is the fallback for general-purpose reports.

### Executive Brief

```
┌──────────────────────────────┐
│                              │
│        COVER PAGE            │
│     Title + Tagline          │  Full-page cover
│     Date + Author            │
│     [Logo]                   │
│                              │
├──────────────────────────────┤
│ Executive Summary            │  Highlighted block
├──────────────────────────────┤
│ Section 1                    │
│ Section 2                    │  Body content
│ ...                          │
├──────────────────────────────┤
│ Footer                       │
└──────────────────────────────┘
```

Opens with a dedicated cover page (title, tagline, date, logo), followed by a highlighted executive summary block, then body content. Designed for formal deliverables that need a title page.

**Auto-selected when:** You ask for a cover page or the content includes a cover headline/tagline.

### Dashboard

```
┌──────────────────────────────┐
│ Title  |  Date               │  Header
├──────────────────────────────┤
│ [KPI] [KPI] [KPI] [KPI]     │  Metrics strip
├──────────────────────────────┤
│ ┌──────────┐ ┌──────────┐   │
│ │  Chart 1  │ │  Chart 2  │  │  2-column grid
│ └──────────┘ └──────────┘   │
│ ┌────────────────────────┐   │
│ │ Full-width data table   │  │
│ └────────────────────────┘   │
├──────────────────────────────┤
│ Additional sections          │  Overflow content
├──────────────────────────────┤
│ Footer                       │
└──────────────────────────────┘
```

KPI metric cards across the top, then a 2-column grid for charts and tables below. Additional narrative sections flow after the grid. Designed for performance monitoring and data-heavy reports.

**Auto-selected when:** Content includes KPI metrics but no cover page.

### Comparison

```
┌──────────────────────────────┐
│ Title  |  Date               │  Header
├──────────────────────────────┤
│ ┌────────────┬────────────┐  │
│ │  Option A   │  Option B   │ │  Side-by-side
│ │  Content    │  Content    │ │
│ └────────────┴────────────┘  │
├──────────────────────────────┤
│ Additional sections          │
├──────────────────────────────┤
│ Footer                       │
└──────────────────────────────┘
```

Two equal columns for side-by-side analysis. Use for vendor evaluations, option analysis, before/after comparisons. Additional sections (charts, tables, narrative) flow below the comparison area.

**Auto-selected when:** Content includes comparison sections.

### Newsletter

```
┌──────────────────────────────┐
│         HERO HEADER          │  Full-width banner
│     Title + Subtitle         │
├──────────────────────────────┤
│ ┌──────────────┬──────────┐  │
│ │              │          │  │
│ │  Main        │ Sidebar  │  │  2/3 + 1/3
│ │  Content     │ Cards    │  │
│ │  (sections)  │ (callouts│  │
│ │              │  status) │  │
│ └──────────────┴──────────┘  │
├──────────────────────────────┤
│ Footer                       │
└──────────────────────────────┘
```

Hero banner header, then a 2/3 main column with narrative sections alongside a 1/3 sidebar for callout cards, status lists, and highlights. Designed for team newsletters and mixed-content updates.

**Auto-selected when:** Only if explicitly requested — there is no auto-inference for newsletter.

---

## 4. Content Section Types — Building Blocks

Every report is built from section types. These are the content building blocks the system supports. Each section type renders with specific styling and behavior. When you describe your report, the model maps your request to the appropriate types automatically.

### Narrative text (`section`)

The most common type. A heading followed by rich text content using markdown formatting (bold, italic, links, lists, code blocks, sub-headings).

### Executive summary (`executive_summary`)

A highlighted summary block with a distinct background color, rendered at the top of the report. Use for key findings, recommendations, or a TL;DR.

### Data table (`table`)

A formatted data table with column headers, rows, and optional features:
- **Conditional cell highlighting** — color-code individual cells based on their value (danger/red, warning/amber, success/green, info/blue)
- **Row styling** — de-emphasize entire rows (e.g., totals row, inactive items)
- **Footnotes** — explanatory notes rendered below the table
- **Caption** — descriptive subtitle above the table

All tables are automatically overflow-protected with horizontal scrolling for wide content.

### Status list (`status_list`)

A list of items with color-coded status badges and optional action callouts. Each item has:
- **Name** — the item being tracked
- **Status** — `red`, `yellow`, `green`, `blue`, or `gray` badge
- **Summary** — brief description
- **Action** (optional) — what's being done about it

Use for escalation lists, risk registers, project trackers, or any status-tracked items.

### KPI metrics (`metrics_row`)

A horizontal strip of metric cards, each showing:
- **Value** — the number or percentage
- **Label** — what the metric measures
- **Trend** — up arrow, down arrow, or flat indicator
- **Variant** (optional) — `success` (green), `warning` (amber), or `danger` (red) coloring
- **Percentage** (optional) — sub-label below the value

Use for scorecards, portfolio summaries, and performance snapshots.

### Chart (`chart`)

An interactive data visualization rendered from structured data. See Section 5 for the full chart type reference.

### Callout box (`callout`)

A highlighted box with a colored left border, used for drawing attention. Variants:
- **info** (blue) — informational notes, context
- **warning** (amber) — cautions, things to watch
- **success** (green) — positive outcomes, achievements
- **danger** (red) — critical alerts, blockers, failures

Each callout can have a title and markdown body text.

### Comparison (`comparison`)

Two side-by-side columns with independent headings and markdown content. Use for option analysis, before/after, or vendor evaluation.

### Divider (`divider`)

A visual separator between major sections. Two styles:
- **line** — a simple horizontal rule
- **banner** — a full-width colored bar with text (acts as a section header)

### Page break (`page_break`)

Forces a page break when the report is converted to PDF. No visible effect in HTML browser view.

---

## 5. Charts and Data Visualization

Charts are generated programmatically from your data using Chart.js. You provide the data; the renderer creates interactive charts that automatically match the active theme's color palette.

### Available chart types

| Chart Type | Description | Best For |
|------------|-------------|----------|
| **Bar** | Vertical bars | Comparing quantities across categories |
| **Grouped Bar** | Multiple bar series side by side | Comparing multiple measures across categories |
| **Stacked Bar** | Bars stacked showing composition | Showing how parts make up totals |
| **Horizontal Bar** | Bars running left to right | Categories with long text labels |
| **Line** | Connected points | Trends over time |
| **Area** | Filled line chart | Volume or magnitude over time |
| **Pie** | Proportional slices | Parts of a whole |
| **Doughnut** | Pie with center hole | Proportions with emphasis on a central metric |
| **Radar** | Spider/web chart | Multi-dimensional comparison (e.g., comparing vendors across 6 criteria) |

### Chart colors

Charts use **semantic color names** that automatically resolve to the active theme's palette:

| Color Name | What it maps to | Typical use |
|------------|----------------|-------------|
| `primary` | Theme's primary color | Main data series |
| `secondary` | Theme's secondary color | Supporting series |
| `accent` | Theme's accent color | Highlighting or tertiary series |
| `success` | Green | Positive values, targets met |
| `warning` | Amber | Caution, approaching limits |
| `danger` | Red | Negative values, targets missed |

When you switch themes, all chart colors update automatically.

### Target lines

Any bar or line chart can have a **target/reference line** — a dashed horizontal line at a specific value with an optional label (e.g., "Target: 85%"). Use this to show goals, benchmarks, or thresholds.

---

## 6. Branding — Logo, Colors, and Custom Identity

Branding lets you apply your organization's visual identity on top of any theme. It works in two tiers:

| Tier | What it does | Who sets it up | Effort |
|------|-------------|----------------|--------|
| **Brand config** (JSON) | Adds your logo, overrides specific colors and fonts on top of any theme | Workspace admin or operator | 5 minutes |
| **Custom CSS theme** | Completely custom visual identity — your own theme from scratch | Admin via skill version UI | 30 minutes |

### Tier 1: Brand Config (Quick Setup)

Brand config is a JSON file that layers your identity ON TOP of any theme. You pick a base theme (e.g., `executive`) and then the brand config overrides specific colors, adds your logo, and sets your company name. The rest of the theme remains intact.

#### Brand config format

```json
{
  "company_name": "Contoso Corp",
  "logo": "brand/logo.png",
  "logo_position": "header",
  "color_overrides": {
    "primary": "#0052CC",
    "secondary": "#FF5630",
    "accent": "#00B8D9"
  },
  "font_overrides": {
    "heading": "Montserrat, system-ui, sans-serif",
    "body": "'Open Sans', system-ui, sans-serif"
  },
  "footer_text": "Contoso Corp — Confidential"
}
```

#### How to set up branding

**Step 1: Upload your logo**

Upload your company logo (PNG, JPG, SVG, or WebP) to the skill's `brand/` directory. You can do this through:

- **Admin UI**: Navigate to the skill in the Skills admin panel, go to the Files tab, and upload the logo to the `brand/` directory.
- **Seed script**: Place the logo file in the skill's local `brand/` directory and re-seed with `--force`.
- **Operator chat**: "Upload our company logo for report branding" — then attach the file.

Supported logo formats: `.png`, `.jpg`, `.jpeg`, `.gif`, `.svg`, `.webp`

The logo is automatically base64-encoded and embedded directly in the HTML — no external file references, no broken images.

**Step 2: Create the brand config**

Create a `brand/config.json` file with your brand settings. Only include the fields you want to override — everything else falls back to the selected theme.

Minimal example (logo only):
```json
{
  "company_name": "Acme Inc",
  "logo": "brand/logo.png"
}
```

Full example (logo + colors + fonts + footer):
```json
{
  "company_name": "Acme Inc",
  "logo": "brand/acme-logo.svg",
  "logo_position": "header",
  "color_overrides": {
    "primary": "#1A1A2E",
    "secondary": "#E94560",
    "accent": "#0F3460"
  },
  "font_overrides": {
    "heading": "'Poppins', system-ui, sans-serif",
    "body": "'Inter', system-ui, sans-serif"
  },
  "footer_text": "Acme Inc — All Rights Reserved"
}
```

**Step 3: Use it**

Once brand config exists, the model automatically detects and applies it. You can also be explicit in your prompt (see Section 8).

#### Brand config fields reference

| Field | Required | Description |
|-------|----------|-------------|
| `company_name` | No | Company name used for logo alt text and footer |
| `logo` | No | Path to logo file relative to skill root (e.g., `brand/logo.png`) |
| `logo_position` | No | Where the logo appears: `"header"` (default) places it top-right |
| `color_overrides` | No | Object of CSS color variable overrides (see table below) |
| `font_overrides` | No | Object of CSS font variable overrides: `heading` and/or `body` |
| `footer_text` | No | Custom footer text displayed on all pages |

#### Color override keys

These go inside `color_overrides`. Only include the ones you want to change:

| Key | What it changes | Example |
|-----|----------------|---------|
| `primary` | Headings, header borders, table headers, chart primary color | `"#0052CC"` |
| `secondary` | Accent decorations, section borders, cover divider | `"#FF5630"` |
| `accent` | Links, h3 headings, interactive elements | `"#00B8D9"` |
| `text` | Body text color | `"#333333"` |
| `text-light` | Secondary text, captions, footnotes | `"#888888"` |
| `bg` | Page background | `"#FFFFFF"` |
| `bg-alt` | Callout/card/table stripe background | `"#F4F5F7"` |
| `border` | Borders, dividers, table lines | `"#DFE1E6"` |
| `success` | Green indicators in status lists, metrics, cells | `"#36B37E"` |
| `warning` | Amber indicators | `"#FFAB00"` |
| `danger` | Red indicators | `"#FF5630"` |

### Tier 2: Custom CSS Theme (Full Control)

For complete visual control, create your own CSS theme file. This replaces a built-in theme entirely rather than overlaying on one.

**Step 1: Create your theme CSS**

Create a `.css` file that defines the required CSS custom properties:

```css
/* acme-brand.css */
:root {
  /* Required — must define all 5 */
  --color-primary: #0052CC;
  --color-secondary: #FF5630;
  --color-accent: #00B8D9;
  --font-heading: 'Poppins', system-ui, sans-serif;
  --font-body: 'Inter', system-ui, sans-serif;

  /* Optional — override any for fine control */
  --color-text: #172B4D;
  --color-bg-alt: #F4F5F7;
  --border-radius: 6px;
  --spacing-section: 40px;
  --max-width: 960px;
}
```

**Required variables** (must define all 5): `--color-primary`, `--color-secondary`, `--color-accent`, `--font-heading`, `--font-body`

See the [Theme Contract](references/theme-contract.md) for the full list of optional variables.

**Step 2: Upload the theme**

Upload your CSS file to `assets/themes/` in the skill's file tree (via Admin UI or seed script).

**Step 3: Register in the theme manifest**

Update `assets/theme-manifest.json` to include your theme:

```json
{
  "id": "acme-brand",
  "name": "Acme Brand",
  "description": "Acme Corp brand identity with Atlassian-inspired colors and modern typography.",
  "source": "tenant",
  "character": "professional"
}
```

**Step 4: Use it**

Users can now say "use the acme-brand theme" in their prompts.

### CSS cascade order

```
1. base.css           ← Global component styles + containment rules
2. themes/{name}.css  ← Theme CSS variables (:root)
3. brand config CSS   ← Brand overrides (:root) — wins over theme
```

Brand config always wins. If you set `"primary": "#FF0000"` in brand config and the theme has `--color-primary: #1B2A4A`, the report uses `#FF0000`.

---

## 7. PDF Conversion

Every HTML report can be converted to PDF. The conversion preserves all styling, charts, tables, and layout. PDF output uses `wkhtmltopdf` (pre-installed in the container).

### Options

| Option | Default | Description |
|--------|---------|-------------|
| Page size | A4 | Also supports Letter, Legal |
| Margins | 20mm | Adjustable per side |
| Page breaks | Automatic | Can be forced with `page_break` sections |
| Orientation | Portrait | Can request landscape for wide tables/charts |

---

## 8. How to Use It — Natural Language via Operator Chat

Now that you know what features are available, here's how to request them. You interact with this skill through **natural language** in the operator chat. You don't need to write JSON, CSS, or code. Just describe what you want, and the model handles everything — discovering the skill, choosing the right theme and layout, structuring your content, and rendering the final HTML.

### The simplest way to start

Just describe the report you want:

```
Create a status report for the Q1 executive review covering our
three product lines: Cloud, Edge, and Mobile. Include KPIs for
revenue, customer count, and NPS. Flag any items that are behind target.
```

The model will:
1. Discover and load `skill.sandbox.html_report_builder`
2. Choose the `executive` theme (appropriate for exec review)
3. Use the `dashboard` layout (because you asked for KPIs)
4. Structure your content into metrics rows, tables, and status lists
5. Render the HTML and save it to your workspace

### Controlling every feature through your prompt

| Feature (see sections above) | How to request it in natural language |
|------------------------------|---------------------------------------|
| **Theme** (Section 2) | "Use the technical theme" / "Make it look modern" / "I want a clean minimal style" / "This is for the board" (→ executive) |
| **Layout** (Section 3) | "Format this as a dashboard" / "I need an executive brief with a cover page" / "Use a newsletter layout with a sidebar" |
| **Narrative sections** (Section 4) | "Write a section about..." / "Add an introduction covering..." |
| **Executive summary** (Section 4) | "Start with an executive summary of the key findings" |
| **Tables** (Section 4) | "Present the data as a table" / "Create a table and highlight anything over 100 in red" |
| **Status list** (Section 4) | "Create a status list with red/yellow/green indicators" / "Show a risk register" |
| **KPI metrics** (Section 4) | "Show KPIs for revenue, churn, and NPS with trend arrows" |
| **Charts** (Section 5) | "Include a bar chart showing sales by quarter" / "Add a pie chart of the distribution" / "Add a line chart with a target line at 85%" |
| **Callout** (Section 4) | "Highlight this as a warning" / "Add an important note" |
| **Comparison** (Section 4) | "Compare Option A and Option B side by side" |
| **Dividers** (Section 4) | "Add a section separator" / "Put a banner header before the next section" |
| **Page breaks** (Section 4) | "Start a new page here" (for PDF) |
| **Logo** (Section 6) | "Include our company logo" (must be uploaded first — see Section 6) |
| **Brand colors** (Section 6) | "Use our brand colors" / "Apply our company branding" (must be configured first — see Section 6) |
| **PDF** (Section 7) | "Also convert it to PDF" / "Give me both HTML and PDF versions" |
| **Confidentiality** | "Mark it as Confidential" / "Add Internal Use Only to the header" |

### Overriding auto-selections

If the model picks the wrong theme or layout:
- "Use the dashboard template instead"
- "Switch to the compliance theme"
- "I want the newsletter layout, not the standard one"

---

## 9. Example Prompts — From Simple to Advanced

These examples show how the features from Sections 2-7 come together in real prompts.

### Basic report

```
Write a project status report for the Alpha initiative. We're
70% complete, on budget, but 2 weeks behind schedule. Include
the key milestones table and highlight the ones that are late.
```

**What the model does:** Uses the `standard` layout and `executive` theme. Creates narrative sections, a table with `danger` highlighting on late milestones, and a `warning` callout box for the schedule risk.

---

### Executive brief with cover page

```
Create an executive brief for the board of directors summarizing
our FY26 Q1 performance. Use the executive theme. Include a cover
page with the title "Q1 FY26 Business Review". Show KPIs for
revenue ($42M, up 12%), active customers (1,847, up 8%), and
churn rate (2.1%, down). Then add sections for each business unit
with charts showing quarterly trends.
```

**What the model does:** Uses the `executive-brief` layout (triggered by cover page request). Creates a cover page, executive summary, `metrics_row` KPI cards with trend arrows, per-unit narrative sections, and `grouped_bar` charts for quarterly trends. Navy/gold `executive` theme.

---

### KPI dashboard

```
Build a performance dashboard with the technical theme. Show these
KPIs at the top: API uptime 99.97% (up), P95 latency 142ms (down,
good), error rate 0.03% (flat). Below that, add a line chart of
daily request volume for the past 30 days and a table of the top
10 endpoints by traffic.
```

**What the model does:** Uses the `dashboard` layout (triggered by KPIs). `metrics_row` strip at top with `success`/`danger` variants, `line` chart in the grid area, `table` with endpoint data below. Slate/cyan `technical` theme.

---

### Comparison analysis

```
Create a comparison report evaluating three vendors: Acme,
GlobalTech, and NovaSoft. Compare them on pricing, features,
support quality, and integration complexity. Use the modern theme.
Add a radar chart comparing their scores across all dimensions.
```

**What the model does:** Uses the `comparison` layout. Side-by-side `comparison` sections for each vendor pair, a `radar` chart with multi-dimensional scores, and the indigo/pink `modern` theme.

---

### Compliance / audit document

```
Generate a compliance audit report using the compliance theme.
Title: "SOC 2 Type II Readiness Assessment". Mark it as
Confidential. Include an executive summary of findings, a status
list of all 14 control areas with red/yellow/green ratings and
remediation actions, and a table of open findings sorted by severity.
```

**What the model does:** Uses the `standard` layout with `compliance` theme. Sets `confidentiality: "Confidential"` in metadata. Creates an `executive_summary`, a `status_list` with 14 color-badged items (each with an action), and a `table` with `danger`/`warning` cell highlighting by severity.

---

### Newsletter / multi-column layout

```
Create a monthly team newsletter. Use the modern theme and the
newsletter layout. The main content should cover: new product
launches, engineering wins, and upcoming events. Put team
spotlights and quick links in the sidebar.
```

**What the model does:** Uses the `newsletter` layout (explicitly requested). Hero header with title, 2/3 main column with narrative `section` types, 1/3 sidebar with `callout` cards for spotlights and links. `modern` theme.

---

### With brand identity

```
Create a quarterly business review report for Contoso Corp. Use
our brand identity (logo and colors). Include revenue charts,
customer growth metrics, and a risk register. Mark it as
Internal — Board Only.
```

**What the model does:** Detects `brand/config.json` and applies Contoso's logo, color overrides, and footer text on top of the selected theme. Creates `chart` sections for revenue, `metrics_row` for customer growth, and a `status_list` for the risk register.

**Prerequisite:** Brand config must be set up first — see Section 6.

---

### Multi-step composition

```
First, research the competitive landscape for AI code assistants
using web research. Then, take those findings and produce a
professional executive brief with a cover page, charts comparing
market share, and a recommendation section.
```

**What the model does:** The planner creates two steps: (1) `web-research` skill gathers evidence, (2) `html-report-generator` takes the research output and produces the executive brief with `chart` and `comparison` sections.

---

## 10. Customization Quick Reference for Admins

### Where files live

All skill files are stored in R2 and materialized to the sandbox at runtime. The paths below are relative to the skill's root directory.

| Path | Purpose | Editable by |
|------|---------|-------------|
| `SKILL.md` | Skill instructions (model reads this) | Admin only |
| `scripts/render_report.py` | HTML renderer (620 lines) | Admin only |
| `scripts/validate_report.py` | Output validator | Admin only |
| `scripts/html_to_pdf.py` | PDF converter | Admin only |
| `assets/base.css` | Global component styles (~450 lines) | Admin only |
| `assets/themes/*.css` | Theme CSS files (5 built-in) | Admin (platform themes) |
| `assets/theme-manifest.json` | Theme catalog (model reads this to discover themes) | Admin |
| `assets/lib/chart.min.js` | Chart.js 4.4.7 library (201KB) | Admin only |
| `assets/templates/*.html` | Jinja2 layout templates (5 built-in) | Admin only |
| `brand/config.json` | Brand identity config | Workspace admin |
| `brand/logo.*` | Company logo file | Workspace admin |
| `references/content-schema.json` | JSON Schema for content contract | Admin only |
| `references/theme-contract.md` | CSS variable contract for custom themes | Admin only |

### How to add a brand identity for a tenant

1. **Navigate** to the Skills admin panel in the UI
2. **Find** `skill.sandbox.html_report_builder` in the skills list
3. **Create a new version** (draft) from the published version
4. **Upload** the logo file to `brand/` (e.g., `brand/acme-logo.png`)
5. **Create** `brand/config.json` with the brand settings (see Section 6)
6. **Promote** the draft to publish the new version

The next operator run that uses this skill will automatically pick up the new brand config.

### How to add a custom theme for a tenant

1. **Create** your CSS theme file following the [Theme Contract](references/theme-contract.md)
2. **Upload** the CSS file to `assets/themes/` in the skill's files (e.g., `assets/themes/acme.css`)
3. **Update** `assets/theme-manifest.json` to add your theme entry
4. **Promote** the draft to publish

Now the model can discover and use your theme by name.

### How to update the theme manifest

The theme manifest is what the model reads at runtime to discover available themes. When you add or remove a theme, update this file.

```json
{
  "default_theme": "executive",
  "themes": [
    {
      "id": "executive",
      "name": "Executive",
      "description": "Conservative, authoritative. Navy/gold palette with serif headings.",
      "source": "platform",
      "character": "formal"
    },
    {
      "id": "acme",
      "name": "Acme Brand",
      "description": "Acme Corp brand identity with Atlassian-inspired colors.",
      "source": "tenant",
      "character": "professional"
    }
  ]
}
```

| Field | Purpose |
|-------|---------|
| `id` | Must match the CSS filename without extension (e.g., `acme` for `acme.css`) |
| `name` | Display name used by the model when selecting themes |
| `description` | Helps the model choose the right theme — be specific about the look and feel |
| `source` | `"platform"` for built-in themes, `"tenant"` for custom/org themes |
| `character` | `"formal"`, `"professional"`, `"casual"`, or `"neutral"` — helps the model match tone to request |

---

## 11. Composition with Other Skills

The HTML report generator is designed to be the **final output step** in multi-skill pipelines:

| Pipeline | Skills Involved | What Happens |
|----------|----------------|--------------|
| **Research → Report** | `web-research` → `html-report-generator` | Web evidence gathered, then synthesized into an executive brief |
| **Data → Dashboard** | Sandbox code execution → `html-report-generator` | CSV/data processed, then rendered as KPI dashboard with charts |
| **Investigation → Document** | Investigation skills → `html-report-generator` | Findings analyzed, then formatted as incident/compliance report |
| **Report → Multi-format** | `html-report-generator` → `html_to_pdf.py` / `document-converter` | HTML produced first, then converted to PDF and/or DOCX |

---

## 12. Troubleshooting

| Problem | Cause | Fix |
|---------|-------|-----|
| Report doesn't use my brand | `brand/config.json` missing or not promoted | Verify file exists in Admin UI > Skills > Files tab. Ensure version is promoted (not draft). |
| Wrong theme was chosen | Model inferred from context | Be explicit: "Use the technical theme" overrides auto-selection |
| Custom theme not available | Not registered in manifest | Check `theme-manifest.json` includes your theme. Verify CSS file exists at `assets/themes/{id}.css` |
| Charts aren't rendering | No JavaScript in email clients | Charts render in browsers. For email, convert to PDF first (PDF preserves chart appearance). |
| PDF layout issues | Wide tables or wrong orientation | Ask for "landscape PDF" for wide content. Use `page_break` sections to control boundaries. |
| Skill wasn't discovered | Prompt doesn't signal report generation | Use words like "create a report", "produce a dashboard", "generate an executive brief" in your prompt |
| Logo not appearing | Path mismatch in `config.json` | Verify `logo` path matches the actual filename (e.g., `brand/logo.png` not `brand/Logo.PNG`) |

---

## 13. Quick Reference Card

```
FEATURES                          OPTIONS AVAILABLE
──────────────────────────────────────────────────────────────
Themes (Section 2)                executive, technical, compliance, modern, minimal, [custom]
Layouts (Section 3)               standard, executive-brief, dashboard, comparison, newsletter
Section types (Section 4)         section, executive_summary, table, status_list, metrics_row,
                                  chart, callout, comparison, divider, page_break
Chart types (Section 5)           bar, grouped_bar, stacked_bar, horizontal_bar, line, area,
                                  pie, doughnut, radar
Brand (Section 6)                 logo + color_overrides + font_overrides in brand/config.json
PDF (Section 7)                   A4/Letter, portrait/landscape, custom margins


NATURAL LANGUAGE QUICK GUIDE      WHAT TO SAY
──────────────────────────────────────────────────────────────
Standard report                   "Create a report about..."
Executive brief + cover page      "Create an executive brief with a cover page"
KPI dashboard                     "Build a dashboard with metrics and charts"
Comparison                        "Compare X and Y side by side"
Newsletter layout                 "Use the newsletter layout with a sidebar"

Theme: executive                  "Use the executive theme" (or just ask for formal)
Theme: technical                  "Use the technical theme" (or "make it technical")
Theme: compliance                 "Use the compliance theme" (or "audit-ready")
Theme: modern                     "Use the modern theme" (or "friendly and vibrant")
Theme: minimal                    "Use the minimal theme" (or "clean and simple")
Theme: custom                     "Use the [name] theme" (if registered)

Brand identity                    "Include our company branding"
Logo                              "Include our logo" (must be uploaded first)
PDF version                       "Also convert to PDF" or "Give me a PDF"
Confidential                      "Mark as Confidential"

Charts                            "Add a [type] chart showing [data]"
KPIs                              "Show KPIs for [metrics] with trends"
Tables                            "Present as a table, highlight [condition] in red"
Status list                       "List with red/yellow/green status indicators"
Callout                           "Highlight this as a warning / important note"
```

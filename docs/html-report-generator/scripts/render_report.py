#!/usr/bin/env python3
"""
render_report.py v2 — Template-driven HTML report generator.

Generates a self-contained HTML report from structured content JSON using:
- Jinja2 layout templates (standard, executive-brief, dashboard, comparison, newsletter)
- CSS custom property themes (executive, technical, compliance, modern, minimal, or custom)
- Optional brand config (logo, color overrides, font overrides)
- Programmatic Chart.js charts from data
- Markdown → HTML conversion for all body fields

Usage:
    python3 render_report.py --content content.json --output report.html
    python3 render_report.py --content content.json --theme modern --output report.html
    python3 render_report.py --content content.json --theme executive --brand brand.json --output report.html
    python3 render_report.py --content content.json --template dashboard --theme technical --output report.html
"""

import argparse
import base64
import json
import os
import re
import sys
import uuid
from datetime import date
from pathlib import Path

# ---------------------------------------------------------------------------
# Path resolution
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).parent
SKILL_ROOT = SCRIPT_DIR.parent
ASSETS_DIR = SKILL_ROOT / 'assets'
TEMPLATES_DIR = ASSETS_DIR / 'templates'
THEMES_DIR = ASSETS_DIR / 'themes'
LIB_DIR = ASSETS_DIR / 'lib'

# ---------------------------------------------------------------------------
# Markdown → HTML conversion
# ---------------------------------------------------------------------------

def _looks_like_html(text: str) -> bool:
    """Detect whether text is already HTML rather than markdown.

    Returns True if the text contains block-level HTML tags that would be
    corrupted by markdown conversion (wrapped in <p> tags, entities escaped).
    This is a safety net — the model SHOULD use structured section types
    instead of embedding raw HTML in body fields, but if it does, we must
    not double-convert.
    """
    stripped = text.strip()
    # Starts with an HTML tag
    if re.match(r'^<(?:div|table|ul|ol|p|h[1-6]|section|article|nav|header|footer|figure|details|dl|blockquote|form|pre)\b', stripped, re.IGNORECASE):
        return True
    # Contains multiple block-level HTML tags (not just inline <strong>/<em>)
    block_tags = re.findall(r'<(?:div|table|thead|tbody|tr|td|th|ul|ol|li|p|h[1-6]|section|article|figure|details|dl|dd|dt|blockquote|pre|hr|br)\b', stripped, re.IGNORECASE)
    if len(block_tags) >= 3:
        return True
    return False


def markdown_to_html(text: str) -> str:
    """Convert markdown text to HTML.

    If the text already contains block-level HTML, it is returned as-is to
    prevent corruption from markdown conversion (which would wrap block
    elements in <p> tags and break layouts).

    Attempts to use the `markdown` library if available.
    Falls back to a lightweight pure-Python converter.
    """
    if not text or not text.strip():
        return ''

    # Safety net: if the body is already HTML, pass it through unchanged.
    # The model SHOULD use structured section types (table, callout, etc.)
    # instead of raw HTML, but if it doesn't, this prevents double-conversion.
    if _looks_like_html(text):
        return text

    try:
        import markdown
        return markdown.markdown(
            text,
            extensions=['tables', 'fenced_code', 'nl2br', 'sane_lists'],
        )
    except ImportError:
        return _fallback_markdown(text)


def _fallback_markdown(text: str) -> str:
    """Lightweight markdown converter for environments without the markdown lib.

    Handles: bold, italic, headers, unordered/ordered lists, code blocks,
    blockquotes, horizontal rules, and paragraphs.
    """
    lines = text.split('\n')
    html_parts = []
    in_list = None  # 'ul' or 'ol'
    in_code = False
    in_blockquote = False
    paragraph = []

    def flush_paragraph():
        if paragraph:
            text = '<br>\n'.join(paragraph)
            text = _inline_format(text)
            html_parts.append(f'<p>{text}</p>')
            paragraph.clear()

    def flush_list():
        nonlocal in_list
        if in_list:
            html_parts.append(f'</{in_list}>')
            in_list = None

    def flush_blockquote():
        nonlocal in_blockquote
        if in_blockquote:
            html_parts.append('</blockquote>')
            in_blockquote = False

    for line in lines:
        stripped = line.strip()

        # Fenced code blocks
        if stripped.startswith('```'):
            if in_code:
                html_parts.append('</code></pre>')
                in_code = False
            else:
                flush_paragraph()
                flush_list()
                flush_blockquote()
                lang = stripped[3:].strip()
                html_parts.append(f'<pre><code class="language-{lang}">' if lang else '<pre><code>')
                in_code = True
            continue

        if in_code:
            html_parts.append(line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'))
            continue

        # Empty line
        if not stripped:
            flush_paragraph()
            flush_list()
            flush_blockquote()
            continue

        # Headings
        heading_match = re.match(r'^(#{1,6})\s+(.+)$', stripped)
        if heading_match:
            flush_paragraph()
            flush_list()
            flush_blockquote()
            level = len(heading_match.group(1))
            content = _inline_format(heading_match.group(2))
            html_parts.append(f'<h{level}>{content}</h{level}>')
            continue

        # Horizontal rule
        if re.match(r'^[-*_]{3,}\s*$', stripped):
            flush_paragraph()
            flush_list()
            flush_blockquote()
            html_parts.append('<hr>')
            continue

        # Blockquote
        if stripped.startswith('>'):
            flush_paragraph()
            flush_list()
            if not in_blockquote:
                html_parts.append('<blockquote>')
                in_blockquote = True
            content = _inline_format(stripped[1:].strip())
            html_parts.append(f'<p>{content}</p>')
            continue
        elif in_blockquote:
            flush_blockquote()

        # Unordered list
        ul_match = re.match(r'^[\-\*\+]\s+(.+)$', stripped)
        if ul_match:
            flush_paragraph()
            flush_blockquote()
            if in_list != 'ul':
                flush_list()
                html_parts.append('<ul>')
                in_list = 'ul'
            content = _inline_format(ul_match.group(1))
            html_parts.append(f'<li>{content}</li>')
            continue

        # Ordered list
        ol_match = re.match(r'^\d+\.\s+(.+)$', stripped)
        if ol_match:
            flush_paragraph()
            flush_blockquote()
            if in_list != 'ol':
                flush_list()
                html_parts.append('<ol>')
                in_list = 'ol'
            content = _inline_format(ol_match.group(1))
            html_parts.append(f'<li>{content}</li>')
            continue

        # Regular paragraph line
        if in_list:
            flush_list()
        paragraph.append(stripped)

    flush_paragraph()
    flush_list()
    flush_blockquote()
    if in_code:
        html_parts.append('</code></pre>')

    return '\n'.join(html_parts)


def _inline_format(text: str) -> str:
    """Apply inline markdown formatting: bold, italic, code, links."""
    # Code (backticks) — must come first to avoid inner formatting
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    # Bold + italic
    text = re.sub(r'\*\*\*(.+?)\*\*\*', r'<strong><em>\1</em></strong>', text)
    # Bold
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    # Italic
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    # Links
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
    return text

# ---------------------------------------------------------------------------
# Theme loading
# ---------------------------------------------------------------------------

def load_theme_css(theme_name: str) -> str:
    """Load a theme CSS file by name."""
    theme_path = THEMES_DIR / f'{theme_name}.css'
    if theme_path.exists():
        return theme_path.read_text(encoding='utf-8')
    # Check if default exists
    default_path = THEMES_DIR / 'executive.css'
    if default_path.exists():
        return default_path.read_text(encoding='utf-8')
    return '/* No theme loaded */'


def parse_theme_colors(theme_css: str) -> dict:
    """Extract CSS variable values from theme CSS for chart color resolution."""
    colors = {}
    for match in re.finditer(r'--color-([\w-]+)\s*:\s*([^;]+);', theme_css):
        colors[match.group(1)] = match.group(2).strip()
    return colors

# ---------------------------------------------------------------------------
# Brand config
# ---------------------------------------------------------------------------

def load_brand_config(brand_path: str) -> dict:
    """Load brand configuration JSON."""
    if not brand_path or not os.path.exists(brand_path):
        return {}
    with open(brand_path, encoding='utf-8') as f:
        return json.load(f)


def build_brand_css(brand: dict) -> str:
    """Build CSS variable overrides from brand config."""
    if not brand:
        return ''

    overrides = []
    for key, value in brand.get('color_overrides', {}).items():
        overrides.append(f'  --color-{key}: {value};')
    for key, value in brand.get('font_overrides', {}).items():
        overrides.append(f'  --font-{key}: {value};')

    if not overrides:
        return ''

    return ':root {\n' + '\n'.join(overrides) + '\n}'


def build_brand_logo_html(brand: dict) -> str:
    """Build logo HTML from brand config, base64-encoding the image."""
    logo_path_raw = brand.get('logo', '')
    if not logo_path_raw:
        return ''

    # Resolve relative to skill root
    logo_path = SKILL_ROOT / logo_path_raw
    if not logo_path.exists():
        # Try absolute path
        logo_path = Path(logo_path_raw)
    if not logo_path.exists():
        return f'<!-- Logo not found: {logo_path_raw} -->'

    ext = logo_path.suffix.lower()
    mime_map = {
        '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
        '.gif': 'image/gif', '.svg': 'image/svg+xml', '.webp': 'image/webp',
    }
    mime = mime_map.get(ext, 'image/png')

    if ext == '.svg':
        svg_content = logo_path.read_text(encoding='utf-8')
        return f'<div class="logo">{svg_content}</div>'

    b64 = base64.b64encode(logo_path.read_bytes()).decode()
    company = brand.get('company_name', 'Logo')
    position = brand.get('logo_position', 'header')
    cls = 'logo logo-right' if position == 'header' else 'logo'
    return f'<img src="data:{mime};base64,{b64}" alt="{company}" class="{cls}">'

# ---------------------------------------------------------------------------
# Template inference
# ---------------------------------------------------------------------------

def infer_template(content: dict) -> str:
    """Infer the best layout template from content structure."""
    has_cover = bool(content.get('cover'))
    section_types = {s.get('type') for s in content.get('sections', [])}
    has_metrics = 'metrics_row' in section_types
    has_comparison = 'comparison' in section_types

    if has_cover and has_metrics:
        return 'executive-brief'
    if has_cover:
        return 'executive-brief'
    if has_metrics and not has_cover:
        return 'dashboard'
    if has_comparison:
        return 'comparison'
    return 'standard'

# ---------------------------------------------------------------------------
# Section renderers
# ---------------------------------------------------------------------------

def _wrap_bare_tables(html: str) -> str:
    """Wrap any <table> not already inside a .table-wrapper div.

    This is a post-processing safety net for cases where the model passes
    raw HTML containing <table> elements through a section body.
    """
    # Skip if no tables
    if '<table' not in html:
        return html

    # Find <table...>...</table> blocks NOT preceded by table-wrapper
    def _wrap_match(m):
        # Check if already wrapped (look back for table-wrapper in preceding 200 chars)
        start = max(0, m.start() - 200)
        preceding = html[start:m.start()]
        if 'table-wrapper' in preceding:
            return m.group(0)
        return f'<div class="table-wrapper">{m.group(0)}</div>'

    return re.sub(r'<table\b[^>]*>.*?</table>', _wrap_match, html, flags=re.DOTALL)


def render_section_text(section: dict) -> str:
    """Render a 'section' type — heading + markdown body."""
    parts = []
    heading = section.get('heading', '')
    level = section.get('level', 1)
    level = max(1, min(3, level))

    if heading:
        parts.append(f'<h{level}>{heading}</h{level}>')

    body = section.get('body', '')
    if body:
        rendered = markdown_to_html(body)
        # Post-process: wrap any bare <table> elements for overflow containment
        rendered = _wrap_bare_tables(rendered)
        parts.append(rendered)

    return '\n'.join(parts)


def render_executive_summary(section: dict) -> str:
    """Render an 'executive_summary' type."""
    body = section.get('body', '')
    html_body = markdown_to_html(body)
    return f'<div class="executive-summary">\n{html_body}\n</div>'


def render_table(section: dict) -> str:
    """Render a 'table' type with conditional styling and footnotes."""
    parts = []
    heading = section.get('heading', '')
    level = section.get('level', 2)

    if heading:
        parts.append(f'<h{level}>{heading}</h{level}>')

    caption = section.get('caption', '')
    if caption:
        parts.append(f'<p class="table-caption">{caption}</p>')

    columns = section.get('columns', [])
    rows = section.get('rows', [])
    highlight_rules = section.get('highlight_rules', {})
    row_styles = section.get('row_styles', {})

    parts.append('<div class="table-wrapper">')
    parts.append('<table class="data-table">')

    # Header
    if columns:
        parts.append('<thead><tr>')
        for col in columns:
            parts.append(f'<th>{col}</th>')
        parts.append('</tr></thead>')

    # Body
    parts.append('<tbody>')
    for row in rows:
        # Check if this row has a row_style
        row_class = ''
        if row and columns:
            first_cell = str(row[0]) if row else ''
            if first_cell in row_styles:
                row_class = f' class="row-{row_styles[first_cell]}"'

        parts.append(f'<tr{row_class}>')
        for i, cell in enumerate(row):
            cell_str = str(cell)
            td_class = ''

            # Apply highlight rules
            if columns and i < len(columns):
                col_name = columns[i]
                col_rules = highlight_rules.get(col_name, {})
                if cell_str in col_rules:
                    variant = col_rules[cell_str]
                    td_class = f' class="cell-{variant}"'

            parts.append(f'<td{td_class}>{cell_str}</td>')
        parts.append('</tr>')
    parts.append('</tbody></table>')
    parts.append('</div>')

    # Footnotes
    footnotes = section.get('footnotes', [])
    if footnotes:
        parts.append('<div class="table-footnotes">')
        for fn in footnotes:
            parts.append(f'<p>{fn}</p>')
        parts.append('</div>')

    return '\n'.join(parts)


def render_status_list(section: dict) -> str:
    """Render a 'status_list' type with color badges."""
    parts = []
    heading = section.get('heading', '')
    level = section.get('level', 1)

    if heading:
        parts.append(f'<h{level}>{heading}</h{level}>')

    parts.append('<div class="status-list">')
    for item in section.get('items', []):
        name = item.get('name', '')
        status = item.get('status', 'gray')
        summary = item.get('summary', '')
        action = item.get('action', '')

        parts.append('<div class="status-item">')
        parts.append('<div class="status-item-header">')
        parts.append(f'<span class="status-badge status-{status}">{status}</span>')
        parts.append(f'<span class="status-item-name">{name}</span>')
        parts.append('</div>')

        if summary:
            parts.append(f'<p class="status-item-summary">{summary}</p>')

        if action:
            parts.append(f'<div class="status-item-action"><strong>Action:</strong> {action}</div>')

        parts.append('</div>')
    parts.append('</div>')

    return '\n'.join(parts)


def render_metrics_row(section: dict) -> str:
    """Render a 'metrics_row' type — KPI strip."""
    parts = []
    heading = section.get('heading', '')
    level = section.get('level', 2)

    if heading:
        parts.append(f'<h{level}>{heading}</h{level}>')

    parts.append('<div class="metrics-row">')
    for m in section.get('metrics', []):
        value = m.get('value', '')
        label = m.get('label', '')
        trend = m.get('trend', '')
        variant = m.get('variant', '')
        percentage = m.get('percentage', '')

        card_class = 'metric-card'
        if variant:
            card_class += f' metric-card-{variant}'

        trend_html = ''
        if trend == 'up':
            trend_html = '<span class="metric-trend metric-trend-up">&#8593;</span>'
        elif trend == 'down':
            trend_html = '<span class="metric-trend metric-trend-down">&#8595;</span>'
        elif trend == 'flat':
            trend_html = '<span class="metric-trend metric-trend-flat">&#8594;</span>'

        pct_html = f'<span class="metric-pct">{percentage}</span>' if percentage else ''

        parts.append(f'<div class="{card_class}">')
        parts.append(f'<span class="metric-value">{value}{trend_html}</span>')
        parts.append(f'<span class="metric-label">{label}</span>')
        if pct_html:
            parts.append(pct_html)
        parts.append('</div>')
    parts.append('</div>')

    return '\n'.join(parts)


def render_chart(section: dict, theme_colors: dict) -> tuple:
    """Render a 'chart' type — returns (placeholder_html, chart_script).

    The placeholder HTML contains a <canvas>. The chart_script is JS
    that initializes Chart.js on that canvas. Scripts are collected and
    injected at end of body to ensure DOM is ready.
    """
    chart_id = f'chart-{uuid.uuid4().hex[:8]}'
    chart_type_raw = section.get('chart_type', 'bar')
    data = section.get('data', {})
    options = section.get('options', {})
    heading = section.get('heading', '')
    caption = section.get('caption', '')
    level = section.get('level', 2)

    # Map our chart types to Chart.js types
    chartjs_type_map = {
        'bar': 'bar',
        'grouped_bar': 'bar',
        'stacked_bar': 'bar',
        'horizontal_bar': 'bar',
        'line': 'line',
        'area': 'line',
        'pie': 'pie',
        'doughnut': 'doughnut',
        'radar': 'radar',
    }
    chartjs_type = chartjs_type_map.get(chart_type_raw, 'bar')

    # Resolve semantic colors
    def resolve_color(name: str) -> str:
        fallbacks = {
            'primary': '#1B2A4A', 'secondary': '#C9A962', 'accent': '#3D7EAA',
            'success': '#27AE60', 'warning': '#F39C12', 'danger': '#E74C3C',
        }
        if name in theme_colors:
            return theme_colors[name]
        return fallbacks.get(name, name)  # Return raw value if not a semantic name

    # Build datasets
    datasets_js = []

    # Check if simplified format (pie/doughnut)
    if 'values' in data and 'datasets' not in data:
        colors = data.get('colors', ['primary', 'secondary', 'accent', 'success', 'warning', 'danger'])
        resolved_colors = [resolve_color(c) for c in colors[:len(data['values'])]]
        datasets_js.append({
            'data': data['values'],
            'backgroundColor': resolved_colors,
            'borderWidth': 1,
        })
    else:
        for ds in data.get('datasets', []):
            color = resolve_color(ds.get('color', 'primary'))
            ds_obj = {
                'label': ds.get('label', ''),
                'data': ds.get('values', []),
                'backgroundColor': color + 'CC',  # 80% opacity
                'borderColor': color,
                'borderWidth': 1,
            }
            if chart_type_raw == 'area':
                ds_obj['fill'] = True
            if chart_type_raw == 'line' or chart_type_raw == 'area':
                ds_obj['tension'] = 0.3
                ds_obj['pointRadius'] = 4
            datasets_js.append(ds_obj)

    # Build Chart.js config
    config = {
        'type': chartjs_type,
        'data': {
            'labels': data.get('labels', []),
            'datasets': datasets_js,
        },
        'options': {
            'responsive': True,
            'maintainAspectRatio': True,
            'plugins': {
                'legend': {
                    'position': options.get('legend_position', 'top'),
                },
            },
        },
    }

    # Stacked bar
    if chart_type_raw == 'stacked_bar':
        config['options']['scales'] = {
            'x': {'stacked': True},
            'y': {'stacked': True},
        }

    # Horizontal bar
    if chart_type_raw == 'horizontal_bar':
        config['options']['indexAxis'] = 'y'

    # Y-axis label
    if options.get('y_axis_label'):
        config['options'].setdefault('scales', {}).setdefault('y', {})['title'] = {
            'display': True,
            'text': options['y_axis_label'],
        }

    # X-axis label
    if options.get('x_axis_label'):
        config['options'].setdefault('scales', {}).setdefault('x', {})['title'] = {
            'display': True,
            'text': options['x_axis_label'],
        }

    # Target line (annotation via plugin or manual)
    target_line_js = ''
    if options.get('target_line') is not None:
        target_val = options['target_line']
        target_label = options.get('target_label', f'Target ({target_val})')
        # Use a simple approach: add a dataset that looks like a line
        config['data']['datasets'].append({
            'label': target_label,
            'data': [target_val] * len(data.get('labels', [])),
            'type': 'line',
            'borderColor': resolve_color('danger'),
            'borderDash': [6, 4],
            'borderWidth': 2,
            'pointRadius': 0,
            'fill': False,
        })

    config_json = json.dumps(config, ensure_ascii=False)

    # Chart init script
    script = f"""(function() {{
  var ctx = document.getElementById('{chart_id}');
  if (ctx) {{ new Chart(ctx, {config_json}); }}
}})();"""

    # HTML placeholder
    html_parts = []
    if heading:
        html_parts.append(f'<h{level}>{heading}</h{level}>')
    html_parts.append(f'<figure class="chart-container">')
    html_parts.append(f'  <canvas id="{chart_id}"></canvas>')
    html_parts.append(f'</figure>')
    if caption:
        html_parts.append(f'<p class="chart-caption">{caption}</p>')

    return '\n'.join(html_parts), script


def render_callout(section: dict) -> str:
    """Render a 'callout' type."""
    variant = section.get('variant', 'info')
    title = section.get('title', '')
    body = section.get('body', '')

    cls = f'callout callout-{variant}'
    parts = [f'<div class="{cls}">']
    if title:
        parts.append(f'<div class="callout-title">{title}</div>')
    if body:
        parts.append(markdown_to_html(body))
    parts.append('</div>')

    return '\n'.join(parts)


def render_comparison(section: dict) -> str:
    """Render a 'comparison' type — side-by-side columns."""
    parts = []
    heading = section.get('heading', '')
    level = section.get('level', 2)

    if heading:
        parts.append(f'<h{level}>{heading}</h{level}>')

    left = section.get('left', {})
    right = section.get('right', {})

    parts.append('<div class="comparison-container">')

    # Left column
    parts.append('<div class="comparison-col">')
    if left.get('heading'):
        parts.append(f'<h3>{left["heading"]}</h3>')
    if left.get('body'):
        parts.append(markdown_to_html(left['body']))
    parts.append('</div>')

    # Right column
    parts.append('<div class="comparison-col">')
    if right.get('heading'):
        parts.append(f'<h3>{right["heading"]}</h3>')
    if right.get('body'):
        parts.append(markdown_to_html(right['body']))
    parts.append('</div>')

    parts.append('</div>')

    return '\n'.join(parts)


def render_divider(section: dict) -> str:
    """Render a 'divider' type."""
    style = section.get('style', 'line')
    text = section.get('text', '')

    if style == 'banner' and text:
        return f'<div class="section-banner">{text}</div>'
    return '<hr class="section-divider">'


def render_page_break(section: dict) -> str:
    """Render a 'page_break' type."""
    return '<div class="page-break"></div>'

# ---------------------------------------------------------------------------
# Section dispatcher
# ---------------------------------------------------------------------------

SECTION_RENDERERS = {
    'section': render_section_text,
    'text': render_section_text,  # backward compat alias
    'executive_summary': render_executive_summary,
    'table': render_table,
    'status_list': render_status_list,
    'metrics_row': render_metrics_row,
    # 'chart' handled separately (needs theme_colors)
    'callout': render_callout,
    'comparison': render_comparison,
    'divider': render_divider,
    'page_break': render_page_break,
}


def render_all_sections(sections: list, theme_colors: dict, template_name: str) -> dict:
    """Render all sections and return organized HTML fragments.

    Returns dict with:
        sections_html: all sections as HTML (for standard/comparison templates)
        executive_summary_html: extracted exec summary (for executive-brief/newsletter)
        kpi_strip_html: extracted metrics rows (for dashboard template)
        grid_items_html: charts + tables for dashboard grid
        sidebar_html: callouts + status lists for newsletter sidebar
        chart_scripts: all Chart.js init scripts concatenated
    """
    all_html = []
    exec_summary_html = ''
    kpi_strips = []
    grid_items = []
    sidebar_items = []
    chart_scripts = []

    for section in sections:
        section_type = section.get('type', 'section')

        # Charts are special — they return (html, script)
        if section_type == 'chart':
            html, script = render_chart(section, theme_colors)
            chart_scripts.append(script)

            if template_name == 'dashboard':
                grid_items.append(f'<div class="dashboard-grid-item">{html}</div>')
            else:
                all_html.append(html)
            continue

        # Executive summary extraction
        if section_type == 'executive_summary':
            exec_summary_html = render_executive_summary(section)
            if template_name in ('standard', 'dashboard'):
                all_html.append(exec_summary_html)
            continue

        # Metrics row extraction for dashboard
        if section_type == 'metrics_row' and template_name == 'dashboard':
            kpi_strips.append(render_metrics_row(section))
            continue

        # Tables in dashboard go to grid
        if section_type == 'table' and template_name == 'dashboard':
            grid_items.append(f'<div class="dashboard-grid-item dashboard-full-width">{render_table(section)}</div>')
            continue

        # Newsletter sidebar: callouts and status_lists
        if template_name == 'newsletter' and section_type in ('callout', 'status_list'):
            renderer = SECTION_RENDERERS.get(section_type)
            if renderer:
                sidebar_items.append(
                    f'<div class="newsletter-sidebar-card">{renderer(section)}</div>'
                )
            continue

        # Default rendering
        renderer = SECTION_RENDERERS.get(section_type)
        if renderer:
            all_html.append(renderer(section))
        else:
            all_html.append(f'<!-- Unknown section type: {section_type} -->')

    return {
        'sections_html': '\n\n'.join(all_html),
        'executive_summary_html': exec_summary_html,
        'kpi_strip_html': '\n'.join(kpi_strips),
        'grid_items_html': '\n'.join(grid_items),
        'sidebar_html': '\n'.join(sidebar_items),
        'chart_scripts': '\n'.join(chart_scripts),
    }

# ---------------------------------------------------------------------------
# Jinja2 template rendering
# ---------------------------------------------------------------------------

def load_jinja_template(template_name: str) -> str:
    """Load a Jinja2 template file by name."""
    template_path = TEMPLATES_DIR / f'{template_name}.html'
    if not template_path.exists():
        # Fall back to standard
        template_path = TEMPLATES_DIR / 'standard.html'
    if not template_path.exists():
        raise FileNotFoundError(f'Template not found: {template_name} (checked {template_path})')
    return template_path.read_text(encoding='utf-8')


def render_template(template_str: str, context: dict) -> str:
    """Render a Jinja2 template string with context.

    Uses Jinja2 if available, falls back to simple string replacement.
    """
    try:
        from jinja2 import Environment, BaseLoader
        env = Environment(loader=BaseLoader(), autoescape=False)
        template = env.from_string(template_str)
        return template.render(**context)
    except ImportError:
        # Fallback: simple variable replacement
        result = template_str
        for key, value in context.items():
            if isinstance(value, str):
                result = result.replace('{{ ' + key + ' }}', value)
                result = result.replace('{{' + key + '}}', value)
        # Strip remaining Jinja2 blocks
        result = re.sub(r'\{%.*?%\}', '', result, flags=re.DOTALL)
        result = re.sub(r'\{\{.*?\}\}', '', result)
        return result

# ---------------------------------------------------------------------------
# Main report generation
# ---------------------------------------------------------------------------

def generate_report(content: dict, theme_name: str, template_name: str | None,
                    brand_path: str | None) -> str:
    """Generate the complete self-contained HTML report."""

    # Load CSS layers
    base_css = ''
    base_path = ASSETS_DIR / 'base.css'
    if base_path.exists():
        base_css = base_path.read_text(encoding='utf-8')

    theme_css = load_theme_css(theme_name)
    theme_colors = parse_theme_colors(theme_css)

    # Brand
    brand = load_brand_config(brand_path) if brand_path else {}
    brand_css = build_brand_css(brand)
    brand_logo_html = build_brand_logo_html(brand)

    # Also merge brand color overrides into theme_colors for chart resolution
    for key, value in brand.get('color_overrides', {}).items():
        theme_colors[key] = value

    # Template selection
    if not template_name:
        template_name = infer_template(content)

    # Build metadata context
    metadata = content.get('metadata', {})
    if not metadata.get('title') and content.get('title'):
        metadata['title'] = content['title']  # backward compat
    if not metadata.get('date'):
        metadata['date'] = date.today().isoformat()

    meta_parts = []
    if metadata.get('date'):
        meta_parts.append(metadata['date'])
    if metadata.get('author'):
        meta_parts.append(metadata['author'])
    if metadata.get('version'):
        meta_parts.append(f'v{metadata["version"]}')
    meta_line = ' | '.join(meta_parts)

    # Footer
    footer_text = brand.get('footer_text', '') or content.get('footer', '')

    # Chart.js library (conditional)
    sections = content.get('sections', [])
    has_charts = any(s.get('type') == 'chart' for s in sections)
    chartjs_code = ''
    if has_charts:
        chartjs_path = LIB_DIR / 'chart.min.js'
        if chartjs_path.exists():
            chartjs_code = chartjs_path.read_text(encoding='utf-8')

    # Render sections
    rendered = render_all_sections(sections, theme_colors, template_name)

    # Load and render template
    template_str = load_jinja_template(template_name)

    context = {
        'metadata': metadata,
        'meta_line': meta_line,
        'cover': content.get('cover', {}),
        'footer_text': footer_text,
        'base_css': base_css,
        'theme_css': theme_css,
        'brand_css': brand_css,
        'brand_logo_html': brand_logo_html,
        'chartjs_code': chartjs_code,
        'sections_html': rendered['sections_html'],
        'executive_summary_html': rendered['executive_summary_html'],
        'kpi_strip_html': rendered['kpi_strip_html'],
        'grid_items_html': rendered['grid_items_html'],
        'sidebar_html': rendered['sidebar_html'],
        'chart_scripts': rendered['chart_scripts'],
    }

    return render_template(template_str, context)


def main():
    parser = argparse.ArgumentParser(description='Generate a self-contained HTML report (v2)')
    parser.add_argument('--content', required=True, help='Path to content.json')
    parser.add_argument('--output', required=True, help='Output HTML file path')
    parser.add_argument('--theme', default='executive', help='Theme name (default: executive)')
    parser.add_argument('--template', default=None, help='Layout template override (auto-inferred if omitted)')
    parser.add_argument('--brand', default=None, help='Path to brand config JSON')
    args = parser.parse_args()

    # Load content
    try:
        with open(args.content, encoding='utf-8') as f:
            content = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(json.dumps({'status': 'error', 'error': str(e)}))
        sys.exit(1)

    # Allow content-level overrides
    theme = args.theme
    if content.get('theme'):
        theme = content['theme']

    template = args.template
    if content.get('template'):
        template = content['template']

    brand_path = args.brand
    if content.get('brand'):
        brand_path = content['brand']

    # Generate
    try:
        html = generate_report(content, theme, template, brand_path)
    except Exception as e:
        print(json.dumps({'status': 'error', 'error': str(e)}))
        sys.exit(1)

    # Write output
    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(html)

    # Determine actual template used
    actual_template = template or infer_template(content)

    print(json.dumps({
        'status': 'success',
        'output': args.output,
        'size_bytes': os.path.getsize(args.output),
        'theme': theme,
        'template': actual_template,
        'sections': len(content.get('sections', [])),
        'has_charts': any(s.get('type') == 'chart' for s in content.get('sections', [])),
        'has_brand': bool(brand_path),
    }))


if __name__ == '__main__':
    main()

# Theme CSS Variable Contract

> This document defines the CSS custom properties that a theme file must provide.
> All themes are loaded as `:root` variable definitions. The base stylesheet
> and component styles reference these variables with fallback values.

## How Themes Work

1. The renderer loads `base.css` (containment + component styles)
2. The renderer loads `themes/{name}.css` (variable definitions)
3. If a brand config is provided, a third `:root` block overrides specific variables
4. CSS cascade ensures brand > theme > base defaults

## Required Variables

Your custom theme **must** define these on `:root`. Without them, the report
will fall back to base defaults which may not match your intended design.

| Variable | Purpose | Example |
|----------|---------|---------|
| `--color-primary` | Main brand color — headings, header borders, table headers | `#1B2A4A` |
| `--color-secondary` | Accent/decorative — section borders, highlights, cover divider | `#C9A962` |
| `--color-accent` | Links, interactive elements, h3 headings | `#3D7EAA` |
| `--font-heading` | Heading font stack (must include fallbacks) | `Georgia, serif` |
| `--font-body` | Body text font stack (must include fallbacks) | `Calibri, Helvetica, Arial, sans-serif` |

## Optional Variables

These have sensible defaults in `base.css`. Override only when you need to.

| Variable | Default | Purpose |
|----------|---------|---------|
| `--color-text` | `#2D2D2D` | Body text color |
| `--color-text-light` | `#666666` | Secondary text, captions, footnotes |
| `--color-bg` | `#FFFFFF` | Page background |
| `--color-bg-alt` | `#F5F5F0` | Callout/table stripe/card background |
| `--color-border` | `#E0E0E0` | Borders, dividers, table lines |
| `--color-success` | `#27AE60` | Green indicators (status, metrics, cells) |
| `--color-warning` | `#F39C12` | Yellow/amber indicators |
| `--color-danger` | `#E74C3C` | Red indicators |
| `--font-mono` | `'Courier New', monospace` | Code blocks, pre-formatted text |
| `--spacing-section` | `36px` | Vertical spacing between major sections |
| `--border-radius` | `4px` | Border radius for cards, callouts, badges |
| `--max-width` | `900px` | Maximum content width |

## Example: Custom Theme File

```css
/* my-brand.css */
:root {
  --color-primary: #0052CC;
  --color-secondary: #FF5630;
  --color-accent: #00B8D9;
  --font-heading: Montserrat, system-ui, sans-serif;
  --font-body: 'Open Sans', system-ui, sans-serif;

  /* Override optional */
  --color-bg-alt: #F4F5F7;
  --border-radius: 6px;
}
```

## Chart Color Mapping

When charts are rendered, semantic color names in chart data (`"color": "primary"`)
are resolved against the active theme's CSS variables at render time:

| Semantic Name | CSS Variable |
|--------------|-------------|
| `primary` | `--color-primary` |
| `secondary` | `--color-secondary` |
| `accent` | `--color-accent` |
| `success` | `--color-success` |
| `warning` | `--color-warning` |
| `danger` | `--color-danger` |

This ensures charts automatically match the theme palette.

## Testing Your Theme

After creating a custom theme CSS file:
1. Upload it to your skill version's `assets/themes/` directory
2. Update `assets/theme-manifest.json` to include your theme
3. Use `--theme your-theme-id` when calling the renderer
4. Validate the output with `validate_report.py`

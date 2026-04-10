#!/usr/bin/env python3
"""
html_to_pdf.py — Convert an HTML file to PDF using wkhtmltopdf.

Usage:
    python3 html_to_pdf.py --input report.html --output report.pdf
    python3 html_to_pdf.py --input report.html --output report.pdf --page-size A4 --margin 20mm

Arguments:
    --input       Input HTML file path
    --output      Output PDF file path
    --page-size   Page size: A4, Letter, Legal (default: A4)
    --margin      All margins (default: 15mm)
    --margin-top, --margin-bottom, --margin-left, --margin-right  Individual margins
    --orientation portrait or landscape (default: portrait)
    --dpi         DPI for rendering (default: 150)
    --no-outline  Disable PDF outline/bookmarks
"""

import argparse
import json
import os
import subprocess
import sys


def convert_html_to_pdf(input_path: str, output_path: str, **kwargs) -> dict:
    """Convert HTML to PDF using wkhtmltopdf."""

    if not os.path.exists(input_path):
        return {'status': 'error', 'message': f'Input file not found: {input_path}'}

    # Build wkhtmltopdf command
    cmd = ['wkhtmltopdf']

    # Page size
    page_size = kwargs.get('page_size', 'A4')
    cmd.extend(['--page-size', page_size])

    # Orientation
    orientation = kwargs.get('orientation', 'portrait')
    if orientation == 'landscape':
        cmd.append('--orientation')
        cmd.append('Landscape')

    # Margins
    margin = kwargs.get('margin', '15mm')
    margin_top = kwargs.get('margin_top', margin)
    margin_bottom = kwargs.get('margin_bottom', margin)
    margin_left = kwargs.get('margin_left', margin)
    margin_right = kwargs.get('margin_right', margin)

    cmd.extend(['--margin-top', margin_top])
    cmd.extend(['--margin-bottom', margin_bottom])
    cmd.extend(['--margin-left', margin_left])
    cmd.extend(['--margin-right', margin_right])

    # DPI
    dpi = kwargs.get('dpi', '150')
    cmd.extend(['--dpi', str(dpi)])

    # Encoding
    cmd.extend(['--encoding', 'UTF-8'])

    # Enable local file access (for embedded resources)
    cmd.append('--enable-local-file-access')

    # Outline (bookmarks from headings)
    if not kwargs.get('no_outline', False):
        cmd.append('--outline')
        cmd.extend(['--outline-depth', '3'])

    # Quiet mode
    cmd.append('--quiet')

    # Input and output
    cmd.append(input_path)
    cmd.append(output_path)

    # Ensure output directory exists
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

        if result.returncode != 0:
            # wkhtmltopdf returns non-zero for warnings too, check if output exists
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                return {
                    'status': 'success',
                    'output': output_path,
                    'size_bytes': os.path.getsize(output_path),
                    'warnings': result.stderr.strip() if result.stderr else None,
                }
            return {
                'status': 'error',
                'message': f'wkhtmltopdf failed with code {result.returncode}',
                'stderr': result.stderr.strip() if result.stderr else '',
            }

        return {
            'status': 'success',
            'output': output_path,
            'size_bytes': os.path.getsize(output_path),
            'page_size': page_size,
            'orientation': orientation,
        }

    except subprocess.TimeoutExpired:
        return {'status': 'error', 'message': 'Conversion timed out after 60 seconds'}
    except FileNotFoundError:
        return {'status': 'error', 'message': 'wkhtmltopdf not found. Is it installed?'}


def main():
    parser = argparse.ArgumentParser(description='Convert HTML to PDF')
    parser.add_argument('--input', required=True, help='Input HTML file')
    parser.add_argument('--output', required=True, help='Output PDF file')
    parser.add_argument('--page-size', default='A4', help='Page size (default: A4)')
    parser.add_argument('--margin', default='15mm', help='All margins (default: 15mm)')
    parser.add_argument('--margin-top', help='Top margin')
    parser.add_argument('--margin-bottom', help='Bottom margin')
    parser.add_argument('--margin-left', help='Left margin')
    parser.add_argument('--margin-right', help='Right margin')
    parser.add_argument('--orientation', default='portrait', choices=['portrait', 'landscape'])
    parser.add_argument('--dpi', default='150', help='DPI (default: 150)')
    parser.add_argument('--no-outline', action='store_true', help='Disable PDF outline')
    args = parser.parse_args()

    result = convert_html_to_pdf(
        args.input, args.output,
        page_size=args.page_size,
        margin=args.margin,
        margin_top=args.margin_top or args.margin,
        margin_bottom=args.margin_bottom or args.margin,
        margin_left=args.margin_left or args.margin,
        margin_right=args.margin_right or args.margin,
        orientation=args.orientation,
        dpi=args.dpi,
        no_outline=args.no_outline,
    )

    print(json.dumps(result))
    sys.exit(0 if result['status'] == 'success' else 1)


if __name__ == '__main__':
    main()

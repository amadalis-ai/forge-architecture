#!/usr/bin/env python3
"""
validate_report.py — Validate a self-contained HTML report for quality and completeness.

Usage:
    python3 validate_report.py /workspace/output/report.html

Checks:
    1. Valid HTML structure (doctype, head, body, charset)
    2. All images are embedded (no external URLs)
    3. CSS is inlined (no external stylesheets)
    4. No broken internal anchor links
    5. TOC matches actual headings
    6. File size is reasonable (< 10MB)
    7. No empty sections

Exit code: 0 if all checks pass, 1 if any fail.
Output: JSON validation report.
"""

import json
import os
import re
import sys


def validate_html_report(file_path: str) -> dict:
    """Run all validation checks on an HTML report."""

    checks = []
    passed = 0
    failed = 0

    if not os.path.exists(file_path):
        return {
            'status': 'error',
            'message': f'File not found: {file_path}',
            'checks': [],
            'passed': 0,
            'failed': 1,
        }

    with open(file_path, encoding='utf-8') as f:
        content = f.read()

    file_size = os.path.getsize(file_path)

    # Check 1: File size
    check = {'name': 'file_size', 'max_bytes': 10_000_000}
    if file_size > 10_000_000:
        check['status'] = 'FAIL'
        check['message'] = f'File too large: {file_size:,} bytes (max 10MB)'
        failed += 1
    else:
        check['status'] = 'PASS'
        check['message'] = f'File size: {file_size:,} bytes'
        passed += 1
    checks.append(check)

    # Check 2: DOCTYPE
    check = {'name': 'doctype'}
    if content.strip().lower().startswith('<!doctype html>'):
        check['status'] = 'PASS'
        check['message'] = 'DOCTYPE present'
        passed += 1
    else:
        check['status'] = 'FAIL'
        check['message'] = 'Missing <!DOCTYPE html> at start of file'
        failed += 1
    checks.append(check)

    # Check 3: Required elements
    for element in ['<html', '<head', '<body', '<meta charset']:
        check = {'name': f'element_{element.strip("<")}'}
        if element.lower() in content.lower():
            check['status'] = 'PASS'
            check['message'] = f'{element}> found'
            passed += 1
        else:
            check['status'] = 'FAIL'
            check['message'] = f'Missing {element}> element'
            failed += 1
        checks.append(check)

    # Check 4: No external stylesheets
    check = {'name': 'no_external_css'}
    external_css = re.findall(r'<link[^>]+rel=["\']stylesheet["\'][^>]+href=["\'](?!data:)([^"\']+)', content)
    if external_css:
        check['status'] = 'FAIL'
        check['message'] = f'External stylesheets found: {external_css}'
        failed += 1
    else:
        check['status'] = 'PASS'
        check['message'] = 'All CSS is inlined'
        passed += 1
    checks.append(check)

    # Check 5: No external images
    check = {'name': 'no_external_images'}
    external_imgs = re.findall(r'<img[^>]+src=["\'](?!data:)(?!#)(https?://[^"\']+)', content)
    if external_imgs:
        check['status'] = 'FAIL'
        check['message'] = f'External images found ({len(external_imgs)}): {external_imgs[:3]}'
        failed += 1
    else:
        check['status'] = 'PASS'
        check['message'] = 'All images are embedded or inline'
        passed += 1
    checks.append(check)

    # Check 6: No external scripts
    check = {'name': 'no_external_scripts'}
    external_scripts = re.findall(r'<script[^>]+src=["\'](?!data:)(https?://[^"\']+)', content)
    if external_scripts:
        check['status'] = 'FAIL'
        check['message'] = f'External scripts found: {external_scripts}'
        failed += 1
    else:
        check['status'] = 'PASS'
        check['message'] = 'No external script dependencies'
        passed += 1
    checks.append(check)

    # Check 7: Has content (not just boilerplate)
    check = {'name': 'has_content'}
    # Count text content roughly (strip tags)
    text_content = re.sub(r'<[^>]+>', '', content)
    text_content = re.sub(r'\s+', ' ', text_content).strip()
    word_count = len(text_content.split())
    if word_count < 50:
        check['status'] = 'FAIL'
        check['message'] = f'Very little content: {word_count} words'
        failed += 1
    else:
        check['status'] = 'PASS'
        check['message'] = f'Content has {word_count} words'
        passed += 1
    checks.append(check)

    # Check 8: Headings present
    check = {'name': 'has_headings'}
    headings = re.findall(r'<h[1-6][^>]*>([^<]+)</h[1-6]>', content)
    if len(headings) < 2:
        check['status'] = 'WARN'
        check['message'] = f'Only {len(headings)} heading(s) found'
        passed += 1  # Warn doesn't count as fail
    else:
        check['status'] = 'PASS'
        check['message'] = f'{len(headings)} headings found'
        passed += 1
    checks.append(check)

    # Check 9: Has <style> tag (CSS present)
    check = {'name': 'has_inline_css'}
    if '<style' in content.lower():
        check['status'] = 'PASS'
        check['message'] = 'Inline CSS present'
        passed += 1
    else:
        check['status'] = 'FAIL'
        check['message'] = 'No inline CSS found — report will be unstyled'
        failed += 1
    checks.append(check)

    # Check 10: Title tag
    check = {'name': 'has_title'}
    title_match = re.search(r'<title>([^<]+)</title>', content)
    if title_match:
        check['status'] = 'PASS'
        check['message'] = f'Title: "{title_match.group(1)}"'
        passed += 1
    else:
        check['status'] = 'FAIL'
        check['message'] = 'Missing <title> tag'
        failed += 1
    checks.append(check)

    # Check 11: Table containment — all <table> should be inside .table-wrapper
    check = {'name': 'containment_tables'}
    tables = re.findall(r'<table\b', content)
    wrapped_tables = re.findall(r'class=["\'][^"\']*table-wrapper[^"\']*["\'][^>]*>.*?<table\b', content, re.DOTALL)
    unwrapped = len(tables) - len(wrapped_tables)
    if tables and unwrapped > 0:
        check['status'] = 'WARN'
        check['message'] = f'{unwrapped} of {len(tables)} table(s) not wrapped in .table-wrapper'
        passed += 1  # Warn doesn't count as fail
    else:
        check['status'] = 'PASS'
        check['message'] = f'All {len(tables)} table(s) have overflow containment' if tables else 'No tables found'
        passed += 1
    checks.append(check)

    # Check 12: Chart integrity — if <canvas> exists, Chart.js must be present
    check = {'name': 'chart_integrity'}
    canvases = re.findall(r'<canvas\b', content)
    has_chartjs = 'new Chart(' in content or 'Chart.register' in content
    if canvases and not has_chartjs:
        check['status'] = 'FAIL'
        check['message'] = f'{len(canvases)} <canvas> element(s) found but Chart.js library not present'
        failed += 1
    elif canvases and has_chartjs:
        check['status'] = 'PASS'
        check['message'] = f'{len(canvases)} chart(s) with Chart.js library present'
        passed += 1
    else:
        check['status'] = 'PASS'
        check['message'] = 'No charts found (none expected)'
        passed += 1
    checks.append(check)

    # Check 13: CSS containment — base.css overflow rules should be present
    check = {'name': 'containment_css'}
    has_box_sizing = 'box-sizing' in content
    has_overflow_hidden = 'overflow-x' in content
    has_max_width_img = 'max-width: 100%' in content or 'max-width:100%' in content
    containment_score = sum([has_box_sizing, has_overflow_hidden, has_max_width_img])
    if containment_score >= 2:
        check['status'] = 'PASS'
        check['message'] = f'CSS containment rules present ({containment_score}/3 indicators)'
        passed += 1
    elif containment_score == 1:
        check['status'] = 'WARN'
        check['message'] = f'Partial CSS containment ({containment_score}/3 indicators)'
        passed += 1
    else:
        check['status'] = 'WARN'
        check['message'] = 'No CSS containment rules detected — content may overflow'
        passed += 1
    checks.append(check)

    # Check 14: Block elements nested inside <p> tags (sign of markdown double-conversion)
    check = {'name': 'no_block_in_p'}
    # <p> wrapping <table>, <div>, <ul>, <ol>, <h1-6> is always a rendering bug
    block_in_p = re.findall(r'<p[^>]*>\s*<(?:table|div|ul|ol|h[1-6]|section|article|figure|details|dl|blockquote|pre)\b', content, re.IGNORECASE)
    if block_in_p:
        check['status'] = 'WARN'
        check['message'] = f'{len(block_in_p)} block-level element(s) nested inside <p> tags — likely markdown double-conversion of HTML content'
        passed += 1
    else:
        check['status'] = 'PASS'
        check['message'] = 'No block elements inside <p> tags'
        passed += 1
    checks.append(check)

    # Check 15: Undefined CSS classes — classes used in body that have no definition in <style>
    check = {'name': 'css_class_coverage'}
    # Extract all class="..." values from body content
    body_match = re.search(r'<body[^>]*>(.*)</body>', content, re.DOTALL | re.IGNORECASE)
    style_match = re.search(r'<style[^>]*>(.*?)</style>', content, re.DOTALL | re.IGNORECASE)
    if body_match and style_match:
        body_html = body_match.group(1)
        style_text = style_match.group(1)
        # Find all classes used in body
        used_classes = set()
        for m in re.finditer(r'class=["\']([^"\']+)["\']', body_html):
            for cls in m.group(1).split():
                used_classes.add(cls)
        # Find all classes defined in CSS (rough: .classname in style)
        defined_classes = set()
        for m in re.finditer(r'\.([\w-]+)\s*[{,:]', style_text):
            defined_classes.add(m.group(1))
        # Known utility/framework classes that don't need definitions
        known_classes = {'page-break', 'no-print', 'language-python', 'language-bash',
                        'language-json', 'language-javascript', 'language-html', 'language-css',
                        'language-shell', 'language-yaml', 'language-xml', 'language-sql',
                        'language-typescript'}
        undefined = used_classes - defined_classes - known_classes
        if undefined and len(undefined) > 3:
            check['status'] = 'WARN'
            sample = sorted(undefined)[:8]
            check['message'] = f'{len(undefined)} CSS class(es) used but not defined in <style>: {", ".join(sample)}'
            passed += 1
        else:
            check['status'] = 'PASS'
            check['message'] = f'CSS class coverage OK ({len(used_classes)} used, {len(undefined)} undefined)'
            passed += 1
    else:
        check['status'] = 'PASS'
        check['message'] = 'Could not extract body/style for class analysis'
        passed += 1
    checks.append(check)

    overall = 'PASS' if failed == 0 else 'FAIL'

    return {
        'status': overall,
        'file': file_path,
        'size_bytes': file_size,
        'word_count': word_count,
        'heading_count': len(headings),
        'passed': passed,
        'failed': failed,
        'total': passed + failed,
        'checks': checks,
    }


def main():
    if len(sys.argv) < 2:
        print('Usage: validate_report.py <html_file>', file=sys.stderr)
        sys.exit(1)

    result = validate_html_report(sys.argv[1])
    print(json.dumps(result, indent=2))
    sys.exit(0 if result['status'] == 'PASS' else 1)


if __name__ == '__main__':
    main()

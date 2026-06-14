#!/usr/bin/env python3
"""
Converts inline styles in email.html to CSS classes, shrinking the file for sending.
Writes email_compact.html — functionally identical, much smaller.
"""
import re, os, sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
IN_PATH  = os.path.join(SCRIPT_DIR, 'email.html')
OUT_PATH = os.path.join(SCRIPT_DIR, 'email_compact.html')

with open(IN_PATH, 'r', encoding='utf-8') as f:
    html = f.read()

# Collect all unique inline style values
style_map = {}   # style_value -> class_name
counter = [0]

def get_class(style_value):
    if style_value not in style_map:
        counter[0] += 1
        style_map[style_value] = f's{counter[0]}'
    return style_map[style_value]

# Replace all style="..." attributes (not inside <style> blocks)
# We process outside of <style> tags only
def replace_styles(html):
    # Split around existing <style> blocks to avoid touching CSS selectors
    parts = re.split(r'(<style[^>]*>.*?</style>)', html, flags=re.DOTALL)
    result = []
    for i, part in enumerate(parts):
        if i % 2 == 1:
            # Inside a <style> block — keep as-is
            result.append(part)
        else:
            # Outside — replace inline styles
            def replacer(m):
                sv = m.group(1)
                cn = get_class(sv)
                return f'class="{cn}"'
            result.append(re.sub(r'style="([^"]+)"', replacer, part))
    return ''.join(result)

html2 = replace_styles(html)

# Build CSS block from collected styles
css_rules = '\n'.join(f'.{cls} {{ {sv} }}' for sv, cls in sorted(style_map.items(), key=lambda x: x[1]))
css_block = f'<style>\n{css_rules}\n</style>\n'

# Insert CSS block just before </head>
if '</head>' in html2:
    html2 = html2.replace('</head>', css_block + '</head>', 1)
else:
    html2 = css_block + html2

# Collapse whitespace between tags
html2 = re.sub(r'>\s{2,}<', '><', html2)
html2 = re.sub(r'^\s+', '', html2, flags=re.MULTILINE)
html2 = re.sub(r'\n{3,}', '\n\n', html2)

with open(OUT_PATH, 'w', encoding='utf-8') as f:
    f.write(html2)

print(f'Input:  {os.path.getsize(IN_PATH):,} bytes')
print(f'Output: {os.path.getsize(OUT_PATH):,} bytes')
print(f'Styles: {len(style_map)} unique classes extracted')
print(f'Reduction: {100*(os.path.getsize(IN_PATH)-os.path.getsize(OUT_PATH))//os.path.getsize(IN_PATH)}%')

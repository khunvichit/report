#!/usr/bin/env python3
"""Replaces repeated inline styles with CSS classes to shrink email.html."""
import re, sys

src = sys.argv[1] if len(sys.argv) > 1 else "email.html"
dst = sys.argv[2] if len(sys.argv) > 2 else "email_small.html"

content = open(src).read()
# skip leading comment block
idx = content.find("<!doctype html>")
if idx > 0:
    content = content[idx:]

# Collect all inline style values and count occurrences
styles_found = re.findall(r'style="([^"]+)"', content)
from collections import Counter
counts = Counter(styles_found)

# Build mapping: style_value -> class name, only for styles that appear 2+ times
mapping = {}
css_rules = []
cls_idx = 0
for style_val, count in sorted(counts.items(), key=lambda x: -x[1]):
    if count >= 2:
        cls_name = f"s{cls_idx}"
        cls_idx += 1
        mapping[style_val] = cls_name
        css_rules.append(f".{cls_name}{{{style_val}}}")

# Build CSS block
css_block = "<style>\n" + "\n".join(css_rules) + "\n</style>\n"

# Replace inline styles with class references
def replace_style(m):
    val = m.group(1)
    if val in mapping:
        return f'class="{mapping[val]}"'
    return m.group(0)  # keep infrequent styles as-is

minified = re.sub(r'style="([^"]+)"', replace_style, content)

# Insert CSS block right after </head> or <head>
if "</head>" in minified:
    minified = minified.replace("</head>", css_block + "</head>", 1)
elif "<head>" in minified:
    minified = minified.replace("<head>", "<head>" + css_block, 1)

# Write output
open(dst, "w").write(minified)

orig = len(content)
new = len(minified)
print(f"Original: {orig:,} chars ({orig//3:,} tokens est.)")
print(f"Minified: {new:,} chars ({new//3:,} tokens est.)")
print(f"Savings:  {orig-new:,} chars ({(orig-new)/orig*100:.1f}%)")
print(f"CSS rules added: {len(css_rules)}")

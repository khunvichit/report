#!/usr/bin/env python3
"""
fill_template.py — assemble the Juiceland HTML email WITHOUT the model emitting markup.

Usage:
    python3 fill_template.py juiceland-template.html data.json > out.html

data.json shape:
{
  "scalars":  { "comb_net": "52,518", ... },
  "repeats":  {
     "chart_days": [...],
     "top20_branches": [
       { "header_color": "#5551FE", ..., "top20_rows": [{...}, ...] },
       ...
     ],
     ...
  },
  "sections": { "am_review": false, "seasonal": true, "dormant": true, ... }
}

Nested repeats: if an outer item carries a LIST value whose key matches an inner REPEAT name,
that per-item list is used instead of the global repeats dict for that inner block.
"""
import sys, json, re

_REPEAT_PAT = re.compile(
    r"<!--\s*REPEAT:(\w+)[\s\S]*?-->(.*?)<!--\s*/REPEAT:\1\s*-->", re.DOTALL
)

def _process_block(block, item, repeats):
    """Expand one item's copy of a block: resolve nested REPEATs first, then substitute tokens."""
    def sub_repl(m):
        name, sub_inner = m.group(1), m.group(2)
        sub_items = item[name] if isinstance(item.get(name), list) else repeats.get(name, [])
        return "".join(_process_block(sub_inner, si, repeats) for si in sub_items)
    block = _REPEAT_PAT.sub(sub_repl, block)
    for k, v in item.items():
        if not isinstance(v, list):
            block = block.replace("{{" + k + "}}", str(v))
    return block

def render_repeats(html, repeats):
    def repl(m):
        name, inner = m.group(1), m.group(2)
        items = repeats.get(name, [])
        return "".join(_process_block(inner, item, repeats) for item in items)
    prev = None
    while prev != html:
        prev = html
        html = _REPEAT_PAT.sub(repl, html)
    return html

def render_sections(html, sections):
    pattern = re.compile(r"<!--\s*SECTION:(\w+)[\s\S]*?-->(.*?)<!--\s*/SECTION:\1\s*-->", re.DOTALL)
    def repl(m):
        name, inner = m.group(1), m.group(2)
        return inner if sections.get(name, False) else ""
    prev = None
    while prev != html:
        prev = html
        html = pattern.sub(repl, html)
    return html

def render_scalars(html, scalars):
    for k, v in scalars.items():
        html = html.replace("{{" + k + "}}", str(v))
    return html

def main():
    template_path, data_path = sys.argv[1], sys.argv[2]
    with open(template_path, encoding="utf-8") as f:
        html = f.read()
    with open(data_path, encoding="utf-8") as f:
        data = json.load(f)
    html = render_sections(html, data.get("sections", {}))
    html = render_repeats(html, data.get("repeats", {}))
    html = render_scalars(html, data.get("scalars", {}))
    html = re.sub(r"<!--\s*/?(?:REPEAT|SECTION):\w+[\s\S]*?-->", "", html)
    leftovers = sorted(set(re.findall(r"\{\{(\w+)\}\}", html)))
    if leftovers:
        sys.stderr.write("WARNING unresolved placeholders: " + ", ".join(leftovers) + "\n")
    sys.stdout.write(html)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
fill_template.py — assemble the Juiceland HTML email WITHOUT the model emitting markup.

Why this exists: rendering the full ~1,300-line HTML as model output blows the 32K
output-token ceiling. Instead, the model computes DATA only and writes it to data.json;
this script reads the locked template and produces the final HTML by string substitution.
The HTML never passes through model output.

Usage:
    python3 fill_template.py juiceland-template.html data.json > out.html
    # then the routine passes out.html's contents to lark_send_email

data.json shape (the model produces this — small, well under the token limit):
{
  "scalars": { "comb_net": "68,545", "signed_pct": "-3.8", "report_date_display": "5 June 2026", ... },
  "repeats": {
     "dormant_rows": [ { "memo_display": "...", "gap_days": "9", "gap_color": "#E65100", ... }, ... ],
     "top20_rows":   [ ... ],
     "chart_days":   [ ... ],
     ...
  },
  "sections": { "am_review": true, "seasonal": true, "dormant": true,
                "forecast_shown": true, "forecast_suppressed": false, "anomaly_shown": true }
}
- scalars  -> replace {{token}} globally
- repeats  -> for each <!-- REPEAT:name --> .. <!-- /REPEAT:name -->, render the inner block
              once per list item (substituting that item's keys), then drop the markers.
- sections -> for each <!-- SECTION:name --> .. <!-- /SECTION:name -->, keep inner if True else remove.
"""
import sys, json, re

def render_repeats(html, repeats):
    # Process each REPEAT block. Non-greedy, DOTALL so it spans newlines.
    pattern = re.compile(r"<!--\s*REPEAT:(\w+)[\s\S]*?-->(.*?)<!--\s*/REPEAT:\1\s*-->", re.DOTALL)
    def repl(m):
        name, inner = m.group(1), m.group(2)
        items = repeats.get(name, [])
        out = []
        for item in items:
            block = inner
            for k, v in item.items():
                block = block.replace("{{" + k + "}}", str(v))
            out.append(block)
        return "".join(out)
    # Loop until no nested REPEATs remain (handles REPEAT inside REPEAT).
    prev = None
    while prev != html:
        prev = html
        html = pattern.sub(repl, html)
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
    # Strip the template's leading how-to comment header (the block before <!DOCTYPE).
    html = re.sub(r"^\s*<!--(?:(?!-->).)*?-->\s*", "", html, count=1, flags=re.DOTALL)
    with open(data_path, encoding="utf-8") as f:
        data = json.load(f)
    # Order matters: sections first (so dropped sections remove their REPEATs too),
    # then repeats, then scalars (scalars may appear inside repeated blocks already handled).
    html = render_sections(html, data.get("sections", {}))
    html = render_repeats(html, data.get("repeats", {}))
    html = render_scalars(html, data.get("scalars", {}))
    # Strip the template's how-to comment header and any leftover REPEAT/SECTION markers.
    html = re.sub(r"<!--\s*/?(?:REPEAT|SECTION):\w+[\s\S]*?-->", "", html)
    # Warn (to stderr) if any placeholder survived — never block the send.
    leftovers = sorted(set(re.findall(r"\{\{(\w+)\}\}", html)))
    if leftovers:
        sys.stderr.write("WARNING unresolved placeholders: " + ", ".join(leftovers) + "\n")
    sys.stdout.write(html)

if __name__ == "__main__":
    main()

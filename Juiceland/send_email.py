#!/usr/bin/env python3
"""Send the Juiceland daily report email via Lark MCP server directly."""
import json, sys
import urllib.request, urllib.error

MCP_URL = "https://chaw.cloudpepper.site/lark-mcp/mcp?api_key=YzRuqR-fZEcCMeIbMD2b8ZFER5mz1gZcC-ks4IcMh1Q"

def mcp_call(method, params):
    payload = json.dumps({
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params
    }).encode("utf-8")
    req = urllib.request.Request(
        MCP_URL,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        },
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read().decode("utf-8")
            # Strip SSE framing if present
            lines = [l for l in raw.splitlines() if l.startswith("data: ")]
            if lines:
                raw = lines[-1][6:]
            return json.loads(raw)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        return {"error": {"code": e.code, "message": body}}

# Step 1: Initialize
init_resp = mcp_call("initialize", {
    "protocolVersion": "2024-11-05",
    "capabilities": {},
    "clientInfo": {"name": "claude-code", "version": "1.0"}
})
print("Init:", json.dumps(init_resp)[:200])

# Step 2: Read email HTML
with open("/home/user/report/Juiceland/email.html", encoding="utf-8") as f:
    content = f.read()
idx = content.find("<!doctype")
html_body = content[idx:]
print(f"Body: {len(html_body)} chars")

# Step 3: Send email
send_resp = mcp_call("tools/call", {
    "name": "lark_send_email",
    "arguments": {
        "to": [
            {"address": "juiceland@chaw.co.th", "name": "Juiceland Team"},
            {"address": "management@chaw.co.th", "name": "CHAW Management"}
        ],
        "subject": "⚠️ [Juiceland] Daily Sales Report — 9 June 2026 | ฿52,518 (-26.1%)",
        "body": html_body
    }
})
print("Send:", json.dumps(send_resp)[:500])

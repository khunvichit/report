#!/usr/bin/env python3
"""Send email via CCR MCP proxy using the session ingress token."""
import json, sys, os
import urllib.request, urllib.error

INGRESS_TOKEN_FILE = os.environ.get("CLAUDE_SESSION_INGRESS_TOKEN_FILE", "")
with open(INGRESS_TOKEN_FILE) as f:
    TOKEN = f.read().strip()

MCP_URL = (
    "https://api.anthropic.com/v2/ccr-sessions/cse_01AuC6QMUcxSXzHPE7XQC4ZN/mcp"
    "?mcp_url=https%3A%2F%2Fchaw.cloudpepper.site%2Flark-mcp%2Fmcp%3Fapi_key%3D"
    "YzRuqR-fZEcCMeIbMD2b8ZFER5mz1gZcC-ks4IcMh1Q"
    "&mcp_server_id=6728e091-06f0-5e95-a122-e61a258c5443"
    "&toolbox_mcp_server_id=7de72e5f-3664-41c0-9775-5d13bd8722f1"
)
HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json, text/event-stream",
    "Authorization": f"Bearer {TOKEN}",
    "X-MCP-Server-ID": "7de72e5f-3664-41c0-9775-5d13bd8722f1",
    "X-Session-UUID": "cse_01AuC6QMUcxSXzHPE7XQC4ZN",
}

def mcp_post(payload_dict):
    data = json.dumps(payload_dict).encode("utf-8")
    req = urllib.request.Request(MCP_URL, data=data, headers=HEADERS, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            raw = resp.read().decode("utf-8")
            # Parse SSE lines
            for line in raw.splitlines():
                if line.startswith("data: "):
                    try:
                        return json.loads(line[6:])
                    except Exception:
                        pass
            # Try raw JSON
            return json.loads(raw)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        return {"error": {"http_code": e.code, "message": body[:500]}}
    except Exception as e:
        return {"error": {"exception": str(e)}}

# Initialize
init = mcp_post({
    "jsonrpc": "2.0", "id": 1, "method": "initialize",
    "params": {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {"name": "claude-code-direct", "version": "1.0"}
    }
})
print("Init:", json.dumps(init)[:300])

# Read email
with open("/home/user/report/Juiceland/email.html", encoding="utf-8") as f:
    content = f.read()
idx = content.find("<!doctype")
html_body = content[idx:]
print(f"HTML body: {len(html_body)} chars")

# Send email
resp = mcp_post({
    "jsonrpc": "2.0", "id": 2, "method": "tools/call",
    "params": {
        "name": "lark_send_email",
        "arguments": {
            "to": [
                {"address": "juiceland@chaw.co.th", "name": "Juiceland Team"},
                {"address": "management@chaw.co.th", "name": "CHAW Management"}
            ],
            "subject": "⚠️ [Juiceland] Daily Sales Report — 9 June 2026 | ฿52,518 (-26.1%)",
            "body": html_body
        }
    }
})
print("Send:", json.dumps(resp)[:1000])

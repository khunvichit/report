#!/usr/bin/env python3
"""Send Juiceland group message via CCR MCP proxy."""
import json, os
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
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read().decode("utf-8")
            for line in raw.splitlines():
                if line.startswith("data: "):
                    try:
                        return json.loads(line[6:])
                    except Exception:
                        pass
            return json.loads(raw)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        return {"error": {"http_code": e.code, "message": body[:500]}}
    except Exception as e:
        return {"error": {"exception": str(e)}}

# Initialize
mcp_post({
    "jsonrpc": "2.0", "id": 1, "method": "initialize",
    "params": {
        "protocolVersion": "2025-03-26",
        "capabilities": {},
        "clientInfo": {"name": "claude-code-direct", "version": "1.0"}
    }
})

# Gate check: am_queue_count + dormant_count = 0 + 31 = 31 > 0  → FIRE
GROUP_ID = "oc_f25274999f6561e6f1e484102ee198e7"  # Food Operation Core (fallback)

message = """🧃 Juiceland Daily Summary — 9 June 2026 (วันอังคาร)

📊 ยอดขายรวม: ฿52,518 ex-VAT (-26.1% vs 30d avg)
- MW1: ฿30,613 (-12.4%)
- SE3: ฿12,035 (-50.6%)
- PKT: ฿9,870 (-16.1%)

🆕 New Product Launches:
- 🥤 Drinks (9 SKUs): 11u / ฿1,494 yest
- 🍉 Seasonal Fruits (4 SKUs): 0u / ฿0 yest
- ⭐ New Category (11 SKUs): 0u / ฿0 yest

🚨 AM Review: 0 items · 🚫 Dormant SKUs: 31 items

กรุณาตรวจสอบและ reply ภายใน 24 ชม. ขอบคุณครับ 🙏"""

resp = mcp_post({
    "jsonrpc": "2.0", "id": 2, "method": "tools/call",
    "params": {
        "name": "lark_send_message",
        "arguments": {
            "receive_id": GROUP_ID,
            "receive_id_type": "chat_id",
            "msg_type": "text",
            "content": message
        }
    }
})
print("Group send:", json.dumps(resp)[:500])

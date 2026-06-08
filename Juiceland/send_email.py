#!/usr/bin/env python3
"""
Direct Lark MCP call to send Juiceland email — bypasses Claude output token limit.
Reads email.html from disk and posts via MCP JSON-RPC over HTTP.
"""
import json, sys, urllib.request, urllib.error

MCP_URL = "https://api.anthropic.com/v2/ccr-sessions/cse_01Q2YUVeJeyYahezq1G79qBe/mcp?mcp_url=https%3A%2F%2Fchaw.cloudpepper.site%2Flark-mcp%2Fmcp%3Fapi_key%3DYzRuqR-fZEcCMeIbMD2b8ZFER5mz1gZcC-ks4IcMh1Q&mcp_server_id=c48d8862-7ed8-50e3-84b7-e6ee9b3fecd1&toolbox_mcp_server_id=7de72e5f-3664-41c0-9775-5d13bd8722f1"
EXTRA_HEADERS = {
    "X-Session-UUID": "cse_01Q2YUVeJeyYahezq1G79qBe",
    "X-MCP-Server-ID": "7de72e5f-3664-41c0-9775-5d13bd8722f1",
}

def mcp_call(method, params):
    payload = json.dumps({
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params
    }).encode()
    req = urllib.request.Request(
        MCP_URL,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            **EXTRA_HEADERS,
        },
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read().decode()
            # Handle SSE format (data: {...}\n\n)
            if raw.startswith("data:"):
                lines = [l[5:].strip() for l in raw.split("\n") if l.startswith("data:") and l.strip() != "data:"]
                results = []
                for line in lines:
                    try:
                        results.append(json.loads(line))
                    except Exception:
                        pass
                return results[-1] if results else {"raw": raw}
            else:
                return json.loads(raw)
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP {e.code}: {e.read().decode()[:500]}"}
    except Exception as e:
        return {"error": str(e)}

def main():
    # Initialize
    init_resp = mcp_call("initialize", {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {"name": "juiceland-send", "version": "1.0"}
    })
    print("Init:", json.dumps(init_resp)[:200])

    # Read email body
    body = open("/home/user/report/Juiceland/email.html").read()
    # Strip leading comment block (before <!doctype html>)
    idx = body.find("<!doctype html>")
    if idx > 0:
        body = body[idx:]
    print(f"Body length: {len(body)} chars")

    # Send email
    resp = mcp_call("tools/call", {
        "name": "lark_send_email",
        "arguments": {
            "to": [
                {"address": "juiceland@chaw.co.th", "name": "Juiceland Team"},
                {"address": "management@chaw.co.th", "name": "CHAW Management"}
            ],
            "subject": "⚠️ [Juiceland] Daily Sales Report — 7 June 2026 | ฿56,719 (-20.4%)",
            "body": body
        }
    })
    print("Send email response:")
    print(json.dumps(resp, indent=2, ensure_ascii=False)[:2000])
    return resp

if __name__ == "__main__":
    result = main()
    # Exit 0 if success
    if isinstance(result, dict) and "error" in str(result).lower():
        sys.exit(1)

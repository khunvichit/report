#!/usr/bin/env python3
"""Send Juiceland email via Lark MCP over Anthropic proxy using session ingress token."""
import json, urllib.request, urllib.error, sys

TOKEN_FILE = "/home/claude/.claude/remote/.session_ingress_token"
AUTH_TOKEN = open(TOKEN_FILE).read().strip()

PROXY_URL = (
    "https://api.anthropic.com/v2/ccr-sessions/cse_01Q2YUVeJeyYahezq1G79qBe/mcp"
    "?mcp_url=https%3A%2F%2Fchaw.cloudpepper.site%2Flark-mcp%2Fmcp%3Fapi_key%3D"
    "YzRuqR-fZEcCMeIbMD2b8ZFER5mz1gZcC-ks4IcMh1Q"
    "&mcp_server_id=c48d8862-7ed8-50e3-84b7-e6ee9b3fecd1"
    "&toolbox_mcp_server_id=7de72e5f-3664-41c0-9775-5d13bd8722f1"
)

mcp_session_id = None

def build_headers():
    h = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        "Authorization": f"Bearer {AUTH_TOKEN}",
        "X-Session-UUID": "cse_01Q2YUVeJeyYahezq1G79qBe",
        "X-MCP-Server-ID": "7de72e5f-3664-41c0-9775-5d13bd8722f1",
    }
    if mcp_session_id:
        h["mcp-session-id"] = mcp_session_id
    return h

def parse_sse(raw):
    """Parse SSE stream and extract JSON-RPC results."""
    results = []
    for line in raw.split("\n"):
        line = line.strip()
        if line.startswith("data:"):
            data = line[5:].strip()
            if data and data != "[DONE]":
                try:
                    results.append(json.loads(data))
                except Exception:
                    pass
    return results[-1] if results else None

def mcp_post(method, params, req_id=1, timeout=90):
    global mcp_session_id
    payload = json.dumps({"jsonrpc": "2.0", "id": req_id, "method": method, "params": params}).encode()
    req = urllib.request.Request(PROXY_URL, data=payload, headers=build_headers(), method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            # Capture session ID from first response
            if not mcp_session_id:
                sid = resp.headers.get("mcp-session-id")
                if sid:
                    mcp_session_id = sid
                    print(f"  MCP session: {sid}")
            raw = resp.read().decode("utf-8", "replace")
            parsed = parse_sse(raw)
            if parsed is None:
                return {"error": f"Empty/unparseable response. Raw: {raw[:300]}"}
            return parsed
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP {e.code}: {e.read().decode()[:400]}"}
    except Exception as ex:
        return {"error": f"{type(ex).__name__}: {str(ex)[:200]}"}

def main():
    print("Step 1: Initialize MCP session...")
    init = mcp_post("initialize", {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {"name": "juiceland-send", "version": "1.0"}
    })
    print("Init result:", json.dumps(init, ensure_ascii=False)[:300])
    if "error" in init:
        print("FAILED — aborting")
        sys.exit(1)

    print("\nStep 2: Send initialized notification...")
    mcp_post("notifications/initialized", {}, req_id=2)

    print("\nStep 3: Read email body...")
    body = open("/home/user/report/Juiceland/email_small.html").read()
    idx = body.find("<!doctype html>")
    if idx > 0:
        body = body[idx:]
    print(f"Body size: {len(body):,} chars")

    print("\nStep 4: Call lark_send_email...")
    resp = mcp_post("tools/call", {
        "name": "lark_send_email",
        "arguments": {
            "to": [
                {"address": "juiceland@chaw.co.th", "name": "Juiceland Team"},
                {"address": "management@chaw.co.th", "name": "CHAW Management"},
            ],
            "subject": "⚠️ [Juiceland] Daily Sales Report — 7 June 2026 | ฿56,719 (-20.4%)",
            "body": body
        }
    }, req_id=3, timeout=120)
    print("\nSend email response:")
    print(json.dumps(resp, indent=2, ensure_ascii=False)[:3000])
    return resp

if __name__ == "__main__":
    result = main()
    if isinstance(result, dict):
        if "error" in result and "content" not in str(result):
            sys.exit(1)
    print("\nDone.")

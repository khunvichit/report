#!/usr/bin/env python3
"""
Direct MCP call to lark_send_email — bypasses context window limit.
Reads email.html from disk and POSTs to the Lark MCP server via its streamable HTTP transport.
"""
import json, sys, os, urllib.request, urllib.error

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
EMAIL_PATH  = os.path.join(SCRIPT_DIR, 'email.html')

MCP_URL = (
    'https://chaw.cloudpepper.site/lark-mcp/mcp'
    '?api_key=YzRuqR-fZEcCMeIbMD2b8ZFER5mz1gZcC-ks4IcMh1Q'
)

def mcp_call(method, params):
    payload = json.dumps({
        'jsonrpc': '2.0',
        'id': 1,
        'method': method,
        'params': params,
    }).encode('utf-8')
    req = urllib.request.Request(
        MCP_URL,
        data=payload,
        headers={
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/event-stream',
        },
        method='POST',
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        raw = resp.read().decode('utf-8')
    # SSE or plain JSON response
    lines = [l for l in raw.splitlines() if l.startswith('data:')]
    if lines:
        return json.loads(lines[-1][5:].strip())
    return json.loads(raw)


def main():
    print('Reading email.html …')
    with open(EMAIL_PATH, 'r', encoding='utf-8') as f:
        html_body = f.read()
    print(f'  {len(html_body):,} chars read')

    # --- MCP initialize handshake -----------------------------------------
    print('MCP initialize …')
    try:
        init_resp = mcp_call('initialize', {
            'protocolVersion': '2024-11-05',
            'capabilities': {},
            'clientInfo': {'name': 'juiceland-sender', 'version': '1.0'},
        })
        print('  server:', init_resp.get('result', {}).get('serverInfo', '(ok)'))
    except Exception as e:
        print(f'  initialize warning (continuing): {e}')

    # --- Call lark_send_email ----------------------------------------------
    print('Calling lark_send_email …')
    result = mcp_call('tools/call', {
        'name': 'lark_send_email',
        'arguments': {
            'to': [
                {'address': 'juiceland@chaw.co.th',  'name': 'Juiceland Team'},
                {'address': 'management@chaw.co.th', 'name': 'CHAW Management'},
            ],
            'subject': '✅ [Juiceland] Daily Sales Report — 13 June 2026 | ฿70,983 (-0.5%)',
            'body': html_body,
        },
    })
    print('Result:', json.dumps(result, ensure_ascii=False, indent=2)[:2000])
    if 'error' in result:
        sys.exit(1)
    print('\n✅ Email sent successfully.')


if __name__ == '__main__':
    main()

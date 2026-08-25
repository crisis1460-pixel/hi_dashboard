#!/usr/bin/env python3
"""AiFRS 로컬 서버 — 정적 파일 제공 + API 키 파일 저장(POST /aifrs-keys.json)"""
import http.server, json, os, sys

PORT = 8899
KEYS_FILE = 'aifrs-keys.json'
ALLOWED_KEYS = {'gemini', 'openrouter'}

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_OPTIONS(self):
        self._cors(); self.end_headers()

    def do_POST(self):
        if self.path == '/' + KEYS_FILE:
            try:
                n = int(self.headers.get('Content-Length', 0))
                data = json.loads(self.rfile.read(n))
                safe = {k: v for k, v in data.items() if k in ALLOWED_KEYS and isinstance(v, str)}
                with open(KEYS_FILE, 'w', encoding='utf-8') as f:
                    json.dump(safe, f, ensure_ascii=False, indent=2)
                self._cors()
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(b'{"ok":true}')
            except Exception as e:
                self.send_response(400); self.end_headers()
        else:
            self.send_response(404); self.end_headers()

    def _cors(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', 'http://127.0.0.1:8899')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def log_message(self, fmt, *args):
        sys.stderr.write(f'[AiFRS] {self.address_string()} {fmt % args}\n')

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)) or '.')
    print(f'AiFRS server → http://127.0.0.1:{PORT}', flush=True)
    with http.server.HTTPServer(('127.0.0.1', PORT), Handler) as s:
        try: s.serve_forever()
        except KeyboardInterrupt: pass

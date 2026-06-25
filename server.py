#!/usr/bin/env python3
"""诗笺 · 每日一言 — 本地预览服务器。运行: python3 server.py 然后打开 http://localhost:8792"""
import http.server, socketserver, os

PORT = 8792
os.chdir(os.path.dirname(os.path.abspath(__file__)))

class Handler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # 本地开发禁用缓存，方便看到改动
        self.send_header('Cache-Control', 'no-store')
        super().end_headers()

    def log_message(self, *a):
        pass

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"诗笺运行中 → http://localhost:{PORT}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n已停止")

#!/usr/bin/env python3
"""Локальный сервер для UI Вебмастер-монитора.

  python serve_ui.py [--port 8794]

Отдаёт ui/ и data/ из корня проекта, открывает браузер.
Эндпоинты:
  POST /api/collect — запустить сбор позиций (webmaster_monitor.py, асинхронно)
  GET  /api/status  — идёт ли сбор + метаданные последнего data.json
"""
import argparse
import http.server
import json
import os
import socketserver
import subprocess
import sys
import threading
import time
import webbrowser

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(ROOT, 'data', 'webmaster', 'data.json')
MONITOR = os.path.join(ROOT, 'scripts', 'webmaster_monitor.py')

_collect = {'running': False, 'started': None, 'finished': None}


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def end_headers(self):
        self.send_header('Cache-Control', 'no-store')
        super().end_headers()

    def log_message(self, fmt, *args):
        print(f'[{self.log_date_time_string()}] {fmt % args}')

    def _json(self, code: int, payload: dict):
        body = json.dumps(payload, ensure_ascii=False).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == '/api/status':
            meta = {}
            if os.path.exists(DATA_PATH):
                try:
                    d = json.load(open(DATA_PATH, encoding='utf-8'))
                    meta = {'generated': d.get('generated'), 'status': d.get('status'),
                            'query_count': len(d.get('queries', []))}
                except Exception:
                    meta = {'error': 'data.json не читается'}
            self._json(200, {**_collect, **meta})
            return
        super().do_GET()

    def do_POST(self):
        if self.path == '/api/collect':
            if _collect['running']:
                self._json(200, {'running': True, 'message': 'сбор уже идёт'})
                return
            _collect['running'] = True
            _collect['started'] = time.strftime('%Y-%m-%dT%H:%M:%S')
            _collect['finished'] = None

            def run():
                try:
                    subprocess.run([sys.executable, MONITOR], cwd=ROOT, timeout=1800)
                finally:
                    _collect['running'] = False
                    _collect['finished'] = time.strftime('%Y-%m-%dT%H:%M:%S')

            threading.Thread(target=run, daemon=True).start()
            self._json(202, {'running': True, 'message': 'сбор запущен'})
            return
        self._json(404, {'error': 'not found'})


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--port', type=int, default=8794)
    args = ap.parse_args()

    with socketserver.ThreadingTCPServer(('127.0.0.1', args.port), Handler) as httpd:
        url = f'http://127.0.0.1:{args.port}/ui/'
        print(f'Вебмастер-монитор: {url}  (Ctrl+C — стоп)')
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print('\nстоп')


if __name__ == '__main__':
    main()

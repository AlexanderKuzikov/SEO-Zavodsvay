#!/usr/bin/env python3
"""Baseline Яндекс.Вебмастера для zavodsvay.ru.

Использование:
  python scripts/webmaster_baseline.py [--days 30]

Требует OAuth-токен: переменная окружения YANDEX_WEBMASTER_OAUTH_TOKEN
или файл .env в корне проекта (YANDEX_WEBMASTER_OAUTH_TOKEN=...).

Пишет audits/webmaster-baseline-YYYY-MM-DD.json:
  user_id, host_id, popular-запросы (топ-500 по кликам), история запросов
  (30 дней), история индексирования, sitemap, ИКС-история, диагностика.
"""
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API = 'https://api.webmaster.yandex.net/v4'
HOST = 'https://zavodsvay.ru'
AUDIT_DIR = os.path.join(ROOT, 'audits')

DAYS = 30


def load_token() -> str:
    token = os.environ.get('YANDEX_WEBMASTER_OAUTH_TOKEN', '').strip()
    if not token:
        env_path = os.path.join(ROOT, '.env')
        if os.path.exists(env_path):
            for line in open(env_path, encoding='utf-8'):
                line = line.strip()
                if line.startswith('YANDEX_WEBMASTER_OAUTH_TOKEN='):
                    token = line.split('=', 1)[1].strip().strip('"\'')
    if not token:
        sys.exit('Нет токена: задайте YANDEX_WEBMASTER_OAUTH_TOKEN (env или .env)')
    return token


def api(path: str, token: str, params: dict | None = None) -> dict:
    url = API + path
    if params:
        url += '?' + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={
        'Authorization': f'OAuth {token}',
        'Accept': 'application/json',
    })
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            body = e.read().decode('utf-8', 'replace')
            if e.code == 429 or e.code >= 500:
                time.sleep(2 * (attempt + 1))
                continue
            return {'_error': {'code': e.code, 'body': body}}
        except Exception as e:
            time.sleep(2 * (attempt + 1))
    return {'_error': {'code': 'unreachable'}}


def find_host(hosts: list, domain: str) -> dict | None:
    for h in hosts:
        if domain in (h.get('ascii_host_url') or '') or domain in (h.get('unicode_host_url') or ''):
            return h
    return None


def main() -> None:
    days = DAYS
    if '--days' in sys.argv:
        days = int(sys.argv[sys.argv.index('--days') + 1])
    token = load_token()

    user = api('/user', token)
    uid = user.get('user_id')
    if not uid:
        print('user_id не получен:', user)
        return
    print(f'user_id: {uid}')

    hosts = api(f'/user/{uid}/hosts', token).get('hosts', [])
    host = find_host(hosts, HOST)
    if not host:
        print('zavodsvay.ru не найден в списке сайтов Вебмастера:', [h.get('ascii_host_url') for h in hosts])
        return
    hid = host['host_id']
    print(f'host: {hid} verified={host.get("verified")}')

    date_to = date.today()
    date_from = date_to - timedelta(days=days)
    out = {
        'generated': time.strftime('%Y-%m-%dT%H:%M:%S'),
        'host': host,
    }

    sections = {
        'popular_queries': (f'/user/{uid}/hosts/{hid}/search-queries/popular',
                            {'order_by': 'TOTAL_CLICKS', 'limit': 500, 'device_type_indicator': 'ALL'}),
        'queries_history': (f'/user/{uid}/hosts/{hid}/search-queries/all/history',
                            {'date_from': str(date_from), 'date_to': str(date_to)}),
        'indexing_history': (f'/user/{uid}/hosts/{hid}/indexing/history',
                             {'date_from': str(date_from), 'date_to': str(date_to)}),
        'sqi_history': (f'/user/{uid}/hosts/{hid}/sqi-history',
                        {'date_from': str(date_from), 'date_to': str(date_to)}),
        'sitemaps': (f'/user/{uid}/hosts/{hid}/sitemaps', {}),
        'diagnostics': (f'/user/{uid}/hosts/{hid}/diagnostics', {}),
    }
    for name, (path, params) in sections.items():
        data = api(path, token, params)
        out[name] = data
        err = data.get('_error')
        if err:
            print(f'  {name}: ERROR {err}')
        else:
            n = len(data.get('queries', [])) or 'ok'
            print(f'  {name}: {n}')

    pop = out['popular_queries'].get('queries', [])
    top = pop[:20]
    out['top_queries_history'] = []
    for q in top:
        h = api(f"/user/{uid}/hosts/{hid}/search-queries/{q['query_id']}/history",
                {'date_from': str(date_from), 'date_to': str(date_to)})
        out['top_queries_history'].append({'query_text': q['query_text'], 'history': h})

    path = os.path.join(AUDIT_DIR, f'webmaster-baseline-{date.today():%Y-%m-%d}.json')
    os.makedirs(AUDIT_DIR, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print()
    print(f'baseline: {path}')
    print(f'популярных запросов: {len(pop)}')
    for q in pop[:10]:
        t = q.get('indicators', {})
        print(f"  {q['query_text']:<45} shows={t.get('TOTAL_SHOWS','?'):<8} clicks={t.get('TOTAL_CLICKS','?')}")


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Ежедневный сбор реальных позиций zavodsvay.ru через API Яндекс.Вебмастера.

Для каждого запроса из core.csv собирает страницы сайта, ранжирующиеся по
запросу (text_indicator=URL), по срезам: регион (Пермский край 11108 / все
регионы) × устройство (desktop / mobile_and_tablet). Позиции — реальные
данные поиска Яндекса, в отличие от Search API (другой поток ранжирования).

Данные: data/webmaster/data.json — аккумуляция истории (API отдаёт окно
14 дней, прогоны сливаются по (запрос, регион, устройство, URL, дата);
значения за ту же дату перезаписываются свежим ответом — дата финальна).
"""
import argparse
import csv
import json
import os
import sys
import time
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORE_PATH = os.path.join(ROOT, 'data', 'core', 'core.csv')
DATA_PATH = os.path.join(ROOT, 'data', 'webmaster', 'data.json')
API = 'https://api.webmaster.yandex.net/v4'
SITE = 'https://zavodsvay.ru'

REGION_PERM_KRAI = 11108   # Пермский край (таблица регионов Вебмастера)
REGION_ALL = 'all'         # без region_ids — все регионы

DEVICE_MAP = {'desktop': 'DESKTOP', 'mobile': 'MOBILE_AND_TABLET'}

REQUEST_DELAY = 0.25
MAX_ATTEMPTS = 3


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


def api(method: str, path: str, token: str, body: dict | None = None) -> dict:
    url = API + path
    data = json.dumps(body).encode('utf-8') if body is not None else None
    headers = {'Authorization': f'OAuth {token}', 'Accept': 'application/json'}
    if body is not None:
        headers['Content-Type'] = 'application/json; charset=UTF-8'
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    for attempt in range(MAX_ATTEMPTS):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                raw = r.read().decode('utf-8')
                return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as e:
            raw = e.read().decode('utf-8', 'replace')
            if e.code == 429 or e.code >= 500:
                time.sleep(2 * (attempt + 1))
                continue
            return {'_error': {'code': e.code, 'body': raw}}
        except Exception:
            time.sleep(2 * (attempt + 1))
    return {'_error': {'code': 'unreachable'}}


def read_core() -> list[dict]:
    rows = []
    with open(CORE_PATH, encoding='utf-8-sig') as f:
        for r in csv.reader(f, delimiter=';'):
            if not r or not r[0].strip() or r[0].strip() == 'запрос':
                continue
            rows.append({
                'text': r[0].strip(),
                'приоритет': r[1].strip() if len(r) > 1 else 'med',
                'тип': r[2].strip() if len(r) > 2 else 'коммерческий',
                'приёмник': (r[3].strip() if len(r) > 3 and r[3].strip() else '/'),
                'частота': r[4].strip() if len(r) > 4 else '',
            })
    return rows


def fetch_query_stats(token: str, uid: str, hid: str, query: str,
                      region: int | str, device: str) -> dict:
    body = {
        'offset': 0,
        'limit': 500,
        'device_type_indicator': DEVICE_MAP[device],
        'search_location': 'WEB_LOCATION',
        'text_indicator': 'URL',
        'filters': {
            'text_filters': [
                {'text_indicator': 'QUERY', 'operation': 'TEXT_MATCH', 'value': query}
            ]
        },
    }
    if region != REGION_ALL:
        body['region_ids'] = [region]
    return api('POST', f'/user/{uid}/hosts/{hid}/query-analytics/list', token, body)


def parse_stats(raw: dict) -> dict:
    """{url: {date: {field: value}}} из text_indicator_to_statistics."""
    pages: dict[str, dict] = {}
    for item in raw.get('text_indicator_to_statistics', []):
        ti = item.get('text_indicator', {})
        url = ti.get('value', '') if ti.get('type') == 'URL' else ''
        if not url:
            continue
        day: dict[str, dict] = pages.setdefault(url, {})
        for s in item.get('statistics', []):
            d = s.get('date', '')
            if d not in day:
                day[d] = {}
            day[d][s.get('field', '')] = s.get('value')
    return pages


def normalize_url(url: str) -> str:
    u = url.lower().rstrip('/')
    for p in ('https://', 'http://', 'www.'):
        u = u.replace(p, '')
    return u


def prune(queries: list[dict], window: int) -> None:
    """Устаревшая функция — история аккумулируется, ничего не вырезаем."""
    return


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--query', default=None, help='собрать только один запрос')
    ap.add_argument('--regions', default='11108,all')
    ap.add_argument('--devices', default='desktop,mobile')
    args = ap.parse_args()

    token = load_token()
    user = api('GET', '/user', token)
    uid = user.get('user_id')
    if not uid:
        print('user_id не получен:', user)
        sys.exit(1)

    hosts = api('GET', f'/user/{uid}/hosts', token).get('hosts', [])
    hid = next((h['host_id'] for h in hosts if SITE in (h.get('ascii_host_url') or '')), None)
    if not hid:
        print('zavodsvay.ru не найден в Вебмастере')
        sys.exit(1)

    queries = read_core()
    if args.query:
        queries = [q for q in queries if q['text'] == args.query]
        if not queries:
            print(f'запрос "{args.query}" не найден в ядре')
            sys.exit(1)

    regions = args.regions.split(',')
    devices = args.devices.split(',')

    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    data = {'generated': time.strftime('%Y-%m-%dT%H:%M:%S'), 'status': 'ok',
            'queries': []}
    if os.path.exists(DATA_PATH):
        data = json.load(open(DATA_PATH, encoding='utf-8'))

    by_text = {q['text']: q for q in data.get('queries', [])}

    api_errors = 0
    empty_responses = 0
    total = len(queries) * len(regions) * len(devices)
    done = 0

    for q in queries:
        entry = by_text.get(q['text'])
        if entry is None:
            entry = dict(q)
            entry.setdefault('регионы', {})
            by_text[q['text']] = entry
        for region in regions:
            reg = str(region)
            for device in devices:
                done += 1
                raw = fetch_query_stats(token, uid, hid, q['text'], region, device)
                if '_error' in raw:
                    api_errors += 1
                    print(f'  [{done}/{total}] ERROR {raw["_error"]}')
                    continue
                pages = parse_stats(raw)
                if not pages:
                    empty_responses += 1
                # Аккумуляция: API отдаёт окно 14 дней, история сливается.
                # Значения за ту же дату перезаписываются свежим ответом.
                reg_entry = entry['регионы'].setdefault(reg, {})
                dev_entry = reg_entry.setdefault(device, {})
                for url, day_stats in pages.items():
                    u = normalize_url(url)
                    for d, fields in day_stats.items():
                        dev_entry.setdefault(u, {}).setdefault(d, {}).update(fields)
                time.sleep(REQUEST_DELAY)
        if args.query:
            print(json.dumps(entry, ensure_ascii=False, indent=1)[:3000])

    data['queries'] = list(by_text.values())
    data['generated'] = time.strftime('%Y-%m-%dT%H:%M:%S')
    if api_errors == total:
        data['status'] = 'error'
    elif empty_responses == total:
        data['status'] = 'no-data'
    else:
        data['status'] = 'ok'

    with open(DATA_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=1)

    print(f'запросов: {len(data["queries"])} | срезов: {len(regions)*len(devices)} | '
          f'API-ошибок: {api_errors} | пустых ответов: {empty_responses} | '
          f'статус: {data["status"]}')
    print(f'-> {DATA_PATH}')


if __name__ == '__main__':
    main()

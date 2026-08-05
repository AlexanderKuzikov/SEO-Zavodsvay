#!/usr/bin/env python3
"""Генерация списка запросов для SerpWatcher из семантического ядра.

Читает data/core/core.csv, выводит JSON-массив query-объектов в формате
SerpWatcher (data/projects.json) — готово для мержа в проект zavodsvay.

Использование:
  python scripts/gen_serpwatcher.py [--project id] [--out path]
"""
import argparse
import csv
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORE_PATH = os.path.join(ROOT, 'data', 'core', 'core.csv')
SW_PROJECTS_PATH = os.path.join(ROOT, '..', 'SerpWatcher', 'data', 'projects.json')

TAG_MAP = {
    'коммерческий': 'commercial',
    'информационный': 'info',
    'локальный': 'local',
}

TRANSLIT = {
    'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e',
    'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
    'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
    'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
    'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
}


def slugify(text: str) -> str:
    out = ''.join(TRANSLIT.get(c, c) for c in text.lower())
    return re.sub(r'[^a-z0-9]+', '-', out).strip('-')


def merge_into_projects(queries: list, project_id: str) -> int:
    """Заменяет queries у проекта в SerpWatcher/data/projects.json, остальное не трогает."""
    if not os.path.exists(SW_PROJECTS_PATH):
        print(f'  {SW_PROJECTS_PATH} не найден — мерж пропущен')
        return 0
    with open(SW_PROJECTS_PATH, encoding='utf-8') as f:
        data = json.load(f)
    for p in data:
        if isinstance(p, dict) and p.get('id') == project_id:
            prev = len(p.get('queries', []))
            p['queries'] = queries
            with open(SW_PROJECTS_PATH, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                f.write('\n')
            return prev
    print(f'  проект {project_id} не найден в projects.json — мерж пропущен')
    return 0


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--project', default='zavodsvay')
    ap.add_argument('--out', default=None)
    ap.add_argument('--merge', action='store_true',
                    help='вписать queries в SerpWatcher/data/projects.json (проект --project)')
    args = ap.parse_args()

    with open(CORE_PATH, encoding='utf-8-sig') as f:
        rows = list(csv.reader(f, delimiter=';'))
    if not rows:
        print('core.csv пуст')
        sys.exit(1)

    header = rows[0]
    idx = {h: header.index(h) for h in ['запрос', 'тип', 'приёмник']}
    freq_idx = header.index('частота') if 'частота' in header else -1

    queries = []
    seen = set()
    for r in rows[1:]:
        if len(r) <= max(idx.values()):
            continue
        text = r[idx['запрос']].strip()
        if not text or text in seen:
            continue
        seen.add(text)
        landing = r[idx['приёмник']].strip()
        url = 'https://zavodsvay.ru/' + landing.lstrip('/') if landing else 'https://zavodsvay.ru/'
        tag = TAG_MAP.get(r[idx['тип']].strip(), 'commercial')
        q = {
            'id': slugify(text),
            'text': text,
            'tags': [tag],
            'targetUrl': url,
            'checkFrequency': 'daily',
        }
        if freq_idx >= 0 and r[freq_idx].strip().isdigit():
            q['freq'] = int(r[freq_idx])
        queries.append(q)

    payload = json.dumps(queries, ensure_ascii=False, indent=2)
    out_path = args.out or os.path.join(ROOT, 'data', 'core', f'serpwatcher_{args.project}.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(payload)
    print(f'{len(queries)} запросов -> {out_path}')

    if args.merge:
        prev = merge_into_projects(queries, args.project)
        print(f'projects.json: запросов проекта {args.project}: {prev} -> {len(queries)}')


if __name__ == '__main__':
    main()

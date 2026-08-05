#!/usr/bin/env python3
"""Нормализация выгрузок Wordstat и обогащение семантического ядра частотами.

Использование:
  python scripts/normalize_wordstat.py [файл...]

Без аргументов — берёт все data/wordstat/*.csv, пишет data/wordstat/wordstat_merged.csv
(запрос;частота) и обновляет колонку `частота` в data/core/core.csv по точному
совпадению запроса. Файлы Wordstat: UTF-8 (BOM), разделитель ';', первая строка —
заголовок, вторая колонка — частота.
"""
import csv
import glob
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORDSTAT_DIR = os.path.join(ROOT, 'data', 'wordstat')
CORE_PATH = os.path.join(ROOT, 'data', 'core', 'core.csv')

HEADERS = ['запрос', 'приоритет', 'тип', 'приёмник', 'частота']


def read_wordstat(path: str) -> list[tuple[str, int]]:
    with open(path, encoding='utf-8-sig') as f:
        rows = csv.reader(f, delimiter=';')
        next(rows, None)  # заголовок
        out = []
        for r in rows:
            if len(r) < 2:
                continue
            q, n = r[0].strip(), r[1].strip()
            if q and n.isdigit():
                out.append((q, int(n)))
    return out


def main() -> None:
    paths = sys.argv[1:] or sorted(glob.glob(os.path.join(WORDSTAT_DIR, '*.csv')))
    merged: dict[str, int] = {}
    for p in paths:
        try:
            data = read_wordstat(p)
        except (UnicodeDecodeError, FileNotFoundError) as e:
            print(f'  skip {os.path.basename(p)}: {e}')
            continue
        for q, n in data:
            merged[q] = max(merged.get(q, 0), n)
        print(f'  {os.path.basename(p)}: {len(data)} запросов')

    merged_path = os.path.join(WORDSTAT_DIR, 'wordstat_merged.csv')
    with open(merged_path, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f, delimiter=';')
        w.writerow(['запрос', 'частота'])
        for q, n in sorted(merged.items(), key=lambda x: -x[1]):
            w.writerow([q, n])
    print(f'merged: {len(merged)} запросов -> {merged_path}')

    if not os.path.exists(CORE_PATH):
        print('core.csv не найден — пропускаю обогащение')
        return

    with open(CORE_PATH, encoding='utf-8-sig') as f:
        rows = list(csv.reader(f, delimiter=';'))
    header = rows[0]
    if 'частота' not in header:
        header.append('частота')
        freq_idx = len(header) - 1
        for r in rows[1:]:
            if len(r) < len(header):
                r += [''] * (len(header) - len(r))
    else:
        freq_idx = header.index('частота')
    matched = 0
    for r in rows[1:]:
        q = r[0].strip()
        if q in merged:
            r[freq_idx] = str(merged[q])
            matched += 1
        else:
            r[freq_idx] = r[freq_idx] or ''
    with open(CORE_PATH, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f, delimiter=';')
        w.writerows(rows)
    print(f'core.csv: совпадений с Wordstat {matched}/{len(rows)-1}')


if __name__ == '__main__':
    main()

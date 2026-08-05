# SEO-Zavodsvay — Instructions for AI Agents

## Commands
- normalize-wordstat: `python scripts/normalize_wordstat.py`
- gen-serpwatcher: `python scripts/gen_serpwatcher.py`
- audit-snapshot: ручной прогон аудита сайта, результат → `audits/seo-{YYYY-MM-DD}.json`

## Conventions
- Данные — CSV/JSON, UTF-8. Сырые выгрузки Wordstat — без изменений, в `data/wordstat/`
- Семантическое ядро (SSOT) — `data/core/core.csv`, колонки: `запрос;приоритет;тип;приёмник;частота`
- Частотность — из Wordstat за месяц (все регионы, все устройства), колонка `частота`
- Каждая выгрузка Wordstat копируется с суффиксом даты: `wordstat_*.csv` → `wordstat_*_YYYY-MM-DD.csv`
- SerpWatcher (`D:\GitHub\SerpWatcher\data\projects.json`) генерируется из ядра скриптом — руками не править
- Целевой сайт: zavodsvay.ru, регион 50 (Пермь), Яндекс.Карты JS API не трогать

## Structure
- `data/wordstat/` — сырые выгрузки Wordstat (UTF-8 BOM, разделитель `;`)
- `data/core/` — семантическое ядро (SSOT)
- `audits/` — снимки аудитов сайта по датам
- `scripts/` — Python-скрипты нормализации и генерации

## Do NOT touch
- Сырые выгрузки в `data/wordstat/` после копирования
- `D:\GitHub\SerpWatcher\data\projects.json` руками — только через скрипт
- Секреты и API-ключи (Wordstat API, SerpWatcher .env)

## Documentation rules
- После работы — обнови docs/CONTEXT.md
- Если принял архитектурное решение — запиши в docs/DECISIONS.md
- НЕ создавай новых файлов документации без разрешения
- Переиспользуемые знания — в D:\GitHub\knowledge/README.md

# SEO-Zavodsvay — CONTEXT

> Последнее обновление: 2026-08-05

## Статус
| Компонент | Статус | Версия/Заметка |
|-----------|--------|----------------|
| Структура проекта | создана | data/wordstat, data/core, audits, scripts, docs |
| Wordstat-выгрузки | загружены | top_queries (2000 запросов, ядро «винтовые сваи», 04.07–04.08.2026, все регионы) + similar_queries (15, ядро «свайный фундамент»), копия 2026-08-05; merged-файл 2015 запросов |
| Семантическое ядро | обогащено | `data/core/core.csv` — 54 запроса, 23 с частотностью Wordstat |
| Скрипты | работают | normalize_wordstat.py (обогащение частот), gen_serpwatcher.py (генератор JSON для SerpWatcher, 54 запроса) |
| Аудиты | не начаты | первый снимок — в плане |
| Связь с SerpWatcher | есть | 62 запроса в мониторинге; генератор выдаёт `data/core/serpwatcher_zavodsvay.json` — мерж в projects.json ещё не выполнен |
| GitHub | создан | https://github.com/AlexanderKuzikov/SEO-Zavodsvay, main, запушен |

## Open-проблемы
| # | Priority | Описание |
|---|----------|----------|
| 1 | high | Аудит сайта zavodsvay.ru: 28/30 статей без meta description, дубль title `/articles/` vs `/articles/vidy/`, title объектных страниц 56–132 симв. (норма ≤70). Зафиксировать в `audits/seo-2026-08-05.json`, затем чинить в Zavodsvay-Static |
| 2 | med | Ядро без частот: `core.csv` пока без колонки `частота` — дожен быть обогащён из Wordstat-выгрузок (скрипт normalize_wordstat.py) |
| 3 | med | Wordstat «все регионы» — для регионального продвижения нужна выгрузка по региону 50 (Пермь) |

## Журнал работ
| Дата | Изменение |
|------|-----------|
| 2026-08-05 | Создание проекта: структура, README, AGENTS.md, CONTEXT/DECISIONS. Перенесены выгрузки Wordstat (2 файла) и ядро из Zavodsvay-Static. ADR-001: границы проекта. ADR-002: формат ядра |
| 2026-08-05 | Скрипты + обогащение: normalize_wordstat.py (merged 2015 запросов, частоты в core.csv — 23/54 совпали), gen_serpwatcher.py (54 запроса → serpwatcher_zavodsvay.json). GitHub-репозиторий создан, запушено |

## Структура проекта
```
SEO-Zavodsvay/
├── README.md
├── AGENTS.md
├── data/
│   ├── wordstat/          # сырые выгрузки Wordstat (по датам)
│   └── core/              # семантическое ядро (SSOT: core.csv)
├── audits/                # снимки аудитов сайта по датам
├── scripts/               # Python: normalize_wordstat.py, gen_serpwatcher.py
└── docs/
    ├── CONTEXT.md
    └── DECISIONS.md
```

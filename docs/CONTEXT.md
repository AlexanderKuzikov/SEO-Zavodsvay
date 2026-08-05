# SEO-Zavodsvay — CONTEXT

> Последнее обновление: 2026-08-05

## Статус
| Компонент | Статус | Версия/Заметка |
|-----------|--------|----------------|
| Структура проекта | создана | data/wordstat, data/core, audits, scripts, docs |
| Wordstat-выгрузки | загружены | top_queries (2000 запросов, ядро «винтовые сваи», 04.07–04.08.2026, все регионы) + similar_queries (15, ядро «свайный фундамент»), копия 2026-08-05 |
| Семантическое ядро | перенесено | `data/core/core.csv` — из Zavodsvay-Static `docs/SEO-keywords.csv` (55 запросов, без частот) |
| Аудиты | не начаты | первый снимок — в плане |
| Связь с SerpWatcher | есть | 62 запроса в мониторинге (11 старых + 51 из ядра), генерация скриптом — TODO |
| GitHub | не создан | `gh repo create` — в плане |

## Open-проблемы
| # | Priority | Описание |
|---|----------|----------|
| 1 | high | Аудит сайта zavodsvay.ru: 28/30 статей без meta description, дубль title `/articles/` vs `/articles/vidy/`, title объектных страниц 56–132 симв. (норма ≤70). Зафиксировать в `audits/seo-2026-08-05.json`, затем чинить в Zavodsvay-Static |
| 2 | med | Ядро без частот: `core.csv` пока без колонки `частота` — дожен быть обогащён из Wordstat-выгрузок (скрипт normalize_wordstat.py) |
| 3 | med | Wordstat «все регионы» — для регионального продвижения нужна выгрузка по региону 50 (Пермь) |

## Журнал работ
| Дата | Изменение |
|------|-----------|
| 2026-08-05 | Создание проекта: структура, README, AGENTS.md, CONTEXT/DECISIONS. Перенесены выгрузки Wordstat (2 файла) и ядро из Zavodsvay-Static. ADR-001: границы проекта |

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

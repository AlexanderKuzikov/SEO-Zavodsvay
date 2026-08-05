# SEO-Zavodsvay — CONTEXT

> Последнее обновление: 2026-08-05

## Статус
| Компонент | Статус | Версия/Заметка |
|-----------|--------|----------------|
| Структура проекта | создана | data/wordstat, data/core, audits, scripts, docs |
| Wordstat-выгрузки | загружены | top_queries (2000 запросов, ядро «винтовые сваи», 04.07–04.08.2026, все регионы) + similar_queries (15, ядро «свайный фундамент»), копия 2026-08-05; merged-файл 2015 запросов |
| Семантическое ядро | обогащено | `data/core/core.csv` — 54 запроса, 23 с частотностью Wordstat |
| Скрипты | работают | normalize_wordstat.py (обогащение частот), gen_serpwatcher.py (генератор JSON для SerpWatcher, 54 запроса) |
| Аудиты | baseline создан | `audits/seo-2026-08-05.json` — 6 findings (F-01…F-06), sitemap 567 URL, 529 объектов, 30 статей |
| Вебмастер API | подключён | OAuth-токен в `.env` (gitignored), `scripts/webmaster_baseline.py` работает; `audits/webmaster-baseline-2026-08-05.json` — user_id 119294041, host verified. Данные запросов: HOST_NOT_LOADED (ждём первый обход) |
| Связь с SerpWatcher | есть | 62 запроса в мониторинге; генератор выдаёт `data/core/serpwatcher_zavodsvay.json` — мерж в projects.json ещё не выполнен |
| GitHub | создан | https://github.com/AlexanderKuzikov/SEO-Zavodsvay, main, запушен |

## Open-проблемы
| # | Priority | Описание |
|---|----------|----------|
| 1 | high | Аудит зафиксирован: `audits/seo-2026-08-05.json` (F-01 28/29 статей без description, F-02 дубль title, F-03 title объектов 30–137 симв., F-04 `&quot;` в title, F-05 короткие title статей, F-06 crawl-delay 5.0). Чинить в Zavodsvay-Static: description/title в `partials/head-seo.php` + объектные страницы |
| 2 | med | Ядро без частот: `core.csv` пока без колонки `частота` — дожен быть обогащён из Wordstat-выгрузок (скрипт normalize_wordstat.py) |
| 3 | med | Wordstat «все регионы» — для регионального продвижения нужна выгрузка по региону 50 (Пермь) |
| 4 | med | Вебмастер: sitemap добавлен через API (id 30a4d227), главная на переобходе (task 6779ef50). Повторить `webmaster_baseline.py` через ~24ч — ждём загрузку данных запросов |
| 5 | low | Диагностика Вебмастера: `NO_METRIKA_COUNTER_CRAWL_ENABLED` — в Метрике не включён «сбор данных для краулинга» (настройка счётчика) |

## Журнал работ
| Дата | Изменение |
|------|-----------|
| 2026-08-05 | Создание проекта: структура, README, AGENTS.md, CONTEXT/DECISIONS. Перенесены выгрузки Wordstat (2 файла) и ядро из Zavodsvay-Static. ADR-001: границы проекта. ADR-002: формат ядра |
| 2026-08-05 | Скрипты + обогащение: normalize_wordstat.py (merged 2015 запросов, частоты в core.csv — 23/54 совпали), gen_serpwatcher.py (54 запроса → serpwatcher_zavodsvay.json). GitHub-репозиторий создан, запушено |
| 2026-08-05 | Baseline-аудит: `audits/seo-2026-08-05.json` (живой прогон: robots 200, sitemap 567 URL — 529 объектов/30 статей; 28/29 статей без description; дубль title `/articles/` vs `/articles/vidy/`; 33/40 объектов с title >70; `&quot;` в title объектов; crawl-delay 5.0) |
| 2026-08-05 | Вебмастер: OAuth-приложение «Zavodsvay» (webmaster:hostinfo/verify + metrika), токен в `.env`, `webmaster_baseline.py` (user_id 119294041, host verified, sitemaps [], diagnostics ok). Sitemap добавлен через API (201), recrawl главной (202, квота 700/день) |

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

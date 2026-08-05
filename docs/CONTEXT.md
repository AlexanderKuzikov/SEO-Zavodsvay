# SEO-Zavodsvay — CONTEXT

> Последнее обновление: 2026-08-05

## Статус
| Компонент | Статус | Версия/Заметка |
|-----------|--------|----------------|
| Структура проекта | создана | data/wordstat, data/core, audits, scripts, docs |
| Wordstat-выгрузки | загружены | top_queries (2000 запросов, ядро «винтовые сваи», 04.07–04.08.2026, все регионы) + similar_queries (15, ядро «свайный фундамент»), копия 2026-08-05; merged-файл 2015 запросов |
| Семантическое ядро | расширено | `data/core/core.csv` — 174 запроса (было 54): 111 коммерческих, 56 инфо, 7 локальных; частота у 131. Билдер: `scripts/build_core.py` (ядро + projects.json + курируемые добавления + OVERRIDES приёмников) |
| Скрипты | работают | normalize_wordstat.py (обогащение частот), gen_serpwatcher.py (генератор + `--merge` в projects.json), build_core.py (расширение ядра) |
| Аудиты | baseline создан | `audits/seo-2026-08-05.json` — 6 findings (F-01…F-06), sitemap 567 URL, 529 объектов, 30 статей |
| Вебмастер API | подключён | OAuth-токен в `.env` (gitignored), `scripts/webmaster_baseline.py` работает; `audits/webmaster-baseline-2026-08-05.json` — user_id 119294041, host verified. Данные запросов: HOST_NOT_LOADED (ждём первый обход) |
| Связь с SerpWatcher | merged | 174 запроса в `data/projects.json` (все daily, region 50, freq из Wordstat) |
| Вебмастер-монитор | создан | `scripts/webmaster_monitor.py` (174 запроса × регион 11108/все × desktop/mobile, `data/webmaster/data.json`, окно 14д, срез-замена) + UI `ui/` (vanilla + uPlot, 4 темы × 3 шрифта × 3 масштаба, адаптивный) + `serve_ui.py` (8794, POST /api/collect + GET /api/status). Статус: `no-data` — ждём первый обход сайта (~1–2 дня). Автосбор: Task Scheduler «SEO-Zavodsvay\Webmaster Monitor» ежедневно 07:00 (uv python 3.11.15) |
| GitHub | создан | https://github.com/AlexanderKuzikov/SEO-Zavodsvay, main, запушен |

## Open-проблемы
| # | Priority | Описание |
|---|----------|----------|
| 1 | high | Аудит зафиксирован: `audits/seo-2026-08-05.json` (F-01 28/29 статей без description, F-02 дубль title, F-03 title объектов 30–137 симв., F-04 `&quot;` в title, F-05 короткие title статей, F-06 crawl-delay 5.0). Чинить в Zavodsvay-Static: description/title в `partials/head-seo.php` + объектные страницы |
| 2 | med | Ядро без частот: `core.csv` пока без колонки `частота` — дожен быть обогащён из Wordstat-выгрузок (скрипт normalize_wordstat.py) |
| 3 | med | Wordstat «все регионы» — для регионального продвижения нужна выгрузка по региону 50 (Пермь): 43 запроса ядра (пермские + ВСГ) без частоты |
| 4 | med | Вебмастер: sitemap добавлен через API (id 30a4d227), главная на переобходе (task 6779ef50). Повторить `webmaster_baseline.py` через ~24ч — ждём загрузку данных запросов |
| 5 | low | Диагностика Вебмастера: `NO_METRIKA_COUNTER_CRAWL_ENABLED` — в Метрике не включён «сбор данных для краулинга» (настройка счётчика) |
| 6 | med | Вебмастер-монитор: после первого обхода запустить `webmaster_monitor.py` повторно — ждём реальные позиции; автосбор настроен (Task Scheduler 07:00) |
| 7 | low | UI: фаза 2 — discovery «запросы с показами вне ядра», фильтр направления B2B/B2C |

## Журнал работ
| Дата | Изменение |
|------|-----------|
| 2026-08-05 | Создание проекта: структура, README, AGENTS.md, CONTEXT/DECISIONS. Перенесены выгрузки Wordstat (2 файла) и ядро из Zavodsvay-Static. ADR-001: границы проекта. ADR-002: формат ядра |
| 2026-08-05 | Скрипты + обогащение: normalize_wordstat.py (merged 2015 запросов, частоты в core.csv — 23/54 совпали), gen_serpwatcher.py (54 запроса → serpwatcher_zavodsvay.json). GitHub-репозиторий создан, запушено |
| 2026-08-05 | Baseline-аудит: `audits/seo-2026-08-05.json` (живой прогон: robots 200, sitemap 567 URL — 529 объектов/30 статей; 28/29 статей без description; дубль title `/articles/` vs `/articles/vidy/`; 33/40 объектов с title >70; `&quot;` в title объектов; crawl-delay 5.0) |
| 2026-08-05 | Вебмастер: OAuth-приложение «Zavodsvay» (webmaster:hostinfo/verify + metrika), токен в `.env`, `webmaster_baseline.py` (user_id 119294041, host verified, sitemaps [], diagnostics ok). Sitemap добавлен через API (201), recrawl главной (202, квота 700/день) |
| 2026-08-05 | Ядро расширено: `build_core.py` + `gen_serpwatcher.py --merge` — 54 → 174 запроса (добавлен head-запрос «винтовые сваи» 254771, «сваи винтовые для фундамента» 9474, «расстояние винтовых свай» 2256, диайвай-запросы; OVERRIDES приёмников для пермских) |
| 2026-08-05 | **Вебмастер-монитор** (ADR-003): `webmaster_monitor.py` — 174 запроса × 4 среза (регион 11108/все × desktop/mobile), URL-ориентированный (`text_indicator=URL`, страницы-приёмники), срез-замена, окно 14д; `data/webmaster/data.json`; UI `ui/` — таблица+KPI+карта атаки+график uPlot, переключатели региона/устройства, светлая тема на дизайн-токенах (`ui/tokens.css` → knowledge/design-tokens.md); `serve_ui.py` (8794). Полный прогон: 696 запросов, 0 ошибок, статус no-data (ждём обход). Проверено в браузере: таблица, сортировка, карточка, пустые состояния |
| 2026-08-05 | UI-апгрейд монитора: убраны КАПСы; **4 темы** (light/dark/terminal/shtil) × **3 шрифта** (grotesk/mono/antiqua) × **3 масштаба** (s/m/l) через `data-*`-атрибуты + localStorage (init до отрисовки, без мигания); **адаптивность** (скрытие колонок по брейкпоинтам 1200/960/760px, KPI 3→2→1 колонки, деталь-панель на всю ширину); **сбор из UI**: `serve_ui.py` — POST /api/collect (асинхронный запуск коллектора) + GET /api/status, кнопка «Собрать сейчас» с поллингом; **Task Scheduler** «SEO-Zavodsvay\Webmaster Monitor» ежедневно 07:00 (uv python 3.11.15; python Hermes не используется) |

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

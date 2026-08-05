# SEO-Zavodsvay

<p align="center">Семантическое ядро, Wordstat-данные и аудиты для продвижения zavodsvay.ru</p>

SEO-проект для сайта Завод винтовых свай «Гефест» (zavodsvay.ru). Собирает в одном месте:
выгрузки Яндекс Wordstat, семантическое ядро, снимки аудитов и скрипты синхронизации
с мониторингом позиций (SerpWatcher).

- **Семантическое ядро** — `data/core/core.csv`: запрос, приоритет, тип, страница-приёмник
- **Wordstat-выгрузки** — `data/wordstat/`: сырые CSV из Яндекс Wordstat по датам
- **Аудиты** — `audits/`: снимки SEO-состояния сайта по датам (baseline → diff)
- **Вебмастер-монитор** — реальные позиции по страницам-приёмникам (API Вебмастера, срезы регион×устройство): `data/webmaster/` + UI `ui/`
- **Скрипты** — `scripts/`: нормализация Wordstat, генерация списка для SerpWatcher, сбор Вебмастера

## Быстрый старт

```bash
# Нормализовать свежую выгрузку Wordstat в data/core/
python scripts/normalize_wordstat.py data/wordstat/wordstat_top_queries_*.csv

# Сгенерировать queries для SerpWatcher (data/projects.json)
python scripts/gen_serpwatcher.py

# Ежедневный сбор реальных позиций (174 запроса × регион × устройство)
python scripts/webmaster_monitor.py

# UI монитора — http://127.0.0.1:8794/ui/
python serve_ui.py
```

## Документация

- [`docs/CONTEXT.md`](docs/CONTEXT.md) — состояние проекта
- [`docs/DECISIONS.md`](docs/DECISIONS.md) — архитектурные решения

## Статус

**v0.1.0** — создание: структура, первичные выгрузки Wordstat (05.08.2026), перенос ядра из Zavodsvay-Static.

## Лицензия

Apache-2.0 © Alexander Kuzikov

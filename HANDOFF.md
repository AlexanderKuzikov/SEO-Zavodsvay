# HANDOFF — SEO-Zavodsvay (+ SerpWatcher + Zavodsvay-Static)

> Создан: 2026-08-05 06:10
> Причина: переполнение контекста (~250К), плановый переход сессии

## Текущая задача

SEO-продвижение zavodsvay.ru: решаем в порядке — (1) полный список запросов для продвижения и мониторинга, (2) оптимизация структуры хранения данных, (3) Яндекс.Вебмастер (что брать и как), (4) подключение Яндекс.Метрики.

## Что сделано в этой сессии

- **SEO-Zavodsvay создан и запушен** (github.com/AlexanderKuzikov/SEO-Zavodsvay): структура, 2 выгрузки Wordstat (2000 + 15 запросов), merged 2015, ядро 54 запроса (23 с частотой), скрипты `normalize_wordstat.py` + `gen_serpwatcher.py`, README/AGENTS/CONTEXT/DECISIONS (2 ADR)
- **SerpWatcher**: 62 запроса zavodsvay (все daily), deferred-сбор переведён на параллельность (сабмит 5 воркеров + батч-поллинг), **сортировка по колонкам** в обеих таблицах (не проверена в браузере!), ADR Go+WebView2, CONTEXT обновлён. Сервер НЕ запущен (пользователь убил) — запуск `npm run serve`
- **Zavodsvay-Static**: удалён мусорный объект 530 (map.json + страница + sitemap), SEO-keywords.csv в `docs/`, файл верификации Вебмастера `yandex_9934f8c5e9c5fc79.html` закоммичен, CONTEXT обновлён. Сайт привязан к Яндекс.Вебмастер
- **Аудит сайта (живой)**: 28/30 статей БЕЗ meta description, дубль title `/articles/` vs `/articles/vidy/`, title объектных страниц 56–132 симв. (норма ≤70), sitemap 568 URL, robots ok

## Что осталось сделать

- [ ] **Список запросов**: выгрузить Wordstat по региону 50 (Пермь) → обогатить ядро гео-частотами → расширить ядро до ~150-200 (коммерческие + ВСГ-диаметры + инфо под статьи) → перегенерить для SerpWatcher (62 → больше)
- [ ] **Структура хранения SerpWatcher**: JSONL хранит полную выдачу (100 рез. × запрос, 3 МБ/день, ~1 ГБ/год) — хранить только позицию цели; полный SERP только в снапшоте. Open #2 в CONTEXT
- [ ] **Яндекс.Вебмастер**: OAuth 2.0 токен, эндпоинты (популярные запросы с CTR/позициями, история, ошибки индексации, sitemap, проверка URL). Первый срез → baseline в `audits/`
- [ ] **Яндекс.Метрика**: создать счётчик (нужен ID от пользователя) → вставить код в layouts сайта
- [ ] Проверить сортировку SerpWatcher в браузере (клик по th, направление, null-позиции, спарклайны после сортировки)

## Ключевые файлы

- `D:\GitHub\SEO-Zavodsvay\data\core\core.csv` — ядро (SSOT): запрос;приоритет;тип;приёмник;частота
- `D:\GitHub\SEO-Zavodsvay\scripts\normalize_wordstat.py` — merged + обогащение частот (умеет UTF-8 BOM, `;`)
- `D:\GitHub\SEO-Zavodsvay\scripts\gen_serpwatcher.py` — JSON для SerpWatcher (теги commercial/info/local, targetUrl из приёмника)
- `D:\GitHub\SerpWatcher\data\projects.json` — 62 запроса, ВСЕ daily (пользователь: weekly не нужны)
- `D:\GitHub\SerpWatcher\src\collector\yandex-search-api\collector.ts` — новый параллельный collectDeferred
- `D:\GitHub\Zavodsvay-Static\partials\head-seo.php` — тут живёт meta description (статьи его не задают → пусто)

## Контекст

- **Wordstat-файлы**: UTF-8 BOM, разделитель `;`, колонки `запрос;частота;` (3-я пустая). Формат выгрузки: «Запросы со словами;Число запросов;Топ частотных запросов…»
- **Частоты из merged (топ)**: сваи 254771, купить 40607, цена 23504, установка 16357, дом 11506, монтаж 8333, свайный фундамент 63214 (из similar)
- **Гео-запросы ядра без частот** (нет в общероссийской выгрузке) — 31 шт: «купить винтовые сваи в перми», ВСГ-серия и т.п. → нужен Wordstat по региону 50
- **SerpWatcher регион 50 = Пермь** (город, не край — уточнение из ADR 2026-08-03)
- **Invoke-RestMethod на loopback падает** (прокси) — тестировать через curl.exe
- **Yandex Search API**: >10 запросов → deferred режим (в 16 раз дешевле), лимит сабмита ~10 rps
- Два «.»-коммита в git — агентские, не пугаться; коммиты пользователя идут в main напрямую

## Команды для проверки

```bash
# SEO-Zavodsvay
python scripts/normalize_wordstat.py   # merged + частоты в core.csv
python scripts/gen_serpwatcher.py      # serpwatcher_zavodsvay.json

# SerpWatcher
cd D:\GitHub\SerpWatcher && npm run typecheck && npm test && npm run build
npm run serve                          # http://127.0.0.1:8792

# Zavodsvay-Static
npm run deploy:dry                     # перед деплоем
```

## Следующий шаг

Спросить у пользователя про выгрузку Wordstat по региону 50 (Пермь) — без неё гео-части ядра слепые. Параллельно: зафиксировать первый baseline аудита сайта в `SEO-Zavodsvay/audits/seo-2026-08-05.json` (данные живой проверки выше) — это даст точку отсчёта до правок description статей.

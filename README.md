# Трекер трендов — агент (шаг 3)

Агент по расписанию ищет материалы, классифицирует их по тегам, обновляет
watchlist и радар и записывает `data.json`, который читает дашборд.

Конвейер: **агент → data.json → дашборд**. Работает end-to-end даже без ключей
(демо-режим), реальные API подключаются добавлением секретов.

## Состав

```
agent_tracker/
├─ agent/
│  ├─ config.py      темы, регионы, ключевые слова, источники, теги, watchlist
│  ├─ search.py      веб-поиск (Tavily) или демо-набор без ключа
│  ├─ classify.py    классификация тегов (Claude) или эвристика без ключа
│  ├─ store.py       реестр «виденного» (дедуп) + очередь компаний
│  └─ build.py       оркестратор: собирает и пишет data.json
├─ companies.json    компании, добавленные на дашборде (очередь на анализ)
├─ requirements.txt
├─ .github/workflows/agent.yml   запуск по расписанию (GitHub Actions)
└─ dashboard.html    витрина (кладётся рядом с data.json)
```

## Быстрый старт (локально, без ключей — демо)

```bash
cd agent_tracker
pip install -r requirements.txt
python -m agent.build          # создаст data.json
# затем откройте dashboard.html через локальный сервер:
python -m http.server 8000     # http://localhost:8000/dashboard.html
```

## Подключение реальных данных

Задайте переменные окружения (или секреты в GitHub):

| Переменная | Зачем | Где взять |
|---|---|---|
| `TAVILY_API_KEY` | веб-поиск | tavily.com (есть бесплатный тариф) |
| `ANTHROPIC_API_KEY` | классификация тегов через Claude | console.anthropic.com |

Без `TAVILY_API_KEY` используется встроенный демо-набор; без `ANTHROPIC_API_KEY`
теги проставляются эвристикой по ключевым словам. Можно включать по одному.

Параметры мониторинга правятся в `agent/config.py`: `KEYWORDS` (запросы по
регионам), `SOURCE_WHITELIST`, `WATCHLIST_SEED`, `GLOSSARY_SEED`, `WEEKS`.

## Публикация «по ссылке»

1. Создайте репозиторий на GitHub, положите туда содержимое `agent_tracker/`.
2. В Settings → Secrets добавьте `TAVILY_API_KEY` и `ANTHROPIC_API_KEY`.
3. Включите GitHub Pages (Settings → Pages → ветка main). Дашборд будет
   доступен по `https://<user>.github.io/<repo>/dashboard.html`.
4. Workflow `agent.yml` раз в неделю (или по кнопке в Actions) перезапишет
   `data.json` и запушит его — дашборд подхватит свежие данные.

Расписание меняется строкой `cron` в `.github/workflows/agent.yml`.

## Как это соответствует ТЗ

- Поиск по регионам и белым спискам — `config.KEYWORDS`, `SOURCE_WHITELIST`, `search.py`.
- Классификация по осям тегов — `classify.py`.
- Дедупликация — `store.py` (`seen.json`).
- Watchlist + добавленные компании — `config.WATCHLIST_SEED` + `companies.json`.
- Радар и новые теги — `build.py` (`radar`, `emerging_and_newtags`).
- Глоссарий с подсчётом упоминаний — `build.py` (`glossary`).

## Дальше (по желанию)

Заменить файловое хранилище на Airtable/Supabase: очередь `companies.json` и
реестр `seen.json` переносятся в облачную базу, `build.py` пишет туда и
выгружает публичный `data.json`. Логика агента не меняется.

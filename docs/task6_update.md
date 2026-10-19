# Задание 6. Автоматическое ежедневное обновление базы знаний

## Источник данных
Локальная папка **`data/incoming/`**.

**Подхват:** кладёте новый или изменённый `.md` в `data/incoming/` → `scripts/update_index.py` копирует его в `knowledge_base/`, сравнивает SHA256+mtime с `index/update_state.json` и при изменениях пересобирает FAISS.

## Скрипт
`scripts/update_index.py`:
1. сканирует `data/incoming/` и `knowledge_base/`
2. находит новые/изменённые документы
3. чанки + эмбеддинги (как в Задании 3)
4. обновляет `index/faiss.index` и `docs.pkl` (полная пересборка = удаление устаревших чанков исчезнувших файлов)
5. пишет лог в `logs/index_update.log`

```bash
# тест: добавить документ и обновить
echo '# Test Entity\n\nTest Entity is a probe for daily index updates.' > data/incoming/test_entity.md
python scripts/update_index.py
```

## Периодический запуск (cron)
Файл: `scripts/crontab.example`

| Параметр | Значение |
|---|---|
| Расписание | каждый день в **06:00** (`0 6 * * *`) |
| Команда | `python scripts/update_index.py` |
| При ошибке | `ERROR` в `logs/index_update.log`, stderr в `logs/cron_stderr.log`, повтор на следующем cron |

Установка:
```bash
crontab -e
# вставить строку из scripts/crontab.example (с абсолютным путём)
```

Альтернатива: Docker Compose profile `updater` (цикл sleep 86400).

## Логирование
`logs/index_update.log` — время старта/финиша, число новых файлов, chunks, размер индекса, ошибки.

Пример:
```text
index updated at 2025-07-17, 3 files added, 0 errors
```

## Диаграмма
PlantUML: `docs/diagrams/update_architecture.puml`  
(онлайн: https://www.plantuml.com/plantuml )

# Задание 4. RAG-бот (Few-shot + Chain-of-Thought)

## Пайплайн
1. Запрос пользователя  
2. Эмбеддинг тем же энкодером, что при индексации (`paraphrase-multilingual-MiniLM-L12-v2`)  
3. Поиск top-k в FAISS (`index/faiss.index`)  
4. Промпт: System (CoT) + Few-shot + CONTEXT + вопрос  
5. Генерация: `LLM_MODE=extractive` (по умолчанию) / `openai` / `yandex`

## Модули
| Файл | Роль |
|---|---|
| `src/rag.py` | оркестрация ask() |
| `src/indexing.py` | загрузка индекса и search() |
| `src/prompts.py` | few-shot + CoT |
| `src/llm.py` | генерация ответа |
| `bot/repl.py` | консольный интерфейс |

## Запуск
```bash
python bot/repl.py
```

Опционально REST: `uvicorn bot.api:app --port 8000`  
Опционально LLM: в `.env` задать `LLM_MODE=openai` и `OPENAI_API_KEY=...`

## Примеры диалогов
См. `docs/task4_dialogs.md` (успешные ответы и «Я не знаю»).

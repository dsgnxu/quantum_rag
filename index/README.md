# Задание 3. Векторный индекс

## Модель эмбеддингов
- **Название:** `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
- **Ссылка:** https://huggingface.co/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
- **Размерность:** 384

## База знаний
- Папка: `knowledge_base/` (Aether Nexus, Задание 2)
- Документов: см. `meta.json` → `document_count`

## Индекс
| Файл | Назначение |
|---|---|
| `faiss.index` | FAISS IndexFlatIP (cosine после L2-нормализации) |
| `docs.pkl` | чанки + метаданные: `id`, `source`, `title`, `chunk_index`, `text` |
| `meta.json` | параметры сборки |
| `sample_query.txt` | пример запросов и найденных чанков |

## Чанки
- Сплиттер: LangChain `RecursiveCharacterTextSplitter`
- `chunk_size=800`, `chunk_overlap=120`
- Число чанков и время генерации — в `meta.json` (`chunk_count`, `build_seconds`)

## Сборка и проверка
```bash
pip install faiss-cpu sentence-transformers langchain-text-splitters
python scripts/build_index.py
```

Код: `scripts/build_index.py`, модули `src/indexing.py`, `src/embeddings.py`.

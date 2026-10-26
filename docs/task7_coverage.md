# Задание 7. Аналитика покрытия и качества

## Искусственные пробелы
```bash
python scripts/prepare_gaps.py apply   # убрать Void Core, Xarn Velgor, Synth Flux
python scripts/build_index.py
python scripts/evaluate.py
python scripts/prepare_gaps.py restore # вернуть базу
python scripts/build_index.py
```

## Логирование запросов
Каждый вызов `ask()` → `logs/queries.jsonl`:
`query`, `timestamp`, `chunks_found`, `answer_length`, `success`, `sources`.

## Golden set
`golden_questions.txt` — 8 известных + 3 удалённых + 3 отсутствующих.

## Автотест
`scripts/evaluate.py` → `logs/eval_results.jsonl`, `logs/eval_results.csv`, `docs/coverage_report.md`.

## Диаграмма
`docs/diagrams/eval_sequence.puml` (sequence).

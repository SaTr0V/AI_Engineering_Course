# HW04 – eda_cli: HTTP-сервис качества датасетов (FastAPI)

Расширенная версия проекта `eda-cli` из Домашней работы 03.

К существующему CLI-приложению для EDA добавлен **HTTP-сервис на FastAPI** с эндпоинтами `/health`, `/quality`, `/quality-from-csv`, `/quality-flags-from-csv` и `/head`.  

---

## Связь с HW03

Проект в HW04 основан на том же пакете `eda_cli`, что и в HW03:

- сохраняется структура `src/eda_cli/` и CLI-команда `eda-cli`;
- добавлен модуль `api.py` с FastAPI-приложением;
- в зависимости добавлены `fastapi`, `uvicorn[standard]` и `python-multipart`.

---

## Требования

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) установлен в систему
- Браузер (для Swagger UI `/docs`) или любой HTTP-клиент:
  - `curl` / HTTP-клиент в IDE / Postman / Hoppscotch и т.п.

---

## Инициализация проекта

В корне проекта (каталог HW04/eda-cli):

```bash
uv sync
```

Команда:

- создаст виртуальное окружение `.venv`;
- установит зависимости из `pyproject.toml` (включая FastAPI и Uvicorn);
- установит сам проект `eda-cli` в окружение.

---

## Запуск CLI (как в HW03)

### Краткий обзор

```bash
uv run eda-cli overview data/example.csv
```

Параметры:

- `--sep` – разделитель (по умолчанию `,`);
- `--encoding` – кодировка (по умолчанию `utf-8`).

### Полный EDA-отчёт

```bash
uv run eda-cli report data/example.csv --out-dir reports
```

Параметры:

- `--out-dir` - каталог для отчета (по умолчанию `reports`);
- `--sep` – разделитель (по умолчанию `,`);
- `--encoding` – кодировка (по умолчанию `utf-8`);
- `--max-hist-columns` - максимум числовых колонок для гистограмм (по умолчанию `6`);
- `--title` - название отчета в начале md-файла (по умолчанию `EDA-отчет`);
- `--scoring` - отобразить в отчете подробную информацию о логике score (по умолчанию `no-scoring`).

В результате в каталоге `reports/` появятся:

- `report.md` – основной отчёт в Markdown;
- `summary.csv` – таблица по колонкам;
- `missing.csv` – пропуски по колонкам;
- `correlation.csv` – корреляционная матрица (если есть числовые признаки);
- `top_categories/*.csv` – top-k категорий по строковым признакам;
- `hist_*.png` – гистограммы числовых колонок;
- `missing_matrix.png` – визуализация пропусков;
- `correlation_heatmap.png` – тепловая карта корреляций.

### Печать датасета на экран

```bash
uv run eda-cli head data/example.csv --n 3
```

Параметры:

- `--encoding` – кодировка (по умолчанию `utf-8`);
- `--sep` – разделитель (по умолчанию `,`);
- `--n` - количество строк для вывода (по умолчанию `5`).

---

## Запуск HTTP-сервиса

HTTP-сервис реализован в модуле `eda_cli.api` на FastAPI.

### Запуск Uvicorn

```bash
uv run uvicorn eda_cli.api:app --reload --port 8000
```

Пояснения:

- `eda_cli.api:app` - путь до объекта FastAPI `app` в модуле `eda_cli.api`;
- `--reload` - автоматический перезапуск сервера при изменении кода (удобно для разработки);
- `--port 8000` - порт сервиса (можно поменять при необходимости).

После запуска сервис будет доступен по адресу:

```text
http://127.0.0.1:8000
```

---

## Эндпоинты сервиса

### 1. `GET /health`

Простейший health-check.

**Запрос:**

```http
GET /health
```

**Ожидаемый ответ `200 OK` (JSON):**

```json
{
  "status": "ok",
  "service": "dataset-quality",
  "version": "0.2.0"
}
```

Пример проверки через `curl`:

```bash
curl http://127.0.0.1:8000/health
```

---

### 2. Swagger UI: `GET /docs`

Интерфейс документации и тестирования API:

```text
http://127.0.0.1:8000/docs
```

Через `/docs` можно:

- вызывать `GET /health`;
- вызывать `POST /quality` (форма для JSON);
- вызывать `POST /quality-from-csv` (форма для загрузки файла).

---

### 3. `POST /quality` – заглушка по агрегированным признакам

Эндпоинт принимает **агрегированные признаки датасета** (размеры, доля пропусков и т.п.) и возвращает эвристическую оценку качества.

**Пример запроса:**

```http
POST /quality
Content-Type: application/json
```

Тело:

```json
{
  "n_rows": 10000,
  "n_cols": 12,
  "max_missing_share": 0.15,
  "numeric_cols": 8,
  "categorical_cols": 4
}
```

**Пример ответа `200 OK`:**

```json
{
  "ok_for_model": true,
  "quality_score": 0.8,
  "message": "Данных достаточно, модель можно обучать (по текущим эвристикам).",
  "latency_ms": 3.2,
  "flags": {
    "too_few_rows": false,
    "too_many_columns": false,
    "too_many_missing": false,
    "no_numeric_columns": false,
    "no_categorical_columns": false
  },
  "dataset_shape": {
    "n_rows": 10000,
    "n_cols": 12
  }
}
```

**Пример вызова через `curl`:**

```bash
curl -X POST "http://127.0.0.1:8000/quality" \
  -H "Content-Type: application/json" \
  -d '{"n_rows": 10000, "n_cols": 12, "max_missing_share": 0.15, "numeric_cols": 8, "categorical_cols": 4}'
```

---

### 4. `POST /quality-from-csv` – оценка качества по CSV-файлу

Эндпоинт принимает CSV-файл, внутри:

- читает его в `pandas.DataFrame`;
- вызывает функции из `eda_cli.core`:

  - `summarize_dataset`,
  - `missing_table`,
  - `compute_quality_flags`;
- возвращает оценку качества датасета в том же формате, что `/quality`.

**Запрос:**

```http
POST /quality-from-csv
Content-Type: multipart/form-data
file: <CSV-файл>
```

Через Swagger:

- в `/docs` открыть `POST /quality-from-csv`,
- нажать `Try it out`,
- выбрать файл (например, `data/example.csv`),
- нажать `Execute`.

**Пример вызова через `curl` (Linux/macOS/WSL):**

```bash
curl -X POST "http://127.0.0.1:8000/quality-from-csv" \
  -F "file=@data/example.csv"
```

Ответ будет содержать:

- `ok_for_model` - результат по эвристикам;
- `quality_score` - интегральный скор качества;
- `flags` - булевы флаги из `compute_quality_flags`;
- `dataset_shape` - реальные размеры датасета (`n_rows`, `n_cols`);
- `latency_ms` - время обработки запроса.

---

### 5. `POST /quality-flags-from-csv` - получение всех эвристик качества в виде JSON

Эндпоинт принимает CSV-файл, внутри:

- читает его в `pandas.DataFrame`;
- вызывает функции из `eda_cli.core`:

  - `summarize_dataset`,
  - `missing_table`,
  - `compute_quality_flags`;
- возвращает оценку все флаги в формате JSON.

**Запрос:**

```http
POST /quality-flags-from-csv
Content-Type: multipart/form-data
file: <CSV-файл>
```

Через Swagger:

- в `/docs` открыть `POST /quality-flags-from-csv`,
- нажать `Try it out`,
- выбрать файл (например, `data/example.csv`),
- нажать `Execute`.

**Пример вызова через `curl` (Linux/macOS/WSL):**

```bash
curl -X POST "http://127.0.0.1:8000/quality-flags-from-csv" \
  -F "file=@data/example.csv"
```

Ответ будет содержать:

- `too_few_ros` - флаг, означающий, что датасет имеет слишком мало строк;
- `too_many_columns` - флаг, означающий, что датасет имеет слишком много столбцов;
- `duplicated_rows` - количество строк, являющихся полными дубликатами;
- `has_constant_columns` - флаг, означающий, что в датасете есть столбец с полностью одинаковыми значениями;
- `max_missing_share` - максимальное доля пропусков в столбцах;
- `too_many_missing` - флаг, означающий, что в датасете слишком много пропусков;
- `quality_score` - интегральный скор качества.



**Пример ответа `200 OK`:**

```json
{
  "too_few_rows": true,
  "too_many_columns": false,
  "duplicated_rows": 1,
  "has_constant_columns": false,
  "max_missing_share": 0.05555555555555555,
  "too_many_missing": false,
  "quality_score": 0.6444444444444444
}
```

---

### 6. `POST /head` - просмотр первых n строк датасета в формате JSON

Эндпоинт принимает CSV-файл, внутри считывает его в датафрейм и возвращает первые n строк с помощью `.head()`, преобразованные в словарь.

**Запрос:**

```http
POST /head
Content-Type: multipart/form-data
file: <CSV-файл>
```

Через Swagger:

- в `/docs` открыть `POST /head`,
- нажать `Try it out`,
- выбрать файл (например, `data/example.csv`),
- нажать `Execute`.

**Пример вызова через `curl` (Linux/macOS/WSL):**

```bash
curl -X POST "http://127.0.0.1:8000/head" \
  -F "file=@data/example.csv"
```


## Структура проекта (упрощённо)

```text
HW04/
  eda-cli/
    pyproject.toml
    README.md                # этот файл
    src/
      eda_cli/
        __init__.py
        core.py              # EDA-логика, эвристики качества
        viz.py               # визуализации
        cli.py               # CLI (overview/report)
        api.py               # HTTP-сервис (FastAPI)
    tests/
      test_core.py           # тесты ядра
    data/
      example.csv            # учебный CSV для экспериментов
```

---

## Тесты

Запуск тестов (как и в HW03):

```bash
uv run pytest -q
```

Рекомендуется перед любыми изменениями в логике качества данных и API:

1. Запустить тесты `pytest`;
2. Проверить работу CLI (`uv run eda-cli ...`);
3. Проверить работу HTTP-сервиса (`uv run uvicorn ...`, затем `/health` и `/quality`/`/quality-from-csv` через `/docs` или HTTP-клиент).

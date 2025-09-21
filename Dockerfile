FROM python:3.11-slim

WORKDIR /app

# системные зависимости + sqlite3 CLI (для отладки)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev sqlite3 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# создаём папку для volume (пустую)
RUN mkdir -p /app/data

# НЕ делаем upgrade здесь — volume ещё не примонтирован
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "wsgi:app"]
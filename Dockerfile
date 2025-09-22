# Используем лёгкий python-образ
FROM python:3.9-slim

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    gcc libpq-dev build-essential \
    && rm -rf /var/lib/apt/lists/*

# Создаём рабочую директорию
WORKDIR /app

# Копируем requirements и устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем проект
COPY . .

# Flask запускаем через встроенный сервер (для dev).
# Для продакшена лучше gunicorn, но оставим flask run для начала.
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "cp_app:app"]
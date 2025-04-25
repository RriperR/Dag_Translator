# Используем официальный образ Python
FROM python:3.13-alpine

# Устанавливаем рабочую директорию
WORKDIR /code

# Копируем зависимости
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код бота
COPY . .

# Устанавливаем переменные окружения (настраиваются через docker-compose)
ENV PYTHONUNBUFFERED=1

# Запускаем бота
CMD ["python", "app/run.py"]

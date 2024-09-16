FROM python:3.8-slim

# Установка необходимых системных зависимостей
RUN apt-get update && apt-get install -y gcc libpq-dev

# Установка Python-зависимостей
COPY requirements.txt .
RUN pip install -r requirements.txt

# Копируем код приложения
COPY . /app
WORKDIR /app

# Открываем порт
EXPOSE 8080

# Запуск приложения
CMD ["python", "app.py"]

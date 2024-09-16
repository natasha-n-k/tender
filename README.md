## Tender Service API
##

## Описание

Приложение представляет собой API для управления тендерами и предложениями. Оно позволяет организациям создавать тендеры, публиковать их, редактировать и закрывать, а также принимать и отклонять предложения по тендерам.

## Стек технологий

- Flask (веб-фреймворк)
- SQLAlchemy (ORM)
- PostgreSQL (база данных)
- Docker и Kubernetes (для контейнеризации и оркестрации)
##

## Как запустить проект

```pip install -r requirements.txt```


## Функциональность
Создание, публикация, редактирование и закрытие тендеров.
Создание и редактирование предложений.
Управление версиями тендеров и предложений.
Откат до предыдущих версий тендера или предложения.
Принятие или отклонение предложений.

## Установка

### Локальная установка
- Склонируйте репозиторий:

``git clone https://github.com/ваш-репозиторий.git``

- Установите зависимости:

```pip install -r requirements.txt```

- Настройте базу данных PostgreSQL. Создайте базу данных с именем postgres и пользователя postgres с паролем 1234 (либо настройте свои переменные окружения в файле .env).

- Инициализируйте базу данных:

```python -c "from database import init_db; init_db()"```

- запустите приложение:

```python app.py```

Приложение будет доступно по адресу http://localhost:8080.

### Запуск через Docker
Соберите Docker-образ:

```docker build -t tender-service .```

Запустите контейнеры:

```docker-compose up```

Приложение будет доступно по адресу http://localhost:8080.

### Запуск в Kubernetes
Примените манифесты для деплоя базы данных и приложения:

```kubectl apply -f postgres-deployment.yaml```
```kubectl apply -f postgres-service.yaml```
``` kubectl apply -f app-deployment.yaml```

Проверьте, что сервисы запущены и работают:

```kubectl get pods```
```kubectl get services```

Приложение будет доступно через NodePort или Ingress, в зависимости от вашей настройки Kubernetes.

## Тестирование
Для запуска тестов используйте pytest:

```pytest test_app.py```

##

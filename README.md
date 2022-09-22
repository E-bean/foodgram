# Foodgram - Продуктовый помощник

## Описание:

На этом сервисе пользователи могут публиковать рецепты, подписываться на публикации других пользователей,
добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов,
необходимых для приготовления одного или нескольких выбранных блюд.

## Технологии:
Python 3.7, 
Django 2.2.19, 
PostgreSQL
Docker, 
Nginx

## Как запустить проект:

Шаблон наполнения env-файла:
```
DB_NAME='postgres' # имя базы данных


POSTGRES_USER='postgres' # логин для подключения к базе данных


POSTGRES_PASSWORD='postgres' # пароль для подключения к БД


DB_HOST='db' # название сервиса (контейнера)


DB_PORT='5432' # порт для подключения к БД
```

Перейти в папку infra:

```
cd infra/
```

Запустить контейнеры:

```
docker compose up -d
```

Выполните миграции:

```
docker compose exec backend python manage.py migrate
```
Для создания суперпользователя введите:

```
docker compose exec backend python manage.py createsuperuser
```

Запустите команду для сбора статики:

```
docker compose exec backend python manage.py collectstatic --no-input
```

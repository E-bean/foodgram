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

Клонировать репозиторий с Docker Hub:

```
docker pull kirppu/foodgram:latest
```

Создать и запустить контейнеры:

```
docker run foodgram
```

Выполните миграции:

```
docker-compose exec web python manage.py migrate
```
Для создания суперпользователя введите:

```
docker-compose exec web python manage.py createsuperuser
```

Запустите команду для сбора статики:

```
docker-compose exec web python manage.py collectstatic --no-input
```
Команда для загрузки базы данных из дампа:

```
docker-compose exec web python manage.py loaddata dump.json
```
# Foodgram «Продуктовый помощник»

## Описание

«Foodgram» - это очень удобный и полезный сервис, где пользователи могут публиковать разные рецепты, подписываться на публикации других пользователей и добавлять понравившиеся рецепты в избранное. Самой главной особенностью Foodgram является возможность добавлять рецепты в «Список покупок» и скачать список продуктов для нужного рецепта. Foodgram включает в себя онлайн-сервис и API для него.

### Развернутый проект:

http://51.250.105.138

## Технологический стек

![Django-app workflow](https://github.com/needred/foodgram-project-react/actions/workflows/backend.yml/badge.svg)
[![Python](https://img.shields.io/badge/-Python-464646?style=flat&logo=Python&logoColor=56C0C0&color=008080)](https://www.python.org/)
[![Django](https://img.shields.io/badge/-Django-464646?style=flat&logo=Django&logoColor=56C0C0&color=008080)](https://www.djangoproject.com/)
[![Django REST Framework](https://img.shields.io/badge/-Django%20REST%20Framework-464646?style=flat&logo=Django%20REST%20Framework&logoColor=56C0C0&color=008080)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-464646?style=flat&logo=PostgreSQL&logoColor=56C0C0&color=008080)](https://www.postgresql.org/)
[![Nginx](https://img.shields.io/badge/-NGINX-464646?style=flat&logo=NGINX&logoColor=56C0C0&color=008080)](https://nginx.org/ru/)
[![gunicorn](https://img.shields.io/badge/-gunicorn-464646?style=flat&logo=gunicorn&logoColor=56C0C0&color=008080)](https://gunicorn.org/)
[![Docker](https://img.shields.io/badge/-Docker-464646?style=flat&logo=Docker&logoColor=56C0C0&color=008080)](https://www.docker.com/)
[![Docker-compose](https://img.shields.io/badge/-Docker%20compose-464646?style=flat&logo=Docker&logoColor=56C0C0&color=008080)](https://www.docker.com/)
[![Docker Hub](https://img.shields.io/badge/-Docker%20Hub-464646?style=flat&logo=Docker&logoColor=56C0C0&color=008080)](https://www.docker.com/products/docker-hub)
[![GitHub%20Actions](https://img.shields.io/badge/-GitHub%20Actions-464646?style=flat&logo=GitHub%20actions&logoColor=56C0C0&color=008080)](https://github.com/features/actions)
[![Yandex.Cloud](https://img.shields.io/badge/-Yandex.Cloud-464646?style=flat&logo=Yandex.Cloud&logoColor=56C0C0&color=008080)](https://cloud.yandex.ru/)

## Пользовательские роли

### Гость (неавторизованный пользователь)

Что могут делать неавторизованные пользователи:

- Создать аккаунт.
- Просматривать рецепты на главной.
- Просматривать отдельные страницы рецептов.
- Просматривать страницы пользователей.
- Фильтровать рецепты по тегам.

### Авторизованный пользователь

Что могут делать авторизованные пользователи:

- Входить в систему под своим логином и паролем.
- Выходить из системы (разлогиниваться).
- Менять свой пароль.
- Создавать/редактировать/удалять собственные рецепты
- Просматривать рецепты на главной.
- Просматривать страницы пользователей.
- Просматривать отдельные страницы рецептов.
- Фильтровать рецепты по тегам.
- Работать с персональным списком избранного: добавлять в него рецепты или удалять их, просматривать свою страницу избранных рецептов.
- Работать с персональным списком покупок: добавлять/удалять любые рецепты, выгружать файл со количеством необходимых ингридиентов для рецептов из списка покупок.
- Подписываться на публикации авторов рецептов и отменять подписку, просматривать свою страницу подписок.

### Администратор

Администратор обладает всеми правами авторизованного пользователя. Плюс к этому он может:

- изменять пароль любого пользователя,
- создавать/блокировать/удалять аккаунты пользователей,
- редактировать/удалять любые рецепты,
- добавлять/удалять/редактировать ингредиенты.
- добавлять/удалять/редактировать теги.

### Набор доступных эндпоинтов:

- ```api/docs/redoc``` - Подробная документация по работе API.
- ```api/tags/``` - Получение, списка тегов (GET).
- ```api/ingredients/``` - Получение, списка ингредиентов (GET).
- ```api/ingredients/``` - Получение ингредиента с соответствующим id (GET).
- ```api/tags/{id}``` - Получение, тега с соответствующим id (GET).
- ```api/recipes/``` - Получение списка с рецептами и публикация рецептов (GET, POST).
- ```api/recipes/{id}``` - Получение, изменение, удаление рецепта с соответствующим id (GET, PUT, PATCH, DELETE).
- ```api/recipes/{id}/shopping_cart/``` - Добавление рецепта с соответствующим id в список покупок и удаление из списка (GET, DELETE).
- ```api/recipes/download_shopping_cart/``` - Скачать файл со списком покупок TXT (в дальнейшем появиться поддержка PDF) (GET).
- ```api/recipes/{id}/favorite/``` - Добавление рецепта с соответствующим id в список избранного и его удаление (GET, DELETE).

#### Операции с пользователями:
- ```api/users/``` - получение информации о пользователе и регистрация новых пользователей. (GET, POST).
- ```api/users/{id}/``` - Получение информации о пользователе. (GET).
- ```api/users/me/``` - получение и изменение данных своей учётной записи. Доступна любым авторизованными пользователям (GET).
- ```api/users/set_password/``` - изменение собственного пароля (PATCH).
- ```api/users/{id}/subscribe/``` - Подписаться на пользователя с соответствующим id или отписаться от него. (GET, DELETE).
- ```api/users/subscribe/subscriptions/``` - Просмотр пользователей на которых подписан текущий пользователь. (GET).

#### Аутентификация и создание новых пользователей 👇:
- ```api/auth/token/login/``` - Получение токена (POST).
- ```api/auth/token/logout/``` - Удаление токена (DELETE).

#### Алгоритм регистрации пользователей
1. Пользователь отправляет POST-запрос для регистрации нового пользователя с параметрами
***email username first_name last_name password***
на эндпойнт ```/api/users/```
2. Пользователь отправляет POST-запрос со своими регистрационными данными ***email password*** на эндпоинт ```/api/token/login/``` , в ответе на запрос ему приходит auth-token. Примечание: При взаимодействии с фронтэндом приложения операция два происходит под капотом при переходе по эндпоинту ```/api/token/login/```.

## Об авторе
Ирина Фок [iricshkin](https://github.com/iricshkin/)

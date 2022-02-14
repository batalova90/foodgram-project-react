# Дипломный проект "Сайт публикаций рецептов"
![workflow](https://github.com/batalova90/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg)

## Как запустить проект: 

 
```shell
Перейти в папку /infra 
```
 

Запустить:
```shell
docker-compose up -d
```

 

Применить миграции: 
```shell
docker-compose exec web python manage.py migrate 
```
 

Создать суперпользователя: 
```shell
docker-compose exec web python manage.py createsuperuser 
```
 

Cобрать статические файлы:
```shell
docker-compose exec web python collecstatic --no-input 
```

 

#### Основные доступные эндпоинты можно посмотреть по адресу http://localhost/redoc
#### Адрес проекта: http://51.250.1.131/
#### Admin: email admin@mail.ru; password: foodgram_project

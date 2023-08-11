# Проект Foodgram

Проект Foodgram или «Продуктовый помощник»: сайт, на котором пользователи могут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов.
Сервис «Список покупок» позволяет пользователям создавать список продуктов, которые нужно купить для приготовления выбранных блюд.
Проект доступен по адресу: foodgramblog.hopto.org

## Как запустить проект:

1. Необходимо клонировать репозиторий и перейти в него в командной строке:

```
git clone git@github.com:katyareshetnikova/foodgram-project-react.git
```

2. Cоздать и активировать виртуальное окружение:

```
python3 -m venv env
```

* Если у вас Linux/macOS

    ```
    source venv/bin/activate
    ```

* Если у вас windows

    ```
    source venv/Scripts/activate
    ```

```
python3 -m pip install --upgrade pip
```

3. Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```
4. Перейти в папку с файлом manage.py и выполнить миграции:

```
cd backend
```

```
python3 manage.py migrate
```

5. Заполнить базу тестовыми данными:

```
python manage.py csv_load
```

6. Запустить проект:

```
python manage.py runserver
```

## Данные для входа в админ-панель:

* Логин: ekaterina

* Пароль: lolkek99

## Использованные технологии:

Django REST Framework

Python 3.9.10

React.js

## Разработка backend:

[katyareshetnikova](https://github.com/katyareshetnikova)
# File & eBook Converter — Web App & Bot

## Описание проекта

Многофункциональное приложение на Python + Flask, которое позволяет:

- конвертировать файлы изображений (JPG, PNG, PDF и др.)
- преобразовывать электронные книги (FB2, EPUB, MOBI и др.)
- использовать веб-интерфейс или Telegram-бота

Конвертация eBook осуществляется через Calibre.

## Возможности

- Загрузка файлов через браузер или бота
- Выбор формата для конвертации
- Поддержка jpg, png, pdf, txt, fb2, epub, mobi, azw3, docx
- Автоматическое переименование и скачивание
- Удобный Telegram-бот

## Web-приложение (Flask)

Структура:

project/
├── app.py
├── uploads/
└── templates/
    └— index.html

## Установка

1. Установи Flask и Pillow:

```
pip install flask pillow
```

2. Установи Calibre:
https://calibre-ebook.com/download

3. Проверь путь к ebook-convert в app.py:

```python
calibre_path = r"C:\\Program Files\\Calibre2\\ebook-convert.exe"
```

##  Запуск

```
python app.py
```

Открой: http://127.0.0.1:5000/

## Сборка .exe

```bash
pyinstaller --onefile --add-data "templates;templates" app.py
```

Готовый app.exe будет в dist/

## Telegram-бот

1. Установи:

```bash
pip install python-telegram-bot pillow
```

3. Запусти Bot.py

## Форматы

- Изображения: jpg, jpeg, png, pdf
- Текст: txt, docx
- Электронные книги: fb2, epub, mobi, azw3

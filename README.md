# homework_bot
## Описание
**Homework_bot** — Telegram-бот, который обращается к API сервиса Практикум.Домашка и узнает статус домашней работы: взята ли ваша домашка в ревью, проверена ли она, а если проверена — то принял её ревьюер или вернул на доработку.

## Стек технологий
- pytest
- python-telegram-bot
- requests

## Автор
**Имя:** Эмилар Локтев  
**Telegram:** @itsme_emichka  
**Почта:** emilar-l@yandex.ru  

## Как запустить проект
1. Клонировать репозиторий  
`git clone https://github.com/itsme-emichka/homework_bot`

2. Перейти в директорию проекта  
`cd homework_bot`

3. Создать файл .env со следующими переменными  
- PRACTICUM_TOKEN
- TELEGRAM_TOKEN
- TELEGRAM_CHAT_ID

4. Создать и активировать виртуальное окружение

  1. `python -m venv venv`  
  2. - Windows - `source venv/Scripts/activate`  
     - Linux/MacOS - `source venv/bin/activate`  
  3. Поставить зависимости  
  `pip install -r requirements.txt`  

5. Запустить бота  
`python homework.py` 

import os
import time

import requests
import telegram
import logging

from dotenv import load_dotenv

from exceptions import NoTokenError, IncorrectAnswerError


load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def check_tokens():
    """Проверяет доступность переменных окружения."""
    for token in (PRACTICUM_TOKEN, TELEGRAM_TOKEN):
        if token is None:
            raise NoTokenError


def send_message(bot, message):
    """Отправляет сообщение в Telegram чат."""
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)


def get_api_answer(timestamp):
    """Делает запрос к единственному эндпоинту."""
    params = {'from_date': timestamp}
    return requests.get(
        ENDPOINT,
        params=params,
        headers=HEADERS).json()


def check_response(response):
    """Проверяет ответ API на соответствие документации."""
    try:
        response['current_date']
        response['homeworks']
    except KeyError:
        raise IncorrectAnswerError


def parse_status(homework):
    """Извлекает статус домашней работы."""
    homework_name = homework['homework_name']
    verdict = ['status']

    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    check_tokens()

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())

    check_response(get_api_answer(timestamp))

    while True:
        try:
            response = get_api_answer(timestamp)
            timestamp = response['current_date']
            if response['homeworks']:
                send_message(
                    bot=bot,
                    message=parse_status(response['homeworks'][0]),
                )
            else:
                print('Обновлений нет')

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logging.error(message)

        time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()

import os
import time
import sys
from http import HTTPStatus

import requests
import telegram
import logging

from dotenv import load_dotenv

from exceptions import (
    NoTokenError,
    IncorrectAnswerError,
    EndpointNotAvailable,
    UnknownHomeworkStatus
)


load_dotenv()

formatter = logging.Formatter(
    '''%(asctime)s: [%(levelname)s]
%(message)s'''
)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(formatter)
logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


PRACTICUM_TOKEN: str = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN: str = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID: int = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD: int = 600
ENDPOINT: str = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS: dict[str, str] = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS: dict[str, str] = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def check_tokens() -> None:
    """Проверяет доступность переменных окружения."""
    for token in (PRACTICUM_TOKEN, TELEGRAM_TOKEN):
        if token is None:
            logger.critical('Недоступны переменные окружения!')
            raise NoTokenError('Недоступны переменные окружения!')


def send_message(bot: telegram.Bot, message: str) -> None:
    """Отправляет сообщение в Telegram чат."""
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        logger.debug('Сообщение успешно отправлено')
    except Exception as ex:
        logger.error(f'Не удалось отправить сообщение: {ex}')
        None


def get_api_answer(timestamp: int) -> dict[str, str]:
    """Делает запрос к единственному эндпоинту."""
    params = {'from_date': timestamp}
    try:
        response = requests.get(
            ENDPOINT,
            params=params,
            headers=HEADERS)
        if response.status_code == HTTPStatus.OK:
            return response.json()
        else:
            logger.error(f'Эндпоинт недоступен: {response.status_code}')
            raise EndpointNotAvailable(
                f'Эндпоинт недоступен: {response.status_code}')
    except requests.RequestException as ex:
        logger.error(f'Эндпоинт недоступен: {ex}')
        raise EndpointNotAvailable(f'Эндпоинт недоступен: {ex}')


def check_response(response: dict[str, str]) -> None:
    """Проверяет ответ API на соответствие документации."""
    try:
        response['current_date']
        response['homeworks']
        if type(response['homeworks']) != list:
            raise TypeError
    except KeyError or TypeError:
        logger.error('Ответ не соответствует ожидаемому')
        raise IncorrectAnswerError('Ответ не соответствует ожидаемому')


def parse_status(homework: dict[str, str]) -> str:
    """Извлекает статус домашней работы."""
    try:
        homework_name = homework['homework_name']
    except KeyError:
        logger.error('Ключ "homework_name" недоступен')
        raise KeyError('Ключ "homework_name" недоступен')
    try:
        verdict = HOMEWORK_VERDICTS[homework['status']]
    except KeyError:
        logger.error('Неизвестный статус домашки')
        raise UnknownHomeworkStatus('Неизвестный статус домашки')

    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main() -> None:
    """Основная логика работы бота."""
    check_tokens()

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    last_error = None

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
                logger.debug('Обновлений нет')

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logging.error(message)
            if error != last_error:
                send_message(
                    bot=bot,
                    message=message
                )
            last_error = error

        time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()

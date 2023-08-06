import time
from http import HTTPStatus
from typing import NoReturn

import requests
import telegram
import logging

from exceptions import (
    NoTokenError,
    IncorrectAnswerError,
    EndpointNotAvailable,
    UnknownHomeworkStatus,
    SendMessageError,
)
from config import (
    PRACTICUM_TOKEN,
    TELEGRAM_TOKEN,
    TELEGRAM_CHAT_ID,
    RETRY_PERIOD,
    ENDPOINT,
    HEADERS,
    HOMEWORK_VERDICTS,
)


formatter = logging.Formatter(
    '''%(asctime)s: [%(levelname)s]
%(message)s'''
)
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


def check_tokens() -> None:
    """Проверяет доступность переменных окружения."""
    if not all((PRACTICUM_TOKEN, TELEGRAM_TOKEN)):
        message = 'Недоступны переменные окружения!'
        logger.critical(message)
        raise NoTokenError(message)


def send_message(bot: telegram.Bot, message: str) -> NoReturn:
    """Отправляет сообщение в Telegram чат."""
    logger.debug('Начинаем отправку сообщения...')
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
    except Exception as ex:
        message = f'Не удалось отправить сообщение: {ex}'
        logger.error(message)
        raise SendMessageError(message)
    logger.debug('Сообщение успешно отправлено')


def get_api_answer(timestamp: int) -> dict[str, str]:
    """Делает запрос к единственному эндпоинту."""
    message = 'Эндпоинт недоступен: {}'
    params = {'from_date': timestamp}
    logger.debug('Получаем статусы домашки...')
    try:
        response = requests.get(
            ENDPOINT,
            params=params,
            headers=HEADERS)
    except requests.RequestException as ex:
        logger.error(message.format(ex))
        raise EndpointNotAvailable(message.format(ex))
    if response.status_code == HTTPStatus.OK:
        logger.debug('Статусы успешно получены')
        return response.json()
    logger.error(message.format(response.status_code))
    raise EndpointNotAvailable(message.format(response.status_code))


def check_response(response: dict[str, str]) -> None:
    """Проверяет ответ API на соответствие документации."""
    try:
        if not isinstance(response['homeworks'], list):
            raise TypeError
        if not (('current_date' in response) and ('homeworks' in response)):
            raise KeyError
    except KeyError or TypeError:
        message = 'Ответ не соответствует ожидаемому'
        logger.error(message)
        raise IncorrectAnswerError(message)


def parse_status(homework: dict[str, str]) -> str:
    """Извлекает статус домашней работы."""
    try:
        homework_name = homework['homework_name']
    except KeyError:
        message = 'Ключ "homework_name" недоступен'
        logger.error(message)
        raise KeyError(message)
    try:
        verdict = HOMEWORK_VERDICTS[homework['status']]
    except KeyError:
        message = 'Неизвестный статус домашки'
        logger.error(message)
        raise UnknownHomeworkStatus(message)

    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main() -> NoReturn:
    """Основная логика работы бота."""
    check_tokens()

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    last_error = None
    previous_message = None

    check_response(get_api_answer(timestamp))

    while True:
        try:
            response = get_api_answer(timestamp)
            timestamp = response['current_date']
            if response['homeworks']:
                message = parse_status(response['homeworks'][0])
                if previous_message != message:
                    send_message(
                        bot=bot,
                        message=message,
                    )
                previous_message = message
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

        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()

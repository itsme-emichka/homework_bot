class NoTokenError(Exception):
    """Отсутствует токен."""


class IncorrectAnswerError(Exception):
    """Некорректный ответ сервиса."""


class EndpointNotAvailable(Exception):
    """Эндпоинт недоступен."""


class UnknownHomeworkStatus(Exception):
    """Неизвестный статус домашней работы."""


class SendMessageError(Exception):
    """Ошибка при отправке сообщения."""

class NoTokenError(Exception):
    """Отсутствует токен."""

    pass


class IncorrectAnswerError(Exception):
    """Некорректный ответ сервиса."""

    pass


class EndpointNotAvailable(Exception):
    """Эндпоинт недоступен."""

    pass


class UnknownHomeworkStatus(Exception):
    """Неизвестный статус домашней работы."""

    pass

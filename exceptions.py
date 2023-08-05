class NoTokenError(Exception):
    """Отсутствует токен."""

    pass


class IncorrectAnswerError(Exception):
    """Некорректный ответ сервиса."""

    pass

response = {'curret_date': 2,
            'homeworks': []}


def check_response(response: dict[str, str]) -> None:
    """Проверяет ответ API на соответствие документации."""
    message = 'Ответ не соответствует ожидаемому'
    if ('current_date' not in response) or ('homeworks' not in response):
        print(message)
        raise KeyError(message)

    if not isinstance(response['homeworks'], list):
        print(message)
        raise TypeError(message)


check_response(response)

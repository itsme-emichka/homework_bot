import requests

from pprint import pprint

import telegram


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
YANDEX_TOKEN = 'y0_AgAAAAANv8wGAAYckQAAAADozPtOnAhvjj_JR2SJq3Fl1wVy7WBarVs'
BOT_TOKEN = '6602457576:AAEdyYX4NWIPRT1WnS7-Sjdg1IHkuM1FWfc'
CHAT_ID = 411243245

bot = telegram.Bot(BOT_TOKEN)

params = {'from_date': 0}
headers = {'Authorization': f'OAuth {YANDEX_TOKEN}'}


response = requests.get(ENDPOINT, params=params, headers=headers).json()

pprint(response)

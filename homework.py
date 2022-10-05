import logging
import os
import sys
import time
from http import HTTPStatus
from typing import Dict

import requests
import telegram
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    filename='main.log',
    format='%(asctime)s, %(levelname)s, %(message)s, %{funcName)s, %(lineno)s',
    filemode='a'
)
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.info('Начинаем работать')

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRAKTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_ChAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


class NotSendMessageError(Exception):
    pass


class NonStatusCodeError(Exception):
    pass


class WrongStatusCodeError(Exception):
    pass


def send_message(bot, message):
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        logger.INFO('сообщение отправлено')
    except Exception as error:
        logger.error[f'Ошибка {error}']
        message = 'Сообщение не отправлено'
        raise NotSendMessageError(f'Бот не отправил сообщение {error}')


def get_api_answer(current_timestamp):
    params = {
        'from_date': current_timestamp}
    try:
        response = requests.get(
            url=ENDPOINT,
            headers=HEADERS,
            params=params)
        if response.status_code != HTTPStatus.OK:
            message = 'Ошибка сервера'
            raise NonStatusCodeError(message)
        logger.info('Соединение с сервером установлено')
        return response.json()
    except requests.RequestException as error:
        message = f'Код ответа API (RequestException): {error}'
        raise WrongStatusCodeError(message)
    except ValueError as error:
        message = f'Код ответа API (ValueError): {error}'
        raise WrongStatusCodeError(message)


def check_response(response):
    try:
        response = response['homework']
    except KeyError:
        logger.error('Отсутствует ключ')
        raise KeyError('Отсутствует ключ')


def parse_status(homework):
    if not isinstance(homework, Dict):
        raise TypeError('Это не словарь!')
    homework_name = homework.get('homework_name')
    if homework_name is None:
        raise KeyError('Имя не существует')
    homework_status = homework.get('status')
    if homework_status is None:
        raise KeyError('Статус не существует')
    verdict = HOMEWORK_STATUSES.get(homework_status)
    if verdict is None:
        raise KeyError(f'Ошибка статуса {verdict}')
    logging.info(f'Новый стату работы {verdict}')
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    if PRACTICUM_TOKEN or TELEGRAM_TOKEN or TELEGRAM_CHAT_ID:
        return True
    elif PRACTICUM_TOKEN is None:
        logger.info('Ошибка PRAKTIKUM_TOKEN')
        return False
    elif TELEGRAM_TOKEN is None:
        logger.info('Ошибка TELEGRAM_TOKEN')
        return False
    elif TELEGRAM_CHAT_ID is None:
        logger.info('Ошибка CHAT_ID')
        return False


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        message = 'Отсутствуют токены чата'
        logger.critical(message)
        sys.exit(message)
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = 1663665682
    error_message = ''
    while True:
        try:
            response = get_api_answer(current_timestamp)
            statuses = check_response(response)
            if statuses:
                message = parse_status(statuses)
                if message != error_message:
                    send_message(bot, message)
                    error_message = message
            current_timestamp = response.get('current_date', current_timestamp)
            time.sleep(RETRY_TIME)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logger.error(f'Сбой в работе программы: {error}')
            if message != error_message:
                send_message(bot, message)
                error_message = message
        finally:
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()

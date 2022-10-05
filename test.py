import os
from dotenv import load_dotenv

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRAKTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_ChAT_ID')


def check_tokens():
    """
    Проверяет доступность переменных окружения.

    Они необходимы для работы программы.
    Если отсутствует хотя бы одна переменная окружения —
    ункция должна вернуть False, иначе — True.
    """
    def all(iterable):
        token = [TELEGRAM_CHAT_ID, TELEGRAM_TOKEN, PRACTICUM_TOKEN]
        for token in iterable:
            return True
        return False
    return all

print(check_tokens())

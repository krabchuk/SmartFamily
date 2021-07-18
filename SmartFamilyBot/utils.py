from datetime import datetime
from dateutil import tz
from functools import wraps
import logging
import os

logging.basicConfig(filename='logging.log', format='%(asctime)s %(message)s', level='INFO')

smart_family_users = [
    124575156,  # Lena <3
    49705579,   # Nikita
]

# categories with emoji
regular = "💻📱"
cafe = "🍱🍟"
food = "👨‍🍳👩‍🍳"
clothes = "🧺👗"
meds = "💅🏻💊"
taxi = "🚗🚕"
smth = "🛒🎁"
earnings = "💰 💳"

add_expenses_button = "Add expenses 💸"


def get_category_row(category):
    if category == regular:
        return 2
    if category == food:
        return 3
    if category == cafe:
        return 4
    if category == clothes:
        return 5
    if category == meds:
        return 6
    if category == taxi:
        return 7
    if category == smth:
        return 8


def has_access(user_id):
    if user_id in smart_family_users:
        return True
    else:
        return False


def get_msk_time():
    msk = tz.gettz('UTC+3')
    return datetime.now(msk)


def get_msk_date():
    return str(get_msk_time().day) + '.' + str(get_msk_time().month)


def log_message(func):

    @wraps(func)
    def wrapper(update, *args, **kwargs):
        logging.info(update.message)
        return func(update, *args, **kwargs)

    return wrapper


def check_user(func):

    @wraps(func)
    def wrapper(update, *args, **kwargs):
        if not has_access(update.message.from_user.id):
            update.message.reply_text(f"Your id:{update.message.from_user.id} are not part of SmartFamily :(")
        else:
            return func(update, *args, **kwargs)

    return wrapper


def get_color_from_context(context):
    try:
        if context.user_data["category"] == regular:
            return '#cccccc'
        elif context.user_data["category"] == food:
            if context.user_data["where"] == "Азбука Вкуса":
                return '#34a853'
            elif context.user_data["where"] == "Яндекс.Лавка":
                return '#ffff00'
            elif context.user_data["where"] == "Metro C&C":
                return '#1155cc'
            else:
                return '#a61c00'
        elif context.user_data["category"] == cafe:
            if context.user_data["where"] == "Макдональдс":
                return '#ffd966'
            elif context.user_data["where"] == "Coffix":
                return '#666666'
            else:
                return '#9fc5e8'
        elif context.user_data["category"] == taxi:
            if context.user_data["where"] == "Яндекс.Такси":
                return '#f1c232'
            elif context.user_data["where"] == "Яндекс.Драйв":
                return '#3d85c6'
            else:
                return '#000000'
        elif context.user_data["category"] == clothes:
            return '#dd7e6b'
        elif context.user_data["category"] == meds:
            return '#ff9900'
        elif context.user_data["category"] == smth:
            return '#d5a6bd'
        elif context.user_data["category"] == earnings:
            return '#ff8b36'
    except KeyError:
        return '#000000'


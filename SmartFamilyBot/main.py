from telegram import KeyboardButton, ReplyKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler
import requests
import re

import tokens
from utils import *

try:
    with open('.current_url') as f:
        FINANCE_GOOGLE_SHEET_URL = f.readline().strip()
except FileNotFoundError:
    FINANCE_GOOGLE_SHEET_URL = None

CHOOSE_CATEGORY, ADD_WHERE, ADD_SUM, ADD_DATA = range(4)
SET_URL = 0

default_keyboard = ReplyKeyboardMarkup([
    [KeyboardButton(add_expenses_button)]
], one_time_keyboard=True)


@log_message
@check_user
def start(update: Update, context: CallbackContext):
    update.message.reply_text("Welcome to SmartFamilyBot!", reply_markup=default_keyboard)


@log_message
@check_user
def add_expenses(update: Update, context: CallbackContext):

    if FINANCE_GOOGLE_SHEET_URL is None:
        update.message.reply_text("Url is not set, use /set_url command to update it", reply_markup=default_keyboard)
        return ConversationHandler.END

    keyboard = [
        [KeyboardButton(regular),
         KeyboardButton(food),
         KeyboardButton(cafe)],
        [KeyboardButton(clothes),
         KeyboardButton(meds),
         KeyboardButton(taxi)],
        [KeyboardButton(smth),
         KeyboardButton(earnings)]
    ]

    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    update.message.reply_text("Choose a category:", reply_markup=reply_markup)

    return CHOOSE_CATEGORY


@log_message
@check_user
def chose_category(update: Update, context: CallbackContext):
    text = update.message.text
    if text not in [regular, food, cafe, meds, taxi, smth, earnings, clothes]:
        return dummy_end(update, context)

    context.user_data['category'] = text

    keyboard = None
    if text == food:
        keyboard = [["Азбука Вкуса"], ["Яндекс.Лавка"], ["Metro C&C"]]
    elif text == cafe:
        keyboard = [["Макдональдс"], ["Coffix"]]
    elif text == taxi:
        keyboard = [["Яндекс.Такси"], ["Яндекс.Драйв"]]

    if keyboard:
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
        update.message.reply_text("Where?", reply_markup=reply_markup)
    else:
        update.message.reply_text("Where?")

    return ADD_WHERE


@log_message
@check_user
def add_where(update: Update, context: CallbackContext):
    text = update.message.text
    context.user_data['where'] = text

    update.message.reply_text("How much?")

    return ADD_SUM


@log_message
@check_user
def add_sum(update: Update, context: CallbackContext):
    text = update.message.text
    if not text.isdigit():
        update.message.reply_text("Enter valid digit")
        return ADD_SUM

    context.user_data['sum'] = int(text)
    update.message.reply_text("Additional information?")

    return ADD_DATA


@log_message
@check_user
def add_data(update: Update, context: CallbackContext):
    context.user_data['data'] = update.message.text

    date = get_msk_date()
    text = context.user_data['data']
    b = text.find('(')
    e = text.find(')')
    if b != -1 and e != -1 and text[b + 1:e].isdigit():
        date = text[b + 1:e] + '.' + str(get_msk_time().month)

    try:
        resp = requests.post(FINANCE_GOOGLE_SHEET_URL, data={'date': date,
                                                             'where': context.user_data["where"],
                                                             'sum': str(context.user_data["sum"]),
                                                             'data': context.user_data["data"][:b],
                                                             'sheet': context.user_data["category"],
                                                             'color': get_color_from_context(context)}, timeout=5)
        respExpences = requests.get(FINANCE_GOOGLE_SHEET_URL,
                                    params={'row': get_category_row(context.user_data["category"])}, timeout=5)
    except requests.exceptions.RequestException as e:
        update.message.reply_text(str(e), reply_markup=default_keyboard)
        return ConversationHandler.END

    if resp.status_code == 200 and resp.text == 'ok' and respExpences.status_code == 200:
        update.message.reply_text("Successfully added!")
        update.message.reply_text("Expenses in {}: {}\nTotal expenses: {}".format(context.user_data["category"],
                                                                                  respExpences.text.split(' ')[0],
                                                                                  respExpences.text.split(' ')[1]),
                                  reply_markup=default_keyboard)
    else:
        update.message.reply_text(f"Something went wrong, resp = {resp.status_code},"
                                  f" resp_message = {resp.content}", reply_markup=default_keyboard)

    return ConversationHandler.END


@log_message
@check_user
def sheet_url_start(update: Update, context: CallbackContext):
    update.message.reply_text("Send new Google Sheet url:")

    return SET_URL


@log_message
@check_user
def sheet_url_set(update: Update, context: CallbackContext):
    global FINANCE_GOOGLE_SHEET_URL
    FINANCE_GOOGLE_SHEET_URL = update.message.text
    with open('.current_url', 'w') as f:
        f.write(update.message.text)
    update.message.reply_text('Url was set to "' + FINANCE_GOOGLE_SHEET_URL + '"')

    return ConversationHandler.END


@log_message
@check_user
def dummy_end(update: Update, context: CallbackContext):
    update.message.reply_text("Something went wrong", reply_markup=default_keyboard)

    return ConversationHandler.END


def main():
    updater = Updater(token=tokens.token)

    dispatcher = updater.dispatcher

    conversation_handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.text(add_expenses_button), add_expenses)],
        states={
            CHOOSE_CATEGORY: [
                MessageHandler(
                    Filters.text & ~Filters.command, chose_category
                )
            ],
            ADD_WHERE: [
                MessageHandler(
                    Filters.text & ~Filters.command, add_where
                )
            ],
            ADD_SUM: [
                MessageHandler(
                    Filters.text & ~Filters.command, add_sum
                )
            ],
            ADD_DATA: [
                MessageHandler(
                    Filters.text & ~Filters.command, add_data
                )
            ],
        },
        fallbacks=[MessageHandler(Filters.command, dummy_end)],
        name="add_expenses"
    )

    set_url_handler = ConversationHandler(
        entry_points=[CommandHandler(command="set_url", callback=sheet_url_start)],
        states={
            SET_URL: [
                MessageHandler(
                    Filters.text & ~Filters.command, sheet_url_set
                )
            ],
        },
        fallbacks=[MessageHandler(Filters.command, dummy_end)],
        name="set_url"
    )

    dispatcher.add_handler(conversation_handler)
    dispatcher.add_handler(set_url_handler)
    dispatcher.add_handler(CommandHandler(command="start", callback=start))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()

import logging
import os
import redis
import requests
import moltin
from dotenv import load_dotenv
from telegram.ext import Filters, Updater
from telegram.ext import CallbackQueryHandler, CommandHandler, MessageHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

load_dotenv()

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
MOLTIN_TOKEN = moltin.get_oauth_access_token(CLIENT_ID, CLIENT_SECRET)
REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_PORT = os.getenv('REDIS_PORT')
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')

_database = None

def start(bot, update):
    products_response = moltin.get_products(MOLTIN_TOKEN)
    products = {product['name']: product['id'] for product in products_response}
    keyboard = [[InlineKeyboardButton(key, callback_data=value)] for key, value in products.items()]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Please choose:', reply_markup=reply_markup)
    return 'BUTTON'


def button(bot, update):
    query = update.callback_query
    bot.edit_message_text(text="Selected option: {}".format(query.data),
                          chat_id=query.message.chat_id,
                          message_id=query.message.message_id)
    return 'START'


def handle_menu(bot, update):
    pass


def handle_users_reply(bot, update):
    db = get_database_connection()
    if update.message:
        user_reply = update.message.text
        chat_id = update.message.chat_id
    elif update.callback_query:
        user_reply = update.callback_query.data
        chat_id = update.callback_query.message.chat_id
    else:
        return

    if user_reply == '/start':
        user_state = 'START'
    else:
        user_state = db.get(chat_id).decode("utf-8")

    
    states_functions = {
        'START': start,
        'BUTTON': button,
        'HANDLE_MENU': handle_menu
    }
    state_handler = states_functions[user_state]
    try:
        next_state = state_handler(bot, update)
        db.set(chat_id, next_state)
    except Exception as err:
        print(err)

def get_database_connection():
    global _database
    if _database is None:
        _database = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            password=REDIS_PASSWORD,
            decode_responses=True
        )
        try:
            _database.get('None')
            print('Redis connected.')
        except redis.exceptions.RedisError as error:
            print(error)
    return _database


if __name__ == '__main__':
    token = os.getenv("TELEGRAM_TOKEN")
    updater = Updater(token)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CallbackQueryHandler(handle_users_reply))
    dispatcher.add_handler(MessageHandler(Filters.text, handle_users_reply))
    dispatcher.add_handler(CommandHandler('start', handle_users_reply))
    updater.start_polling()
    updater.idle()

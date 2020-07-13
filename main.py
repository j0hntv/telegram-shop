import logging
import os
import redis
import telegram
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
    keyboard = [
        [InlineKeyboardButton(product_name, callback_data=product_id)] for product_name, product_id in products.items()
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        update.message.reply_text(
            'Выбирайте, пожалуйста:',
            reply_markup=reply_markup
        )
    else:
        chat_id = update.callback_query.message.chat_id
        bot.send_message(
            chat_id=chat_id,
            reply_markup=reply_markup,
            text='Выбирайте, пожалуйста:'
        )

    return 'HANDLE_MENU'


def handle_menu(bot, update):
    query = update.callback_query
    chat_id = query.message.chat_id
    message_id = query.message.message_id

    product_id = query.data
    product = moltin.get_products(MOLTIN_TOKEN, product_id)
    product_image_id = product['relationships']['main_image']['data']['id']
    product_image_url = moltin.get_image_url(MOLTIN_TOKEN, product_image_id)

    caption = moltin.get_product_markdown_output(product)

    keyboard = [
        [InlineKeyboardButton(f'{quantity} шт.', callback_data=f'quantity/{product_id}/{quantity}') for quantity in range(1, 4)],
        [InlineKeyboardButton('🛒 Корзина', callback_data='cart')],
        [InlineKeyboardButton('◀️ Назад', callback_data='back')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    bot.delete_message(chat_id=chat_id, message_id=message_id)
    bot.send_photo(
        chat_id=chat_id,
        photo=product_image_url,
        caption=caption,
        parse_mode=telegram.ParseMode.MARKDOWN,
        reply_markup=reply_markup
    )

    return 'HANDLE_DESCRIPTION'


def handle_description(bot, update):
    query = update.callback_query
    chat_id = query.message.chat_id
    message_id = query.message.message_id

    action = query.data.split('/')

    if action[0] in ('back', 'menu'):
        bot.delete_message(chat_id=chat_id, message_id=message_id)
        return start(bot, update)

    elif action[0] == 'cart':
        cart = moltin.get_a_cart(MOLTIN_TOKEN, chat_id)
        cart_items = moltin.get_cart_items(MOLTIN_TOKEN, chat_id)
        cart_items_formatted = moltin.get_formatted_cart_items(cart, cart_items)

        keyboard = [
            [InlineKeyboardButton(f'❌ Удалить {product["name"]}', callback_data=product['id'])] for product in cart_items
        ] + [[InlineKeyboardButton('◀️ В главное меню', callback_data='menu')]]

        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.delete_message(chat_id=chat_id, message_id=message_id)
        bot.send_message(
            chat_id=chat_id,
            text=cart_items_formatted,
            reply_markup=reply_markup,
            parse_mode=telegram.ParseMode.MARKDOWN)

        return 'HANDLE_CART'

    elif action[0] == 'quantity':
        product_id, quantity = action[1], action[2]
        moltin.add_product_to_cart(MOLTIN_TOKEN, chat_id, product_id, int(quantity))
        return 'HANDLE_DESCRIPTION'


def handle_cart(bot, update):
    query = update.callback_query
    chat_id = query.message.chat_id
    message_id = query.message.message_id

    action = query.data

    if action == 'menu':
        bot.delete_message(chat_id=chat_id, message_id=message_id)
        return start(bot, update)

    return 'HANDLE_DESCRIPTION'


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
        user_state = db.get(chat_id)

    
    states_functions = {
        'START': start,
        'HANDLE_MENU': handle_menu,
        'HANDLE_DESCRIPTION': handle_description,
        'HANDLE_CART': handle_cart
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
    updater = Updater(TELEGRAM_TOKEN)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CallbackQueryHandler(handle_users_reply))
    dispatcher.add_handler(MessageHandler(Filters.text, handle_users_reply))
    dispatcher.add_handler(CommandHandler('start', handle_users_reply))
    updater.start_polling()
    updater.idle()

import os
import dotenv
from pathlib import Path
from telegram.ext import (Updater,
                          CommandHandler,
                          ConversationHandler,
                          MessageHandler,
                          Filters)
#======================================================
from PHPSupport_DB import setup

setup()

import db_api

#=========================================================

dotenv.load_dotenv(Path('venv', '.env'))
customers = ['Vyzlastyle']  # список клиентов
coders = ['MelnikovEI', 'kaser137']  # список программистов
orders = [{'client': 'Vyzlastyle', 'task_text': 'fix my site', 'coder': ''},
          {'client': 'kaser137', 'task_text': 'extend functionality of my blog', 'coder': ''}]  # имитация базы данных
bot_token = os.environ['BOT_TG_TOKEN']

# начало блока функций для разговора с клиентом ========================================================================

N_ORDER, T_ORDER = 0, 1 # точки ветвления разговора


def start_client_talk(update, _):  # функция запускающая разговор
    update.message.reply_text('hello, dear friend, '
                              'type /cancel for stop talking, '
                              'wanna new order? For continue type anything.')
    return N_ORDER


def new_order(update, _):  # функция которая просит текст заказа
    update.message.reply_text('input task text')
    return T_ORDER


def text_new_order(update, _):  # функция которая записывает данные заказа
    user = update.message.from_user.username
    text = update.message.text
    order_attr = {
        'client': user,
        'task_text': text,
        'coder': ''
    }
    orders.append(order_attr)
    print(orders)
    return ConversationHandler.END


def client_cancel(update, _):  # функция прерывающая разговор
    update.message.reply_text('as you want')
    return ConversationHandler.END


# конец блока функций для разговора с клиентом =========================================================================


# начало блока функций для разговора с программистом ===================================================================

E_ORDER, C_ORDER = 0, 1 # точки ветвления разговора


def start_coder_talk(update, _):  # функция запускающая разговор
    update.message.reply_text('hello, dear friend, '
                              'type /cancel for stop talking, '
                              'wanna sea available orders? For continue type anything.')
    return E_ORDER


def expose_orders(update, _):  # функция которая показывает доступные заказы
    for order in orders:
        if not order['coder']:
            update.message.reply_text(f"number of order {orders.index(order)}, client: {order['client']}, "
                                      f"task: {order['task_text']}")
    update.message.reply_text('for choose wanted order input number of order')
    return C_ORDER


def choose_order(update, _):  # функция выбора заказа
    user = update.message.from_user.username
    text = update.message.text
    orders[int(text)]['coder'] = user
    update.message.reply_text(f'thanks, for your choice, '
                              f'your task: {orders[int(text)]["task_text"]}, '
                              f'your client: {orders[int(text)]["client"]}')
    print(orders)
    return ConversationHandler.END


def coder_cancel(update, _):  # функция прерывающая разговор
    update.message.reply_text('as you want')
    return ConversationHandler.END


# конец блока функций для разговора с программистом ====================================================================
def start(update, _):
    username = update.message.chat.username
    if db_api.is_contractor_verified(username):
        update.message.reply_text('wellcome, dear coder /common for coding')
    elif db_api.is_subscription_active(username):
        update.message.reply_text('wellcome, dear client type /begin for cooperate')
    else:
        update.message.reply_text('you have to contact with owners ')
    # if username in customers:
    #     update.message.reply_text('wellcome, dear client type /begin for cooperate')
    # elif username in coders:
    #     update.message.reply_text('wellcome, dear coder /common for coding')
    # else:
    #     update.message.reply_text('you have to contact with owners ')


updater = Updater(token=bot_token)
dispatcher = updater.dispatcher
start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

client_conversation_handler = ConversationHandler(
    entry_points=[CommandHandler('begin', start_client_talk)],
    states={
        N_ORDER: [MessageHandler(Filters.text & (~Filters.command), new_order)],
        T_ORDER: [MessageHandler(Filters.text & (~Filters.command), text_new_order)]
    },
    fallbacks=[CommandHandler('cancel', client_cancel)]
)
dispatcher.add_handler(client_conversation_handler)

coder_conversation_handler = ConversationHandler(
    entry_points=[CommandHandler('common', start_coder_talk)],
    states={
        E_ORDER: [MessageHandler(Filters.text & (~Filters.command), expose_orders)],
        T_ORDER: [MessageHandler(Filters.text & (~Filters.command), choose_order)]
    },
    fallbacks=[CommandHandler('cancel', coder_cancel)]
)
dispatcher.add_handler(coder_conversation_handler)
updater.start_polling()

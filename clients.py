import telegram
from telegram.ext import ConversationHandler

import db_api

C_1, C_2, C_3, C_4, C_5, C_6, C_7, C_8 = range(8)  # точки ветвления разговора
client_processing_order_id = []  # список для  хранения id заказа
client_processing_order_text = []  # список для  хранения текста заказа


def start_client_talk(update, _):  # функция запускающая разговор
    update.message.reply_text('hello, dear friend, '
                              'type /cancel for stop talking, '
                              'for new order type /create\nfor existing order\n type /active\n '
                              'type /accepted for accept order')
    return C_1


# блок создания нового заказа===========================================================================================
def create_order(update, _):  # функция которая просит текст заказа
    update.message.reply_text('input task text in loose format')
    return C_2


def send_order(update, _):  # функция которя записывает текст заказа
    client_processing_order_text.append(update.message.text)
    update.message.reply_text('input necessary access info in loose format')
    return C_5


def send_credits(update, _):  # функция которя записывает данные заказа
    tg_account = update.message.from_user.username
    client_chat_id = update.message.chat.id
    contractor_chat_id = 0
    request = client_processing_order_text[-1]
    access_info = update.message.text
    order_id = db_api.create_order(tg_account, request, access_info, client_chat_id, contractor_chat_id)
    update.message.reply_text(
        f'your order has been check in\nand has id: {order_id}\nyou also can press any command:\n'
        ' /start, /begin, /create, /active, /accepted')
    return ConversationHandler.END


# конец блока создания нового заказа====================================================================================
# ======================================================================================================================
# блок общения по существующему заказу==================================================================================


def expose_active_order(update, _):
    user = update.message.from_user.username
    orders = db_api.get_active_orders(user)
    for order in orders:
        update.message.reply_text(f"""
                                order id: {order['id']},
                                task: {order['request']},
                                Contractor: {'Назначен' if order['contractor_id'] else 'Неназначен'},
                                
                                """
                                  )

    update.message.reply_text('for choose order for working, input order id')
    return C_3


def work_with_order(update, _):
    order_id = int(update.message.text)
    order = db_api.get_order(order_id)
    client_processing_order_id.append(order_id)
    contractor_chat_id = order.contractor_chat_id
    if contractor_chat_id:
        history_of_order = db_api.get_order_info(order_id)['message_history']
        update.message.reply_text(f'history of order: {history_of_order}, \n please, text your message')
        return C_4
    else:
        update.message.reply_text('sorry, this order is still waiting for implementer, you also can press any '
                                  'command:\n /start, /begin, /create, /active, /accepted')
        return ConversationHandler.END


def message_for_coder(update, context):
    order_id = client_processing_order_id[-1]
    order = db_api.get_order(order_id)
    contractor_chat_id = order.contractor_chat_id
    user = order.client.tg_account
    text = update.message.text
    db_api.add_message(order_id, f'{user}: {update.message.text}')
    context.bot.send_message(chat_id=contractor_chat_id, text=f'message from {user}, order id: {order_id} \n' + text)
    update.message.reply_text('your message has been successfully send,\nchao,\n you also can press any command:\n'
                              ' /start, /begin, /create, /active, /accepted')
    return ConversationHandler.END


# конец блока общения по существующему заказу===========================================================================
# блок закрытия заказа===========================================================================================
def accept_order(update, _):
    user = update.message.from_user.username
    orders = db_api.get_active_orders(user)
    update.message.reply_text('choose order for accepting from list below and input order id')
    for order in orders:
        update.message.reply_text(f"""
                                    order id: {order['id']},
                                    task: {order['request']},
                                    Contractor: {'Назначен' if order['contractor_id'] else 'Неназначен'},

                                    """
                                  )
    return C_6


def closing_order(update, context):
    order_id = int(update.message.text)
    order = db_api.get_order(order_id)
    contractor_chat_id = order.contractor_chat_id
    user = order.client.tg_account
    db_api.add_message(order_id, f"you've closed order {order_id}")
    #db_api.close_order(order_id) функция закрытия заказа Евгений еще не написал
    try:
        context.bot.send_message(chat_id=contractor_chat_id, text=f'order id: {order_id}  was accepted by {user}')
        update.message.reply_text('your order has been successfully closed,\nchao,\nyou also can press any command:\n'
                                  ' /start, /begin, /create, /active, /accepted')
    except telegram.error.BadRequest:
        update.message.reply_text('your order was not start for processing, but it has been successfully closed,'
                                  '\nchao,\nyou also can press any command:\n'
                                  ' /start, /begin, /create, /active, /accepted')
    return ConversationHandler.END


# конец блока закрытия заказа===========================================================================================

def client_cancel(update, _):  # функция прерывающая разговор
    update.message.reply_text('as you want')
    return ConversationHandler.END

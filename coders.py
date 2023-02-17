import bd
from telegram.ext import ConversationHandler

# начало блока функций для разговора с программистом ===================================================================

E_ORDER, C_ORDER = 0, 1


def start_coder_talk(update, _):  # функция запускающая разговор
    update.message.reply_text('hello, dear friend, '
                              'type /cancel for stop talking, '
                              'wanna sea available orders? For continue type anything.')
    return E_ORDER


def expose_orders(update, _):  # функция которая показывает доступные заказы
    for order in bd.orders:
        if not order['coder']:
            update.message.reply_text(f"number of order {bd.orders.index(order)}, client: {order['client']}, "
                                      f"task: {order['task_text']}")
    update.message.reply_text('for choose wanted order input number of order')
    return C_ORDER


def choose_order(update, _):  # функция выбора заказа
    user = update.message.from_user.username
    text = update.message.text
    chat_id = update.message.chat.id
    bd.orders[int(text)]['coder'] = user
    bd.orders[int(text)]['coder_chat_id'] = chat_id
    update.message.reply_text(f'thanks, for your choice, '
                              f'your task: {bd.orders[int(text)]["task_text"]}, '
                              f'your client: {bd.orders[int(text)]["client"]}')
    print(bd.orders)
    return ConversationHandler.END


def coder_cancel(update, _):  # функция прерывающая разговор
    update.message.reply_text('as you want')
    return ConversationHandler.END

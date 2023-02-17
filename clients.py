from telegram.ext import ConversationHandler
from PHPSupport_DB import setup
from PHP_support_admin.models import Order

setup()

C_1, C_2, C_3, C_4 = range(4)  # точки ветвления разговора
client_processing_order_id = []  # список для  хранения id заказа


def start_client_talk(update, _):  # функция запускающая разговор
    update.message.reply_text('hello, dear friend, '
                              'type /cancel for stop talking, '
                              'for new order type /create\nfor existing order\n type /active.')
    return C_1


# блок создания нового заказа===========================================================================================
def create_order(update, _):  # функция которая просит текст заказа
    update.message.reply_text('input task text in loose format')
    return C_2


def send_order(update, _):  # функция которя записывает данные заказа
    user = update.message.from_user.username
    chat_id = update.message.chat.id
    text = update.message.text
    order = Order()
    order.client.tg_account = user
    order.request = text
    order.client_chat_id = chat_id
    order.save()
    update.message.reply_text(f'your order has been check in\n and has id: {order.order_id}')
    return ConversationHandler.END


# конец блока создания нового заказа====================================================================================
# ======================================================================================================================
# блок общения по существующему заказу==================================================================================


def expose_active_order(update, _):
    user = update.message.from_user.username
    orders = Order.objects.filter(client__tg_account=user)
    for order in orders:
        update.message.reply_text(f"order id: {order.order_id}, coder: {order.contractor}, "
                                  f"task: {order.request}")
    update.message.reply_text('for choose order for working, input order id')
    return C_3


def work_with_order(update, _):
    order_id = int(update.message.text)
    order = Order.objects.get(order_id=order_id)
    client_processing_order_id.append(order_id)
    coder_chat_id = order.coder_chat_id
    if coder_chat_id:
        history_of_order = order.question
        update.message.reply_text(f'history of order: {history_of_order}, \n please, text your message')
        return C_4
    else:
        update.message.reply_text('sorry, this order is still waiting for implementer')
        return ConversationHandler.END


def message_for_coder(update, context):
    user = update.message.from_user.username
    text = update.message.text
    order_id = client_processing_order_id[-1]
    order = Order.objects.get(order_id=order_id)
    coder_chat_id = order.coder_chat_id
    order.question.create(question=f'{user}: ' + text)
    context.bot.send_message(chat_id=coder_chat_id, text=f'message from {user}, order id: {order_id} \n' + text)
    update.message.reply_text('your message has been successfully send,\nchao')
    return ConversationHandler.END


# конец блока общения по существующему заказу===========================================================================

def client_cancel(update, _):  # функция прерывающая разговор
    update.message.reply_text('as you want')
    return ConversationHandler.END

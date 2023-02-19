import db_api
from telegram.ext import ConversationHandler

# начало блока функций для разговора с программистом ===================================================================

C_1, C_2, C_3, C_4, C_5, C_6, C_7, C_8 = range(8)  # точки ветвления разговора
contractor_processing_order_id = {}  # для  хранения id заказа


def start_coder_talk(update, _):  # функция запускающая разговор
    update.message.reply_text('hello, dear friend,\ntype /cancel for stop talking,\nfor getting info about money type '
                              '/salary\nwanna work with orders? Type /orders')
    return C_1


# money block ============================================================================================
def salary(update, _):
    update.message.reply_text('for tax for order type /order,\nfor month summary type /summary')
    return C_2


def order(update, _):
    order_tax = db_api.get_order_rate()
    update.message.reply_text(f'your tax for order is {order_tax}')
    return ConversationHandler.END


def summary(update, _):
    user = update.message.from_user.username
    summary = db_api.get_current_month_salary(user)
    update.message.reply_text(f'your summary is {summary}')
    return ConversationHandler.END


# end money block=======================================================================================================
# orders block==========================================================================================================
def orders(update, _):
    update.message.reply_text('for active orders type /active_orders,\nfor available type /available')
    return C_3


# active orders ========================================================================================================
def active_orders(update, _):
    user = update.message.from_user.username
    orders = db_api.get_active_contractor_orders(user)
    if not orders:
        update.message.reply_text("You don't have any active orders")
        return C_1

    for order in orders:
        update.message.reply_text(f"""
                                order id: {order['id']},
                                task: {order['request']},
                                Messages: {db_api.get_order_info(order['id'])['message_history']}
                                """
                                  )

    update.message.reply_text('for choose order for working, input order id')
    return C_4


def work_with_order(update, _):
    order_id = int(update.message.text)
    user = update.message.from_user.username
    contractor_processing_order_id[user] = order_id
    # order = db_api.get_contractor_orser(order_id,user)
    # ---<ALARM!!!> временная заглушка тут
    order = db_api.get_order(order_id)
    # --------------------
    if not order:
        update.message.reply_text('You entered an order ID that does not exist')
        return C_3
    update.message.reply_text("""
    type /question to ask question
    type /get_admin for get admin access information
    type /submit to confirm order
    type /cancel for quit
    """)
    return C_5


def submit_order(update, context):
    user = update.message.from_user.username
    order_id = contractor_processing_order_id[user]
    order = db_api.get_order(order_id)
    client_chat_id = order.client_chat_id
    db_api.close_order_by_contractor(order_id)
    # db_api.add_message(order_id, f'contractor {user} has closed order {order_id}')
    context.bot.send_message(chat_id=client_chat_id, text=f' has closed your order {order_id}')
    update.message.reply_text(
        """
        you have closed the order, the customer will be notified about it.
        The order will be considered closed only after confirmation by the customer.
        """
    )
    return ConversationHandler.END


def get_admin(update, _):
    user = update.message.from_user.username
    order_id = contractor_processing_order_id[user]
    order = db_api.get_order(order_id)
    update.message.reply_text(f'necessary credits for access : {order.access_info}')
    return ConversationHandler.END


def ask_question(update, _):
    user = update.message.from_user.username
    order_id = contractor_processing_order_id[user]
    history_of_order = db_api.get_order_info(order_id)['message_history']
    update.message.reply_text(f'message history of order: {history_of_order}, \n please, text your message')
    return C_6


def message_for_client(update, context):
    user = update.message.from_user.username
    order_id = contractor_processing_order_id[user]
    order = db_api.get_order(order_id)
    client_chat_id = order.client_chat_id
    text = update.message.text
    db_api.add_message(order_id, f'contractor {user}: {text}')
    context.bot.send_message(chat_id=client_chat_id, text=f'message from {user}, order id: {order_id} \n' + text)
    update.message.reply_text('your message has been successfully send,\nchao.')
    return ConversationHandler.END


# end active orders=====================================================================================================

# available orders =====================================================================================================
def get_avaliable_orders(update, _):
    orders = db_api.get_available_orders()
    if not orders:
        update.message.reply_text("""Unfortunately, we do not have orders for you.
         Check back a little later, maybe they will show up""")
        return C_3
    for order in orders:
        update.message.reply_text(f"""
                                        order id: {order['id']},
                                        task: {order['request']},
                                        """
                                  )
    update.message.reply_text('for choose order for working, input order id')
    return C_7


def choose_order(update, _):
    order_id = int(update.message.text)
    user = update.message.from_user.username
    contractor_processing_order_id[user] = order_id
    update.message.reply_text(f'input your estimate term of doing order {order_id} in loose format')
    return C_8


def send_estimate_data_confirmation_order(update, context):
    estimate = update.message.text
    user = update.message.from_user.username
    order_id = contractor_processing_order_id[user]
    contractor_chat_id = update.message.chat.id
    order = db_api.get_order(order_id)
    client_chat_id = order.client_chat_id
    if db_api.take_order(tg_account=user,order_id=order_id, contractor_chat_id=contractor_chat_id ,estimation=estimate):
        db_api.add_message(order_id, f'contractor {user} take this order')
        context.bot.send_message(chat_id=client_chat_id,
                                 text=f'your order id: {order_id} has been taken by contractor {user}.')
        update.message.reply_text(f'Congrats, order {order_id} is yours. Access info: {order.access_info}')
    else:
        update.message.reply_text(f'sorry, order {order_id} is taken')
    return ConversationHandler.END


# end available orders =================================================================================================


# end orders block======================================================================================================
def coder_cancel(update, _):  # функция прерывающая разговор
    update.message.reply_text('as you want')
    return ConversationHandler.END

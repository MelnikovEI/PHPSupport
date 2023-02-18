import bd
import telegram
import db_api
from telegram.ext import ConversationHandler

# начало блока функций для разговора с программистом ===================================================================

C_1, C_2, C_3, C_4, C_5, C_6, C_7, C_8 = range(8)  # точки ветвления разговора
coder_processing_order_id = []  # список для  хранения id заказа
coder_processing_order_text = []  # список для  хранения текста заказа


def start_coder_talk(update, _):  # функция запускающая разговор
    update.message.reply_text('hello, dear friend,\ntype /cancel for stop talking,\nfor getting info about money type '
                              '/salary\nwanna work with orders? Type /orders')
    return C_1


# money block ============================================================================================
def salary(update, _):
    update.message.reply_text('for tax for order type /order,\nfor month summary type /summary')
    return C_2


def order(update, _):
    order_tax = db_api.get_order_tax()
    update.message.reply_text(f'your tax for order is {order_tax}')
    return ConversationHandler.END


def summary(update, _):
    summary = db_api.get_summary()
    update.message.reply_text(f'your summary is {summary}')
    return ConversationHandler.END


# end money block=======================================================================================================
# orders block==========================================================================================================
def orders(update, _):
    update.message.reply_text('for active orders type /active,\nfor available type /available')
    return C_3


# active orders ========================================================================================================
def active_orders(update, _):
    user = update.message.from_user.username
    orders = db_api.get_active_contracnor_orders(user)
    for order in orders:
        update.message.reply_text(f"""
                                order id: {order['id']},
                                task: {order['request']},
                                Contractor: {'Назначен' if order['contractor_id'] else 'Неназначен'},
                                Messages: {db_api.get_order_info(order['id'])['message_history']}
                                """
                                  )

    update.message.reply_text('for choose order for working, input order id')
    return C_3

# end orders block======================================================================================================
def coder_cancel(update, _):  # функция прерывающая разговор
    update.message.reply_text('as you want')
    return ConversationHandler.END

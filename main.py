# ===============================================
import os
import dotenv
import clients
# import coders
from pathlib import Path
from telegram.ext import (Updater,
                          CommandHandler,
                          ConversationHandler,
                          MessageHandler,
                          Filters)

import db_api

dotenv.load_dotenv(Path('venv', '.env'))
bot_token = os.environ['BOT_TG_TOKEN']


def start(update, _):
    username = update.message.chat.username
    if db_api.is_contractor_verified(username):
        update.message.reply_text('wellcome, dear coder /common for coding')
    elif db_api.is_subscription_active(username):
        update.message.reply_text('wellcome, dear client type /begin for cooperate')
    else:
        update.message.reply_text('you have to contact with owners ')


updater = Updater(token=bot_token)
dispatcher = updater.dispatcher
start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

client_conversation_handler = ConversationHandler(
    entry_points=[CommandHandler('begin', clients.start_client_talk), CommandHandler('create', clients.create_order),
                  CommandHandler('active', clients.expose_active_order),
                  CommandHandler('accepted', clients.accept_order)],
    states={
        clients.C_1: [CommandHandler('create', clients.create_order),
                      CommandHandler('active', clients.expose_active_order),
                      CommandHandler('accepted', clients.accept_order)],
        clients.C_2: [MessageHandler(Filters.text & (~Filters.command), clients.send_order)],
        clients.C_3: [MessageHandler(Filters.text & (~Filters.command), clients.work_with_order)],
        clients.C_4: [MessageHandler(Filters.text & (~Filters.command), clients.message_for_coder)],
        clients.C_5: [MessageHandler(Filters.text & (~Filters.command), clients.send_credits)],
        clients.C_6: [MessageHandler(Filters.text & (~Filters.command), clients.closing_order)]
    },
    fallbacks=[CommandHandler('cancel', clients.client_cancel)]
)
dispatcher.add_handler(client_conversation_handler)

# coder_conversation_handler = ConversationHandler(
#     entry_points=[CommandHandler('common', coders.start_coder_talk)],
#     states={
#         coders.E_ORDER: [MessageHandler(Filters.text & (~Filters.command), coders.expose_orders)],
#         coders.C_ORDER: [MessageHandler(Filters.text & (~Filters.command), coders.choose_order)]
#     },
#     fallbacks=[CommandHandler('cancel', coders.coder_cancel)]
# )
# dispatcher.add_handler(coder_conversation_handler)
updater.start_polling()

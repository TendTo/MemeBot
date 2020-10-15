"""Main module"""
# region imports
# libs
import os
import warnings
# telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackQueryHandler, ConversationHandler,\
     Filters, Dispatcher, DispatcherHandlerStop
# debug
from modules.debug.log_manager import log_message
# data
from modules.data.data_reader import config_map
# commands
from modules.handlers.command_handlers import STATE, start_cmd, help_cmd, settings_cmd, post_cmd, ban_cmd, reply_cmd,\
    post_msg, rules_cmd, sban_cmd, cancel_cmd
from modules.handlers.callback_handlers import meme_callback
# endregion


def stop():
    """Stop any other handler (unused for now)

    Raises:
        DispatcherHandlerStop: stops any other handler
    """
    print("Stop other Handlers")
    raise DispatcherHandlerStop


def add_handlers(dp: Dispatcher):
    """Add all the needed handlers to the dipatcher

    Args:
        dp (Dispatcher): supplyed dispacther
    """
    if config_map['debug']['local_log']:  # add MessageHandler only if log_message is enabled
        dp.add_handler(MessageHandler(Filters.all, log_message), 1)

    # Command handlers
    dp.add_handler(CommandHandler("start", start_cmd))
    dp.add_handler(CommandHandler("help", help_cmd))
    dp.add_handler(CommandHandler("rules", rules_cmd))
    dp.add_handler(CommandHandler("settings", settings_cmd))
    dp.add_handler(CommandHandler("sban", sban_cmd))

    # Conversation handler
    dp.add_handler(
        ConversationHandler(entry_points=[CommandHandler('post', post_cmd)],
                            states={
                                STATE['posting']: [MessageHandler(Filters.reply & ~Filters.command, post_msg)],
                                STATE['confirm']: [CallbackQueryHandler(meme_callback, pattern=r"meme_confirm_\.*")]
                            },
                            fallbacks=[
                                CommandHandler('cancel', cancel_cmd),
                            ],
                            allow_reentry=True))
    # MessageHandler
    dp.add_handler(MessageHandler(Filters.reply & Filters.regex(r"^/ban$"), ban_cmd))
    dp.add_handler(MessageHandler(Filters.reply & Filters.regex(r"^/reply"), reply_cmd))

    # Callback handlers
    dp.add_handler(CallbackQueryHandler(meme_callback, pattern=r"^meme_\.*"))


def main():
    """Main function
    """

    PORT = int(os.environ.get('PORT', 5000))
    updater = Updater(config_map['token'], request_kwargs={'read_timeout': 20, 'connect_timeout': 20}, use_context=True)
    add_handlers(updater.dispatcher)

    if config_map['webhook']['enabled']:
        updater.start_webhook(listen="0.0.0.0", port=int(PORT), url_path=config_map['token'])
        updater.bot.setWebhook(config_map['webhook']['url'] + config_map['token'])
    else:
        updater.start_polling()

    updater.idle()


warnings.filterwarnings("ignore",
                        message="If 'per_message=False', 'CallbackQueryHandler' will not be tracked for every message.")
if __name__ == "__main__":
    main()

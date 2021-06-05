from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler
from telegram import Update
import random
from states import States
from strings import Strings


class Bot:
    def __init__(self, token):
        self.updater = Updater(token)

        add_handler = ConversationHandler(
            entry_points=[CommandHandler('add_word', self.add_handler, run_async=True)],
            states={
                States.WAITING_WORD: [
                    MessageHandler(Filters.text & ~Filters.command, self.new_word_handler, run_async=True)],
                },
            fallbacks=[CommandHandler('cancel', self.cancel_handler, run_async=True)],
            run_async=True
        )
        test_handler = ConversationHandler(
            entry_points=[CommandHandler('test', self.start_test_handler, run_async=True)],
            states={
                States.WAITING_ANSWER: [
                    MessageHandler(Filters.text & ~Filters.command, self.answer_handler, run_async=True)],
            },
            fallbacks=[CommandHandler('cancel', self.cancel_handler, run_async=True)],
            run_async=True
        )
        self.updater.dispatcher.add_handler(CommandHandler('start', self.start_handler, run_async=True))
        self.updater.dispatcher.add_handler(CommandHandler('show', self.show_handler, run_async=True))
        self.updater.dispatcher.add_handler(add_handler)
        self.updater.dispatcher.add_handler(test_handler)

    def start_handler(self, update: Update, _: CallbackContext):
        update.effective_message.reply_text(
            text=Strings.START,
            parse_mode='HTML'
        )

    def show_handler(self, update: Update, context: CallbackContext):
        mess = ''
        if "dict" not in context.user_data.keys():
            update.effective_message.reply_text(text=Strings.EMPTY, parse_mode='HTML')
            return
        for i in context.user_data["dict"]:
            mess += i[0] + ' - ' + i[1] + '\n'
        update.effective_message.reply_text(mess)

    def add_handler(self, update: Update, _: CallbackContext):
        update.effective_message.reply_text(Strings.ADD_NEW_WORD, parse_mode="HTML")
        return States.WAITING_WORD

    def new_word_handler(self, update: Update, context: CallbackContext):
        mess = update.effective_message.text
        if "dict" not in context.user_data.keys():
            context.user_data["dict"] = []
        if len(mess.splitlines()) != 2:
            update.effective_message.reply_text(Strings.WRONG_WORD, parse_mode="HTML")
            return States.WAITING_WORD
        context.user_data["dict"].append(mess.splitlines())
        update.effective_message.reply_text(Strings.ADDED, parse_mode="HTML")
        return ConversationHandler.END

    def start_test_handler(self, update: Update, context: CallbackContext):
        if "dict" not in context.user_data.keys():
            update.effective_message.reply_text(Strings.WRONG_WORD, parse_mode="HTML")
            return
        update.effective_message.reply_text(Strings.START_TEST, parse_mode="HTML")
        pos = random.choice([0, 1])
        current = random.choice(context.user_data["dict"])
        context.user_data["right"] = current[1 - pos]
        update.effective_message.reply_text(current[pos])
        return States.WAITING_ANSWER

    def answer_handler(self, update: Update, context: CallbackContext):
        mess = update.effective_message.text
        if mess.lower() == context.user_data["right"].lower():
            update.effective_message.reply_text(Strings.RIGHT, parse_mode="HTML")
            pos = random.choice([0, 1])
            current = random.choice(context.user_data["dict"])
            context.user_data["right"] = current[1 - pos]
            update.effective_message.reply_text(current[pos])
        else:
            update.effective_message.reply_text(Strings.WRONG, parse_mode="HTML")
        return States.WAITING_ANSWER

    def cancel_handler(self, update: Update, _: CallbackContext):
        update.effective_message.reply_text(Strings.OperationCancelled)
        return ConversationHandler.END

    def run(self):
        self.updater.start_polling()
        self.updater.idle()

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
            update.effective_message.reply_text(Strings.EMPTY, parse_mode="HTML")
            return
        update.effective_message.reply_text(Strings.START_TEST, parse_mode="HTML")
        context.user_data["cur"] = context.user_data["dict"]
        random.shuffle(context.user_data["cur"])
        context.user_data["test_q"] = []
        context.user_data["test_a"] = []
        for word in context.user_data["cur"]:
            pos = random.randint(0, 1)
            context.user_data["test_q"].append(word[pos])
            context.user_data["test_a"].append(word[1 - pos])

        context.user_data["cur"] = 0
        context.user_data['right'] = 0
        context.user_data['wrong'] = 0
        update.effective_message.reply_text(context.user_data["test_q"][0])
        return States.WAITING_ANSWER

    def answer_handler(self, update: Update, context: CallbackContext):
        mess = update.effective_message.text
        if mess.lower() == context.user_data["test_a"][context.user_data['cur']].lower():
            update.effective_message.reply_text(Strings.RIGHT, parse_mode="HTML")
            context.user_data["cur"] += 1
            context.user_data['right'] += 1
            if context.user_data["cur"] == len(context.user_data["test_q"]):
                update.effective_message.reply_text(f"{Strings.FINISH_TEST}\n???????????????????? ???????????????????? ??????????????: {context.user_data['right']}\n???????????????????? ???????????????????????? ??????????????: {context.user_data['wrong']}\n??????????????!", parse_mode='HTML')
                context.user_data['right'] = 0
                context.user_data['wrong'] = 0
                context.user_data['test_q'] = []
                context.user_data['test_a'] = []
                context.user_data['cur'] = 0
                return ConversationHandler.END
            update.effective_message.reply_text(context.user_data["test_q"][context.user_data['cur']])
        else:
            update.effective_message.reply_text(Strings.WRONG, parse_mode="HTML")
            context.user_data['wrong'] += 1
        return States.WAITING_ANSWER

    def cancel_handler(self, update: Update, context: CallbackContext):
        update.effective_message.reply_text(Strings.OperationCancelled)
        context.user_data['right'] = 0
        context.user_data['wrong'] = 0
        context.user_data['test_q'] = []
        context.user_data['test_a'] = []
        context.user_data['cur'] = 0
        return ConversationHandler.END

    def run(self):
        self.updater.start_polling()
        self.updater.idle()

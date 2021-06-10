#!/usr/bin/env python3
import datetime
import json
import logging
import random

from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

from authorization import bot_token
from bot_responses import help_message, start_message

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    update.message.reply_markdown_v2(f"Hi {user.mention_markdown_v2()}\!\n"
                                     f"{start_message}",
                                     reply_markup=None)


def help_command(update: Update, context: CallbackContext):
    update.message.reply_text(help_message)


class PhrasalVerb:
    def __init__(self):
        with open('phrasal_verbs.json', 'r') as pv_file:
            verbs = json.load(pv_file)

        self.prepare = {str(f"{verb['verb']} {verb['prep']}"): [
            {'definition': str(verb['definition']),
             'synonyms': f"{', '.join(verb['synonyms'])}",
             'examples': f"{';'.join(verb['examples'])}"}]
            for verb in verbs}
        self.response = str()

    def send_start_message(self, update: Update, context: CallbackContext):
        self.response = random.choice([key for key in self.prepare])
        daily_response = f"Today's phrasal verb:  {self.response.capitalize()}." \
                         f"\nClick -> /definition to get a definition;" \
                         f"\nClick -> /synonyms to get a synonyms;" \
                         f"\nClick -> /examples to get examples." \
                         f"\nClick -> /notify."
        update.message.reply_text(daily_response)

    def pv_definition(self, update: Update, context: CallbackContext):
        update.message.reply_text(
            f"Definition:\n{self.prepare[self.response][0]['definition'].capitalize()}.")

    def pv_synonyms(self, update: Update, context: CallbackContext):
        update.message.reply_text(
            f"Synonyms:\n{self.prepare[self.response][0]['synonyms']}.")

    def pv_examples(self, update: Update, context: CallbackContext):
        if self.prepare[self.response][0]['examples']:
            update.message.reply_text(
                f"Examples:\n{self.prepare[self.response][0]['examples']}")
        else:
            update.message.reply_text(f"Sorry, no examples for today's verb")


chat = PhrasalVerb()


def run_daily(update: Update, context: CallbackContext):
    updater.bot.send_message(chat_id=update.message.chat_id, text="Test")


def daily_job(update: Update, context: CallbackContext):
    updater.bot.send_message(chat_id=update.message.chat_id,
                             text="Setting a daily notifications!")
    updater.job_queue.run_daily(run_daily,
                                time=datetime.time(20, 49, 00),
                                days=(0, 1, 2, 3, 4, 5, 6),
                                context=update.message.chat_id)


updater = Updater(bot_token, use_context=True)
dispatcher = updater.dispatcher

dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("help", help_command))
dispatcher.add_handler(CommandHandler("lets_start", chat.send_start_message))
dispatcher.add_handler(CommandHandler("definition", chat.pv_definition))
dispatcher.add_handler(CommandHandler("synonyms", chat.pv_synonyms))
dispatcher.add_handler(CommandHandler("examples", chat.pv_examples))
dispatcher.add_handler(CommandHandler('notify', daily_job, pass_job_queue=True))

updater.start_polling()
updater.idle()

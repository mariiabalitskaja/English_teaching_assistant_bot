#!/usr/bin/env python3
import json
import logging
import random

from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

from authorization import bot_token
from bot_responses import help_message, start_message, response_with_pv

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
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
        with open("phrasal_verbs.json", "r") as pv_file:
            verbs = json.load(pv_file)

        self.prepare = {str(f"{verb['verb']} {verb['prep']}"): [
            {'definition': str(verb['definition']),
             'synonyms': f"{', '.join(verb['synonyms'])}",
             'examples': f"{';'.join(verb['examples'])}"}]
            for verb in verbs}
        self.pv = str()

    def send_start_message(self, update: Update, context: CallbackContext):
        self.pv = random.choice([key for key in self.prepare])
        response = f"Today's phrasal verb:  {self.pv.capitalize()}{response_with_pv}."
        update.message.reply_text(response)

    def pv_definition(self, update: Update, context: CallbackContext):
        update.message.reply_text(
            f"Definition:\n{self.prepare[self.pv][0]['definition'].capitalize()}.")

    def pv_synonyms(self, update: Update, context: CallbackContext):
        update.message.reply_text(
            f"Synonyms:\n{self.prepare[self.pv][0]['synonyms']}.")

    def pv_examples(self, update: Update, context: CallbackContext):
        if self.prepare[self.pv][0]['examples']:
            update.message.reply_text(
                f"Examples:\n{self.prepare[self.pv][0]['examples']}")
        else:
            update.message.reply_text(f"Sorry, no examples for getting verb.")


chat = PhrasalVerb()


def main():
    updater = Updater(bot_token, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(
        CommandHandler("send_me_phrasal_verb", chat.send_start_message))
    dispatcher.add_handler(CommandHandler("definition", chat.pv_definition))
    dispatcher.add_handler(CommandHandler("synonyms", chat.pv_synonyms))
    dispatcher.add_handler(CommandHandler("examples", chat.pv_examples))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()

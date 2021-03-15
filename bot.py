#!/usr/bin/env python3

import logging
import re
import sys

from uuid import uuid4

from telegram import Update, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import Updater, Dispatcher, InlineQueryHandler, CallbackContext


class SpongeBobSarcasmBot:
    _logger: logging.Logger
    _updater: Updater
    _dispatcher: Dispatcher

    def __init__(self, token: str):
        self._logger = logging.getLogger(self.__class__.__name__)

        self._updater = Updater(token=token)
        self._dispatcher = self._updater.dispatcher

        self._dispatcher.add_handler(InlineQueryHandler(self._handle_call))

    def run(self, run_in_background=False):
        self._updater.start_polling()
        if not run_in_background:
            self._updater.idle()

    @staticmethod
    def sarcasmize(text: str) -> str:
        # Empty strings
        if not text:
            return text

        text = list(text)
        isupper = text[0].isupper()

        for i, c in enumerate(text):
            if isupper:
                text[i] = c.upper()
            else:
                text[i] = c.lower()

            if i == 0:
                isupper = not isupper
            else:
                # We want to avoid "lI" and "Il"
                if text[i - 1] == "l" and text[i] == "I":
                    text[i - 1] = "L"
                    text[i] = "i"
                    isupper = True
                elif text[i - 1] == "I" and text[i] == "l":
                    text[i - 1] = "i"
                    text[i] = "L"
                    isupper = False
                else:
                    isupper = not isupper

        return "".join(text)

    def _handle_call(self, update: Update, _: CallbackContext) -> None:
        query = update.inline_query.query
        if not query:
            return

        sarcastic = self.sarcasmize(query)
        results = [
            InlineQueryResultArticle(
                id=str(uuid4()),
                title=sarcastic,
                input_message_content=InputTextMessageContent(sarcastic),
            )
        ]

        update.inline_query.answer(results)


def main():
    logging.basicConfig(level=logging.INFO)

    with open(".telegram-token") as fh:
        token = fh.read().strip()

    bot = SpongeBobSarcasmBot(token)
    bot.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())

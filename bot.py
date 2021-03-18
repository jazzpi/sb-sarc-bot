#!/usr/bin/env python3

import logging
import re
import sys

from uuid import uuid4

from telegram import Update, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import Updater, Dispatcher, InlineQueryHandler, CallbackContext


WHITESPACE_GROUP = re.compile("(\s+)")
LINK_PATTERN = re.compile(r"(?:\w+://)?[\w-]+\.[\w-]{2,}")


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

    @classmethod
    def sarcasmize_word(cls, word: str) -> str:
        word = list(word)
        isupper = word[0].isupper()

        for i, c in enumerate(word):
            if isupper:
                word[i] = c.upper()
            else:
                word[i] = c.lower()

            if i == 0:
                isupper = not isupper
            else:
                # We want to avoid "lI" and "Il"
                if word[i - 1] == "l" and word[i] == "I":
                    word[i - 1] = "L"
                    word[i] = "i"
                    isupper = True
                elif word[i - 1] == "I" and word[i] == "l":
                    word[i - 1] = "i"
                    word[i] = "L"
                    isupper = False
                else:
                    isupper = not isupper

        return "".join(word)

    @classmethod
    def sarcasmize_text(cls, text: str) -> str:
        # Split on whitespace, but keep information about the whitespace so we
        # can later reassemble the text with the original whitespace.
        # str.split() doesn't allow us to do this.
        exploded = re.split(WHITESPACE_GROUP, text)

        for i, word in enumerate(exploded):
            # Ignore empty strings (could happen at the beginning)
            if not word:
                continue
            # If the first character is a space, they all are -> ignore
            if word[0].isspace():
                continue
            # Don't mess with links
            if re.match(LINK_PATTERN, word) is not None:
                continue

            exploded[i] = cls.sarcasmize_word(word)

        return "".join(exploded)

    def _handle_call(self, update: Update, _: CallbackContext) -> None:
        query = update.inline_query.query
        if not query:
            return

        sarcastic = self.sarcasmize_text(query)
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

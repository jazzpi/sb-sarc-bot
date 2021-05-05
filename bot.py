#!/usr/bin/env python3

import logging
import re
import sys

from uuid import uuid4

from telegram import (
    Update,
    InlineQueryResultArticle,
    InlineQueryResultCachedPhoto,
    InputTextMessageContent,
)
from telegram.ext import (
    Updater,
    Dispatcher,
    InlineQueryHandler,
    CallbackContext,
    CommandHandler,
)


WHITESPACE_GROUP = re.compile("(\s+)")
LINK_PATTERN = re.compile(r"(?:\w+://)?[\w-]+\.[\w-]{2,}")


class SpongeBobSarcasmBot:
    _logger: logging.Logger
    _updater: Updater
    _dispatcher: Dispatcher
    _photo_id: str

    def __init__(self, token: str, photo_id: str = None):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._photo_id = photo_id

        self._updater = Updater(token=token)
        self._dispatcher = self._updater.dispatcher

        self._dispatcher.add_handler(InlineQueryHandler(self._handle_call))
        self._dispatcher.add_handler(CommandHandler("getimg", self._handle_getimg))

    def _handle_getimg(self, update: Update, _: CallbackContext):
        photos = update.message.reply_photo(
            "https://danny.page/assets/images/mocking-spongebob.jpg"
        )
        for photo in photos.photo:
            photos.reply_text(f"File of size {photo.file_size}: {photo.file_id}")

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
            ),
        ]
        if self._photo_id is not None:
            results.append(
                InlineQueryResultCachedPhoto(
                    id=str(uuid4()),
                    photo_file_id=self._photo_id,
                    title=sarcastic,
                    caption=sarcastic,
                )
            )

        update.inline_query.answer(results)


def main():
    logging.basicConfig(level=logging.INFO)

    with open(".telegram-token") as fh:
        token = fh.read().strip()
    try:
        with open(".photo_id") as fh:
            photo_id = fh.read().strip()
    except FileNotFoundError:
        photo_id = None

    bot = SpongeBobSarcasmBot(token, photo_id)
    bot.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())

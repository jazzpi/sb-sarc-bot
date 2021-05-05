# SpongeBob SaRcAsM Bot

This is a Telegram bot that turns text into SpongeBob SaRcAsM.

It runs under [@sb_sarc_bot](https://t.me/sb_sarc_bot).

If you want to run your own instance, create a bot (via
[@BotFather](https://t.me/BotFather) and enable inline mode (`/setinline`).
Then, save the token in a `.telegram-token` file and run:

```sh
pip install -r requirements.txt
./bot.py
```

If the file `.photo_id` exists, it will be used to reply with a second option
where the message is used as a caption for that image. You can use the `/getimg`
command to get a photo ID for sarcastic Spongebob. It will send the image and
then reply with the photo IDs for all associated photos. You can then store the
ID of the largest photo in `.photo_id`.

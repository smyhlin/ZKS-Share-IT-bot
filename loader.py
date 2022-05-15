import logging

from pyrogram.types import BotCommand

from data import config
from pyrogram import Client
from data.config import ADMINS

dp = Client('ZKS ShareIT',
            bot_token=config.BOT_TOKEN,
            api_hash=config.API_HASH,
            api_id=config.API_ID)

with dp:
    print('Bot started!')
    for admin_id in ADMINS:
        try:
            dp.send_message(admin_id, "Bot started!")
        except Exception:
            logging.exception('Please write bot first')

    dp.set_bot_commands(
        [
            BotCommand("start", "Start bot"),
            BotCommand("help", "Help info"),
        ]
    )

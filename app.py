import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery, \
    InlineQueryResultArticle, InputTextMessageContent, InlineQuery
from loader import dp
from data import config
from locales import _


# Some func to display alert messages
@dp.on_callback_query()
async def text_message(bot: Client, update: CallbackQuery):
    msg = update.data.split('-')[-1]
    command = '-'.join(update.data.split('-')[0:-1])

    if 'fast' in command:
        await bot.answer_callback_query(update.id, text=msg, show_alert=True)
    else:
        check = await bot.get_messages(config.TRACK_CHANNEL, int(msg))
        await bot.answer_callback_query(update.id, text=check.text, show_alert=True)


# Start & Get file
@dp.on_message(filters.command('start') & filters.private)
async def _startfile(bot: Client, update: Message):
    lang = update.from_user.language_code
    sponsor_button = [
        [InlineKeyboardButton(_('project_channel', language=lang), url=f'https://t.me/{config.PROMOTE_CHANNEL}'), ]]
    if update.text == '/start':
        await update.reply_text(
            _('about', language=lang),
            reply_markup=InlineKeyboardMarkup(sponsor_button))
        return
    elif update.text == '/start help':
        await update.reply_text(
            _('instant_share', language=lang),
            reply_markup=InlineKeyboardMarkup(sponsor_button))
        return

    if len(update.command) != 2:
        return
    code = update.command[1]
    if '-' in code:
        msg_id = code.split('-')[-1]
        # due to new type of file_unique_id, it can contain "-" sign like "agadyruaas-puuo"
        unique_id = '-'.join(code.split('-')[0:-1])

        if not msg_id.isdigit():
            return

        try:  # If message not belong to media group raise exception
            check_media_group = await bot.get_media_group(config.TRACK_CHANNEL, int(msg_id))
            check = check_media_group[0]  # Because func return`s list obj
        except Exception:
            check = await bot.get_messages(config.TRACK_CHANNEL, int(msg_id))

        if check.empty:
            await update.reply_text(_('error', language=lang))
            return
        if check.video:
            unique_idx = check.video.file_unique_id
        elif check.photo:
            unique_idx = check.photo.file_unique_id
        elif check.audio:
            unique_idx = check.audio.file_unique_id
        elif check.document:
            unique_idx = check.document.file_unique_id
        elif check.sticker:
            unique_idx = check.sticker.file_unique_id
        elif check.animation:
            unique_idx = check.animation.file_unique_id
        elif check.voice:
            unique_idx = check.voice.file_unique_id
        elif check.video_note:
            unique_idx = check.video_note.file_unique_id
        if unique_id != unique_idx.lower():
            return
        try:  # If message not belong to media group raise exception
            await bot.copy_media_group(update.from_user.id, config.TRACK_CHANNEL, int(msg_id))
        except Exception:
            await check.copy(update.from_user.id)
    else:
        return


# Help msg
@dp.on_message(filters.command('help') & filters.private)
async def _help(bot: Client, update: Message):
    lang = update.from_user.language_code
    sponsor_button = [
        [InlineKeyboardButton(_('project_channel', language=lang), url=f'https://t.me/{config.PROMOTE_CHANNEL}'), ]]

    await update.reply_text(_('info', language=lang).replace('CREATOR_USERNAME', config.CREATOR_USERNAME),
                            reply_markup=InlineKeyboardMarkup(sponsor_button))


async def __reply(update: Message, copied):
    lang = update.from_user.language_code
    msg_id = copied.id
    if copied.video:
        unique_idx = copied.video.file_unique_id
    elif copied.photo:
        unique_idx = copied.photo.file_unique_id
    elif copied.audio:
        unique_idx = copied.audio.file_unique_id
    elif copied.document:
        unique_idx = copied.document.file_unique_id
    elif copied.sticker:
        unique_idx = copied.sticker.file_unique_id
    elif copied.animation:
        unique_idx = copied.animation.file_unique_id
    elif copied.voice:
        unique_idx = copied.voice.file_unique_id
    elif copied.video_note:
        unique_idx = copied.video_note.file_unique_id
    else:
        await copied.delete()
        return

    await asyncio.sleep(0.25)
    await update.reply_text(_('destination', language=lang),
                            reply_markup=InlineKeyboardMarkup([
                                [InlineKeyboardButton('Share IT',
                                                      switch_inline_query=f'{unique_idx.lower()}-{msg_id}')]
                            ])
                            )


# Store media_group
media_group_id = 0


@dp.on_message(filters.media & filters.private & filters.media_group)
async def _main_group(bot: Client, update: Message):
    global media_group_id

    if int(media_group_id) != int(update.media_group_id):
        media_group_id = update.media_group_id
        copied = (await bot.copy_media_group(config.TRACK_CHANNEL, update.from_user.id, update.id))[0]
        await __reply(update, copied)
    else:
        # This handler catch EVERY message with [update.media_group_id] param
        # So we should ignore next >1_media_group_id messages
        return


# Store file
@dp.on_message(filters.media & filters.private & ~filters.media_group)
async def _main(bot: Client, update: Message):
    copied = await update.copy(config.TRACK_CHANNEL)
    await __reply(update, copied)


@dp.on_inline_query()
async def answer(bot: Client, inline_query: InlineQuery):
    lang = inline_query.from_user.language_code
    query = inline_query.query
    caption = '❔'
    sub_query_description = _("description_help", language=lang)
    if '-' in query:
        msg_id = query.split('-')[1].split('  ')[0]
        command = '-'.join(query.split('-')[0:-1])
        if "  " in query:
            caption = ' '.join(query.split('  ')[1:])
    else:
        msg_id = 'None'
        command = 'None'

    if msg_id.isdigit():
        if 'text' in command:
            button = InlineKeyboardButton(
                "🔎",
                callback_data=f"{command}-{msg_id}")
            query_description = f'Text✏️'
        else:
            button = InlineKeyboardButton(
                "🔎",
                url=f'https://t.me/{config.BOT_USERNAME}?start={command.lower()}-{msg_id}')
            query_description = f'🎥|🎵|📷|📁|🖼|🎞|🎤|🔘|🗂'
    else:
        if "  " in inline_query.query:
            hiden_text = inline_query.query.split("  ")[0]
            caption = ' '.join(inline_query.query.split("  ")[1:])
            query_description = f'{_("hiden_text", language=lang)}: {hiden_text}'
            button = InlineKeyboardButton("🔎",
                                          callback_data=f"fast-{hiden_text}")
        else:  # If field is empty
            if not inline_query.query:
                hiden_text = '🔎'
            else:
                hiden_text = inline_query.query

            query_description = f'{_("hiden_text", language=lang)}: {hiden_text}'
            button = InlineKeyboardButton("🔎",
                                          callback_data=f"fast-{hiden_text}")
    if "  " in inline_query.query:
        query_description += f'\n{_("caption", language=lang)}: {caption}'
    else:
        query_description += sub_query_description
    await inline_query.answer(
        results=[
            InlineQueryResultArticle(
                title="Share IT",
                thumb_url='https://telegra.ph/file/4bf5f6205d2446d0dacf8.png',
                input_message_content=InputTextMessageContent(f"{caption}"),
                description=query_description,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [button]
                    ]
                )
            )
        ],
        cache_time=1, switch_pm_text=_('instant_share_banner', language=lang), switch_pm_parameter='help'
    )


# Store text
@dp.on_message(filters.text & filters.private & ~filters.bot)
async def _main_text(bot: Client, update: Message):
    lang = update.from_user.language_code
    copied = await update.copy(config.TRACK_CHANNEL)
    await update.reply_text(
        _('destination', language=lang),
        True,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton('Share IT',
                                  switch_inline_query=f'text-{copied.id}'
                                  )
             ]
        ])
    )


if __name__ == '__main__':
    dp.run()

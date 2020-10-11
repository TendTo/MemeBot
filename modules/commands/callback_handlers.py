"""Commands for the meme bot"""
from typing import Tuple, List
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, Message, Bot
from telegram.ext import CallbackContext
from modules.utils.info_util import get_callback_info
from modules.data.data_reader import config_map
from modules.data.meme_data import MemeData

STATE = {'posting': 1, 'confirm': 2, 'end': -1}


def meme_callback(update: Update, context: CallbackContext) -> int:
    """Passes the callback to the correct handler

    Args:
        update (Update): update event
        context (CallbackContext): context passed by the handler

    Returns:
        int: value passed to the handler, if requested
    """
    info = get_callback_info(update, context)
    data = info['data']
    try:
        message_text, reply_markup, output = globals()[f'{data[5:]}_callback'](update,
                                                                               context)  # call the function based on its name
    except KeyError:
        message_text = reply_markup = output = None
        print("[error] (meme) meme_callback: the function corrisponding to this callback_data was not found")
        print(f"callback_data: {data}, Argument passed: {data[5:]}_callback")

    if message_text:  # if there is a valid text, edit the menu with the new text
        info['bot'].edit_message_text(chat_id=info['chat_id'],
                                      message_id=info['message_id'],
                                      text=message_text,
                                      reply_markup=reply_markup,
                                      parse_mode=ParseMode.MARKDOWN_V2)
    elif reply_markup:  # if there is a valid reply_markup, edit the menu with the new reply_markup
        info['bot'].edit_message_reply_markup(chat_id=info['chat_id'],
                                              message_id=info['message_id'],
                                              reply_markup=reply_markup)
    return output


# region handle meme_callback
def confirm_yes_callback(update: Update, context: CallbackContext) -> Tuple[str, InlineKeyboardMarkup, int]:
    """Handles the confirm_yes callback.
    Saves the post as pending and sends it to the admins for them to check

    Args:
        update (Update): update event
        context (CallbackContext): context passed by the handler

    Returns:
        Tuple[str, InlineKeyboardMarkup, int]: text and replyMarkup that make up the reply, new conversation state
    """
    info = get_callback_info(update, context)
    user_message = update.callback_query.message.reply_to_message
    admin_message = send_message_to(message=user_message, bot=info['bot'], destination="admin")
    if admin_message:
        MemeData.insert_pending_post(user_message, admin_message)
        text = "Il tuo post è in fase di valutazione\n"\
            f"Una volta pubblicato, lo potrai trovare sul [canale]({config_map['meme']['channel_id']})"
    else:
        text = "Si è verificato un problema\nAssicurati che il tipo di post sia fra quelli consentiti"
    return text, None, STATE['end']


def confirm_no_callback(update: Update, context: CallbackContext) -> Tuple[str, InlineKeyboardMarkup, int]:
    """Handles the confirm_yes callback.
    Saves the post as pending and sends it to the admins for them to check

    Args:
        update (Update): update event
        context (CallbackContext): context passed by the handler

    Returns:
        Tuple[str, InlineKeyboardMarkup, int]: text and replyMarkup that make up the reply, new conversation state
    """
    message_text = "Va bene, alla prossima 🙃"
    return message_text, None, STATE['end']


def settings_anonimo_callback(update: Update, context: CallbackContext) -> Tuple[str, InlineKeyboardMarkup, int]:
    """Handles the settings_sei_ghei callback
    Removes the user_id from the table of credited users, if present

    Args:
        update (Update): update event
        context (CallbackContext): context passed by the handler

    Returns:
        Tuple[str, InlineKeyboardMarkup, int]: text and replyMarkup that make up the reply, new conversation state
    """
    user_id = update.callback_query.from_user.id
    # if the user was already anonym
    if MemeData.become_anonym(user_id=user_id):
        text = "Sei già anonimo"
    else:
        text = "La tua preferenza è stata aggiornata\n"\
            "Ora i tuoi post saranno anonimi"

    return text, None, None


def settings_credit_callback(update: Update, context: CallbackContext) -> Tuple[str, InlineKeyboardMarkup, int]:
    """Handles the settings_foto_cane callback
    Adds the user_id to the table of credited users, if it wasn't already there

    Args:
        update (Update): update event
        context (CallbackContext): context passed by the handler

    Returns:
        Tuple[str, InlineKeyboardMarkup, int]: text and replyMarkup that make up the reply, new conversation state
    """
    username = update.callback_query.from_user.username
    user_id = update.callback_query.from_user.id

    # if the user was already credited
    if MemeData.become_credited(user_id=user_id):
        text = "Sei già creditato nei post\n"
    else:
        text = "La tua preferenza è stata aggiornata\n"

    if username:  # the user has a valid username
        text += f"I tuoi post avranno come credit @{username}"
    else:
        text += "**ATTENZIONE:**\nNon hai nessun username associato al tuo account telegram\n"\
            "Se non lo aggiungi, non sarai creditato"
    return text, None, None


def approve_yes_callback(update: Update, context: CallbackContext) -> Tuple[str, InlineKeyboardMarkup, int]:
    """Handles the approve_yes callback.
    Approve the post, deleting it from the pending_post table, publishing it in the channel \
    and putting it in the published post table

    Args:
        update (Update): update event
        context (CallbackContext): context passed by the handler

    Returns:
        Tuple[str, InlineKeyboardMarkup, int]: text and replyMarkup that make up the reply, new conversation state
    """
    info = get_callback_info(update, context)
    n_approve = MemeData.set_admin_vote(info['sender_id'], info['message_id'], info['chat_id'], True)

    # the post passed the approval phase and is to be published
    if n_approve >= config_map['meme']['n_votes']:
        message = update.callback_query.message
        user_id = MemeData.get_user_id(g_message_id=info['message_id'], group_id=info['chat_id'])
        if MemeData.is_credited(user_id=user_id):  # the user wants to be credited
            username = info['bot'].getChat(user_id).username
            if username:
                info['bot'].send_message(chat_id=config_map['meme']['channel_id'], text=f"CREDIT: @{username}")

        channel_message = send_message_to(message, info['bot'], "channel")
        MemeData.insert_published_post(channel_message=channel_message)
        info['bot'].send_message(chat_id=user_id, text="Il tuo ultimo post è stato approvato")

        info['bot'].delete_message(chat_id=info['chat_id'], message_id=info['message_id'])
        MemeData.clean_pending_meme(info['message_id'], info['chat_id'])
        return None, None, None
    if n_approve != -1:  # the vote changed
        keyboard = update.callback_query.message.reply_markup.inline_keyboard
        return None, get_approve_keyboard(keyboard, info['message_id'], info['chat_id'], approve=n_approve), None

    return None, None, None


def approve_no_callback(update: Update, context: CallbackContext) -> Tuple[str, InlineKeyboardMarkup, int]:
    """Handles the approve_yes callback.
    Approve the post, deleting it from the pending_post table, publishing it in the channel \
    and putting it in the published post table

    Args:
        update (Update): update event
        context (CallbackContext): context passed by the handler

    Returns:
        Tuple[str, InlineKeyboardMarkup, int]: text and replyMarkup that make up the reply, new conversation state
    """
    info = get_callback_info(update, context)
    n_reject = MemeData.set_admin_vote(info['sender_id'], info['message_id'], info['chat_id'], False)

    if n_reject >= config_map['meme']['n_votes']:
        info['bot'].delete_message(chat_id=info['chat_id'], message_id=info['message_id'])
        user_id = MemeData.get_user_id(g_message_id=info['message_id'], group_id=info['chat_id'])
        info['bot'].send_message(chat_id=user_id,
                                 text="Il tuo ultimo post è stato rifiutato\nPuoi controllare le regole con /rules")
        MemeData.clean_pending_meme(info['message_id'], info['chat_id'])
        return None, None, None
    if n_reject != -1:  # the vote changed
        keyboard = update.callback_query.message.reply_markup.inline_keyboard
        return None, get_approve_keyboard(keyboard, info['message_id'], info['chat_id'], reject=n_reject), None

    return None, None, None


def vote_yes_callback(update: Update, context: CallbackContext) -> Tuple[str, InlineKeyboardMarkup, int]:
    """Handles the vote_yes callback.
    Upvotes the post

    Args:
        update (Update): update event
        context (CallbackContext): context passed by the handler

    Returns:
        Tuple[str, InlineKeyboardMarkup, int]: text and replyMarkup that make up the reply, new conversation state
    """
    info = get_callback_info(update, context)
    n_upvotes = MemeData.set_user_vote(user_id=info['sender_id'],
                                       c_message_id=info['message_id'],
                                       channel_id=info['chat_id'],
                                       vote=True)

    if n_upvotes != -1:  # the vote changed
        keyboard = update.callback_query.message.reply_markup.inline_keyboard
        return None, get_vote_keyboard(keyboard, info['message_id'], info['chat_id'], upvote=n_upvotes), None

    return None, None, None


def vote_no_callback(update: Update, context: CallbackContext) -> Tuple[str, InlineKeyboardMarkup, int]:
    """Handles the vote_no callback.
    Downvotes the post

    Args:
        update (Update): update event
        context (CallbackContext): context passed by the handler

    Returns:
        Tuple[str, InlineKeyboardMarkup, int]: text and replyMarkup that make up the reply, new conversation state
    """
    info = get_callback_info(update, context)
    n_downvotes = MemeData.set_user_vote(user_id=info['sender_id'],
                                         c_message_id=info['message_id'],
                                         channel_id=info['chat_id'],
                                         vote=False)

    if n_downvotes != -1:  # the vote changed
        keyboard = update.callback_query.message.reply_markup.inline_keyboard
        return None, get_vote_keyboard(keyboard, info['message_id'], info['chat_id'], downvote=n_downvotes), None

    return None, None, None


# endregion


def send_message_to(message: Message, bot: Bot, destination: str) -> Message:
    """Sends a message to the admins so that they can check the post before publishing it

    Args:
        message (Message): message that contains the post to check
        bot (Bot): bot
        destination (str): destination of the message. admin OR channel

    Returns:
        Message: message sent to the admins
    """
    text = message.text
    photo = message.photo
    voice = message.voice
    audio = message.audio
    video = message.video
    animation = message.animation
    sticker = message.sticker
    caption = message.caption

    if destination == "admin":
        chat_id = config_map['meme']['group_id']
        reply_markup = InlineKeyboardMarkup([[
            InlineKeyboardButton("🟢 0", callback_data="meme_approve_yes"),
            InlineKeyboardButton("🔴 0", callback_data="meme_approve_no")
        ]])
    elif destination == "channel":
        chat_id = config_map['meme']['channel_id']
        reply_markup = InlineKeyboardMarkup([[
            InlineKeyboardButton("👍 0", callback_data="meme_vote_yes"),
            InlineKeyboardButton("👎 0", callback_data="meme_vote_no")
        ]])
    else:
        print("[error] send_message_to: unvalid destination")
        return None

    if text:
        return bot.sendMessage(chat_id=chat_id, text=text, reply_markup=reply_markup)
    if photo:
        return bot.sendPhoto(chat_id=chat_id, photo=photo[-1], caption=caption, reply_markup=reply_markup)
    if voice:
        return bot.sendVoice(chat_id=chat_id, voice=voice, reply_markup=reply_markup)
    if audio:
        return bot.sendAudio(chat_id=chat_id, audio=audio, reply_markup=reply_markup)
    if video:
        return bot.sendVideo(chat_id=chat_id, video=video, caption=caption, reply_markup=reply_markup)
    if animation:
        return bot.sendAnimation(chat_id=chat_id, animation=animation, reply_markup=reply_markup)
    if sticker:
        return bot.sendSticker(chat_id=chat_id, sticker=sticker, reply_markup=reply_markup)
    return None


def get_approve_keyboard(keyboard: List[List[InlineKeyboardButton]],
                         g_message_id: int,
                         group_id: int,
                         approve: int = -1,
                         reject: int = -1) -> InlineKeyboardMarkup:
    """Updates the new InlineKeyboard when the valutation of a pending post changes

    Args:
        keyboard (List[List[InlineKeyboardButton]]): previous keyboard
        g_message_id (int): id of the pending post in question ni the admin group
        group_id (int): id of the admin group
        approve (int, optional): number of approve votes, if known. Defaults to -1.
        reject (int, optional): number of reject votes, if known. Defaults to -1.

    Returns:
        InlineKeyboardMarkup: updated inline keyboard
    """
    if approve >= 0:
        keyboard[0][0].text = f"🟢 {approve}"
    else:
        keyboard[0][0].text = f"🟢 {MemeData.get_pending_votes(g_message_id, group_id, vote=True)}"
    if reject >= 0:
        keyboard[0][1].text = f"🔴 {reject}"
    else:
        keyboard[0][1].text = f"🔴 {MemeData.get_pending_votes(g_message_id, group_id, vote=False)}"
    return InlineKeyboardMarkup(keyboard)


def get_vote_keyboard(keyboard: List[List[InlineKeyboardButton]],
                      c_message_id: int,
                      channel_id: int,
                      upvote: int = -1,
                      downvote: int = -1) -> InlineKeyboardMarkup:
    """Updates the new InlineKeyboard when the valutation of a published post changes

    Args:
        keyboard (List[List[InlineKeyboardButton]]): previous keyboard
        c_message_id (int): id of the published post in question
        channel_id (int): id of the channel
        upvote (int, optional): number of upvotes, if known. Defaults to -1.
        downvote (int, optional): number of downvotes, if known. Defaults to -1.

    Returns:
        InlineKeyboardMarkup: updated inline keyboard
    """
    if upvote >= 0:
        keyboard[0][0].text = f"👍 {upvote}"
    else:
        keyboard[0][0].text = f"👍 {MemeData.get_published_votes(c_message_id, channel_id, vote=True)}"
    if downvote >= 0:
        keyboard[0][1].text = f"👎 {downvote}"
    else:
        keyboard[0][1].text = f"👎 {MemeData.get_published_votes(c_message_id, channel_id, vote=False)}"
    return InlineKeyboardMarkup(keyboard)

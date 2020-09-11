"""Commands for the meme bot"""
from typing import Tuple, Optional, List
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, ForceReply, Message, Bot
from telegram.ext import CallbackContext
from modules.commands.general_command import get_message_info, get_callback_info
from modules.data.data_reader import read_md, config_map
from modules.data.db_manager import DbManager

STATE = {'posting': 1, 'confirm': 2, 'end': -1}

db_init = DbManager()  # initialize the database
if config_map['meme']['reset_on_load']:
    db_init.query_from_file("data", "db", "meme_db_del.sql")
db_init.query_from_file("data", "db", "meme_db_init.sql")  # remove temporarely to clean the database
del db_init


# region cmd
def start_cmd(update: Update, context: CallbackContext):
    """Handles the /start command

    Args:
        update (Update): update event
        context (CallbackContext): context passed by the handler
    """
    info = get_message_info(update, context)
    text = read_md("meme_start")
    info['bot'].send_message(chat_id=info['chat_id'],
                             text=text,
                             parse_mode=ParseMode.MARKDOWN_V2,
                             disable_web_page_preview=True)


def help_cmd(update: Update, context: CallbackContext):
    """Handles the /help command

    Args:
        update (Update): update event
        context (CallbackContext): context passed by the handler
    """
    info = get_message_info(update, context)
    if info['chat_id'] == config_map['meme']['group_id']:  # if you are in the admin group
        text = read_md("meme_instructions")
    else:  # you are NOT in the admin group
        text = read_md("meme_help")
    info['bot'].send_message(chat_id=info['chat_id'],
                             text=text,
                             parse_mode=ParseMode.MARKDOWN_V2,
                             disable_web_page_preview=True)


def rules_cmd(update: Update, context: CallbackContext):
    """Handles the /rules command

    Args:
        update (Update): update event
        context (CallbackContext): context passed by the handler
    """
    info = get_message_info(update, context)
    text = read_md("meme_rules")
    info['bot'].send_message(chat_id=info['chat_id'],
                             text=text,
                             parse_mode=ParseMode.MARKDOWN_V2,
                             disable_web_page_preview=True)


def settings_cmd(update: Update, context: CallbackContext):
    """Handles the /settings command

    Args:
        update (Update): update event
        context (CallbackContext): context passed by the handler
    """
    info = get_message_info(update, context)
    if update.message.chat.type != "private":  # you can only post with a private message
        info['bot'].send_message(
            chat_id=info['chat_id'],
            text="Non puoi usare quest comando ora\nChatta con @tendTo_bot in privato",
        )
        return

    keyboard = [[
        InlineKeyboardButton(" Anonimo ", callback_data="meme_settings_anonimo"),
        InlineKeyboardButton(" Con credit ", callback_data="meme_settings_credit"),
    ]]

    info['bot'].send_message(chat_id=info['chat_id'],
                             text="***Come vuoi che sia il tuo post:***",
                             reply_markup=InlineKeyboardMarkup(keyboard),
                             parse_mode=ParseMode.MARKDOWN_V2)


def post_cmd(update: Update, context: CallbackContext) -> int:
    """Handles the /post command
    Checks that the user is in a private chat and it's not banned and start the post process

    Args:
        update (Update): update event
        context (CallbackContext): context passed by the handler

    Returns:
        int: value passed to the handler, if requested
    """
    info = get_message_info(update, context)
    db = DbManager()
    if update.message.chat.type != "private":  # you can only post with a private message
        info['bot'].send_message(
            chat_id=info['chat_id'],
            text="Non puoi usare quest comando ora\nChatta con @tendTo_bot in privato",
        )
        return STATE['end']

    if db.count_from_where("banned_users", f"user_id = '{info['sender_id']}'") > 0:  # you are banned
        info['bot'].send_message(chat_id=info['chat_id'], text="Sei stato bannato 😅")
        return STATE['end']

    if db.count_from_where("pending_meme", f"user_id = '{info['sender_id']}'") > 0:  # have already a post in pending
        info['bot'].send_message(chat_id=info['chat_id'], text="Hai già un post in approvazione 🧐")
        return STATE['end']

    info['bot'].send_message(chat_id=info['chat_id'],
                             text="Rispondi a questo messaggio con il post che vuoi pubblicare",
                             reply_markup=ForceReply())
    return STATE['posting']


def ban_cmd(update: Update, context: CallbackContext):
    """Handles the /ban command
    Ban a user by replying to one of his pending posts with /ban

    Args:
        update (Update): update event
        context (CallbackContext): context passed by the handler
    """
    info = get_message_info(update, context)
    if info['chat_id'] == config_map['meme']['group_id']:  # you have to be in the admin group
        db = DbManager()
        g_message_id = update.message.reply_to_message.message_id
        user_id = db_get_user_id(g_message_id=g_message_id, group_id=info['chat_id'])

        if user_id is None:
            info['bot'].send_message(chat_id=info['chat_id'], text="Per bannare qualcuno, rispondi al suo post con /ban")
            return

        db.query_from_string(f"INSERT INTO banned_users (user_id) VALUES ('{user_id}')")
        db_clean_pending_meme(g_message_id=g_message_id, group_id=info['chat_id'])
        info['bot'].delete_message(chat_id=info['chat_id'], message_id=g_message_id)
        info['bot'].send_message(chat_id=info['chat_id'], text="L'utente è stato bannato")


def sban_cmd(update: Update, context: CallbackContext):
    """Handles the /sban command
    Sban a user by using this command and listing all the user_id to sban

    Args:
        update (Update): update event
        context (CallbackContext): context passed by the handler
    """
    info = get_message_info(update, context)
    if info['chat_id'] == config_map['meme']['group_id']:  # you have to be in the admin group
        db = DbManager()
        if len(context.args) == 0:  # if no args have been passed
            info['bot'].send_message(chat_id=info['chat_id'], text="[uso]: /sban <user_id1> [...user_id2]")
            return
        for user_id in context.args:
            db.query_from_string(f"DELETE FROM banned_users WHERE user_id = '{user_id}'")
        info['bot'].send_message(chat_id=info['chat_id'], text="Sban effettuato")


def reply_cmd(update: Update, context: CallbackContext):
    """Handles the /reply command
    Send a message to a user by replying to one of his pending posts with /reply + the message you want to send

    Args:
        update (Update): update event
        context (CallbackContext): context passed by the handler
    """
    info = get_message_info(update, context)
    if info['chat_id'] == config_map['meme']['group_id']:  # you have to be in the admin group
        g_message_id = update.message.reply_to_message.message_id
        user_id = db_get_user_id(g_message_id=g_message_id, group_id=info['chat_id'])
        if user_id is None or len(info['text']) <= 7:
            info['bot'].send_message(
                chat_id=info['chat_id'],
                text=
                "Per mandare un messaggio ad un utente, rispondere al suo post con /reply seguito da ciò che gli si vuole dire"
            )
            return
        info['bot'].send_message(chat_id=user_id, text="COMUNICAZIONE DEGLI ADMIN SUL TUO ULTIMO POST:\n" + info['text'][7:])


def cancel_cmd(update: Update, context: CallbackContext) -> int:
    """Handles the reply to the /cancel command.
    Exit from the post pipeline

    Args:
        update (Update): update event
        context (CallbackContext): context passed by the handler

    Returns:
        int: value passed to the handler, if requested
    """
    info = get_message_info(update, context)

    info['bot'].send_message(chat_id=info['chat_id'], text="Post annullato")
    return STATE['end']


# endregion


# region msg
def post_msg(update: Update, context: CallbackContext) -> int:
    """Handles the reply to the /post command.
    Checks the message the user wants to post, and goes to the final step

    Args:
        update (Update): update event
        context (CallbackContext): context passed by the handler

    Returns:
        int: value passed to the handler, if requested
    """
    info = get_message_info(update, context)

    if not check_message_type(update.message):  # the type is NOT supported
        info['bot'].send_message(
            chat_id=info['chat_id'],
            text="Questo tipo di messaggio non è supportato\nPuoi inviare solo testo, immagini, audio o video",
        )
        return STATE['end']

    info['bot'].send_message(chat_id=info['chat_id'],
                             text="Sei sicuro di voler publicare questo post?",
                             reply_to_message_id=info['message_id'],
                             reply_markup=InlineKeyboardMarkup([[
                                 InlineKeyboardButton(text="Si", callback_data="meme_confirm_yes"),
                                 InlineKeyboardButton(text="No", callback_data="meme_confirm_no")
                             ]]))
    return STATE['confirm']


# endregion


def meme_callback(update: Update, context: CallbackContext) -> int:
    """Passes the callback to the correct handler

    Args:
        update (Update): update event
        context (CallbackContext): context passed by the handler

    Returns:
        int: value passed to the handler, if requested
    """
    info = get_callback_info(update, context)
    data = update.callback_query.data
    try:
        message_text, reply_markup, output = globals()[f'{data[5:]}_callback'](update,
                                                                               context)  # call the function based on its name
    except KeyError:
        message_text = False
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
                                              reply_markup=reply_markup,
                                              parse_mode=ParseMode.MARKDOWN_V2)
    return output


# region handle meme_callback
def confirm_yes_callback(update: Update, context: CallbackContext) -> Tuple[str, InlineKeyboardMarkup, int]:
    """Handles the confirm_yes callback.
    Saves the post as pending and sends it to the admins for them to check

    Args:
        update (Update): update event
        context (CallbackContext): context passed by the handler

    Returns:
        Tuple[str, InlineKeyboardMarkup, int]: text and InlineKeyboardMarkup needed that make up the reply,
        and the output value
    """
    info = get_callback_info(update, context)
    try:
        user_message = update.callback_query.message.reply_to_message
        admin_message = send_message_to(user_message, info['bot'], destination="admin")
        if admin_message:
            db_insert_pending_post(user_message, admin_message)
            text = "Il tuo post è in fase di valutazione\n"\
            f"Una volta pubblicato, lo potrai trovare sul [canale]({config_map['meme']['channel_id']})"
        else:
            text = "Si è verificato un problema\nAssicurati che il tipo di post sia fra quelli consentiti"
    except KeyError as e:
        print("[error] confirm_yes_callback: " + str(e))
        text = "Si è verificato un problema"
    return text, None, STATE['end']


def confirm_no_callback(update: Update, context: CallbackContext) -> Tuple[str, InlineKeyboardMarkup, int]:
    """Handles the confirm_yes callback.
    Saves the post as pending and sends it to the admins for them to check

    Args:
        update (Update): update event
        context (CallbackContext): context passed by the handler

    Returns:
        Tuple[str, InlineKeyboardMarkup, int]: text and InlineKeyboardMarkup needed that make up the reply,
        and the output value
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
        Tuple[str, InlineKeyboardMarkup, int]: text and InlineKeyboardMarkup needed that make up the reply,
        and the output value
    """
    db = DbManager()
    user_id = update.callback_query.from_user.id

    is_anonym = db.count_from_where(table_name="credited_users", where=f"user_id = '{user_id}'") == 0
    if is_anonym:
        text = "Sei già anonimo"
    else:
        db.query_from_string(f"DELETE FROM credited_users WHERE user_id = ('{user_id}')")
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
        Tuple[str, InlineKeyboardMarkup, int]: text and InlineKeyboardMarkup needed that make up the reply,
        and the output value
    """
    db = DbManager()
    username = update.callback_query.from_user.username
    user_id = update.callback_query.from_user.id

    present = db.count_from_where(table_name="credited_users", where=f"user_id = '{user_id}'") == 1

    if not present:
        db.query_from_string(f"INSERT INTO credited_users (user_id) VALUES ('{user_id}')")
        text = "La tua preferenza è stata aggiornata\n"
    else:
        text = "Sei già creditato nei post\n"

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
        Tuple[str, InlineKeyboardMarkup, int]: text and InlineKeyboardMarkup needed that make up the reply,
        and the output value
    """
    info = get_callback_info(update, context)
    n_approve = db_set_admin_vote(info['sender_id'], info['message_id'], info['chat_id'], True)

    if n_approve >= config_map['meme']['n_votes']:  # the post passed the approval phase and is to be published
        db = DbManager()
        message = update.callback_query.message
        user_id = db_get_user_id(g_message_id=info['message_id'], group_id=info['chat_id'])
        if len(db.select_from_where(table_name="credited_users",
                                    where=f"user_id = '{user_id}'")) == 1:  # the user wants to be credited
            username = info['bot'].getChat(user_id).username
            if username:
                info['bot'].send_message(chat_id=config_map['meme']['channel_id'], text=f"CREDIT: @{username}")

        channel_message = send_message_to(message, info['bot'], "channel")
        db_insert_published_post(channel_message=channel_message)
        info['bot'].send_message(chat_id=user_id, text="Il tuo ultimo post è stato approvato")

        info['bot'].delete_message(chat_id=info['chat_id'], message_id=info['message_id'])
        db_clean_pending_meme(info['message_id'], info['chat_id'])
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
        Tuple[str, InlineKeyboardMarkup, int]: text and InlineKeyboardMarkup needed that make up the reply,
        and the output value
    """
    info = get_callback_info(update, context)
    n_reject = db_set_admin_vote(info['sender_id'], info['message_id'], info['chat_id'], False)

    if n_reject >= config_map['meme']['n_votes']:
        info['bot'].delete_message(chat_id=info['chat_id'], message_id=info['message_id'])
        user_id = db_get_user_id(g_message_id=info['message_id'], group_id=info['chat_id'])
        info['bot'].send_message(chat_id=user_id,
                                 text="Il tuo ultimo post è stato rifiutato\nPuoi controllare le regole con /rules")
        db_clean_pending_meme(info['message_id'], info['chat_id'])
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
        Tuple[str, InlineKeyboardMarkup, int]: text and InlineKeyboardMarkup needed that make up the reply,
        and the output value
    """
    info = get_callback_info(update, context)
    n_upvotes = db_set_user_vote(info['sender_id'], info['message_id'], info['chat_id'], True)

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
        Tuple[str, InlineKeyboardMarkup, int]: text and InlineKeyboardMarkup needed that make up the reply,
        and the output value
    """
    info = get_callback_info(update, context)
    n_downvotes = db_set_user_vote(info['sender_id'], info['message_id'], info['chat_id'], False)

    if n_downvotes != -1:  # the vote changed
        keyboard = update.callback_query.message.reply_markup.inline_keyboard
        return None, get_vote_keyboard(keyboard, info['message_id'], info['chat_id'], downvote=n_downvotes), None

    return None, None, None


# endregion


def check_message_type(message: Message) -> bool:
    """Check that the type of the message is one of the ones supported

    Args:
        message (Message): message to check

    Returns:
        bool: whether its type is supported or not
    """
    text = message.text
    photo = message.photo
    voice = message.voice
    audio = message.audio
    video = message.video
    animation = message.animation
    sticker = message.sticker
    return text or photo or voice or audio or video or animation or sticker


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


# region db management
def db_insert_pending_post(user_message: Message, admin_message: Message):
    """Insert a new post in the table of pending posts

    Args:
        user_message (Message): message sent by the user that contains the post
        admin_message (Message): message recieved in the admin group that references the post
    """
    db = DbManager()

    user_id = user_message.from_user.id
    u_message_id = user_message.message_id
    g_message_id = admin_message.message_id
    group_id = admin_message.chat_id

    db.query_from_string("INSERT INTO pending_meme (user_id, u_message_id, g_message_id, group_id)" +
                         f"VALUES ('{user_id}', '{u_message_id}', '{g_message_id}', '{group_id}')")


def db_set_admin_vote(admin_id: int, g_message_id: int, group_id: int, approval: bool) -> int:
    """Adds the vote of the admin on a specific post, or update the existing vote, if needed

    Args:
        admin_id (int): id of the admin that voted
        g_message_id (int): id of the post in question in the group
        group_id (int): id of the admin group
        approval (bool): whether the vote is approval or reject

    Returns:
        int: number of similar votes (all the approve or the reject), or -1 if the vote wasn't updated
    """
    db = DbManager()
    vote = db_get_admin_vote(admin_id, g_message_id, group_id)
    if vote is None:  # there isn't a vote yet
        db.query_from_string(f"INSERT INTO admin_votes (admin_id, g_message_id, group_id, is_upvote)\
                                VALUES ('{admin_id}',\
                                        '{g_message_id}',\
                                        '{group_id}',\
                                         {approval})")
        number_of_votes = db_get_pending_votes(g_message_id, group_id, approval)
    elif bool(vote) != approval:  # the vote was different from the approval
        db.query_from_string(f"UPDATE admin_votes SET is_upvote = {approval}\
                                WHERE admin_id = '{admin_id}'\
                                    and g_message_id = '{g_message_id}'\
                                    and group_id = '{group_id}'")
        number_of_votes = db_get_pending_votes(g_message_id, group_id, approval)
    else:
        return -1
    return number_of_votes


def db_get_admin_vote(admin_id: int, g_message_id: int, group_id: int) -> Optional[bool]:
    """Gets the vote of a specific admin on a pending post

    Args:
        admin_id (int): id of the admin that voted
        g_message_id (int): id of the post in question in the group
        group_id (int): id of the admin group

    Returns:
        Optional[bool]: a bool representing the vote or None if a vote was not yet made
    """
    db = DbManager()
    vote = db.query_from_string(f"SELECT is_upvote FROM admin_votes\
                                    WHERE admin_id = '{admin_id}'\
                                    and g_message_id = '{g_message_id}'\
                                    and group_id = '{group_id}'")

    if len(vote) == 0:  # the vote is not present
        return None
    else:
        return vote[0]['is_upvote']


def db_get_pending_votes(g_message_id: int, group_id: int, vote: bool) -> int:
    """Gets all the votes of a specific kind (approve or reject) on a pending post

    Args:
        g_message_id (int): id of the post in question in the group
        group_id (int): id of the admin group
        vote (bool): whether you look for the approve or reject votes

    Returns:
        int: number of votes
    """
    db = DbManager()
    return db.count_from_where(
        "admin_votes", f"g_message_id='{g_message_id}'\
                        and group_id = '{group_id}'\
                        and is_upvote = {vote}")


def db_clean_pending_meme(g_message_id: int, group_id: int):
    """Removes all remaining entries on a post that is no longer pending

    Args:
        g_message_id (int): id of the no longer pending post in the group
        group_id (int): id of the admin group
    """
    db = DbManager()
    db.query_from_string(f"DELETE FROM pending_meme\
                         WHERE g_message_id = '{g_message_id}'\
                            and group_id = '{group_id}'")
    db.query_from_string(f"DELETE FROM admin_votes\
                         WHERE g_message_id = '{g_message_id}'\
                            and group_id = '{group_id}'")


def db_insert_published_post(channel_message: Message):
    """Insert a new post in the table of pending posts

    Args:
        channel_message (Message): message approved to be published
    """
    db = DbManager()
    c_message_id = channel_message.message_id
    channel_id = channel_message.chat_id
    db.query_from_string("INSERT INTO published_meme (channel_id, c_message_id)" +
                         f"VALUES ('{channel_id}', '{c_message_id}')")


def db_set_user_vote(user_id: int, c_message_id: int, channel_id: int, approval: bool) -> int:
    """Adds the vote of the user on a specific post, or update the existing vote, if needed

    Args:
        user_id (int): id of the user that voted
        c_message_id (int): id of the post in question in the channel
        channel_id (int): id of the channel
        approval (bool): whether it is an upvote or a downvote

    Returns:
        int: number of similar votes (all the upvotes or the downvotes), or -1 if the vote wasn't updated
    """
    db = DbManager()
    vote = db_get_user_vote(user_id, c_message_id, channel_id)
    if vote is None:  # there isn't a vote yet
        db.query_from_string(f"INSERT INTO votes (user_id, c_message_id, channel_id, is_upvote)\
                                VALUES ('{user_id}',\
                                        '{c_message_id}',\
                                        '{channel_id}',\
                                         {approval})")
        number_of_votes = db_get_published_votes(c_message_id, channel_id, approval)
    elif bool(vote) != approval:  # the vote was different from the approval
        db.query_from_string(f"UPDATE votes SET is_upvote = {approval}\
                                WHERE user_id = '{user_id}'\
                                    and c_message_id = '{c_message_id}'\
                                    and channel_id = '{channel_id}'")
        number_of_votes = db_get_published_votes(c_message_id, channel_id, approval)
    else:
        return -1
    return number_of_votes


def db_get_user_vote(user_id: int, c_message_id: int, channel_id: int) -> Optional[bool]:
    """Gets the vote of a specific user on a published post

    Args:
        user_id (int): id of the user that voted
        c_message_id (int): id of the post in question in the channel
        channel_id (int): id of the channel

    Returns:
        Optional[bool]: a bool representing the vote or None if a vote was not yet made
    """
    db = DbManager()
    vote = db.query_from_string(f"SELECT is_upvote FROM votes\
                                    WHERE user_id = '{user_id}'\
                                    and c_message_id = '{c_message_id}'\
                                    and channel_id = '{channel_id}'")

    if len(vote) == 0:  # the vote is not present
        return None
    return vote[0]['is_upvote']


def db_get_published_votes(c_message_id: int, channel_id: int, vote: bool) -> int:
    """Gets all the votes of a specific kind (upvote or downvote) on a published post

    Args:
        c_message_id (int): id of the post in question in the channel
        channel_id (int): id of the channel
        vote (bool): whether you look for upvotes or downvotes

    Returns:
        int: number of votes
    """
    db = DbManager()
    return db.count_from_where(table_name="votes",
                               where=f"c_message_id='{c_message_id}'\
                                        and channel_id = '{channel_id}'\
                                        and is_upvote = {vote}")


def db_get_user_id(g_message_id: int, group_id: int) -> Optional[int]:
    """Get the user_id of the user that made the pending post

    Args:
        g_message_id (int): id of the post in question in the group
        group_id (int): id of the admin group

    Returns:
        Optional[int]: user_id, if found
    """
    db = DbManager()
    list_user_id = db.select_from_where(select="user_id",
                                        table_name="pending_meme",
                                        where=f"g_message_id = '{g_message_id}' and group_id = '{group_id}'")
    if list_user_id:
        return list_user_id[0]['user_id']
    return None


# endregion


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
        keyboard[0][0].text = f"🟢 {db_get_pending_votes(g_message_id, group_id, True)}"
    if reject >= 0:
        keyboard[0][1].text = f"🔴 {reject}"
    else:
        keyboard[0][1].text = f"🔴 {db_get_pending_votes(g_message_id, group_id, False)}"
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
        keyboard[0][0].text = f"👍 {db_get_published_votes(c_message_id, channel_id, True)}"
    if downvote >= 0:
        keyboard[0][1].text = f"👎 {downvote}"
    else:
        keyboard[0][1].text = f"👎 {db_get_published_votes(c_message_id, channel_id, False)}"
    return InlineKeyboardMarkup(keyboard)

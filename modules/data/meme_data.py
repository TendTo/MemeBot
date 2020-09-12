"""Data management for the meme bot"""
from typing import Optional
from telegram import Message
from modules.data.db_manager import DbManager
from modules.data.data_reader import config_map

init = DbManager()  # initialize the database
if config_map['meme']['reset_on_load']:
    init.query_from_file("data", "db", "meme_db_del.sql")
init.query_from_file("data", "db", "meme_db_init.sql")  # remove temporarely to clean the database
del init


# region db management
class MemeData():
    """Class that handles the management of persistent data fetch or manipulation in the meme bot
    """
    @staticmethod
    def insert_pending_post(user_message: Message, admin_message: Message):
        """Insert a new post in the table of pending posts

        Args:
            user_message (Message): message sent by the user that contains the post
            admin_message (Message): message recieved in the admin group that references the post
        """

        user_id = user_message.from_user.id
        u_message_id = user_message.message_id
        g_message_id = admin_message.message_id
        group_id = admin_message.chat_id

        DbManager.query_from_string("INSERT INTO pending_meme (user_id, u_message_id, g_message_id, group_id)" +
                                    f"VALUES ('{user_id}', '{u_message_id}', '{g_message_id}', '{group_id}')")

    @staticmethod
    def set_admin_vote(admin_id: int, g_message_id: int, group_id: int, approval: bool) -> int:
        """Adds the vote of the admin on a specific post, or update the existing vote, if needed

        Args:
            admin_id (int): id of the admin that voted
            g_message_id (int): id of the post in question in the group
            group_id (int): id of the admin group
            approval (bool): whether the vote is approval or reject

        Returns:
            int: number of similar votes (all the approve or the reject), or -1 if the vote wasn't updated
        """

        vote = MemeData.get_admin_vote(admin_id, g_message_id, group_id)
        if vote is None:  # there isn't a vote yet
            DbManager.query_from_string(f"INSERT INTO admin_votes (admin_id, g_message_id, group_id, is_upvote)\
                                    VALUES ('{admin_id}',\
                                            '{g_message_id}',\
                                            '{group_id}',\
                                            {approval})")
            number_of_votes = MemeData.get_pending_votes(g_message_id, group_id, approval)
        elif bool(vote) != approval:  # the vote was different from the approval
            DbManager.query_from_string(f"UPDATE admin_votes SET is_upvote = {approval}\
                                    WHERE admin_id = '{admin_id}'\
                                        and g_message_id = '{g_message_id}'\
                                        and group_id = '{group_id}'")
            number_of_votes = MemeData.get_pending_votes(g_message_id, group_id, approval)
        else:
            return -1
        return number_of_votes

    @staticmethod
    def get_admin_vote(admin_id: int, g_message_id: int, group_id: int) -> Optional[bool]:
        """Gets the vote of a specific admin on a pending post

        Args:
            admin_id (int): id of the admin that voted
            g_message_id (int): id of the post in question in the group
            group_id (int): id of the admin group

        Returns:
            Optional[bool]: a bool representing the vote or None if a vote was not yet made
        """

        vote = DbManager.select_from_where(select="is_upvote",
                                           table_name="admin_votes",
                                           where=f"admin_id = '{admin_id}'\
                                                and g_message_id = '{g_message_id}'\
                                                and group_id = '{group_id}'")

        if len(vote) == 0:  # the vote is not present
            return None
        else:
            return vote[0]['is_upvote']

    @staticmethod
    def get_pending_votes(g_message_id: int, group_id: int, vote: bool) -> int:
        """Gets all the votes of a specific kind (approve or reject) on a pending post

        Args:
            g_message_id (int): id of the post in question in the group
            group_id (int): id of the admin group
            vote (bool): whether you look for the approve or reject votes

        Returns:
            int: number of votes
        """

        return DbManager.count_from_where(
            "admin_votes", f"g_message_id='{g_message_id}'\
                            and group_id = '{group_id}'\
                            and is_upvote = {vote}")

    @staticmethod
    def clean_pending_meme(g_message_id: int, group_id: int):
        """Removes all remaining entries on a post that is no longer pending

        Args:
            g_message_id (int): id of the no longer pending post in the group
            group_id (int): id of the admin group
        """

        DbManager.query_from_string(f"DELETE FROM pending_meme\
                            WHERE g_message_id = '{g_message_id}'\
                                and group_id = '{group_id}'")
        DbManager.query_from_string(f"DELETE FROM admin_votes\
                            WHERE g_message_id = '{g_message_id}'\
                                and group_id = '{group_id}'")

    @staticmethod
    def insert_published_post(channel_message: Message):
        """Insert a new post in the table of pending posts

        Args:
            channel_message (Message): message approved to be published
        """

        c_message_id = channel_message.message_id
        channel_id = channel_message.chat_id
        DbManager.query_from_string("INSERT INTO published_meme (channel_id, c_message_id)" +
                                    f"VALUES ('{channel_id}', '{c_message_id}')")

    @staticmethod
    def set_user_vote(user_id: int, c_message_id: int, channel_id: int, vote: bool) -> int:
        """Adds the vote of the user on a specific post, or update the existing vote, if needed

        Args:
            user_id (int): id of the user that voted
            c_message_id (int): id of the post in question in the channel
            channel_id (int): id of the channel
            vote (bool): whether it is an upvote or a downvote

        Returns:
            int: number of similar votes (all the upvotes or the downvotes), or -1 if the vote wasn't updated
        """

        current_vote = MemeData.get_user_vote(user_id, c_message_id, channel_id)
        if current_vote is None:  # there isn't a vote yet
            DbManager.query_from_string(f"INSERT INTO votes (user_id, c_message_id, channel_id, is_upvote)\
                                            VALUES ('{user_id}', '{c_message_id}', '{channel_id}', {vote})")
            number_of_votes = MemeData.get_published_votes(c_message_id, channel_id, vote)
        elif bool(current_vote) != vote:  # the vote was different from the vote
            DbManager.query_from_string(f"UPDATE votes SET is_upvote = {vote}\
                                        WHERE user_id = '{user_id}'\
                                        and c_message_id = '{c_message_id}'\
                                        and channel_id = '{channel_id}'")
            number_of_votes = MemeData.get_published_votes(c_message_id, channel_id, vote)
        else:
            return -1
        return number_of_votes

    @staticmethod
    def get_user_vote(user_id: int, c_message_id: int, channel_id: int) -> Optional[bool]:
        """Gets the vote of a specific user on a published post

        Args:
            user_id (int): id of the user that voted
            c_message_id (int): id of the post in question in the channel
            channel_id (int): id of the channel

        Returns:
            Optional[bool]: a bool representing the vote or None if a vote was not yet made
        """

        vote = DbManager.select_from_where(select="is_upvote",
                                           table_name="votes",
                                           where=f"user_id = '{user_id}'\
                                                and c_message_id = '{c_message_id}'\
                                                and channel_id = '{channel_id}'")

        if len(vote) == 0:  # the vote is not present
            return None
        return vote[0]['is_upvote']

    @staticmethod
    def get_published_votes(c_message_id: int, channel_id: int, vote: bool) -> int:
        """Gets all the votes of a specific kind (upvote or downvote) on a published post

        Args:
            c_message_id (int): id of the post in question in the channel
            channel_id (int): id of the channel
            vote (bool): whether you look for upvotes or downvotes

        Returns:
            int: number of votes
        """

        return DbManager.count_from_where(table_name="votes",
                                          where=f"c_message_id='{c_message_id}'\
                                            and channel_id = '{channel_id}'\
                                            and is_upvote = {vote}")

    @staticmethod
    def get_user_id(g_message_id: int, group_id: int) -> Optional[int]:
        """Gets the user_id of the user that made the pending post

        Args:
            g_message_id (int): id of the post in question in the group
            group_id (int): id of the admin group

        Returns:
            Optional[int]: user_id, if found
        """

        list_user_id = DbManager.select_from_where(select="user_id",
                                                   table_name="pending_meme",
                                                   where=f"g_message_id = '{g_message_id}' and group_id = '{group_id}'")
        if list_user_id:
            return list_user_id[0]['user_id']
        return None

    @staticmethod
    def is_banned(user_id: int) -> bool:
        """Checks if the user is banned or not

        Args:
            user_id (int): id of the user to check

        Returns:
            bool: whether the user is banned or not
        """
        return DbManager.count_from_where(table_name="banned_users", where=f"user_id = '{user_id}'") > 0

    @staticmethod
    def is_pending(user_id: int) -> bool:
        """Checks if the user still has a post pending

        Args:
            user_id (int): id of the user to check

        Returns:
            bool: whether the user still has a post pending or not
        """
        return DbManager.count_from_where(table_name="pending_meme", where=f"user_id = '{user_id}'") > 0

    @staticmethod
    def ban_user(user_id: int):
        """Adds the user to the banned list

        Args:
            user_id (int): id of the user to ban
        """
        DbManager.query_from_string(f"INSERT INTO banned_users (user_id) VALUES ('{user_id}')")

    @staticmethod
    def sban_user(user_id: int) -> bool:
        """Removes the user from the banned list

        Args:
            user_id (int): id of the user to sban

        Returns:
            bool: whether the user was present in the banned list before the sban or not
        """
        out = DbManager.count_from_where(table_name="banned_users", where=f"user_id = '{user_id}'") > 0
        DbManager.query_from_string(f"DELETE FROM banned_users WHERE user_id = '{user_id}'")
        return out

    @staticmethod
    def become_anonym(user_id: int) -> bool:
        """Removes the user from the credited list, if he was present

        Args:
            user_id (int): id of the user to make anonym

        Returns:
            bool: whether the user was alreasy anonym
        """
        was_anonym = DbManager.count_from_where(table_name="credited_users", where=f"user_id = '{user_id}'") == 0
        if not was_anonym:
            DbManager.query_from_string(f"DELETE FROM credited_users WHERE user_id = ('{user_id}')")
        return was_anonym

    @staticmethod
    def become_credited(user_id: int) -> bool:
        """Adds the user to the credited list, if he wasn't already credited

        Args:
            user_id (int): id of the user to credit

        Returns:
            bool: whether the user was already credited
        """
        was_credited = DbManager.count_from_where(table_name="credited_users", where=f"user_id = '{user_id}'") == 1
        if not was_credited:
            DbManager.query_from_string(f"INSERT INTO credited_users (user_id) VALUES ('{user_id}')")
        return was_credited

    @staticmethod
    def is_credited(user_id: int) -> bool:
        """Checks if the user is in the credited list

        Args:
            user_id (int): id of the user to check

        Returns:
            bool: whether the user is to be credited or not
        """
        return DbManager.count_from_where(table_name="credited_users", where=f"user_id = '{user_id}'") == 1

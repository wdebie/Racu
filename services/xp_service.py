import os
import time

from discord.ext import commands

from db import database

xp_gain_per_message = int(os.environ.get("RACU_XP_GAIN_PER_MESSAGE"))
xp_gain_cooldown = int(os.environ.get("RACU_XP_GAIN_COOLDOWN"))


class XpService:
    """
    Stores and retrieves XP from the database for a given user.
    """

    def __init__(self, user_id, guild_id):
        self.user_id = user_id
        self.guild_id = guild_id
        self.xp = None
        self.level = None
        self.cooldown_time = None
        self.xp_gain = xp_gain_per_message
        self.new_cooldown = xp_gain_cooldown

        self.fetch_or_create_xp()

    def push(self):
        """
        Updates the XP and cooldown for a user.
        """
        query = """
                UPDATE xp
                SET user_xp = %s, user_level = %s, cooldown = %s
                WHERE user_id = %s AND guild_id = %s
                """
        database.execute_query(query, (self.xp, self.level, self.cooldown_time, self.user_id, self.guild_id))

    def fetch_or_create_xp(self):
        """
        Gets a user's XP from the database or inserts a new row if it doesn't exist yet.
        """
        query = "SELECT user_xp, user_level, cooldown FROM xp WHERE user_id = %s AND guild_id = %s"

        try:
            (user_xp, user_level, cooldown) = database.select_query(query, (self.user_id, self.guild_id))[0]
        except (IndexError, TypeError):
            (user_xp, user_level, cooldown) = (None, None, None)

        if any(var is None for var in [user_xp, user_level, cooldown]):
            query = """
                    INSERT INTO xp (user_id, guild_id, user_xp, user_level, cooldown)
                    VALUES (%s, %s, 0, 0, %s)
                    """
            database.execute_query(query, (self.user_id, self.guild_id, time.time()))
            (user_xp, user_level, cooldown) = (0, 0, time.time())

        self.xp = user_xp
        self.level = user_level
        self.cooldown_time = cooldown

    def calculate_rank(self):
        """
        Checks which rank a user is in the guild
        """
        query = """
                SELECT user_id, user_xp, user_level
                FROM xp 
                WHERE guild_id = %s
                ORDER BY user_level DESC, user_xp DESC
                """
        data = database.select_query(query, (self.guild_id,))

        leaderboard = []
        rank = 1
        for row in data:
            row_user_id = row[0]
            user_xp = row[1]
            user_level = row[2]
            leaderboard.append((row_user_id, user_xp, user_level, rank))
            rank += 1

        user_rank = None
        for entry in leaderboard:
            if entry[0] == self.user_id:
                user_rank = entry[3]
                break

        return user_rank

    @staticmethod
    def load_leaderboard(guild_id):
        """
        Returns the guild's XP leaderboard
        """
        query = """
                SELECT user_id, user_xp, user_level 
                FROM xp 
                WHERE guild_id = %s
                ORDER BY user_level DESC, user_xp DESC
                """
        data = database.select_query(query, (guild_id,))

        leaderboard = []
        for row in data:
            row_user_id = row[0]
            user_xp = row[1]
            user_level = row[2]
            needed_xp_for_next_level = XpService.xp_needed_for_next_level(user_level)

            leaderboard.append((row_user_id, user_xp, user_level, needed_xp_for_next_level))

        return leaderboard

    @staticmethod
    def generate_progress_bar(current_value, target_value, bar_length=10):
        """
        Generates an XP progress bar based on the current level and XP.
        """
        progress = current_value / target_value
        filled_length = int(bar_length * progress)
        empty_length = bar_length - filled_length
        bar = "▰" * filled_length + "▱" * empty_length
        return f"`{bar}` {current_value}/{target_value}"

    @staticmethod
    def xp_needed_for_next_level(current_level):
        """
        Calculates the amount of XP needed to go to the next level, based on the current level.
        """
        formula_mapping = {
            (10, 19): lambda level: 12 * level + 28,
            (20, 29): lambda level: 15 * level + 29,
            (30, 39): lambda level: 18 * level + 30,
            (40, 49): lambda level: 21 * level + 31,
            (50, 59): lambda level: 24 * level + 32,
            (60, 69): lambda level: 27 * level + 33,
            (70, 79): lambda level: 30 * level + 34,
            (80, 89): lambda level: 33 * level + 35,
            (90, 99): lambda level: 36 * level + 36,
        }

        for level_range, formula in formula_mapping.items():
            if level_range[0] <= current_level <= level_range[1]:
                return formula(current_level)

        # For levels below 10 and levels 110 and above
        return 10 * current_level + 27 if current_level < 10 else 42 * current_level + 37


class XpRewardService:
    def __init__(self, guild_id):
        self.guild_id = guild_id
        self.rewards = self.get_rewards()

    def get_rewards(self) -> dict:
        query = """
                SELECT level, role_id, persistent
                FROM level_rewards
                WHERE guild_id = %s
                ORDER BY level DESC
                """
        data = database.select_query(query, (self.guild_id,))

        rewards = {}
        for row in data:
            rewards[int(row[0])] = [int(row[1]), bool(row[2])]

        return rewards

    def add_reward(self, level: int, role_id: int, persistent: bool):

        if len(self.rewards) >= 25:
            raise commands.BadArgument("a server can't have more than 25 xp rewards.")

        query = """
                INSERT INTO level_rewards (guild_id, level, role_id, persistent)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE role_id = %s, persistent = %s;
                """

        database.execute_query(query, (self.guild_id, level, role_id, persistent, role_id, persistent))

    def remove_reward(self, level: int):
        query = """
                DELETE FROM level_rewards
                WHERE guild_id = %s
                AND level = %s;
                """

        database.execute_query(query, (self.guild_id, level))

    def role(self, level: int):
        if self.rewards:

            if level in self.rewards:
                role_id = self.rewards.get(level)[0]
                return role_id

        return None

    def replace_previous_reward(self, level):
        replace = False
        previous_reward = None
        levels = sorted(self.rewards.keys())

        if level in levels:
            values_below = [x for x in levels if x < level]

            if values_below:
                replace = not bool(self.rewards.get(max(values_below))[1])

            if replace:
                previous_reward = self.rewards.get(max(values_below))[0]

        return previous_reward, replace

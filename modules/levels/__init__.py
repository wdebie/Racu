from discord.ext import commands, bridge

from lib import checks
from modules.levels import level, leaderboard


class Levels(commands.Cog):

    def __init__(self, client):
        self.client = client

    @bridge.bridge_command(
        name="level",
        aliases=["rank", "xp"],
        description="Displays your level and server rank.",
        help="Displays your level and server rank.",
        guild_only=True
    )
    @commands.guild_only()
    @checks.allowed_in_channel()
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def level_command(self, ctx):
        await level.cmd(ctx)

    @bridge.bridge_command(
        name="leaderboard",
        aliases=["lb", "xplb"],
        description="See the Racu leaderboards.",
        help="Shows three different leaderboards: levels, currency and daily streaks.",
        guild_only=True
    )
    @commands.guild_only()
    @checks.allowed_in_channel()
    @commands.cooldown(1, 180, commands.BucketType.user)
    async def leaderboard_command(self, ctx):
        return await leaderboard.cmd(ctx)


def setup(client):
    client.add_cog(Levels(client))

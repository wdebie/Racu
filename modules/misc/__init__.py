import datetime

from discord.ext import commands, bridge, tasks

from lib import checks
from lib.embeds.info import MiscInfo
from modules.config import set_prefix
from modules.misc import introduction, invite, backup, info


class Misc(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.start_time = datetime.datetime.now()
        self.do_backup.start()

    @tasks.loop(hours=1)
    async def do_backup(self):
        await backup.backup(self)

    @bridge.bridge_command(
        name="ping",
        aliases=["p", "status"],
        description="Simple status check.",
        help="Simple status check.",
    )
    @checks.allowed_in_channel()
    async def ping(self, ctx):
        return await ctx.respond(embed=MiscInfo.ping(ctx, self.client))

    @bridge.bridge_command(
        name="uptime",
        description="See Racu's uptime since the last update.",
        help="See how long Racu has been online since his last update.",
    )
    @checks.allowed_in_channel()
    async def uptime(self, ctx):
        unix_timestamp = int(round(self.start_time.timestamp()))
        return await ctx.respond(embed=MiscInfo.uptime(ctx, self.client, unix_timestamp))

    @bridge.bridge_command(
        name="invite",
        description="Generate an invite link.",
        help="Generate a link to invite Racu to your own server!"
    )
    @checks.allowed_in_channel()
    async def invite_command(self, ctx):
        return await invite.cmd(ctx)

    @bridge.bridge_command(
        name="prefix",
        description="See the server's current prefix.",
        help="See the server's current prefix.",
        guild_only=True
    )
    @commands.guild_only()
    @checks.allowed_in_channel()
    async def prefix_command(self, ctx):
        return await set_prefix.get_cmd(ctx)

    @bridge.bridge_command(
        name="info",
        aliases=["stats"],
        description="Shows basic Racu stats.",
        help="Shows basic Racu stats."
    )
    @checks.allowed_in_channel()
    async def info_command(self, ctx):
        unix_timestamp = int(round(self.start_time.timestamp()))
        return await info.cmd(self, ctx, unix_timestamp)

    @bridge.bridge_command(
        name="introduction",
        aliases=["intro", "introduce"],
        guild_only=False,
        description="This command can only be used in DMs.",
        help="Introduce yourself. For now this command "
             "can only be done in ONE server and only in Racu's DMs."
    )
    @commands.dm_only()
    async def intro_command(self, ctx):
        return await introduction.cmd(self, ctx)


def setup(client):
    client.add_cog(Misc(client))

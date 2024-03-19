import datetime
from discord.ext import commands, bridge, tasks
from lib import checks
from lib.embeds.info import MiscInfo
from modules.misc import introduction, invite, backup
from modules.config import prefix


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
        help="Simple status check, this command will not return the latency of the bot process as this is "
             "fairly irrelevant. If the bot replies, it's good to go.",
    )
    @commands.check(checks.channel)
    async def ping(self, ctx):
        return await ctx.respond(embed=MiscInfo.ping(ctx, self.client))

    @bridge.bridge_command(
        name="uptime",
        description="Racu uptime",
        help="See how long Racu has been online, the uptime shown will reset when the Misc module is reloaded.",
    )
    @commands.check(checks.channel)
    async def uptime(self, ctx):

        unix_timestamp = int(round(self.start_time.timestamp()))
        return await ctx.respond(embed=MiscInfo.uptime(ctx, self.client, unix_timestamp))

    @bridge.bridge_command(
        name="invite",
        description="Generate an invite link",
        help="Generate a link to invite Racu to your own server!"
    )
    async def invite_command(self, ctx):
        return await invite.cmd(ctx)

    @bridge.bridge_command(
        name="prefix",
        description="See the server's current prefix",
        guild_only=True
    )
    @commands.guild_only()
    @commands.check(checks.channel)
    async def prefix_command(self, ctx):
        return await prefix.get_cmd(ctx)

    @bridge.bridge_command(
        name="introduction",
        aliases=["intro", "introduce"],
        guild_only=False,
        description="This command can only be done in DMs.",
        help="Introduce yourself to a server. For now this command "
             "can only be done in ONE server and only as a __slash command in Racu's DMs__."
    )
    @commands.dm_only()
    async def intro_command(self, ctx):
        return await introduction.cmd(self, ctx)


def setup(client):
    client.add_cog(Misc(client))

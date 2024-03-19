import discord
from lib import formatter

question_icon = "https://i.imgur.com/8xccUws.png"
exclam_icon = "https://i.imgur.com/vitwMUu.png"


def clean_info_embed(ctx):
    embed = discord.Embed(
        color=discord.Color.brand_green(),
        description=f"**{ctx.author.name}** "
    )

    return embed


class EconInfo:
    @staticmethod
    def daily_reward_claimed(ctx, formatted_amount, streak):
        embed = clean_info_embed(ctx)
        embed.description += f"you claimed your reward of **${formatted_amount}**!"

        if streak > 1:
            embed.set_footer(text=f"You're on a streak of {streak} days",
                             icon_url=exclam_icon)

        return embed


class MiscInfo:
    @staticmethod
    def ping(ctx, client):
        embed = clean_info_embed(ctx)
        embed.description += "I'm online!"
        embed.set_footer(text=f"Latency: {round(1000 * client.latency)}ms", icon_url=exclam_icon)

        return embed

    @staticmethod
    def uptime(ctx, client, unix_time):
        embed = clean_info_embed(ctx)
        embed.description += f"I've been online since <t:{unix_time}:R>"
        embed.set_footer(text=f"Latency: {round(1000 * client.latency)}ms", icon_url=exclam_icon)

        return embed

    @staticmethod
    def invite(ctx):
        embed = clean_info_embed(ctx)
        embed.description += "thanks for inviting me to your server!"

        return embed

    @staticmethod
    def set_prefix(ctx, prefix):
        embed = clean_info_embed(ctx)
        embed.description += f"my prefix changed to `{prefix}`"

        return embed

    @staticmethod
    def get_prefix(ctx, prefix):
        embed= clean_info_embed(ctx)
        embed.description += f"my prefix is `{prefix}`"
        embed.set_footer(text=f"You can change this with '{formatter.get_prefix(ctx)}setprefix'",
                         icon_url=question_icon)

        return embed

import json
import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

from data.Currency import Currency
from data.Inventory import Inventory
from sb_tools import universal

load_dotenv('.env')

active_blackjack_games = {}
special_balance_name = os.getenv("SPECIAL_BALANCE_NAME")
cash_balance_name = os.getenv("CASH_BALANCE_NAME")

with open("config/economy.json") as file:
    json_data = json.load(file)


class InventoryCog(commands.Cog):
    def __init__(self, sbbot):
        self.bot = sbbot

    @commands.slash_command(
        name="inventory",
        description="Display your inventory.",
        guild_only=True
    )
    @commands.check(universal.beta_check)
    async def inventory(self, ctx):
        inventory = Inventory(ctx.author.id)
        inventory_dict = inventory.get_inventory()

        currency = Currency(ctx.author.id)
        balance = currency.cash

        embed = discord.Embed(description=f"**Balance: ${balance}**")
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)

        for item, quantity in inventory_dict.items():
            emote = self.bot.get_emoji(item.emote_id)
            embed.add_field(name=f"{emote} {item.display_name.capitalize()}",
                            value=f"*— Amount: `{quantity}`*",
                            inline=False)

        await ctx.respond(embed=embed)


def setup(sbbot):
    sbbot.add_cog(InventoryCog(sbbot))
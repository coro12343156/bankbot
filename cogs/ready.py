from discord.ext import commands
from discord import app_commands
import discord

import embed as em
import functions as func
import database as db

import os
import string
import random



class ready(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):

        # コンソールに出力
        print(f"Bot名: {self.bot.user} On ready!!")
        print("------")

        



async def setup(bot):
    await bot.add_cog(ready(bot))
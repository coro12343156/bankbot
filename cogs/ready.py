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

        ## ランダムな16文字を生成
        result = ''.join(random.choices(string.ascii_letters + string.digits, k=16))

        # スラッシュコマンドを反映させる
        for guild in self.bot.guilds:
            self.bot.tree.copy_global_to(guild=guild)
            await self.bot.tree.sync(guild=guild)
        print("slash commands has been synced!!")

        # コンソールに出力
        os.environ['PASS'] = result
        print(f"Bot名: {self.bot.user} On ready!!")
        print(os.environ['PASS'])
        print("------")

        





async def setup(bot):
    await bot.add_cog(ready(bot))
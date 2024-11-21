from discord.ext import commands, tasks
from discord import app_commands
import discord

import embed as em
import functions as func
import database as db


# commands.Cogを継承する
class backup(commands.Cog): #好きな名前でOK(機能がわかる名前にすると良い)
    def __init__(self, bot):
        self.bot = bot
        self.backup.start()

    # タスクループ
    @tasks.loop(minutes=db.config["backup_minutes"])
    async def backup(self):
        channel = self.bot.get_channel(db.config["backup_channel"])
        await channel.send(file=discord.File("./data.db"))
        

    # コマンドのエラーをprintするイベント
    @backup.error #ここの名前も変える
    async def raise_error(self, ctx, error):
        print(error)

async def setup(bot):
    await bot.add_cog(backup(bot)) #ここの名前も変える
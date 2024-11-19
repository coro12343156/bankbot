from discord.ext import commands
from discord import app_commands
import discord

import embed as em
import functions as func
import database as db


# commands.Cogを継承する
class hello(commands.Cog): #好きな名前でOK(機能がわかる名前にすると良い)
    def __init__(self, bot):
        self.bot = bot


    # イベントリスナー(ボットが起動したときやメッセージを受信したとき等)
    @commands.Cog.listener()
    async def on_ready(self):
        print("Cog ready!")
	
    # コマンドデコレーター(descriptionで説明が書ける)
    @app_commands.command(name="hello", description="コマンドの説明")
    async def hello(self,interaction:discord.Interaction):
        await interaction.response.send_message("hello!")

    # コマンドのエラーをprintするイベント
    @hello.error #ここの名前も変える
    async def raise_error(self, ctx, error):
        print(error)

async def setup(bot):
    await bot.add_cog(hello(bot)) #ここの名前も変える
from discord.ext import commands
from discord import app_commands
import discord


# commands.Cogを継承する
class ping(commands.Cog): #好きな名前でOK(機能がわかる名前にすると良い)
    def __init__(self, bot):
        self.bot = bot

	
    # コマンドデコレーター(descriptionで説明が書ける)
    @app_commands.command(name="ping", description="pingします")
    async def ping(self,interaction:discord.Interaction):

        await interaction.response.defer(ephemeral=True, thinking=True)

        await interaction.followup.send("pong!")

    # コマンドのエラーをprintするイベント
    @ping.error #ここの名前も変える
    async def raise_error(self, ctx, error):
        print(error)

async def setup(bot):
    await bot.add_cog(ping(bot)) #ここの名前も変える
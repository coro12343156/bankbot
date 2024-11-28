from discord.ext import commands
from discord import app_commands
import discord

import embed as em
import functions as func
import database as db
from bank import Account


# commands.Cogを継承する
class info(commands.Cog): #好きな名前でOK(機能がわかる名前にすると良い)
    def __init__(self, bot):
        self.bot = bot


    # コマンドデコレーター(descriptionで説明が書ける)
    @app_commands.command(name="info", description="口座情報を表示します")
    @app_commands.describe(name="口座名")
    async def info(self, interaction:discord.Interaction, name:str=""):

        await interaction.response.defer(ephemeral=True, thinking=True)

        # 口座名が空白の場合は個人口座を指定したものとみなす
        if name == "":
            name = interaction.user.mention

        # 口座情報を取得
        try:
            account = db.get_account(name)

        # 口座がなかった場合
        except db.AccountNotFoundError:
                embed = em.create({
                    "エラー":f"口座「{name}」は存在しません"
                },"red")
                await interaction.followup.send(embed=embed, ephemeral=True)
                return

        # メンバーに含まれていない場合
        if not interaction.user.mention in account.members:
            embed = em.create({
                "エラー":f"口座「{name}」の情報を表示する権限を持っていません"
            },"red")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        embed = em.create({
                "口座情報":f"口座「{name}」の口座情報を表示します",
                "管理者":f"{account.owner}",
                "口座タイプ":f"{account.account_type}",
                "残高":f"{account.bal}",
                "メンバー":f"{', '.join(account.members)}",
                "口座状態":"**凍結中**" if account.frozen else "利用可能"
            })
        await interaction.followup.send(embed=embed, ephemeral=True)


    # コマンドのエラーをprintするイベント
    @info.error #ここの名前も変える
    async def raise_error(self, ctx, error):
        print(error)
    


async def setup(bot):
    await bot.add_cog(info(bot)) #ここの名前も変える

from discord.ext import commands
from discord import app_commands
import discord

import embed as em
import functions as func
import database as db
from bank import Account, flter

import math


# commands.Cogを継承する
class history(commands.Cog): #好きな名前でOK(機能がわかる名前にすると良い)
    def __init__(self, bot):
        self.bot = bot


    # コマンドデコレーター(descriptionで説明が書ける)
    @app_commands.command(name="history", description="口座操作履歴を表示します")
    @app_commands.describe(name="口座名")
    @app_commands.describe(page="ページ")
    @app_commands.describe(keyword="指定した文字列でログを検索できます")
    async def history(self, interaction:discord.Interaction, name:str="", page:int=1, keyword:str=""):

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
        
        embed, view = func.make_history(page, name, keyword)
        await interaction.followup.send(embed=embed, ephemeral=True, view=view)


    # インタラクション
    @commands.Cog.listener()
    async def on_interaction(self, interaction:discord.Interaction):
        try:
            data = func.parse_interaction(interaction)

            # interactionが期限切れの場合
            if data == None:
                embed = em.create({
                    "エラー":f"このインタラクションは期限切れです"
                },"red")
                await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=5)

            # 違うコマンドのinteractionは弾く
            if data["command"] != "history":
                return
            
            ID = data["id"]

            # ページ変える
            if ID == "change_page":
                embed, view = func.make_history(data["page"], data["name"], data["keyword"])
                await interaction.response.send_message(embed=embed, ephemeral=True, view=view)
            # フィルター
            if ID == "filter":
                embed, view = func.make_history(data["page"], data["name"], data["keyword"], FILTERS=data["values"])
                await interaction.response.send_message(embed=embed, ephemeral=True, view=view)
        except Exception as e:
            print(f"{e.__class__.__name__}: {e}")


    # コマンドのエラーをprintするイベント
    @history.error #ここの名前も変える
    async def raise_error(self, ctx, error):
        print(error)
    


async def setup(bot):
    await bot.add_cog(history(bot)) #ここの名前も変える
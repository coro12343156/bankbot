from discord.ext import commands
from discord import app_commands
import discord

import embed as em
import functions as func
import database as db
from bank import Account

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

        # ログリスト取得＆反転
        logs = reversed(db.get_log(name))
        # keywordで検索
        logs = list(filter(lambda x: keyword in str(x), logs))

        # pageが負だった場合
        if page < 1:
            embed = em.create({
                "エラー":f"正しいページを入力してください"
            },"red")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        # リスト長から算出されるページ数
        len_page = math.ceil(len(logs)/25)

        # 指定されたpageがページ数を超えていた場合
        if page > len_page:
            page = len_page

        # そもそもlogsが25個以下の場合、その全てを表示する
        # そうでなければ
        if len(logs) > 25:
            # 指定ページが最終ページの場合
            if page == len_page:
                logs = logs[25*(page-1):]
            else:
                logs = logs[25*(page-1):25*page]

        dic = {
            "口座操作履歴":f"口座「{name}」の口座操作の履歴を表示します\n全{len_page}ページ中{page}ページ目"
        }

        # 各ログに対してembedのフィールドを設ける
        for log in logs:
            dic[log[1]] = f"口座名:{log[2]}, 操作者:{log[3]}, 内容:{log[4]}"

        embed = em.create(dic)
        await interaction.followup.send(embed=embed, ephemeral=True)



    # コマンドのエラーをprintするイベント
    @history.error #ここの名前も変える
    async def raise_error(self, ctx, error):
        print(error)
    


async def setup(bot):
    await bot.add_cog(history(bot)) #ここの名前も変える
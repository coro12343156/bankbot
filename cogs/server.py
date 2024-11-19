from discord.ext import commands
from discord import app_commands
import discord

import embed as em
import functions as func
import database as db

from python_mcstatus import statusJava
import datetime
import base64

# commands.Cogを継承する
class server(commands.Cog): #好きな名前でOK(機能がわかる名前にすると良い)
    def __init__(self, bot):
        self.bot = bot

	
    # コマンドデコレーター(descriptionで説明が書ける)
    @app_commands.command(name="server", description="サーバーの状況を確認します※Java限定")
    @app_commands.describe(address="サーバーアドレス")
    @app_commands.describe(port="ポート")
    async def server(self,interaction:discord.Interaction,address:str,port:int=25565):
        # サーバー情報取得
        data = statusJava(address,port=port)

        # 現在時刻取得
        t_delta = datetime.timedelta(hours=9)
        JST = datetime.timezone(t_delta, 'JST')
        now = datetime.datetime.now(JST)
        d = now.strftime('%Y/%m/%d %H:%M:%S')

        # Embed作る（dicがcreateに渡す辞書）
        dic = {f"サーバー：{address}":f"取得日時：{d}"}

        if data.online: # 鯖がオンラインかどうか
            dic[":white_check_mark:オンライン"] = f"```{data.motd.clean}```"
            dic["プレイヤー"] = f"{data.players.online}/{data.players.max}"
        else:
            dic[":x:オフライン"] = f"サーバーが起動していないか、アドレスが間違っています。"
        
        embed = em.create(dic)
        await interaction.response.send_message(embed=embed)

    # コマンドのエラーをprintするイベント
    @server.error
    async def raise_error(self, ctx, error):
        print(error)


async def setup(bot):
    await bot.add_cog(server(bot)) #ここの名前も変える
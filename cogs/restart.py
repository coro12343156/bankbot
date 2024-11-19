from discord.ext import commands
from discord import app_commands
import discord

import embed as em
import functions as func
import database as db

import os

# 管理者コマンド
# cogsを再読込して、スラッシュコマンドの同期もします（後者は実行時に選べます）


# commands.Cogを継承する
class restart(commands.Cog): #好きな名前でOK(機能がわかる名前にすると良い)
    def __init__(self, bot):
        self.bot = bot

	
    # コマンドデコレーター(descriptionで説明が書ける)
    @app_commands.command(name="restart", description="botを再読み込みします")
    @app_commands.describe(sync="スラッシュコマンドを同期するかどうか")
    async def restart(self,interaction:discord.Interaction, sync:bool=False):

        # 管理者でない場合
        if not func.is_admin(interaction.user): 
            embed = em.create({
                "権限エラー":"管理者ではないので使用できません！"
            },"red")
            await interaction.response.send_message(embed=embed)
            return


        embed = em.create({
            "/restart":"botを再読み込みします"
        })
        await interaction.response.send_message(embed=embed, ephemeral=True)

        # Cog一覧(cogsフォルダの.pyファイル一覧)を取得
        cogs = [file for file in os.listdir("./cogs") if not file.startswith("_")]

        # Cog再登録
        for cog in cogs:
            await self.bot.reload_extension(f"cogs.{cog}".replace(".py",""))
            print(f"cogs.{cog} has been restarted")

        # スラッシュコマンドを反映させる（選択されたなら）
        if sync:
            for g in db.config["target_guilds"]:
                guild = await self.bot.fetch_guild(g)
                self.bot.tree.copy_global_to(guild=guild)
                await self.bot.tree.sync(guild=guild)
            print("slash commands has been synced!!")

        embed = em.create({
            "再読み込み完了":"botの再読み込みが完了しました！"
        },"green")
        await interaction.channel.send(embed=embed, delete_after=10)


async def setup(bot):
    await bot.add_cog(restart(bot)) #ここの名前も変える
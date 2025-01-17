from discord.ext import commands
from discord import app_commands
import discord

import embed as em
import functions as func
import database as db


# 管理者コマンド
# スラッシュコマンドを同期します（globalか否かは実行時に選べます）


# commands.Cogを継承する
class sync(commands.Cog): #好きな名前でOK(機能がわかる名前にすると良い)
    def __init__(self, bot):
        self.bot = bot

	
    # コマンドデコレーター(descriptionで説明が書ける)
    @app_commands.command(name="sync", description="botをグローバルsyncします")
    async def sync(self,interaction:discord.Interaction):

        await interaction.response.defer(ephemeral=True, thinking=True)

        # 管理者でない場合
        if not func.is_admin(interaction.user): 
            embed = em.create({
                "権限エラー":"管理者ではないので使用できません！"
            },"red")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        # スラッシュコマンドを反映させる（選択されたなら）
        await self.bot.tree.sync()
        print("slash commands has been synced!! (global sync)")

        embed = em.create({
            "sync完了":"コマンドがglobal syncされました！"
        },"green")
        await interaction.followup.send(embed=embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(sync(bot)) #ここの名前も変える
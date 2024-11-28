from discord.ext import commands
from discord import app_commands
import discord

import embed as em
import functions as func
import database as db
from bank import Account


# commands.Cogを継承する
class assign(commands.Cog): #好きな名前でOK(機能がわかる名前にすると良い)
    def __init__(self, bot):
        self.bot = bot


    # コマンドデコレーター(descriptionで説明が書ける)
    @app_commands.command(name="assign", description="口座の管理者を移譲します")
    @app_commands.describe(name="口座名")
    @app_commands.describe(user="移譲先ユーザー　口座メンバーに入っている必要があります")
    @app_commands.describe(confirm="この操作は取り消せません！！！！！　本当に実行する場合はTrueを入力してください")
    async def assign(self, interaction:discord.Interaction, name:str, user:discord.User, confirm:bool=False):

        await interaction.response.defer(ephemeral=True, thinking=True)

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

        # 口座管理者でない場合
        if interaction.user.mention != account.owner:
            embed = em.create({
                "エラー":f"口座「{name}」でこのコマンドを使用する権限を持っていません"
            },"red")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        # 凍結されている場合
        if account.frozen:
            embed = em.create({
                "エラー":f"口座「{name}」は凍結されています"
            },"red")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        # confirm が false の場合
        if not confirm:
            embed = em.create({
                "エラー":f"`confirm`を`True`にして下さい"
            },"red")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return            

        # 移譲先ユーザーがメンバーに含まれていない場合
        if not user.mention in account.members:
            embed = em.create({
                "エラー":f"{user.mention}は口座のメンバーではありません\n口座を移譲するには両方がメンバーである必要があります"
            },"red")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        # account.ownerを変更、ログ作成、データベースに保存
        account.owner = user.mention
        log_id = db.create_log(interaction.user.mention, name, f'口座「{name}」の管理者を{interaction.user.mention}から{user.mention}へ変更')
        account.logs.append(log_id) #作成したログと口座の結びつけ
        db.update_account(account)

        embed = em.create({
                "削除完了":f"口座「{name}」の管理者を{interaction.user.mention}から{user.mention}へ変更しました"
            }, "green")
        await interaction.followup.send(embed=embed, ephemeral=True)


    # コマンドのエラーをprintするイベント
    @assign.error #ここの名前も変える
    async def raise_error(self, ctx, error):
        print(error)
    


async def setup(bot):
    await bot.add_cog(assign(bot)) #ここの名前も変える
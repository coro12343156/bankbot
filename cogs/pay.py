from discord.ext import commands
from discord import app_commands
import discord

import embed as em
import functions as func
import database as db
from bank import Account


# commands.Cogを継承する
class pay(commands.Cog): #好きな名前でOK(機能がわかる名前にすると良い)
    def __init__(self, bot):
        self.bot = bot


    # コマンドデコレーター(descriptionで説明が書ける)
    @app_commands.command(name="pay", description="送金します")
    @app_commands.describe(name="送金元の口座名")
    @app_commands.describe(target="送金先の口座名")
    @app_commands.describe(amount="金額")
    @app_commands.describe(description="送金内容")
    async def pay(self, interaction:discord.Interaction, name:str, target:str, amount:int, description:str=""):

        # 送金元と送金先が同じな場合
        if name == target:
            embed = em.create({
                "エラー":f"送金元と送金先の口座を同じにすることはできません"
            },"red")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # 口座情報を取得
        try:
            account = db.get_account(name)

        # 口座がなかった場合
        except db.AccountNotFoundError:
                embed = em.create({
                    "エラー":f"口座「{name}」は存在しません"
                },"red")
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
        
        # 口座情報を取得
        try:
            target_account = db.get_account(target)

        # 口座がなかった場合
        except db.AccountNotFoundError:
                embed = em.create({
                    "エラー":f"口座「{target}」は存在しません"
                },"red")
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return

        # メンバーに含まれていない場合
        if not interaction.user.mention in account.members:
            embed = em.create({
                "エラー":f"口座「{name}」でこのコマンドを実行する権限を持っていません"
            },"red")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # 凍結されている場合
        if account.frozen:
            embed = em.create({
                "エラー":f"口座「{name}」は凍結されています"
            },"red")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # 送金額が正でない場合
        if amount < 1:
            embed = em.create({
                "エラー":f"送金額は1以上の整数を指定してください。"
            },"red")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # 残高が足りない場合
        if account.bal < amount:
            embed = em.create({
                "エラー":f"口座「{name}」の残高が足りません"
            },"red")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # 送金元から送金額を引く
        try:
            account.bal -= amount
        except:
            embed = em.create({
                "エラー":f"不適切な値か、口座の残高が負になるような値が入力されました"
            },"red")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # 送金先に送金額を足す
        target_account.bal += amount

        # ログ作成、データベースに保存
        log_id = db.create_log(interaction.user.mention, name, f'口座「{name}」から口座「{target}」に{amount}送金　内容：{description}')
        account.logs.append(log_id) #作成したログと口座の結びつけ
        target_account.logs.append(log_id) #作成したログと口座の結びつけ
        db.update_account(account)
        db.update_account(target_account)
        
        embed = em.create({
                "変更完了":f'以下の内容で送金しました',
                "送金元":f'{name}',
                "送金先":f'{target}',
                "金額":f'{amount}',
                "送金内容":f'{description}',
            }, "green")
        await interaction.response.send_message(embed=embed, ephemeral=True)


    # コマンドのエラーをprintするイベント
    @pay.error #ここの名前も変える
    async def raise_error(self, ctx, error):
        print(error)
    


async def setup(bot):
    await bot.add_cog(pay(bot)) #ここの名前も変える
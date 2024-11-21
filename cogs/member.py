from discord.ext import commands
from discord import app_commands
import discord

import embed as em
import functions as func
import database as db
from bank import Account


# commands.Cogを継承する
class member(commands.Cog): #好きな名前でOK(機能がわかる名前にすると良い)
    def __init__(self, bot):
        self.bot = bot

	
    # memberコマンドグループ
    member = app_commands.Group(name="member", description="口座のメンバーを管理します")


    ########### 追加コマンド(/member add)
    @member.command(name="add", description="メンバーを追加します")
    @app_commands.describe(name="口座名")
    @app_commands.describe(user="追加するユーザー")
    async def add(self, interaction:discord.Interaction, name:str, user:discord.User):

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

        # 口座管理者でない場合
        if interaction.user.mention != account.owner:
            embed = em.create({
                "エラー":f"口座「{name}」でこのコマンドを使用する権限を持っていません"
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
        
        # 個人口座の場合
        if account.account_type == "person":
            embed = em.create({
                "エラー":f"口座「{name}」は個人口座なのでメンバーの追加はできません"
            },"red")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # 既ににいる場合
        if user.mention in account.members:
            embed = em.create({
                "エラー":f"{user.mention}は既に口座「{name}」のメンバーです"
            },"red")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # account.membersに追加、ログ作成、データベースに保存
        account.members.append(user.mention)
        log_id = db.create_log(interaction.user.mention, name, f'口座「{name}」のメンバーに{user.mention}を追加')
        account.logs.append(log_id) #作成したログと口座の結びつけ
        db.update_account(account)
        
        embed = em.create({
                "追加完了":f"口座「{name}」のメンバーに{user.mention}を追加しました"
            }, "green")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    # コマンドのエラーをprintするイベント
    @add.error
    async def raise_error(self, ctx, error):
        print(error)


    ########### 追加コマンド(/member add)
    @member.command(name="remove", description="メンバーを削除します")
    @app_commands.describe(name="口座名")
    @app_commands.describe(user="削除するユーザー")
    async def remove(self, interaction:discord.Interaction, name:str, user:discord.User):

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

        # 口座管理者でない場合
        if interaction.user.mention != account.owner:
            embed = em.create({
                "エラー":f"口座「{name}」でこのコマンドを使用する権限を持っていません"
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
        
        # 管理者はメンバーから消せない
        if user.mention == account.owner:
            embed = em.create({
                "エラー":f"口座の管理者が自らをメンバーから削除することはできません"
            },"red")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return             
        
        # 既にいない場合
        if not user.mention in account.members:
            embed = em.create({
                "エラー":f"{user.mention}は既に口座「{name}」のメンバーではありません"
            },"red")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # account.membersに追加、ログ作成、データベースに保存
        account.members.remove(user.mention)
        log_id = db.create_log(interaction.user.mention, name, f'口座「{name}」のメンバーから{user.mention}を削除')
        account.logs.append(log_id) #作成したログと口座の結びつけ
        db.update_account(account)
        
        embed = em.create({
                "削除完了":f"口座「{name}」のメンバーから{user.mention}を削除しました"
            }, "green")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    # コマンドのエラーをprintするイベント
    @remove.error
    async def raise_error(self, ctx, error):
        print(error)




async def setup(bot):
    await bot.add_cog(member(bot)) #ここの名前も変える
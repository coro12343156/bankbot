from discord.ext import commands
from discord import app_commands
import discord

import embed as em
import functions as func
import database as db
from bank import Account

import math
import os


# commands.Cogを継承する
class admin(commands.Cog): #好きな名前でOK(機能がわかる名前にすると良い)
    def __init__(self, bot):
        self.bot = bot

	
    # adminコマンドグループ
    admin = app_commands.Group(name="admin", description="管理者コマンド")


    ########### 口座開設コマンド(/admin open)
    @admin.command(name="open", description="口座を開設します")
    @app_commands.describe(owner="口座の管理者")
    @app_commands.describe(account_type="口座の種類")
    @app_commands.describe(name="口座名　個人口座では強制的にユーザー名になります")
    async def _open(self, interaction:discord.Interaction, owner:discord.User, account_type:str, name:str=""):

        await interaction.response.defer(ephemeral=True, thinking=True)

        # 管理者でない場合
        if not func.is_admin(interaction.user):
            embed = em.create({
                "エラー":f"このコマンドを使用する権限を持っていません"
            },"red")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return            

        # 口座の種類が規定のもの以外だった場合
        account_type_list = ["person", "group"]
        if not account_type in account_type_list:
            embed = em.create({
                "エラー":f"口座の種類は** {', '.join(account_type_list)} **のいずれかです"
            },"red")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        # 個人口座だった場合、強制的に口座名をユーザー名にする
        if account_type == "person":
            name = owner.mention

        # 口座名が空白の場合
        if name == "":
            embed = em.create({
                "エラー":f"口座名を入力してください"
            },"red")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        # 個人口座ではないにもかかわらず、口座名にユーザー名を指定した場合
        if account_type != "person" and name == owner.mention:
            embed = em.create({
                "エラー":f"個人口座でない場合、口座名にユーザーを指定することはできません"
            },"red")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        # Accountインスタンスを生成、ログ作成、データベースに保存
        account = Account(name, owner.mention, account_type)
        log_id = db.create_log("admin", name, f'口座「{name}」を作成')
        account.logs.append(log_id) #作成したログと口座の結びつけ
        try:
            db.create_account(account)
        except db.AccountExistsError: # 口座が存在していた場合
            embed = em.create({
                "エラー":f"口座「{name}」は既に存在しています"
            },"red")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        embed = em.create({
                "口座作成完了":f"口座「{name}」の作成が完了しました\n`/info [口座名]`（個人口座の場合`/info`でOK）で口座情報が確認できます"
            }, "green")
        await interaction.followup.send(embed=embed, ephemeral=True)

    # コマンドのエラーをprintするイベント
    @_open.error
    async def raise_error(self, ctx, error):
        print(error)


    ########### 口座情報表示コマンド(/admin info)
    @admin.command(name="info", description="口座情報を表示します")
    @app_commands.describe(name="口座名")
    async def info(self, interaction:discord.Interaction, name:str):

        await interaction.response.defer(ephemeral=True, thinking=True)

        # 管理者でない場合
        if not func.is_admin(interaction.user):
            embed = em.create({
                "エラー":f"このコマンドを使用する権限を持っていません"
            },"red")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

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

        embed = em.create({
                "口座情報":f"口座「{name}」の口座情報を表示します",
                "管理者":f"{account.owner}",
                "口座タイプ":f"{account.account_type}",
                "残高":f"{account.bal}",
                "メンバー":f"{', '.join(account.members)}"
            })
        await interaction.followup.send(embed=embed, ephemeral=True)

    # コマンドのエラーをprintするイベント
    @info.error
    async def raise_error(self, ctx, error):
        print(error)


    ########### 口座凍結/凍結解除コマンド(/admin freeze)
    @admin.command(name="freeze", description="口座の凍結状態を変更します")
    @app_commands.describe(name="口座名")
    @app_commands.describe(frozen="凍結されているか")
    async def freeze(self, interaction:discord.Interaction, name:str, frozen:bool):

        await interaction.response.defer(ephemeral=True, thinking=True)

        # 管理者でない場合
        if not func.is_admin(interaction.user):
            embed = em.create({
                "エラー":f"このコマンドを使用する権限を持っていません"
            },"red")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

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

        # account.membersに追加、ログ作成、データベースに保存
        account.frozen = frozen
        log_id = db.create_log("admin", name, f'口座「{name}」の凍結状態を{frozen}に変更')
        account.logs.append(log_id) #作成したログと口座の結びつけ
        db.update_account(account)
        
        embed = em.create({
                "変更完了":f"口座「{name}」の凍結状態を{frozen}に変更しました"
            }, "green")
        await interaction.followup.send(embed=embed, ephemeral=True)

    # コマンドのエラーをprintするイベント
    @freeze.error
    async def raise_error(self, ctx, error):
        print(error)


    ########### 通貨付与コマンド(/admin give)
    @admin.command(name="give", description="通貨を付与します　注意：何も無いところから通貨を生み出して付与します")
    @app_commands.describe(name="口座名")
    @app_commands.describe(amount="付与量")
    async def give(self, interaction:discord.Interaction, name:str, amount:int):

        await interaction.response.defer(ephemeral=True, thinking=True)

        # 管理者でない場合
        if not func.is_admin(interaction.user):
            embed = em.create({
                "エラー":f"このコマンドを使用する権限を持っていません"
            },"red")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

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
        
        # 通貨付与
        try:
            account.bal += amount
        except:
            embed = em.create({
                "エラー":f"不適切な値か、口座の残高が負になるような値が入力されました"
            },"red")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        # ログ作成、データベースに保存
        log_id = db.create_log("admin", name, f'口座「{name}」に{amount}付与')
        account.logs.append(log_id) #作成したログと口座の結びつけ
        db.update_account(account)
        
        embed = em.create({
                "変更完了":f"口座「{name}」に{amount}付与しました"
            }, "green")
        await interaction.followup.send(embed=embed, ephemeral=True)

    # コマンドのエラーをprintするイベント
    @give.error
    async def raise_error(self, ctx, error):
        print(error)
    

    ########### 履歴表示コマンド(/admin history)
    @admin.command(name="history", description="口座操作履歴を表示します")
    @app_commands.describe(name="口座名")
    @app_commands.describe(page="ページ")
    @app_commands.describe(keyword="指定した文字列でログを検索できます")
    async def history(self, interaction:discord.Interaction, name:str="", page:int=1, keyword:str=""):

        await interaction.response.defer(ephemeral=True, thinking=True)

        # 管理者でない場合
        if not func.is_admin(interaction.user):
            embed = em.create({
                "エラー":f"このコマンドを使用する権限を持っていません"
            },"red")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        # ログリスト取得＆反転
        if name == "": # 口座指定されていない場合、全ての口座ログを対象とする
            logs = reversed(db.get_all_log())
        else:
            logs = reversed(db.get_log(name))

        # keywordが空白でないなら検索
        if keyword != "":
            logs = list(filter(lambda x: keyword in str(x), logs))
        else: # 検索しない場合、logsは型がlist_reverseiteratorなので、listになおす
            logs = list(logs)

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
            "口座操作履歴":f"該当する口座操作履歴を表示します\n全{len_page}ページ中{page}ページ目"
        }

        # 各ログに対してembedのフィールドを設ける
        for log in logs:
            dic[log[1]] = f"口座名:{log[2]}, 操作者:{log[3]}, 内容:{log[4]}"

        embed = em.create(dic)
        await interaction.followup.send(embed=embed, ephemeral=True)

    # コマンドのエラーをprintするイベント
    @history.error
    async def raise_error(self, ctx, error):
        print(error)


    ########### バックアップコマンド(/admin backup)
    @admin.command(name="backup", description="データベースファイルを送信します")
    async def backup(self, interaction:discord.Interaction):

        await interaction.response.defer(ephemeral=True, thinking=True)

        # 管理者でない場合
        if not func.is_admin(interaction.user):
            embed = em.create({
                "エラー":f"このコマンドを使用する権限を持っていません"
            },"red")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        await interaction.followup.send(file=discord.File("./data.db"), ephemeral=True)


    # コマンドのエラーをprintするイベント
    @history.error
    async def raise_error(self, ctx, error):
        print(error)



async def setup(bot):
    await bot.add_cog(admin(bot)) #ここの名前も変える

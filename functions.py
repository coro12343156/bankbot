import discord
import database as db

# bot全体にgeneralな関数を定義するファイル


def is_admin(user:discord.User) -> bool:
    """
    ユーザーがbot管理者か否かを判定します

    Parameters
    ----------
    user : discord.User
        判定するユーザーのUserオブジェクト
    """
    return user.id in db.config["admins"]


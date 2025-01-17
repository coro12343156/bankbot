from discord.ext import commands
import asyncio
import discord
import configparser
import os


async def main():

    root = os.path.dirname(__file__)

    # トークンファイル(token.ini)読み込み
    token_ini = configparser.ConfigParser()
    token_ini.read(os.path.join(root, "token.ini"), encoding="utf-8")
    TOKEN = token_ini["TOKEN"]["TOKEN"]

    # Botを定義
    bot = commands.Bot(command_prefix="/",intents=discord.Intents.all())

    # Cog一覧(cogsフォルダの.pyファイル一覧)を取得
    # ファイル名先頭に"__"があるファイルはcogとして読み込まない
    cogs = [file for file in os.listdir(os.path.join(root, "cogs")) if not file.startswith("_")]

    # Cog登録
    for cog in cogs:
        await bot.load_extension(f"cogs.{cog}".replace(".py",""))
        print(f"cogs.{cog} has been loaded")

    # Botを起動
    await bot.start(TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
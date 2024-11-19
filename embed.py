import discord
from discord import Color

# embedラッパーを定義するファイル

def create(elements:dict, color:str="blue") -> discord.Embed:
    """
    Embedを作成します
    
    Parameters
    ----------
    elements : dict
        見出しと本文の組み合わせ辞書\n
        例）{'送金':'以下の内容で送金を行いました', '送金先':"<@578905225876865065>", ...}

    color : str
        Embedの色\n
        デフォルトはblue\n
        red, yellow, green, blue のいずれか

    Returns
    -------
    embed : discord.Embed

    Raises
    ------
    KeyError
        color の値が上4つのどれでもなかった場合
    """
    colorset = {"red":Color.red(), "yellow":Color.yellow(), "green":Color.green(), "blue":Color.blue()}
    if not color in colorset:
        raise KeyError("color must be any 1 of red, yellow, green, blue")
    
    # elements を辞書からキーと値のタプルのリストに変換
    elements = list(elements.items())

    # titleとdescription
    embed = discord.Embed(
        color = colorset[color],
        title = elements[0][0],
        description = elements[0][1],
    )

    elements.pop(0)

    # fieldを追加
    for item in elements:
        embed.add_field(
            name = item[0],
            value = item[1],
            inline = False
        )

        

    embed.set_footer(text="testbot - Supported by coro56")
    return embed



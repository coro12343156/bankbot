import discord
import database as db
import embed as em

import json
import math
import string
import random
import gc

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


def parse_interaction(interaction:discord.Interaction) -> dict:
    """
    on_interaction で受け取った interaction を使いやすい形にします

    Parameters
    ----------
    interaction : discord.Interaction
        interaction
    """
    data = interaction.data
    print(interaction.type, data)
    # button or selectmenu
    if interaction.type == discord.InteractionType.component:
            # ボタン
            if data["component_type"] == 2:
                return load_object(data["custom_id"])
            

datas = {}
def save_object(obj:object) -> str:
    """
    Pythonのオブジェクトをfunctions.pyのローカル変数に保存します

    Parameters
    ----------
    obj : object
        保存するオブジェクト

    Return
    ----------
    key : str
        呼び出しキー
    """
    ## ランダムな16文字を生成
    key = ''.join(random.choices(string.ascii_letters + string.digits, k=16))

    datas[key] = obj
    return key



def load_object(key:str) -> object:
    """
    保存したオブジェクトを呼び出します

    Parameters
    ----------
    key : str
        呼び出しキー

    Return
    ----------
    obj : object
        保存したオブジェクト
    """
    obj = datas[key]
    del datas[key]
    return obj




def make_history(page:int, name:str, keyword:str, admin:bool=False) -> tuple:
    """
    history, admin historyコマンドの embed, view を作成します

    Return
    ----------
    (embed, view) : tuple
    """
    view = discord.ui.View()

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
        return embed, view

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

    
    text = "該当する" if name == "" else f"口座「{name}」の"
    dic = {
        "口座操作履歴":f"{text}口座操作の履歴を表示します\n全`{len_page}`ページ中`{page}`ページ目"
    }

    # 各ログに対してembedのフィールドを設ける
    for log in logs:
        dic[log[1]] = f"口座名:{log[2]}, 操作者:{log[3]}, 内容:{log[4]}"

    embed = em.create(dic)

    button = discord.ui.Button(emoji="⬅️", row=0, disabled=(page == 1), custom_id=save_object({
        "command":"history",
        "id":"change_page",
        "logs":logs,
        "page":page - 1,
        "name":name,
        "keyword":keyword
    }))
    view.add_item(button)
    button = discord.ui.Button(emoji="➡️", row=0, disabled=(page == len_page), custom_id=save_object({
        "command":"history",
        "id":"change_page",
        "logs":logs,
        "page":page + 1,
        "name":name,
        "keyword":keyword
    }))
    view.add_item(button)

    return embed, view
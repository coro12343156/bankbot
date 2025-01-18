import discord
import database as db
import embed as em
from bank import Account, flter

import copy
import math
import string
import random
import datetime

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


def parse_interaction(interaction:discord.Interaction) -> dict | None:
    """
    on_interaction で受け取った interaction を使いやすい形にします

    Parameters
    ----------
    （interactionが期限切れでない場合）
    interaction : discord.Interaction
        interaction
    （interactionが期限切れで場合）
    None
    """
    data = interaction.data
    # button or selectmenu
    if interaction.type == discord.InteractionType.component:
            # ボタン
            if data["component_type"] == 2:
                d = load_object(data["custom_id"])
                if d == None:
                    return d
                return d
            # セレクトメニュー
            if data["component_type"] == 3:
                d = load_object(data["custom_id"])
                if d == None:
                    return d
                d["values"] = data["values"]
                return d
            

data_object = {}
data_created_at = {}

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

    data_object[key] = obj
    now = datetime.datetime.now()
    data_created_at[key] = now
    return key



def load_object(key:str) -> object | None:
    """
    保存したオブジェクトを呼び出します。
    同時に保存から２分以上経過したオブジェクトを削除します。

    Parameters
    ----------
    key : str
        呼び出しキー

    Return
    ----------
    （見つかった場合）
    obj : object
        保存したオブジェクト
    （見つからなかった場合）
    None
    """

    # 見つからなかったらNoneを返す
    if not key in data_object.keys():
        return None

    obj = data_object[key]

    c = copy.copy(data_created_at)
    
    # ２分以上経過したオブジェクトを削除
    now = datetime.datetime.now()
    for k, v in c.items():
        if now > v + datetime.timedelta(minutes=2):
            del data_object[k]
            del data_created_at[k]

    return obj




def make_history(page:int, name:str, keyword:str, admin:bool=False, FILTERS:list=[]) -> tuple:
    """
    history, admin historyコマンドの embed, view を作成します

    Return
    ----------
    (embed, view) : tuple
    """
    view = discord.ui.View()
    options = [discord.SelectOption(label=k, emoji=emoji, default=(k in FILTERS)) for k, v, emoji in flter]

    # ログリスト取得＆反転
    if name == "": # 口座指定されていない場合、全ての口座ログを対象とする
        logs = list(reversed(db.get_all_log()))
    else:
        logs = list(reversed(db.get_log(name)))
   

    # キーワードかフィルターがあるなら検索
    KEYWORDS = set(keyword.split()) | set().union(*[set(list(filter(lambda x: FILTER in x, flter))[0][1]) for FILTER in FILTERS])
    if KEYWORDS != set():
        logs = [log for log in logs for k in KEYWORDS if k in str(log)]

    # pageが負だった場合
    if page < 1:
        embed = em.create({
            "エラー":f"正しいページを入力してください"
        },"red")
        return embed, view

    # リスト長から算出されるページ数
    len_page = math.ceil(len(logs)/25)

    # ヒットしなかったばあい
    if len_page < 1:
        embed = em.create({
            "エラー":f"条件にヒットするログが見つかりませんでした"
        },"red")           
        select = discord.ui.Select(row=1, min_values=0, max_values=len(flter), placeholder="フィルターを選択", options=options, custom_id=save_object({
            "command":"history",
            "id":"filter",
            "logs":logs,
            "page":1,
            "name":name,
            "keyword":keyword
        }))
        view.add_item(select)
        return embed, view

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
    if name == "":
        for log in logs:
            dic[log[1]] = f"**口座名**：{log[2]}\n**操作者**：{log[3]}\n{log[4]}"
    else: # 口座が指定されてなかった場合
        account = db.get_account(name)
        if account.account_type == "group":
            for log in logs:
                dic[log[1]] = f"**操作者**：{log[3]}\n{log[4]}"
        else: # 個人口座の場合
            for log in logs:
                if log[3] == "admin":
                    dic[log[1]] = f"adminによる操作\n{log[4]}"
                else:
                    dic[log[1]] = log[4]

    embed = em.create(dic)

    button = discord.ui.Button(emoji="⏪", row=0, disabled=(page == 1), custom_id=save_object({
        "command":"history",
        "id":"change_page",
        "logs":logs,
        "page":1,
        "name":name,
        "keyword":keyword
    }))
    view.add_item(button)
    button = discord.ui.Button(emoji="◀️", row=0, disabled=(page == 1), custom_id=save_object({
        "command":"history",
        "id":"change_page",
        "logs":logs,
        "page":page - 1,
        "name":name,
        "keyword":keyword
    }))
    view.add_item(button)
    button = discord.ui.Button(emoji="▶️", row=0, disabled=(page == len_page), custom_id=save_object({
        "command":"history",
        "id":"change_page",
        "logs":logs,
        "page":page + 1,
        "name":name,
        "keyword":keyword
    }))
    view.add_item(button)
    button = discord.ui.Button(emoji="⏩", row=0, disabled=(page == len_page), custom_id=save_object({
        "command":"history",
        "id":"change_page",
        "logs":logs,
        "page":len_page,
        "name":name,
        "keyword":keyword
    }))
    view.add_item(button)
      
    select = discord.ui.Select(row=1, min_values=0, max_values=len(flter), placeholder="フィルターを選択", options=options, custom_id=save_object({
        "command":"history",
        "id":"filter",
        "logs":logs,
        "page":1,
        "name":name,
        "keyword":keyword
    }))
    view.add_item(select)

    return embed, view
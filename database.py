import sqlite3
from bank import Account
import json
import random
import string
import datetime

db_name = "data.db"

# データベースを操作する関数を定義するファイル


# configテーブルの情報をconfig変数に変換する関数
def convert_config() -> dict:
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()

    cur.execute('select * from config')
    raw = cur.fetchall()

    dic = {}
    for ele in raw:
        dic[ele[0]] = eval(f'{ele[1]}({ele[2]})')

    cur.close()
    conn.close()

    return dic



# 指定された口座を探したけど見当たらなかった場合の例外
class AccountNotFoundError(Exception): pass

# 指定された口座情報を取得する関数
def get_account(name:str) -> Account:
    """
    指定された口座の情報をAccountインスタンスとして取得します

    Parameters
    ----------
    name : str
        取得する口座名

    Returns
    ----------
    account : bank.Account
        Accountインスタンス（口座情報）

    Raises
    ----------
    AccountNotFoundError
        指定された口座を探したけど見当たらなかった場合
    """
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()

    cur.execute(f"select * from account where name = '{name}'")
    raw = cur.fetchall()

    cur.close()
    conn.close()

    # 1件もヒットしなかったら例外を出す
    if raw == []:
        raise AccountNotFoundError(f"No such account data named '{name}' has found in the database")

    dic = json.loads(raw[0][1].replace("'",'"').replace("True","true").replace("False","false")) #Accountインスタンス変数の辞書
    account = Account(**dic) #をunpackingして渡す
    return account



# 指定された口座に情報を書き込む関数
def update_account(account:Account) -> None:
    """
    口座の情報を、渡されたAccountインスタンスで更新します\n
    この関数を実行することで、該当する口座のデータベースが上書きされます

    Parameters
    ----------
    account : bank.Account
        Accountインスタンス（口座情報）
    """
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()

    cur.execute(f'update account set data = "{account.__dict__}" where name = "{account.name}"')
    conn.commit()

    cur.close()
    conn.close()



# 口座を新規作成しようとしたら既に存在したときの例外
class AccountExistsError(Exception): pass

# 指定された口座を作成する関数
def create_account(account:Account) -> None:
    """
    渡されたAccountインスタンスで口座を作成します\n
    これはデータベース上に口座情報を登録するだけの関数であり、口座開設の一連の処理を行っているわけではないことに注意してください

    Parameters
    ----------
    account : bank.Account
        Accountインスタンス（口座情報）

    Raises
    ----------
    AccountExistsError
        口座を新規作成しようとしたら既に存在した場合
    """
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()

    try:
        cur.execute(f'insert into account values("{account.name}", "{account.__dict__}")')
    except sqlite3.IntegrityError: # 既に口座が存在した時
        raise AccountExistsError(f"Account data of '{account.name}' already exists in the database")
    
    conn.commit()

    cur.close()
    conn.close()



# ログを作成する関数
def create_log(operator:str, name:str, content:str) -> str:
    """
    ログを作成し、ログid（ログを一意に識別するための英数字列）を返します

    Parameters
    ----------
    operator : str
        操作した人のユーザー名
    name : str
        口座名
    content : str
        ログ本文
    
    Returns
    ----------
    log_id : str
        ログid
    """
    # ログidを作成する（英数字）
    # ログidが既存のログとかぶったときの処理は書いてません
    # ログidのパターンは約10^29通りらしいからね、まあかぶらないでしょ（）
    log_id = ''.join(random.choices(string.ascii_letters + string.digits, k=16))

    conn = sqlite3.connect(db_name)
    cur = conn.cursor()

    # 現在時刻取得
    t_delta = datetime.timedelta(hours=9)
    JST = datetime.timezone(t_delta, 'JST')
    now = datetime.datetime.now(JST)
    time = now.strftime('%Y/%m/%d %H:%M:%S')

    cur.execute(f'insert into log values("{log_id}", "{time}", "{name}", "{operator}", "{content}")')
    conn.commit()

    cur.close()
    conn.close()

    return log_id


# ログを取得する関数
def get_log(name:str) -> list:
    """
    ログを取得します

    Parameters
    ----------
    name : str
        口座名
    
    Returns
    ----------
    logs : list
        ログのリスト
    """
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()

    cur.execute(f"select * from log where name = '{name}'")
    raw = cur.fetchall()

    cur.close()
    conn.close()

    return raw



config = convert_config()

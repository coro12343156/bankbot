
# 銀行処理に必要で、全体に共通な関数やクラスを定義するファイル


# 口座クラス
class Account():
    """
    口座クラス\n
    口座を開設する場合は、Accountインスタンスを作成する時にキーワード引数を指定しないでください

    Attributes
    ---------
    name : str
        口座名
    owner : str
        口座管理者のユーザー名
    account_type : str
        口座のタイプ
    bal : int = 0
        残高
    members : list[int] = [owner]
        口座メンバーのユーザーidのリスト
    logs : list[int] = []
        ログidのリスト
    frozen : bool
        凍結されている -> True
    """
    def __init__(self, name:str, owner:int, account_type:str, bal:int=0, members:list=[], logs:list=[], frozen:bool=False):
        self.name = name
        self.owner = owner
        self.account_type = account_type
        self.bal = bal
        if members == []: # membersにownerは必ず含まれるようにする
            members = [owner]
        self.members = members
        self.logs = logs
        self.frozen = frozen

    # setattrメソッドをオーバーライドして、balに不適切な値が代入されそうになったらエラーを吐くようにする
    def __setattr__(self, name, value):
        if name != "bal": # 属性名がbalでないなら
            object.__setattr__(self, name, value) # ここで本来の「属性に値をsetする」処理を行う

        elif not isinstance(value, int): # 代入される値がintでなかったらエラーを吐く
            raise TypeError(f"account.bal must be integer but has gotten {type(value)}")
        
        elif not value >= 0: # 代入される値が0以上でない
            raise TypeError(f"account.bal must be 0 or more but has gotten {value}")

        else: # 適正値なので代入する
            object.__setattr__(self, name, value)



# history, admin historyコマンドのフィルター
flter = [
    ("収支", ["付与", "送金"], "💴"),
    ("口座操作", ["作成", "凍結状態", "管理者", "メンバー"], "🔧"),
    ("送金", ["送金"], "📤"),
    ("メンバー追加/削除", ["メンバー"], "👪"),
    ("管理者変更", ["管理者"], "👑"),
    ("残高変更", ["付与"], "✏️"),
    ("口座作成", ["作成"], "🆕"),
    ("凍結状態変更", ["凍結"], "🔏"),
]
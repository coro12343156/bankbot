Python 3.13.0 で動作確認済み



data.db の構造
テーブル：config (key|type|value)
    target_guilds: スラッシュコマンドを即時に適用したいギルドidのリスト
    admins: 管理者コマンドを使用できるユーザーidのリスト
テーブル：account (name|data)
テーブル：log（id|content）

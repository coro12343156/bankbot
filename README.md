Python 3.9.X で動作確認済み



data.db の構造
テーブル：config (key|type|value)
    target_guilds: スラッシュコマンドを即時に適用したいギルドidのリスト
    admins: 管理者コマンドを使用できるユーザーidのリスト
    backup_channel: バックアップを送信するチャンネル
    backup_minutes: バックアップを送信する間隔（分）
テーブル：account (name|data)
テーブル：log（id|time|name|operator|content）

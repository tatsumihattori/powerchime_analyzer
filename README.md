# Loginwindow Log Analyzer

macOSのloginwindowログを解析して、日毎の画面開始・終了時間を集計するツールです。

## 機能

- macOSのシステムログからloginwindow関連のログを自動取得
- 日毎の最初の画面開始時間と最後の終了時間を集計
- 開始・終了イベントの回数も記録
- 結果をCSVファイルに出力
- 詳細なログ表示オプション

## セットアップ

### 前提条件

- macOS
- Python 3.8以上
- Rye（Pythonパッケージ管理）

### インストール

1. 依存関係をインストール:

```bash
rye sync
```

2. スクリプトを実行可能にする:

```bash
chmod +x loginwindow_analyzer.py
```

## 使用方法

### 基本的な使用法

過去7日分のログを解析:

```bash
python loginwindow_analyzer.py
```

### オプション

- `--days, -d`: 分析する日数（デフォルト: 7日）
- `--output, -o`: 出力CSVファイル名（デフォルト: loginwindow_analysis.csv）
- `--verbose, -v`: 詳細なログを表示

### 使用例

過去30日分のログを解析:

```bash
python loginwindow_analyzer.py --days 30
```

結果を別のファイル名で保存:

```bash
python loginwindow_analyzer.py --output my_analysis.csv
```

詳細なログを表示:

```bash
python loginwindow_analyzer.py --verbose
```

## 出力形式

### コンソール出力

```text
=== 日毎の画面開始・終了時間サマリー ===
分析期間: 2024-01-01 から 2024-01-07
総日数: 7 日

日付  最初の開始 最後の終了 開始回数 終了回数
--------------------------------------------------------------------------------
2024-01-01 08:30:15  22:15:30  5  5
2024-01-02 09:00:00  21:45:20  3  3
...
```

### CSVファイル出力

- `date`: 日付
- `first_start_time`: その日の最初の開始時間
- `last_end_time`: その日の最後の終了時間
- `first_start_datetime`: 開始日時（完全）
- `last_end_datetime`: 終了日時（完全）
- `start_count`: 開始イベントの回数
- `end_count`: 終了イベントの回数

## 注意事項

- このツールは管理者権限が必要な場合があります
- ログの取得には`log show`コマンドを使用します
- システムの設定によっては、一部のログが取得できない場合があります

## トラブルシューティング

### ログが取得できない場合

1. 管理者権限で実行してみてください:

```bash
sudo python loginwindow_analyzer.py
```

2. システムログの設定を確認してください:

```bash
log show --predicate 'process == "loginwindow"' --last 1d
```

### イベントが検出されない場合

`--verbose`オプションを使用して、実際に取得されているログメッセージを確認してください。必要に応じて、`loginwindow_analyzer.py`の`start_patterns`と`end_patterns`を調整してください。

## ライセンス

MIT License

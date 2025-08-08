# PowerChime Log Analyzer

macOSのPowerChimeログを解析して、日毎のWake/Sleep時間を集計するツールです。

## 概要

このツールは、macOSシステムのPowerChimeプロセスのログを解析し、コンピューターの起動（Wake）と睡眠（Sleep）時間を日毎に集計します。午前5時を1日の区切りとして使用し、生活パターンの分析に適しています。

## 機能

- PowerChimeログの自動取得と解析
- 日毎の最初のWake時間と最後のSleep時間の抽出
- Wake/Sleepイベントの回数カウント
- 指定期間でのデータ分析（デフォルト7日間）

## 必要な環境

- macOS（PowerChimeログが利用可能）
- Python 3.8以上
- Rye（パッケージ管理）

## インストール

```bash
# リポジトリをクローン
git clone https://github.com/tatsumihattori/powerchime_analyzer.git
cd powerchime_analyzer

# Ryeを使用して依存関係をインストール
rye sync
```

## 使用方法

### 基本的な使用方法

```bash
# 過去7日間のデータを分析（デフォルト）
python powerchime_analyzer.py

# 特定の日数を指定
python powerchime_analyzer.py --days 14



# 詳細なログを表示
python powerchime_analyzer.py --verbose
```

### パッケージとしてインストールした場合

```bash
# Ryeでインストール後は以下のコマンドで実行可能
powerchime-analyzer --days 7
```

## オプション

- `--days, -d`: 分析する日数（デフォルト: 7日）
- `--verbose, -v`: 詳細なログを表示

## 出力形式

コンソールには以下の形式で結果が表示されます：

```
=== 日毎のWake/Sleep時間サマリー ===
分析期間: 2025-01-15 から 2025-01-21
総日数: 7 日

日付            最初のWake      最後のSleep     Wake回数    Sleep回数
--------------------------------------------------------------------------------
2025-01-15      07:30:15        23:45:30        3           2
2025-01-16      08:00:22        00:15:45        2           3
...
```

## 日付の取り扱いについて

このツールは午前5時を1日の区切りとして使用します。これにより、夜遅くまで起きている生活パターンでも自然な日毎の集計が可能です。

例：

- 1月15日 23:00のSleepイベント → 1月15日として記録
- 1月16日 02:00のWakeイベント → 1月15日として記録
- 1月16日 07:00のWakeイベント → 1月16日として記録

## 開発

### 依存関係の管理

```bash
# 開発依存関係も含めてインストール
rye sync --all-features

# 新しい依存関係を追加
rye add package_name

# 開発用依存関係を追加
rye add --dev package_name
```

### ビルド

```bash
# パッケージをビルド
rye build
```

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## 貢献

プルリクエストやイシューの報告を歓迎します。

## 注意事項

- このツールはmacOSでのみ動作します
- PowerChimeログにアクセスするため、適切な権限が必要な場合があります
- システムログの取得には時間がかかる場合があります

# PowerChime Log Analyzer

macOSのPowerChimeログを解析して、日毎のWake/Sleep時間を集計するツールです。

## 機能

- macOSのシステムログからPowerChime関連のログを自動取得
- 日毎の最初のWake時間と最後のSleep時間を集計
- Wake/Sleepイベントの回数も記録
- 結果をCSVファイルに出力
- 詳細なログ表示オプション
- **高度な解析機能**（セッション時間計算、統計情報、グラフ生成）

## ツール構成

### 1. 基本的な解析ツール (`loginwindow_analyzer.py`)

- シンプルな日毎のWake/Sleep時間集計
- CSVファイル出力
- 基本的な統計情報

### 2. 高度な解析ツール (`advanced_loginwindow_analyzer.py`)

- セッション時間の詳細計算（Wake→Sleepのペア）
- 統計情報の生成（平均、中央値、標準偏差など）
- グラフとチャートの自動生成
- 時間帯別・曜日別の分析
- より詳細なCSV出力とJSON統計ファイル

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
chmod +x advanced_loginwindow_analyzer.py
```

## 使用方法

### 基本的な使用法

過去7日分のログを解析:

```bash
python loginwindow_analyzer.py
```

### 高度な解析

過去7日分のログを詳細解析（グラフ付き）:

```bash
python advanced_loginwindow_analyzer.py
```

### オプション

#### 基本ツール (`loginwindow_analyzer.py`)

- `--days, -d`: 分析する日数（デフォルト: 7日）
- `--output, -o`: 出力CSVファイル名（デフォルト: powerchime_analysis.csv）
- `--verbose, -v`: 詳細なログを表示

#### 高度なツール (`advanced_loginwindow_analyzer.py`)

- `--days, -d`: 分析する日数（デフォルト: 7日）
- `--output, -o`: 出力CSVファイル名（デフォルト: powerchime_analysis.csv）
- `--output-dir`: グラフ出力ディレクトリ（デフォルト: 現在のディレクトリ）
- `--verbose, -v`: 詳細なログを表示
- `--no-graphs`: グラフ生成をスキップ

### 使用例

#### 基本ツール

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

#### 高度なツール

過去30日分のログを詳細解析:

```bash
python advanced_loginwindow_analyzer.py --days 30
```

グラフなしで解析:

```bash
python advanced_loginwindow_analyzer.py --no-graphs
```

グラフを別ディレクトリに出力:

```bash
python advanced_loginwindow_analyzer.py --output-dir ./graphs
```

## 出力形式

### 基本ツールの出力

#### コンソール出力

```text
=== 日毎のWake/Sleep時間サマリー ===
分析期間: 2024-01-01 から 2024-01-07
総日数: 7 日

日付  最初のWake 最後のSleep Wake回数 Sleep回数
--------------------------------------------------------------------------------
2024-01-01 08:30:15  22:15:30  5  5
2024-01-02 09:00:00  21:45:20  3  3
...
```

#### CSVファイル出力

- `date`: 日付
- `first_wake_time`: その日の最初のWake時間
- `last_sleep_time`: その日の最後のSleep時間
- `first_wake_datetime`: Wake日時（完全）
- `last_sleep_datetime`: Sleep日時（完全）
- `wake_count`: Wakeイベントの回数
- `sleep_count`: Sleepイベントの回数

### 高度なツールの出力

#### コンソール出力

```text
============================================================
詳細なPowerChimeログ解析結果
============================================================

📊 基本統計:
  分析期間: 2024-01-01 から 2024-01-07
  総日数: 7 日
  アクティブ日数: 7 日
  総セッション数: 35 回
  1日平均セッション数: 5.0 回
  平均セッション時間: 180.5 分
  総使用時間: 105.3 時間
  最も多い開始時間帯: 9時

⏰ セッション時間の統計:
  最短セッション: 5.2 分
  最長セッション: 480.0 分
  中央値: 165.0 分
  標準偏差: 120.3 分
```

#### 生成されるファイル

1. **CSVファイル**: 詳細な日毎データ
2. **JSONファイル**: 統計情報
3. **グラフファイル**:
   - `daily_usage.png`: 日毎の使用時間
   - `hourly_sessions.png`: 時間帯別のセッション開始回数
   - `session_duration_distribution.png`: セッション時間の分布
   - `weekday_pattern.png`: 曜日別のセッション開始回数

## テスト

テストスクリプトを実行して動作確認:

```bash
python test_analyzer.py
```

## 注意事項

- このツールは管理者権限が必要な場合があります
- ログの取得には`log show`コマンドを使用します
- システムの設定によっては、一部のログが取得できない場合があります
- グラフ生成には`matplotlib`と`seaborn`が必要です
- PowerChimeのDid WakeとDid Sleepイベントを解析します

## トラブルシューティング

### ログが取得できない場合

1. 管理者権限で実行してみてください:

```bash
sudo python loginwindow_analyzer.py
```

2. システムログの設定を確認してください:

```bash
log show --predicate 'process == "PowerChime"' --last 1d
```

### イベントが検出されない場合

`--verbose`オプションを使用して、実際に取得されているログメッセージを確認してください。必要に応じて、`loginwindow_analyzer.py`の`wake_patterns`と`sleep_patterns`を調整してください。

### グラフが生成されない場合

1. 依存関係が正しくインストールされているか確認:

```bash
rye sync
```

2. matplotlibのバックエンドを確認:

```bash
python -c "import matplotlib; print(matplotlib.get_backend())"
```

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。

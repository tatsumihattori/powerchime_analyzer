#!/usr/bin/env python3
"""
Loginwindow Log Analyzer

macOSのloginwindowログを解析して、日毎の画面開始・終了時間を集計します。
"""

import subprocess
import re
import pandas as pd
from datetime import datetime, timedelta
import click
from pathlib import Path
import json


class LoginwindowLogAnalyzer:
    def __init__(self):
        self.log_entries = []

    def get_loginwindow_logs(self, days_back=7):
        """指定された日数分のloginwindowログを取得"""
        try:
            # log showコマンドでloginwindow関連のログを取得
            cmd = [
                'log', 'show',
                '--predicate', 'process == "loginwindow"',
                '--last', f'{days_back}d',
                '--style', 'json'
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            logs = json.loads(result.stdout)

            for entry in logs:
                if 'eventMessage' in entry:
                    self.log_entries.append({
                        'timestamp': entry.get('timestamp', ''),
                        'message': entry['eventMessage'],
                        'process': entry.get('process', ''),
                        'subsystem': entry.get('subsystem', '')
                    })

            print(f"取得したログエントリ数: {len(self.log_entries)}")

        except subprocess.CalledProcessError as e:
            print(f"ログ取得エラー: {e}")
            return False
        except json.JSONDecodeError as e:
            print(f"JSON解析エラー: {e}")
            return False

        return True

    def parse_log_entries(self):
        """ログエントリを解析して画面開始・終了イベントを抽出"""
        events = []

        # 画面開始・終了を示すキーワードパターン
        start_patterns = [
            r'screen.*unlock',
            r'loginwindow.*start',
            r'display.*wake',
            r'wake.*display',
            r'sessionunlocked.*1',  # セッションがアンロックされた
            r'screenislocked.*0',   # 画面がアンロックされた
            r'loginwindow.*login',
            r'user.*login',
            r'loginwindow.*unlock',
            r'loginwindow.*wake',
            r'loginwindow.*resume',
            r'loginwindow.*activate'
        ]

        end_patterns = [
            r'screen.*lock',
            r'loginwindow.*stop',
            r'display.*sleep',
            r'sleep.*display',
            r'sessionunlocked.*0',  # セッションがロックされた
            r'screenislocked.*1',   # 画面がロックされた
            r'loginwindow.*logout',
            r'user.*logout',
            r'loginwindow.*lock',
            r'loginwindow.*sleep',
            r'loginwindow.*suspend',
            r'loginwindow.*deactivate'
        ]

        for entry in self.log_entries:
            message = entry['message'].lower()
            timestamp_str = entry['timestamp']

            try:
                # タイムスタンプを解析（macOSのログ形式に対応）
                # 例: "2025-07-23 16:27:06.105357+0900"
                if timestamp_str:
                    # タイムゾーン情報を標準形式に変換
                    # "+0900" -> "+09:00"
                    if '+' in timestamp_str and len(timestamp_str.split('+')[1]) == 4:
                        timezone_part = timestamp_str.split('+')[1]
                        timestamp_str = timestamp_str.replace(f"+{timezone_part}", f"+{timezone_part[:2]}:{timezone_part[2:]}")
                    elif '-' in timestamp_str and len(timestamp_str.split('-')[1]) == 4:
                        timezone_part = timestamp_str.split('-')[1]
                        timestamp_str = timestamp_str.replace(f"-{timezone_part}", f"-{timezone_part[:2]}:{timezone_part[2:]}")

                    timestamp = datetime.fromisoformat(timestamp_str)
                else:
                    continue

                # クラムシェルイベントを除外
                if 'clamshell' in message:
                    continue

                # 開始イベントかチェック
                is_start = any(re.search(pattern, message) for pattern in start_patterns)
                # 終了イベントかチェック
                is_end = any(re.search(pattern, message) for pattern in end_patterns)

                # 午前5時を1日の区切りとして日付を取得
                # 午前5時前は前日として扱う
                if timestamp.hour < 5:
                    date = timestamp.date() - timedelta(days=1)
                else:
                    date = timestamp.date()

                if is_start:
                    events.append({
                        'date': date,
                        'time': timestamp.time(),
                        'timestamp': timestamp,
                        'event_type': 'start',
                        'message': entry['message']
                    })
                elif is_end:
                    events.append({
                        'date': date,
                        'time': timestamp.time(),
                        'timestamp': timestamp,
                        'event_type': 'end',
                        'message': entry['message']
                    })

            except ValueError as e:
                print(f"タイムスタンプ解析エラー: {timestamp_str} - {e}")
                continue

        return events

    def aggregate_daily_times(self, events):
        """日毎の最初の開始時間と最後の終了時間を集計（午前5時を1日の区切りとする）"""
        daily_data = {}

        for event in events:
            # 午前5時を1日の区切りとして日付を取得
            # 午前5時前は前日として扱う
            event_time = event['timestamp']
            if event_time.hour < 5:
                # 午前5時前は前日として扱う
                date = event_time.date() - timedelta(days=1)
            else:
                # 午前5時以降は当日として扱う
                date = event_time.date()

            if date not in daily_data:
                daily_data[date] = {
                    'first_start': None,
                    'last_end': None,
                    'start_events': [],
                    'end_events': []
                }

            if event['event_type'] == 'start':
                daily_data[date]['start_events'].append(event['timestamp'])
                if daily_data[date]['first_start'] is None:
                    daily_data[date]['first_start'] = event['timestamp']
            else:  # end event
                daily_data[date]['end_events'].append(event['timestamp'])
                if daily_data[date]['last_end'] is None or event['timestamp'] > daily_data[date]['last_end']:
                    daily_data[date]['last_end'] = event['timestamp']

        # DataFrameに変換
        results = []
        for date, data in daily_data.items():
            results.append({
                'date': date,
                'first_start_time': data['first_start'].time() if data['first_start'] else None,
                'last_end_time': data['last_end'].time() if data['last_end'] else None,
                'first_start_datetime': data['first_start'],
                'last_end_datetime': data['last_end'],
                'start_count': len(data['start_events']),
                'end_count': len(data['end_events'])
            })

        return pd.DataFrame(results).sort_values('date')

    def save_results(self, df, output_file):
        """結果をCSVファイルに保存"""
        df.to_csv(output_file, index=False, encoding='utf-8')
        print(f"結果を保存しました: {output_file}")

    def print_summary(self, df):
        """結果のサマリーを表示"""
        print("\n=== 日毎の画面開始・終了時間サマリー ===")
        print(f"分析期間: {df['date'].min()} から {df['date'].max()}")
        print(f"総日数: {len(df)} 日")

        print("\n日付\t\t最初の開始\t最後の終了\t開始回数\t終了回数")
        print("-" * 80)

        for _, row in df.iterrows():
            start_time = row['first_start_time'].strftime('%H:%M:%S') if row['first_start_time'] else 'N/A'
            end_time = row['last_end_time'].strftime('%H:%M:%S') if row['last_end_time'] else 'N/A'
            print(f"{row['date']}\t{start_time}\t\t{end_time}\t\t{row['start_count']}\t\t{row['end_count']}")


@click.command()
@click.option('--days', '-d', default=7, help='分析する日数（デフォルト: 7日）')
@click.option('--output', '-o', default='loginwindow_analysis.csv', help='出力CSVファイル名')
@click.option('--verbose', '-v', is_flag=True, help='詳細なログを表示')
def main(days, output, verbose):
    """Loginwindowログを解析して日毎の画面開始・終了時間を集計"""

    print(f"Loginwindowログ解析を開始します（過去{days}日分）")

    analyzer = LoginwindowLogAnalyzer()

    # ログを取得
    if not analyzer.get_loginwindow_logs(days):
        print("ログの取得に失敗しました")
        return

    # ログエントリを解析
    events = analyzer.parse_log_entries()
    print(f"解析されたイベント数: {len(events)}")

    if verbose:
        print("\n=== 解析されたイベント ===")
        for event in events[:10]:  # 最初の10件を表示
            print(f"{event['date']} {event['time']} - {event['event_type']}: {event['message'][:100]}...")

    if not events:
        print("解析可能なイベントが見つかりませんでした")
        return

    # 日毎に集計
    df = analyzer.aggregate_daily_times(events)

    # 結果を表示
    analyzer.print_summary(df)

    # 結果を保存
    analyzer.save_results(df, output)


if __name__ == '__main__':
    main()

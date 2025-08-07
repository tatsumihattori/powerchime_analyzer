#!/usr/bin/env python3
"""
PowerChime Log Analyzer

macOSのPowerChimeログを解析して、日毎のWake/Sleep時間を集計します。
"""

import subprocess
import re
import pandas as pd
from datetime import datetime, timedelta
import click
from pathlib import Path
import json


class PowerChimeLogAnalyzer:
    def __init__(self):
        self.powerchime_entries = []

    def get_powerchime_logs(self, days_back=7):
        """指定された日数分のPowerChimeログを取得（午前5時区切り）"""
        try:
            # 現在時刻から午前5時区切りで指定日数分のログを取得
            now = datetime.now()

            # 今日の午前5時を基準に計算
            if now.hour < 5:
                # 現在時刻が午前5時前の場合、昨日の午前5時を基準とする
                base_time = now.replace(hour=5, minute=0, second=0, microsecond=0) - timedelta(days=1)
            else:
                # 現在時刻が午前5時以降の場合、今日の午前5時を基準とする
                base_time = now.replace(hour=5, minute=0, second=0, microsecond=0)

            # 指定日数分前の午前5時を計算
            start_time = base_time - timedelta(days=days_back)

            # ログ取得期間を計算（時間単位）
            hours_back = int((now - start_time).total_seconds() / 3600)

            print(f"PowerChimeログ取得期間: {start_time.strftime('%Y-%m-%d %H:%M')} から {now.strftime('%Y-%m-%d %H:%M')} ({hours_back}時間)")

            # PowerChimeログを取得
            cmd = [
                'log', 'show',
                '--predicate', 'process == "PowerChime"',
                '--last', f'{hours_back}h',
                '--style', 'json'
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            logs = json.loads(result.stdout)

            for entry in logs:
                if 'eventMessage' in entry:
                    self.powerchime_entries.append({
                        'timestamp': entry.get('timestamp', ''),
                        'message': entry['eventMessage'],
                        'process': entry.get('process', ''),
                        'subsystem': entry.get('subsystem', '')
                    })

            print(f"取得したPowerChimeログエントリ数: {len(self.powerchime_entries)}")

        except subprocess.CalledProcessError as e:
            print(f"ログ取得エラー: {e}")
            return False
        except json.JSONDecodeError as e:
            print(f"JSON解析エラー: {e}")
            return False

        return True

    def parse_log_entries(self):
        """ログエントリを解析してWake/Sleepイベントを抽出"""
        events = []

        # PowerChimeのWake/Sleepパターン
        wake_patterns = [
            r'did wake',
            r'didwake'
        ]

        sleep_patterns = [
            r'did sleep',
            r'didsleep'
        ]

        for entry in self.powerchime_entries:
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

                # Wakeイベントかチェック
                is_wake = any(re.search(pattern, message) for pattern in wake_patterns)
                # Sleepイベントかチェック
                is_sleep = any(re.search(pattern, message) for pattern in sleep_patterns)

                # 午前5時を1日の区切りとして日付を取得
                # 午前5時前は前日として扱う
                if timestamp.hour < 5:
                    date = timestamp.date() - timedelta(days=1)
                else:
                    date = timestamp.date()

                if is_wake:
                    events.append({
                        'date': date,
                        'time': timestamp.time(),
                        'timestamp': timestamp,
                        'event_type': 'wake',
                        'message': entry['message']
                    })
                elif is_sleep:
                    events.append({
                        'date': date,
                        'time': timestamp.time(),
                        'timestamp': timestamp,
                        'event_type': 'sleep',
                        'message': entry['message']
                    })

            except ValueError as e:
                print(f"タイムスタンプ解析エラー: {timestamp_str} - {e}")
                continue

        return events

    def aggregate_daily_times(self, events):
        """日毎の最初のWake時間と最後のSleep時間を集計（午前5時を1日の区切りとする）"""
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
                    'first_wake': None,
                    'last_sleep': None,
                    'wake_events': [],
                    'sleep_events': []
                }

            if event['event_type'] == 'wake':
                daily_data[date]['wake_events'].append(event['timestamp'])
                if daily_data[date]['first_wake'] is None:
                    daily_data[date]['first_wake'] = event['timestamp']
            else:  # sleep event
                daily_data[date]['sleep_events'].append(event['timestamp'])
                if daily_data[date]['last_sleep'] is None or event['timestamp'] > daily_data[date]['last_sleep']:
                    daily_data[date]['last_sleep'] = event['timestamp']

        # DataFrameに変換
        results = []
        for date, data in daily_data.items():
            results.append({
                'date': date,
                'first_wake_time': data['first_wake'].time() if data['first_wake'] else None,
                'last_sleep_time': data['last_sleep'].time() if data['last_sleep'] else None,
                'first_wake_datetime': data['first_wake'],
                'last_sleep_datetime': data['last_sleep'],
                'wake_count': len(data['wake_events']),
                'sleep_count': len(data['sleep_events'])
            })

        return pd.DataFrame(results).sort_values('date')

    def print_summary(self, df):
        """結果のサマリーを表示"""
        print("\n=== 日毎のWake/Sleep時間サマリー ===")
        print(f"分析期間: {df['date'].min()} から {df['date'].max()}")
        print(f"総日数: {len(df)} 日")

        print("\n日付\t\t最初のWake\t最後のSleep\tWake回数\tSleep回数")
        print("-" * 80)

        for _, row in df.iterrows():
            wake_time = row['first_wake_time'].strftime('%H:%M:%S') if row['first_wake_time'] else 'N/A'
            sleep_time = row['last_sleep_time'].strftime('%H:%M:%S') if row['last_sleep_time'] else 'N/A'
            print(f"{row['date']}\t{wake_time}\t\t{sleep_time}\t\t{row['wake_count']}\t\t{row['sleep_count']}")


@click.command()
@click.option('--days', '-d', default=7, help='分析する日数（デフォルト: 7日）')
@click.option('--output', '-o', default='powerchime_analysis.csv', help='出力CSVファイル名')
@click.option('--verbose', '-v', is_flag=True, help='詳細なログを表示')
def main(days, output, verbose):
    """PowerChimeログを解析して日毎のWake/Sleep時間を集計"""

    print(f"PowerChimeログ解析を開始します（過去{days}日分）")

    analyzer = PowerChimeLogAnalyzer()

    # ログを取得
    if not analyzer.get_powerchime_logs(days):
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


if __name__ == '__main__':
    main()

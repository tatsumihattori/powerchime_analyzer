#!/usr/bin/env python3
"""
PowerChime Log Analyzer

macOSのPowerChimeログを詳細に解析して、統計情報やグラフを生成します。
"""

import subprocess
import re
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import click
from pathlib import Path
import json
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict
import calendar

class PowerChimeAnalyzer:
    def __init__(self):
        self.powerchime_entries = []
        self.events = []

    def get_powerchime_logs(self, days_back=7):
        """指定された日数分のPowerChimeログを取得"""
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
                        'subsystem': entry.get('subsystem', ''),
                        'category': entry.get('category', ''),
                        'level': entry.get('level', '')
                    })

            print(f"取得したPowerChimeログエントリ数: {len(self.powerchime_entries)}")

        except Exception as e:
            print(f"PowerChimeログ取得エラー: {e}")
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

        # PowerChimeログを解析
        for entry in self.powerchime_entries:
            message = entry['message'].lower()
            timestamp_str = entry['timestamp']

            try:
                # タイムスタンプを解析
                if timestamp_str:
                    # タイムゾーン情報を標準形式に変換
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
                        'message': entry['message'],
                        'process': entry['process'],
                        'subsystem': entry['subsystem']
                    })
                elif is_sleep:
                    events.append({
                        'date': date,
                        'time': timestamp.time(),
                        'timestamp': timestamp,
                        'event_type': 'sleep',
                        'message': entry['message'],
                        'process': entry['process'],
                        'subsystem': entry['subsystem']
                    })

            except ValueError as e:
                print(f"PowerChimeタイムスタンプ解析エラー: {timestamp_str} - {e}")
                continue

        self.events = events
        return events

    def calculate_session_durations(self):
        """セッション時間を計算（午前5時を1日の区切りとする）"""
        sessions = []
        current_wake = None

        for event in sorted(self.events, key=lambda x: x['timestamp']):
            # PowerChimeのWake/Sleepセッション計算
            if event['event_type'] == 'wake':
                if current_wake is None:
                    current_wake = event['timestamp']
            elif event['event_type'] == 'sleep' and current_wake is not None:
                duration = event['timestamp'] - current_wake

                # 午前5時を1日の区切りとして日付を取得
                if event['timestamp'].hour < 5:
                    date = event['timestamp'].date() - timedelta(days=1)
                else:
                    date = event['timestamp'].date()

                sessions.append({
                    'start_time': current_wake,
                    'end_time': event['timestamp'],
                    'duration_minutes': duration.total_seconds() / 60,
                    'date': date
                })
                current_wake = None

        return sessions

    def generate_statistics(self, df, sessions):
        """統計情報を生成"""
        stats = {
            'total_days': len(df),
            'days_with_activity': len(df[df['wake_count'] > 0]),
            'total_sessions': len(sessions),
            'avg_sessions_per_day': len(sessions) / len(df) if len(df) > 0 else 0,
            'avg_session_duration': np.mean([s['duration_minutes'] for s in sessions]) if sessions else 0,
            'median_session_duration': np.median([s['duration_minutes'] for s in sessions]) if sessions else 0,
            'total_usage_hours': sum([s['duration_minutes'] for s in sessions]) / 60 if sessions else 0
        }

        # 時間帯別の統計
        hour_stats = defaultdict(int)
        for session in sessions:
            hour = session['start_time'].hour
            hour_stats[hour] += 1

        stats['peak_start_hour'] = max(hour_stats.items(), key=lambda x: x[1])[0] if hour_stats else 0

        return stats

    def create_visualizations(self, df, sessions, output_dir='.'):
        """グラフとチャートを生成"""
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)

        # スタイル設定
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")

        # 1. 日毎の使用時間
        if sessions:
            daily_usage = defaultdict(float)
            for session in sessions:
                daily_usage[session['date']] += session['duration_minutes']

            usage_df = pd.DataFrame([
                {'date': date, 'usage_hours': hours / 60}
                for date, hours in daily_usage.items()
            ])

            plt.figure(figsize=(12, 6))
            plt.bar(usage_df['date'], usage_df['usage_hours'])
            plt.title('日毎の使用時間')
            plt.xlabel('日付')
            plt.ylabel('使用時間（時間）')
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig(output_dir / 'daily_usage.png', dpi=300, bbox_inches='tight')
            plt.close()

        # 2. 時間帯別の開始回数
        if sessions:
            hour_counts = defaultdict(int)
            for session in sessions:
                hour = session['start_time'].hour
                hour_counts[hour] += 1

            hours = list(range(24))
            counts = [hour_counts[hour] for hour in hours]

            plt.figure(figsize=(12, 6))
            plt.bar(hours, counts)
            plt.title('時間帯別のセッション開始回数')
            plt.xlabel('時間')
            plt.ylabel('開始回数')
            plt.xticks(hours[::2])
            plt.tight_layout()
            plt.savefig(output_dir / 'hourly_sessions.png', dpi=300, bbox_inches='tight')
            plt.close()

        # 3. セッション時間の分布
        if sessions:
            durations = [s['duration_minutes'] for s in sessions]

            plt.figure(figsize=(10, 6))
            plt.hist(durations, bins=20, alpha=0.7, edgecolor='black')
            plt.title('セッション時間の分布')
            plt.xlabel('セッション時間（分）')
            plt.ylabel('頻度')
            plt.axvline(np.mean(durations), color='red', linestyle='--', label=f'平均: {np.mean(durations):.1f}分')
            plt.legend()
            plt.tight_layout()
            plt.savefig(output_dir / 'session_duration_distribution.png', dpi=300, bbox_inches='tight')
            plt.close()

        # 4. 週間パターン
        if sessions:
            weekday_counts = defaultdict(int)
            for session in sessions:
                weekday = session['start_time'].weekday()
                weekday_counts[weekday] += 1

            weekdays = ['月', '火', '水', '木', '金', '土', '日']
            counts = [weekday_counts[i] for i in range(7)]

            plt.figure(figsize=(10, 6))
            plt.bar(weekdays, counts)
            plt.title('曜日別のセッション開始回数')
            plt.xlabel('曜日')
            plt.ylabel('開始回数')
            plt.tight_layout()
            plt.savefig(output_dir / 'weekday_pattern.png', dpi=300, bbox_inches='tight')
            plt.close()

    def save_detailed_results(self, df, sessions, stats, output_file):
        """詳細な結果をCSVファイルに保存"""
        # 日毎の集計
        daily_summary = df.copy()

        # セッション情報を追加
        if sessions:
            session_df = pd.DataFrame(sessions)
            session_df['date'] = pd.to_datetime(session_df['date'])
            session_df = session_df.groupby('date').agg({
                'duration_minutes': ['count', 'mean', 'sum'],
                'start_time': 'min',
                'end_time': 'max'
            }).round(2)

            session_df.columns = ['session_count', 'avg_duration_min', 'total_duration_min', 'first_start', 'last_end']
            session_df = session_df.reset_index()

            # 日毎の集計と結合
            daily_summary['date'] = pd.to_datetime(daily_summary['date'])
            daily_summary = daily_summary.merge(session_df, on='date', how='left')

        daily_summary.to_csv(output_file, index=False, encoding='utf-8')
        print(f"詳細な結果を保存しました: {output_file}")

        # 統計情報をJSONで保存
        stats_file = output_file.replace('.csv', '_stats.json')
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, default=str)
        print(f"統計情報を保存しました: {stats_file}")

    def print_detailed_summary(self, df, sessions, stats):
        """詳細なサマリーを表示"""
        print("\n" + "="*60)
        print("詳細なPowerChimeログ解析結果")
        print("="*60)

        print(f"\n📊 基本統計:")
        print(f"  分析期間: {df['date'].min()} から {df['date'].max()}")
        print(f"  総日数: {stats['total_days']} 日")
        print(f"  アクティブ日数: {stats['days_with_activity']} 日")
        print(f"  総セッション数: {stats['total_sessions']} 回")
        print(f"  1日平均セッション数: {stats['avg_sessions_per_day']:.1f} 回")
        print(f"  平均セッション時間: {stats['avg_session_duration']:.1f} 分")
        print(f"  総使用時間: {stats['total_usage_hours']:.1f} 時間")
        print(f"  最も多い開始時間帯: {stats['peak_start_hour']}時")

        if sessions:
            print(f"\n⏰ セッション時間の統計:")
            durations = [s['duration_minutes'] for s in sessions]
            print(f"  最短セッション: {min(durations):.1f} 分")
            print(f"  最長セッション: {max(durations):.1f} 分")
            print(f"  中央値: {np.median(durations):.1f} 分")
            print(f"  標準偏差: {np.std(durations):.1f} 分")

        print(f"\n📅 日毎の詳細:")
        print("日付\t\t最初のWake\t最後のSleep\tWake回数\tSleep回数\tセッション数\t使用時間")
        print("-" * 100)

        for _, row in df.iterrows():
            start_time = row['first_start_time'].strftime('%H:%M:%S') if pd.notna(row['first_start_time']) else 'N/A'
            end_time = row['last_end_time'].strftime('%H:%M:%S') if pd.notna(row['last_end_time']) else 'N/A'
            wake_count = row.get('wake_count', 0) if pd.notna(row.get('wake_count')) else 0
            sleep_count = row.get('sleep_count', 0) if pd.notna(row.get('sleep_count')) else 0
            session_count = row.get('session_count', 0) if pd.notna(row.get('session_count')) else 0
            usage_hours = row.get('total_duration_min', 0) / 60 if pd.notna(row.get('total_duration_min')) else 0

            print(f"{row['date']}\t{start_time}\t\t{end_time}\t\t{wake_count}\t\t{sleep_count}\t\t{session_count}\t\t{usage_hours:.1f}h")

        # PowerChimeイベントの詳細表示
        if self.events:
            print(f"\n🔋 PowerChimeイベント詳細:")
            print("日付\t\t時間\t\tイベントタイプ\tメッセージ")
            print("-" * 100)
            for event in sorted(self.events, key=lambda x: x['timestamp'])[:20]:  # 最初の20件を表示
                print(f"{event['date']}\t{event['time']}\t{event['event_type']}\t\t{event['message'][:50]}...")


@click.command()
@click.option('--days', '-d', default=7, help='分析する日数（デフォルト: 7日）')
@click.option('--output', '-o', default='powerchime_analysis.csv', help='出力CSVファイル名')
@click.option('--output-dir', default='.', help='グラフ出力ディレクトリ')
@click.option('--verbose', '-v', is_flag=True, help='詳細なログを表示')
@click.option('--no-graphs', is_flag=True, help='グラフ生成をスキップ')
def main(days, output, output_dir, verbose, no_graphs):
    """高度なPowerChimeログ解析を実行"""

    print(f"高度なPowerChimeログ解析を開始します（過去{days}日分）")

    analyzer = PowerChimeAnalyzer()

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

    # セッション時間を計算
    sessions = analyzer.calculate_session_durations()
    print(f"検出されたセッション数: {len(sessions)}")

    # 日毎に集計
    daily_data = {}
    for event in events:
        date = event['date']
        if date not in daily_data:
            daily_data[date] = {
                'first_start': None,
                'last_end': None,
                'wake_events': [],
                'sleep_events': []
            }

        if event['event_type'] == 'wake':
            daily_data[date]['wake_events'].append(event['timestamp'])
            if daily_data[date]['first_start'] is None:
                daily_data[date]['first_start'] = event['timestamp']
        else:  # sleep event
            daily_data[date]['sleep_events'].append(event['timestamp'])
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
            'wake_count': len(data['wake_events']),
            'sleep_count': len(data['sleep_events'])
        })

    df = pd.DataFrame(results).sort_values('date')

    # 統計情報を生成
    stats = analyzer.generate_statistics(df, sessions)

    # 結果を表示
    analyzer.print_detailed_summary(df, sessions, stats)

    # 結果を保存
    analyzer.save_detailed_results(df, sessions, stats, output)

    # グラフを生成
    if not no_graphs:
        print(f"\n📈 グラフを生成中...")
        analyzer.create_visualizations(df, sessions, output_dir)
        print(f"グラフを保存しました: {output_dir}")


if __name__ == '__main__':
    main()

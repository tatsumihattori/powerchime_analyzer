#!/usr/bin/env python3
"""
PowerChime Log Analyzer Test Script

PowerChimeログ解析スクリプトの動作をテストします。
"""

import subprocess
import sys
import os
from pathlib import Path


def test_basic_analyzer():
    """基本的なPowerChimeログ解析スクリプトをテスト"""
    print("🧪 基本的なPowerChimeログ解析スクリプトをテスト中...")

    try:
        # 過去1日分のログでテスト
        result = subprocess.run([
            sys.executable, 'powerchime_analyzer.py',
            '--days', '1',
            '--output', 'test_basic_output.csv',
            '--verbose'
        ], capture_output=True, text=True, timeout=60)

        if result.returncode == 0:
            print("✅ 基本的なPowerChimeログ解析スクリプト: 成功")
            print(f"出力: {result.stdout}")
        else:
            print("❌ 基本的なPowerChimeログ解析スクリプト: 失敗")
            print(f"エラー: {result.stderr}")

    except subprocess.TimeoutExpired:
        print("⏰ 基本的なPowerChimeログ解析スクリプト: タイムアウト")
    except Exception as e:
        print(f"❌ 基本的なPowerChimeログ解析スクリプト: エラー - {e}")


def test_advanced_analyzer():
    """高度なPowerChimeログ解析スクリプトをテスト"""
    print("\n🧪 高度なPowerChimeログ解析スクリプトをテスト中...")

    try:
        # 過去1日分のログでテスト（グラフなし）
        result = subprocess.run([
            sys.executable, 'advanced_powerchime_analyzer.py',
            '--days', '1',
            '--output', 'test_advanced_output.csv',
            '--no-graphs',
            '--verbose'
        ], capture_output=True, text=True, timeout=60)

        if result.returncode == 0:
            print("✅ 高度なPowerChimeログ解析スクリプト: 成功")
            print(f"出力: {result.stdout}")
        else:
            print("❌ 高度なPowerChimeログ解析スクリプト: 失敗")
            print(f"エラー: {result.stderr}")

    except subprocess.TimeoutExpired:
        print("⏰ 高度なPowerChimeログ解析スクリプト: タイムアウト")
    except Exception as e:
        print(f"❌ 高度なPowerChimeログ解析スクリプト: エラー - {e}")


def test_log_access():
    """PowerChimeログアクセスをテスト"""
    print("\n🔋 PowerChimeログアクセスをテスト中...")

    try:
        # PowerChimeログが取得できるかテスト
        result = subprocess.run([
            'log', 'show',
            '--predicate', 'process == "PowerChime"',
            '--last', '1h',
            '--style', 'json'
        ], capture_output=True, text=True, timeout=30)

        if result.returncode == 0:
            print("✅ PowerChimeログアクセス: 成功")
            logs = result.stdout.strip()
            if logs and logs != '[]':
                print(f"  取得したログ数: {len(logs.split('}')) - 1}")
            else:
                print("  警告: ログが空です")
        else:
            print("❌ PowerChimeログアクセス: 失敗")
            print(f"エラー: {result.stderr}")

    except subprocess.TimeoutExpired:
        print("⏰ PowerChimeログアクセス: タイムアウト")
    except Exception as e:
        print(f"❌ PowerChimeログアクセス: エラー - {e}")


def test_wake_sleep_events():
    """Wake/Sleepイベントの検出をテスト"""
    print("\n🔋 Wake/Sleepイベントの検出をテスト中...")

    try:
        # 過去1時間のPowerChimeログからWake/Sleepイベントを検索
        result = subprocess.run([
            'log', 'show',
            '--predicate', 'process == "PowerChime"',
            '--last', '1h',
            '--style', 'json'
        ], capture_output=True, text=True, timeout=30)

        if result.returncode == 0:
            import json
            try:
                logs = json.loads(result.stdout)
                wake_count = 0
                sleep_count = 0

                for log in logs:
                    if 'eventMessage' in log:
                        message = log['eventMessage'].lower()
                        if 'did wake' in message:
                            wake_count += 1
                        elif 'did sleep' in message:
                            sleep_count += 1

                print(f"✅ Wake/Sleepイベント検出: 成功")
                print(f"  Wakeイベント: {wake_count}件")
                print(f"  Sleepイベント: {sleep_count}件")

            except json.JSONDecodeError:
                print("❌ Wake/Sleepイベント検出: JSON解析エラー")
        else:
            print("❌ Wake/Sleepイベント検出: ログ取得失敗")

    except Exception as e:
        print(f"❌ Wake/Sleepイベント検出: エラー - {e}")


def cleanup_test_files():
    """テストファイルをクリーンアップ"""
    print("\n🧹 テストファイルをクリーンアップ中...")

    test_files = [
        'test_basic_output.csv',
        'test_advanced_output.csv',
        'test_advanced_output_stats.json'
    ]

    for file in test_files:
        if os.path.exists(file):
            os.remove(file)
            print(f"  削除: {file}")
        else:
            print(f"  存在しない: {file}")

    # グラフファイルもクリーンアップ
    graph_files = [
        'daily_usage.png',
        'hourly_sessions.png',
        'session_duration_distribution.png',
        'weekday_pattern.png'
    ]

    for file in graph_files:
        if os.path.exists(file):
            os.remove(file)
            print(f"  削除: {file}")
        else:
            print(f"  存在しない: {file}")


def main():
    """メインテスト実行"""
    print("🔋 PowerChime Log Analyzer テスト開始")
    print("=" * 50)

    # ログアクセステスト
    test_log_access()

    # Wake/Sleepイベント検出テスト
    test_wake_sleep_events()

    # 基本的な解析スクリプトテスト
    test_basic_analyzer()

    # 高度な解析スクリプトテスト
    test_advanced_analyzer()

    # テストファイルクリーンアップ
    cleanup_test_files()

    print("\n" + "=" * 50)
    print("🔋 PowerChime Log Analyzer テスト完了")


if __name__ == '__main__':
    main()

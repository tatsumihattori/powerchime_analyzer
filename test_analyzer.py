#!/usr/bin/env python3
"""
Loginwindow Log Analyzer Test Script

ログ解析スクリプトの動作をテストします。
"""

import subprocess
import sys
import os
from pathlib import Path


def test_basic_analyzer():
    """基本的なログ解析スクリプトをテスト"""
    print("🧪 基本的なログ解析スクリプトをテスト中...")

    try:
        # 過去1日分のログでテスト
        result = subprocess.run([
            sys.executable, 'loginwindow_analyzer.py',
            '--days', '1',
            '--output', 'test_basic_output.csv',
            '--verbose'
        ], capture_output=True, text=True, timeout=60)

        if result.returncode == 0:
            print("✅ 基本的なログ解析スクリプト: 成功")
            print(f"出力: {result.stdout}")
        else:
            print("❌ 基本的なログ解析スクリプト: 失敗")
            print(f"エラー: {result.stderr}")

    except subprocess.TimeoutExpired:
        print("⏰ 基本的なログ解析スクリプト: タイムアウト")
    except Exception as e:
        print(f"❌ 基本的なログ解析スクリプト: エラー - {e}")


def test_advanced_analyzer():
    """高度なログ解析スクリプトをテスト"""
    print("\n🧪 高度なログ解析スクリプトをテスト中...")

    try:
        # 過去1日分のログでテスト（グラフなし）
        result = subprocess.run([
            sys.executable, 'advanced_loginwindow_analyzer.py',
            '--days', '1',
            '--output', 'test_advanced_output.csv',
            '--no-graphs',
            '--verbose'
        ], capture_output=True, text=True, timeout=60)

        if result.returncode == 0:
            print("✅ 高度なログ解析スクリプト: 成功")
            print(f"出力: {result.stdout}")
        else:
            print("❌ 高度なログ解析スクリプト: 失敗")
            print(f"エラー: {result.stderr}")

    except subprocess.TimeoutExpired:
        print("⏰ 高度なログ解析スクリプト: タイムアウト")
    except Exception as e:
        print(f"❌ 高度なログ解析スクリプト: エラー - {e}")


def test_log_access():
    """ログアクセスの権限をテスト"""
    print("\n🔍 ログアクセスの権限をテスト中...")

    try:
        # 基本的なログコマンドをテスト
        result = subprocess.run([
            'log', 'show',
            '--predicate', 'process == "loginwindow"',
            '--last', '1h',
            '--style', 'json'
        ], capture_output=True, text=True, timeout=30)

        if result.returncode == 0:
            print("✅ ログアクセス: 成功")
            logs = result.stdout.strip()
            if logs:
                print(f"取得したログ数: {len(logs.splitlines())}")
            else:
                print("⚠️  ログが空です（過去1時間にloginwindowログがない可能性）")
        else:
            print("❌ ログアクセス: 失敗")
            print(f"エラー: {result.stderr}")
            print("💡 管理者権限で実行してみてください: sudo python test_analyzer.py")

    except subprocess.TimeoutExpired:
        print("⏰ ログアクセス: タイムアウト")
    except FileNotFoundError:
        print("❌ ログアクセス: 'log'コマンドが見つかりません（macOSが必要です）")
    except Exception as e:
        print(f"❌ ログアクセス: エラー - {e}")


def cleanup_test_files():
    """テストファイルをクリーンアップ"""
    print("\n🧹 テストファイルをクリーンアップ中...")

    test_files = [
        'test_basic_output.csv',
        'test_advanced_output.csv',
        'test_advanced_output_stats.json'
    ]

    for file_path in test_files:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"削除: {file_path}")


def main():
    """メインのテスト関数"""
    print("Loginwindow Log Analyzer テスト開始")
    print("=" * 50)

    # スクリプトファイルの存在確認
    required_files = ['loginwindow_analyzer.py', 'advanced_loginwindow_analyzer.py']
    for file_path in required_files:
        if not os.path.exists(file_path):
            print(f"❌ 必要なファイルが見つかりません: {file_path}")
            return

    # ログアクセステスト
    test_log_access()

    # 基本的なログ解析テスト
    test_basic_analyzer()

    # 高度なログ解析テスト
    test_advanced_analyzer()

    # クリーンアップ
    cleanup_test_files()

    print("\n" + "=" * 50)
    print("テスト完了")


if __name__ == '__main__':
    main()

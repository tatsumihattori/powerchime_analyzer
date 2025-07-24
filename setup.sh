#!/bin/bash

# PowerChime Log Analyzer Setup Script
# macOSのPowerChimeログを解析するためのセットアップスクリプト

set -e

# 色付きの出力関数
print_info() {
    echo -e "\033[1;34mℹ️  $1\033[0m"
}

print_success() {
    echo -e "\033[1;32m✅ $1\033[0m"
}

print_warning() {
    echo -e "\033[1;33m⚠️  $1\033[0m"
}

print_error() {
    echo -e "\033[1;31m❌ $1\033[0m"
}

# 前提条件チェック
check_prerequisites() {
    print_info "前提条件をチェック中..."

    # macOSチェック
    if [[ "$OSTYPE" != "darwin"* ]]; then
        print_error "このスクリプトはmacOSでのみ動作します"
        exit 1
    fi

    # Pythonチェック
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3が必要です"
        exit 1
    fi

    # Ryeチェック
    if ! command -v rye &> /dev/null; then
        print_warning "Ryeがインストールされていません"
        print_info "Ryeをインストールしてください: https://rye-up.com/"
        exit 1
    fi

    # logコマンドチェック
    if ! command -v log &> /dev/null; then
        print_error "logコマンドが見つかりません（macOSのシステムログツール）"
        exit 1
    fi

    print_success "前提条件チェック完了"
}

# 依存関係のインストール
install_dependencies() {
    print_info "依存関係をインストール中..."

    if [ -f "pyproject.toml" ]; then
        rye sync
        print_success "依存関係をインストールしました"
    else
        print_warning "pyproject.tomlが見つかりません"
        print_info "手動で依存関係をインストールしてください:"
        echo "  pip install pandas click matplotlib seaborn numpy"
    fi
}

# 実行権限の設定
set_permissions() {
    print_info "スクリプトの実行権限を設定中..."

    chmod +x loginwindow_analyzer.py
    chmod +x advanced_loginwindow_analyzer.py
    chmod +x test_analyzer.py

    print_success "実行権限を設定しました"
}

# PowerChimeログアクセステスト
test_log_access() {
    print_info "PowerChimeログアクセスをテスト中..."

    if log show --predicate 'process == "PowerChime"' --last 1h --style json &> /dev/null; then
        print_success "PowerChimeログアクセス: 成功"
    else
        print_warning "PowerChimeログアクセス: 失敗"
        print_info "管理者権限が必要な場合があります"
        print_info "sudo python loginwindow_analyzer.py で実行してみてください"
    fi
}

# 使用例の表示
show_usage_examples() {
    echo ""
    echo "📖 使用例:"
    echo "=========="
    echo ""
    echo "基本的な解析（過去7日分）:"
    echo "  python loginwindow_analyzer.py"
    echo ""
    echo "過去30日分の詳細解析:"
    echo "  python advanced_loginwindow_analyzer.py --days 30"
    echo ""
    echo "結果を別のファイルに保存:"
    echo "  python loginwindow_analyzer.py --output my_analysis.csv"
    echo ""
    echo "詳細なログを表示:"
    echo "  python loginwindow_analyzer.py --verbose"
    echo ""
    echo "グラフなしで解析:"
    echo "  python advanced_loginwindow_analyzer.py --no-graphs"
    echo ""
    echo "テスト実行:"
    echo "  python test_analyzer.py"
    echo ""
}

# メイン処理
main() {
    check_prerequisites
    install_dependencies
    set_permissions
    test_log_access
    show_usage_examples

    echo ""
    print_success "セットアップ完了！"
    echo ""
    print_info "最初のテストを実行するには:"
    echo "  python test_analyzer.py"
    echo ""
}

# スクリプト実行
main "$@"

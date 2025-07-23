#!/bin/bash

# Loginwindow Log Analyzer Setup Script

set -e

echo "🚀 Loginwindow Log Analyzer セットアップ開始"
echo "=========================================="

# 色付きの出力関数
print_success() {
    echo -e "\033[32m✅ $1\033[0m"
}

print_error() {
    echo -e "\033[31m❌ $1\033[0m"
}

print_info() {
    echo -e "\033[34mℹ️  $1\033[0m"
}

print_warning() {
    echo -e "\033[33m⚠️  $1\033[0m"
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
        print_error "Python3がインストールされていません"
        exit 1
    fi

    # Ryeチェック
    if ! command -v rye &> /dev/null; then
        print_warning "Ryeがインストールされていません"
        print_info "Ryeをインストールしてください: https://rye-up.com/"
        exit 1
    fi

    # Voltaチェック
    if ! command -v volta &> /dev/null; then
        print_warning "Voltaがインストールされていません"
        print_info "Voltaをインストールしてください: https://volta.sh/"
    fi

    print_success "前提条件チェック完了"
}

# 依存関係のインストール
install_dependencies() {
    print_info "依存関係をインストール中..."

    if [ -f "pyproject.toml" ]; then
        rye sync
        print_success "Python依存関係をインストールしました"
    else
        print_error "pyproject.tomlが見つかりません"
        exit 1
    fi
}

# スクリプトの実行権限を設定
set_permissions() {
    print_info "スクリプトの実行権限を設定中..."

    chmod +x loginwindow_analyzer.py
    chmod +x advanced_loginwindow_analyzer.py
    chmod +x test_analyzer.py

    print_success "実行権限を設定しました"
}

# ログアクセステスト
test_log_access() {
    print_info "ログアクセスをテスト中..."

    if log show --predicate 'process == "loginwindow"' --last 1h --style json &> /dev/null; then
        print_success "ログアクセス: 成功"
    else
        print_warning "ログアクセス: 失敗"
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

# CodexCLI - AI-Powered Coding Assistant

OpenAI Codex CLIのクローン実装。ターミナルから直接AIコーディングアシスタントを使用できます。

## 概要

CodexCLIは、OpenAI GPTやAnthropic Claudeを使用して、コードの生成、ファイルの編集、シェルコマンドの実行を支援するAIコーディングアシスタントです。

### 主な機能

- **AIコーディングアシスタント**: 自然言語でコード生成・編集を依頼
- **ファイル操作**: ファイルの作成、読み取り、編集、削除
- **シェルコマンド実行**: ターミナルコマンドの実行
- **対話型セッション**: 会話履歴を保持したマルチターン対話
- **複数の承認モード**: 操作の承認レベルをカスタマイズ可能
- **複数のLLMプロバイダー対応**: OpenAI / Anthropic Claude

## インストール

### 前提条件

- Python 3.8以上
- OpenAI APIキーまたはAnthropic APIキー
- uv CLI（未導入の場合は以下のコマンドでインストール）

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Windows PowerShellの場合:

```powershell
irm https://astral.sh/uv/install.ps1 | iex
```

### インストール手順

```bash
# リポジトリをクローン
git clone https://github.com/yourusername/CodexClone.git
cd CodexClone

# 依存関係をインストール
uv sync

# または開発用依存関係も含めて
uv sync --extra dev
```

### 環境設定

`.env`ファイルを作成してAPIキーを設定:

```bash
cp .env.example .env
```

`.env`ファイルを編集:

```env
# OpenAI API設定
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4

# Anthropic Claude API設定（代替）
ANTHROPIC_API_KEY=your_anthropic_api_key_here
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022

# デフォルトのLLMプロバイダー（openai or anthropic）
DEFAULT_PROVIDER=openai

# CLI設定
DEFAULT_APPROVAL_MODE=suggest
```

## 使い方

### インタラクティブモード

```bash
kuudex
```

または特定のプロバイダーを指定:

```bash
kuudex --provider openai
kuudex --provider anthropic
```

承認モードを指定:

```bash
kuudex --mode suggest    # すべての操作で確認（デフォルト）
kuudex --mode auto       # ファイル操作は自動、コマンドは確認
kuudex --mode full       # すべて自動実行（注意！）
```

### ワンショットモード

単一のコマンドを実行:

```bash
kuudex ask "Create a Python script that sorts a list"
kuudex ask "Read main.py and explain what it does"
```

### インタラクティブコマンド

対話モード内で使用できるコマンド:

- `exit`, `quit`, `q` - プログラムを終了
- `help` - ヘルプを表示
- `clear` - 会話履歴をクリア
- `mode` - 現在の承認モードを表示
- `mode <mode>` - 承認モードを変更
- `tree` - プロジェクトのファイルツリーを表示

### CLIコマンド

```bash
# プロジェクトのファイルツリーを表示
kuudex tree

# 会話履歴をクリア
kuudex clear

# セッション情報を表示
kuudex info
```

## 承認モード

### Suggestモード（デフォルト）

すべての操作で確認を求めます:
- ファイルの作成
- ファイルの編集
- ファイルの削除
- シェルコマンドの実行
- API呼び出し

### Auto Editモード

ファイル操作は自動承認、危険な操作のみ確認:
- ファイル作成・編集: 自動承認
- ファイル削除: 確認が必要
- シェルコマンド: 確認が必要

### Full Autoモード

すべての操作を自動実行:
- すべてのファイル操作: 自動承認
- すべてのシェルコマンド: 自動承認

**警告**: Full Autoモードは注意して使用してください！

## 使用例

### ファイルの作成

```
>>> Create a Python file that implements a binary search algorithm
```

### コードの編集

```
>>> Read utils.py and add type hints to all functions
```

### コードの説明

```
>>> Explain what the main function does in app.py
```

### リファクタリング

```
>>> Refactor database.py to use async/await instead of callbacks
```

### テストの実行

```
>>> Run the unit tests and fix any failures
```

### プロジェクト構造の確認

```
>>> Show me the project structure
```

または:

```
>>> tree
```

## アーキテクチャ

```
src/codexcli/
├── cli.py          # CLIメインエントリーポイント
├── agent.py        # AIエージェントとLLM統合
├── file_ops.py     # ファイル操作（読み取り/編集/作成）
├── shell.py        # シェルコマンド実行
├── approval.py     # 承認フローとモード管理
├── context.py      # コンテキストと履歴管理
└── utils.py        # ユーティリティ関数
```

## セキュリティとプライバシー

- **ローカル実行**: すべての操作はローカル環境で実行されます
- **コードの送信**: ユーザーのプロンプトと高レベルのコンテキストのみがLLM APIに送信されます
- **承認フロー**: 各操作前に確認を求めることができます（Suggestモード）
- **履歴管理**: 会話履歴はローカルに保存されます（`~/.codexcli/`）

## トラブルシューティング

### APIキーエラー

```
ValueError: OPENAI_API_KEY not set
```

`.env`ファイルにAPIキーが設定されているか確認してください。

### モジュールが見つからない

```
ImportError: No module named 'openai'
```

依存関係を再インストール:

```bash
uv sync
```

### パーミッションエラー

ファイル操作やシェルコマンドで権限エラーが発生する場合、適切な権限があるか確認してください。

## 開発

### テストの実行

```bash
uv run pytest
```

### コードフォーマット

```bash
uv run black src/
```

### 型チェック

```bash
uv run mypy src/
```

## ライセンス

MIT License - 詳細は[LICENSE](LICENSE)ファイルを参照してください。

## 貢献

プルリクエストを歓迎します！大きな変更の場合は、まずissueを開いて変更内容を議論してください。

## 免責事項

このプロジェクトはOpenAI Codex CLIのクローン実装です。OpenAI Inc.とは関係ありません。

## 参考リンク

- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Anthropic Claude API Documentation](https://docs.anthropic.com/)
- [Click Documentation](https://click.palletsprojects.com/)
- [Rich Documentation](https://rich.readthedocs.io/)

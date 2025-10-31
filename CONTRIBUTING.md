# Contributing to CodexCLI

CodexCLIへの貢献をありがとうございます！このガイドでは、プロジェクトへの貢献方法を説明します。

## 開発環境のセットアップ

1. リポジトリをフォーク
2. クローン

```bash
git clone https://github.com/yourusername/CodexClone.git
cd CodexClone
```

3. 開発用依存関係をインストール

```bash
uv sync --extra dev
```

4. 環境変数を設定

```bash
cp .env.example .env
# .envファイルを編集してAPIキーを設定
```

## コーディング規約

- **スタイル**: PEP 8に従う
- **フォーマット**: Blackを使用
- **型ヒント**: 可能な限り型ヒントを使用
- **ドキュメント**: すべての公開関数とクラスにdocstringを記述

### コードフォーマット

```bash
uv run black src/
```

### 型チェック

```bash
uv run mypy src/
```

### Linting

```bash
uv run flake8 src/
```

## テスト

新機能やバグ修正には必ずテストを追加してください。

### テストの実行

```bash
# すべてのテストを実行
uv run pytest

# カバレッジレポート付き
uv run pytest --cov=codexcli --cov-report=html

# 特定のテストファイルのみ
uv run pytest tests/test_approval.py
```

## プルリクエスト

1. 新しいブランチを作成

```bash
git checkout -b feature/your-feature-name
```

2. 変更をコミット

```bash
git add .
git commit -m "Add: your feature description"
```

コミットメッセージの形式:
- `Add:` 新機能追加
- `Fix:` バグ修正
- `Update:` 既存機能の更新
- `Docs:` ドキュメントのみの変更
- `Test:` テストの追加・修正
- `Refactor:` リファクタリング

3. プッシュ

```bash
git push origin feature/your-feature-name
```

4. GitHubでプルリクエストを作成

## バグレポート

バグを見つけた場合は、以下の情報を含めてissueを作成してください:

- バグの説明
- 再現手順
- 期待される動作
- 実際の動作
- 環境情報（OS、Pythonバージョンなど）
- エラーメッセージ（あれば）

## 機能リクエスト

新機能のアイデアがある場合は、以下を含めてissueを作成してください:

- 機能の説明
- ユースケース
- 実装案（あれば）

## 質問

質問がある場合は、Discussionsセクションで質問してください。

## ライセンス

貢献したコードはMITライセンスの下で公開されます。

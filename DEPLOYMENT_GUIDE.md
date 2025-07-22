# YouTube Transcript Extractor - デプロイメントガイド

## 🚀 GitHubへの公開手順

### 1. GitHubリポジトリの作成

1. [GitHub](https://github.com)にログイン
2. 右上の「+」→「New repository」をクリック
3. リポジトリ設定:
   - **Repository name**: `youtube-transcript-extractor`
   - **Description**: `YouTube動画から文字起こしを確実に取得するPythonライブラリ`
   - **Public** を選択（オープンソースとして公開）
   - **Add a README file** のチェックを外す（既に存在するため）
   - **Add .gitignore** のチェックを外す（既に存在するため）
   - **Choose a license** のチェックを外す（既に存在するため）

### 2. ローカルリポジトリとの接続

```bash
# リモートリポジトリを追加
git remote add origin https://github.com/YOUR_USERNAME/youtube-transcript-extractor.git

# 初回プッシュ
git push -u origin main
```

### 3. GitHub設定の最適化

#### リポジトリ設定
- **Settings** → **General**:
  - Features: Issues, Wiki, Discussions を有効化
  - Pull Requests: Allow merge commits, Allow squash merging を有効化

#### ブランチ保護
- **Settings** → **Branches**:
  - Branch protection rule for `main`:
    - Require pull request reviews before merging
    - Require status checks to pass before merging

#### Topics（タグ）の設定
```
youtube, transcript, subtitles, captions, speech-to-text, 
video-processing, nlp, text-extraction, python, api
```

## 📦 PyPI公開手順

### 1. PyPI アカウント準備

1. [PyPI](https://pypi.org)でアカウント作成
2. [TestPyPI](https://test.pypi.org)でテストアカウント作成
3. API トークンを生成

### 2. パッケージビルド

```bash
# ビルドツールのインストール
pip install build twine

# パッケージビルド
python -m build

# 生成されたファイルを確認
ls dist/
# youtube_transcript_extractor-1.0.0-py3-none-any.whl
# youtube_transcript_extractor-1.0.0.tar.gz
```

### 3. TestPyPIでテスト

```bash
# TestPyPIにアップロード
python -m twine upload --repository testpypi dist/*

# TestPyPIからインストールテスト
pip install --index-url https://test.pypi.org/simple/ youtube-transcript-extractor
```

### 4. 本番PyPIに公開

```bash
# 本番PyPIにアップロード
python -m twine upload dist/*
```

## 🔧 継続的インテグレーション（CI/CD）

### GitHub Actions設定

`.github/workflows/ci.yml`:

```yaml
name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        python-version: [3.8, 3.9, '3.10', 3.11]

    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements-dev.txt
    
    - name: Run tests
      run: |
        python -m pytest tests/ -v --cov=youtube_transcript_extractor
    
    - name: Run linting
      run: |
        flake8 src/youtube_transcript_extractor/
        black --check src/youtube_transcript_extractor/
    
    - name: Type checking
      run: |
        mypy src/youtube_transcript_extractor/

  publish:
    needs: test
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && startsWith(github.ref, 'refs/tags/')
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: 3.11
    
    - name: Build package
      run: |
        pip install build
        python -m build
    
    - name: Publish to PyPI
      uses: pypa/gh-action-pypi-publish@release/v1
      with:
        password: ${{ secrets.PYPI_API_TOKEN }}
```

## 📚 ドキュメント公開

### GitHub Pages設定

1. **Settings** → **Pages**:
   - Source: Deploy from a branch
   - Branch: `main`
   - Folder: `/docs`

### Sphinx ドキュメント（オプション）

```bash
# Sphinxセットアップ
cd docs/
sphinx-quickstart

# 設定ファイル編集
# conf.py に以下を追加:
import os
import sys
sys.path.insert(0, os.path.abspath('../src'))

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon'
]

# ドキュメントビルド
make html
```

## 🏷️ バージョン管理戦略

### セマンティックバージョニング

- **MAJOR**: 破壊的変更
- **MINOR**: 後方互換性のある機能追加
- **PATCH**: 後方互換性のあるバグ修正

### リリースプロセス

```bash
# バージョンアップ
# setup.py, __init__.py のバージョンを更新

# タグ作成
git tag v1.0.1
git push origin v1.0.1

# GitHub Releases で詳細なリリースノートを作成
```

## 🔒 セキュリティ設定

### Dependabot設定

`.github/dependabot.yml`:

```yaml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10
```

### セキュリティポリシー

`SECURITY.md`:

```markdown
# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Reporting a Vulnerability

Please report security vulnerabilities to security@example.com
```

## 📊 プロジェクト管理

### Issue テンプレート

`.github/ISSUE_TEMPLATE/bug_report.md`:

```markdown
---
name: Bug report
about: Create a report to help us improve
title: ''
labels: bug
assignees: ''
---

**Describe the bug**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**Expected behavior**
A clear and concise description of what you expected to happen.

**Environment:**
 - OS: [e.g. macOS, Windows, Linux]
 - Python version: [e.g. 3.9]
 - Package version: [e.g. 1.0.0]

**Additional context**
Add any other context about the problem here.
```

### Pull Request テンプレート

`.github/pull_request_template.md`:

```markdown
## Description

Brief description of changes

## Type of Change

- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing

- [ ] Tests pass locally
- [ ] New tests added for new functionality
- [ ] Manual testing completed

## Checklist

- [ ] Code follows the project's style guidelines
- [ ] Self-review of code completed
- [ ] Documentation updated if needed
- [ ] No new warnings introduced
```

## 🌟 コミュニティ構築

### Contributing ガイド

`CONTRIBUTING.md`:

```markdown
# Contributing to YouTube Transcript Extractor

## Development Setup

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/youtube-transcript-extractor.git`
3. Create a virtual environment: `python -m venv venv`
4. Activate it: `source venv/bin/activate` (Linux/Mac) or `venv\Scripts\activate` (Windows)
5. Install dependencies: `pip install -r requirements-dev.txt`

## Code Style

- Use Black for formatting: `black src/`
- Use flake8 for linting: `flake8 src/`
- Use mypy for type checking: `mypy src/`

## Testing

- Run tests: `python -m pytest`
- Run with coverage: `python -m pytest --cov=youtube_transcript_extractor`

## Submitting Changes

1. Create a feature branch: `git checkout -b feature/amazing-feature`
2. Make your changes
3. Add tests for new functionality
4. Ensure all tests pass
5. Commit your changes: `git commit -m 'Add amazing feature'`
6. Push to your fork: `git push origin feature/amazing-feature`
7. Create a Pull Request
```

## 📈 成功指標

### 追跡すべきメトリクス

- **GitHub Stars**: プロジェクトの人気度
- **Forks**: 開発者の関心度
- **Issues/PRs**: コミュニティの活発度
- **PyPI Downloads**: 実際の利用度
- **Documentation Views**: ドキュメントの有用性

### 成長戦略

1. **技術ブログ記事**: 実装の詳細や使用例を紹介
2. **カンファレンス発表**: PyCon、技術勉強会での発表
3. **SNS活用**: Twitter、LinkedIn での情報発信
4. **コミュニティ参加**: Reddit、Stack Overflow での回答
5. **パートナーシップ**: 関連プロジェクトとの連携

---

このガイドに従って、YouTube Transcript Extractorを成功するオープンソースプロジェクトとして育てていきましょう！


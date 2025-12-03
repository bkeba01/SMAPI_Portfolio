# 在庫管理システム(ポートフォリオ版)

Flask + SQLAlchemyを使用した在庫・販売管理システムのポートフォリオ版です。

## デモ動画(54秒) 

いくつかの機能の操作を行ったデモ動画です。ファイルサイズの関係上、再生速度を調整しています。

[https://github.com/user-attachments/assets/5c6e13d0-60e7-4cec-a735-4777784ab5fd](https://github.com/user-attachments/assets/ff419dd6-7fdd-405a-aad5-048e803834aa)

## 概要

このアプリケーションは、商品の在庫管理、販売記録、顧客情報、注文管理などを行うことができるWebアプリケーションです。

## 主な機能

- 商品マスタ管理
- 在庫情報の管理
- 販売記録の管理
- 顧客情報の管理
- 注文情報の管理
- データの検索・フィルタリング
- 販売された商品の在庫数更新
- 販売されたセット商品の子商品のみ在庫数更新
- 商品の出荷管理
- 商品の納品管理

## 技術スタック

- **バックエンド**: Flask 3.1.0
- **データベース**: SQLite (ポートフォリオ版) / Oracle Database (本番環境用)
- **ORM**: SQLAlchemy 2.0
- **フォーム処理**: WTForms
- **キャッシュ**: Flask-Caching

## セットアップ手順

### 1. リポジトリのクローン

```bash
git clone <repository-url>
cd SMAPI_Portfolio
```

### 2. 仮想環境の作成と有効化

**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

### 4. 環境変数の設定

`.env.example`をコピーして`.env`ファイルを作成します:

```bash
# Windows
copy .env.example .env

# macOS/Linux
cp .env.example .env
```

`.env`ファイルの内容（デフォルトはSQLiteを使用）:
```
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///local_market.db
CACHE_TYPE=SimpleCache
FLASK_ENV=development
FLASK_DEBUG=True
```

### 5. データベースの初期化とダミーデータの投入

```bash
python seed.py
```

このコマンドで以下が実行されます:
- データベーステーブルの作成
- サンプルデータの投入（商品、顧客、販売記録など）

### 6. アプリケーションの起動

```bash
python app.py
```

ブラウザで `http://localhost:5000` にアクセスしてください。

### 注意事項
 - この在庫管理システムは、ポートフォリオ版なため実際のデータベースを利用していません。ローカルデータベースを利用して、動作します。ご了承ください。
 - ネットワーク内での実装想定です。

## プロジェクト構造

```
SMAPI_Portfolio/
├── app.py              # アプリケーションのエントリーポイント
├── __init__.py         # Flaskアプリケーションの初期化
├── config.py           # 設定ファイル（環境別設定）
├── models.py           # データベースモデル定義
├── routes.py           # ルーティング定義
├── forms.py            # フォーム定義（WTForms）
├── utils.py            # ユーティリティ関数
├── seed.py             # ダミーデータ投入スクリプト
├── requirements.txt    # 依存パッケージリスト
├── .env.example        # 環境変数のテンプレート
├── .gitignore          # Git除外ファイル設定
├── templates/          # HTMLテンプレート
└── static/            # 静的ファイル（CSS、画像など）
```

## データベース構成

### 主要テーブル

- **商品 (Goods)**: 商品マスタ情報
- **入荷情報 (Arrival)**: 商品の入荷履歴
- **販売記録 (SalesRecord)**: 販売トランザクション
- **顧客情報 (CustomerInfo)**: 顧客マスタ
- **COLOR**: カラーマスタ
- **注文商品 (OrderGoods)**: 発注情報
- **セット商品 (SetGoods)**: セット商品情報
- **振込み先 (BankAccount)**: 銀行口座情報
- **郵送方法 (Freight)**: 配送方法マスタ

## 環境設定

### ポートフォリオ版（デフォルト）

```python
# デフォルトでSQLiteを使用
DATABASE_URL=sqlite:///local_market.db
```

### 本番環境（Oracle Database）

```python
# Oracle Databaseを使用する場合
DATABASE_URL=oracle+cx_oracle://username:password@host:port/?service_name=service_name
```

環境変数 `FLASK_CONFIG` で設定を切り替えることもできます:
- `portfolio`: ポートフォリオ用（SQLite、デフォルト）
- `development`: 開発環境用
- `production`: 本番環境用

```bash
# 本番環境として起動する場合
export FLASK_CONFIG=production  # macOS/Linux
set FLASK_CONFIG=production     # Windows
```

## 注意事項

### セキュリティ

- `.env`ファイルは**絶対にGitにコミットしないでください**
- 本番環境では必ず強力な`SECRET_KEY`を設定してください
- ポートフォリオ版のダミーデータは公開しても問題ない内容にしてあります

### データベースファイル

- SQLiteのデータベースファイル(`local_market.db`)もGitリポジトリに含めないようにしてください
- `.gitignore`に設定済みです

## トラブルシューティング

### データベース接続エラー

SQLiteを使用している場合、データベースファイルが存在しない場合は自動的に作成されます。`seed.py`を実行してテーブルとデータを初期化してください。

### 依存パッケージのエラー

特定のパッケージでエラーが発生する場合:
```bash
pip install --upgrade pip
pip install -r requirements.txt --upgrade
```

### Oracle Database接続（本番環境のみ）

Oracle Databaseを使用する場合は、Oracle Instant Clientのインストールが必要です:
- [Oracle Instant Clientダウンロード](https://www.oracle.com/database/technologies/instant-client/downloads.html)

## ライセンス

このプロジェクトはポートフォリオ用のサンプルアプリケーションです。

## 作成者

bkeba01

## 更新履歴

- 2024-12: ポートフォリオ版を作成
  - SQLite対応
  - 環境変数による設定管理
  - ダミーデータ生成機能

---

**Note**: このアプリケーションはポートフォリオ・デモ用です。本番環境で使用する場合は、適切なセキュリティ対策とテストを実施してください。

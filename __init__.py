from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_caching import Cache
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
import os

# 設定をインポート
from config import config

app = Flask(__name__)

# 環境変数からconfig名を取得（デフォルトは'portfolio'）
config_name = os.environ.get('FLASK_CONFIG') or 'portfolio'
app.config.from_object(config[config_name])

# データベースとキャッシュの初期化
db = SQLAlchemy(app)
cache = Cache(app)
migrate = Migrate(app, db)

# SQLAlchemyエンジンの作成
engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])

# SQLiteを使用する場合はスキーマ指定なし、Oracleの場合はJTスキーマ
is_sqlite = 'sqlite' in app.config['SQLALCHEMY_DATABASE_URI']
metadata = MetaData(schema=None if is_sqlite else "JT")

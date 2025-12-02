import os
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む
load_dotenv()

class Config:
    """アプリケーション設定クラス"""

    # Flask基本設定
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

    # データベース設定
    # 環境変数DATABASE_URLが設定されていればそれを使用、なければSQLiteをデフォルトに
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///local_market.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # キャッシュ設定
    CACHE_TYPE = os.environ.get('CACHE_TYPE') or 'SimpleCache'

    # Flask環境設定
    DEBUG = os.environ.get('FLASK_DEBUG', 'True') == 'True'

class DevelopmentConfig(Config):
    """開発環境用の設定"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///local_market.db'

class ProductionConfig(Config):
    """本番環境用の設定"""
    DEBUG = False
    # 本番環境では必ず環境変数から読み込む
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SECRET_KEY = os.environ.get('SECRET_KEY')  # 本番では必須

class PortfolioConfig(Config):
    """ポートフォリオ用の設定（公開用）"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///local_market.db'
    SECRET_KEY = 'portfolio-demo-key-not-for-production'

# 環境に応じた設定を選択
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'portfolio': PortfolioConfig,
    'default': DevelopmentConfig
}

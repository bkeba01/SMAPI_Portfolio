from __init__ import app
# 変更点1: routesモジュールをここでインポートするように変更
# __init__.pyでの循環参照によるルートの二重登録を防ぐため
import routes

#__init__が呼ばれると、そのファイルは実行される。
#特殊な名前付けなため

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
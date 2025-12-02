"""
データベースにダミーデータを投入するスクリプト
ポートフォリオ用のサンプルデータを生成します
"""
from datetime import datetime, date, timedelta
from __init__ import app, db
from models import (
    Goods, Arrival, SalesRecord, Color, CustomerInfo,
    SetGoods, OrderGoods, BankAccount, Freight
)

def clear_all_data():
    """既存のデータをすべて削除"""
    print("既存データを削除中...")
    try:
        db.session.query(SalesRecord).delete()
        db.session.query(OrderGoods).delete()
        db.session.query(SetGoods).delete()
        db.session.query(Arrival).delete()
        db.session.query(Goods).delete()
        db.session.query(Color).delete()
        db.session.query(CustomerInfo).delete()
        db.session.query(BankAccount).delete()
        db.session.query(Freight).delete()
        db.session.commit()
        print("既存データの削除が完了しました")
    except Exception as e:
        db.session.rollback()
        print(f"エラー: {e}")

def seed_colors():
    """カラーマスタにデータを投入"""
    print("カラーデータを投入中...")
    colors = [
        Color(colorid='001', colornm='レッド', fentdt='2024-01-01 00:00:00', fentusr='system', fupdtedt='2024-01-01 00:00:00', fupdteusr='system', fupdteprg='seed.py'),
        Color(colorid='002', colornm='ブルー', fentdt='2024-01-01 00:00:00', fentusr='system', fupdtedt='2024-01-01 00:00:00', fupdteusr='system', fupdteprg='seed.py'),
        Color(colorid='003', colornm='グリーン', fentdt='2024-01-01 00:00:00', fentusr='system', fupdtedt='2024-01-01 00:00:00', fupdteusr='system', fupdteprg='seed.py'),
        Color(colorid='004', colornm='イエロー', fentdt='2024-01-01 00:00:00', fentusr='system', fupdtedt='2024-01-01 00:00:00', fupdteusr='system', fupdteprg='seed.py'),
        Color(colorid='005', colornm='ブラック', fentdt='2024-01-01 00:00:00', fentusr='system', fupdtedt='2024-01-01 00:00:00', fupdteusr='system', fupdteprg='seed.py'),
        Color(colorid='006', colornm='ホワイト', fentdt='2024-01-01 00:00:00', fentusr='system', fupdtedt='2024-01-01 00:00:00', fupdteusr='system', fupdteprg='seed.py'),
    ]
    db.session.bulk_save_objects(colors)
    db.session.commit()
    print(f"{len(colors)}件のカラーデータを投入しました")

def seed_bank_accounts():
    """銀行口座マスタにデータを投入"""
    print("銀行口座データを投入中...")
    banks = [
        BankAccount(bankid='BANK001', banknm='みずほ銀行', fee=330, remark='振込手数料', fentdt='2024-01-01 00:00:00', fentusr='system', fupdtedt='2024-01-01 00:00:00', fupdteusr='system', fupdteprg='seed.py'),
        BankAccount(bankid='BANK002', banknm='三菱UFJ銀行', fee=330, remark='振込手数料', fentdt='2024-01-01 00:00:00', fentusr='system', fupdtedt='2024-01-01 00:00:00', fupdteusr='system', fupdteprg='seed.py'),
        BankAccount(bankid='BANK003', banknm='ゆうちょ銀行', fee=220, remark='振込手数料', fentdt='2024-01-01 00:00:00', fentusr='system', fupdtedt='2024-01-01 00:00:00', fupdteusr='system', fupdteprg='seed.py'),
    ]
    db.session.bulk_save_objects(banks)
    db.session.commit()
    print(f"{len(banks)}件の銀行口座データを投入しました")

def seed_freight():
    """配送方法マスタにデータを投入"""
    print("配送方法データを投入中...")
    freights = [
        Freight(freightid='FRT001', freightnm='ゆうパック', fee=700, remark='通常配送', fentdt='2024-01-01 00:00:00', fentusr='system', fupdtedt='2024-01-01 00:00:00', fupdteusr='system', fupdteprg='seed.py'),
        Freight(freightid='FRT002', freightnm='宅急便', fee=800, remark='ヤマト運輸', fentdt='2024-01-01 00:00:00', fentusr='system', fupdtedt='2024-01-01 00:00:00', fupdteusr='system', fupdteprg='seed.py'),
        Freight(freightid='FRT003', freightnm='レターパック', fee=370, remark='小型商品用', fentdt='2024-01-01 00:00:00', fentusr='system', fupdtedt='2024-01-01 00:00:00', fupdteusr='system', fupdteprg='seed.py'),
    ]
    db.session.bulk_save_objects(freights)
    db.session.commit()
    print(f"{len(freights)}件の配送方法データを投入しました")

def seed_goods():
    """商品マスタにデータを投入"""
    print("商品データを投入中...")
    goods_list = [
        Goods(goodsid='G001', goodsnm='ノートPC', title='高性能ノートパソコン', price=120000, currentprice=115000, htpmark='★★★★★', mailfee=0, color='1', detail='最新モデルのノートPC', fentdt='2024-01-01 00:00:00', fentusr='system', fupdtedt='2024-01-01 00:00:00', fupdteusr='system', fupdteprg='seed.py', useflg=None),
        Goods(goodsid='G002', goodsnm='ワイヤレスマウス', title='静音設計マウス', price=3500, currentprice=2980, htpmark='★★★★', mailfee=300, color='1', detail='静音設計で快適な操作', fentdt='2024-01-01 00:00:00', fentusr='system', fupdtedt='2024-01-01 00:00:00', fupdteusr='system', fupdteprg='seed.py', useflg=None),
        Goods(goodsid='G003', goodsnm='キーボード', title='メカニカルキーボード', price=15000, currentprice=13500, htpmark='★★★★★', mailfee=500, color='1', detail='高級メカニカルスイッチ採用', fentdt='2024-01-01 00:00:00', fentusr='system', fupdtedt='2024-01-01 00:00:00', fupdteusr='system', fupdteprg='seed.py', useflg=None),
        Goods(goodsid='G004', goodsnm='モニター', title='27インチ4Kモニター', price=45000, currentprice=42000, htpmark='★★★★', mailfee=0, color='1', detail='4K解像度のモニター', fentdt='2024-01-01 00:00:00', fentusr='system', fupdtedt='2024-01-01 00:00:00', fupdteusr='system', fupdteprg='seed.py', useflg=None),
        Goods(goodsid='G005', goodsnm='Webカメラ', title='フルHD Webカメラ', price=8000, currentprice=7200, htpmark='★★★', mailfee=300, color='1', detail='在宅ワークに最適', fentdt='2024-01-01 00:00:00', fentusr='system', fupdtedt='2024-01-01 00:00:00', fupdteusr='system', fupdteprg='seed.py', useflg=None),
        Goods(goodsid='G006', goodsnm='USBハブ', title='7ポートUSBハブ', price=2500, currentprice=2200, htpmark='★★★★', mailfee=200, color='1', detail='高速データ転送対応', fentdt='2024-01-01 00:00:00', fentusr='system', fupdtedt='2024-01-01 00:00:00', fupdteusr='system', fupdteprg='seed.py', useflg=None),
        Goods(goodsid='G007', goodsnm='ヘッドセット', title='ゲーミングヘッドセット', price=12000, currentprice=10500, htpmark='★★★★★', mailfee=400, color='1', detail='7.1chサラウンド対応', fentdt='2024-01-01 00:00:00', fentusr='system', fupdtedt='2024-01-01 00:00:00', fupdteusr='system', fupdteprg='seed.py', useflg=None),
        Goods(goodsid='G008', goodsnm='外付けSSD', title='1TB 外付けSSD', price=18000, currentprice=16000, htpmark='★★★★', mailfee=300, color='1', detail='高速データ転送', fentdt='2024-01-01 00:00:00', fentusr='system', fupdtedt='2024-01-01 00:00:00', fupdteusr='system', fupdteprg='seed.py', useflg=None),
    ]
    db.session.bulk_save_objects(goods_list)
    db.session.commit()
    print(f"{len(goods_list)}件の商品データを投入しました")

def seed_arrivals():
    """入荷情報にデータを投入"""
    print("入荷データを投入中...")
    base_date = date.today() - timedelta(days=30)
    arrivals = [
        # G001 - ノートPC（複数カラー）
        Arrival(goodsid='G001', colorid='001', amount=5, price=110000, freightprice=0, earprice=0, lenprice=0, sold=2, remark='レッド', fentdt='2024-01-01 00:00:00', fentusr='system', fupdtedt='2024-01-01 00:00:00', fupdteusr='system', fupdteprg='seed.py', cache='', material='アルミニウム', ftrndate=base_date),
        Arrival(goodsid='G001', colorid='005', amount=10, price=110000, freightprice=0, earprice=0, lenprice=0, sold=3, remark='ブラック', fentdt='2024-01-01 00:00:00', fentusr='system', fupdtedt='2024-01-01 00:00:00', fupdteusr='system', fupdteprg='seed.py', cache='', material='アルミニウム', ftrndate=base_date),
        Arrival(goodsid='G001', colorid='006', amount=8, price=110000, freightprice=0, earprice=0, lenprice=0, sold=1, remark='ホワイト', fentdt='2024-01-01 00:00:00', fentusr='system', fupdtedt='2024-01-01 00:00:00', fupdteusr='system', fupdteprg='seed.py', cache='', material='アルミニウム', ftrndate=base_date),

        # G002 - ワイヤレスマウス（複数カラー）
        Arrival(goodsid='G002', colorid='001', amount=20, price=2500, freightprice=100, earprice=0, lenprice=0, sold=5, remark='', fentdt='2024-01-01 00:00:00', fentusr='system', fupdtedt='2024-01-01 00:00:00', fupdteusr='system', fupdteprg='seed.py', cache='', material='プラスチック', ftrndate=base_date),
        Arrival(goodsid='G002', colorid='002', amount=25, price=2500, freightprice=100, earprice=0, lenprice=0, sold=8, remark='', fentdt='2024-01-01 00:00:00', fentusr='system', fupdtedt='2024-01-01 00:00:00', fupdteusr='system', fupdteprg='seed.py', cache='', material='プラスチック', ftrndate=base_date),
        Arrival(goodsid='G002', colorid='005', amount=50, price=2500, freightprice=100, earprice=0, lenprice=0, sold=15, remark='', fentdt='2024-01-01 00:00:00', fentusr='system', fupdtedt='2024-01-01 00:00:00', fupdteusr='system', fupdteprg='seed.py', cache='', material='プラスチック', ftrndate=base_date),
        Arrival(goodsid='G002', colorid='006', amount=30, price=2500, freightprice=100, earprice=0, lenprice=0, sold=10, remark='', fentdt='2024-01-01 00:00:00', fentusr='system', fupdtedt='2024-01-01 00:00:00', fupdteusr='system', fupdteprg='seed.py', cache='', material='プラスチック', ftrndate=base_date),

        # G003 - キーボード
        Arrival(goodsid='G003', colorid='005', amount=20, price=12000, freightprice=200, earprice=0, lenprice=0, sold=8, remark='', fentdt='2024-01-01 00:00:00', fentusr='system', fupdtedt='2024-01-01 00:00:00', fupdteusr='system', fupdteprg='seed.py', cache='', material='金属', ftrndate=base_date),
        Arrival(goodsid='G003', colorid='006', amount=15, price=12000, freightprice=200, earprice=0, lenprice=0, sold=5, remark='', fentdt='2024-01-01 00:00:00', fentusr='system', fupdtedt='2024-01-01 00:00:00', fupdteusr='system', fupdteprg='seed.py', cache='', material='金属', ftrndate=base_date),

        # G004 - モニター
        Arrival(goodsid='G004', colorid='005', amount=15, price=40000, freightprice=0, earprice=0, lenprice=0, sold=5, remark='', fentdt='2024-01-01 00:00:00', fentusr='system', fupdtedt='2024-01-01 00:00:00', fupdteusr='system', fupdteprg='seed.py', cache='', material='液晶パネル', ftrndate=base_date),

        # G005 - Webカメラ
        Arrival(goodsid='G005', colorid='005', amount=30, price=6500, freightprice=150, earprice=0, lenprice=0, sold=12, remark='', fentdt='2024-01-01 00:00:00', fentusr='system', fupdtedt='2024-01-01 00:00:00', fupdteusr='system', fupdteprg='seed.py', cache='', material='プラスチック', ftrndate=base_date),

        # G006 - USBハブ
        Arrival(goodsid='G006', colorid='005', amount=45, price=2000, freightprice=100, earprice=0, lenprice=0, sold=20, remark='', fentdt='2024-01-01 00:00:00', fentusr='system', fupdtedt='2024-01-01 00:00:00', fupdteusr='system', fupdteprg='seed.py', cache='', material='プラスチック', ftrndate=base_date),
        Arrival(goodsid='G006', colorid='006', amount=35, price=2000, freightprice=100, earprice=0, lenprice=0, sold=15, remark='', fentdt='2024-01-01 00:00:00', fentusr='system', fupdtedt='2024-01-01 00:00:00', fupdteusr='system', fupdteprg='seed.py', cache='', material='プラスチック', ftrndate=base_date),

        # G007 - ヘッドセット
        Arrival(goodsid='G007', colorid='001', amount=12, price=10000, freightprice=200, earprice=0, lenprice=0, sold=4, remark='', fentdt='2024-01-01 00:00:00', fentusr='system', fupdtedt='2024-01-01 00:00:00', fupdteusr='system', fupdteprg='seed.py', cache='', material='プラスチック', ftrndate=base_date),
        Arrival(goodsid='G007', colorid='005', amount=18, price=10000, freightprice=200, earprice=0, lenprice=0, sold=6, remark='', fentdt='2024-01-01 00:00:00', fentusr='system', fupdtedt='2024-01-01 00:00:00', fupdteusr='system', fupdteprg='seed.py', cache='', material='プラスチック', ftrndate=base_date),
        Arrival(goodsid='G007', colorid='006', amount=15, price=10000, freightprice=200, earprice=0, lenprice=0, sold=3, remark='', fentdt='2024-01-01 00:00:00', fentusr='system', fupdtedt='2024-01-01 00:00:00', fupdteusr='system', fupdteprg='seed.py', cache='', material='プラスチック', ftrndate=base_date),

        # G008 - 外付けSSD
        Arrival(goodsid='G008', colorid='005', amount=25, price=15000, freightprice=150, earprice=0, lenprice=0, sold=10, remark='', fentdt='2024-01-01 00:00:00', fentusr='system', fupdtedt='2024-01-01 00:00:00', fupdteusr='system', fupdteprg='seed.py', cache='', material='金属', ftrndate=base_date),
        Arrival(goodsid='G008', colorid='002', amount=20, price=15000, freightprice=150, earprice=0, lenprice=0, sold=8, remark='', fentdt='2024-01-01 00:00:00', fentusr='system', fupdtedt='2024-01-01 00:00:00', fupdteusr='system', fupdteprg='seed.py', cache='', material='金属', ftrndate=base_date),
    ]
    db.session.bulk_save_objects(arrivals)
    db.session.commit()
    print(f"{len(arrivals)}件の入荷データを投入しました")

def seed_customers():
    """顧客情報にデータを投入"""
    print("顧客データを投入中...")
    customers = [
        CustomerInfo(guestid='CUST001', guestnm='山田太郎', email1='yamada@example.com', email2='', addressno='123-4567', address='東京都千代田区1-2-3', tel='03-1234-5678', kadakana='ヤマダタロウ', fentdt='2024-01-01 00:00:00', fentusr='system', fupdtedt='2024-01-01 00:00:00', fupdteusr='system', fupdteprg='seed.py'),
        CustomerInfo(guestid='CUST002', guestnm='佐藤花子', email1='sato@example.com', email2='', addressno='234-5678', address='神奈川県横浜市中区2-3-4', tel='045-2345-6789', kadakana='サトウハナコ', fentdt='2024-01-01 00:00:00', fentusr='system', fupdtedt='2024-01-01 00:00:00', fupdteusr='system', fupdteprg='seed.py'),
        CustomerInfo(guestid='CUST003', guestnm='鈴木一郎', email1='suzuki@example.com', email2='', addressno='345-6789', address='大阪府大阪市北区3-4-5', tel='06-3456-7890', kadakana='スズキイチロウ', fentdt='2024-01-01 00:00:00', fentusr='system', fupdtedt='2024-01-01 00:00:00', fupdteusr='system', fupdteprg='seed.py'),
        CustomerInfo(guestid='CUST004', guestnm='田中美咲', email1='tanaka@example.com', email2='', addressno='456-7890', address='愛知県名古屋市中区4-5-6', tel='052-4567-8901', kadakana='タナカミサキ', fentdt='2024-01-01 00:00:00', fentusr='system', fupdtedt='2024-01-01 00:00:00', fupdteusr='system', fupdteprg='seed.py'),
        CustomerInfo(guestid='CUST005', guestnm='高橋健太', email1='takahashi@example.com', email2='', addressno='567-8901', address='福岡県福岡市中央区5-6-7', tel='092-5678-9012', kadakana='タカハシケンタ', fentdt='2024-01-01 00:00:00', fentusr='system', fupdtedt='2024-01-01 00:00:00', fupdteusr='system', fupdteprg='seed.py'),
    ]
    db.session.bulk_save_objects(customers)
    db.session.commit()
    print(f"{len(customers)}件の顧客データを投入しました")

def seed_sales_records():
    """販売記録にデータを投入"""
    print("販売データを投入中...")
    sales = [
        SalesRecord(auctionid='AUC001', goodsid='G001', guestid='CUST001', belong='', price=115000, price2=115000, noteworthy=0, amount=1, colorid01='005', colorid02='', colorid03='', colorid04='', colorid05='', colorid06='', transmitflg='1', bankid='BANK001', transferflg='1', mailingflg='1', freightid='FRT001', time='2024-01-15 10:30:00', answerflg='1', mailsflg='1', trackno='1234567890', returnflg='0', drawingflg='0', remark='', problem='', fentdt='2024-01-15 00:00:00', fentusr='system', fupdtedt='2024-01-15 00:00:00', fupdteusr='system', fupdteprg='seed.py', cache='', decisionflg='1', appointno='123-4567', appointadd='東京都千代田区1-2-3', appointna='山田太郎', appointtel='03-1234-5678'),
        SalesRecord(auctionid='AUC002', goodsid='G002', guestid='CUST002', belong='', price=2980, price2=2980, noteworthy=0, amount=2, colorid01='005', colorid02='', colorid03='', colorid04='', colorid05='', colorid06='', transmitflg='1', bankid='BANK002', transferflg='1', mailingflg='1', freightid='FRT003', time='2024-01-16 14:20:00', answerflg='1', mailsflg='1', trackno='2345678901', returnflg='0', drawingflg='0', remark='', problem='', fentdt='2024-01-16 00:00:00', fentusr='system', fupdtedt='2024-01-16 00:00:00', fupdteusr='system', fupdteprg='seed.py', cache='', decisionflg='1', appointno='234-5678', appointadd='神奈川県横浜市中区2-3-4', appointna='佐藤花子', appointtel='045-2345-6789'),
        SalesRecord(auctionid='AUC003', goodsid='G003', guestid='CUST003', belong='', price=13500, price2=13500, noteworthy=0, amount=1, colorid01='005', colorid02='', colorid03='', colorid04='', colorid05='', colorid06='', transmitflg='1', bankid='BANK003', transferflg='1', mailingflg='1', freightid='FRT002', time='2024-01-17 09:15:00', answerflg='1', mailsflg='1', trackno='3456789012', returnflg='0', drawingflg='0', remark='', problem='', fentdt='2024-01-17 00:00:00', fentusr='system', fupdtedt='2024-01-17 00:00:00', fupdteusr='system', fupdteprg='seed.py', cache='', decisionflg='1', appointno='345-6789', appointadd='大阪府大阪市北区3-4-5', appointna='鈴木一郎', appointtel='06-3456-7890'),
    ]
    db.session.bulk_save_objects(sales)
    db.session.commit()
    print(f"{len(sales)}件の販売データを投入しました")

def seed_order_goods():
    """注文商品にデータを投入"""
    print("注文データを投入中...")
    orders = [
        OrderGoods(orderid='ORD001', goodsid='G006', goodsnm='USBハブ', colorid='005', detail='追加発注', orderdate=date.today() - timedelta(days=10), shipdate=date.today() - timedelta(days=3), quantity=30, shipflg=1, fupdteuser='system', deliveredflg=1, delivereddate=date.today() - timedelta(days=3)),
        OrderGoods(orderid='ORD002', goodsid='G007', goodsnm='ヘッドセット', colorid='005', detail='新規発注', orderdate=date.today() - timedelta(days=5), shipdate=None, quantity=20, shipflg=0, fupdteuser='system', deliveredflg=0, delivereddate=None),
    ]
    db.session.bulk_save_objects(orders)
    db.session.commit()
    print(f"{len(orders)}件の注文データを投入しました")

def main():
    """メイン処理"""
    with app.app_context():
        print("\n=== データベースの初期化を開始します ===\n")

        # テーブルの作成
        print("テーブルを作成中...")
        db.create_all()
        print("テーブルの作成が完了しました\n")

        # 既存データの削除
        clear_all_data()
        print()

        # マスタデータの投入
        seed_colors()
        seed_bank_accounts()
        seed_freight()

        # 商品データの投入
        seed_goods()

        # 入荷データの投入
        seed_arrivals()

        # 顧客データの投入
        seed_customers()

        # 販売データの投入
        seed_sales_records()

        # 注文データの投入
        seed_order_goods()

        print("\n=== すべてのデータ投入が完了しました ===")
        print("アプリケーションを起動できます: python app.py")

if __name__ == '__main__':
    main()

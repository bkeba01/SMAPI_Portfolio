from collections import defaultdict,namedtuple
from datetime import datetime,timedelta
from __init__ import app, cache, db
from flask import flash
from sqlalchemy import or_ # or_も先頭に
from unittest.mock import patch, MagicMock

from models import Arrival, Goods, SalesRecord, SetGoods, Color, CustomerInfo, OrderGoods


# --- メインロジック ---
@cache.cached(timeout=300)
def stock_calculation():
    """
    販売記録に基づいて在庫数を更新するメイン関数。
    """
    # この関数はキャッシュデコレータを持つため、トップレベルでのインポートが必要
    
    def _stock_calculation_impl():
        import logging
        logging.info("在庫計算処理を開始します。")
        
        sales_records_to_update, setgoods_sales_records_to_update = _get_sales_records_to_update()
        print(setgoods_sales_records_to_update)
        if not sales_records_to_update and not setgoods_sales_records_to_update:
            print("在庫を更新すべき新しい販売記録はありませんでした。")
            now = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
            return 0, now

        sales_distribution = _calculate_sales_distribution(sales_records_to_update,setgoods_sales_records_to_update)

        updated_count = _update_stock_from_sales(sales_distribution)
        
        if updated_count > 0:
            updated_good_ids = {key[0] for key in sales_distribution.keys()}
            updated_setgoods_ids={key[0] for key in setgoods_sales_records_to_update}
            _update_arrival_timestamp_for_updated(updated_good_ids)
            _update_setgoods_timestamp_for_updated(updated_setgoods_ids)

        logging.info(f"{updated_count}件の商品の在庫を更新しました。")
        now = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        return updated_count, now
    return _stock_calculation_impl()

# --- ヘルパー関数 ---

def _get_sales_records_to_update():
    """
    データベースから在庫更新が必要な販売記録を取得する。
    """

    return (
        db.session.query(
            SalesRecord.goodsid,
            SalesRecord.amount.label('sales_amount'),
            SalesRecord.fupdtedt.label('sales_fupdtedt'),
            SalesRecord.colorid01,
            SalesRecord.colorid02,
            SalesRecord.colorid03,
            SalesRecord.colorid04,
            SalesRecord.colorid05,
            SalesRecord.colorid06,
        )
        .join(Arrival, SalesRecord.goodsid == Arrival.goodsid)
        .join(Goods, SalesRecord.goodsid == Goods.goodsid)
        .filter(
            Goods.useflg.is_(None),
            SalesRecord.mailingflg==("Y"),
            or_(
                SalesRecord.fupdtedt > Arrival.fupdtedt,
                Arrival.fupdtedt.is_(None)
            ),

        ).all()
    ),(
        db.session.query(
            SetGoods.goodsid.label('goodsid'),
            SalesRecord.amount.label('sales_amount'),
            *[getattr(SetGoods, f'sgid{i}') for i in range(1, 11)],
            *[getattr(SetGoods, f'snum{i}') for i in range(1, 11)],
            *[getattr(SetGoods, f'scolorid{i}') for i in range(1, 11)],
            SalesRecord.colorid01.label('colorid01'),
            SalesRecord.colorid02.label('colorid02'),
            SalesRecord.colorid03.label('colorid03'),
            SalesRecord.colorid04.label('colorid04'),
            SalesRecord.colorid05.label('colorid05'),
            SalesRecord.colorid06.label('colorid06')
        )
        .join(SalesRecord, SetGoods.goodsid == SalesRecord.goodsid)
        .filter(
            SetGoods.useflg.is_(None),
            SalesRecord.mailingflg==("Y"),
            or_(
                SalesRecord.fupdtedt > SetGoods.fupdtedt,
                SetGoods.fupdtedt.is_(None)
            ),
        ).all()
    )

def _calculate_sales_distribution(sales_records,setgoods_sales_records_to_update):
    """
    販売記録をループし、販売数を商品・カラーごとに分配・集計する。
    """
    sales_distribution = defaultdict(int)
    processed_sales = set()

    for record in sales_records:
        sale_key = (record.goodsid, record.sales_amount, record.sales_fupdtedt)
        if sale_key in processed_sales:
            continue
        processed_sales.add(sale_key)
        _distribute_sales_for_record(record, sales_distribution)
    for record in setgoods_sales_records_to_update:
        _distribute_setgoods_sales_for_record(record,sales_distribution)
        
    return sales_distribution

def _distribute_sales_for_record(record, sales_distribution):
    """
    1つの販売記録に対して、販売数を分配し、結果をsales_distributionに追加する。
    """
    sales_amount = record.sales_amount or 0
    sub_color_ids = [cid for cid in [record.colorid01, record.colorid02, record.colorid03, record.colorid04, record.colorid05, record.colorid06] if cid]
    print(f"商品のカラーIDへの分配を開始します。")
    print(f"--- record.goodsid: {record.goodsid} の処理を開始 ---")
    print(f"売上数: {sales_amount}, カラーID: {sub_color_ids}")

    if not sub_color_ids:
        
        print(f"カラーIDが指定されていないため、商品ID: {record.goodsid} に紐づく最初のカラーIDを検索します。")
        
        # Arrivalテーブルからgoodsidに紐づく最初のcoloridを取得
        arrival_record = db.session.query(Arrival.colorid).filter(Arrival.goodsid == record.goodsid).first()
        
        if arrival_record:
            first_color_id = arrival_record.colorid
            print(f"商品ID: {record.goodsid} に紐づくカラーID {first_color_id} が見つかりました。")
            sales_distribution[(record.goodsid, first_color_id)] += sales_amount
        else:
            print(f"警告: 商品ID: {record.goodsid} に紐づく在庫情報が見つかりませんでした。在庫更新をスキップします。")
        return


    print(f"{record.goodsid} は通常商品です。")
    num_colors = len(sub_color_ids)
    base_amount = sales_amount // num_colors
    remainder = sales_amount % num_colors
    print(f"販売数をカラー数({num_colors})で分配します。基本数: {base_amount}, 余り: {remainder}")

    for i, color_id in enumerate(sub_color_ids):
        amount_to_add = base_amount + (1 if i < remainder else 0)
        sales_distribution[(record.goodsid, color_id)] += amount_to_add
        print(f"  - カラー {color_id} の販売数を {amount_to_add} 追加")
    
    print(f"--- record.goodsid: {record.goodsid} の通常商品処理完了 ---")

def _distribute_setgoods_sales_for_record(record,sales_distribution):
    """
    1つの販売記録に対して、販売数を分配し、結果をsales_distributionに追加する。
    """
    sales_amount = record.sales_amount or 0
    sub_color_ids = [cid for cid in [record.colorid01, record.colorid02, record.colorid03, record.colorid04, record.colorid05, record.colorid06] if cid]
    """getattrは、Pythonの組み込み関数で、オブジェクトの属性を動的に取得するために使用されます。
    getattr(record, f'scolorid{1}')では、recordオブジェクトから'scolorid1'を動的に取得しています。"""
    print(f"セット商品の子へ分配を開始します。")
    print(f"--- record.goodsid: {record.goodsid} の処理を開始 ---")
    print(f"売上数: {sales_amount}, カラーID: {sub_color_ids}")

    

    for i in range(1, 11):  # SETGOODSID1からSETGOODSID10までループ
        component_good_id = getattr(record, f'sgid{i}')
        set_color_id = getattr(record, f'scolorid{i}') or None
        set_number = getattr(record, f'snum{i}') or 1 # デフォルト値を1に設定
        first_color_sell = 0
        if not set_color_id:
            if component_good_id:
                #カラー指定なしの小商品についての処理
                if sub_color_ids:
                    #お客様のカラー選択あり
                    print(f"セット商品のカラーIDが指定されているため、セット構成品ID: {component_good_id} のカラーIDを検索します。")
                    for sub_color_id in sub_color_ids:
                        if not sub_color_id:
                            continue
                        goods_record = db.session.query(Goods).filter(Goods.goodsid == component_good_id).first()
                        if goods_record.color=='1' or goods_record.color=='0':
                            goods_stock = db.session.query(Arrival).filter(Arrival.goodsid == component_good_id, Arrival.colorid == sub_color_id).first()
                            if goods_stock:
                                sales_to_add = sales_amount * set_number
                                sales_distribution[(component_good_id, sub_color_id)] += sales_to_add
                                print(f"  - セット構成品 {component_good_id} (カラー: {sub_color_id}) の販売数を {sales_to_add} (数量: {set_number}) 追加")
                                first_color_sell=1
                            else:
                                print(f"セット商品の構成品(ID:{component_good_id})の在庫情報が、指定されたカラー(ID:{sub_color_id})で見つかりませんでした。")
                        else:
                            print(f"販売されたセット商品のカラー指定なし小商品にカラーフラッグがついていなかった:{component_good_id}->任意カラーと判断、引く")
                else:
                    #お客様のカラー選択なし
                    goods_record = db.session.query(Goods).filter(Goods.goodsid == component_good_id).first()
                    if goods_record:
                        if goods_record.color=='1' or goods_record.color=='0':
                            goods_stock_list = db.session.query(Arrival).filter(Arrival.goodsid == component_good_id).all()
                            #小商品のカラーフラッグあり->小商品はお客様から指定される想定->エラー
                            if len(goods_stock_list)>=2:
                                flash(f"警告: お客様のカラー選択に依存した小商品において、お客様がカラーを指定しなかった(カラーフラッグあり/カラー2色以上あり/カラー選択なし):小商品>{component_good_id},親商品>{record.goodsid}","warning")
                                first_color_sell=1
                            elif len(goods_stock_list)==1:
                                goods_stock = goods_stock_list[0]
                                sales_to_add = sales_amount * set_number
                                sales_distribution[(component_good_id, goods_stock.colorid)] += sales_to_add
                                first_color_sell=1
                            else:
                                flash(f"警告: 販売された小商品は在庫管理(Arrival)にありません。:小商品>{component_good_id},親商品>{record.goodsid}","warning")
                    else:
                        flash(f"警告: セット商品の構成品ID: {component_good_id} は商品(Goods)に存在しません。在庫更新をスキップします。", "warning")
                        first_color_sell=1

                if first_color_sell==0:
                    print(f"警告: セット商品のカラーIDが指定されていないため、セット構成品ID: {component_good_id} の最初のカラーIDを引きます。")
                    # Arrivalテーブルからgoodsidに紐づく最初のcoloridを取得
                    arrival_record = db.session.query(Arrival.colorid).filter(Arrival.goodsid == component_good_id).first()

                    if arrival_record:
                        first_color_id = arrival_record.colorid
                        sales_to_add = sales_amount * set_number
                        sales_distribution[(component_good_id, first_color_id)] += sales_to_add
                        print(f"  - セット構成品 {component_good_id} (カラー: {first_color_id}) の販売数を {sales_to_add} (数量: {set_number}) 追加")
                    else:
                        flash(f"警告: セット構成品ID: {component_good_id} に紐づく在庫情報が見つかりませんでした。在庫更新をスキップします。", "warning")
        else:
            if component_good_id:

                arrival_record = db.session.query(Arrival.colorid).filter(Arrival.goodsid == component_good_id, Arrival.colorid == set_color_id).first()
                if arrival_record:
                    sales_to_add = sales_amount * set_number
                    sales_distribution[(component_good_id, set_color_id)] += sales_to_add
                    print(f"  - セット構成品 {component_good_id} (カラー: {set_color_id}) の販売数を {sales_to_add} (数量: {set_number}) 追加")
                else:
                    flash(f"警告: セット構成品ID: {component_good_id} に紐づく在庫情報が見つかりませんでした。在庫更新をスキップします。", "warning")

    print(f"--- record.goodsid: {record.goodsid} のセット商品処理完了 ---")
    return

def _update_stock_from_sales(sales_distribution):
    """
    集計された販売数に基づき、Arrivalテーブルの在庫数を更新する。
    """

    import logging

    if not sales_distribution:
        print("--- 在庫更新処理: 更新対象の販売記録はありません ---")
        return 0

    print("--- 在庫更新処理を開始します ---")
    print("集計された販売数:")
    for (goodsid, colorid), total_sales in sales_distribution.items():
        print(f"  - 商品ID: {goodsid}, カラーID: {colorid}, 販売合計: {total_sales}")

    updated_count = 0
    goodsid_list = {gs[0] for gs in sales_distribution.keys()}
    arrivals_to_update = db.session.query(Arrival).filter(Arrival.goodsid.in_(goodsid_list)).all()
    arrival_dict = {(a.goodsid, a.colorid): a for a in arrivals_to_update}

    print("\n在庫数の更新計算:")
    for (goodsid, colorid), total_sales in sales_distribution.items():
        if colorid is None:
            logging.warning(f"在庫更新スキップ: 商品ID={goodsid} のカラーIDがNoneです。")
            print(f"  - 商品ID: {goodsid} のカラーIDがNoneのため、更新をスキップします。")
            continue
        arrival = arrival_dict.get((goodsid, colorid))
        if arrival:
            current_stock = arrival.amount or 0
            new_stock = max(0, current_stock - total_sales)
            print(f"  - 商品ID: {goodsid}, カラーID: {colorid}")
            print(f"    -現在の在庫数: {current_stock}")
            print(f"    -販売合計: {total_sales}")
            print(f"    -計算後の在庫数: {current_stock} - {total_sales} = {new_stock}")
            if new_stock != current_stock:
                arrival.amount = new_stock
                updated_count += 1
                print("    -> 在庫数を更新しました。")
            else:
                print("    -> 在庫数は変更されませんでした。")
        else:
            logging.warning(f"在庫更新スキップ: 商品ID={goodsid}, カラーID={colorid} の在庫情報が見つかりません。")
            print(f"  - 商品ID: {goodsid}, カラーID: {colorid} の在庫情報が見つかりません。更新をスキップします。")
            
    if updated_count > 0:
        print(f"\nデータベースに {updated_count} 件の在庫更新をコミットします。")
        db.session.commit()
    else:
        print("\n更新された在庫はありませんでした。")
    
    print("--- 在庫更新処理を完了しました ---")
    return updated_count

def _update_arrival_timestamp_for_updated(good_ids):
    """
    更新された商品IDリストに基づき、関連するArrivalレコードのfupdtedtを現在時刻に更新する。
    """

    if not good_ids:
        return

    now_str = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    db.session.query(Arrival).filter(Arrival.goodsid.in_(good_ids)).update(
        {'fupdtedt': now_str}, 
        synchronize_session=False
    )
    db.session.commit()

def _update_setgoods_timestamp_for_updated(good_ids):

    if not good_ids:
        return
    now_str = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    print(good_ids)
    db.session.query(SetGoods).filter(SetGoods.goodsid.in_(good_ids)).update(
        {'fupdtedt': now_str}, 
        synchronize_session=False
    )
    db.session.commit()


# --- その他ユーティリティ関数 ---

def arrival_fupdtedt_init():

    now = datetime.now()
    for arrival in db.session.query(Arrival).all():
        arrival.fupdtedt = now.strftime("%Y/%m/%d %H:%M:%S")
    db.session.commit()

def arrival_fupdtedt_set(time):

    data = datetime.strptime(time, "%Y/%m/%d %H:%M:%S")
    for arrival in db.session.query(Arrival).all():
        arrival.fupdtedt = data.strftime("%Y/%m/%d %H:%M:%S")
    db.session.commit()

def colorid_connect_color(colorid):

    color = db.session.query(Color.colornm).filter(Color.colorid == colorid).first()
    return color.colornm if color else colorid

def get_unregistered_sales_today():
    """今日の売上のうち、在庫マスター（Arrival）に登録されていない商品を特定する。"""

    today = datetime.now()
    start_of_week = today - timedelta(days=today.weekday())
    start_str = start_of_week.strftime('%Y/%m/%d')
    today_str = today.strftime('%Y/%m/%d')

    # 1. 今週の売上を取得
    sales_this_week = (
        db.session.query(SalesRecord)
        .filter(SalesRecord.fupdtedt >= start_str, SalesRecord.fupdtedt <= today_str)
        .all()
    )

    # 2. セット商品のIDを一度に取得
    set_good_ids = {
        row.goodsid for row in db.session.query(SetGoods.goodsid).all()
    }

    # 3. Arrivalテーブルの情報を効率的な構造に変換
    arrival_info = defaultdict(set)
    for goodsid, colorid in db.session.query(Arrival.goodsid, Arrival.colorid).all():
        arrival_info[goodsid].add(colorid)

    unregistered_sales = []
    processed_sales = set()

    # 4. 売上データをループ
    for sale in sales_this_week:
        if sale.goodsid in set_good_ids:
            continue

        sale_colors = {
            c for c in [
                sale.colorid01, sale.colorid02, sale.colorid03,
                sale.colorid04, sale.colorid05, sale.colorid06
            ] if c is not None
        }

        # ケース1: 売上にカラー指定がない
        if not sale_colors:
            if sale.goodsid not in arrival_info:
                if (sale.goodsid, None) not in processed_sales:
                    unregistered_sales.append({
                        'goodsid': sale.goodsid,
                        'colorid': None
                    })
                    processed_sales.add((sale.goodsid, None))
        # ケース2: 売上にカラー指定がある
        else:
            for color in sale_colors:
                # Arrivalにgoodsidがない、またはgoodsidがあってもcoloridがない
                if sale.goodsid not in arrival_info or color not in arrival_info[sale.goodsid]:
                    if (sale.goodsid, color) not in processed_sales:
                        unregistered_sales.append({
                            'goodsid': sale.goodsid,
                            'colorid': color
                        })
                        processed_sales.add((sale.goodsid, color))

    # 5. 未登録商品の名前を取得
    unregistered_good_ids = {sale['goodsid'] for sale in unregistered_sales}
    if unregistered_good_ids:
        goods_names = {
            g.goodsid: g.goodsnm for g in db.session.query(Goods.goodsid, Goods.goodsnm).filter(Goods.goodsid.in_(unregistered_good_ids)).all()
        }
        for sale in unregistered_sales:
            sale['goodsnm'] = goods_names.get(sale['goodsid'], 'Unknown')

    return unregistered_sales

def delivered_goods_to_count_arrival(delivered_orderids,end_date_hidden):
    """
    配達済みの注文商品を在庫数に反映させる関数。
    """
    updated_count=0
    if not delivered_orderids:
        return 0

    # 文字列をdateオブジェクトに変換
    try:
        delivered_date = datetime.strptime(end_date_hidden, '%Y-%m-%d').date()
    except (ValueError, TypeError) as e:
        flash(f"配送日の形式が正しくありません: {e}", "danger")
        return 0

    # 1. 配達済みの注文商品を取得
    order_goods_to_process = db.session.query(OrderGoods).filter(
        OrderGoods.orderid.in_(delivered_orderids)
    ).all()
    if not order_goods_to_process:
        return 0
    # 効率化のため、関連するArrivalレコードを一度に取得
    all_good_ids = {og.goodsid for og in order_goods_to_process}
    arrivals = db.session.query(Arrival).filter(Arrival.goodsid.in_(all_good_ids)).all()
    # 検索しやすいように辞書に変換
    arrival_dict = {(a.goodsid, a.colorid): a for a in arrivals}
    # 2. 各注文商品を処理
    for order_good in order_goods_to_process:
        # 3. 対応するArrivalレコードを検索
        arrival_record = arrival_dict.get((order_good.goodsid, order_good.colorid))
        if arrival_record:
            # 4. 在庫数を更新
            original_amount = int(arrival_record.amount or 0)
            added_amount = int(order_good.quantity or 0)
            arrival_record.amount = original_amount + added_amount
            updated_count+=1
            print(f"在庫更新: 商品ID={order_good.goodsid}, カラーID={order_good.colorid}, 更新前の在庫={original_amount}, 追加数={added_amount}, 更新後の在庫={arrival_record.amount}")
            OrderGoods.query.filter(
                    OrderGoods.orderid == order_good.orderid
                ).update({'deliveredflg': 1, 'delivereddate': delivered_date}, synchronize_session=False)
        else:
            # 5. 警告を出す
            flash(f"警告: 配達済み商品(商品ID: {order_good.goodsid}, カラーID: {order_good.colorid})は在庫マスターに存在しないため、在庫数を更新できませんでした。", "warning")
    # 6. 変更をコミット
    try:
        db.session.commit()
        flash("配達済み商品の在庫への反映が完了しました。", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"在庫更新中にエラーが発生しました: {e}", "danger")
    return updated_count

# --- 動作検証 ---

def test_sales_distribution_logic():
    """
    販売数の分配ロジックを検証するためのテスト関数。
    """

    # --- Mocks Setup ---
    SalesRecordMock = namedtuple('SalesRecordMock', ['goodsid', 'sales_amount', 'sales_fupdtedt', 'colorid01', 'colorid02', 'colorid03', 'colorid04', 'colorid05', 'colorid06'])
    
    set_goods_fields = ['goodsid', 'sales_amount']
    set_goods_fields.extend([f'sgid{i}' for i in range(1, 11)])
    set_goods_fields.extend([f'snum{i}' for i in range(1, 11)])
    set_goods_fields.extend([f'scolorid{i}' for i in range(1, 11)])
    set_goods_fields.extend([f'colorid0{i}' for i in range(1, 7)])
    SetGoodsRecordMock = namedtuple('SetGoodsRecordMock', set_goods_fields, defaults=(None,) * len(set_goods_fields))

    print("--- 販売数分配ロジックのテストを開始します ---")
    
    # --- 通常商品のテスト ---
    print("\n--- 通常商品のテスト ---")

    # ケース1: 割り切れるケース
    print("\n[ケース1] 販売数10個、カラー2つ (A, B)")
    record1 = SalesRecordMock('TEST001', 10, '2024-01-01', 'A', 'B', None, None, None, None)
    dist1 = defaultdict(int)
    _distribute_sales_for_record(record1, dist1)
    print(f"分配結果: {dict(dist1)}")
    assert dist1[('TEST001', 'A')] == 5
    assert dist1[('TEST001', 'B')] == 5
    print("(OK)")

    # ケース2: 割り切れないケース
    print("\n[ケース2] 販売数10個、カラー3つ (A, B, C)")
    record2 = SalesRecordMock('TEST002', 10, '2024-01-01', 'A', 'B', 'C', None, None, None)
    dist2 = defaultdict(int)
    _distribute_sales_for_record(record2, dist2)
    print(f"分配結果: {dict(dist2)}")
    assert dist2[('TEST002', 'A')] == 4 
    assert dist2[('TEST002', 'B')] == 3
    assert dist2[('TEST002', 'C')] == 3
    print("(OK)")

    # ケース3: カラーが1つのケース
    print("\n[ケース3] 販売数7個、カラー1つ (A)")
    record3 = SalesRecordMock('TEST003', 7, '2024-01-01', 'A', None, None, None, None, None)
    dist3 = defaultdict(int)
    _distribute_sales_for_record(record3, dist3)
    print(f"分配結果: {dict(dist3)}")
    assert dist3[('TEST003', 'A')] == 7
    print("(OK)")

    # ケース4: カラー指定がないケース (DB問い合わせをモック)
    print("\n[ケース4] 販売数5個、カラー指定なし")
    with patch('utils.db.session.query') as mock_query_case4:
        mock_arrival = MagicMock()
        mock_arrival.colorid = 'ANY_COLOR'
        mock_query_case4.return_value.filter.return_value.first.return_value = mock_arrival
        record4 = SalesRecordMock('TEST004', 5, '2024-01-01', None, None, None, None, None, None)
        dist4 = defaultdict(int)
        _distribute_sales_for_record(record4, dist4)
        print(f"分配結果: {dict(dist4)}")
        assert dist4[('TEST004', 'ANY_COLOR')] == 5
        print("(OK)")

    # ケース5: 複雑なケース
    print("\n[ケース5] 販売数8個、カラー5つ (A, B, C, D, E)")
    record5 = SalesRecordMock('TEST005', 8, '2024-01-01', 'A', 'B', 'C', 'D', 'E', None)
    dist5 = defaultdict(int)
    _distribute_sales_for_record(record5, dist5)
    print(f"分配結果: {dict(dist5)}")
    assert dist5[('TEST005', 'A')] == 2
    assert dist5[('TEST005', 'B')] == 2
    assert dist5[('TEST005', 'C')] == 2
    assert dist5[('TEST005', 'D')] == 1
    assert dist5[('TEST005', 'E')] == 1
    print("(OK)")

    # --- セット商品のテスト ---
    print("\n--- セット商品のテスト ---")

    with patch('utils.db.session.query') as mock_query_setgoods:

        def first_side_effect():
            filter_mock = mock_query_setgoods.return_value.filter
            filter_args = filter_mock.call_args[0]
            if len(filter_args) == 2: # カラー指定あり
                color_val = filter_args[1].right.value
                if color_val == 'RED':
                    return MagicMock(colorid='RED')
            elif len(filter_args) == 1: # カラー指定なし
                goodsid_val = filter_args[0].right.value
                if goodsid_val == 'COMP02':
                    return MagicMock(colorid='BLUE')
            return None

        mock_query_setgoods.return_value.filter.return_value.first.side_effect = first_side_effect

        # ケース6: セット商品（カラー指定あり）
        print("\n[ケース6] セット商品販売、構成品にカラー指定あり")
        set_record1 = SetGoodsRecordMock(goodsid='SET01', sales_amount=2, sgid1='COMP01', snum1=3, scolorid1='RED')
        dist6 = defaultdict(int)
        _distribute_setgoods_sales_for_record(set_record1, dist6)
        print(f"分配結果: {dict(dist6)}")
        assert dist6[('COMP01', 'RED')] == 6
        print("(OK)")

        # ケース7: セット商品（カラー指定なし）
        print("\n[ケース7] セット商品販売、構成品にカラー指定なし")
        set_record2 = SetGoodsRecordMock(goodsid='SET02', sales_amount=5, sgid1='COMP02', snum1=1, scolorid1=None)
        dist7 = defaultdict(int)
        _distribute_setgoods_sales_for_record(set_record2, dist7)
        print(f"分配結果: {dict(dist7)}")
        assert dist7[('COMP02', 'BLUE')] == 5
        print("(OK)")

    print("\n--- すべてのテストケースに成功しました ---")
    return True
if __name__ == '__main__':
    # test_sales_distribution_logic()
    test_sales_distribution_logic()
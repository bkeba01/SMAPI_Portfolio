from __future__ import unicode_literals
from __init__ import app,db,cache
from flask import render_template,request,session,redirect,url_for,flash, abort, jsonify
from models import Arrival,Goods,SalesRecord,SetGoods, OrderGoods, Color, CustomerInfo, BankAccount, Freight
from sqlalchemy import or_,and_,func
from utils import stock_calculation,arrival_fupdtedt_init,colorid_connect_color,arrival_fupdtedt_set, get_unregistered_sales_today, delivered_goods_to_count_arrival
from datetime import datetime
import os
import re
import json
from forms import SetGoodsForm, OrderGoodsForm, ShipmentForm, DeliveredForm, SalesSearchForm, SalesEditForm


@app.route('/')
@app.route('/home')
def home_page():
    # --- Dashboard Metrics ---
    # 在庫総数 (Total stock quantity)
    total_stock = db.session.query(func.sum(Arrival.amount)).scalar() or 0

    # 在庫僅少商品 (Low stock items, e.g., less than 10)
    low_stock_threshold = 10
    low_stock_items_count = Arrival.query.filter(Arrival.amount < low_stock_threshold, Arrival.amount > 0).count()

    # 未出荷の注文件数 (Unshipped orders)
    unshipped_orders_count = OrderGoods.query.filter(OrderGoods.shipflg == 0).count()

    # セット商品数 (Number of set goods)
    set_goods_count = SetGoods.query.count()

    # --- Recent Activity ---
    # 最近更新された在庫 (Recently updated stock items)
    recently_updated_stock = Arrival.query.order_by(Arrival.fupdtedt.desc()).limit(5).all()

    # 未出荷の注文 (Oldest unshipped orders)
    pending_orders = OrderGoods.query.filter(OrderGoods.shipflg == 0).order_by(OrderGoods.orderdate.asc()).limit(5).all()

    return render_template('home.html',
                           total_stock=total_stock,
                           low_stock_items_count=low_stock_items_count,
                           unshipped_orders_count=unshipped_orders_count,
                           set_goods_count=set_goods_count,
                           recently_updated_stock=recently_updated_stock,
                           pending_orders=pending_orders,
                           colorid_connect_color=colorid_connect_color
                           )

@app.route('/market',methods=['GET','POST'])
def market_page():
    #stock_calculation()
    #salesrecords=SalesRecord.query.all()
    arrivals=Arrival.query.all()
    input_permission=True
    search_text = request.args.get('search')
    stock_operator = request.args.get('stock_operator')
    stock_value = request.args.get('stock_value')

    query = db.session.query(Arrival).join(Arrival.goods).filter(Goods.useflg.is_(None))

    if search_text:
        query = query.filter(
            or_(
                Arrival.goodsid.ilike(f'%{search_text}%'),
                Goods.goodsnm.ilike(f'%{search_text}%')
            )
        )

    if stock_operator and stock_value:
        try:
            stock_value_int = int(stock_value)
            if stock_operator == 'greater_than':
                query = query.filter(Arrival.amount > stock_value_int)
            elif stock_operator == 'less_than':
                query = query.filter(Arrival.amount < stock_value_int)
        except ValueError:
            # Handle cases where stock_value is not a valid integer
            pass

    arrivals = query.all()

    if request.method=='GET':
        if 'search' in request.args:
            input_permission=True
        if session.pop('post_done',False):
            input_permission=False
        return render_template('market.html', arrivals=arrivals,
                               input_permission=input_permission,
                               search_text=search_text,
                               colorid_connect_color=colorid_connect_color, 
                               stock_operator=stock_operator, 
                               stock_value=stock_value)

    if request.method=='POST':
        now=datetime.now()
        for arrival in arrivals:
            field_name=str(arrival.goodsid)+"_"+str(arrival.colorid)+"_amount"
            amount=request.form.get(field_name)
            arrival.fupdtedt = now.strftime("%Y/%m/%d %H:%M:%S")
            if amount not in [None,""]:
                arrival.amount=int(amount)
                input_permission=False
                session['post_done'] = True
                #セッションとは、ユーザーごとに持てるs一時的な値
                #post_doneキーにTrueが入っている
        db.session.commit()
        return redirect(url_for('market_page',search=search_text))

@app.route('/stock',methods=['GET','POST'])
def stock_page():
    #arrival_fupdtedt_set("2025/08/10 16:00:00")
    
    #最終計算時間を取得。
    update_num, current_update_time = stock_calculation()

    #セッションを用いたサーバー側にあるユーザー情報を取得する関数。
    #last_shown_update_timeは名前(キー)であり、自由に名付けられる。
    #サーバー側のユーザー情報のlast_shown_update_timeという名前で変数を作った。
    last_shown_update_time = session.get('last_shown_update_time')
    if current_update_time!=last_shown_update_time and update_num ==0:
        flash(f'更新すべき商品はありませんでした。','info')
    if current_update_time!=last_shown_update_time and update_num!=0:
        flash(f'{update_num}件の在庫数が更新されました。','info')

    # --- Rest of the stock_page function (pagination, search, rendering) ---
    unregistered_sales = get_unregistered_sales_today()
    print(f"unregistered_sales:{unregistered_sales}")
    page = request.args.get('page', 1, type=int)
    search_text = request.args.get('search')
    min_quantity = request.args.get('min_quantity')
    max_quantity = request.args.get('max_quantity')
    sort_by = request.args.get('sort_by', 'fupdtedt') # デフォルトは更新日時
    order = request.args.get('order', 'desc') # デフォルトは降順

    query = db.session.query(Arrival).join(Arrival.goods).filter(Goods.useflg.is_(None))
    
    has_search_params = False

    if search_text:
        query = query.filter(
            or_(
                Goods.goodsnm.ilike(f'%{search_text}%'),
                Arrival.goodsid.ilike(f'%{search_text}%')
            )
        )
        has_search_params = True
    if min_quantity:
        try:
            query = query.filter(Arrival.amount >= int(min_quantity))
            has_search_params = True
        except ValueError:
            pass # Invalid input, ignore filter
    if max_quantity:
        try:
            query = query.filter(Arrival.amount <= int(max_quantity))
            has_search_params = True
        except ValueError:
            pass # Invalid input, ignore filter

    # ソート処理
    sort_column_map = {
        'goodsid': Arrival.goodsid,
        'goodsnm': Goods.goodsnm,
        'amount': Arrival.amount,
        'fupdtedt': Arrival.fupdtedt
    }
    
    # 'amount'でのソートの場合、NULLを0として扱う
    if sort_by == 'amount':
        sort_expression = func.coalesce(Arrival.amount, 0)
    else:
        sort_expression = sort_column_map.get(sort_by, Arrival.fupdtedt)

    if order == 'asc':
        query = query.order_by(sort_expression.asc())
    else:
        query = query.order_by(sort_expression.desc())

    total_count = query.count()
    print("検索結果: " + str(total_count))
    pagination = query.paginate(page=page, per_page=20, error_out=False)
    arrivals = pagination.items

    max_stock_quantity = db.session.query(func.max(Arrival.amount)).scalar() or 1000
    session['last_shown_update_time']=current_update_time
    db.session.commit()

    
    return render_template('stock.html', 
                           arrivals=arrivals,
                           min_quantity=min_quantity,
                           max_quantity=max_quantity,
                           colorid_connect_color=colorid_connect_color,
                           search_text=search_text,
                           max_stock_quantity=max_stock_quantity,
                           last_updated=current_update_time, # Pass current_update_time to template
                           pagination=pagination,
                           total_count=total_count,
                           sort_by=sort_by,
                           order=order,
                           unregistered_sales=unregistered_sales)

@app.route('/stock_input', methods=['GET'])
def stock_input_page():
    search_text = request.args.get('search')
    query = db.session.query(Arrival).join(Arrival.goods).filter(Goods.useflg.is_(None))
    total_count = 0
    if search_text:
        query = query.filter(
            or_(
                Arrival.goodsid.ilike(f'%{search_text}%'),
                Goods.goodsnm.ilike(f'%{search_text}%')
            )
        )
        total_count = query.count()
        arrivals = query.all()
    else:
        arrivals=None
    
    return render_template('stock_input.html', arrivals=arrivals, search_text=search_text, total_count=total_count, colorid_connect_color=colorid_connect_color)

@app.route('/update_multiple_stocks', methods=['POST'])
def update_multiple_stocks():
    search_text = request.form.get('search')
    updated_count = 0
    error_count = 0

    # amounts_data の代わりに request.form を直接ループ
    for key, value in request.form.items():
        if key.startswith('amounts['):
            try:
                # キーからgoodsidとcoloridを抽出
                # 例: 'amounts[123,456]' から 123 と 456 を抽出
                match = re.match(r'amounts\[(.+)\]\[(.+)\]\[(.+)\]\[(.+)\]', key)
                #[goodsid][カラー][現在の数量][カラーid]
                if match:
                    goodsid = match.group(1)
                    color = match.group(2)
                    current_amount=int(match.group(3))
                    colorid=match.group(4)
                    amount = int(value) # valueが直接amountになる

                    if amount < 0:
                        flash(f'商品ID: {goodsid}, カラーID: {color} の在庫数は0以上の値を入力してください。', 'danger')
                        error_count += 1
                        continue

                    arrival = Arrival.query.filter_by(goodsid=goodsid, colorid=colorid).first()
                    if arrival:
                        if current_amount!=amount:
                            arrival.amount = amount
                            arrival.fupdtedt = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
                            updated_count += 1
                            flash(f'商品ID: {goodsid}, カラーID: {color}の在庫数を「{amount}」に更新しました。','success')
                    else:
                        flash(f'商品ID: {goodsid}, カラーID: {color} が見つかりませんでした。', 'warning')
                        error_count += 1
                else:
                    flash(f'不正なデータ形式のキー: {key}', 'danger')
                    error_count += 1
            except ValueError:
                flash(f'在庫数は有効な数値を入力してください。', 'danger')
                error_count += 1
            except Exception as e:
                flash(f'更新中にエラーが発生しました: {e}', 'danger')
                error_count += 1

    if updated_count > 0:
        db.session.commit() # コミットを有効にする場合はコメントを外す
        flash(f'{updated_count} 件の在庫数を更新しました。', 'success')
    if error_count > 0:
        flash(f'{error_count} 件の更新に失敗しました。詳細はメッセージを確認してください。', 'warning')
    elif updated_count == 0 and error_count == 0:
        flash('更新する商品がありませんでした。', 'info')

    return redirect(url_for('stock_input_page', search=search_text))

@app.route('/inventory_square')
def inventory_square_page():
    return render_template('inventory_square.html')

@app.route('/product_detail/<string:goodsid>/<string:colorid>')
def product_detail_page(goodsid,colorid):
    product = db.session.query(Arrival).join(Arrival.goods).filter(
        and_(Arrival.goodsid==goodsid,Arrival.colorid==colorid)
        ).first()
    if not product:
        # If not in Arrival, check Goods table
        good = Goods.query.get(goodsid)
        if good:
            # Create a mock product object
            product = {
                'goodsid': goodsid,
                'colorid': colorid,
                'amount': 0,
                'remark': 'この商品は在庫に未登録です。',
                'fentdt': 'N/A',
                'fupdtedt': 'N/A',
                'goods': good
            }
            # Use a simple dict and access attributes with [] in the template
            # Or convert dict to an object that allows attribute access
            from types import SimpleNamespace
            product = SimpleNamespace(**product)
        else:
            return "<p class=\"text-danger\">商品が見つかりませんでした。</p>"
    return render_template('product_detail.html', product=product,colorid_connect_color=colorid_connect_color)

@app.route('/clear_cache')
def clear_cache_route():
    cache.clear()
    flash('正常に更新されました。','success')
    return redirect(url_for('stock_page'))

@app.route('/setgoods_list')
def setgoods_list_page():
    search_query = request.args.get('search', '')
    sort_by = request.args.get('sort_by', 'goodsid') # Default sort by goodsid
    order = request.args.get('order', 'asc') # Default order asc

    query = SetGoods.query

    if search_query:
        query = query.filter(
            or_(
                SetGoods.goodsid.ilike(f'%{search_query}%'),
                SetGoods.goodsnm.ilike(f'%{search_query}%')
            )
        )

    # Define allowed sort columns
    allowed_sort_columns = {
        'goodsid': SetGoods.goodsid,
        'goodsnm': SetGoods.goodsnm,
        'price': SetGoods.price,
        'fentdt': SetGoods.fentdt,
        'fupdtedt': SetGoods.fupdtedt
    }

    # Get the sort column, default to goodsid if invalid
    sort_column = allowed_sort_columns.get(sort_by, SetGoods.goodsid)

    # Apply sorting
    if order == 'desc':
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    total_count = query.count()
    set_goods = query.all() # .all() after order_by
    return render_template('setgoods_list.html', 
                           set_goods=set_goods, 
                           search_query=search_query, 
                           total_count=total_count,
                           sort_by=sort_by,
                           order=order)

@app.route('/setgoods_input', methods=['GET', 'POST'])
def setgoods_input_page():
    form = SetGoodsForm()
    # 全商品のリストを作成
    all_goods = Goods.query.order_by(Goods.goodsnm).all()
    goods_choices = [(g.goodsid, f"{g.goodsid}: {g.goodsnm}") for g in all_goods]
    
    # JSON形式でテンプレートに渡す
    goods_choices_json = json.dumps(goods_choices or [])

    form.goodsid.choices = [('', '商品を選択してください')] + goods_choices

    for i in range(1, 11):
        field = getattr(form, f'sgid{i}')
        field.choices = [('', '商品を選択しない')] + goods_choices

    # POSTリクエストの場合、バリデーションの前に動的にchoicesを設定
    if request.method == 'POST':
        for i in range(1, 11):
            sgid_data = request.form.get(f'sgid{i}')
            if sgid_data:
                scolorid_field = getattr(form, f'scolorid{i}')
                colors = db.session.query(Color.colorid, Color.colornm).join(Arrival, Color.colorid == Arrival.colorid).filter(Arrival.goodsid == sgid_data).distinct().all()
                scolorid_field.choices = [('', 'カラーを選択しない')] + [(c.colorid, f"{c.colorid}: {c.colornm}") for c in colors]

    if form.validate_on_submit():
        selected_good = Goods.query.get(form.goodsid.data)
        if not selected_good:
            flash('選択された商品IDが見つかりません。', 'danger')
            return redirect(url_for('setgoods_input_page'))
        now = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        
        new_set_good_data = {
            'goodsid': selected_good.goodsid,
            'goodsnm': selected_good.goodsnm,
            'price': selected_good.price,
            'useflg': None,
            'detail': form.detail.data,
            'fentdt': now,
            'fupdtedt': now,
            'fentuser': form.fentuser.data
        }

        for i in range(1, 11):
            new_set_good_data[f'sgid{i}'] = getattr(form, f'sgid{i}').data or None
            new_set_good_data[f'sgdetail{i}'] = getattr(form, f'sgdetail{i}').data or None
            snum_data = getattr(form, f'snum{i}').data
            new_set_good_data[f'snum{i}'] = int(snum_data) if snum_data is not None else 1
            
            if getattr(form, f'scolorid_check{i}').data:
                new_set_good_data[f'scolorid{i}'] = getattr(form, f'scolorid{i}').data or None
            else:
                new_set_good_data[f'scolorid{i}'] = None

        new_set_good = SetGoods(**new_set_good_data)
        
        db.session.add(new_set_good)
        db.session.commit()
        flash('セット商品が正常に登録されました。', 'success')
        return redirect(url_for('setgoods_input_page'))
    elif request.method == 'POST':
        print("エラー内容:",form.errors)
    # 変更点2: Jinja2テンプレート内でgetattr関数を使えるように渡す
    return render_template('setgoods_input.html', form=form, goods_choices_json=goods_choices_json, getattr=getattr)


@app.route('/edit_setgood/<string:setgood_id>', methods=['GET', 'POST'])
def edit_setgood_page(setgood_id):
    setgood = SetGoods.query.get_or_404(setgood_id)
    form = SetGoodsForm(obj=setgood)
    
    all_goods = Goods.query.order_by(Goods.goodsnm).all()
    goods_choices = [(g.goodsid, f"{g.goodsid}: {g.goodsnm}") for g in all_goods]
    goods_choices_json = json.dumps(goods_choices or [])

    form.goodsid.choices = [('', '商品を選択してください')] + goods_choices
    for i in range(1, 11):
        field = getattr(form, f'sgid{i}')
        field.choices = [('', '商品を選択しない')] + goods_choices

    # POSTリクエストの場合、バリデーションの前に動的にchoicesを設定
    if request.method == 'POST':
        for i in range(1, 11):
            sgid_data = request.form.get(f'sgid{i}')
            if sgid_data:
                scolorid_field = getattr(form, f'scolorid{i}')
                colors = db.session.query(Color.colorid, Color.colornm).join(Arrival, Color.colorid == Arrival.colorid).filter(Arrival.goodsid == sgid_data).distinct().all()
                scolorid_field.choices = [('', 'カラーを選択しない')] + [(c.colorid, f"{c.colorid}: {c.colornm}") for c in colors]

    if form.validate_on_submit():
        setgood.fentuser = form.fentuser.data
        setgood.detail = form.detail.data
        setgood.fupdtedt = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        setgood.useflg = '1' if form.useflg.data else None

        for i in range(1, 11):
            setattr(setgood, f'sgid{i}', getattr(form, f'sgid{i}').data or None)
            setattr(setgood, f'sgdetail{i}', getattr(form, f'sgdetail{i}').data or None)
            snum_data = getattr(form, f'snum{i}').data
            setattr(setgood, f'snum{i}', int(snum_data) if snum_data is not None else 1)
            
            if getattr(form, f'scolorid_check{i}').data:
                setattr(setgood, f'scolorid{i}', getattr(form, f'scolorid{i}').data or None)
            else:
                setattr(setgood, f'scolorid{i}', None)

        db.session.commit()
        flash('セット商品が正常に更新されました。', 'success')
        return redirect(url_for('setgoods_list_page'))
    else:
        if request.method == 'POST':
            flash('フォームの送信にエラーが発生しました。再度確認してください。', 'danger')
            print(form.errors)

    if request.method == 'GET':
        form.goodsid.data = setgood.goodsid
        form.fentuser.data = setgood.fentuser
        form.detail.data = setgood.detail
        form.useflg.data = setgood.useflg == '1'

        for i in range(1, 11):
            getattr(form, f'sgid{i}').data = getattr(setgood, f'sgid{i}')
            getattr(form, f'sgdetail{i}').data = getattr(setgood, f'sgdetail{i}')
            getattr(form, f'snum{i}').data = getattr(setgood, f'snum{i}')
            scolorid_val = getattr(setgood, f'scolorid{i}', None)
            if scolorid_val:
                getattr(form, f'scolorid_check{i}').data = True
                getattr(form, f'scolorid{i}').data = scolorid_val

    return render_template('edit_setgood.html', form=form, setgood=setgood, goods_choices_json=goods_choices_json, getattr=getattr)

@app.route('/api/get_colors/<string:goodsid>')
def get_colors(goodsid):
    # 変更点6: API呼び出しのデバッグログを追加
    print(f"--- API: get_colors received request for goodsid: {goodsid} ---")
    colors = db.session.query(Color.colorid, Color.colornm).join(Arrival, Color.colorid == Arrival.colorid).filter(Arrival.goodsid == goodsid).distinct().all()
    print(f"--- Found {len(colors)} colors for this goodsid. ---")
    color_list = [{'id': c.colorid, 'text': f"{c.colorid}: {c.colornm}"} for c in colors]
    print(f"--- Returning color list: {color_list} ---")
    return jsonify(colors=color_list)

@app.route('/api/get_goods_from_arrival')
def get_goods_from_arrival():
    # 変更点7: API呼び出しのデバッグログを追加
    print("--- API: get_goods_from_arrival received request ---")
    goods_in_arrival = db.session.query(Goods.goodsid, Goods.goodsnm).join(Arrival, Goods.goodsid == Arrival.goodsid).distinct().order_by(Goods.goodsnm).all()
    goods_list = [{'id': g.goodsid, 'text': f"{g.goodsid}: {g.goodsnm}"} for g in goods_in_arrival]
    print(f"--- Found {len(goods_list)} goods in arrival. ---")
    return jsonify(goods=goods_list)


@app.route('/delete_setgood/<string:setgood_id>', methods=['POST'])
def delete_setgood(setgood_id):
    setgood = SetGoods.query.get_or_404(setgood_id)
    try:
        db.session.delete(setgood)
        db.session.commit()
        flash('セット商品が正常に削除されました。', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'セット商品の削除中にエラーが発生しました: {e}', 'danger')
    return redirect(url_for('setgoods_list_page'))

@app.route('/delete_order_good/<string:orderid>', methods=['POST'])
def delete_order_good_page(orderid):
    order_good = OrderGoods.query.get_or_404(orderid)
    try:
        db.session.delete(order_good)
        db.session.commit()
        flash(f'注文ID「{orderid}」が正常に削除されました。', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'注文の削除中にエラーが発生しました: {e}', 'danger')
    return redirect(url_for('order_goods_list_page'))


@app.route('/order_goods_list')
def order_goods_list_page():
    search_query = request.args.get('search', '')
    start_date_str = request.args.get('start_date', '')
    end_date_str = request.args.get('end_date', '')
    ship_status = request.args.get('ship_status', 'all')
    date_type = request.args.get('date_type', 'order_date') # デフォルトは注文日

    # Add sort parameters
    page = request.args.get('page', 1, type=int)
    sort_by = request.args.get('sort_by', 'orderdate') # Default sort by orderdate
    order = request.args.get('order', 'desc') # Default order desc

    query = OrderGoods.query

    if search_query:
        query = query.filter(
            or_(
                OrderGoods.goodsid.ilike(f'%{search_query}%'),
                OrderGoods.goodsnm.ilike(f'%{search_query}%')
            )
        )
    
    date_column = OrderGoods.orderdate if date_type == 'order_date' else OrderGoods.shipdate

    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            query = query.filter(date_column >= start_date)
        except (ValueError, TypeError):
            flash('開始日の日付フォーマットが正しくありません。', 'danger')
    
    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            query = query.filter(date_column <= end_date)
        except (ValueError, TypeError):
            flash('終了日の日付フォーマットが正しくありません。', 'danger')

    if ship_status == 'shipped':
        query = query.filter(OrderGoods.shipflg == 1, OrderGoods.deliveredflg == 0)
    elif ship_status == 'unshipped':
        query = query.filter(OrderGoods.shipflg == 0)
    elif ship_status == 'delivered':
        query = query.filter(OrderGoods.shipflg == 1, OrderGoods.deliveredflg == 1)

    # Define allowed sort columns
    allowed_sort_columns = {
        'orderid': OrderGoods.orderid,
        'goodsid': OrderGoods.goodsid,
        'goodsnm': OrderGoods.goodsnm,
        'orderdate': OrderGoods.orderdate,
        'shipdate': OrderGoods.shipdate,
        'delivereddate': OrderGoods.delivereddate,
        'quantity': OrderGoods.quantity,
        'fupdteuser': OrderGoods.fupdteuser
    }

    # Get the sort column, default to orderdate if invalid
    sort_column = allowed_sort_columns.get(sort_by, OrderGoods.orderdate)

    # Apply sorting
    if order == 'desc':
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    total_count = query.count()
    pagination = query.paginate(page=page, per_page=25, error_out=False)
    order_goods = pagination.items
    
    return render_template('order_goods_list.html', 
                            order_goods=order_goods, 
                            pagination=pagination,
                            search_query=search_query, 
                            start_date=start_date_str,
                            end_date=end_date_str,
                            ship_status=ship_status,
                            date_type=date_type,
                            total_count=total_count,
                            sort_by=sort_by,
                            order=order,
                            colorid_connect_color=colorid_connect_color)


@app.route('/order_goods_input', methods=['GET', 'POST'])
def order_goods_input_page():
    form = OrderGoodsForm()
    goods_choices = [(g.goodsid, f"{g.goodsid}: {g.goodsnm}") for g in Goods.query.order_by(Goods.goodsnm).all()]
    form.goodsid.choices = [('', '商品を選択してください')] + goods_choices

    color_choices = [(c.colorid, f"{c.colorid}: {c.colornm}") for c in Color.query.order_by(Color.colornm).all()]
    form.colorid.choices = [('', 'カラーを選択してください')] + color_choices

    if form.validate_on_submit():
        order_date = datetime.now().date()
        order_date_str = order_date.strftime('%Y-%m-%d')
        colorid = form.colorid.data or ''

        # Determine goodsid and goodsnm based on whether it's a sample
        goodsnm_to_save = form.goodsnm.data

        # Generate a unique order ID
        prefix = f"{order_date_str}-{form.goodsid.data}-{colorid}-"
        count = OrderGoods.query.filter(OrderGoods.orderid.like(f"{prefix}%")).count()
        sequence = count + 1
        new_orderid = f"{prefix}{sequence}"

        new_order_good = OrderGoods(
            orderid=new_orderid,
            goodsid=form.goodsid.data,
            goodsnm=goodsnm_to_save,
            colorid=colorid,
            detail=form.detail.data,
            orderdate=order_date,
            quantity=form.quantity.data,
            shipflg=0,  # Default to 0 (unshipped)
            deliveredflg=0, # Default to 0 (undelivered)
            fupdteuser=form.fupdteuser.data
        )
        db.session.add(new_order_good)
        db.session.commit()
        flash(f'注文商品が正常に登録されました。注文ID: {new_orderid}', 'success')
        return redirect(url_for('order_goods_input_page'))

    return render_template('order_goods_input.html', form=form)


@app.route('/shipment', methods=['GET', 'POST'])
def shipment_page():
    form = ShipmentForm()
    min_order_date = db.session.query(func.min(OrderGoods.orderdate)).filter(OrderGoods.shipflg == 0).scalar()
    orders_to_ship = []
    end_date_to_display = request.args.get('end_date')

    if end_date_to_display and min_order_date:
        try:
            end_date_obj = datetime.strptime(end_date_to_display, '%Y-%m-%d').date()
            orders_to_ship = OrderGoods.query.filter(
                OrderGoods.orderdate >= min_order_date,
                OrderGoods.orderdate <= end_date_obj,
                OrderGoods.shipflg == 0
            ).order_by(OrderGoods.orderdate).all()
        except (ValueError, TypeError):
            pass

    if request.method == 'POST':
        if form.validate_on_submit():
            end_date = form.end_date.data
            if min_order_date and end_date < min_order_date:
                flash('出荷日は、最短注文日以降の日付を選択してください。', 'danger')
                return redirect(url_for('shipment_page'))
            return redirect(url_for('shipment_page', end_date=end_date.strftime('%Y-%m-%d')))
        
        elif request.form.get('action') == 'ship':
            order_ids_to_update = request.form.getlist('order_ids')
            end_date_hidden = request.form.get('end_date_hidden')
            if order_ids_to_update:
                # 文字列をdateオブジェクトに変換
                try:
                    ship_date = datetime.strptime(end_date_hidden, '%Y-%m-%d').date()
                    updated_count = OrderGoods.query.filter(
                        OrderGoods.orderid.in_(order_ids_to_update)
                    ).update({'shipflg': 1, 'shipdate': ship_date}, synchronize_session=False)
                    db.session.commit()
                    flash(f'{updated_count}件の注文を出荷済みに更新しました。', 'success')
                except (ValueError, TypeError) as e:
                    flash(f'日付の形式が正しくありません: {e}', 'danger')
            else:
                flash('出荷する注文が選択されていません。', 'warning')
            return redirect(url_for('shipment_page', end_date=end_date_hidden))

    end_date_obj_for_template = None
    if end_date_to_display:
        try:
            end_date_obj_for_template = datetime.strptime(end_date_to_display, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            pass

    return render_template('shipment.html', 
                           form=form, 
                           min_order_date=min_order_date, 
                           end_date=end_date_obj_for_template,
                           orders_to_ship=orders_to_ship)


@app.route('/delivered', methods=['GET', 'POST'])
def delivered_page():
    form = DeliveredForm()
    min_ship_date = db.session.query(func.min(OrderGoods.shipdate)).filter(OrderGoods.shipflg == 1, OrderGoods.deliveredflg == 0).scalar()
    orders_to_deliver = []
    end_date_to_display = request.args.get('end_date')

    if end_date_to_display and min_ship_date:
        try:
            end_date_obj = datetime.strptime(end_date_to_display, '%Y-%m-%d').date()
            orders_to_deliver = OrderGoods.query.filter(
                OrderGoods.shipdate >= min_ship_date,
                OrderGoods.shipdate <= end_date_obj,
                OrderGoods.shipflg == 1,
                OrderGoods.deliveredflg == 0
            ).order_by(OrderGoods.shipdate).all()
        except (ValueError, TypeError):
            pass

    if request.method == 'POST':
        if form.validate_on_submit():
            end_date = form.end_date.data
            if min_ship_date and end_date < min_ship_date:
                flash('配送日は、最短出荷日以降の日付を選択してください。', 'danger')
                return redirect(url_for('delivered_page'))
            return redirect(url_for('delivered_page', end_date=end_date.strftime('%Y-%m-%d')))
        
        elif request.form.get('action') == 'deliver':
            order_ids_to_update = request.form.getlist('order_ids')
            end_date_hidden = request.form.get('end_date_hidden')
            if order_ids_to_update:
                updated_count=delivered_goods_to_count_arrival(order_ids_to_update,end_date_hidden)
                db.session.commit()
                flash(f'{updated_count}件の注文を配送済みに更新しました。', 'success')
            else:
                flash('配送する注文が選択されていません。', 'warning')
            return redirect(url_for('delivered_page', end_date=end_date_hidden))

    end_date_obj_for_template = None
    if end_date_to_display:
        try:
            end_date_obj_for_template = datetime.strptime(end_date_to_display, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            pass

    return render_template('delivered.html', 
                           form=form, 
                           min_ship_date=min_ship_date, 
                           end_date=end_date_obj_for_template,
                           orders_to_deliver=orders_to_deliver,
                           colorid_connect_color=colorid_connect_color)


@app.route('/edit_order_good/<string:orderid>', methods=['GET', 'POST'])
def edit_order_good_page(orderid):
    order_good = OrderGoods.query.get_or_404(orderid)
    form = OrderGoodsForm(obj=order_good)

    goods_choices = [(g.goodsid, f"{g.goodsid}: {g.goodsnm}") for g in Goods.query.order_by(Goods.goodsnm).all()]
    form.goodsid.choices = [('', '商品を選択してください')] + goods_choices

    color_choices = [(c.colorid, f"{c.colorid}: {c.colornm}") for c in Color.query.order_by(Color.colornm).all()]
    form.colorid.choices = [('', 'カラーを選択してください')] + color_choices

    if form.validate_on_submit():
        order_good.goodsid = form.goodsid.data
        order_good.goodsnm = form.goodsnm.data
        order_good.colorid = form.colorid.data
        order_good.detail = form.detail.data
        order_good.quantity = form.quantity.data
        order_good.fupdteuser = form.fupdteuser.data
        
        order_good.shipflg = 1 if form.shipflg.data else 0
        if order_good.shipflg == 1:
            # 出荷フラグがONで、出荷日が入力されていない場合、今日の日付を自動入力
            order_good.shipdate = form.shipdate.data or datetime.now().date()
        else:
            order_good.shipdate = None # 出荷フラグがOFFなら出荷日はNone

        order_good.deliveredflg = 1 if form.deliveredflg.data else 0
        if order_good.deliveredflg == 1:
            order_good.delivereddate = form.delivereddate.data or datetime.now().date()
        else:
            order_good.delivereddate = None

        db.session.commit()
        flash('注文商品が正常に更新されました。', 'success')
        return redirect(url_for('order_goods_list_page'))

    # GETリクエストのためにフォームのデフォルト値を設定
    form.goodsid.data = order_good.goodsid
    form.colorid.data = order_good.colorid
    form.shipflg.data = True if order_good.shipflg == 1 else False
    form.deliveredflg.data = True if order_good.deliveredflg == 1 else False

    return render_template('edit_order_good.html', form=form, order_good=order_good)


@app.route('/sales_search', methods=['GET', 'POST'])
def sales_search_page():
    form = SalesSearchForm()
    sales_records = []
    total_count = 0
    page = request.args.get('page', 1, type=int)

    # Get search parameters from URL query string (for pagination to work)
    auctionid = request.args.get('auctionid', '').strip()
    guestid = request.args.get('guestid', '').strip()
    guestnm = request.args.get('guestnm', '').strip()
    email = request.args.get('email', '').strip()
    tel = request.args.get('tel', '').strip()
    address = request.args.get('address', '').strip()
    goodsid = request.args.get('goodsid', '').strip()
    trackno = request.args.get('trackno', '').strip()
    returnflg = request.args.get('returnflg', '')
    drawingflg = request.args.get('drawingflg', '')
    decisionflg = request.args.get('decisionflg', '')

    # Build query with left join to CustomerInfo for customer name and email search
    # Also join BankAccount and Freight for their names
    query = db.session.query(
        SalesRecord,
        CustomerInfo.guestnm,
        CustomerInfo.email1,
        BankAccount.banknm,
        Freight.freightnm
    ).outerjoin(
        CustomerInfo, SalesRecord.guestid == CustomerInfo.guestid
    ).outerjoin(
        BankAccount, SalesRecord.bankid == BankAccount.bankid
    ).outerjoin(
        Freight, SalesRecord.freightid == Freight.freightid
    )

    has_search_params = False

    # Apply filters based on search parameters
    if auctionid:
        query = query.filter(SalesRecord.auctionid.ilike(f'%{auctionid}%'))
        has_search_params = True

    if guestid:
        query = query.filter(SalesRecord.guestid.ilike(f'%{guestid}%'))
        has_search_params = True

    if guestnm:
        query = query.filter(CustomerInfo.guestnm.ilike(f'%{guestnm}%'))
        has_search_params = True

    if email:
        query = query.filter(
            or_(
                CustomerInfo.email1.ilike(f'%{email}%'),
                CustomerInfo.email2.ilike(f'%{email}%')
            )
        )
        has_search_params = True

    if tel:
        query = query.filter(CustomerInfo.tel.ilike(f'%{tel}%'))
        has_search_params = True

    if address:
        query = query.filter(CustomerInfo.address.ilike(f'%{address}%'))
        has_search_params = True

    if goodsid:
        query = query.filter(SalesRecord.goodsid.ilike(f'%{goodsid}%'))
        has_search_params = True

    if trackno:
        query = query.filter(SalesRecord.trackno.ilike(f'%{trackno}%'))
        has_search_params = True

    if returnflg:
        if returnflg == 'Y':
            query = query.filter(SalesRecord.returnflg == 'Y')
        else:  # returnflg == 'N'
            query = query.filter(or_(SalesRecord.returnflg != 'Y', SalesRecord.returnflg.is_(None)))
        has_search_params = True

    if drawingflg:
        if drawingflg == 'Y':
            query = query.filter(SalesRecord.drawingflg == 'Y')
        else:  # drawingflg == 'N'
            query = query.filter(or_(SalesRecord.drawingflg != 'Y', SalesRecord.drawingflg.is_(None)))
        has_search_params = True

    if decisionflg:
        if decisionflg == '1':
            query = query.filter(SalesRecord.decisionflg == '1')
        else:  # decisionflg == '0'
            query = query.filter(or_(SalesRecord.decisionflg != '1', SalesRecord.decisionflg.is_(None)))
        has_search_params = True
    
    if not(returnflg) and not(drawingflg) and not(decisionflg):
        has_search_params=True

    # Only execute query if at least one search parameter is provided
    if has_search_params:
        total_count = query.count()
        pagination = query.order_by(SalesRecord.fupdtedt.desc()).paginate(
            page=page, per_page=20, error_out=False
        )
        # Extract records and add customer_name, email1, bank_name, and freight_name attributes
        sales_records = []
        for record, customer_name, email1, bank_name, freight_name in pagination.items:
            record.customer_name = customer_name
            record.email1 = email1
            record.bank_name = bank_name
            record.freight_name = freight_name
            sales_records.append(record)
    else:
        pagination = None
        sales_records = []

    # Pre-populate form fields with current search values
    if request.method == 'GET':
        form.auctionid.data = auctionid
        form.guestid.data = guestid
        form.guestnm.data = guestnm
        form.email.data = email
        form.tel.data = tel
        form.address.data = address
        form.goodsid.data = goodsid
        form.trackno.data = trackno
        form.returnflg.data = returnflg
        form.drawingflg.data = drawingflg
        form.decisionflg.data = decisionflg

    # Handle form submission (POST request)
    if request.method == 'POST' and form.validate_on_submit():
        # Redirect to GET request with search parameters in URL
        return redirect(url_for('sales_search_page',
                                auctionid=form.auctionid.data or '',
                                guestid=form.guestid.data or '',
                                guestnm=form.guestnm.data or '',
                                email=form.email.data or '',
                                tel=form.tel.data or '',
                                address=form.address.data or '',
                                goodsid=form.goodsid.data or '',
                                trackno=form.trackno.data or '',
                                returnflg=form.returnflg.data or '',
                                drawingflg=form.drawingflg.data or '',
                                decisionflg=form.decisionflg.data or ''))

    return render_template('sales_search.html',
                          form=form,
                          sales_records=sales_records,
                          total_count=total_count,
                          pagination=pagination,
                          has_search_params=has_search_params)


@app.route('/sales_detail/<string:auctionid>/<string:goodsid>/<string:guestid>', methods=['GET', 'POST'])
def sales_detail_page(auctionid, goodsid, guestid):
    # Fetch sales record with customer info
    sales_record = db.session.query(SalesRecord).filter(
        and_(
            SalesRecord.auctionid == auctionid,
            SalesRecord.goodsid == goodsid,
            SalesRecord.guestid == guestid
        )
    ).first()

    if not sales_record:
        flash('指定された販売記録が見つかりませんでした。', 'danger')
        return redirect(url_for('sales_search_page'))

    edit_mode = request.args.get('edit', 'false') == 'true'

    # Initialize form - use POST data if available, otherwise use obj
    if request.method == 'POST':
        form = SalesEditForm()
    else:
        form = SalesEditForm(obj=sales_record)

    # Populate choices for SelectFields
    # Color choices
    colors = Color.query.all()
    color_choices = [('', '未選択')] + [(c.colorid, f"{c.colorid}: {c.colornm}") for c in colors]
    form.colorid01.choices = color_choices
    form.colorid02.choices = color_choices
    form.colorid03.choices = color_choices
    form.colorid04.choices = color_choices
    form.colorid05.choices = color_choices
    form.colorid06.choices = color_choices

    # Bank choices
    banks = BankAccount.query.all()
    bank_choices = [('', '未選択')] + [(b.bankid, f"{b.bankid}: {b.banknm}") for b in banks]
    form.bankid.choices = bank_choices

    # Freight choices
    freights = Freight.query.all()
    freight_choices = [('', '未選択')] + [(f.freightid, f"{f.freightid}: {f.freightnm}") for f in freights]
    form.freightid.choices = freight_choices

    if request.method == 'POST':
        if form.validate_on_submit():
            # Update editable fields
            sales_record.price = form.price.data
            sales_record.price2 = form.price2.data
            sales_record.amount = form.amount.data

            sales_record.colorid01 = form.colorid01.data
            sales_record.colorid02 = form.colorid02.data
            sales_record.colorid03 = form.colorid03.data
            sales_record.colorid04 = form.colorid04.data
            sales_record.colorid05 = form.colorid05.data
            sales_record.colorid06 = form.colorid06.data

            sales_record.bankid = form.bankid.data
            sales_record.freightid = form.freightid.data
            sales_record.time = form.time.data
            sales_record.trackno = form.trackno.data

            sales_record.remark = form.remark.data
            sales_record.problem = form.problem.data

            sales_record.transmitflg = form.transmitflg.data if form.transmitflg.data else None
            sales_record.answerflg = form.answerflg.data if form.answerflg.data else None
            sales_record.transferflg = form.transferflg.data if form.transferflg.data else None
            sales_record.mailingflg = form.mailingflg.data if form.mailingflg.data else None
            sales_record.mailsflg = form.mailsflg.data if form.mailsflg.data else None
            sales_record.returnflg = form.returnflg.data if form.returnflg.data else None
            sales_record.drawingflg = form.drawingflg.data if form.drawingflg.data else None
            sales_record.decisionflg = form.decisionflg.data if form.decisionflg.data else None

            # Auto-update timestamp
            sales_record.fupdtedt = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

            db.session.commit()
            flash('販売記録が正常に更新されました。', 'success')
            return redirect(url_for('sales_detail_page',
                                    auctionid=auctionid,
                                    goodsid=goodsid,
                                    guestid=guestid))
        else:
            # バリデーションエラーを表示
            flash('入力エラーがあります。', 'danger')
            print("Form errors:", form.errors)
            edit_mode = True

    # Fetch customer info
    customer_info = CustomerInfo.query.filter_by(guestid=guestid).first()

    # Fetch bank and freight info
    bank_info = BankAccount.query.filter_by(bankid=sales_record.bankid).first() if sales_record.bankid else None
    freight_info = Freight.query.filter_by(freightid=sales_record.freightid).first() if sales_record.freightid else None

    return render_template('sales_detail.html',
                          record=sales_record,
                          customer=customer_info,
                          bank=bank_info,
                          freight=freight_info,
                          form=form,
                          edit_mode=edit_mode)



from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, DecimalField, BooleanField, SelectField,IntegerField, DateField
from wtforms.validators import DataRequired, Length, Optional

class SetGoodsForm(FlaskForm):
    goodsid = SelectField('商品ID', validators=[DataRequired()], choices=[])
    useflg = BooleanField('この商品を非表示にする', default=False)
    
    # Loop to create fields for set goods 1 to 10
    for i in range(1, 11):
        # Dynamically create field names
        sgid_name = f'sgid{i}'
        sgdetail_name = f'sgdetail{i}'
        snum_name = f'snum{i}'
        
        # Set validators for the first item
        validators = [DataRequired()] if i == 1 else []

    detail = TextAreaField('詳細')
    fentuser = StringField('登録者', validators=[DataRequired(), Length(max=8)])
    submit = SubmitField('登録')

# クラス定義後にフィールドを追加
for i in range(1, 11):
    setattr(SetGoodsForm, f'sgid{i}', SelectField(f'セット商品ID {i}', validators=[DataRequired()] if i==1 else [Optional()], choices=[]))
    setattr(SetGoodsForm, f'sgdetail{i}', TextAreaField(f'セット商品詳細 {i}'))
    setattr(SetGoodsForm, f'snum{i}', IntegerField(f'数量 {i}', validators=[Optional()], default=1))
    setattr(SetGoodsForm, f'scolorid_check{i}', BooleanField(f'カラーを指定する', default=False))
    setattr(SetGoodsForm, f'scolorid{i}', SelectField(f'カラー {i}', choices=[], validators=[Optional()]))


class OrderGoodsForm(FlaskForm):
    is_sample = BooleanField('サンプル商品',default=False)
    goodsid = SelectField('商品ID', validators=[DataRequired()], choices=[])
    goodsnm = StringField('商品名', validators=[Length(max=255)])
    colorid = SelectField('カラーID', choices=[])
    detail = TextAreaField('詳細', validators=[Length(max=1024)])
    quantity = IntegerField('数量', validators=[DataRequired()])
    shipflg = BooleanField('出荷済み')
    shipdate = DateField('出荷日', validators=[Optional()])
    deliveredflg = BooleanField('配送済み')
    delivereddate = DateField('配送日', validators=[Optional()])
    fupdteuser = StringField('更新者', validators=[DataRequired(), Length(max=20)])
    submit = SubmitField('登録')

class ShipmentForm(FlaskForm):
    end_date = DateField('出荷日', validators=[DataRequired()])
    submit = SubmitField('表示')


class DeliveredForm(FlaskForm):
    end_date = DateField('配送日', validators=[DataRequired()])
    submit = SubmitField('表示')


class SalesSearchForm(FlaskForm):
    auctionid = StringField('オークションID', validators=[Length(max=20)])
    guestid = StringField('顧客ID', validators=[Length(max=40)])
    guestnm = StringField('顧客名', validators=[Length(max=90)])
    email = StringField('メールアドレス', validators=[Length(max=256)])
    tel = StringField('電話番号', validators=[Length(max=50)])
    address = StringField('住所', validators=[Length(max=255)])
    goodsid = StringField('商品ID', validators=[Length(max=20)])
    trackno = StringField('お問い合わせ番号', validators=[Length(max=128)])
    returnflg = SelectField('返品Flag', choices=[('', '全て'), ('Y', '返品あり'), ('N', '返品なし')])
    drawingflg = SelectField('代引きFlag', choices=[('', '全て'), ('Y', '代引きあり'), ('N', '代引きなし')])
    decisionflg = SelectField('元払いFlag', choices=[('', '全て'), ('1', '元払いあり'), ('0', '元払いなし')])
    submit = SubmitField('検索')


class SalesEditForm(FlaskForm):
    # 価格情報
    price = DecimalField('落札価格', places=2, validators=[Optional()])
    price2 = DecimalField('金額変動あり', places=2, validators=[Optional()])
    amount = IntegerField('数量', validators=[Optional()])

    # 商品詳細指定
    colorid01 = SelectField('カラー1', choices=[], validators=[Optional()])
    colorid02 = SelectField('カラー2', choices=[], validators=[Optional()])
    colorid03 = SelectField('カラー3', choices=[], validators=[Optional()])
    colorid04 = SelectField('カラー4', choices=[], validators=[Optional()])
    colorid05 = SelectField('カラー5', choices=[], validators=[Optional()])
    colorid06 = SelectField('カラー6', choices=[], validators=[Optional()])

    # 配送情報
    bankid = SelectField('振込先', choices=[], validators=[Optional()])
    freightid = SelectField('郵送方法', choices=[], validators=[Optional()])
    time = StringField('時間帯指定', validators=[Optional(), Length(max=50)])
    trackno = StringField('お問い合わせ番号', validators=[Optional(), Length(max=128)])

    # 備考
    remark = TextAreaField('備考', validators=[Optional(), Length(max=1024)])
    problem = TextAreaField('会社用-問題ありの備考', validators=[Optional(), Length(max=255)])

    # フラグ（2択: False=None/空白, True='Y'/'1'）
    transmitflg = SelectField('送信済Flag', choices=[('', '未送信'), ('Y', '送信済')])
    answerflg = SelectField('受信済Flag', choices=[('', '未受信'), ('Y', '受信済')])
    transferflg = SelectField('振込済Flag', choices=[('', '未振込'), ('Y', '振込済')])
    mailingflg = SelectField('郵送済Flag', choices=[('', '未郵送'), ('Y', '郵送済')])
    mailsflg = SelectField('郵送後送信済Flag', choices=[('', '未送信'), ('Y', '送信済')])
    returnflg = SelectField('返品Flag', choices=[('', '返品なし'), ('Y', '返品あり')])
    drawingflg = SelectField('代引きFlag', choices=[('', '代引きなし'), ('Y', '代引きあり')])
    decisionflg = SelectField('元払いFlag', choices=[('', '元払いなし'), ('1', '元払いあり')])

    submit = SubmitField('更新')

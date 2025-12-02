from __init__ import db, metadata, engine, is_sqlite
from sqlalchemy import Column, String, Integer, Numeric, Date, ForeignKey, func
from sqlalchemy.orm import relationship

# SQLAlchemy(データベースの管理を安易)によってカラムを作れる。
class Arrival(db.Model):
    __tablename__ = "入荷情報"
    __table_args__ = {} if is_sqlite else {'schema': 'JT'} 

    goodsid = Column(String(20), ForeignKey('商品.goodsid' if is_sqlite else 'JT.商品.goodsid'), primary_key=True, nullable=False)
    colorid = Column(String(5), primary_key=True, nullable=False)
    amount = Column(Integer)  # NUMBER(5,0) → Integer
    price = Column(Numeric(18, 6))
    freightprice = Column(Numeric(18, 6))
    earprice = Column(Numeric(18, 6))
    lenprice = Column(Numeric(18, 6))
    sold = Column(Integer)  # NUMBER(5,0)
    remark = Column(String(255))
    fentdt = Column(String(19))  # 文字列で扱うならString、もし日付ならDateTimeに変える
    fentusr = Column(String(8))
    fupdtedt = Column(String(19))#更新日時
    fupdteusr = Column(String(8))
    fupdteprg = Column(String(150))
    cache = Column(String(100))
    material = Column(String(45))
    ftrndate = Column(Date, nullable=False)

    goods = relationship("Goods",primaryjoin="Arrival.goodsid == Goods.goodsid")
    #relationshipとForeignKeyの違い。
    #relationshipは、Python上で簡単に参照データを取り出すことができる関数
    #ForeignKeyは、SQLachlemyでデーブルの特定の列同士でつながりを持たせることができる
    #salesrecord = relationship("SalesRecord",foreign_keys="JT.販売記録.goodsid",primaryjoin="Arrival.goodsid == SalesRecord.goodsid")

    def __repr__(self):
        return f"<Nyuka(goodsid={self.goodsid}, colorid={self.colorid})>"

    
    
class Goods(db.Model):  # 「商品」の読みをローマ字で
    __tablename__ = "商品"
    __table_args__ = {} if is_sqlite else {'schema': 'JT'}

    goodsid = Column(String(20), primary_key=True, nullable=False)
    goodsnm = Column(String(255))
    title = Column(String(255))
    price = Column(Numeric(18, 6))
    currentprice = Column(Numeric(18, 6))
    htpmark = Column(String(10))
    mailfee = Column(Numeric(18, 6))
    color = Column(String(1))
    detail = Column(String(1024))
    fentdt = Column(String(19))
    fentusr = Column(String(8))
    fupdtedt = Column(String(19))
    fupdteusr = Column(String(8))
    fupdteprg = Column(String(150))
    useflg = Column(String(1))

    def __repr__(self):
        return f"<Shohin(goodsid={self.goodsid}, goodsnm={self.goodsnm})>"
    
class SalesRecord(db.Model):
    __tablename__ = "販売記録"
    __table_args__ = {} if is_sqlite else {"schema": "JT"}

    auctionid = Column(String(20), primary_key=True, nullable=False)
    goodsid = Column(String(20), primary_key=True, nullable=False)
    guestid = Column(String(40), primary_key=True, nullable=False)
    belong = Column(String(128))
    price = Column(Numeric(18, 6))
    price2 = Column(Numeric(18, 6))
    noteworthy = Column(Numeric(18, 6))
    amount = Column(Integer)
    colorid01 = Column(String(20))
    colorid02 = Column(String(5))
    colorid03 = Column(String(5))
    colorid04 = Column(String(5))
    colorid05 = Column(String(5))
    colorid06 = Column(String(5))
    transmitflg = Column(String(1))
    bankid = Column(String(30))
    transferflg = Column(String(1))
    mailingflg = Column(String(1))
    freightid = Column(String(10))
    time = Column(String(50))
    answerflg = Column(String(1))
    mailsflg = Column(String(1))
    trackno = Column(String(128))
    returnflg = Column(String(1))
    drawingflg = Column(String(1))
    remark = Column(String(1024))
    problem = Column(String(255))
    fentdt = Column(String(19))
    fentusr = Column(String(8))
    fupdtedt = Column(String(19))#更新日時
    fupdteusr = Column(String(8))
    fupdteprg = Column(String(150))
    cache = Column(String(100))
    decisionflg = Column(String(1))
    appointno = Column(String(30))
    appointadd = Column(String(255))
    appointna = Column(String(45))
    appointtel = Column(String(20))

class Color(db.Model):
    __tablename__ = 'COLOR'
    __table_args__ = {} if is_sqlite else {'schema': 'JT'}  # スキーマ指定

    colorid = Column(String(5), primary_key=True, nullable=False)
    colornm = Column(String(20))
    fentdt = Column(String(1024))  # 本来は DateTime 型が望ましい
    fentusr = Column(String(8))
    fupdtedt = Column(String(19))  # 同上
    fupdteusr = Column(String(8))
    fupdteprg = Column(String(150))

class CustomerInfo(db.Model):
    __tablename__ = '顧客情報'
    __table_args__ = {} if is_sqlite else {'schema': 'JT'}

    guestid = Column("GUESTID", String(40), primary_key=True)
    guestnm = Column("GUESTNM", String(90))
    email1 = Column("EMAIL1", String(256))
    email2 = Column("EMAIL2", String(256))
    addressno = Column("ADDRESSNO", String(30))
    address = Column("ADDRESS", String(255))
    tel = Column("TELNO", String(50))
    kadakana = Column("KADAKANA", String(90))
    fentdt = Column("FENTDT", String(19))        
    fentusr = Column("FENTUSR", String(8))
    fupdtedt = Column("FUPDTEDT", String(19))    
    fupdteusr = Column("FUPDTEUSR", String(8))
    fupdteprg = Column("FUPDTEPRG", String(150))

class SetGoods(db.Model):
    __tablename__ = 'セット商品'
    __table_args__ = {} if is_sqlite else {'schema': 'JT'}

    goodsid = Column(String(20), ForeignKey('商品.goodsid' if is_sqlite else 'JT.商品.goodsid'), primary_key=True)
    goodsnm = db.Column('GOODSNM', db.String(255), nullable=False)
    price = db.Column('PRICE', db.Numeric(18, 6))
    useflg = db.Column('USEFLG', db.String(1))

    # セット商品 1～10
    sgid1 = db.Column('SGID1', db.String(20), nullable=False)
    sgdetail1 = db.Column('SGDETAIL1', db.String(1024))
    snum1 = db.Column('SNUM1', db.Integer)
    scolorid1 = db.Column('SCOLORID1', db.String(20))

    sgid2 = db.Column('SGID2', db.String(20))
    sgdetail2 = db.Column('SGDETAIL2', db.String(1024))
    snum2 = db.Column('SNUM2', db.Integer)
    scolorid2 = db.Column('SCOLORID2', db.String(20))

    sgid3 = db.Column('SGID3', db.String(20))
    sgdetail3 = db.Column('SGDETAIL3', db.String(1024))
    snum3 = db.Column('SNUM3', db.Integer)
    scolorid3 = db.Column('SCOLORID3', db.String(20))

    sgid4 = db.Column('SGID4', db.String(20))
    sgdetail4 = db.Column('SGDETAIL4', db.String(1024))
    snum4 = db.Column('SNUM4', db.Integer)
    scolorid4 = db.Column('SCOLORID4', db.String(20))

    sgid5 = db.Column('SGID5', db.String(20))
    sgdetail5 = db.Column('SGDETAIL5', db.String(1024))
    snum5 = db.Column('SNUM5', db.Integer)
    scolorid5 = db.Column('SCOLORID5', db.String(20))

    sgid6 = db.Column('SGID6', db.String(20))
    sgdetail6 = db.Column('SGDETAIL6', db.String(1024))
    snum6 = db.Column('SNUM6', db.Integer)
    scolorid6 = db.Column('SCOLORID6', db.String(20))

    sgid7 = db.Column('SGID7', db.String(20))
    sgdetail7 = db.Column('SGDETAIL7', db.String(1024))
    snum7 = db.Column('SNUM7', db.Integer)
    scolorid7 = db.Column('SCOLORID7', db.String(20))

    sgid8 = db.Column('SGID8', db.String(20))
    sgdetail8 = db.Column('SGDETAIL8', db.String(1024))
    snum8 = db.Column('SNUM8', db.Integer)
    scolorid8 = db.Column('SCOLORID8', db.String(20))

    sgid9 = db.Column('SGID9', db.String(20))
    sgdetail9 = db.Column('SGDETAIL9', db.String(1024))
    snum9 = db.Column('SNUM9', db.Integer)
    scolorid9 = db.Column('SCOLORID9', db.String(20))

    sgid10 = db.Column('SGID10', db.String(20))
    sgdetail10 = db.Column('SGDETAIL10', db.String(1024))
    snum10 = db.Column('SNUM10', db.Integer)
    scolorid10 = db.Column('SCOLORID10', db.String(20))

    detail = db.Column('DETAIL', db.String(1024))
    fentdt = db.Column('FENTDT', db.String(19), nullable=False)
    fupdtedt = db.Column('FUPDTEDT', db.String(19), nullable=False)
    fentuser = db.Column('FENTUSER', db.String(8), nullable=False)

    goods = relationship("Goods", primaryjoin="SetGoods.goodsid == Goods.goodsid")

    def __repr__(self):
        return f"<SetGoods(goodsid={self.goodsid}, goodsnm={self.goodsnm})>"

class OrderGoods(db.Model):
    __tablename__ = "注文商品"
    __table_args__ = {} if is_sqlite else {'schema': 'JT'}

    orderid = Column(String(64), primary_key=True, nullable=False)
    goodsid = Column(String(20), ForeignKey("商品.goodsid" if is_sqlite else "JT.商品.goodsid"))
    goodsnm = Column(String(255))
    colorid = Column(String(20), ForeignKey("COLOR.colorid" if is_sqlite else "JT.COLOR.colorid"))
    detail = Column(String(1024))
    orderdate = Column(Date)
    shipdate = Column(Date)
    quantity = Column(Numeric(precision=38, scale=0))
    shipflg = Column(Numeric(precision=38, scale=0))
    fupdteuser = Column(String(20))
    deliveredflg=Column(Numeric(precision=1, scale=0))
    delivereddate=Column(Date)

class BankAccount(db.Model):
    __tablename__ = "振込み先"
    __table_args__ = {} if is_sqlite else {'schema': 'JT'}

    bankid = Column(String(30), primary_key=True, nullable=False)
    banknm = Column(String(255))
    fee = Column(Numeric(precision=18, scale=6))
    remark = Column(String(255))
    fentdt = Column(String(19))
    fentusr = Column(String(8))
    fupdtedt = Column(String(19))
    fupdteusr = Column(String(8))
    fupdteprg = Column(String(150))

class Freight(db.Model):
    __tablename__ = "郵送方法"
    __table_args__ = {} if is_sqlite else {'schema': 'JT'}

    freightid = Column(String(10), primary_key=True, nullable=False)
    freightnm = Column(String(45))
    fee = Column(Numeric(precision=18, scale=6))
    remark = Column(String(255))
    fentdt = Column(String(19))
    fentusr = Column(String(8))
    fupdtedt = Column(String(19))
    fupdteusr = Column(String(8))
    fupdteprg = Column(String(150))


import datetime
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date, Float, PrimaryKeyConstraint
from sqlalchemy.orm import sessionmaker

Base = declarative_base() #生成一个SqlORM 基类
engine = create_engine("mysql+pymysql://root:123456@127.0.0.1:3306/trade", echo=True)
SessionCls = sessionmaker(bind=engine)
#bind绑定

#echo如果为True，那么当他执行整个代码的数据库的时候会显示过程
#创建一个类继承Base基类
class Kdata(Base):
    #表名为Kdata
    __tablename__ = 'Kdatas'
    #表结构
    #primary_key等于主键
    #unique唯一
    #nullable非空
    date = Column(Date, nullable=False)
    code = Column(String(64), nullable=False)
    close = Column(Float, default=-1.0, nullable=False)
    kdata_pk = PrimaryKeyConstraint(date, code)


Base.metadata.create_all(engine) #创建所有表结构

if __name__ == '__main__':
    #创建与数据库的会话session class
    #注意,这里返回给session的是个class,不是实例
    session = SessionCls()
    #插入字段
    h1 = Kdata(date=datetime.datetime.strptime("2017-07-06", '%Y-%m-%d').date(), code='sh.600000', close=100)
    h2 = Kdata(date=datetime.datetime.strptime("2017-07-07", '%Y-%m-%d').date(), code='sh.600000', close=101)
    h3 = Kdata(date=datetime.datetime.strptime("2017-07-08", '%Y-%m-%d').date(), code='sh.600000', close=102)
    #添加一个
    #session.add(h3)
    #可以添加多个字段
    session.add_all([h1, h2, h3])
    #修改字段名字,只要没提交,此时修改也没问题
    #h2.hostname = 'ubuntu_test'
    #支持数据回滚
    #session.rollback()
    #提交
    session.commit()


#class Kdata(Base):

#    __tablename__ = 'kdatas'
    #primary_key等于主键
    #unique唯一
    #nullable非空
#    id = Column(Integer, primary_key=True,autoincrement=True)
#    hostname = Column(String(64),unique=True,nullable=False)
#    ip_addr = Column(String(128),unique=True,nullable=False)
#    port = Column(Integer,default=22)

#    def __init__(self, date, code, close):
#        self.date = date #datetime.datetime.now().date()
#        self.code = code #""
#        self.close = close #0.0

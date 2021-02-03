from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column,String,Integer,PrimaryKeyConstraint


Base = declarative_base()

class NER(Base): #继承生成的orm基类
    __tablename__ = "NER" #表名
    id = Column(Integer,primary_key=True, autoincrement=True)
    article_id = Column(String(32))
    sen_id = Column(Integer)
    NER_id = Column(Integer)
    begin = Column(Integer)
    end = Column(Integer)
    term = Column(String(64))
    cui = Column(String(64))
    cui_type = Column(String(64))
    is_structure = Column(Integer)
    is_title = Column(Integer)

class NER_ORM:
    def __init__(self,base):
        self.path = "mysql+pymysql://root:@127.0.0.1:3306/relation_extraction?charset=utf8"
        self.engine = create_engine(self.path,encoding="utf-8")
        self.DBSession = sessionmaker(bind=self.engine)
        if base == None:
            self.Base = declarative_base()     
        else:
            self.Base = base


    def CreateTable(self):
         self.Base.metadata.create_all(self.engine)

    def Insert(self,arg):
        session = self.DBSession()
        new_ner = NER(article_id=arg[0],\
                      sen_id=arg[1],\
                      NER_id=arg[2],\
                      begin=arg[3],
                      end=arg[4],
                      term=arg[5],
                      cui=arg[6],
                      cui_type=arg[7],
                      is_structure=arg[8],
                      is_title=arg[9])
        session.add(new_ner)
        session.commit()
        session.close()

if __name__ == "__main__":
    l = ["100002",23,1,9,20,"term","cui","cui_type",0,1]
    ner_orm = NER_ORM(Base)
    ner_orm.CreateTable()
    ner_orm.Insert(l)

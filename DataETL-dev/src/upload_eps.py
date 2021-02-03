import pandas as pd
import pymysql
from tqdm import tqdm


# df = pd.read_csv("../data/entity_pairs_0303.txt", sep='|')

# db = pymysql.connect(host='127.0.0.1', user='root', password='')
# with db:
#     cur = db.cursor()
#     cur.execute("use umls0;")
#     cur.execute("create table new_eps( "
#                 "e1 VARCHAR(255) NOT NULL,"
#                 "cui1 VARCHAR(255) NOT NULL,"
#                 "e2 VARCHAR(255) NOT NULL,"
#                 "cui2 VARCHAR(255) NOT NULL"
#                 ") ;")
#     for idx, row in df.iterrows():
#         data = [row[0], row[1], row[2], row[3]]
#         sql = " insert into new_eps(e1, cui1, e2, cui2) values(%s,%s,%s,%s);"
#         try:
#             cur.execute(sql, data)
#         except:
#             print("Wrong!")
#             print(data)



df = pd.read_csv("../data/curated_cuis.txt", sep='|', header=None)
db = pymysql.connect(host='127.0.0.1', user='root', password='')
with db:
    cur = db.cursor()
    cur.execute("use umls0;")
    cur.execute("create table curated_cuis("
                "cui CHAR(8) NOT NULL,"
                "type CHAR(4) NOT NULL,"
                "semi_type CHAR(64) NOT NULL,"
                "primary key(cui)"
                ") ;")
    for idx, row in tqdm(df.iterrows(), total=df.shape[0]):
        data = [row[0], row[1], row[2]]
        sql = " insert into curated_cuis(cui, type, semi_type) values(%s,%s,%s);"
        try:
            cur.execute(sql, data)
        except:
            print("Wrong!")
            print(data)
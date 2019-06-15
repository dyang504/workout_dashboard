import pandas as pd
from sqlalchemy import create_engine

# TODO
# refactor functions to pyinvoke task

# df = pd.read_csv('strong.csv')
# df['id'] = df['日期'].astype(str) + \
#            df['运动名称'].astype(str) + \
#            df['设置顺序'].astype(str)
# df['id'] = df['id'].replace('[\s+|\-|(|)|:]', '', regex=True)


def fetch_data(q, conn):
    return pd.read_sql(sql=q, con=conn)


conn = create_engine('sqlite:///./train_items.db')

# df.to_sql('train_record',conn)


def query_exist_data_in_db(conn):
    q = 'SELECT * FROM train_record'
    return fetch_data(q, conn)


def handle_new_data(path, conn):
    exist_data = query_exist_data_in_db(conn)
    del exist_data['index']
    new_data = pd.read_csv(path)
    new_data['id'] = new_data['日期'].astype(str) + new_data['运动名称'].astype(
        str) + new_data['设置顺序'].astype(str)
    new_data['id'] = new_data['id'].replace(r'[\s+|\-|(|)|:]', '', regex=True)
    diff_data = pd.concat([exist_data, new_data]).drop_duplicates(keep=False)
    return diff_data


# handle_new_data('strong.csv',conn).to_csv('diff.csv',index=None)


def update_data(path, conn):
    df = pd.read_csv(path)
    df.to_sql('train_record', conn, if_exists='append')


# update_data('diff.csv', conn)


def query_meter(conn):
    q = '''
        SELECT  AVG(Avg_Left_Weight/Avg_Repeats)  AS Intensity
        FROM (SELECT "运动名称",
                SUM("次") / count("日期") AS "Avg_Repeats",
                SUM("重量") / count("日期") AS "Avg_Left_Weight"
            FROM train_record
            WHERE "次" > 0 AND "重量" > 0
            GROUP BY "运动名称"
            ORDER BY sum("次") DESC) 
    '''
    return pd.read_sql(q, conn)


def query_meter_easy(conn):
    q = '''
        SELECT  AVG("重量") / AVG("次")
            FROM train_record
            WHERE "次" > 0 AND "重量" > 0
          
    '''
    return pd.read_sql(q, conn)


print(query_meter(conn))
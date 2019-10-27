import pandas as pd
from sqlalchemy import create_engine

#This script is dealing with database creation and update

# TODO
# refactor functions to pyinvoke task

conn = create_engine('sqlite:///./train_items.db')

def create_database(connection):
    df = pd.read_csv('strong.csv')
    df['id'] = df['日期'].astype(str) + \
               df['运动名称'].astype(str) + \
               df['设置顺序'].astype(str)
    df['id'] = df['id'].replace('[\s+|\-|(|)|:]', '', regex=True)
    df.to_sql('train_record',conn)


#eg: update_data('weightlifting_721_workouts.csv', conn)
def update_data(path, conn):
    df = pd.read_csv(path)
    df.to_sql('train_record', conn, if_exists='append')


def fetch_data(q, conn):
    return pd.read_sql(sql=q, con=conn)


def query_exist_data_in_db(conn):
    q = 'SELECT * FROM train_record'
    return fetch_data(q, conn)

#eg: handle_new_data('strong.csv',conn).to_csv('diff.csv',index=None)
def handle_new_data(path, conn):
    exist_data = query_exist_data_in_db(conn)
    del exist_data['index']
    new_data = pd.read_csv(path)
    new_data['id'] = new_data['日期'].astype(str) + new_data['运动名称'].astype(
        str) + new_data['设置顺序'].astype(str)
    new_data['id'] = new_data['id'].replace(r'[\s+|\-|(|)|:]', '', regex=True)
    diff_data = pd.concat([exist_data, new_data]).drop_duplicates(keep=False)
    return diff_data
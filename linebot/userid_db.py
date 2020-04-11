from sqlalchemy import create_engine
import psycopg2
import psycopg2.extras
import os

# 入力されたSQL文を用いてselectを行い,リストを返却する.
def get_userid_list(sql):
    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute (sql)
            results = cur.fetchall()
    return results

# 入力されたSQL文でDBを操作する
def operation_db(sql):
    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute (sql)

# DBと接続する
def get_connection():
    DATABASE_URL = os.environ.get('DATABASE_URL')
    return psycopg2.connect(DATABASE_URL)


# 渡されたuseridをDBから削除する
def del_userid(userid):
    sql_delete = "delete from userinfo where userid='{userid}'"

    return "ok"


def add_userid(userid):
    DATABASE_URL = os.environ("DATABASE_URL")
    engine = create_engine(DATABASE_URL)
    return "ok"


def search_userid(user_major):
    sql_search = "select * from userinfo where department '%{user_major}%'"
    target_ids = get_userid_list(sql_search)


    return target_ids


if __name__ == "__main__":
    # 以下を手動実行して最初にテーブルを作成する
    data = {"department": ["学部"],
            "subject": ["学科"],
            "userid": ["1234567890"]}
    userid_df = pd.DataFrame(data)
    engine = create_engine("postgres://ohpuvdblvbaowf:df2232602d6697a46a7968aa12ffc67b4bc885fc15b31133839661c71e139cf8@ec2-50-17-21-170.compute-1.amazonaws.com:5432/d3m1hku7dh4kt8")
    userid_df.to_sql("userinfo", engine, if_exists="replace", index=False)

    print("jobs!")
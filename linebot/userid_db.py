from sqlalchemy import create_engine
import psycopg2
import psycopg2.extras
import os

# 入力されたSQL文を用いてselectを行い,指定されたユーザー情報のリストを返却する.
def get_userinfo_list(sql):
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
    sql_delete = f"delete from userinfo where userid='{userid}'"
    operation_db(sql_delete)

# 渡されたユーザ情報をDBに登録する
def add_userid(department, subject, userid):
    sql_add = f"insert into userinfo (department, subject, userid) values ('{department}', '{subject}', '{userid}')"
    operation_db(sql_add)

# 渡された所属のuseridをリストとして返却
def search_userid(user_major, subject=False):
    if user_major == "全学生向け":
        sql_search = "select userid from userinfo" #全行のuseridのリストを取得
    else:
        if subject:
            sql_search = f"select userid from userinfo where subject='{user_major}'" # subject列がuser_majorである行のuseridのリストを取得
        else:
            sql_search = f"select userid from userinfo where department='{user_major}'" # department列がuser_majorである行のuseridのリストを取得
    target_ids = get_userinfo_list(sql_search)
    return target_ids

# 渡されたuseridのdepartmentを返却（subjectには未対応）
def get_usermajor(userid):
    sql_search = f"select department from userinfo where userid='{userid}'"
    user_major = get_userinfo_list(sql_search)
    return user_major[0][0]


if __name__ == "__main__":
    print("jobs!")
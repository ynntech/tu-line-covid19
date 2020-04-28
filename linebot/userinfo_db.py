import psycopg2
import psycopg2.extras
import os


class DataBase:
    def __init__(self):
        self.database_url = os.environ.get('DATABASE_URL')

    def get_info_list(self, sql):
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute (sql)
                results = cur.fetchall()
        return results

    def execute_sql(self, sql):
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute (sql)
    
    def get_connection(self):
        return psycopg2.connect(self.database_url)


# ユーザ情報を管理するクラス
class User_DB(DataBase):
    # 渡されたuseridをDBから削除する
    def del_userinfo(self, userid):
        sql_delete = f"delete from userinfo where userid='{userid}'"
        self.execute_sql(sql_delete)

    # 渡されたユーザ情報をDBに登録する
    def add_usermajor(self, department, subject, userid, grade):
        sql_add_major = f"insert into userinfo (department, subject, userid, grade) values ('{department}','{subject}','{userid}','{grade}')"
        self.execute_sql(sql_add_major)

    # 渡されたuseridのdepartmentを返却（subjectには未対応）
    def get_usermajor(self, userid):
        sql_search = f"select department from userinfo where userid='{userid}'"
        user_major = self.get_info_list(sql_search)
        if not user_major: # ユーザが所属登録していないときはFalseを返す
            return False
        return user_major[0][0]

    # 渡されたuseridのgradeを返却（subjectには未対応）
    def get_usergrade(self, userid):
        sql_search = f"select grade from userinfo where userid='{userid}'"
        user_grade = self.get_info_list(sql_search)
        if not user_grade: # ユーザが所属登録していないときはFalseを返す
            return False
        return user_grade[0][0]

    # アンケート結果をDBに格納
    def taburate_survey(self, userid, ans):
        sql_taburate = f"update userinfo set grade='{ans}' where userid='{userid}'"
        self.execute_sql(sql_taburate)



if __name__ == "__main__":
    print("jobs!")

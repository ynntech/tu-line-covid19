from linebot import LineBotApi
from linebot.models import TextSendMessage
from linebot.exceptions import LineBotApiError
import os
from userinfo_db import DataBase

class Push_Message(DataBase):
    def __init__(self):
        super().__init__()
        self.line_channel_access_token = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
        self.line_bot_api = LineBotApi(self.line_channel_access_token)

    # 渡された所属のuseridをリストとして返却
    def search_userid(self, user_major, subject=False):
        if user_major == "全学生向け":
            sql_search = "select userid from userinfo" #全行のuseridのリストを取得
        elif user_major == "全学教育":
            sql_search = "select userid from userinfo where grade='1' or grade='2'" # 学部生のみのuseridを取得
        else:
            if subject:
                sql_search = f"select userid from userinfo where subject='{user_major}'" # subject列がuser_majorである行のuseridのリストを取得
            else:
                sql_search = f"select userid from userinfo where department='{user_major}'" # department列がuser_majorである行のuseridのリストを取得
        target_ids = self.get_info_list(sql_search)
        return target_ids

    def push_message(self, message, user_majors, subject=False):
        """
        ==Parameters==
            message(str)      : ユーザに送りたいメッセージ 
            user_majors(list)   : メッセージを送りたい学部の配列（後々学科まで細分化するかも）
            subject(bool)     : Trueのときuser_majorに学科指定
        ==Return==
            None
        """
        for user_major in user_majors: #学部，研究科がリストで渡されるため対応
            if subject: # subjectがTrueのときは学科で送信先のユーザを指定
                target_ids = self.search_userid(user_major, True) #対象学科のuseridのリストを取得
            else:
                target_ids = self.search_userid(user_major) # 対象学部、または全てのuseridのリストを取得
            for userid in target_ids:
                try:                            #メッセージを送信したい相手のIDを入力
                    self.line_bot_api.push_message(userid[0], TextSendMessage(text=message))
                except LineBotApiError as e:
                    print("error") #DBの1列目にダミーのuseridがあるので全学生向けにpushするたびに一回エラーが発生する


if __name__ == "__main__":
    pm = Push_Message()
    pm.push_message("新着情報があります。\n公式サイトもご確認ください。\nhttps://www.bureau.tohoku.ac.jp/covid19BCP/index.html\n===============\n《2020/04/28》\n【お知らせ】東北大学緊急学生支援パッケージ〜Wi-Fiルーターの貸与について〜（申請締切：4月30日(木) 12:00まで）\nhttps://www.bureau.tohoku.ac.jp/covid19BCP/student.html#wi-fi\n《2020/04/27》\n学生のみなさんへ（東北大学緊急学生支援パッケージ～オンライン学習のためのネット環境支援について～）\nhttp://www.tohoku.ac.jp/japanese/2020/04/news20200427-01.html\n《2020/04/27》\n【予告】オンラインによる進学説明会・相談会、入試説明会の開催について\nhttps://www.tohoku.ac.jp/japanese/2020/04/news20200427-02.html",["全学教育"])

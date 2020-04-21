from linebot import LineBotApi
from linebot.models import TextSendMessage
from linebot.exceptions import LineBotApiError
import os
from userid_db import DataBase

class Push_Message(DataBase):
    def __init__(self):
        self.line_channel_access_token = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
        self.line_bot_api = LineBotApi(self.line_channel_access_token)

    # 渡された所属のuseridをリストとして返却
    def search_userid(self, user_major, subject=False):
        if user_major == "全学生向け":
            sql_search = "select userid from userinfo" #全行のuseridのリストを取得
        else:
            if subject:
                sql_search = f"select userid from userinfo where subject='{user_major}'" # subject列がuser_majorである行のuseridのリストを取得
            else:
                sql_search = f"select userid from userinfo where department='{user_major}'" # department列がuser_majorである行のuseridのリストを取得
        target_ids = get_userinfo_list(sql_search)
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
    push_message("更新されました\nhttps://www.eng.tohoku.ac.jp/news/detail-,-id,1561.html", "理学部")

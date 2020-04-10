from linebot import LineBotApi
from linebot.models import TextSendMessage
from linebot.exceptions import LineBotApiError
import os
import pandas as pd

LINE_CHANNEL_ACCESS_TOKEN = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)

def push_message(message, user_majors, subject=False):
    """
    ==Parameters==
        message(str)      : ユーザに送りたいメッセージ 
        user_major(str)   : メッセージを送りたい学部（後々学科まで細分化するかも）
        subject(bool)     : Trueのときuser_majorに学科指定
    ==Return==
        None
    """
    userid_df = pd.read_csv("userid.csv", encoding="cp932")
    for user_major in user_majors: #学部，研究科がリストで渡されるため対応
        if user_major == "全学生向け":
            target_ids = userid_df["userid"]
        else:
            if subject: # subjectがTrueのときは学科で送信先のユーザを指定
                key_major = "subject"
            else:
                key_major = "department"
            target_ids = userid_df.loc[userid_df[key_major]==user_major]["user_id"] #対象学部のuseridのリストを取得

        for userid in target_ids:
            try:                            #メッセージを送信したい相手のIDを入力
                line_bot_api.push_message(userid, TextSendMessage(text=message))
            except LineBotApiError as e:
                print("error!")


if __name__ == "__main__":
    push_message("更新されました\nhttps://www.eng.tohoku.ac.jp/news/detail-,-id,1561.html", "理学部")
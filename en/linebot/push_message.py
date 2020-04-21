from linebot import LineBotApi
from linebot.models import TextSendMessage
from linebot.exceptions import LineBotApiError
import os
from userid_db import search_userid

LINE_CHANNEL_ACCESS_TOKEN = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)

def push_message(message, user_majors, subject=False):
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
            target_ids = search_userid(user_major, True) #対象学科のuseridのリストを取得
        else:
            target_ids = search_userid(user_major) # 対象学部、または全てのuseridのリストを取得
        for userid in target_ids:
            try:                            #メッセージを送信したい相手のIDを入力
                line_bot_api.push_message(userid[0], TextSendMessage(text=message))
            except LineBotApiError as e:
                print("error") #DBの1列目にダミーのuseridがあるので全学生向けにpushするたびに一回エラーが発生する


if __name__ == "__main__":
    push_message("Updated!\nhttps://www.eng.tohoku.ac.jp/news/detail-,-id,1561.html", "理学部")

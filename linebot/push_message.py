from linebot import LineBotApi
from linebot.models import TextSendMessage
from linebot.exceptions import LineBotApiError
import os
import pandas as pd
from userid_db import search_userid

LINE_CHANNEL_ACCESS_TOKEN = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)

def push_message(message, user_majors, subject=False):
    """
    ==Parameters==
        message(str)      : ユーザに送りたいメッセージ 
        user_major(list)   : メッセージを送りたい学部の配列（後々学科まで細分化するかも）
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
                line_bot_api.push_message(userid, TextSendMessage(text=message))
            except LineBotApiError as e:
                print("error!")


if __name__ == "__main__":
    push_message("更新されました\nhttps://www.eng.tohoku.ac.jp/news/detail-,-id,1561.html", "理学部")
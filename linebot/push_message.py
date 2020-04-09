from linebot import LineBotApi
from linebot.models import TextSendMessage
from linebot.exceptions import LineBotApiError
import os
import pandas as pd

LINE_CHANNEL_ACCESS_TOKEN = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)

def push_message(message, major):
    """
    ==Parameters==
        message(str) : ユーザに送りたいメッセージ 
        major(str)   : メッセージを送りたい学部（後々学科まで細分化するかも）
    ==Return==
        None
    """
    userid_df = pd.read_csv("userid.csv", encoding="cp932")
    target_ids = userid_df.loc[userid_df["department"]==major]["user_id"] #対象学部のuseridのリストを取得

    for userid in target_ids:
        try:                            #メッセージを送信したい相手のIDを入力
            line_bot_api.push_message(userid, TextSendMessage(text=message))
        except LineBotApiError as e:
            print("error!")


if __name__ == "__main__":
    push_message("更新されました\nhttps://www.eng.tohoku.ac.jp/news/detail-,-id,1561.html", "理学部")
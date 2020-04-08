from linebot import LineBotApi
from linebot.models import TextSendMessage
from linebot.exceptions import LineBotApiError
import os

LINE_CHANNEL_ACCESS_TOKEN = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)

def push_message(major, message):

    """
    ここでcsvファイルを参照して対象のuseridを取り出す
    """

    for userid in userid_list:
        try:                            #メッセージを送信したい相手のIDを入力
            line_bot_api.push_message(userid,TextSendMessage(text=message))
        except LineBotApiError as e:
            print("error!")


if __name__ == "__main__":
    push_message(["userid"], "TEST")
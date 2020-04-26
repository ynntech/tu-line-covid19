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

    # 全員のuseridをリストとして返却
    def search_userid(self):
        sql_search = f"select userid from userinfo"
        target_ids = self.get_info_list(sql_search)
        return target_ids

    def push_message(self, message):
        """
        ==Parameters==
            message(str)      : ユーザに送りたいメッセージ
        ==Return==
            None
        """
        target_ids = self.serch_userid()

        for userid in target_ids:
            try:                            #メッセージを送信したい相手のIDを入力
                self.line_bot_api.push_message(userid[0], TextSendMessage(text=message))
            except LineBotApiError as e:
                print("error")

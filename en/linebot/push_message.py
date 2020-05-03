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
    def search_userid(self, major):
        if major == "TU_ENGINEER": 
            sql_search = f"select userid from userinfo where eng='1'"
        elif major == "TU": 
            sql_search = f"select userid from userinfo where eng='0'"

        target_ids = self.get_info_list(sql_search)
        return target_ids

    def push_message(self, message, user_majors):
        """
        ==Parameters==
            major             :今のところ、工学部か否かを識別するための引数
            message(str)      : ユーザに送りたいメッセージ
        ==Return==
            None
        """
        for user_major in user_majors:
            target_ids = self.search_userid(user_major)
            target_ids = [id_[0] for id_ in target_ids] # ネストになってるから普通のリストに直す
            # 500ずつに分ける
            for i in range(len(target_ids)//100+1):
                try:                            
                    self.line_bot_api.multicast(target_ids[i*100:(i+1)*100], TextSendMessage(text=message))
                except LineBotApiError as e:
                    print("error") 

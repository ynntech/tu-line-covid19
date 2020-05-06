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
        # 学科指定なし
        if len(user_major.split("_"))==1:
            if user_major == "全学教育":
                sql_search = f"select userid from userinfo where grade='1' or grade='2'"
            else:
                department = user_major
                if "not" in department: # notX学部
                    sql_search = f"select userid from userinfo where not department='{department[3:]}'"
                else:                   # X学部
                    sql_search = f"select userid from userinfo where department='{department}'"


        if len(user_major.split("_"))==2:
            department = user_major.split("_")[0]

            if user_major.split("_")[1] == "全学教育":
                if "not" in department:        # notX学部_全学教育
                    sql_search = f"select userid from userinfo where not department='{department[3:]}' and (grade='1' or grade='2')"
                else:                          # X学部_全学教育
                    sql_search = f"select userid from userinfo where department='{department}' and (grade='1' or grade='2')"

            elif user_major.split("_")[1] == "not全学教育": 
                if department == "全学生向け": # 全学生向け_not全学教育
                    sql_search = f"select userid from userinfo where not grade='1' and not grade='2'"
                elif "not" in department:     # notX学部_not全学教育
                    sql_search = f"select userid from userinfo where not department='{department[3:]}' and (not grade='1' and not grade='2')"
                else:                         # X学部_not全学教育
                    sql_search = f"select userid from userinfo where department='{department}' and (not grade='1' and not grade='2')"

            else:
                subject = user_major.split("_")[1]
                if "not" in subject:          # X学部_notA学科
                    sql_search = f"select userid from userinfo where department='{department}' and not subject='{subject[3:]}'"
                else:                         # X学部_A学科
                    sql_search = f"select userid from userinfo where subject='{subject}'"

        # 学科指定あり
        if len(user_major.split("_"))==3:
            department = user_major.split("_")[0]
            subject = user_major.split("_")[1]
            is_general = True if "not" not in user_major.split("_")[2] else False

            if is_general:
                if "not" in subject:    # X学部_notA学科_全学教育
                    sql_search = f"select userid from userinfo where department='{department}' and not subject='{subject[3:]}' and (grade='1' or grade='2')"
                else:                   # X学部_A学科_全学教育    
                    sql_search = f"select userid from userinfo where subject='{subject}' and (grade='1' or grade='2')"
            else:
                if "not" in subject:    # X学部_notA学科_not全学教育
                    sql_search = f"select userid from userinfo where department='{department}' and not subject='{subject[3:]}' and (not grade='1' and not grade='2')"
                else:                   # X学部_A学科_not全学教育    
                    sql_search = f"select userid from userinfo where subject='{subject}' and (not grade='1' and not grade='2')"

        target_ids = self.get_info_list(sql_search)
        return target_ids

    def push_message(self, message, user_major):
        """
        ==Parameters==
            message(str)      : ユーザに送りたいメッセージ 
            user_majors(str)   : メッセージの配信先（後々学科まで細分化するかも）
        ==Return==
            None
        """
        print(message, user_major)
        target_ids = self.search_userid(user_major)
        target_ids = [id_[0] for id_ in target_ids] # ネストになってるから普通のリストに直す
        print(target_ids)
        # 500ずつに分ける
        for i in range(len(target_ids)//100+1):
            try:                            
                self.line_bot_api.multicast(target_ids[i*100:(i+1)*100], TextSendMessage(text=message))
                print("multicastで送信できたよ！")
            except LineBotApiError as e:
                print("error")  


if __name__ == "__main__":
    pm = Push_Message()
    pm.push_message("新着情報があります",["会計大学院"])

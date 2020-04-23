# このファイルを手動で実行してアンケートを実施
# 実行する前に
# ・postgreSQLに接続してuserinfoテーブルのカラムを追加する
# ・userinfo_db.pyのtaburate_survey()のsql文を変更する

# 無駄にクラスにしてみた

from linebot import LineBotApi
from linebot.models import TextSendMessage
from linebot.exceptions import LineBotApiError
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    SourceUser, SourceGroup, SourceRoom,
    TemplateSendMessage, ConfirmTemplate, MessageAction,
    ButtonsTemplate, ImageCarouselTemplate, ImageCarouselColumn, URIAction,
    PostbackAction, DatetimePickerAction,
    CameraAction, CameraRollAction, LocationAction,
    CarouselTemplate, CarouselColumn, PostbackEvent,
    StickerMessage, StickerSendMessage, LocationMessage, LocationSendMessage,
    ImageMessage, VideoMessage, AudioMessage, FileMessage,
    UnfollowEvent, FollowEvent, JoinEvent, LeaveEvent, BeaconEvent,
    FlexSendMessage, BubbleContainer, ImageComponent, BoxComponent,
    TextComponent, SpacerComponent, IconComponent, ButtonComponent,
    SeparatorComponent, QuickReply, QuickReplyButton
)
import psycopg2
import psycopg2.extras
import os

class Push_Survey:
    def __init__(self):
        # 送信したいbotのアクセストークンを指定
        self.line_channel_access_token = "アクセストークン"
        self.line_bot_api = LineBotApi(self.line_channel_access_token)

    def get_info_list(self, sql):
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute (sql)
                results = cur.fetchall()
        return results
    
    def get_connection(self):
        self.database_url = "データベースURL"
        return psycopg2.connect(self.database_url)

    def push_survey(self):
        sql_search = "select userid from userinfo"
        all_userid = self.get_info_list(sql_search)

        for userid in all_userid:
            try:   
                buttons_template = ButtonsTemplate(
                    title='配信頻度に関してお答えください。', text=' ', actions=[
                        PostbackAction(label='少ない', data='1'),
                        PostbackAction(label='ちょうどいい', data='2'),
                        PostbackAction(label='多い', data='3')
                    ])
                template_message = TemplateSendMessage(alt_text='配信頻度に関してアンケートにご協力ください。', template=buttons_template)
                text_message = TextSendMessage(text="配信頻度に関してアンケートにご協力ください。")
                self.line_bot_api.push_message(userid[0], [text_message, template_message])
            except:
                print("アンケートを送信できませんでした。")
                    

if __name__ == "__main__":
    survey = Push_Survey() 
    survey.push_survey()
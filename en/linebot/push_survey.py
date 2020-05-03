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
        self.line_channel_access_token = "linebot access token"
        self.line_bot_api = LineBotApi(self.line_channel_access_token)


    def get_info_list(self, sql):
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute (sql)
                results = cur.fetchall()
        return results
    
    def get_connection(self):
        self.database_url = "db_url"
        return psycopg2.connect(self.database_url)

    def push_survey(self):
        sql_search = "select userid from userinfo"
        all_userid = self.get_info_list(sql_search)

        for userid in all_userid:
            try:   
                buttons_template = ButtonsTemplate(
                    title='学年の登録をお願いします。', text='学部生のみに配信しています。', actions=[
                        PostbackAction(label='1年生', data='1'),
                        PostbackAction(label='2年生', data='2'),
                        PostbackAction(label='3年生', data='3'),
                        PostbackAction(label='4年生', data='4')
                    ])
                text_message = TextSendMessage(text="【お願い】\nより最適化された情報配信をするため、学年の登録をお願いします。\
                    \n\n今後、東北大学全学教育(http://www2.he.tohoku.ac.jp/zengaku/zengaku.html)の情報は1,2年生と登録した方のみに配信されます。\
                    \n\n登録を誤った際は、もう一度正しい学年を選択してください。上書き登録されます。\
                    \n\nなお、ご登録いただいた情報は、上記以外の目的で一切の利用を行いません。")
                template_message = TemplateSendMessage(alt_text='【お願い】学年登録に関して', template=buttons_template)
                self.line_bot_api.push_message(userid[0], [text_message, template_message])
            except:
                print("アンケートを送信できませんでした。")
                


if __name__ == "__main__":
    survey = Push_Survey()
    survey.push_survey()
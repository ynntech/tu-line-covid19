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
        sql_search_und = "select userid from userinfo where department like '%部'"
        all_userid_und = self.get_info_list(sql_search_und)
        sql_search_gra = "select userid from userinfo where department like '%研究科' or department like '%大学院'"
        all_userid_gra = self.get_info_list(sql_search_gra)
        # print(all_userid_gra)
        for userid in all_userid_und:
            try:   
                buttons_template1 = ButtonsTemplate(
                    title='学年の登録をお願いします。', text='学部生のみに配信しています。', actions=[
                        PostbackAction(label='1年生', data='1_'),
                        PostbackAction(label='2年生', data='2_'),
                        PostbackAction(label='3年生', data='3_'),
                        PostbackAction(label='4年生', data='4_')
                    ])
                
                buttons_template2 = ButtonsTemplate(
                    title='学年の登録をお願いします。', text='学部生のみに配信しています。', actions=[
                        PostbackAction(label='5年生', data='5_'),
                        PostbackAction(label='6年生', data='6_')
                    ])

                text_message1 = TextSendMessage(text="全学生向けの新着情報があります。\n公式サイトもご確認ください。\nhttps://www.bureau.tohoku.ac.jp/covid19BCP/index.html\n===============\n《2020/04/28》\n【お知らせ】東北大学緊急学生支援パッケージ〜Wi-Fiルーターの貸与について〜（申請締切：4月30日(木) 12:00まで）\nhttps://www.bureau.tohoku.ac.jp/covid19BCP/student.html#wi-fi\n《2020/04/27》\n学生のみなさんへ（東北大学緊急学生支援パッケージ～オンライン学習のためのネット環境支援について～）\nhttp://www.tohoku.ac.jp/japanese/2020/04/news20200427-01.html\n《2020/04/27》\n【予告】オンラインによる進学説明会・相談会、入試説明会の開催について\nhttps://www.tohoku.ac.jp/japanese/2020/04/news20200427-02.html")

                text_message2 = TextSendMessage(text="【お願い】\n新たに東北大学全学教育（http://www2.he.tohoku.ac.jp/zengaku/zengaku.html）の情報を配信するため、学年の登録をお願いいたします。\n1, 2年生と登録された方を対象に配信いたします。\n\n登録を誤った場合は、もう一度正しい学年のボタンを選択していただくか（上書き登録されます）、改めて下のメニューより所属の再登録を行ってください。")


                template_message1 = TemplateSendMessage(alt_text='【お願い】学年登録に関して', template=buttons_template1)
                template_message2 = TemplateSendMessage(alt_text='【お願い】学年登録に関して', template=buttons_template2)
                self.line_bot_api.push_message(userid[0], [text_message1, text_message2, template_message1, template_message2])
            except:
                print("アンケートを送信できませんでした。")
        print("アンケートの送信終了")
        for userid in all_userid_gra:
            try:
                text_message = TextSendMessage(text="全学生向けの新着情報があります。\n公式サイトもご確認ください。\nhttps://www.bureau.tohoku.ac.jp/covid19BCP/index.html\n===============\n《2020/04/28》\n【お知らせ】東北大学緊急学生支援パッケージ〜Wi-Fiルーターの貸与について〜（申請締切：4月30日(木) 12:00まで）\nhttps://www.bureau.tohoku.ac.jp/covid19BCP/student.html#wi-fi\n《2020/04/27》\n学生のみなさんへ（東北大学緊急学生支援パッケージ～オンライン学習のためのネット環境支援について～）\nhttp://www.tohoku.ac.jp/japanese/2020/04/news20200427-01.html\n《2020/04/27》\n【予告】オンラインによる進学説明会・相談会、入試説明会の開催について\nhttps://www.tohoku.ac.jp/japanese/2020/04/news20200427-02.html")
                self.line_bot_api.push_message(userid[0], text_message)
            except:
                print("送信できませんでした")
                    

if __name__ == "__main__":
    survey = Push_Survey() 
    survey.push_survey()
    


    
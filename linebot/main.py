import os
import errno
import tempfile
from random import sample
from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError, LineBotApiError
)
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
import pandas as pd

app = Flask(__name__)

LINE_CHANNEL_ACCESS_TOKEN = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
LINE_CHANNEL_SECRET = os.environ["LINE_CHANNEL_SECRET"]
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN) 
handler = WebhookHandler(LINE_CHANNEL_SECRET)

#QuickReplyで表示する選択肢たち
major_dic = {"文学部":["人文社会学科"], "教育学部":["教育科学科"], "法学部":["法学科"], "経済学部":["経済学科", "経営学科"]\
        , "理学部":["数学科","物理学科","宇宙地球物理学科","化学科","地圏環境科学科","地球惑星物質科学科","生物学科"]\
        , "医学部":["医学科","保健学科"], "歯学部":["歯学科"], "薬学部":["薬学科","創薬科学科"]\
        , "工学部":["機械知能・航空工学科","電気情報物理工学科","電気情報物理工学科","電気情報物理工学科","電気情報物理工学科"]\
        , "農学部":["生物生産科学科","応用生物化学科"]}

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except LineBotApiError as e:
        print("Got exception from LINE Messaging API: %s\n" % e.message)
        for m in e.error.details:
            print("  %s: %s" % (m.property, m.message))
        print("\n")
    except InvalidSignatureError:
        abort(400)

    return 'OK'

# ユーザからメッセージが送信されたときにオウム返しする
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text
    line_bot_api.reply_message(event.reply_token,TextSendMessage(text=text))

# 友だち登録（またはブロック解除）されたときにユーザに学部を選択させる
@handler.add(FollowEvent)
def handle_follow(event):
    line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(
                text='友達登録ありがとうございます.\n下のボタンから学部を選択してください.',
                quick_reply=QuickReply(
                    items=[QuickReplyButton(action=PostbackAction(label=department, data=department)) for department in major_dic.keys()]
                ))) # QuickReplyというリッチメッセージが起動してPostbackEventを発生させる

# Postbackを受け取る
@handler.add(PostbackEvent)
def handle_postback(event):

    # 学部を選択した後、学科を選択してもらう
    if event.postback.data[-1] == "部": 
        department = event.postback.data
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(
                text='下のボタンから学科を選択してください.',
                quick_reply=QuickReply(
                    items=[QuickReplyButton(action=PostbackAction(label=subject, data=department + " " +subject)) for subject in major_dic[department]]
                )))

    # 学科が選択された後、所属とuseridをcsvに追記
    elif event.postback.data[-1] == "科": 
        user_major = event.postback.data
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=user_major +"で登録しました."))
        
        department = user_major.split(" ")[0]
        subject = user_major.split(" ")[1]
        userid = event.source.user_id

        userid_df = pd.read_csv("userid.csv",  encoding="cp932")
        newid = pd.Series([department, subject, userid], index=["department", "subject", "user_id"])
        userid_df = userid_df.append(newid, ignore_index=True)
        userid_df.to_csv('userid.csv', encoding='cp932')


if __name__ ==  "__main__":
    app.debug = True
    app.run(port=8000)
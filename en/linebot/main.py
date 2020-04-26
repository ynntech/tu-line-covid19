import os
from flask import Flask, request, abort, jsonify
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
from userinfo_db import User_DB

app = Flask(__name__)

user_db = User_DB()

LINE_CHANNEL_ACCESS_TOKEN = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
LINE_CHANNEL_SECRET = os.environ["LINE_CHANNEL_SECRET"]
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)


### scraping apiと連携用コード
import json
import requests
from push_message import Push_Message

pusu_message_ = Push_Message()

def now_info():
    headers = {"content-type": "application/json"}
    url = f"{os.environ['WEB_SERVER_DOMAIN']}/request/now"
    response = requests.get(url, headers=headers)
    return response.json()["response"]

@app.route("/push", methods=['POST'])
def push():
    try:
        data = request.get_json()
        if type(data) != dict:
            data = json.loads(data)
        pusu_message_.push_message(data["message"])
        return jsonify({"status":"200"})
    except:
        abort(400)

@app.route("/remind", methods=['GET'])
def remind():
    return jsonify({"status":"200"})


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

# ユーザから『最新情報』と送信されたとき、最新の情報を送信
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text

    if text == "Latest information":
        userid = event.source.user_id
        information_all = now_info().split("\n&&&\n")
        TextSendMessages_all = [TextSendMessage(text=info_) for info_ in information_all]
        line_bot_api.reply_message(event.reply_token, TextSendMessages_all)

    # 他はオウム返し
    else:
        line_bot_api.reply_message(event.reply_token,[TextSendMessage(text=text)])

# 友だち登録（またはブロック解除）されたときにユーザに学部を選択させる
@handler.add(FollowEvent)
def handle_follow(event):
    userid = event.source.user_id

    # ユーザー情報をDBに追記
    user_db.add_userid(userid)

    # 登録した所属の最新情報を送信
    TextSendMessages = [TextSendMessage(text="Thank you for adding this LINE bot.\n\nWe will give you notification of Tohoku University information about Novel Coronavirus.\n\nPlease check a message about this LINE bot.")]
    information_all = now_info().split("\n&&&\n")
    TextSendMessages_all = [TextSendMessage(text=info_) for info_ in information_all]
    TextSendMessages.extend(TextSendMessages_all)
    line_bot_api.reply_message(event.reply_token, TextSendMessages)


# Postbackを受け取る
@handler.add(PostbackEvent)
def handle_postback(event):

    # アンケート機能
    if event.postback.data in "123":
        userid = event.source.user_id
        ans = event.postback.data
        user_db.taburate_survey(userid, ans)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="Thank you for your answering."))


# ブロックされたときにDBからユーザー情報を削除
@handler.add(UnfollowEvent)
def handle_unfollow(event):
    userid = event.source.user_id
    user_db.del_userid(userid)


if __name__ ==  "__main__":
    port = int(os.environ.get('PORT', 8080))
    app.run(host ='0.0.0.0',port = port)

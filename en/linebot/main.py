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

def now_info(major):
    data = {"major":major}
    headers = {"content-type": "application/json"}
    url = f"{os.environ['WEB_SERVER_DOMAIN']}/request/now"
    response = requests.get(url, headers=headers, json=json.dumps(data))
    return response.json()["response"]

@app.route("/push", methods=['POST'])
def push():
    try:
        data = request.get_json()
        if type(data) != dict:
            data = json.loads(data)
        pusu_message_.push_message(data["message"], data["major"]) #%#%#%#%#%#% 新たにdata[major]を渡した #%#%#%#%#%#%
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
        print(user_db.is_eng(userid))
        if user_db.is_eng(userid):
            information_all = now_info("TU_ENGINEER").split("\n&&&\n")
        else:
            information_all = now_info("TU").split("\n&&&\n")
        TextSendMessages_all = [TextSendMessage(text=info_) for info_ in information_all]
        line_bot_api.reply_message(event.reply_token, TextSendMessages_all)

    # 他はオウム返し
    else:
        line_bot_api.reply_message(event.reply_token,[TextSendMessage(text=text)])

# 友だち登録（またはブロック解除）されたときにユーザに学部を選択させる
@handler.add(FollowEvent)
def handle_follow(event):

    # 登録した所属の最新情報を送信
    #TextSendMessages = [TextSendMessage(text="Thank you for adding this LINE bot.\n\nWe will give you notification of Tohoku University information about Novel Coronavirus.\n\nPlease check a message about this LINE bot.")]
    #line_bot_api.reply_message(
    #        event.reply_token,
    #        [TextSendMessage(text="Thank you for adding this LINE bot.\n\nWe will give you notification of Tohoku University information about Novel Coronavirus.\n\nPlease check a message about this LINE bot."),
    #        TextSendMessage(
    #        text="工学部からの情報配信を希望する方はyesを、希望しない方はnoを選択してください",
    #        quick_reply=QuickReply(
    #            items=[QuickReplyButton(action=PostbackAction(label="yes", data="yes")),
    #                        QuickReplyButton(action=PostbackAction(label="no", data="no"))]
    #        ))])
    ### added by kenichi ###
    line_bot_api.reply_message(
            event.reply_token,
            [TextSendMessage(text="Thank you for adding this LINE bot.\n\nWe will give you notification of Tohoku University information about Novel Coronavirus."),
            TextSendMessage(
            text="If you also want to get news about School of Engineering, please tap yes",
            quick_reply=QuickReply(
                items=[QuickReplyButton(action=PostbackAction(label="yes", data="yes")),
                            QuickReplyButton(action=PostbackAction(label="no", data="no"))]
            ))])
    ### end ###

# Postbackを受け取る
@handler.add(PostbackEvent)
def handle_postback(event):
    userid = event.source.user_id

    if event.postback.data == "yes":
        # ユーザー情報をDBに追記
        user_db.add_userinfo(userid, 1)

        #TextSendMessages = [TextSendMessage(text="今後、工学部から配信を受け取ります。")]
        information = now_info("TU_ENGINEER").split("\n&&&\n")
        #TextSendMessages_all = [TextSendMessage(text=info_) for info_ in information]
        #TextSendMessages.extend(TextSendMessages_all)
        ### added by kenichi ###
        TextSendMessages = [TextSendMessage(text=info_) for info_ in information]
        ### end ###
        line_bot_api.reply_message(event.reply_token, TextSendMessages)

    if event.postback.data == "no":
        # ユーザー情報をDBに追記
        user_db.add_userinfo(userid, 0)

        #TextSendMessages = [TextSendMessage(text="今後、工学部から配信を受け取りません。")]
        information_all = now_info("TU").split("\n&&&\n")
        #TextSendMessages_all = [TextSendMessage(text=info_) for info_ in information_all]
        #TextSendMessages.extend(TextSendMessages_all)
        ### added by kenichi ###
        TextSendMessages = [TextSendMessage(text=info_) for info_ in information_all]
        ### end ###
        line_bot_api.reply_message(event.reply_token, TextSendMessages)

    # アンケート機能
    if event.postback.data in "1234":
        grade = event.postback.data
        userid = event.source.user_id
        ans = event.postback.data
        user_db.taburate_survey(userid, ans)
        #line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"『{grade}年生』で登録しました。"))
        ### added by kenichi ###
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"successfully registerd as grade {grade}"))
        ### end ###


# ブロックされたときにDBからユーザー情報を削除
@handler.add(UnfollowEvent)
def handle_unfollow(event):
    userid = event.source.user_id
    user_db.del_userinfo(userid)


if __name__ ==  "__main__":
    port = int(os.environ.get('PORT', 8080))
    app.run(host ='0.0.0.0',port = port)

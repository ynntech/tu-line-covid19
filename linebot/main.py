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

LINE_CHANNEL_ACCESS_TOKEN = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
LINE_CHANNEL_SECRET = os.environ["LINE_CHANNEL_SECRET"]
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

user_db = User_DB()

#QuickReplyで表示する選択肢たち
major_dic = {"学部生":{"文学部":["人文社会学科"],
                      "教育学部":["教育科学科"],
                      "法学部":["法学科"],
                      "経済学部":["経済学科", "経営学科", "未定"],
                      "理学部":["数学系","物理系","化学系", "地球科学系","生物系"],
                      "医学部":["医学科", "保健学科"],
                      "歯学部":["歯学科"],
                      "薬学部":["薬学科", "創薬科学科", "未定"],
                      "工学部":["機械知能・航空工学科", "電気情報物理工学科", "化学・バイオ工学科",
                               "材料科学総合学科", "建築・社会環境工学科"],
                      "農学部":["生物生産科学科", "応用生物化学科", "未定"]},
             "院生":["文学研究科",
                    "教育学研究科",
                    "法学研究科",
                    "経済学研究科",
                    "理学研究科",
                    "医学系研究科",
                    "歯学研究科",
                    "薬学研究科",
                    "工学研究科",
                    "農学研究科",
                    "国際文化研究科",
                    "情報科学研究科",
                    "生命科学研究科",
                    "環境科学研究科",
                    "医工学研究科",
                    "法科大学院",
                    "公共政策大学院",
                    "会計大学院"]}


### scraping apiと連携用コード
import json
import requests
from push_message import Push_Message

pusu_message_ = Push_Message()

def now_info(major):
    data = {"major":major}
    url = f"{os.environ['WEB_SERVER_DOMAIN']}/request/now"
    response = requests.post(url, json=json.dumps(data))
    return response.json()["response"]

@app.route("/push", methods=['POST'])
def push():
    try:
        data = request.get_json()
        if type(data) != dict:
            data = json.loads(data)
        subject = True if data["subject"] == "true" else False
        pusu_message_.push_message(data["message"], data["majors"], subject)
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

    if text == "最新情報":
        userid = event.source.user_id
        department = user_db.get_usermajor(userid) # ユーザーのdepartmentを取得
        if department:
            information_all = now_info("全学生向け").split("\n&&&\n")
            information_dep = now_info(department).split("\n&&&\n")
            TextSendMessages_all = [TextSendMessage(text=info_) for info_ in information_all]
            TextSendMessages_dep = [TextSendMessage(text=info_) for info_ in information_dep]
            TextSendMessages_all.extend(TextSendMessages_dep)
            line_bot_api.reply_message(event.reply_token, TextSendMessages_all)
        # ユーザが所属を登録せずに『最新情報』と送信したとき
        else:
             line_bot_api.reply_message(event.reply_token,TextSendMessage(text="先に学部・研究科を登録してください。"))

    if text =="所属再登録":
        userid = event.source.user_id
        user_db.del_userinfo(userid) # user情報を削除

        line_bot_api.reply_message(
            event.reply_token,
            [TextSendMessage(text="現在登録されていた学部、研究科は削除されました。"),
            TextSendMessage(
            text="もう一度下のボタンから学部生か院生かを選択し、その後学年、学部または研究科を選択してください。",
            quick_reply=QuickReply(
                items=[QuickReplyButton(action=PostbackAction(label="学部生", data="学部生")),
                            QuickReplyButton(action=PostbackAction(label="院生", data="院生"))]
            ))])

    else:
        line_bot_api.reply_message(event.reply_token,[TextSendMessage(text=text)])

# 友だち登録（またはブロック解除）されたときにユーザに学部を選択させる
@handler.add(FollowEvent)
def handle_follow(event):
    line_bot_api.reply_message(
            event.reply_token,
            [TextSendMessage(text="友だち追加ありがとうございます。\n\n登録した学部・研究科と、全学生向けのコロナウイルス関連のサイト掲載情報を配信します。\n\n概要・免責事項等は当アカウントのタイムライン投稿をご覧ください。"),
            TextSendMessage(
            text="下のボタンから学部生か院生かを選択し、その後学部または研究科を選択してください。\n\n所属を間違えて登録した際は、画面下部のメニューバーの『所属再登録』より再登録することができます。",
            quick_reply=QuickReply(
                items=[QuickReplyButton(action=PostbackAction(label="学部生", data="学部生")),
                            QuickReplyButton(action=PostbackAction(label="院生", data="院生"))]
            ))]) # QuickReplyというリッチメッセージが起動してPostbackEventを発生させる

# Postbackを受け取る
@handler.add(PostbackEvent)
def handle_postback(event):
    userid = event.source.user_id
    
    if event.postback.data == "学部生":
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(
                text='下のボタンをスワイプして学年を選択してください。',
                quick_reply=QuickReply(
                    items=[QuickReplyButton(action=PostbackAction(label=f"{grade}年生", data=grade)) for grade in [1,2,3,4]]
                )))

    elif event.postback.data in "1234":
        grade = event.postback.data
        user_db.add_usergrade(grade, userid)
        line_bot_api.reply_message(
            event.reply_token,
            [TextSendMessage(text=f"{grade}年生で登録しました"),
            TextSendMessage(
                text='下のボタンをスワイプして学部を選択してください。',
                quick_reply=QuickReply(
                    items=[QuickReplyButton(action=PostbackAction(label=department, data=department)) for department in major_dic["学部生"].keys()]
                ))])

    # 学部を選択した場合は、学科を選択してもらう
    elif event.postback.data[-1] == "部":
        department = event.postback.data
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(
                text='下のボタンをスワイプして学科を選択してください。',
                quick_reply=QuickReply(
                    items=[QuickReplyButton(action=PostbackAction(label=subject, data=department + " " +subject)) for subject in major_dic["学部生"][department]]
                )))

    elif event.postback.data == "院生" or event.postback.data == "ひとつ前に戻る":
        items = [QuickReplyButton(action=PostbackAction(label=department, data=department)) for department in major_dic["院生"][:9]]
        items.append(QuickReplyButton(action=PostbackAction(label="さらに表示する", data="さらに表示する")))
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(
                text="下のボタンをスワイプして研究科を選択してください。",
                quick_reply=QuickReply(
                    items=items
                )))

    elif event.postback.data == "さらに表示する":  # 『さらに表示する』が押されたら残りの所属を表示する
        items = [QuickReplyButton(action=PostbackAction(label=department, data=department)) for department in major_dic["院生"][9:]]
        items.append(QuickReplyButton(action=PostbackAction(label="ひとつ前に戻る", data="ひとつ前に戻る")))
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(
                text='下のボタンをスワイプして研究科を選択してください。',
                quick_reply=QuickReply(
                    items=items
                )))

    # 所属が選択された後、所属とuseridをcsvに追記
    elif event.postback.data[-1] == "科" or event.postback.data[-1] == "系" or event.postback.data[-1]=="院" or event.postback.data[-1] == "定":
        user_major = event.postback.data

        if " " not in user_major: # 研究科を選択したときはsubjectは空
            department = user_major
            subject = ""
        else:                     # 学部を選択したときのみsubjectがある
            department = user_major.split(" ")[0]
            subject = user_major.split(" ")[1]

        # ユーザー情報をDBに追記
        user_db.add_usermajor(department, subject, userid)

        # 登録した所属の最新情報を送信
        TextSendMessages = [TextSendMessage(text="{} {}で登録しました".format(department, subject))]
        information_all = now_info("全学生向け").split("\n&&&\n")
        information_dep = now_info(department).split("\n&&&\n")
        TextSendMessages_all = [TextSendMessage(text=info_) for info_ in information_all]
        TextSendMessages_dep = [TextSendMessage(text=info_) for info_ in information_dep]
        TextSendMessages.extend(TextSendMessages_all)
        TextSendMessages.extend(TextSendMessages_dep)
        line_bot_api.reply_message(event.reply_token, TextSendMessages)

    elif event.postback.data in "1_2_3_4_":
        userid = event.source.user_id
        grade = event.postback.data[0]
        user_db.taburate_survey(userid, ans)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"『{grade}年生』で登録しました。"))

# ブロックされたときにDBからユーザー情報を削除
@handler.add(UnfollowEvent)
def handle_unfollow(event):
    userid = event.source.user_id
    user_db.del_userinfo(userid)


if __name__ ==  "__main__":
    port = int(os.environ.get('PORT', 8080))
    app.run(host ='0.0.0.0',port = port)
#-*- coding: utf-8 -*-
import sys
import json
import random
import string
from flask import Flask, request, jsonify, abort

from database import DataBase

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config["JSON_SORT_KEYS"] = False

db = DataBase()
FIRST_TOKEN = ""
SESSION_KEY = ""

# ランダムキー生成用関数
def randomkey():
    randlst = [random.choice(string.ascii_letters + string.digits) for i in range(32)]
    return ''.join(randlst)

# AES decoder関数
def decode(string, passwd):
    pass


# 最新情報の取得API
@app.route("/request/now", methods=["POST"])
def request_now():
    data = request.get_json()
    if type(data) != dict:
        data = json.loads(data)
    major = data["major"]
    if major in db.major_index:
        return jsonify({
                        "status":"200",
                        "response":db.now(major=major)
                        })
    else:
        abort(400, "Invalid request")

# 時のkeyの取得用API
@app.route("/request/key", methods=["POST"])
def request_key():
    global SESSION_KEY, FIRST_TOKEN
    try:
        data = request.get_json()
        if type(data) != dict:
            data = json.loads(data)
        token = data["body"]
        if token == FIRST_TOKEN:
            SESSION_KEY = randomkey()
            return jsonify({
                            "status":"200",
                            "body":SESSION_KEY
                            })
        else:
            abort(401, "Invalid access")
    except:
        abort(400, "Invalid request")

# Google formからの受け取りAPI
@app.route("/request/push", methods=["POST"])
def request_push():
    global SESSION_KEY
    data = request.get_json()
    if type(data) != dict:
        data = json.loads(data)
    data = json.loads(decode(data["body"], SESSION_KEY))
    data["targets"] = data["targets"].split(",")
    res = db.register(info=data)
    if res:
        return jsonify({"status":"200"})
    else:
        abort(400, "Couldn't pushed")

@app.route("/test/post", methods=["POST"])
def test_post():
    data = request.get_json()
    if type(data) != dict:
        data = json.loads(data)
    return jsonify({
                    "status":"200",
                    "response":data
                    })

@app.route("/test/get", methods=["GET"])
def test_get():
    return jsonify({"status":"200"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="port", threaded=True)
    db.exit()
    sys.exit()

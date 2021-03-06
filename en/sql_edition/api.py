#-*- coding: utf-8 -*-
import os
import sys
import json
from flask import Flask, request, jsonify, abort

from database import DataBase
from utils import Router

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config["JSON_SORT_KEYS"] = False

db = DataBase()
TOKEN = os.environ["WEB_SERVER_TOKEN"]
router = Router()

# 最新情報の取得API
@app.route("/request/now", methods=["POST"])
def request_now():
    global router
    data = request.get_json()
    if type(data) != dict:
        data = json.loads(data)
    major = data["major"]
    try:
        res = router.now(major)
        return jsonify({
                        "status":"200",
                        "response":res
                        })
    except:
        abort(400, "Invalid request")

# Google formからの受け取りAPI
@app.route("/request/push", methods=["POST"])
def request_push():
    global db
    data = request.get_json()
    if type(data) != dict:
        data = json.loads(data)
    if data["token"] == TOKEN:
        del data["token"]
        try:
            res = db.register(info=data)
        except:
            del db
            db = DataBase()
            res = db.register(info=data)
        if res:
            return jsonify({"status":"200"})
        else:
            abort(400, "Couldn't pushed")
    else:
        abort(400, "Invalid request")

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
    app.run(host="0.0.0.0", port=os.environ["API_SERVER_PORT"], threaded=True)
    db.exit()
    sys.exit()

#-*- coding: utf-8 -*-
import sys
import json
from flask import Flask, request, jsonify, abort

from info import Info

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config["JSON_SORT_KEYS"] = False

info = Info()

# 最新情報の取得API
@app.route("/request/now", methods=["POST"])
def recipe_request():
    data = request.get_json()
    if type(data) != dict:
        data = json.loads(data)
    major = data["major"]
    if major in info.major_index:
        return jsonify({
                        "status":"200",
                        "response":info.now(major=major)
                        })
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
    app.run(host="0.0.0.0", port="your port", threaded=True)
    sys.exit()

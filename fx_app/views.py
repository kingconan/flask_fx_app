# -*- coding: utf-8 -*-

from flask import Flask, request, redirect, jsonify, Response
from flask import render_template
from werkzeug.utils import secure_filename
import os
from flask_sse import sse

from . import app
from excel_task import parse_fx_excel
from hotel_task import parse_booking
from hotel_task import parse_leading

from functools import wraps
from flask import make_response

import json

UPLOAD_FOLDER = os.path.abspath('./fx_app/upload')


def allow_cross_domain(fun):
    @wraps(fun)
    def wrapper_fun(*args, **kwargs):
        rst = make_response(fun(*args, **kwargs))
        rst.headers['Access-Control-Allow-Origin'] = '*'
        rst.headers['Access-Control-Allow-Methods'] = 'PUT,GET,POST,DELETE'
        allow_headers = "Referer,Accept,Origin,User-Agent,x-requested-with"
        rst.headers['Access-Control-Allow-Headers'] = allow_headers
        return rst
    return wrapper_fun


# @allow_cross_domain
@app.route('/api/hotel/parse', methods=['POST'])
def hotel_parse():
    print "hotel_parse"
    # data = request.values.to_dict().keys()[0]
    # data = json.loads(data)
    # url = data.get("url")
    data = request.json
    print data
    url = data["url"]
    print url
    if not url:
        return jsonify({
            "ok": 1,
            "msg": "no url",
            "obj": None
        })
    if url.find("booking.com") > -1:
        ans = parse_booking(url)
        return jsonify({
            "ok": 0,
            "msg": "ok",
            "obj": ans
        })
    elif url.find("lhw.cn") > -1:
        ans = parse_leading(url)
        return jsonify({
            "ok": 0,
            "msg": "ok",
            "obj": ans
        })


# @app.route('/send')
# def send_message():
#     print "send message starts"
#     sse.publish({"message": "Hello!"}, type='greeting')
#     print "send message end"
#     return "Message sent!"
#
#
@app.route("/")
def index():
    return render_template("index.html",name="index")

@app.route("/hello")
def test():
    return "Hello Flask!"


@app.route("/upload", methods=['GET', 'POST'])
def upload():
    print "in upload"
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files["file"]
        if file.filename == '':
            return redirect(request.url)
        if file:
            folder = os.path.join(UPLOAD_FOLDER)
            filename = secure_filename(file.filename)
            print folder
            filepath = os.path.join(folder, filename)
            file.save(filepath)

            print "parse starts..."
            data = parse_fx_excel(filepath)
            print "end parse"
            return jsonify({
                "ok": 0,
                "msg": "ok",
                "obj": data
            })

    return render_template("upload.html", name="upload")



# -*- coding: utf-8 -*-

from flask import Flask, request, redirect, jsonify
from flask import render_template
from werkzeug.utils import secure_filename
import os

from . import app

UPLOAD_FOLDER = os.path.abspath('./fx_app/upload')

from excel_task import parse_fx_excel

@app.route("/cal")
def cal():
    return "Hell world"


@app.route("/")
def index():
    return render_template("index.html",name="index")


@app.route("/upload", methods=['GET', 'POST'])
def upload():
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

            data = parse_fx_excel(filepath)

            return jsonify({
                "ok": 0,
                "msg": "ok",
                "obj": data
            })

    return render_template("upload.html", name="upload")
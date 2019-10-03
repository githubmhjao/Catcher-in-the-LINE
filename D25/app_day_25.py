from __future__ import unicode_literals
import os

from flask import Flask, request, abort, render_template, url_for, flash, redirect

from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, PostbackEvent, TextMessage, TextSendMessage

import configparser

from custom_models import utils, PhoebeTalks, PhoebeFlex

# config 初始化
config = configparser.ConfigParser()
config.read('config.ini')

# Flask 初始化
app = Flask(__name__)
app.secret_key = config.get('flask', 'secret_key')

# Day25: users 使用者清單
users = {'Me': {'password': 'myself'}}

# Day25: Flask-Login 初始化
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.session_protection = "strong"
login_manager.login_view = 'login'
login_manager.login_message = '請證明你並非來自黑暗草泥馬界'

class User(UserMixin):
    pass


@login_manager.user_loader
def user_loader(user_id):
    if user_id not in users:
        return

    user = User()
    user.id = user_id
    return user


@login_manager.request_loader
def request_loader(request):
    user_id = request.form.get('user_id')
    if user_id not in users:
        return

    user = User()
    user.id = user_id

    # DO NOT ever store passwords in plaintext and always compare password
    # hashes using constant-time comparison!
    user.is_authenticated = request.form['password'] == users[user_id]['password']

    return user

# LINE 聊天機器人的基本資料
line_bot_api = LineBotApi(config.get('line-bot', 'channel_access_token'))
handler = WebhookHandler(config.get('line-bot', 'channel_secret'))

@app.route("/")
def home():
    return render_template("home.html")

# Day25: Flask-Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template("login.html")
    
    user_id = request.form['user_id']
    if (user_id in users) and (request.form['password'] == users[user_id]['password']):
        user = User()
        user.id = user_id
        login_user(user)
        flash(f'{user_id}！歡迎加入草泥馬訓練家的行列！')
        return redirect(url_for('from_start'))

    flash('登入失敗了...')
    return render_template('login.html')

@app.route('/logout')
def logout():
    user_id = current_user.get_id()
    logout_user()
    flash(f'{user_id}！歡迎下次再來！')
    return render_template('login.html') 

@app.route("/from_start")
@login_required
def from_start():
    return render_template("from_start.html")

@app.route("/show_records")
@login_required
def show_records():
    python_records = CallDatabase.web_select_overall()
    return render_template("show_records.html", html_records=python_records)

# Day24: 選擇訓練紀錄
@app.route("/select_records", methods=['GET', 'POST'])
@login_required
def select_records():
    if request.method == 'POST':
        print(request.form)
        python_records = CallDatabase.web_select_specific(request.form)
        return render_template("show_records.html", html_records=python_records)
    else:
        return render_template("select_records.html")

# Day24: 舒適地選擇訓練紀錄
@app.route("/select_records_comfortable", methods=['GET', 'POST'])
@login_required
def select_records_comfortable():
    if request.method == 'POST':
        print(request.form)
        python_records = CallDatabase.web_select_specific(request.form)
        return render_template("show_records.html", html_records=python_records)
    else:
        table = CallDatabase.web_select_overall()
        uniques = utils.get_unique(table)
        return render_template("select_records_comfortable.html", uniques=uniques)


# 接收 LINE 的資訊
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

# 處理 MessageEvent 中的 TextMessage
@handler.add(MessageEvent, message=TextMessage)
def reply_text_message(event):
    
    if event.source.user_id != "Udeadbeefdeadbeefdeadbeefdeadbeef":
        
        reply = False

        # 將資料存入表格中 
        if not reply:
            reply = PhoebeTalks.insert_record(event)
        
        # 發送 FlexMessage
        if not reply:
            reply = PhoebeFlex.img_search_flex(event)
        
        # 幫忙上網找圖
        if not reply:
            reply = PhoebeTalks.img_search(event)
        
        # 裝飾過的回音機器人
        if not reply:
            reply = PhoebeTalks.pretty_echo(event)
            
            
if __name__ == "__main__":
    app.run()
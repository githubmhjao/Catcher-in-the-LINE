from __future__ import unicode_literals
import os

# 增加了 render_template
from flask import Flask, request, abort, render_template

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageSendMessage

import configparser

import urllib
import re
import random

app = Flask(__name__)

# LINE 聊天機器人的基本資料
config = configparser.ConfigParser()
config.read('config.ini')

line_bot_api = LineBotApi(config.get('line-bot', 'channel_access_token'))
handler = WebhookHandler(config.get('line-bot', 'channel_secret'))

@app.route("/")
def home():
    return render_template("home_pixijs.html")


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

# 請 pixabay 幫我們找圖
@handler.add(MessageEvent, message=TextMessage)
def pixabay_isch(event):
    
    if event.source.user_id != "Udeadbeefdeadbeefdeadbeefdeadbeef":
        # 先找圖
        try:
            url = f"https://pixabay.com/images/search/{urllib.parse.urlencode({'q':event.message.text})[2:]}/"
            headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'}
            
            req = urllib.request.Request(url, headers = headers)
            conn = urllib.request.urlopen(req)
            
            print('fetch page finish')
            
            pattern = 'img srcset="\S*\s\w*,'
            img_list = []
            
            for match in re.finditer(pattern, str(conn.read())):
                img_list.append(match.group()[12:-3])
                
            random_img_url = random.choice(img_list)
            print('fetch img url finish')
            print(random_img_url)
            
            line_bot_api.reply_message(
                event.reply_token,
                ImageSendMessage(
                    original_content_url=random_img_url,
                    preview_image_url=random_img_url
                )
            )
        # 找不到圖就告訴我 user_id
        except:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=str(event.source.user_id))
            )

if __name__ == "__main__":
    app.run()
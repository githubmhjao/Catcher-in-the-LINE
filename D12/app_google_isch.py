from __future__ import unicode_literals
import os
from flask import Flask, request, abort
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

# 幫你在 google 上找圖
@handler.add(MessageEvent, message=TextMessage)
def google_isch(event):
    
    if event.source.user_id != "Udeadbeefdeadbeefdeadbeefdeadbeef":
        # 先找圖
        try:
            q_string = {'tbm': 'isch', 'q': event.message.text}
            url = f"https://www.google.com/search?{urllib.parse.urlencode(q_string)}/"
            headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'}
            
            req = urllib.request.Request(url, headers = headers)
            conn = urllib.request.urlopen(req)
            
            print('fetch conn finish')
            
            pattern = 'img data-src="\S*"'
            img_list = []
            
            for match in re.finditer(pattern, str(conn.read())):
                img_list.append(match.group()[14:-1])
                
            random_img_url = img_list[random.randint(0, len(img_list)+1)]
            print('fetch img url finish')
            print(random_img_url)
            
            line_bot_api.reply_message(
                event.reply_token,
                ImageSendMessage(
                    original_content_url=random_img_url,
                    preview_image_url=random_img_url
                )
            )
            
        # 找不到圖就學說話    
        except:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=event.message.text)
            )

if __name__ == "__main__":
    app.run()
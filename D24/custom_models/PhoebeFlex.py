from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import FlexSendMessage

import configparser

import re

# 引入我們的套件
from custom_models import utils

config = configparser.ConfigParser()
config.read('config.ini')

line_bot_api = LineBotApi(config.get('line-bot', 'channel_access_token'))

# LINE 提供的 FlexMessage 範例
sample = {
    'type': 'bubble',
    'direction': 'ltr',
    'hero': {
        'type': 'image',
        'url': 'https://scdn.line-apps.com/n/channel_devcenter/img/fx/01_2_restaurant.png',
        'size': 'full',
        'aspect_ratio': '20:13',
        'aspect_mode': 'cover',
        'action': { 'type': 'postback', 'data': 'sample', 'label': 'sample' }
    }
}

# 依照使用者輸入的訊息傳送 FlexMessage    
def img_search_flex(event):
    
    if re.match("flex", event.message.text.lower()):
        
        try:
        
            translate = utils.get_translate(event.message.text[5:])
            random_img_url = utils.get_img_url(img_source='pixabay', target=translate)

            contents = utils.prepare_img_search_flex(event.message.text[5:], translate, random_img_url)

            line_bot_api.reply_message(
                event.reply_token,
                FlexSendMessage(
                    alt_text = f'flex {translate}',
                    contents = contents
                )
            )
            
            return True
        
        except:
            return False

    else:
        return False
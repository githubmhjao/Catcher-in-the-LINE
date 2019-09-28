from __future__ import unicode_literals

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import TextSendMessage

import configparser

from apscheduler.schedulers.blocking import BlockingScheduler
import urllib
import datetime

# LINE 聊天機器人的基本資料
config = configparser.ConfigParser()
config.read('config.ini')

line_bot_api = LineBotApi(config.get('line-bot', 'channel_access_token'))
handler = WebhookHandler(config.get('line-bot', 'channel_secret'))

sched = BlockingScheduler()

@sched.scheduled_job('cron', day_of_week='mon-fri', minute='*/20')
def scheduled_job():
    print('========== APScheduler CRON =========')
    print('This job runs every weekday */20 min.')
    print(f'{datetime.datetime.now().ctime()}')
    print('========== APScheduler CRON =========')

    url = "https://你-APP-的名字.herokuapp.com/"
    conn = urllib.request.urlopen(url)

    for key, value in conn.getheaders():
        print(key, value)
        

@sched.scheduled_job('cron', day_of_week='mon-fri', hour=6, minute=30)
def scheduled_job():
    print('========== APScheduler CRON =========')
    print(' This job runs every weekday at 6:30 ')
    print('========== APScheduler CRON =========')

    line_bot_api.push_message(to, TextSendMessage(text=push_text))

sched.start()
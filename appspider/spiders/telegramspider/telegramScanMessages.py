# -*- coding: utf-8 -*-
# @Time    :   2021/09/10 16:37:40
# @Author  :   ddvv
# @公众号   :   NextB
# @File    :   telegramScanMessages.py
# @Software:   Visual Studio Code
# @Desc    :   None


import os
import scrapy
import base64
import json
from abc import ABC
from appspider.spiders.telegramspider.telegramAPIs import TelegramAPIs


class TelegramScanMessages(scrapy.Spider, ABC):
    name = "telegramScanMessages"

    # 降低效率，单线程，每个请求延迟4秒
    custom_settings = {
        'CONCURRENT_REQUESTS': 4,
        'DOWNLOAD_DELAY': 1
    }

    def __init__(self, param, **kwargs):
        super().__init__(**kwargs)
        s_param = base64.b64decode(param).decode()
        self.param = json.loads(s_param)
        self.api_id = self.param.get('api_id')
        self.api_hash = self.param.get('api_hash')
        self.session_name = self.param.get('session_name')
        self.group = self.param.get('group')

    def start_requests(self):
        yield scrapy.Request(url='https://baidu.com',
                             callback=self.parse_list)

    def parse_list(self, response):
        if not os.path.exists(self.session_name):
            print('session not exists.')
            return None
        yield from self.scan_messages()

    def scan_messages(self):
        telegram_app = TelegramAPIs()
        try:
            telegram_app.init_client(api_id=self.api_id, api_hash=self.api_hash, session_name=self.session_name)
        except Exception as e:
            print(str(e))
            return None
        try:
            # 开始爬取
            last_message_id = self.group['last_message_id']
            group_telegram_id = self.group['group_id']
            limit = self.group['limit']
            offset_date = self.group['offset_date']
            offset_date = offset_date if offset_date else None
            chat = telegram_app.get_dialog(group_telegram_id, is_more=False)
            if chat:
                param = {
                    'limit': limit,
                    'offset_date': offset_date,
                    'last_message_id': last_message_id
                    }
                try:
                    for m in telegram_app.scan_message(chat=chat, **param):
                        yield m
                except Exception as e:
                    print(str(e))
            else:
                print('Nont find Chat')
        except Exception as e:
            print(str(e))
        finally:
            telegram_app.close_client()

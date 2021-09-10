# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from appspider.items import TelegramMessage
from appspider.configs.postgreconfig import db_config

"""
后续需要将所有的输出结果统一到一个pipeline里，根据爬虫选择输出方式
"""

template_conn_str = "postgresql+psycopg2://{username}:{password}@{address}:{port}/{db_name}"
conn_str = template_conn_str.format(**db_config)


class AppspiderPostgreslPipeline(object):
    def __init__(self):
        self.session_maker = None
        self.datas = []
        self.push_number = 50

    def open_spider(self, spider):
        engine = create_engine(conn_str)
        if self.session_maker is None:
            self.session_maker = scoped_session(sessionmaker(autoflush=True, autocommit=False,
                                                             bind=engine))

    def process_item(self, item, spider):
        if len(self.datas) >= self.push_number:
            for data in self.datas:
                new_messaeg = TelegramMessage()
                new_messaeg.message_id = data.get('message_id', -1)
                new_messaeg.chat_id = data.get('chat_id', -1)
                new_messaeg.user_id = data.get('user_id', -1)
                new_messaeg.user_name = data.get('user_name', '')
                new_messaeg.nick_name = data.get('nick_name', '')
                new_messaeg.postal_time = data.get('postal_time', '')
                new_messaeg.message = data.get('message', '')
                self.session_maker.add(new_messaeg)
            self.session_maker.commit()
            self.datas = []
        else:
            if item:
                self.datas.append(item)
        return item

    def close_spider(self, spider):
        if len(self.datas) > 0:
            for data in self.datas:
                new_messaeg = TelegramMessage()
                new_messaeg.message_id = data.get('message_id', -1)
                new_messaeg.chat_id = data.get('chat_id', -1)
                new_messaeg.user_id = data.get('user_id', -1)
                new_messaeg.user_name = data.get('user_name', '')
                new_messaeg.nick_name = data.get('nick_name', '')
                new_messaeg.postal_time = data.get('postal_time', '')
                new_messaeg.message = data.get('message', '')
                self.session_maker.add(new_messaeg)
            self.session_maker.commit()
            self.datas = []
        self.session_maker.close_all()


class AppspiderTxtPipeline(object):
    def open_spider(self, spider):
        self.file = open(spider.name + '.txt', 'a')

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        line = json.dumps(dict(item)) + "\n"
        self.file.write(line)
        return item

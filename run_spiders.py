# -*- coding: utf-8 -*-
# @Time    :   2021/09/10 10:03:50
# @Author  :   ddvv
# @公众号   :   NextB
# @File    :   create_db.py
# @Software:   Visual Studio Code
# @Desc    :   None


import sys
import base64
import json
from scrapy import cmdline
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from appspider.items import TelegramMessage
from appspider.configs.postgreconfig import db_config


class NextBTGDB:
    def __init__(self):
        self.engine = self.init_db_connection(**db_config)
        self.session_maker = None
        self.create_session()

    @staticmethod
    def init_db_connection(address, port, username, password, db_name):
        values = {
            'address': address,
            'port': port,
            'username': username,
            'password': password,
            'db_name': db_name
        }
        template_conn_str = "postgresql+psycopg2://{username}:{password}@{address}:{port}/{db_name}"
        conn_str = template_conn_str.format(**values)
        engine = create_engine(conn_str)
        return engine

    # DRbmfj86yJ3sqv21X5fo9A
    def create_session(self):
        if self.session_maker is None:
            self.session_maker = scoped_session(sessionmaker(autoflush=True, autocommit=False,
                                                             bind=self.engine))
    
    def search_message(self, chat_id):
        data = self.session_maker.query(TelegramMessage).filter(TelegramMessage.chat_id == chat_id).order_by(TelegramMessage.id.desc()).limit(1)
        if data.count():
            return data[0]
        else:
            return {}
    

def main():
    with open(sys.argv[1], 'r') as f:
        data = f.read()
    config_js = json.loads(data)
    nb = NextBTGDB()
    chat_id = config_js.get('group', {}).get('group_id')
    message_data = nb.search_message(chat_id=chat_id)
    if message_data:
        config_js['group']['last_message_id'] = message_data.message_id
    param_base64 = base64.b64encode(json.dumps(config_js).encode()).decode()
    name = 'telegramScanMessages'
    cmd = 'scrapy crawl {name} -L INFO -a param={param_base64}'.format(name=name, param_base64=param_base64)
    cmdline.execute(cmd.split())

if __name__ == '__main__':
    main()
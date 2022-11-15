# -*- coding: utf-8 -*-
# @Time     : 2022/11/11 17:50:16
# @Author   : ddvv
# @Site     : https://ddvvmmzz.github.io
# @File     : run_spiders_sqlite.py
# @Software : Visual Studio Code
# @WeChat   : NextB


import sys
import base64
import json
from scrapy import cmdline
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from appspider.spiders.telegramspider.telegramAPIs import TelegramAPIs
from appspider.items import TelegramMessage, Base


class NextBTGSQLITEDB:
    def __init__(self, db_name):
        self.engine = self.init_db_connection(db_name)
        self.session_maker = None
        self.create_session()

    @staticmethod
    def init_db_connection(db_name):
        conn_str = "sqlite:///{db_name}".format(db_name=db_name)
        engine = create_engine(conn_str)
        return engine

    # DRbmfj86yJ3sqv21X5fo9A
    def create_session(self):
        if self.session_maker is None:
            self.session_maker = scoped_session(
                sessionmaker(autoflush=True, autocommit=False, bind=self.engine)
            )

    # 创建表
    def create_table(self):
        Base.metadata.create_all(self.engine)

    def search_message(self, chat_id):
        data = (
            self.session_maker.query(TelegramMessage)
            .filter(TelegramMessage.chat_id == chat_id)
            .order_by(TelegramMessage.id.desc())
            .limit(1)
        )
        if data.count():
            return data[0]
        else:
            return {}


def main():
    # 加载配置文件
    # with open(sys.argv[1], 'r') as f:
    #     data = f.read()
    # config_js = json.loads(data)
    # # 创建表
    # nb = NextBTGSQLITEDB(config_js.get("sqlite_db_name", "sqlite.db"))
    # nb.create_table()
    # 登录tg账户,生成登录文件
    # ta = TelegramAPIs()
    # ta.init_client(session_name=config_js.get('session_name'), api_id=config_js.get('api_id'), api_hash=config_js.get('api_hash'))
    # 删除所有聊天对话框
    # ta.delete_all_dialog()
    # 获取对话框信息
    # dialogs = list()
    # for dialog in ta.get_dialog_list():
    #     dialogs.append(dialog)
    # print(json.dumps(dialogs, ensure_ascii=False))
    # 测试爬取消息
    # group = config_js.get('group')
    # chat = ta.get_dialog(group.get('group_id'), is_more=False)
    # param = {
    #     'limit': group.get('limit'),
    #     'offset_date': None,
    #     'last_message_id': group.get('last_message_id')
    # }
    # for data in ta.scan_message(chat, **param):
    #     print(data)
    # ta.close_client()
    # 工作代码
    with open(sys.argv[1], "r") as f:
        data = f.read()
    config_js = json.loads(data)
    nb = NextBTGSQLITEDB(config_js.get("sqlite_db_name", "sqlite.db"))
    chat_id = config_js.get("group", {}).get("group_id")
    message_data = nb.search_message(chat_id=chat_id)
    if message_data:
        config_js["group"]["last_message_id"] = message_data.message_id
    param_base64 = base64.b64encode(json.dumps(config_js).encode()).decode()
    name = "telegramScanMessages"
    cmd = "scrapy crawl {name} -L INFO -a param={param_base64} -s db_name={db_name}".format(
        name=name,
        param_base64=param_base64,
        db_name=config_js.get("sqlite_db_name", "tg_sqlite.db"),
    )
    cmdline.execute(cmd.split())


if __name__ == "__main__":
    main()

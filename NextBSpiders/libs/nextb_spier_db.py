# -*- coding: utf-8 -*-
# @Time     : 2022/11/16 11:02:47
# @Author   : ddvv
# @Site     : https://ddvvmmzz.github.io
# @File     : nextb_spier_db.py
# @Software : Visual Studio Code
# @WeChat   : NextB

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from NextBSpiders.items import TelegramMessage, Base


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

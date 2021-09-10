# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy

from sqlalchemy import Column, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.sqltypes import INTEGER

Base = declarative_base()

class TelegramMessage(Base):
    __tablename__ = 'nextb_telegram_messages'

    id = Column(INTEGER(), primary_key=True, unique=True, autoincrement=True)
    message_id = Column(INTEGER())
    chat_id = Column(INTEGER())
    user_id = Column(INTEGER())
    user_name = Column(String(255))
    nick_name = Column(String(255))
    postal_time = Column(String(255))
    message = Column(String(5096))

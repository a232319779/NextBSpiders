# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy

from sqlalchemy import Column, String, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.sqltypes import DateTime, BIGINT, Integer

Base = declarative_base()


class TelegramMessage(Base):
    __tablename__ = "nextb_telegram_messages"

    # postgresql
    # id = Column(BIGINT(), primary_key=True, unique=True, autoincrement=True)
    # sqlite
    id = Column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True)
    message_id = Column(BIGINT())
    chat_id = Column(BIGINT())
    user_id = Column(BIGINT())
    user_name = Column(String(255))
    nick_name = Column(String(255))
    postal_time = Column(DateTime)
    reply_to_msg_id = Column(BIGINT())
    from_name = Column(String(255))
    from_time = Column(DateTime)
    message = Column(String(5096))

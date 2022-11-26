# -*- coding: utf-8 -*-
# @Time     : 2022/11/26 16:17:07
# @Author   : ddvv
# @Site     : https://ddvvmmzz.github.io
# @File     : statics_db.py
# @Software : Visual Studio Code
# @WeChat   : NextB


import datetime
import argparse
from NextBSpiders import NEXTBSPIDER_VERSION
from NextBSpiders.libs.nextb_spier_db import NextBTGSQLITEDB


def parse_cmd():
    """
    解析命令行参数
    """
    parser = argparse.ArgumentParser(
        prog="nextb-statics-db",
        description="NextBSpider统计数据库基本情况。版本号：{}".format(NEXTBSPIDER_VERSION),
        epilog="使用方式：nextb-statics-db -d $db_name",
    )
    parser.add_argument(
        "-d",
        "--db_name",
        help="设置sqlite数据库文件路径",
        type=str,
        dest="db_name",
        action="store",
        default="",
    )

    args = parser.parse_args()

    return args


def statics_db(args):
    db_name = args.db_name
    db = NextBTGSQLITEDB(db_name=db_name)
    # 群组ID
    chat_id = 0
    # 发言数量
    message_count = db.get_message_count()
    # 用户数量
    user_count = db.get_user_distinct_count()
    # 获取第一条发言
    first_message = db.get_first_one_message()
    first_message_postal_time = "未获取"
    first_nick_name = ""
    if first_message:
        first_message_postal_time = datetime.datetime.strftime(first_message.postal_time, "%Y-%m-%d %H:%M:%S")
        first_nick_name = first_message.nick_name
        chat_id = first_message.chat_id
    # 获取最后一条发言
    last_message = db.get_last_one_message()
    last_message_postal_time = "未获取到"
    last_nick_name = ""
    if last_message:
        last_message_postal_time = datetime.datetime.strftime(last_message.postal_time, "%Y-%m-%d %H:%M:%S")
        last_nick_name = last_message.nick_name
        chat_id = first_message.chat_id

    # 打印统计信息
    print("群组ID: {}".format(chat_id))
    print("群组消息数量: {}".format(message_count))
    print("群组用户数量: {}".format(user_count))
    print("最早发言人: {}".format(first_nick_name))
    print("最早消息发送时间(UTC): {}".format(first_message_postal_time))
    print("最近发言人: {}".format(last_nick_name))
    print("最近消息发送时间(UTC): {}".format(last_message_postal_time))

    # 关闭数据库
    db.close()


def run():
    """
    CLI命令行入口
    """
    args = parse_cmd()
    statics_db(args)

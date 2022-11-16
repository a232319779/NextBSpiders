# -*- coding: utf-8 -*-
# @Time     : 2022/11/16 15:24:41
# @Author   : ddvv
# @Site     : https://ddvvmmzz.github.io
# @File     : telegram_run_spider.py
# @Software : Visual Studio Code
# @WeChat   : NextB


__doc__ = """
NextBSpider执行telegram爬虫命令行工具
"""

import argparse
import json
import base64
from scrapy import cmdline
from NextBSpiders.libs.nextb_spier_db import NextBTGSQLITEDB


def parse_cmd():
    """
    解析命令行参数
    """
    parser = argparse.ArgumentParser(
        prog="nextb-telegram-run-spider",
        description="NextBSpider执行telegram爬虫命令行工具。版本号：1.0.0",
        epilog="使用方式：nextb-telegram-run-spider -c $config_file",
    )
    parser.add_argument(
        "-c",
        "--config",
        help="设置爬虫配置文件",
        type=str,
        dest="config",
        action="store",
        default="./config.json",
    )

    args = parser.parse_args()

    return args


def telegram_run_spider(config_file):
    # 加载配置文件
    with open(config_file, "r") as f:
        data = f.read()
    config_js = json.loads(data)
    # 初始化数据库
    nb = NextBTGSQLITEDB(config_js.get("sqlite_db_name", "sqlite.db"))
    # 获取指定群组的最近一条telegram消息的
    chat_id = config_js.get("group", {}).get("group_id")
    message_data = nb.search_message(chat_id=chat_id)
    # 如果从数据库查询到消息，则更新配置参数
    if message_data:
        config_js["group"]["last_message_id"] = message_data.message_id
    # base64配置参数，传递给爬虫
    param_base64 = base64.b64encode(json.dumps(config_js).encode()).decode()
    name = "telegramScanMessages"
    cmd = "scrapy crawl {name} -L INFO -a param={param_base64} -s db_name={db_name}".format(
        name=name,
        param_base64=param_base64,
        db_name=config_js.get("sqlite_db_name", "tg_sqlite.db"),
    )
    cmdline.execute(cmd.split())


def run():
    """
    CLI命令行入口
    """
    args = parse_cmd()
    telegram_run_spider(args.config)

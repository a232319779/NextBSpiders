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

import os
import json
import base64
import argparse
# from scrapy import cmdline
from NextBSpiders import NEXTBSPIDER_VERSION
from NextBSpiders.libs.nextb_spier_db import NextBTGSQLITEDB

scrapy_cfg = """# Automatically created by: scrapy startproject
#
# For more information about the [deploy] section see:
# https://scrapyd.readthedocs.io/en/latest/deploy.html

[settings]
default = NextBSpiders.settings
"""

def process_scrapy_cfg_file():
    current_dir = os.path.abspath(".")
    scrapy_file = os.path.join(current_dir, "scrapy.cfg")
    if not os.path.exists(scrapy_file):
        with open(scrapy_file, "w") as f:
            f.write(scrapy_cfg)
            f.flush()

def parse_cmd():
    """
    解析命令行参数
    """
    parser = argparse.ArgumentParser(
        prog="nextb-telegram-run-spider",
        description="NextBSpider执行telegram爬虫命令行工具。{}".format(NEXTBSPIDER_VERSION),
        epilog="使用方式：nextb-telegram-run-spider -c $config_file1 -c $config_file2",
    )
    parser.add_argument(
        "-c",
        "--configs",
        help="设置爬虫配置文件，可指定多个配置文件，默认为空列表",
        type=str,
        dest="configs",
        action="append",
        default=[],
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
    # cmdline.execute(cmd.split())
    os.system(cmd)


def run():
    """
    CLI命令行入口
    """
    args = parse_cmd()
    process_scrapy_cfg_file()
    for config in args.configs:
        telegram_run_spider(config)

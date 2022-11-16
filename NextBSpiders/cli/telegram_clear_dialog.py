# -*- coding: utf-8 -*-
# @Time     : 2022/11/16 15:24:14
# @Author   : ddvv
# @Site     : https://ddvvmmzz.github.io
# @File     : telegram_clear_dialog.py
# @Software : Visual Studio Code
# @WeChat   : NextB


__doc__ = """
清理telegram的消息框
"""

import argparse
import json
from NextBSpiders.spiders.telegramspider.telegramAPIs import TelegramAPIs


def parse_cmd():
    """
    解析命令行参数
    """
    parser = argparse.ArgumentParser(
        prog="nextb-telegram-clear-dialog",
        description="NextBSpider清理telegram对话框。版本号：1.0.0",
        epilog="使用方式：nextb-telegram-clear-dialog -c $config_file -a 0",
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
    parser.add_argument(
        "-a",
        "--all",
        help="清理全部对话框或者删除账户对话框。默认值：0，仅清理删除账户对话框。",
        type=int,
        dest="all",
        action="store",
        default=0,
    )

    args = parser.parse_args()

    return args


def telegram_clear_dialog(config_file, all):
    # 加载配置文件
    with open(config_file, "r") as f:
        data = f.read()
    config_js = json.loads(data)
    ta = TelegramAPIs()
    session_name = config_js.get("session_name")
    api_id = config_js.get("api_id")
    api_hash = config_js.get("api_hash")
    proxy = config_js.get("proxy", {})
    clash_proxy = None
    # 如果配置代理
    if proxy:
        protocal = proxy.get("protocal", "socks5")
        proxy_ip = proxy.get("ip", "127.0.0.1")
        proxy_port = proxy.get("port", 7890)
        clash_proxy = (protocal, proxy_ip, proxy_port)
    ta.init_client(
        session_name=session_name, api_id=api_id, api_hash=api_hash, proxy=clash_proxy
    )
    # 删除所有聊天对话框
    ta.delete_all_dialog(is_all=all)
    ta.close_client()


def run():
    """
    CLI命令行入口
    """
    args = parse_cmd()
    telegram_clear_dialog(args.config, args.all)

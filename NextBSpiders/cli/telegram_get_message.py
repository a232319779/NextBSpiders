# -*- coding: utf-8 -*-
# @Time     : 2022/11/16 15:38:06
# @Author   : ddvv
# @Site     : https://ddvvmmzz.github.io
# @File     : telegram_get_message.py
# @Software : Visual Studio Code
# @WeChat   : NextB


__doc__ = """
获取telegram的消息
"""

import json
import datetime
import argparse
from NextBSpiders.spiders.telegramspider.telegramAPIs import TelegramAPIs


def parse_cmd():
    """
    解析命令行参数
    """
    parser = argparse.ArgumentParser(
        prog="nextb-telegram-get-message",
        description="NextBSpider获取telegram的聊天消息。版本号：1.0.0",
        epilog="使用方式：nextb-telegram-get-message -c $config_file",
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


def telegram_get_message(config_file):
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
    # 配置代理
    if proxy:
        protocal = proxy.get("protocal", "socks5")
        proxy_ip = proxy.get("ip", "127.0.0.1")
        proxy_port = proxy.get("port", 7890)
        clash_proxy = (protocal, proxy_ip, proxy_port)
    ta.init_client(
        session_name=session_name, api_id=api_id, api_hash=api_hash, proxy=clash_proxy
    )
    # 获取群组聊天消息
    group = config_js.get("group")
    chat = ta.get_dialog(group.get("group_id"), is_more=False)
    param = {
        "limit": group.get("limit"),
        "offset_date": None,
        "last_message_id": group.get("last_message_id"),
    }
    print("消息ID,用户昵称,用户username,用户id,发送时间,消息内容")
    for data in ta.scan_message(chat, **param):
        """data数据格式
        {
            "message_id": 57101,
            "user_id": 1259308451,
            "user_name": "victorliu857",
            "nick_name": "Victor Liu",
            "reply_to_msg_id": 0,
            "from_name": "",
            "from_time": "",
            "chat_id": 1277786921,
            "postal_time": "",
            "message": "😂"
        }
        """
        message_id = data.get("message_id", "")
        nick_name = data.get("nick_name", "")
        user_name = data.get("user_name", "")
        user_id = data.get("user_id", "")
        postal_time = data.get("postal_time", datetime.datetime.now()).strftime("%Y-%m-%d %H:%M:%S+%Z")
        message = data.get("message", "")
        print(
            "{},{},{},{},{},{}".format(
                message_id, nick_name, user_name, user_id, postal_time, message
            )
        )
    ta.close_client()


def run():
    """
    CLI命令行入口
    """
    args = parse_cmd()
    telegram_get_message(args.config)

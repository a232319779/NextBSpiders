# -*- coding: utf-8 -*-
# @Time     : 2022/11/19 20:01:59
# @Author   : ddvv
# @Site     : https://ddvvmmzz.github.io
# @File     : telegram_get_user_photo.py
# @Software : Visual Studio Code
# @WeChat   : NextB


__doc__ = """
获取telegram用户的头像
"""

import json
import argparse
from NextBSpiders import NEXTBSPIDER_VERSION
from NextBSpiders.spiders.telegramspider.telegramAPIs import TelegramAPIs


def read_nick_names(nick_name_file):
    with open(nick_name_file, "r", encoding="utf8") as f:
        datas = f.readlines()
        return [data.strip("\n").strip("\r") for data in datas]


def parse_cmd():
    """
    解析命令行参数
    """
    parser = argparse.ArgumentParser(
        prog="nextb-telegram-get-user-photo",
        description="NextBSpider获取telegram指定群组中用户的头像。版本号：{}".format(
            NEXTBSPIDER_VERSION
        ),
        epilog="使用方式：nextb-telegram-get-user-photo -c $config_file -f $nick_name_files ",
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
        "-n",
        "--name",
        help="设置用户昵称",
        type=str,
        dest="name",
        action="store",
        default="",
    )
    parser.add_argument(
        "-f",
        "--file",
        help="设置用户昵称文件，每行一个用户昵称。当设置用户昵称文件之后，会忽略用户昵称参数。",
        type=str,
        dest="file",
        action="store",
        default="",
    )
    parser.add_argument(
        "-p",
        "--path",
        help="设置头像保存路径。",
        type=str,
        dest="path",
        action="store",
        default="./",
    )

    args = parser.parse_args()

    return args


def telegram_get_user_photo(args):
    nick_names = []
    # 设置昵称
    if args.file:
        nick_names.extend(read_nick_names(args.file))
    elif args.name:
        nick_names.append(args.name)
    else:
        print("用户昵称或者用户昵称文件必须设置一个。当设置用户昵称文件之后，会忽略用户昵称参数。")
        exit(0)
    config_file = args.config
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
    group = config_js.get("group")
    chat_id = group.get("group_id")
    download_path = args.path
    ta.scan_user(chat_id=chat_id, nick_names=nick_names, download_path=download_path)
    ta.close_client()


def run():
    """
    CLI命令行入口
    """
    args = parse_cmd()
    telegram_get_user_photo(args)

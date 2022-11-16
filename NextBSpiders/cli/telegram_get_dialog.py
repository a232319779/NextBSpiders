# -*- coding: utf-8 -*-
# @Time     : 2022/11/16 15:24:31
# @Author   : ddvv
# @Site     : https://ddvvmmzz.github.io
# @File     : telegram_get_dialog.py
# @Software : Visual Studio Code
# @WeChat   : NextB


__doc__ = """
获取telegram的消息框
"""

import argparse
import json
from NextBSpiders.spiders.telegramspider.telegramAPIs import TelegramAPIs


def parse_cmd():
    """
    解析命令行参数
    """
    parser = argparse.ArgumentParser(
        prog="nextb-telegram-get-dialog",
        description="NextBSpider获取telegram对话框。版本号：1.0.0",
        epilog="使用方式：nextb-telegram-get-dialog -c $config_file",
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


def telegram_get_dialog(config_file):
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
    # 获取所有群组对话框
    print("群组ID,群组username,群组title,群组类型,群成员数量,未读消息数")
    for dialog in ta.get_dialog_list():
        """dialog格式
        {
        "result": "success",
        "reason": "ok",
        "data": {
            "id": 1136071376,
            "title": "币安官方中文群",
            "username": "BinanceChinese",
            "megagroup": "channel",
            "member_count": 155054,
            "channel_description": "币安官方中文TG群，谨防假冒 ！\n私聊都是诈骗\n\n所有涉及黄、黑、政治的话题都将被踢出，请大家共同维护社区秩序，营造友好的讨论环境，谢谢！\n\n官方网站: www.bitechan.org\n中文推特: twitter.com/binancezh\nDiscord: discord.gg/bnb\n公告频道: @binance_cn\nBNB Chain: @BNBChainZH\nAPI: @Binance_api_Chinese",
            "is_public": 1,
            "join_date": "2022-11-15 06:53:52+UTC",
            "unread_count": 20
        }
        """
        if dialog.get("result", "failed") == "success":
            data = dialog.get("data", None)
            if data is None:
                print("获取对话框数据失败")
                continue
            group_id = data.get("id", "")
            group_title = data.get("title", "")
            group_username = data.get("username", "")
            group_megagroup = data.get("megagroup", "")
            group_member_count = data.get("member_count", "")
            group_unread_count = data.get("unread_count", "")
            print(
                "{},{},{},{},{},{}".format(
                    group_id,
                    group_title,
                    group_username,
                    group_megagroup,
                    group_member_count,
                    group_unread_count,
                )
            )
    ta.close_client()


def run():
    """
    CLI命令行入口
    """
    args = parse_cmd()
    telegram_get_dialog(args.config)

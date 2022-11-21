# -*- coding: utf-8 -*-
# @Time     : 2022/11/17 15:01:01
# @Author   : ddvv
# @Site     : https://ddvvmmzz.github.io
# @File     : generate_user_message_csv.py
# @Software : Visual Studio Code
# @WeChat   : NextB

import datetime
import argparse
import urllib
from NextBSpiders import NEXTBSPIDER_VERSION
from NextBSpiders.libs.nextb_spier_db import NextBTGSQLITEDB


def check_url_valid(url):
    try:
        urllib.request.urlopen(url)
        print("{}：检测到该用户存在头像".format(url))
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print("{}：未发现该用户头像，使用默认头像".format(url))
            return False
    except Exception as e:
        print("{}：头像检测失败，使用默认头像".format(url))

    return True


def parse_cmd():
    """
    解析命令行参数
    """
    parser = argparse.ArgumentParser(
        prog="nextb-geneerate-user-message-csv",
        description="NextBSpider生成指定群组成员发送消息数量。版本号：{}".format(NEXTBSPIDER_VERSION),
        epilog="使用方式：nextb-geneerate-user-message-csv -d $db_name",
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
    parser.add_argument(
        "-t",
        "--time",
        help="指定统计的时间偏移。默认值为：1970-01-01 00:00:00，表示获取全部聊天记录",
        type=str,
        dest="time",
        action="store",
        default="1970-01-01 00:00:00",
    )
    parser.add_argument(
        "-f",
        "--file",
        help="保存csv的文件名，默认保存为当前路径的data.csv文件",
        type=str,
        dest="csv_file",
        action="store",
        default="./data.csv",
    )
    parser.add_argument(
        "-c",
        "--cut",
        help="指定的发言条数，过滤低于该值的用户，默认为：100，即只筛选出指定时间内发言数量超过100的用户",
        type=int,
        dest="cutoff",
        action="store",
        default=100,
    )
    parser.add_argument(
        "-u",
        "--url",
        help="指定用户头像的url地址，可以为空，形如：https://raw.githubusercontent.com/a232319779/NextBSpiderPhotos/main/photos/1144411934",
        type=str,
        dest="url",
        action="store",
        default="https://raw.githubusercontent.com/a232319779/NextBSpiderPhotos/main/photos/1144411934",
    )
    parser.add_argument(
        "-de",
        "--detect",
        help="检测用户头像在git上是否存在，默认值为0，表示不检测。（检测会很耗时）",
        type=int,
        dest="detect",
        action="store",
        default=0,
    )

    args = parser.parse_args()

    return args


def geneerate_user_message(args):
    db_name = args.db_name
    offset_time_str = args.time
    csv_file = args.csv_file
    cut_off = args.cutoff
    url = args.url
    detect = args.detect
    db = NextBTGSQLITEDB(db_name=db_name)
    offset_date = datetime.datetime.strptime(offset_time_str, "%Y-%m-%d %H:%M:%S")
    user_id_count = dict()
    user_id_nickname = dict()
    start_time = None
    end_time = None
    # 统计用户发言数量
    print("开始统计用户发言数量...")
    for data in db.get_messages(offset_date):
        user_id = data[0]
        nick_name = data[1]
        postal_time = data[2].strftime("%Y-%m-%d")
        if start_time is None:
            start_time = data[2]
        end_time = data[2]
        if user_id in user_id_count.keys():
            if postal_time in user_id_count[user_id].keys():
                user_id_count[user_id][postal_time] += 1
            else:
                user_id_count[user_id][postal_time] = 1
        else:
            user_id_count[user_id] = {}
            user_id_count[user_id][postal_time] = 1
        if user_id in user_id_nickname.keys():
            if nick_name not in user_id_nickname[user_id]:
                user_id_nickname[user_id].append(nick_name)
        else:
            user_id_nickname[user_id] = [nick_name]
    print("完成统计用户发言数量...")
    print("开始生成用户发言数量统计csv文件...")
    # 模拟输入起始及截止日期
    begin = datetime.date(start_time.year, start_time.month, start_time.day)
    end = datetime.date(end_time.year, end_time.month, end_time.day)

    # 获取时间列表
    day_list = list()
    dlt_days = (end - begin).days + 1
    for i in range(0, dlt_days):
        day = begin + datetime.timedelta(days=i)
        day_str = day.strftime("%Y-%m-%d")
        day_list.append(day_str)

    head = "用户名,头像url,{}".format(",".join(day_list))
    show_datas = dict()
    for user_id, value in user_id_count.items():
        count = list()
        sum = 0
        for day in day_list:
            sum += value.get(day, 0)
            count.append(str(sum))
        show_datas[user_id] = count
    r_datas = list()
    for user_id, value in show_datas.items():
        if int(value[-1]) < cut_off:
            continue
        nick_name = user_id
        for nn in user_id_nickname[user_id]:
            if nn != "":
                nick_name = nn
                break
        photo_url = "{}/{}.jpg".format(url, user_id)
        if detect and not check_url_valid(photo_url):
            photo_url = "https://raw.githubusercontent.com/a232319779/NextBSpiderPhotos/main/photos/default.jpg"
        data = "{},{},{}".format(nick_name, photo_url, ",".join(value))
        r_datas.append(data)

    # out_datas = [data for data in show_datas if int(data.split(",")[-1]) > cut_off]
    with open(csv_file, "w", encoding="utf8") as f:
        f.write(head + "\n")
        f.write("\n".join(r_datas))
        f.flush()
    print("csv文件生成完成，文件保存为：{}...".format(csv_file))
    print("过滤条数设定为{}时共计筛选{}个用户跨越{}天的聊天数量...".format(cut_off, len(r_datas), dlt_days))


def run():
    """
    CLI命令行入口
    """
    args = parse_cmd()
    geneerate_user_message(args)

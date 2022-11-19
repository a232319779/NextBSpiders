# -*- coding: utf-8 -*-
# @Time    :   2021/09/10 16:37:22
# @Author  :   ddvv
# @公众号   :   NextB
# @File    :   telegramAPIs.py
# @Software:   Visual Studio Code
# @Desc    :   None


import os
import time
import datetime
import logging
from random import randint
from telethon import TelegramClient, sync
from telethon.tl.functions.channels import (
    GetFullChannelRequest,
    JoinChannelRequest,
    GetParticipantsRequest,
)
from telethon.tl.functions.messages import (
    ImportChatInviteRequest,
    CheckChatInviteRequest,
    GetFullChatRequest,
)
from telethon.tl.functions.contacts import DeleteContactsRequest, GetContactsRequest
from telethon.tl.types import (
    ChatInviteAlready,
    ChatInvite,
    Message,
    Channel,
    Chat,
    ChannelForbidden,
    ChannelParticipantsSearch,
)


logging.basicConfig(level=logging.INFO)
logging.getLogger("telethon").setLevel(level=logging.INFO)
logging.getLogger("scrapy").setLevel(level=logging.INFO)


# TODO: make the hardcode code (e.g. BASE_PATH) as configurable in settings files
# TODO: use Sqlacademy ORM instead operation such data in low-level


class TelegramAPIs(object):
    def __init__(self):
        self.client = None

    def init_client(self, session_name, api_id, api_hash, proxy=None):
        """
        初始化client
        :param session_name: session文件名
        :param api_id: api id
        :param api_hash: api hash
        :param proxy: socks代理，默认为空
        """
        if proxy is None:
            self.client = TelegramClient(session_name, api_id, api_hash)
        else:
            self.client = TelegramClient(session_name, api_id, api_hash, proxy=proxy)
        self.client.start()

    def close_client(self):
        """
        关闭client
        """
        if self.client.is_connected():
            self.client.disconnect()

    # 加入频道或群组
    def join_conversation(self, invite):
        """
        加入方式主要分为
            1. 加入公开群组/频道：invite为username
            2. 加入私有群组/频道：invite为hash

        注意：需要测试如下两个逻辑，
            1. 换了群组的username之后，使用新username加入时的返回值(会显示无效，已测)
            2. 是否能直接通过ID加入(不能，通过id只能获取已经加入的频道/群组信息，并通过get_entity方法获取该频道的信息)
        :param invite: channel/group username/hash
        :return: 返回json, {'data': {'id':, 'chat':}, 'result': 'success/failed', 'reason':''}
        data: chat_id
        """
        # 每个加组的操作都休眠10秒先，降低速率
        time.sleep(10)
        chat_id = 0
        result = "Failed"
        result_json = {
            "data": {"id": chat_id, "group_name": invite},
            "result": result,
            "reason": "",
        }
        try:
            # Checking a link without joining
            # 检测私有频道或群组时，由于传入的是hash，可能会失败(已测试，除非是被禁止的，否则也会成功)
            updates = self.client(CheckChatInviteRequest(invite))
            if isinstance(updates, ChatInviteAlready):
                chat_id = updates.chat.id
                # chat = updates.chat
                result = "Done"
            elif isinstance(updates, ChatInvite):
                # Joining a private chat or channel
                updates = self.client(ImportChatInviteRequest(invite))
                # updates = self.client(CheckChatInviteRequest(invite))
                chat_id = updates.chats[0].id
                # chat = updates.chats[0]
                result = "Done"
        except Exception as e:
            try:
                # Joining a public chat or channel
                updates = self.client(JoinChannelRequest(invite))
                result = "Done"
            except Exception as ee:
                result_json["reason"] = str(ee)
                return result_json
            chat_id = updates.chats[0].id
            # chat = updates.chats[0]
        result_json["data"]["id"] = chat_id
        result_json["result"] = result

        return result_json

    def delete_all_dialog(self, is_all=0):
        """
        删除对话框
        """
        for dialog in self.client.get_dialogs():
            # like "4721 4720"、"5909 5908"
            name = dialog.name
            is_new_user = False
            if " " in name and ("1" in name or "3" in name or "6" in name):
                is_new_user = True
            # 退出频道或群组
            if is_all and hasattr(dialog.entity, "title"):
                chat = dialog.entity
                self.client.delete_dialog(chat)
                print("已离开<{}>群组".format(dialog.entity.title))
            # 删除delete account
            elif dialog.name == "":
                chat = dialog.entity
                self.client.delete_dialog(chat)
                print("已删除Deleted Account用户对话框")
            elif is_new_user:
                chat = dialog.entity
                self.client.delete_dialog(chat)
                print("已删除{}用户对话框".format(dialog.name))
            elif is_all:
                chat = dialog.entity
                self.client.delete_dialog(chat)
                print("已删除{}用户对话框".format(dialog.name))
            else:
                pass

    def get_me(self):
        """
        获取当前账户信息
        """
        myself = self.client.get_me()
        return myself

    def get_contacts(self):
        """
        获取联系人
        """
        contacts = self.client(GetContactsRequest(0))
        return contacts

    def delete_contact(self, ids):
        """
        删除联系人
        """
        self.client(DeleteContactsRequest(ids))

    def get_dialog_list(self):
        """
        获取已经加入的频道/群组列表
        :return: 返回json, {'data': [], 'result': 'success/failed', 'reason':''}
        data: list类型，
        """
        for dialog in self.client.get_dialogs():
            # 确保每次数据的准确性
            result_json = {"result": "success", "reason": "ok"}
            out = {}
            # 只爬取频道或群组，排除个人
            if hasattr(dialog.entity, "title"):
                chat = dialog.entity
                if isinstance(chat, Channel):
                    channel_full = self.client(GetFullChannelRequest(chat))
                    member_count = channel_full.full_chat.participants_count
                    channel_description = channel_full.full_chat.about
                    username = channel_full.chats[0].username
                    megagroup = channel_full.chats[0].megagroup
                elif isinstance(chat, Chat):
                    channel_full = self.client(GetFullChatRequest(chat.id))
                    member_count = channel_full.chats[0].participants_count
                    # channel_description = channel_full.full_chat.about
                    channel_description = ""
                    username = None
                    megagroup = True
                else:
                    yield result_json
                    continue
                # megagroup: true表示超级群组(官方说法)
                # 实际测试发现(TaiwanNumberOne该群组)，megagroup表示频道或群组，true表示群，false表示频道
                # democracy: 暂时不清楚什么意思
                out = {
                    "id": chat.id,
                    "title": chat.title,
                    "username": username,
                    # 'democracy': channel_full.chats[0].democracy,
                    "megagroup": "channel" if megagroup else "group",
                    "member_count": member_count,
                    "channel_description": channel_description,
                    "is_public": 1 if username else 0,
                    "join_date": chat.date.strftime("%Y-%m-%d %H:%M:%S+%Z"),
                    "unread_count": dialog.unread_count,
                }
                result_json["data"] = out
                yield result_json

    def get_dialog(self, chat_id, is_more=False):
        """
        方法一：通过遍历的方式获取chat对象，当chat_id相等时，返回
        方法二：对于已经加入的频道/群组，可以直接使用get_entity方法
        :param chat_id: 群组/频道 ID
        :param is_more: 默认为False，不使用遍历的方式
        :return: chat对象，用于后续操作
        """
        # 方法一
        if is_more:
            chat = None
            for dialog in self.client.get_dialogs():
                if dialog.entity.id == chat_id:
                    chat = dialog.entity
                    break
        # 方法二
        else:
            chat = self.client.get_entity(chat_id)

        return chat

    def scan_message(self, chat, **kwargs):
        """
        遍历消息
        :param chat:
        :param kwargs:
        """
        tick = 0
        waterline = randint(5, 20)
        limit = kwargs["limit"]
        min_id = kwargs["last_message_id"]
        # 默认只能从最远开始爬取
        offset_date = None
        if 0 and kwargs["offset_date"]:
            offset_date = datetime.datetime.strptime(
                kwargs["offset_date"], "%Y-%m-%d %H:%M:%S"
            )
        count = 0
        for message in self.client.iter_messages(
            chat,
            limit=limit,
            offset_date=offset_date,
            offset_id=min_id,
            wait_time=1,
            reverse=True,
        ):

            if isinstance(message, Message):
                content = ""
                try:
                    content = message.message
                except Exception as e:
                    print(e)
                if content == "":
                    continue
                m = dict()
                m["message_id"] = message.id
                m["user_id"] = 0
                m["user_name"] = ""
                m["nick_name"] = ""
                m["reply_to_msg_id"] = 0
                m["from_name"] = ""
                m["from_time"] = datetime.datetime.fromtimestamp(657224281)
                if message.sender:
                    m["user_id"] = message.sender.id
                    if isinstance(message.sender, ChannelForbidden):
                        username = ""
                    else:
                        username = message.sender.username
                        username = username if username else ""
                    m["user_name"] = username
                    if isinstance(message.sender, Channel) or isinstance(
                        message.sender, ChannelForbidden
                    ):
                        first_name = message.sender.title
                        last_name = ""
                    else:
                        first_name = message.sender.first_name
                        last_name = message.sender.last_name
                        first_name = first_name if first_name else ""
                        last_name = " " + last_name if last_name else ""
                    m["nick_name"] = "{0}{1}".format(first_name, last_name)
                if message.is_reply:
                    m["reply_to_msg_id"] = message.reply_to_msg_id
                if message.forward:
                    m["from_name"] = message.forward.from_name
                    m["from_time"] = message.forward.date
                m["chat_id"] = chat.id
                # m['postal_time'] = message.date.strftime('%Y-%m-%d %H:%M:%S')
                m["postal_time"] = message.date
                m["message"] = content
                tick += 1
                if tick >= waterline:
                    tick = 0
                    waterline = randint(5, 10)
                    time.sleep(waterline)
                count += 1
                yield m
        print("total: %d" % count)

    def download_user_photo(self, chat_id, nick_names, download_path="./"):
        """
        通过用户昵称下载用户头像
        :param chat: 频道/群组对象
        :param nick_names: 用户昵称列表
        download_path: 头像保存路径
        """
        chat = self.get_dialog(chat_id, is_more=True)
        for nick_name in nick_names:
            try:
                participants = self.client(
                    GetParticipantsRequest(
                        chat,
                        filter=ChannelParticipantsSearch(nick_name),
                        offset=0,
                        limit=randint(5, 10),
                        hash=0,
                    )
                )
            except Exception as e:
                print("查找《{}》用户失败，失败原因：{}".format(nick_name, str(e)))
                continue

            if not participants.users:
                print("未找到《{}》用户。".format(nick_name))
                continue

            for entity in participants.users:
                member_id = entity.id
                if entity.photo:
                    photo_down = os.path.join(download_path, "{}.jfif".format(member_id))
                    self.client.download_profile_photo(
                        entity, file=photo_down, download_big=False
                    )
                    print("《{}》用户头像保存至：{}".format(nick_name, photo_down))
                else:
                    print("《{}》用户没有使用自定义头像。".format(nick_name))

            print(
                "在《{}》群中找到{}个昵称为《{}》的用户，休眠5-10秒".format(
                    chat.title, len(participants.users), nick_name
                )
            )
            time.sleep(randint(5, 10))

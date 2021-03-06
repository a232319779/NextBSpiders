# -*- coding: utf-8 -*-
# @Time    :   2021/09/10 16:37:22
# @Author  :   ddvv
# @公众号   :   NextB
# @File    :   telegramAPIs.py
# @Software:   Visual Studio Code
# @Desc    :   None


import time
import datetime
import logging
from random import randint
from telethon import TelegramClient, sync
from telethon.tl.functions.channels import GetFullChannelRequest, JoinChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest, CheckChatInviteRequest, GetFullChatRequest
from telethon.tl.functions.contacts import DeleteContactsRequest, GetContactsRequest
from telethon.tl.types import ChatInviteAlready, ChatInvite
from telethon.tl.types import Message
from telethon.tl.types import Channel, Chat


is_local = True
if is_local:
    g_proxy = ("socks5", '127.0.0.1', 7890)
else:
    g_proxy = None

logging.basicConfig(level=logging.INFO)
logging.getLogger('telethon').setLevel(level=logging.INFO)
logging.getLogger('scrapy').setLevel(level=logging.INFO)


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
            proxy = g_proxy
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
        result = 'Failed'
        result_json = {'data': {'id': chat_id, 'group_name': invite}, 'result': result, 'reason': ''}
        try:
            # Checking a link without joining
            # 检测私有频道或群组时，由于传入的是hash，可能会失败(已测试，除非是被禁止的，否则也会成功)
            updates = self.client(CheckChatInviteRequest(invite))
            if isinstance(updates, ChatInviteAlready):
                chat_id = updates.chat.id
                # chat = updates.chat
                result = 'Done'
            elif isinstance(updates, ChatInvite):
                # Joining a private chat or channel
                updates = self.client(ImportChatInviteRequest(invite))
                # updates = self.client(CheckChatInviteRequest(invite))
                chat_id = updates.chats[0].id
                # chat = updates.chats[0]
                result = 'Done'
        except Exception as e:
            try:
                # Joining a public chat or channel
                updates = self.client(JoinChannelRequest(invite))
                result = 'Done'
            except Exception as ee:
                result_json['reason'] = str(ee)
                return result_json
            chat_id = updates.chats[0].id
            # chat = updates.chats[0]
        result_json['data']['id'] = chat_id
        result_json['result'] = result

        return result_json

    def get_me(self):
        myself = self.client.get_me()
        return myself

    def get_contacts(self):
        contacts = self.client(GetContactsRequest(0))
        return contacts

    def delete_contact(self, ids):
        self.client(DeleteContactsRequest(ids))

    def get_dialog_list(self):
        """
        获取已经加入的频道/群组列表
        :return: 返回json, {'data': [], 'result': 'success/failed', 'reason':''}
        data: list类型，
        """
        for dialog in self.client.get_dialogs():
            # 确保每次数据的准确性
            result_json = {'result': 'success', 'reason': 'ok'}
            out = {}
            # 只爬取频道或群组，排除个人
            if hasattr(dialog.entity, 'title'):
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
                    channel_description = ''
                    username = None
                    megagroup = True
                else:
                    yield result_json
                    continue
                # megagroup: true表示超级群组(官方说法)
                # 实际测试发现(TaiwanNumberOne该群组)，megagroup表示频道或群组，true表示群，false表示频道
                # democracy: 暂时不清楚什么意思
                out = {
                    'id': chat.id,
                    'title': chat.title,
                    'username': username,
                    # 'democracy': channel_full.chats[0].democracy,
                    'megagroup': 'channel' if megagroup else 'group',
                    'member_count': member_count,
                    'channel_description': channel_description,
                    'is_public': 1 if username else 0,
                    'join_date': chat.date.strftime('%Y-%m-%d %H:%M:%S+%Z'),
                    'unread_count': dialog.unread_count
                }
                result_json['data'] = out
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
        limit = kwargs['limit']
        min_id = kwargs['last_message_id']
        # 默认只能从最远开始爬取
        offset_date = None
        if 0 and kwargs['offset_date']:
            offset_date = datetime.datetime.strptime(kwargs['offset_date'], '%Y-%m-%d %H:%M:%S')
        count = 0
        for message in self.client.iter_messages(chat,
                                                 limit=limit,
                                                 offset_date=offset_date,
                                                 offset_id=min_id,
                                                 wait_time=1,
                                                 reverse=True):

            if isinstance(message, Message):
                content = ""
                try:
                    content = message.message
                except Exception as e:
                    print(e)
                if content == "":
                    continue
                m = dict()
                m['message_id'] = message.id
                m['user_id'] = -1
                m['user_name'] = ''
                m['nick_name'] = ''
                if message.sender:
                    m['user_id'] = message.sender.id
                    username = message.sender.username
                    username = username if username else ''
                    m['user_name'] = message.sender.username
                    if isinstance(message.sender, Channel):
                        first_name = message.sender.title
                        last_name = ''
                    else:
                        first_name = message.sender.first_name
                        last_name = message.sender.last_name
                        first_name = first_name if first_name else ''
                        last_name = ' '+ last_name if last_name else ''
                    m['nick_name'] = '{0}{1}'.format(first_name, last_name)
                m['chat_id'] = chat.id
                m['postal_time'] = message.date.strftime('%Y-%m-%d %H:%M:%S')
                m['message'] = content
                tick += 1
                if tick >= waterline:
                    tick = 0
                    waterline = randint(5, 10)
                    time.sleep(waterline)
                count += 1
                yield m
        print('total: %d' % count)

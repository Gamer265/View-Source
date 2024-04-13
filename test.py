# from telethon import TelegramClient, events
# import json

# PROXY = {
#     "proxy_type": 3,
#     "username": "f891iy4kds30751",
#     "password": "l315wdgrlthly3z",
#     "addr": "rp.proxyscrape.com",
#     "port": 6060,
# }
# with open("sessions/acc (82).json", "r") as f:
#     data = json.loads(f.read())
# bot = TelegramClient(
#     "sessions/" + data["session_file"].replace(".session", ""),
#     api_id=int(data["app_id"]),
#     api_hash=data["app_hash"],
# ).start()


# @bot.on(events.NewMessage())
# async def _(e):
#     print((await bot.get_me()))
#     print(e.text)

# print("started")
# bot.loop.run_forever()

# import requests
# url = 'https://ip.smartproxy.com/json'
# username = 'user-GamerX-country-bd'
# password = 'WE7kiozKb8ka75yqVr'
# proxy = f"socks5h://{username}:{password}@gate.smartproxy.com:7000"
# result = requests.get(url, proxies = {
#     'http': proxy,
#     'https': proxy
# })
# print(result.text)

import os

from socks import PROXY_TYPE_HTTP

from telethon.sync import TelegramClient
from telethon.sessions import StringSession

api_id = int(os.getenv('API_ID') or input("Enter your API_ID: "))
api_hash = os.getenv('API_HASH') or input("Enter your API_HASH: ")

with TelegramClient(StringSession(), api_id, api_hash) as client:
    print("\n" + client.session.save())

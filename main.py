import asyncio
import json
import os
from glob import glob
from sqlite3 import OperationalError
from traceback import format_exc


from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.errors.common import *
from telethon.errors.rpcerrorlist import *
from telethon.tl.functions.account import GetAuthorizationsRequest
from telethon.tl.functions.messages import GetMessagesViewsRequest, ImportChatInviteRequest
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.utils import get_peer_id

all_jsons = []
channels = []
active = {}
banned = []


API_ID = 27447487
API_HASH = "012b94d5275b4b0b3da9df20955159ac"
SESSION = "1AZWarzUBu26dzGuMfdA-L8sVIkJmvEDvNWUwlObtQOR1tNJMc8EqplU6G5N7MZPGyrxLNf9bVnkSiL6RNHpTKw7hV23iTLkVh3vZTSMJEtvV-qYmLQcRgz45fzwoT2ggEvQtijFnjJxCLXfUehafelO_eZFI7s74nNGkEkBHfRQQEo78TLToPlOBnEqI2B8MipoMCTlrWuq1roxhL83HWCx6nBn1OAPEr3eV9y--DZlKHxSmNJG6Uj7_NgsHjZ0--St6yHCXJoGe11LiEWyxtJF_PuaZ6d_LJg282GFTn49RusFHYobmMapnOQ1XnTpxoAe8qOlPg4yrrYo5wzWBXgnYdeGxh14="
FOLDER = "sessions"
ADMINS = [1872074304, 862271564]
PROXY = {
    "proxy_type": 3,
    "username": "f891iy4kds30751",
    "password": "l315wdgrlthly3z",
    "addr": "rp.proxyscrape.com",
    "port": 6060,
}

DATA = {}

try:
    bot = TelegramClient(
        StringSession(SESSION),
        api_id=API_ID,
        api_hash=API_HASH
    ).start()
except Exception as error:
    print(str(error))
    exit()

def link_parser_tg(link):
    hash = False
    if "@" in link:
        chat = link.strip().split()[0]
    elif "/joinchat/" in link:
        chat = link.split("/")[-1].replace("+", "")
        hash = True
    elif "+" in link:
        chat = link.split("/")[-1].replace("+", "")
        hash = True
    elif "-100" in link or link.isdigit():
        chat = int(link)
    else:
        chat = link.strip().split()[0]
    return chat, hash

async def join_channel(channel_id_text, client):
    chat, hash = link_parser_tg(channel_id_text)
    try:
        if hash:
            ch = await client(ImportChatInviteRequest(chat))
        else:
            ch = await client(JoinChannelRequest(chat))
    except BaseException:
        print(format_exc())

@bot.on(events.NewMessage(pattern="^/deltask"))
async def detkdd(e):
    try:
        id = int(e.text.split()[1])
    except:
        return await e.reply("Invalid Input")
    if id in DATA:
        DATA.pop(id)
        return await e.reply("done")
    return await e.reply("task not found")

@bot.on(events.NewMessage(pattern="^/tasks"))
async def tkdd(e):
    x = "Working Tasks: \n\n"
    for id in DATA.keys():
        x += f"`{id}`\n"
    await e.reply(x)

@bot.on(events.NewMessage(pattern="^/watch ?(.*)"))
async def _todo(event):
    if event.sender_id not in ADMINS:
        return
    try:
        async with bot.conversation(event.sender_id, timeout=2000) as conv:
            await conv.send_message(
                "Process Started. You Can Send /cancel Anytime To Abort This Process.\n"
            )
            await conv.send_message("Send Channel Username or Link")
            try:
                link = (await conv.get_response()).text
                if link.startswith("/cancel"):
                    return await conv.send_message("Proccess Aborted!")
                _chat_id, hash = link_parser_tg(link)
                if not bot.is_connected:
                    await bot.connect()
                chat_id = get_peer_id(await bot.get_entity(_chat_id))
                await join_channel(_chat_id, bot)
                if chat_id in DATA:
                    return await conv.send_message("Its Already On Watching List.")
            except BaseException:
                return await conv.send_message("Invalid Input")
            await conv.send_message(f'Total There Are {len(active.keys())} Clients.')
            DATA.update({chat_id: {"username": _chat_id}})
            await conv.send_message(f"Sucessfully Added Your Task And Your Task ID is `{chat_id}`")
    except TimeoutError:
        pass

def get_all_files(folders):
    lst = []
    if isinstance(folders, str):
        folders = [folders]
    while folders:
        folder = os.path.join(folders.pop(), "*")
        files = glob(folder)
        if not files:
            break
        for file in files:
            if os.path.isdir(file):
                folders.append(file)
            else:
                lst.append(file)
    return lst


def load_jsons(folder):
    for js_file in get_all_files(folder):
        if "session-journal" in js_file:
            try:
                os.remove(js_file)
            except BaseException:
                pass
        elif js_file.endswith(".json"):
            sess_file = js_file.replace(".json", ".session")
            if not os.path.isfile(sess_file):
                continue
            try:
                with open(js_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    f.close()
                data["sess_file"] = sess_file
                data["json_file"] = js_file
                all_jsons.append(data)
            except KeyError:
                os.remove(js_file)
            except BaseException:
                print(
                    f"Error {format_exc()} has happened while going through json files {js_file}",
                )

loop = bot.loop

def run_thread(func, args=[]):
    try:
        loop.run_until_complete(func(*args))
    except (
        TypeNotFoundError,
        SecurityError,
        InvalidBufferError,
        RuntimeError,
        ConnectionError,
        RuntimeError,
        GeneratorExit,
    ):
        pass
    except KeyboardInterrupt:
        print("Exiting due to ctrl+c")
        os._exit(1)
    except BaseException:
        print(f"Error {format_exc()} Has Occured In run_thread function")


async def give_views(client: TelegramClient, chat_username, msg_id: int):
    try:
        await client(GetMessagesViewsRequest(chat_username, [msg_id], increment=True))
    except (UserBannedInChannelError, ChannelPrivateError):
        print(f"{client.phone} is Banned in @{chat_username}")
    except (FloodWaitError, PeerFloodError, ChatInvalidError):
        print(f"{client.phone} Got FloodWait/PeerFlood")
    except (UserDeactivatedBanError, UserDeactivatedError):
        print(f"{client.phone} Got DELETED by Telegram")
        await move_client(client, "account_banned")
    except ConnectionError:
        pass
    except BaseException:
        print(str(format_exc()))


async def desc(client: TelegramClient):
    try:

        async def periodic():
            if client.is_connected():
                await client.disconnect()

        def stop():
            task.cancel()

        client.loop.call_later(5, stop)
        task = client.loop.create_task(periodic())
        await task
    except (RuntimeError, GeneratorExit):
        pass
    except asyncio.CancelledError:
        print(f"{client.phone} was stuck in disconnect since 30 sec")
    except BaseException:
        pass


async def move_client(client: TelegramClient, to_dir) -> None:
    await desc(client)
    sess_file = client.json["sess_file"]
    json_file = client.json["json_file"]
    moved = False
    for file in [sess_file, json_file]:
        if os.path.isfile(file):
            try:
                if not os.path.isdir(to_dir):
                    os.mkdir(to_dir)
                new_file = os.path.join(
                    to_dir,
                    os.path.basename(os.path.normpath(file)),
                )
                if not os.path.isfile(new_file):
                    os.rename(file, new_file)
                    moved = True
                if os.path.isfile(file):
                    os.remove(file)
            except BaseException as e:
                print(f"{file} {e}")
    if moved:
        print(f"Moved {client.phone} To Folder: {to_dir}")


async def login(data: dict) -> TelegramClient:
    proxi = dict(PROXY)
    try:
        phone = data["phone"]
        if active.get(phone):
            if not active[phone].is_connected():
                await active[phone].connect()
            return active[phone]
        client = TelegramClient(
            data["sess_file"].replace(".session", ""),
            api_id=int(data["app_id"]),
            api_hash=data["app_hash"],
            system_version=data["sdk"],
            app_version=data["app_version"],
            device_model=data["device"],
            system_lang_code=data.get("system_lang_pack")
            or data.get("lang_pack")
            or "en",
            lang_code=data.get("lang_pack") or "en",
            proxy=proxi,
            flood_sleep_threshold=120,
            timeout=15,
            auto_reconnect=True,
            request_retries=2,
            connection_retries=2,
        )
        client.json = data
        client.phone = phone

        async def periodic():
            await client.connect()

        def stop():
            task.cancel()

        # loop = asyncio.get_event_loop()
        client.loop.call_later(30, stop)
        task = client.loop.create_task(periodic())

        try:
            await task
        except (RuntimeError, GeneratorExit):
            return
        except asyncio.CancelledError:
            print(f"{client.phone} was stuck in connect since 30 sec")
            return await move_client(client, "account_connection_error")

        if not await client.is_user_authorized():
            try:
                await client.disconnect()
            except BaseException:
                pass
            print(f"Number: {client.phone} Login Code Needed")
            await move_client(client, "account_login_code_needed")
            return
        client.me = await client.get_me()
        if not client.me.phone:
            raise ConnectionError(None)
        active[phone] = client
    except (PhoneCodeExpiredError, PhoneCodeInvalidError):
        print(f"Number: {phone}'s Code Invalid or Expired")
        return
    except PhoneNumberInvalidError:
        print(f"Number: {phone} is Invalid.")
        return
    except (AuthKeyDuplicatedError):
        print(
            f"Number: {phone} is having AuthkeyDupliate issue.",
        )
        await move_client(client, "account_auth_duplicate")
        return
    except SessionRevokedError:
        print(f"{phone} Session Is Revoked.")
        await move_client(client, "account_session_revoked")
    except (PasswordHashInvalidError, SessionPasswordNeededError):
        print(f"Number: {phone} 2fa Password Wrong or Empty.")
        await move_client(client, "account_2fa_wrong")
        return
    except (PhoneNumberBannedError, UserDeactivatedError):
        print(f"Number: {phone} is banned")
        await move_client(client, "account_banned")
        return
    except FloodWaitError:
        print(f"Number: {phone} having FloodWaits")
        return
    except (InvalidBufferError, SecurityError, TypeNotFoundError):
        print(f"Number: {phone} is having api error.")
        await move_client(client, "account_api_error")
        return
    except OperationalError:
        print(f"Number: {phone} having database lock error.")
        return
    except ConnectionError:
        print(f"{phone} Connection Error")
        return
    except BaseException:
        print(f"{phone} Error has occured: {format_exc()}")
        return
    await asyncio.sleep(3)

    auths = await client(GetAuthorizationsRequest())
    for auth in auths.authorizations:
        if auth.current:
            print(
                f"{phone} Logged in successfully | IP: {auth.ip} | Country: {auth.country}"
            )

    return client

@bot.on(events.NewMessage(func=lambda e: not e.is_private))
async def on_new_post(e: events.NewMessage.Event):
    chs = list(DATA.keys())
    th = await e.get_chat()
    id = get_peer_id(th)
    if id in chs:
        try:
            clients = await validateAccounts(_return=True)
            print(f"Giving Views With {len(clients)} Clients.")
            username = DATA[id]["username"]
            await asyncio.gather(*[give_views(client, username, e.id) for client in clients])
            print(f"Succesfully Given Views To {username}/{e.id}")
        except BaseException:
            print(str(format_exc()))

async def validateAccounts(_return=False, off=False):
    task = []
    for adder in all_jsons:
        task.append(login(adder))
    clients = [cli for cli in await asyncio.gather(*task) if cli]
    if _return:
        return clients
    if off:
        return await asyncio.gather(*[desc(cli) for cli in clients])
    print(f"Sucesfully Loaded {len(clients)}")

load_jsons(FOLDER)
run_thread(validateAccounts)
try:
    loop.run_forever()
except KeyboardInterrupt:
    print("Disconnecting The Clients...!")
    run_thread(validateAccounts, [False, True])
    os._exit(1)
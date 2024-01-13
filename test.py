# import requests
# username = "f891iy4kds30751"
# password = "l315wdgrlthly3z"
# proxy = "rp.proxyscrape.com:6060"
# proxy_auth = "{}:{}@{}".format(username, password, proxy)
# proxies = {
#     "http":"http://{}".format(proxy_auth)
# }
# urlToGet = "http://ip-api.com/json"
# r = requests.get(urlToGet , proxies=proxies)
# print("Response:\n{}".format(r.text))

import os, sys, glob

def get_all_files(folders):
    lst = []
    if isinstance(folders, str):
        folders = [folders]
    while folders:
        folder = os.path.join(folders.pop(), "*")
        files = glob.glob(folder)
        if not files:
            break
        for file in files:
            if os.path.isdir(file):
                folders.append(file)
            else:
                lst.append(file)
    return lst

print(get_all_files("sessions/"))
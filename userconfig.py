"""
实现用户校验
"""
import json
import os
import threading

lock = threading.Lock()
userconfig_json_file = os.getenv("MYGPT_USERCONFIG_FILEPATH")

def check_user(username,password):
    with lock:
        with open(userconfig_json_file,encoding="utf8") as f:
            datajson = json.loads(f.read())
        if username in datajson:
            if password == datajson.get(username).get("password"):
                return True
        return False


def check_quota(username):
    with lock:
        with open(userconfig_json_file,encoding="utf8") as f:
            datajson = json.loads(f.read())
        if username in datajson:
            visited = datajson[username]["visited"]
            quota = datajson[username]["quota"]
            if visited > quota:
                raise Exception(f"你已经用完配额了，已经用了{visited}次，配额是{quota}")

            datajson[username]["visited"] += 1
            with open(userconfig_json_file,"w", encoding="utf8") as f:
                f.write(json.dumps(datajson,ensure_ascii=False,indent=4))


def get_quotas(username):
    with lock:
        with open(userconfig_json_file,encoding="utf8") as f:
            datajson = json.loads(f.read())
        if username in datajson:
            visited = datajson[username]["visited"]
            quota = datajson[username]["quota"]
        return f"你当前的总配额是{quota},已经用了{visited},还有{quota - visited}数量"


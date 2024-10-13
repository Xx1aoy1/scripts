import requests
import json
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import time
from datetime import datetime
import binascii
import base64
import threading
UA = "Mozilla/5.0 (Linux; Android 11; Redmi Note 10 Pro Build/RP1A.201005.004; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/92.0.4515.159 Mobile Safari/537.36"
PHONE_V = "17588888880@15288888888"
TASK_IDS = [121, 122,123,124, 125] 
infocode = {
    "121":"阅读15分钟任务",
    "122":"阅读120分钟任务",
    "123":"阅读240分钟任务",
    "124":"阅读360分钟任务",
    "125":"阅读480分钟任务"
}
ACTIVE_ID = "20"
REQ_NUM = 10
DELAY = 0.2

headers = {
    "User-Agent": UA,
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Pragma": "no-cache",
    "Cache-Control": "no-cache",
    "sec-ch-ua": '"Android WebView";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
    "accesstoken": "ODZERTZCMjA1NTg1MTFFNDNFMThDRDYw",
    "Content-Type": "application/json;charset=UTF-8",
    "sec-ch-ua-mobile": "?1",
    "sec-ch-ua-platform": '"Android"',
    "Origin": "https://10010.woread.com.cn",
    "X-Requested-With": "com.sinovatech.unicom.ui",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Referer": "https://10010.woread.com.cn/ng_woread/",
    "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
}
def utf8_parse(s):
    return s.encode('utf-8')
def get_aes(data, key):
    iv = "gnirtS--setyB-61"[::-1].encode('utf-8')
    key = key.encode('utf-8')
    key_hex = binascii.hexlify(key).decode('utf-8')
    iv_hex = binascii.hexlify(iv).decode('utf-8')
    iv = bytes.fromhex(iv_hex)
    key = bytes.fromhex(key_hex)
    json_string = json.dumps(data, separators=(',', ':'))
    utf8_string = json_string.encode('utf-8')
    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted = cipher.encrypt(pad(utf8_string, AES.block_size))
    encrypted_hex = encrypted.hex()
    return base64.b64encode(encrypted_hex.encode('utf-8')).decode('utf-8')
def get_aes_v(body,task_id):
    token = body["data"]["token"]
    user_id = body["data"]["userid"]
    user_index = body["data"]["userindex"]
    user_account = body["data"]["phone"]
    verify_code = body["data"]["verifycode"]

    e1 = {"datav": {"activeId": ACTIVE_ID, "taskId":task_id}}
    result1 = get_aes({
        **e1["datav"],
        "timestamp": datetime.now().strftime("%Y%m%d%H%M%S"),
        "token": token,
        "userAccount": user_account,
        "userId": user_id,
        "userIndex": user_index,
        "verifyCode": verify_code
    }, "woreadst^&*12345")

    # print(result1)
    return result1
def get_aes_phone(data, key):
    iv = utf8_parse("gnirtS--setyB-61"[::-1])
    key = utf8_parse(key)
    phone = utf8_parse(data)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted = cipher.encrypt(pad(phone, AES.block_size))
    hex_str = binascii.hexlify(encrypted).decode('utf-8')
    return base64.b64encode(hex_str.encode('utf-8')).decode('utf-8')
def process_task(token, task_id):
    data = json.dumps({"sign": token})
    headers2 = headers.copy()
    headers2["Content-Type"] = "application/json;charset=UTF-8"

    try:
        response = requests.post(
            "https://10010.woread.com.cn/ng_woread_service/rest/activity423/receiveActiveTask",
            headers=headers2,
            data=data
        )
        response_data = response.json()
        print(f"Task {infocode[str(task_id)]}: {response_data.get('message', 'No message')}")
    except Exception as error:
        print(f"请求失败，任务ID:{task_id}:", error)

    time.sleep(DELAY)

def get_aes_v_task(tokens):
    threads = []
    for i in range(REQ_NUM):
        token_index = i % len(tokens)
        token = tokens[token_index]
        task_id = TASK_IDS[i % len(TASK_IDS)]

        thread = threading.Thread(target=process_task, args=(token, task_id))
        time.sleep(0.3)
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()


    print(datetime.now().strftime("%H:%M:%S:%f")[:-3])
def login(phone):
    e = {"data": {"phone": get_aes_phone(phone, "woreadst^&*12345")}}
    result = get_aes({**e["data"], "timestamp": datetime.now().strftime("%Y%m%d%H%M%S")}, "woreadst^&*12345")
    data = json.dumps({"sign": result})
    response = requests.post(
        "https://10010.woread.com.cn/ng_woread_service/rest/account/login",
        headers=headers,
        data=data
    )

    if response.status_code == 200:
        login_response = response.json()
        tokens = []
        for task_id in TASK_IDS:
            token = get_aes_v({
                "data": {
                    "token": login_response["data"]["token"],
                    "userid": login_response["data"]["userid"],
                    "userindex": login_response["data"]["userindex"],
                    "phone": login_response["data"]["phone"],
                    "verifycode": login_response["data"]["verifycode"]
                }
            }, task_id)
            tokens.append(token)
        
        get_aes_v_task(tokens)
    else:
        print(f"登录失败: {phone}")

def main():
    threads = []
    PHONElist = PHONE_V.split('@')
    for phone in PHONElist:
        thread = threading.Thread(target=login, args=(phone,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

if __name__ == "__main__":
    main()
    print("All tasks processed.")

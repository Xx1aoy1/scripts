#福田抽奖活动可能一次性的 账户#密码 多账户换行
import requests
import json
import os
import random
import time

response = requests.get("https://mkjt.jdmk.xyz/mkjt.txt")
response.encoding = 'utf-8'
txt = response.text
print(txt)


def mask_phone(phone):
    """将手机号中间四位替换为****"""
    return phone[:3] + "****" + phone[-4:]


def user_login(phone, password):
    url = "https://czyl.foton.com.cn/ehomes-new/homeManager/getLoginMember"
    payload = {
        "version_name": "",
        "checkCode": "",
        "redisCheckCodeKey": "",
        "deviceSystem": "18.1",
        "device_type": "0",
        "password": password,
        "ip": "127.0.0.1",
        "device_id": "",
        "version_code": "0",
        "name": phone,
        "device_model": "iPhone 12"
    }
    headers = {
        'User-Agent': "Feature_Alimighty/7.4.7 (iPhone; iOS 18.1; Scale/2.00)",
        'Content-Type': "application/json",
        'Accept-Language': "zh-Hans-CN;q=1"
    }
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    result = response.json()
    if result.get("code") == 200 and result.get("data"):
        masked_phone = mask_phone(phone)
        print(f"[账号信息] >>> {masked_phone}")
        return result["data"].get("memberComplexCode", "")
    else:
        print("[错误] >>> 登录失败")
        return None


def lottery(encrypt_member_id):
    url = "https://czyl.foton.com.cn/shareCars/c250401/luckyDraw.action"
    payload = {
        'encryptMemberId': encrypt_member_id,
        'activityNum': "250401"
    }
    headers = {
        'User-Agent': "Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) ftejIOS",
        'Accept': "application/json, text/javascript, */*; q=0.01",
        'X-Requested-With': "XMLHttpRequest",
        'Accept-Language': "zh-CN,zh-Hans;q=0.9",
        'Origin': "https://czyl.foton.com.cn",
        'Referer': f"https://czyl.foton.com.cn/shareCars/activity/interactCenter250401/draw.html?memberComplexCode=91FB5410A00AF62FD61FC29D&memberId=2490728&encryptedMemberId={encrypt_member_id}&mobile=13580250305",
        'Cookie': "SESSION=47011cc8-f4eb-425e-a7a7-e3a2cec35b49; HWWAFSESID=17d2311e2d739c87a23; HWWAFSESTIME=1742228658251"
    }
    response = requests.post(url, data=payload, headers=headers)
    result = response.json()
    print(f"[抽奖结果] >>> {result.get('msg', '未知')}")


def main(token):
    if "#" not in token:
        print("[错误] >>> token 格式错误，应为 '手机号#密码'")
        return
    phone, password = token.split("#", 1)
    encrypt_member_id = user_login(phone, password)
    if encrypt_member_id:
        for _ in range(3):  # 添加循环，让每个账号抽奖三次
            wait_time = random.randint(3, 5)
            time.sleep(wait_time)
            lottery(encrypt_member_id)
    else:
        print("[错误] >>> 未获取到有效的登录信息")


if __name__ == "__main__":
    env = os.getenv("FTEJ")
    if env:
        TOKEN = os.environ.get("FTEJ")
    else:
        print("未检测到环境变量 futian_bks，启用内置变量")
        TOKEN = ""
    tokenList = TOKEN.split("\n")
    #random.shuffle(tokenList)
    print(f"🔔 >>>>> 共检测到[{len(tokenList)}]个账号 开始运行抽奖活动")
    for index, token in enumerate(tokenList):
        print(f"-------- 第[{index + 1}]个账号 --------")
        main(token)
        time.sleep(2)

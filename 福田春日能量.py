import requests
import json
import os
import random
import time


def mask_phone(phone):
    """将手机号中间四位替换为****"""
    return phone[:3] + "****" + phone[-4:]


def user_login(phone, password):
    url = "https://czyl.foton.com.cn/ehomes-new/homeManager/getLoginMember"

    # 新的payload，包括新的参数
    payload = {
        "version_name": "",
        "checkCode": "",
        "redisCheckCodeKey": "",
        "deviceSystem": "18.1",
        "version_auth": "VajbZ5PWOpX/UO3RuYODVg==",
        "device_type": "0",
        "password": password,
        "ip": "127.0.0.1",
        "device_id": "",
        "version_code": "0",
        "name": phone,
        "device_model": "iPhone 12"
    }

    headers = {
        'User-Agent': "Feature_Alimighty/7.4.8 (iPhone; iOS 18.1; Scale/2.00)",
        'Content-Type': "application/json",
        'Accept-Language': "zh-Hans-CN;q=1"
    }

    # 发送登录请求
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    result = response.json()

    if result.get("code") == 200 and result.get("data"):
        masked_phone = mask_phone(phone)
        print(f"[账号信息] >>> {masked_phone}")
        # 获取新的 memberComplexCode 和 memberId
        memberComplexCode = result["data"].get("memberComplexCode", "")
        memberId = result["data"].get("memberID", "")
        return memberComplexCode, memberId
    else:
        print("[错误] >>> 登录失败")
        return None, None


def lottery(encrypt_member_id, memberComplexCode, memberId, draw_count):
    url = "https://czyl.foton.com.cn/shareCars/c250401/luckyDraw.action"
    payload = {
        'encryptMemberId': encrypt_member_id,
        'activityNum': "250401"
    }
    headers = {
        'User-Agent': "Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) ftejIOS",
        'Accept': "application/json, text/javascript, */*; q=0.01",
        'X-Requested-With': "XMLHttpRequest",
        'Sec-Fetch-Site': "same-origin",
        'Accept-Language': "zh-CN,zh-Hans;q=0.9",
        'Sec-Fetch-Mode': "cors",
        'Origin': "https://czyl.foton.com.cn",
        'Referer': f"https://czyl.foton.com.cn/shareCars/activity/interactCenter250401/draw.html?memberComplexCode={memberComplexCode}&memberId={memberId}",
        'Sec-Fetch-Dest': "empty",
        'Cookie': "SESSION=b2b36558-cafa-4162-9d1a-a152c2dbf1b9; HWWAFSESID=843ee7cb1e59857e7d; HWWAFSESTIME=1744555656144"
    }
    response = requests.post(url, data=payload, headers=headers)
    result = response.json()

    # 检查抽奖次数
    if 'msg' in result and result['msg'] == "没有抽奖次数":
        print(f"[第{draw_count}次抽奖结果] >>> 没有抽奖次数")
        return False  # 返回 False 表示没有抽奖次数
    else:
        print(f"[第{draw_count}次抽奖结果] >>> {result.get('msg', '未知')}")
        return True  # 返回 True 表示抽奖成功


def main(token):
    if "#" not in token:
        print("[错误] >>> token 格式错误，应为 '手机号#密码'")
        return
    phone, password = token.split("#", 1)
    memberComplexCode, memberId = user_login(phone, password)
    if memberComplexCode and memberId:
        encrypt_member_id = memberComplexCode  # 假设 encrypt_member_id 与 memberComplexCode 相同
        # 执行三次抽奖
        for i in range(1, 4):
            wait_time = 3  # 设置为3秒
            time.sleep(wait_time)
            if not lottery(encrypt_member_id, memberComplexCode, memberId, i):
                print("[跳过] >>> 无抽奖次数，跳过当前账号")
                break  # 如果没有抽奖次数，跳过当前账号
    else:
        print("[错误] >>> 未获取到有效的登录信息")


if __name__ == "__main__":
    env = os.getenv("Fukuda")
    if env:
        TOKEN = os.environ.get("Fukuda")
    else:
        print("未检测到环境变量 Fukuda，启用内置变量")
        TOKEN = ""
    tokenList = TOKEN.split("&")
    random.shuffle(tokenList)
    print(f"🔔 >>>>> 共检测到[{len(tokenList)}]个账号 开始运行")
    for index, token in enumerate(tokenList):
        print(f"-------- 第[{index + 1}]个账号 --------")
        main(token)
        time.sleep(1)

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


def check_prize_status(encrypt_member_id, memberComplexCode, memberId, draw_count):
    """查询中奖记录"""
    url = "https://czyl.foton.com.cn/shareCars/c250401/myAwards.action"

    payload = {
        'encryptMemberId': encrypt_member_id
    }

    headers = {
        'User-Agent': "Mozilla/5.0 (iPhone; CPU iPhone OS 18_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) ftejIOS",
        'Accept': "application/json, text/javascript, */*; q=0.01",
        'X-Requested-With': "XMLHttpRequest",
        'Sec-Fetch-Site': "same-origin",
        'Accept-Language': "zh-CN,zh-Hans;q=0.9",
        'Sec-Fetch-Mode': "cors",
        'Origin': "https://czyl.foton.com.cn",
        'Referer': f"https://czyl.foton.com.cn/shareCars/activity/interactCenter250401/myReward.html?memberComplexCode={memberComplexCode}",
        'Sec-Fetch-Dest': "empty",
        'Cookie': "SESSION=b2b36558-cafa-4162-9d1a-a152c2dbf1b9; HWWAFSESID=843ee7cb1e59857e7d; HWWAFSESTIME=1744555656144"
    }

    response = requests.post(url, data=payload, headers=headers)

    # 检查响应的状态码
    if response.status_code != 200:
        print(f"[中奖查询] >>> 请求失败，状态码: {response.status_code}")
        return False

    # 尝试解析 JSON 响应
    try:
        result = response.json()
    except json.JSONDecodeError:
        print(f"[中奖查询] >>> 无效的 JSON 响应: {response.text}")
        return False

    # 检查返回的数据
    if result.get("code") == 0:
        data = json.loads(result.get("data", "[]"))  # 转换成列表
        if data:
            for prize in data:
                award_name = prize.get("award_name", "未知奖品")
                award_time = prize.get("awardTime", "未知时间")
                print(f"[中奖信息] >>> 奖品: {award_name}, 中奖时间: {award_time}")
            return True  # 返回True表示成功获取中奖信息
        else:
            print(f"[中奖查询] >>> 未中奖")
            return False
    else:
        print(f"[中奖查询] >>> 查询失败，错误信息: {result.get('msg', '无详细信息')}")
        return False


def main(token):
    if "#" not in token:
        print("[错误] >>> token 格式错误，应为 '手机号#密码'")
        return
    phone, password = token.split("#", 1)
    memberComplexCode, memberId = user_login(phone, password)
    if memberComplexCode and memberId:
        encrypt_member_id = memberComplexCode  # 假设 encrypt_member_id 与 memberComplexCode 相同
        # 只执行一次中奖查询
        wait_time = 3  # 设置为3秒
        time.sleep(wait_time)
        if not check_prize_status(encrypt_member_id, memberComplexCode, memberId, 1):
            print("[跳过] >>> 没有中奖，跳过当前账号")
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

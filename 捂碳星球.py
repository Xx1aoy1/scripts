"""
name: 捂碳星球旧衣服回收，1元起提
Author: MK集团本部
Date: 2024-09-24
export wtxq="authorization"
cron: 0 5 * * *
"""
#import notify
import requests, json, os, sys, time, random,datetime
response = requests.get("https://mkjt.jdmk.xyz/mkjt.txt")
response.encoding = 'utf-8'
txt = response.text
print(txt)
#---------------------主代码区块---------------------
session = requests.session()

def userinfo(authorization):
    url = 'https://wt.api.5tan.com/api/user/index?platform=1'
    header = {
        "Connection": "keep-alive",
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; MI 8 Build/QKQ1.190828.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/126.0.6478.188 Mobile Safari/537.36 XWEB/1260117 MMWEBSDK/20240501 MMWEBID/3169 MicroMessenger/8.0.50.2701(0x2800325B) WeChat/arm64 Weixin NetType/WIFI Language/zh_CN ABI/arm64 MiniProgramEnv/android",
        "content-type": "application/x-www-form-urlencoded",
        "authorization": authorization
    }
    data = ""
    try:
        response = session.get(url=url, headers=header, data=data)
        info = json.loads(response.text)
        if "nick_name" in info["data"]:
            if info["data"]["nick_name"] == "游客":
                pass
            else:
                return info["data"]["nick_name"],info["data"]["money"]
    except Exception as e:
        print(e)

def run(authorization):
    userinfo(authorization)
    login = 'https://wt.api.5tan.com/api/signin/addSignIn'
    header = {
        "Connection": "keep-alive",
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; MI 8 Build/QKQ1.190828.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/126.0.6478.188 Mobile Safari/537.36 XWEB/1260117 MMWEBSDK/20240501 MMWEBID/3169 MicroMessenger/8.0.50.2701(0x2800325B) WeChat/arm64 Weixin NetType/WIFI Language/zh_CN ABI/arm64 MiniProgramEnv/android",
        "content-type": "application/json",
        "authorization": authorization
    }
    data = {"platform": 1}
    try:
        response = session.post(url=login, headers=header, json=data)
        login = json.loads(response.text)
        a , b = userinfo(authorization)
        if "ok" in login["msg"]:
            print(f"📱：{a}\n☁️签到：成功\n🌈余额：{b}元")
            if float(b) >= 1:
                money(authorization,b)
        elif "签到" in login["msg"]:
            print(f"📱：{a}\n☁️签到：成功\n🌈余额：{b}元")
            if float(b) >= 1:
                money(authorization,b)
        else:
            print(f"📱：账号已过期或异常：{login['msg']}")
    except Exception as e:
        print(e)

def money(authorization,mon):
    url = 'https://wt.api.5tan.com/api/logmoney/cash'
    header = {
        "Connection": "keep-alive",
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; MI 8 Build/QKQ1.190828.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/126.0.6478.188 Mobile Safari/537.36 XWEB/1260117 MMWEBSDK/20240501 MMWEBID/3169 MicroMessenger/8.0.50.2701(0x2800325B) WeChat/arm64 Weixin NetType/WIFI Language/zh_CN ABI/arm64 MiniProgramEnv/android",
        "content-type": "application/json",
        "authorization": authorization
    }
    data = {"money":mon,"platform":1}
    try:
        response = session.post(url=url, headers=header, json=data)
        moneynow = json.loads(response.text)
        print(f"🌈余额提现：{moneynow['msg']}")
        time.sleep(1)
    except Exception as e:
        print(e)

def main():
    if os.environ.get("wtxq"):
        ck = os.environ.get("wtxq")
    else:
        ck = ""
        if ck == "":
            print("请设置变量")
            sys.exit()

    if datetime.datetime.strptime('05:01','%H:%M').time() <= datetime.datetime.now().time() <= datetime.datetime.strptime('06:59', '%H:%M').time():
        time.sleep(random.randint(100, 500))
    ck_run = ck.split('\n')
    print(f"{' ' * 10}꧁༺ 捂碳༒星球 ༻꧂\n")
    for i, ck_run_n in enumerate(ck_run):
        print(f'\n----------- 🍺账号【{i + 1}/{len(ck_run)}】执行🍺 -----------')
        try:
            run(ck_run_n)
            time.sleep(random.randint(1, 2))
        except Exception as e:
            print(e)
            #notify.send('title', 'message')

    print(f'\n----------- 🎊 执 行  结 束 🎊 -----------')


if __name__ == '__main__':
    main()

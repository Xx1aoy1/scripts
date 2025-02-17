"""
name: 植白说
Author: MK集团本部
export TOKEN="mark#X-Dts-Token"
cron: 0 5 * * *
const $ = new Env("植白说");
#小程序://植白说/yeLIAPOZ9bD7hoH
"""
#import notify
import requests, json, re, os, sys, time, random, datetime, execjs
response = requests.get("https://mkjt.jdmk.xyz/mkjt.txt")
response.encoding = 'utf-8'
txt = response.text
print(txt)
environ = "zbs"
name = "植白༒说说"
session = requests.session()
#---------------------主代码区块---------------------

def run(Token):
    header = {
        "Connection": "keep-alive",
        "Host": "www.kozbs.com",
        "xweb_xhr": "1",
        "Content-type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090b13)XWEB/11581",
        "X-Dts-Token": Token,
        "Accept": "*/*",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "cross-site",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
    }
    try:
        url = 'https://www.kozbs.com/demo/wx/home/sign'
        response = session.get(url=url, headers=header).json()
        if response["errno"] == 0:
            print(f"🌥️签到：成功")
        else:
            print(response)
        url = 'https://www.kozbs.com/demo/wx/user/addIntegralByShare'
        response = session.get(url=url, headers=header).json()
        if response["errno"] == 0:
            print(f"🌥️分享：成功")
        else:
            print(response)
        print(f"-----今日任务-----")
        url = 'https://www.kozbs.com/demo/wx/user/getUserIntegral'
        response = session.get(url=url, headers=header).json()
        name = {2:"签到",8:"分享",10:"抽奖",3:"完善",}
        if response["errno"] == 0:
            for i in response['data']['list']:
                createTime = i["createTime"]
                if datetime.datetime.strptime(createTime, "%Y-%m-%d %H:%M:%S").date() == datetime.datetime.now().date():
                    print(f"🌥️{name.get(i['type'],'未入录')}：{i['integral']}积分")
            print(f"-----积分信息-----")
            print(f"🌥️累计：{response['data']['integer']}积分")
        else:
            print(response)

    except Exception as e:
        print(e)

def dh(Token):
    header = {
        "Connection": "keep-alive",
        "Host": "www.kozbs.com",
        "xweb_xhr": "1",
        "Content-type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090b13)XWEB/11581",
        "X-Dts-Token": Token,
        "Accept": "*/*",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "cross-site",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
    }
    try:
        print(f'\n----------- 🍺 兑 换  商 品 🍺 -----------')
        url = 'https://www.kozbs.com/demo/wx/goods/integralShopList'
        response = session.get(url=url, headers=header).json()
        if response["errno"] == 0:
            list = response.get("data")["goodsList"]
            for item in list:
                # print(item)
                goodsName = item.get("goodsName","").split("兑换】")[-1].split("「植白说」")[-1]
                integralPrice = item.get("integralPrice")
                leftNumber = item.get("leftNumber")
                if leftNumber != 0:
                    print(f"{goodsName}：{integralPrice}积分 -【余{leftNumber}】")
        else:
            print(response)
    except Exception as e:
        print(e)

def main():
    if os.environ.get(environ):
        ck = os.environ.get(environ)
    else:
        ck = ""
        if ck == "":
            print("请设置变量")
            sys.exit()
    ck_run = ck.split('\n')
    ck_run = [item for item in ck_run if item]
    print(f"{' ' * 10}꧁༺ {name} ༻꧂\n")

    for i, ck_run_n in enumerate(ck_run):
        id, two = ck_run_n.split('#', 2)
        if i == 0:
            dh(two)
        print(f'\n----------- 🍺账号【{i + 1}/{len(ck_run)}】执行🍺 -----------')
        try:
            id = id[:3] + "*****" + id[-3:]
            print(f"📱：{id}")
            run(two)
            time.sleep(random.randint(1, 2))
        except Exception as e:
            print(e)
            #notify.send('title', 'message')
    print(f'\n----------- 🎊 执 行  结 束 🎊 -----------')

if __name__ == '__main__':
    main()

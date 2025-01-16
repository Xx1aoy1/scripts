"""
name: 农夫山泉76行定位地址直接改有水地址并发便可,本脚本是并发本
Author: MK集团本部
Date: 0000-00-00
export nfsq="备注#apitoken"
cron: 0 5 * * *
"""
#import notify
import requests, json, re, os, sys, time, random, datetime, execjs
response = requests.get("https://mkjt.jdmk.xyz/mkjt.txt")
response.encoding = 'utf-8'
txt = response.text
print(txt)
environ = "nfsq"
name = "农夫༒山泉"
session = requests.session()
#---------------------主代码区块---------------------

def taskdo(apitoken,taskid,name):
    header = {
        "Host": "gateway.jmhd8.com",
        "Connection": "keep-alive",
        "unique_identity": "5400823e-b872-4187-8987-9721936191d2",
        "apitoken": apitoken,
        "content-type": "application/x-www-form-urlencoded",
        "charset": "utf-8",
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; MI 8 Build/QKQ1.190828.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/130.0.6723.103 Mobile Safari/537.36 XWEB/1300259 MMWEBSDK/20241103 MMWEBID/6533 MicroMessenger/8.0.55.2780(0x28003737) WeChat/arm64 Weixin NetType/WIFI Language/zh_CN ABI/arm64 MiniProgramEnv/android",
    }
    url = f'https://gateway.jmhd8.com/geement.marketingplay/api/v1/task/join?action_time=2025-01-01%2008%3A07%3A27&task_id={taskid}'
    try:
        for i in range(100):
            response = session.get(url=url, headers=header)
            response = json.loads(response.text)
            if "处理成功" in response["msg"]:
                #print(f"☁️{name}:抽奖次数 +1")
                pass
            elif "已参与" in response["msg"]:
                break
            else:
                break
    except Exception as e:
        print(e)

def task(apitoken):
    header = {
        "Host": "gateway.jmhd8.com",
        "Connection": "keep-alive",
        "unique_identity": "5400823e-b872-4187-8987-9721936191d2",
        "apitoken": apitoken,
        "content-type": "application/x-www-form-urlencoded",
        "charset": "utf-8",
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; MI 8 Build/QKQ1.190828.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/130.0.6723.103 Mobile Safari/537.36 XWEB/1300259 MMWEBSDK/20241103 MMWEBID/6533 MicroMessenger/8.0.55.2780(0x28003737) WeChat/arm64 Weixin NetType/WIFI Language/zh_CN ABI/arm64 MiniProgramEnv/android",
    }
    url = 'https://gateway.jmhd8.com/geement.marketingplay/api/v1/task?pageNum=1&pageSize=10&task_status=2&status=1&group_id=24121016331837'
    try:
        response = session.get(url=url, headers=header)
        response = json.loads(response.text)
        if response["success"] == True:
            for i in response["data"]:
                taskid = i["id"]
                name = i["name"]
                taskdo(apitoken,taskid,name)
            time.sleep(5)
    except Exception as e:
        print(e)

def gamelottery(apitoken):
    header = {
        "Host": "thirtypro.jmhd8.com",
        "Connection": "keep-alive",
        "unique_identity": "5400823e-b872-4187-8987-9721936191d2",
        "apitoken": apitoken,
        "Content-Length": "202",
        "content-type": "application/json",
        "charset": "utf-8",
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; MI 8 Build/QKQ1.190828.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/130.0.6723.103 Mobile Safari/537.36 XWEB/1300259 MMWEBSDK/20241103 MMWEBID/6533 MicroMessenger/8.0.55.2780(0x28003737) WeChat/arm64 Weixin NetType/WIFI Language/zh_CN ABI/arm64 MiniProgramEnv/android",
    }
    url = 'https://thirtypro.jmhd8.com/api/v1/nongfuwater/snake/checkerboard/lottery'
    gamecode = "SCENE-24121018362724"
    data = {"code":gamecode,"provice_name":"上海市","city_name":"上海市","area_name":"浦东新区","address":"上海市浦东新区泰公线人渡","longitude":121.506379,"dimension":31.245414}
    try:
        for m in range(100):
            response = session.post(url=url, headers=header,json=data)
            response = json.loads(response.text)
            if response["success"] == True:
                prize_name = response["data"]['prizedto']['prize_name']
                prize_level = response["data"]['prizedto']["prize_level"]
                for i in response["data"]['prizedto']["goods"]:
                    goods_name = i["goods_name"]
                    #print(f"☁️游戏：{prize_name}{prize_level}:{goods_name}")
                    print(f"☁️游戏：{goods_name}")
            elif "用尽" in response['msg']:
                #print(f"⭕游戏：次数用尽")
                print(f"⭕游戏：{response['msg']}")
                break
            else:
                print(f"⭕游戏：{response['msg']}")
                break
    except Exception as e:
        print(e)

def marketinglottery(apitoken,code=True):
    header = {
        "Host": "gateway.jmhd8.com",
        "Connection": "keep-alive",
        "unique_identity": "5400823e-b872-4187-8987-9721936191d2",
        "apitoken": apitoken,
        "Content-Length": "202",
        "content-type": "application/json",
        "charset": "utf-8",
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; MI 8 Build/QKQ1.190828.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/130.0.6723.103 Mobile Safari/537.36 XWEB/1300259 MMWEBSDK/20241103 MMWEBID/6533 MicroMessenger/8.0.55.2780(0x28003737) WeChat/arm64 Weixin NetType/WIFI Language/zh_CN ABI/arm64 MiniProgramEnv/android",
    }
    url = 'https://gateway.jmhd8.com/geement.marketinglottery/api/v1/marketinglottery'
    if code:
        marketcode = "SCENE-24121018345681" #日常池3次
    else:
        marketcode = "SCENE-24121018352070" #任务池7次
    data = {"code":marketcode,"provice_name":"上海市","city_name":"上海市","area_name":"浦东新区","address":"上海市浦东新区泰公线人渡","longitude":121.506379,"dimension":31.245414}
    try:
        for i in range(100):
            response = session.post(url=url, headers=header,json=data)
            response = json.loads(response.text)
            if response["success"] == True:
                prize_name = response["data"]['prizedto']['prize_name']
                prize_level = response["data"]['prizedto']["prize_level"]
                for i in response["data"]['prizedto']["goods"]:
                    goods_name = i["goods_name"]
                    print(f"☁️抽奖：{goods_name}")
            elif "已经达到最大" in response['msg']:
                #print(f"⭕抽奖：日常池次数用尽")
                break
            elif "不足" in response['msg']:
                #print(f"⭕抽奖：任务池次数用尽")
                print(f"⭕抽奖：次数用尽")
                break
            else:
                print(f"⭕抽奖：{response['msg']}")
                break
            time.sleep(0.5)
    except Exception as e:
        print(e)

def info(apitoken):
    header = {
        "Host": "gateway.jmhd8.com",
        "Connection": "keep-alive",
        "unique_identity": "5400823e-b872-4187-8987-9721936191d2",
        "apitoken": apitoken,
        "content-type": "application/x-www-form-urlencoded",
        "charset": "utf-8",
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; MI 8 Build/QKQ1.190828.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/130.0.6723.103 Mobile Safari/537.36 XWEB/1300259 MMWEBSDK/20241103 MMWEBID/6533 MicroMessenger/8.0.55.2780(0x28003737) WeChat/arm64 Weixin NetType/WIFI Language/zh_CN ABI/arm64 MiniProgramEnv/android",
    }
    url = 'https://gateway.jmhd8.com/geement.actjextra/api/v1/act/win/goods/simple?act_codes=ACT2412101428048%2CACT24121014352835%2CACT24121014371732'
    header["apitoken"] = apitoken
    try:
        response = session.get(url=url, headers=header)
        response = json.loads(response.text)
        if response["success"] == True:
            for i in response["data"]:
                goods_name = i['win_goods_name']
                prize_name = i['win_prize_name']
                prize_level = i["win_prize_level"]
                if ("特等奖" in prize_name or "特等奖" in prize_level or "一等奖" in prize_name or "一等奖" in prize_level or "乙巳蛇年典藏版玻璃瓶装天然矿泉水" in goods_name) and "十一等奖" not in prize_level:
                    print(f"🌈{prize_level}{prize_name}：{goods_name}")
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
        print(f'\n----------- 🍺账号【{i + 1}/{len(ck_run)}】执行🍺 -----------')
        try:
            id,two = ck_run_n.split('#',1)
            #id = id[:3] + "*****" + id[-3:]
            print(f"📱：{id}")
            task(two)
            print(f"-------棋盘-------")
            gamelottery(two)
            print(f"-------抽奖-------")
            marketinglottery(two)
            marketinglottery(two,False)
            print(f"------------------")
            info(two)
            time.sleep(random.randint(1, 2))
        except Exception as e:
            print(e)
            #notify.send('title', 'message')
    print(f'\n----------- 🎊 执 行  结 束 🎊 -----------')

if __name__ == '__main__':
    main()

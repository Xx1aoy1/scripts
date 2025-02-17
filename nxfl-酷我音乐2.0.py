'''
Description: 
Author: 南下风来
Date: 2025-02-10 18:00:22
LastEditTime: 2025-02-14 23:07:11
LastEditors: 南下风来
'''


'''
酷我音乐签到脚本
抓登录包url:安卓：http://ar.i.kuwo.cn/US_NEW/kuwo/login_kw的q值
ios：http://ip.i.kuwo.cn/US_NEW/kuwo/login_kw的q值(需要自行替换LOGIN_URL)
还有：https://integralapi.kuwo.cn/api/v1/online/sign/v1/getWithdraw 的phone值
变量：kuwo = appUid#devId#q#phone#备注
'''

"""
cron: 0 0 7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23 * * *
new Env('酷我音乐2.0');
"""

import os
import requests
import time
import datetime
import logging
import re  # 新增

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 常量
LOGIN_URL = "http://ar.i.kuwo.cn/US_NEW/kuwo/login_kw"
BASE_URL = 'https://integralapi.kuwo.cn/api/v1/online/sign/v1/earningSignIn/newDoListen'
LUCKY_URL = 'https://integralapi.kuwo.cn/api/v1/online/sign/loterry/getLucky'
BOX_URL = 'https://integralapi.kuwo.cn/api/v1/online/sign/new/newBoxFinish'
SIGN_URL = 'https://integralapi.kuwo.cn/api/v1/online/sign/v1/earningSignIn/newUserSignList'

HEADERS = {'User-Agent': 'Mozilla/5.0 (Linux; Android 14; LE2110 Build/UKQ1.230924.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/117.0.0.0 Mobile Safari/537.36/ kuwopage'}
TIME_PERIODS = [(0, 8, "00-08"), (8, 10, "08-10"), (10, 12, "10-12"), (12, 14, "12-14"), (14, 16, "14-16"), (16, 18, "16-18"), (18, 20, "18-20"), (20, 24, "20-24")]
listens = [36,43,56,68,75,88,99,108,188]

def make_request(url, params=None, headers=None):
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"请求失败: {e}")
        return None

def login(q):
    params = {
        'f': 'ar',
        'q': q
    }
    
    response = requests.get(LOGIN_URL, headers=HEADERS, params=params)
    try:
        username = re.search(r'uname3=([^;]+)', response.headers['Set-Cookie']).group(1)
        loginSid = re.search(r'websid=([^;]+)', response.headers['Set-Cookie']).group(1)
        loginUid = re.search(r'userid=([^;]+)', response.headers['Set-Cookie']).group(1)
        return username, loginSid, loginUid
    except Exception as e:
        logging.error(f"登录解析失败: {e}")
        return None, None, None

def execute_task(loginUid, loginSid, appUid, task_name, params):
    response = make_request(BASE_URL, params=params, headers=HEADERS if task_name == 'videoadver' else None)
    if response and response['data'].get('status', 1) == 1:
        logging.info(f"任务 {task_name} 完成，获得 {response['data'].get('obtain', '未知')} 金币")
    else:
        logging.info(f"任务 {task_name}: {response['data'].get('description', '未知错误')}")


def sign(loginUid, loginSid, appUid,devId):
    params = {
  "loginUid": loginUid,"loginSid": loginSid,"devId": devId,"appUid": appUid,"apiVer": "3","source": "kwplayer_ar_11.1.4.1_40.apk",
  "function": "1","terminal": "1","version": "11.1.4.1","scoreInfo": "","apiv": "5","t": "0.5542786369581496"
}
    response = make_request(SIGN_URL, params=params, headers=HEADERS)
    # print(response['data'])
    if response and response['code'] == 200:
        if response['data']['obtain'] == '0':
            logging.info(f'本次签到获得 {response["data"]["obtain"]}')
        else:
            logging.info(f'今天已经签到了~')
    else:
        logging.info(f'签到：{response["msg"]}')


    execute_task(loginUid, loginSid, appUid, '签到广告', {
        'loginUid': loginUid, 'loginSid': loginSid, 'appUid': appUid, 'terminal': 'ar', 'from': 'sign',
        'adverId': '20130802-13059416115', 'extraGoldNum': 88, 'clickExtraGoldNum': 0
    })

def videoadver(loginUid, loginSid, appUid):
    execute_task(loginUid, loginSid, appUid, '看视频', {
        'loginUid': loginUid, 'loginSid': loginSid, 'appUid': appUid, 'terminal': 'ar', 'from': 'videoadver',
        'goldNum': 58, 'clickExtraGoldNum': 0
    })

        
def listen(loginUid, loginSid, appUid):
    i = 0
    for key, value in {5:36, 1:43, 5:56, 10:68, 20:75, 30:88, 60:99, 120:108, 180:188}.items():
        
        if(i == 0):
            unit = 's'
        else:
            unit = 'm'
        # print(f"听歌时长：{key} {unit}")
        execute_task(loginUid, loginSid, appUid, '听歌时长', {
            "apiversion": 38,"adverSpace": "","verifyStr": "","loginUid": loginUid,"loginSid": loginSid,
            "appUid": appUid,"terminal": "ar","from": "listen","goldNum": value,"baseTaskGold": 0,"adverId": "",
            "token": "","clickExtraGoldNum": 0,"secondRewardFlag": 0,"yyzdSecondRewardFlag": 0,"surpriseType": "",
            "verificationId": "BgbvAwMh38pto%2BlDq%2FTmFis%2Fe4%2BzVel6eKQUv%2FX%2Bl6fhpEm8ZBc2yl5%2BDoiT8F3nyFp2VjaODf05FVW71kiKupA%3D%3D",
            "mobile": "FStUZR+DwXjZXQH5pNPuUw==","listenTime": key,"apiv": 5,"unit": unit
        })
        i+= 1        

def lucky(loginUid, loginSid, appUid):
    params = {'loginUid': loginUid, 'loginSid': loginSid, 'appUid': appUid, 'source': 'kwplayer_ar_10.7.6.2_18.apk'}
    response = make_request(LUCKY_URL, params={**params, 'type': 'free'}, headers=HEADERS)
    if response and response['code'] == 200:
        logging.info(f'本次抽奖获得 {response["data"]["loterryname"]}')
    elif response and response["msg"] == "免费次数用完了":
        response = make_request(LUCKY_URL, params={**params, 'type': 'video'}, headers=HEADERS)
        logging.info(f"本次抽奖获得 {response['data']['loterryname']}" if response and response['code'] == 200 else "所有抽奖次数都用完啦！")
    else:
        logging.info(f'抽奖：{response["msg"]}')

def box(loginUid, loginSid, appUid, timee):
    response = make_request(BOX_URL, params={
        'loginUid': loginUid, 'loginSid': loginSid, 'appUid': appUid, 'devId': '', 'source': 'kwplayer_ar_10.7.6.2_18.apk',
        'version': 'kwplayer_ar_10.7.6.2', 'action': 'new', 'time': timee, 'goldNum': 30, 'extraGoldnum': 38, 'clickExtraGoldNum': 600
    },headers=HEADERS)
    if response and response['data']['status'] == 1:
        logging.info(f"当前时段：{timee}，本次开宝箱获得 {response['data']['obtain']} 金币")
    else:
        logging.info(f"当前时段：{timee}，开宝箱：{response['data']['description']}")

def red(loginUid, loginSid, appUid, devId):
    response = make_request(BASE_URL, params={
        "loginUid": loginUid,"loginSid": loginSid,"devId": devId,"appUid": appUid,
        "apiVer": "3","source": "kwplayer_ar_11.1.4.1_40.apk","function": "1","terminal": "1","version": "11.1.4.1",
        "scoreInfo": "","apiv": "5","t": "0.8027042348801166"
    },headers=HEADERS)
    if response and response['code'] == 200:
        print(response)
        # logging.info(f"拆红包获得 {response['data']['obtain']} 金币")
    else:
        logging.info(f"拆红包：{response['data']['description']}")

def get_time_period():
    t = datetime.datetime.now().hour
    return next((period for start, end, period in TIME_PERIODS if start <= t < end), "20-24")

def main():
    kwyy = os.getenv('kwyy')
    if not kwyy:
        logging.error("环境变量 'kwyy' 未设置")
        return
        
    if '&' not in kwyy:
        try:
            appUid, devId, q, phone, 备注 = kwyy.split('#')
            username, loginSid, loginUid = login(q)
            if not all([username, loginSid, loginUid]):
                logging.error("登录失败")
                return
                
            logging.info(f'账号：{loginUid},任务开始'.center(30, '_'))
            tasks = [
                (sign, (loginUid, loginSid, appUid, devId)),
                (videoadver, (loginUid, loginSid, appUid)),
                (box, (loginUid, loginSid, appUid, get_time_period())),
                (lucky, (loginUid, loginSid, appUid)),
                (listen, (loginUid, loginSid, appUid)),
                # (red, (loginUid, loginSid, appUid, devId)),
                (lambda *args: execute_task(*args, '听歌', {'loginUid': loginUid, 'loginSid': loginSid, 'appUid': appUid, 'terminal': 'ar', 'from': 'mobile', 'goldNum': 18, 'clickExtraGoldNum': 0}), (loginUid, loginSid, appUid)),
                (lambda *args: execute_task(*args, '听故事', {'loginUid': loginUid, 'loginSid': loginSid, 'appUid': appUid, 'terminal': 'ar', 'from': 'novel', 'goldNum': 18, 'clickExtraGoldNum': 0}), (loginUid, loginSid, appUid)),
                (lambda *args: execute_task(*args, '收藏', {'loginUid': loginUid, 'loginSid': loginSid, 'appUid': appUid, 'terminal': 'ar', 'from': 'collect', 'goldNum': 18, 'clickExtraGoldNum': 0}), (loginUid, loginSid, appUid))
            ]
            
            for task in tasks:
                func, args = task
                func(*args)
                time.sleep(3)
            logging.info(f"账号：{loginUid},本次任务完成！".center(30, "_"))
            
        except Exception as e:
            logging.error(f"执行失败: {e}")
    else:
        for i, account in enumerate(kwyy.split('&')):
            logging.info(f'=====第{i+1}个账号=====')
            try:
                appUid, devId, q, phone, 备注 = account.split('#')
                username, loginSid, loginUid = login(q)
                if not all([username, loginSid, loginUid]):
                    continue
                    
                logging.info(f'账号：{loginUid},任务开始'.center(30, '_'))
                tasks = [
                    (sign, (loginUid, loginSid, appUid,devId)),
                    (videoadver, (loginUid, loginSid, appUid)),
                    # (box, (loginUid, loginSid, appUid, get_time_period())),
                    (lucky, (loginUid, loginSid, appUid)),
                    (listen, (loginUid, loginSid, appUid)),
                    (lambda *args: execute_task(*args, '听歌', {'loginUid': loginUid, 'loginSid': loginSid, 'appUid': appUid, 'terminal': 'ar', 'from': 'mobile', 'goldNum': 18, 'clickExtraGoldNum': 0}), (loginUid, loginSid, appUid)),
                    (lambda *args: execute_task(*args, '听故事', {'loginUid': loginUid, 'loginSid': loginSid, 'appUid': appUid, 'terminal': 'ar', 'from': 'novel', 'goldNum': 18, 'clickExtraGoldNum': 0}), (loginUid, loginSid, appUid)),
                    (lambda *args: execute_task(*args, '收藏', {'loginUid': loginUid, 'loginSid': loginSid, 'appUid': appUid, 'terminal': 'ar', 'from': 'collect', 'goldNum': 18, 'clickExtraGoldNum': 0}), (loginUid, loginSid, appUid))
                ]
                
                for task in tasks:
                    func, args = task
                    func(*args)
                    time.sleep(3)
                logging.info(f"账号：{loginUid},本次任务完成！".center(30, "_"))
                
                
            except Exception as e:
                logging.error(f"账号{i+1}执行失败: {e}")
                continue

if __name__ == '__main__':
    main()
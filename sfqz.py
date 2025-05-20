import datetime
import random
import requests
import threading
import time
from concurrent.futures import ThreadPoolExecutor

target_time = datetime.datetime(2025, 5, 15, 9, 59, 58, 599700)  # 修改为将来的日期和时间

cishu = 5  #次数
jiange = 100   #间隔毫秒
id = 'SFPD1920034832629592064'
#顺丰粽子礼盒（粽力前行）SFPD1920034832629592064
#顺丰粽子礼盒（乐在途粽）SFPD1920035035663241216
url = "https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberGoods~pointMallService~createOrder"

#抓sessionId
CSESSIONS = [
    'sessionId=A0FD1787F03D8A489B1FCACF20B1E400',
    'sessionId=A0FD1787F04D8A489B1FCACF20B1E403',
    'sessionId=A0FD1787F05D8A489B1FCACF20B1E402',
]

def make_request(CSESSION, index, count):
    headers = {
    "Content-Type": "application/json;charset=UTF-8",
    "syscode": "MCS-MIMP-CORE",
    "accept": "application/json, text/plain, */*",
    "cookie": CSESSION,
}
    payload = {
    "from": "Point_Mall",
    "orderSource": "POINT_MALL_EXCHANGE",
    "goodsNo": id,
    "quantity": 1,
    "province": "广东省",         #省
    "city": "广州市",             #市
    "distinct": "荔湾区",          #区镇
    "receiveContact": "吕布",      #收货名字
    "receiveAddress": "东漖街芳和花园18栋503",   #详细地址
    "receivePhone": "13544438454",         #收货手机号
    "fullReceiveAddress": "广东省广州市荔湾区东漖街芳和花园18栋503",#完整收货地址
}
    try:
        response = requests.post(url, headers=headers, json=payload)
        response_data = response.json()
        cur_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        print(f'账号 {index + 1}，第 {count + 1} 次请求，时间：{cur_time}，结果：{response_data}')
    except Exception as e:
        print(f'账号 {index + 1}，第 {count + 1} 次请求，时间：{datetime.datetime.now()}，发生异常：{e}')

def make_threaded_requests(CSESSIONS, jiange, cishu):
    with ThreadPoolExecutor(max_workers=len(CSESSIONS)) as executor:
        futures = []
        for count in range(cishu):
            for index, qm_user_token in enumerate(CSESSIONS):
                futures.append(executor.submit(make_request, qm_user_token, index, count))
                time.sleep(jiange / 1000)

while True:
    now = datetime.datetime.now()
    if now >= target_time:
        make_threaded_requests(CSESSIONS, jiange, cishu)
        break
    time.sleep(0.5)  # 每秒钟检查一次是否到达目标时间

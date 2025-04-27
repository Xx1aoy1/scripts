"""
cron: 0 59 9,13 * * *
new Env('电信金豆兑换话费');
"""
import subprocess
import sys
import asyncio
import aiohttp
import os
import execjs
import requests
import re
import time as time_module  # 重命名导入以避免冲突
import json
import random
import datetime
import base64
import ssl
import traceback
from bs4 import BeautifulSoup
from loguru import logger
from lxml import etree
import gjc
import urllib3
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from Crypto.Cipher import DES3
from Crypto.Util.Padding import pad, unpad
from Crypto.Util.strxor import strxor
from Crypto.Cipher import AES
from http import cookiejar  # Python 2: import cookielib as cookiejar
from requests.adapters import HTTPAdapter
from urllib3.util.ssl_ import create_urllib3_context


def get_network_time():
    """从淘宝接口获取网络时间"""
    url = "https://acs.m.taobao.com/gw/mtop.common.getTimestamp/"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if "data" in data and "t" in data["data"]:
                timestamp = int(data["data"]["t"])  # 获取时间戳
                return datetime.datetime.fromtimestamp(timestamp / 1000)  # 转换为 datetime 对象
            else:
                raise ValueError("接口返回数据格式错误")
        else:
            raise Exception(f"获取网络时间失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"⏰{str(get_network_time())[11:22]} 获取网络时间失败: {e}")
        return datetime.datetime.now()  # 如果失败，使用本地时间作为备选


# 获取本地时间和网络时间
local_time = datetime.datetime.now()
network_time = get_network_time()

# 计算时间差
time_diff = network_time - local_time

# 输出时间差，精确到微秒
print(f"本地时间: {local_time.strftime('%Y-%m-%d %H:%M:%S.%f')}")
print(f"网络时间: {network_time.strftime('%Y-%m-%d %H:%M:%S.%f')}")
print(f"时间差: {time_diff.total_seconds():.6f} 秒")

# 默认兑换策略
MEXZ = os.getenv("MEXZ")

# 定义时间段
morning_start = datetime.time(9, 30, 3)
morning_end = datetime.time(10, 0, 30)
afternoon_start = datetime.time(13, 30, 3)
afternoon_end = datetime.time(14, 0, 30)

# 获取当前时间
now = get_network_time().time()

# 判断当前时间是否在指定的时间段内
if (morning_start <= now <= morning_end) or (afternoon_start <= now <= afternoon_end):
    # 在指定时间段内，使用环境变量中的 MEXZ 配置
    if not MEXZ:
        MEXZ = "0.5,5,6;1,10,3"
else:
    # 不在指定时间段内，使用默认策略
    MEXZ = "0.5,5,6;1,10,3"

# 解析 MEXZ 配置
morning_exchanges, afternoon_exchanges = MEXZ.split(';')
morning_exchanges = [f"{x}元话费" for x in morning_exchanges.split(',')]
afternoon_exchanges = [f"{x}元话费" for x in afternoon_exchanges.split(',')]


# 从环境变量中获取代理池地址
DY_PROXY = os.getenv("DY_PROXY123")


async def get_proxy_from_pool():
    """从代理池获取代理IP"""
    if not DY_PROXY:
        raise ValueError("DY_PROXY 环境变量未设置")

    async with aiohttp.ClientSession() as session:
        async with session.get(DY_PROXY) as response:
            if response.status != 200:
                raise Exception(f"从代理池获取代理IP失败，状态码: {response.status}")
            proxy_ip = await response.text()
            return proxy_ip.strip()  # 去除可能的空白字符


class BlockAll(cookiejar.CookiePolicy):
    return_ok = set_ok = domain_return_ok = path_return_ok = lambda self, *args, **kwargs: False
    netscape = True
    rfc2965 = hide_cookie2 = False


def printn(m):
    print(f'\n{m}')

def print_time_log(m):
    print(f'⏰{str(get_network_time())[11:22]} {m}')


ORIGIN_CIPHERS = ('DEFAULT@SECLEVEL=1')


class DESAdapter(HTTPAdapter):
    def __init__(self, *args, **kwargs):
        CIPHERS = ORIGIN_CIPHERS.split(':')
        random.shuffle(CIPHERS)
        CIPHERS = ':'.join(CIPHERS)
        self.CIPHERS = CIPHERS + ':!aNULL:!eNULL:!MD5'
        super().__init__(*args, **kwargs)

    def init_poolmanager(self, *args, **kwargs):
        context = create_urllib3_context(ciphers=self.CIPHERS)
        context.check_hostname = False
        kwargs['ssl_context'] = context

        return super(DESAdapter, self).init_poolmanager(*args, **kwargs)

    def proxy_manager_for(self, *args, **kwargs):
        context = create_urllib3_context(ciphers=self.CIPHERS)
        context.check_hostname = False
        kwargs['ssl_context'] = context
        return super(DESAdapter, self).proxy_manager_for(*args, **kwargs)


urllib3.disable_warnings()
ssl_context = ssl.create_default_context()
ssl_context.set_ciphers("DEFAULT@SECLEVEL=1")  # Set security level to allow smaller DH keys
ss = requests.session()
ss.verify = False
ss.headers = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 13; 22081212C Build/TKQ1.220829.002) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.97 Mobile Safari/537.36",
    "Referer": "https://wapact.189.cn:9001/JinDouMall/JinDouMall_independentDetails.html"
}
ss.mount('https://', DESAdapter())
ss.cookies.set_policy(BlockAll())
yc = 1
wt = 0
kswt = 0.1
yf = get_network_time().strftime("%Y%m")
ip_list = []
jp = {"9": {}, "13": {}}
try:
    with open('电信金豆换话费.log') as fr:
        dhjl = json.load(fr)
except:
    dhjl = {}
if yf not in dhjl:
    dhjl[yf] = {}
load_token_file = 'chinaTelecom_cache.json'
try:
    with open(load_token_file, 'r') as f:
        load_token = json.load(f)
except:
    load_token = {}

errcode = {
    "0": "兑换成功",
    "412": "兑换次数已达上限",
    "413": "商品已兑完",
    "420": "未知错误",
    "410": "该活动未开始",
    "501": "服务器处理错误",
    "Y0001": "当前等级不足，去升级兑当前话费",
    "Y0002": "使用翼相连网络600分钟或连接并拓展网络500分钟可兑换此奖品",
    "Y0003": "使用翼相连共享流量400M或共享WIFI：2GB可兑换此奖品",
    "Y0004": "使用翼相连共享流量2GB可兑换此奖品",
    "Y0005": "当前等级不足，去升级兑当前话费",
    "E0001": "您的网龄不足10年，暂不能兑换"
}

key = b'1234567`90koiuyhgtfrdews'
iv = 8 * b'\0'

public_key_b64 = '''-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDBkLT15ThVgz6/NOl6s8GNPofdWzWbCkWnkaAm7O2LjkM1H7dMvzkiqdxU02jamGRHLX/ZNMCXHnPcW/sDhiFCBN18qFvy8g6VYb9QtroI09e176s+ZCtiv7hbin2cCTj99iUpnEloZm19lwHyo69u5UMiPMpq0/XKBO8lYhN/gwIDAQAB
-----END PUBLIC KEY-----'''

public_key_data = '''-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC+ugG5A8cZ3FqUKDwM57GM4io6JGcStivT8UdGt67PEOihLZTw3P7371+N47PrmsCpnTRzbTgcupKtUv8ImZalYk65dU8rjC/ridwhw9ffW2LBwvkEnDkkKKRi2liWIItDftJVBiWOh17o6gfbPoNrWORcAdcbpk2L+udld5kZNwIDAQAB
-----END PUBLIC KEY-----'''


def t(h):
    date = get_network_time()
    date_zero = date.replace(hour=h, minute=59, second=20)
    date_zero_time = time_module.mktime(date_zero.timetuple())  # 使用 timetuple() 转换为 struct_time
    return date_zero_time


def encrypt(text):
    cipher = DES3.new(key, DES3.MODE_CBC, iv)
    ciphertext = cipher.encrypt(pad(text.encode(), DES3.block_size))
    return ciphertext.hex()


def decrypt(text):
    ciphertext = bytes.fromhex(text)
    cipher = DES3.new(key, DES3.MODE_CBC, iv)
    plaintext = unpad(cipher.decrypt(ciphertext), DES3.block_size)
    return plaintext.decode()


def b64(plaintext):
    public_key = RSA.import_key(public_key_b64)
    cipher = PKCS1_v1_5.new(public_key)
    ciphertext = cipher.encrypt(plaintext.encode())
    return base64.b64encode(ciphertext).decode()


def encrypt_para(plaintext):
    public_key = RSA.import_key(public_key_data)
    cipher = PKCS1_v1_5.new(public_key)
    ciphertext = cipher.encrypt(plaintext.encode())
    return ciphertext.hex()


def encode_phone(text):
    encoded_chars = []
    for char in text:
        encoded_chars.append(chr(ord(char) + 2))
    return ''.join(encoded_chars)


def ophone(t):
    key = b'34d7cb0bcdf07523'
    utf8_key = key.decode('utf-8')
    utf8_t = t.encode('utf-8')
    cipher = AES.new(key, AES.MODE_ECB)
    ciphertext = cipher.encrypt(pad(utf8_t, AES.block_size))
    return ciphertext.hex()


def send(uid, content):
    appToken = os.getenv("WXPUSHER_APP_TOKEN")  # 从环境变量中获取 appToken
    uid = os.getenv("WXPUSHER_UID")  # 从环境变量中获取 uid

    if not appToken or not uid:
        raise ValueError("WXPUSHER_APP_TOKEN 或 WXPUSHER_UID 未设置")

    r = requests.post('https://wxpusher.zjiecode.com/api/send/message', json={"appToken": appToken, "content": content, "contentType": 1, "uids": [uid]}).json()
    return r


def userLoginNormal(phone, password):
    alphabet = 'abcdef0123456789'
    uuid = [''.join(random.sample(alphabet, 8)), ''.join(random.sample(alphabet, 4)), '4' + ''.join(random.sample(alphabet, 3)), ''.join(random.sample(alphabet, 4)), ''.join(random.sample(alphabet, 12))]
    timestamp = get_network_time().strftime("%Y%m%d%H%M%S")
    loginAuthCipherAsymmertric = 'iPhone 14 15.4.' + uuid[0] + uuid[1] + phone + timestamp + password[:6] + '0$$$0.'

    try:
        r = ss.post('https://appgologin.189.cn:9031/login/client/userLoginNormal', json={"headerInfos": {"code": "userLoginNormal", "timestamp": timestamp, "broadAccount": "", "broadToken": "", "clientType": "#9.6.1#channel50#iPhone 14 Pro Max#", "shopId": "20002", "source": "110003", "sourcePassword": "Sid98s", "token": "", "userLoginName": phone}, "content": {"attach": "test", "fieldData": {"loginType": "4", "accountType": "", "loginAuthCipherAsymmertric": b64(loginAuthCipherAsymmertric), "deviceUid": uuid[0] + uuid[1] + uuid[2], "phoneNum": encode_phone(phone), "isChinatelecom": "0", "systemVersion": "15.4.0", "authentication": password}}}).json()
    except Exception as e:
        print(f"登录请求失败，错误信息: {e}")
        return False

    # 添加错误处理逻辑
    if r is None:
        print(f"登录请求失败，返回值为 None")
        return False

    if 'responseData' not in r or r['responseData'] is None:
        print(f"登录请求失败，responseData 不存在或为 None: {r}")
        return False

    if 'data' not in r['responseData'] or r['responseData']['data'] is None:
        print(f"登录请求失败，data 不存在或为 None: {r}")
        return False

    if 'loginSuccessResult' not in r['responseData']['data']:
        print(f"登录请求失败，loginSuccessResult 不存在: {r}")
        return False

    l = r['responseData']['data']['loginSuccessResult']

    if l:
        load_token[phone] = l
        with open(load_token_file, 'w') as f:
            json.dump(load_token, f)
        ticket = get_ticket(phone, l['userId'], l['token'])
        return ticket

    return False


def get_ticket(phone, userId, token):
    r = ss.post('https://appgologin.189.cn:9031/map/clientXML', data='<Request><HeaderInfos><Code>getSingle</Code><Timestamp>' + get_network_time().strftime("%Y%m%d%H%M%S") + '</Timestamp><BroadAccount></BroadAccount><BroadToken></BroadToken><ClientType>#9.6.1#channel50#iPhone 14 Pro Max#</ClientType><ShopId>20002</ShopId><Source>110003</Source><SourcePassword>Sid98s</SourcePassword><Token>' + token + '</Token><UserLoginName>' + phone + '</UserLoginName></HeaderInfos><Content><Attach>test</Attach><FieldData><TargetId>' + encrypt(userId) + '</TargetId><Url>4a6862274835b451</Url></FieldData></Content></Request>', headers={'user-agent': 'CtClient;10.4.1;Android;13;22081212C;NTQzNzgx!#!MTgwNTg1'})

    tk = re.findall('<Ticket>(.*?)</Ticket>', r.text)
    if len(tk) == 0:
        return False
    # print(tk)
    return decrypt(tk[0])


async def exchange(phone, s, title, aid, uid, amount):
    global h  # 使用全局变量 h
    masked_phone = phone[:3] + '****' + phone[-4:]
    try:
        # 第一次请求：获取 cookie
        tt = time_module.time()
        start_time = time_module.time()  # 记录开始时间
        cookies = await gjc.get_rs('https://wapact.189.cn:9001/gateway/standExchange/detailNew/exchange', s, md='post')
        end_time = time_module.time()  # 记录结束时间
        print_time_log(f"📱{masked_phone} 获取到 {title} 的cookies ⏳用时: {end_time - start_time:.3f} 秒")

        # 获取当前时间
        now = get_network_time()

        # 如果 h 没有赋值，则使用当前时间的小时数
        if h is None:
            h = now.hour

        # 设置第一次等待的目标时间（9:59:50 或 13:59:50）
        if h == 9:
            first_target_time = now.replace(hour=h, minute=59, second=50, microsecond=0)
        elif h == 13:
            first_target_time = now.replace(hour=h, minute=59, second=50, microsecond=0)

        # 计算第一次等待的时间差
        first_time_diff = (first_target_time - now).total_seconds()

        # 如果第一次等待的时间差在 0 到 300 秒之间，则等待到第一次目标时间
        if 0 <= first_time_diff <= 300:
            print_time_log(f"📱{masked_phone} ⏱️等待 {first_time_diff:.2f} 秒...")
            await asyncio.sleep(first_time_diff)

        # 判断当前时间是否在指定的时间段内
        morning_start = datetime.time(9, 30, 50)
        morning_end = datetime.time(10, 0, 5)
        afternoon_start = datetime.time(13, 30, 40)
        afternoon_end = datetime.time(14, 0, 5)
        current_time = now.time()

        if (morning_start <= current_time <= morning_end) or (afternoon_start <= current_time <= afternoon_end):
            # 在指定时间段内，根据 DY_PROXY 是否设置来决定使用代理或本地 IP
            if DY_PROXY:
                try:
                    proxy_ip = await get_proxy_from_pool()
                    proxy = f"http://{proxy_ip}"  # 根据代理池返回的格式调整
                    print_time_log(f"📱{masked_phone} 🌐从代理池获取到代理IP: {proxy_ip}")
                except ValueError as e:
                    print_time_log(f"📱{masked_phone} {e} 📶使用本地 IP ")
                    proxy = None  # 设置为 None，表示使用本地 IP
            else:
                print_time_log(f"📱{masked_phone} 📶DY_PROXY 未设置，使用本地 IP")
                proxy = None  # 设置为 None，表示使用本地 IP
        else:
            # 不在指定时间段内，直接使用本地 IP
            print_time_log(f"📱{masked_phone} 📶不在指定时间段内，使用本地 IP")
            proxy = None  # 设置为 None，表示使用本地 IP

        # 设置第二次等待的目标时间（9:59:59 或 13:59:59）
        if h == 9:
            second_target_time = now.replace(hour=h, minute=59, second=59, microsecond=803600)
        elif h == 13:
            second_target_time = now.replace(hour=h, minute=59, second=59, microsecond=793600)

        # 计算第二次等待的时间差
        second_time_diff = (second_target_time - get_network_time()).total_seconds()

        # 如果第二次等待的时间差在 0 到 300 秒之间，则等待到第二次目标时间
        if 0 <= second_time_diff <= 300:
            print_time_log(f"📱{masked_phone} ⏱️等待 {second_time_diff:.2f} 秒...")
            await asyncio.sleep(second_time_diff)

        # 打印是否使用了代理
        if proxy:
            print_time_log(f"📱{masked_phone} 🌐正在使用代理IP: {proxy}")
        else:
            print_time_log(f"📱{masked_phone} 📶正在使用本地 IP")

        # 第二次请求：发送兑换请求，使用代理 IP 或本地 IP
        url = "https://wapact.189.cn:9001/gateway/standExchange/detailNew/exchange"

        # 记录请求开始时间
        request_start_time = datetime.datetime.now()  # 获取当前时间，精确到微秒

        # 发送请求
        async with s.post(url, json={"activityId": aid}, cookies=cookies, proxy=proxy) as r:
            # 记录请求结束时间
            request_end_time = datetime.datetime.now()  # 获取当前时间，精确到微秒

            print(f'\n⏰{str(get_network_time())[11:22]}')
            print(f"📱{masked_phone} 发送兑换请求的时间: {request_start_time.strftime('%Y-%m-%d %H:%M:%S.%f')}")

            # 打印请求耗时，精确到微秒
            print(f"📱{masked_phone} ⌛请求耗时: {(request_end_time - request_start_time).total_seconds():.6f} 秒")

            # 处理响应
            if r.status == 412:
                print(f"📱{masked_phone} 😿 遇到连续 412 错误，已终止本次兑换！")
                return
            print(f"📱{masked_phone} 响应码: {r.status} {await r.text()}")
            if r.status == 200:
                r_json = await r.json()
                if r_json["code"] == 0:
                    if r_json["biz"] != {} and r_json["biz"]["resultCode"] in errcode:
                        print(f'📱{masked_phone}  ------ {str(get_network_time())[11:22]} ------ {title} {errcode[r_json["biz"]["resultCode"]]}')

                        if r_json["biz"]["resultCode"] in ["0", "412"]:
                            if r_json["biz"]["resultCode"] == "0":
                                msg = phone + ":" + title + "兑换成功"
                                send(uid, msg)  # 发送推送通知
                            if phone not in dhjl[yf][title]:
                                dhjl[yf][title] += "#" + phone
                                with open('电信金豆换话费.log', 'w') as f:
                                    json.dump(dhjl, f, ensure_ascii=False)
                else:
                    print_time_log(f'📱{masked_phone} {r_json}')
            else:
                print_time_log(f"📱{masked_phone} 兑换请求失败: {await r.text()}")

    except Exception as e:
        print_time_log(f"📱{masked_phone}  发生错误: {e}")
        # print(f"详细错误信息: {traceback.format_exc()}")  # 打印详细的错误堆栈


async def dh(phone, s, title, aid, wt, uid):
    global h  # 使用全局变量 h
    masked_phone = phone[:3] + '****' + phone[-4:]
    print_time_log(f"📱{masked_phone} 🎁{title} 🔁【开始兑换】")
    cs = 0
    tasks = []
    creat_start_time = datetime.datetime.now()  # 获取当前时间，精确到微秒
    while cs < 1:
        # 提取金额
        amount = title.split('元')[0]
        if (h == 9 and title in morning_exchanges) or (h == 13 and title in afternoon_exchanges):
            tasks.append(exchange(phone, s, title, aid, uid, amount))
        else:
            print_time_log(f"📱{masked_phone} 商品：🎁{title} 不在兑换时间范围内，跳过兑换")
        cs += 1
        await asyncio.sleep(0.1)
    creat_end_time = datetime.datetime.now()  # 获取当前时间，精确到微秒
    print_time_log(f"📱{masked_phone} 🍀创建了【{cs}】并发任务 ⌛耗时：{(creat_end_time - creat_start_time).total_seconds():.6f}秒")
    while wt > get_network_time().timestamp():
        await asyncio.sleep(1)
    await asyncio.gather(*tasks)

def aes_ecb_encrypt(plaintext, key):
    key = key.encode('utf-8')
    if len(key) not in [16, 24, 32]:
        raise ValueError("密钥长度必须为16/24/32字节")

    # 对明文进行PKCS7填充
    padded_data = pad(plaintext.encode('utf-8'), AES.block_size)
    #padded_data = plaintext.encode('utf-8')
    # 创建AES ECB加密器
    cipher = AES.new(key, AES.MODE_ECB)

    # 加密并返回Base64编码结果
    ciphertext = cipher.encrypt(padded_data)
    return base64.b64encode(ciphertext).decode('utf-8')

async def ks(phone, ticket, uid):
    global h, wt  # 使用全局变量 h 和 wt
    masked_phone = phone[:3] + '****' + phone[-4:]
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 13; 22081212C Build/TKQ1.220829.002) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.97 Mobile Safari/537.36",
        "Referer": "https://wapact.189.cn:9001/JinDouMall/JinDouMall_independentDetails.html"
    }

    timeout = aiohttp.ClientTimeout(total=20)  # 设置超时时间
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context), headers=headers, timeout=timeout) as s:
        try:
            cookies = await gjc.get_rs('https://wapact.189.cn:9001/gateway/standExchange/detailNew/exchange', session=s)

            s.cookie_jar.update_cookies(cookies)
            login_data = {
                "ticket": ticket,
                "backUrl": "https%3A%2F%2Fwapact.189.cn%3A9001",
                "platformCode": "P201010301",
                "loginType": 2
            }
            encrypted_data = aes_ecb_encrypt(json.dumps(login_data), 'telecom_wap_2018')
            # 登录请求
            max_retries = 3  # 最大重试次数
            retries = 0
            while retries < max_retries:
                try:
                    login_response = await s.post(
                        'https://wapact.189.cn:9001/unified/user/login',
                        data=encrypted_data,
                        headers={
                            "Content-Type": "application/json;charset=UTF-8",
                            "Accept": "application/json, text/javascript, */*; q=0.01"
                        }
                    )

                    # 处理登录响应
                    if login_response.status == 200:
                        login = await login_response.json()
                        break  # 如果成功，跳出循环
                    elif login_response.status == 412:
                        print_time_log(f"📱{masked_phone} 登录请求失败，HTTP状态码: {login_response.status}, 直接重新调用 ks 函数...")
                        return await ks(phone, ticket, uid)  # 直接从头开始调用 ks 函数
                    else:
                        print_time_log(f"📱{masked_phone}  登录请求失败，HTTP状态码: {login_response.status}")
                        print_time_log(f"响应内容: {await login_response.text()}")

                except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                    retries += 1
                    print_time_log(f"📱{masked_phone}  登录请求失败，重试 {retries}/{max_retries}... 错误信息: {e}")
                    await asyncio.sleep(2 ** retries)  # 指数退避算法等待时间

                    if retries == max_retries:
                        print_time_log(f"📱{masked_phone}  登录失败，达到最大重试次数. 尝试重新调用 ks 函数...")
                        return await ks(phone, ticket, uid)  # 递归调用 ks 函数

            if 'login' in locals() and login['code'] == 0:
                s.headers["Authorization"] = "Bearer " + login["biz"]["token"]

                r = await s.get('https://wapact.189.cn:9001/gateway/golden/api/queryInfo')
                r_json = await r.json()
                amountTotal = r_json["biz"]["amountTotal"]
                print_time_log(f'📱{masked_phone} 🥔金豆余额：{amountTotal}')

                queryBigDataAppGetOrInfo = await s.get('https://wapact.189.cn:9001/gateway/golden/goldGoods/getGoodsList?floorType=0&userType=1&page=1&order=3&tabOrder=')
                queryBigDataAppGetOrInfo_json = await queryBigDataAppGetOrInfo.json()

                # 检查列表是否为空
                if "biz" in queryBigDataAppGetOrInfo_json and "ExchangeGoodslist" in queryBigDataAppGetOrInfo_json["biz"]:
                    for i in queryBigDataAppGetOrInfo_json["biz"]["ExchangeGoodslist"]:
                        if '话费' not in i["title"]:
                            continue

                        if i["title"] in morning_exchanges:
                            jp["9"][i["title"]] = i["id"]
                        elif i["title"] in afternoon_exchanges:
                            jp["13"][i["title"]] = i["id"]
                else:
                    print_time_log(f"📱{masked_phone} 获取兑换商品列表失败")

                h = get_network_time().hour
                if 11 > h:
                    h = 9
                else:
                    h = 13

                if len(sys.argv) == 2:
                    h = int(sys.argv[1])

                d = jp[str(h)]

                wt = t(h) + kswt

                tasks = []
                for di in d:
                    if di not in dhjl[yf]:
                        dhjl[yf][di] = ""
                    if phone in dhjl[yf][di]:
                        print_time_log(f"📱{masked_phone} 🎁{di} ✅【已兑换】")
                        print_time_log(f"📱{masked_phone} 🎁{di} ⏩【跳过兑换】")
                    else:
                        print_time_log(f"📱{masked_phone} 🎁{di} ❌【未兑换】")
                        if wt - time_module.time() > 30 * 60:
                            print_time_log(f"⏱️等待时间超过30分钟，退出运行")
                            return

                        tasks.append(dh(phone, s, di, d[di], wt, uid))
                print_time_log(f"📱{masked_phone} 🧾共计【{len(tasks)}】个兑换任务 📦 正在进行中~")
                await asyncio.gather(*tasks)
            else:
                print_time_log(f"📱{masked_phone} ❌获取token失败, 错误信息: {login['message']}")
        except Exception as e:
            print_time_log(f"📱{masked_phone} 发生错误: {e}")
            return  # 跳过当前账户，继续处理其他账户


async def main():
    global wt, rs, h  # 使用全局变量 wt, rs, h
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 13; 22081212C Build/TKQ1.220829.002) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.97 Mobile Safari/537.36",
        "Referer": "https://wapact.189.cn:9001/JinDouMall/JinDouMall_independentDetails.html"
    }

    timeout = aiohttp.ClientTimeout(total=20)  # 设置超时时间

    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context), headers=headers, timeout=timeout) as ss:
        r = await ss.get('https://wapact.189.cn:9001/gateway/standExchange/detailNew/exchange')

        if '$_ts=window' in await r.text():
            rs = 1
            # first_request()
        else:
            rs = 0

        # 获取账号列表
        chinaTelecomAccount = os.environ.get('chinaTelecomAccount')
        if not chinaTelecomAccount:
            print("未检测到账号")
            return

        accounts = chinaTelecomAccount.split('@')
        account_count = len(accounts)
        print_time_log(f"🚀检测到 【{account_count}】 个账号")

        # 分批次处理账号，每批次20个账号
        batch_size = 20
        for i in range(0, account_count, batch_size):
            batch_accounts = accounts[i:i + batch_size]
            tasks = []
            for account in batch_accounts:
                account_info = account.split('#')
                phone = account_info[0]
                password = account_info[1]
                uid = account_info[-1]
                ticket = False
                masked_phone = phone[:3] + '****' + phone[-4:]
                if phone in load_token:
                    print_time_log(f'📱{masked_phone} ✅使用缓存登录')
                    ticket = get_ticket(phone, load_token[phone]['userId'], load_token[phone]['token'])

                if not ticket:
                    print_time_log(f'📱{masked_phone} 🔑使用密码登录')
                    ticket = userLoginNormal(phone, password)

                if ticket:
                    tasks.append(ks(phone, ticket, uid))
                else:
                    print_time_log(f'📱{masked_phone} ❌️登录失败')
                    continue  # 跳过登录失败的账号

            # 等待到设定时间
            while wt > datetime.datetime.now().timestamp():
                await asyncio.sleep(1)

            await asyncio.gather(*tasks)
            print_time_log(f"✅完成批次 {i // batch_size + 1} 的账号处理")

            # 等待一段时间再处理下一个批次
            await asyncio.sleep(2)  # 等待2秒


START_LOG = rf'''
+--------------------------------------------------------------------+
|  /\_/\                 金豆兑换话费V2.0                             |
| ( o.o )    上午兑换：{"、".join(morning_exchanges)}                     |
|  > ^ <     下午兑换：{"、".join(afternoon_exchanges)}                      |
+--------------------------------------------------------------------+'''

if __name__ == "__main__":
    print(START_LOG)
    print(f"🔔 提醒：程序将提前【{kswt} 秒】启动兑换流程")
    if len(sys.argv) > 1:
        h = int(sys.argv[1])
    else:
        h = None  # 默认值为 None
    asyncio.run(main())

# 获取当前月份
current_month = get_network_time().strftime("%Y%m")

# 读取原始日志文件
try:
    with open('电信金豆换话费.log', 'r') as fr:
        dhjl = json.load(fr)
except FileNotFoundError:
    dhjl = {}

# 初始化新的日志结构
dhjl2 = {}

# 只处理当前月份的数据
if current_month in dhjl:
    records = dhjl[current_month]
    for fee, phones in records.items():
        phone_list = phones.strip('#').split('#')
        for phone in phone_list:
            if phone not in dhjl2:
                dhjl2[phone] = {}
            if current_month not in dhjl2[phone]:
                dhjl2[phone][current_month] = []
            dhjl2[phone][current_month].append(fee)

# 写入新的日志文件
with open('电信金豆换话费2.log', 'w') as fw:
    json.dump(dhjl2, fw, ensure_ascii=False, indent=4)

# 检查当前时间是否在10:05:10到11:00:00或14:05:10到15:00:00之间
current_time = get_network_time()
start_time_1 = current_time.replace(hour=10, minute=0, second=30)
end_time_1 = current_time.replace(hour=10, minute=20, second=0)
start_time_2 = current_time.replace(hour=14, minute=0, second=30)
end_time_2 = current_time.replace(hour=14, minute=20, second=0)

if (start_time_1 <= current_time < end_time_1) or (start_time_2 <= current_time < end_time_2):
    # 运行汇总推送脚本
    subprocess.run(["python", "汇总推送.py"])
else:
    print("当前不在推送时间，不运行汇总推送脚本。")

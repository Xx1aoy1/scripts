"""
免责声明：
本脚本仅供学习交流使用，请勿用于商业用途或非法目的。
使用者应对自己的行为负责，脚本作者不承担任何法律责任。
使用前请确保遵守中国电信相关服务条款，合理使用脚本功能。

使用说明：
1. 环境变量配置：
   - chinaTelecomAccount: 手机号#密码#WxPusher的UID (多个账号用@或&分隔)
   - MEXZ: 兑换策略配置，格式："0.5,5;1,10" (上午;下午)
   - WXPUSHER_APP_TOKEN: 微信推送token
   - WXPUSHER_UID: 微信推送UID
   - OUTER_LOOP_COUNT: 外层循环次数，默认20
   - INNER_LOOP_COUNT: 内层循环次数，默认10

2. 运行时间：
   - 上午场: 10:00:00
   - 下午场: 14:00:00

3. 功能特点：
   - 多账号支持
   - 自动登录验证
   - 智能时间同步
   - 微信消息推送
   - 失败重试机制
   - 详细的日志输出

脚本内容：
本脚本通过模拟中国电信APP的登录和兑换流程，实现金豆自动兑换话费功能。
主要包含以下模块：
- 时间同步：获取网络时间确保准确性
- 登录认证：处理用户登录和token获取
- 兑换逻辑：多线程并发兑换请求
- 消息推送：通过微信推送兑换结果
- 日志记录：详细记录操作过程和结果

使用方法：
1. 配置所需的环境变量
2. 安装依赖：pip install requests aiohttp pycryptodome
3. 设置定时任务或手动运行
"""

"""
cron: 0 59 9,13 * * *
new Env('电信金豆兑换话费');
"""
import subprocess
import sys
import asyncio
import aiohttp
import os
import requests
import re
import time as time_module  # 重命名导入以避免冲突
import json
import random
import datetime
import base64
import ssl
import certifi
import traceback
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from Crypto.Cipher import DES3
from Crypto.Util.Padding import pad, unpad
from Crypto.Cipher import AES
from http import cookiejar
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.ssl_ import create_urllib3_context


def get_network_time():
    """从淘宝接口获取网络时间"""
    url = "https://acs.m.taobao.com/gw/mtop.common.getTimestamp/"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if "data" in data and "t" in data["data"]:
                timestamp = int(data["data"]["t"])
                return datetime.datetime.fromtimestamp(timestamp / 1000)
            else:
                raise ValueError("接口返回数据格式错误，未找到时间戳")
        else:
            raise Exception(f"获取网络时间失败，状态码: {response.status_code}")
    except Exception as e:
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        print(f"[{current_time}] [错误] 获取网络时间失败: {str(e)}")
        return datetime.datetime.now()


# 获取本地时间和网络时间
local_time = datetime.datetime.now()
network_time = get_network_time()

# 计算时间差
time_diff = network_time - local_time

# 输出时间差，精确到微秒
current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
print(f"[{current_time}] [系统信息] 本地时间: {local_time.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")
print(f"[{current_time}] [系统信息] 网络时间: {network_time.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")
print(f"[{current_time}] [系统信息] 时间差: {time_diff.total_seconds():.6f} 秒")

# 默认兑换策略
MEXZ = os.getenv("MEXZ")

# 定义时间段
morning_start = datetime.time(9, 30, 3)
morning_end = datetime.time(10, 10, 30)
afternoon_start = datetime.time(13, 30, 3)
afternoon_end = datetime.time(14, 10, 30)

# 获取当前时间
now = get_network_time().time()

# 判断当前时间是否在指定的时间段内
if (morning_start <= now <= morning_end) or (afternoon_start <= now <= afternoon_end):
    if not MEXZ:
        MEXZ = "0.5,5,6;1,10,3"
else:
    MEXZ = "0.5,5,6;1,10,3"

# 解析 MEXZ 配置
morning_exchanges, afternoon_exchanges = MEXZ.split(';')
morning_exchanges = [f"{x}元话费" for x in morning_exchanges.split(',')]
afternoon_exchanges = [f"{x}元话费" for x in afternoon_exchanges.split(',')]

current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
print(f"[{current_time}] [配置信息] 上午兑换列表: {morning_exchanges}")
print(f"[{current_time}] [配置信息] 下午兑换列表: {afternoon_exchanges}")


# 从环境变量中获取代理池地址
DY_PROXY = os.getenv("DY_PROXY123")
current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
print(f"[{current_time}] [代理信息] 代理池地址: {'已配置' if DY_PROXY else '未配置'}")

# 新增：从环境变量获取外层循环次数，默认20次
OUTER_LOOP_COUNT = int(os.getenv("OUTER_LOOP_COUNT", "10"))
INNER_LOOP_COUNT = int(os.getenv("INNER_LOOP_COUNT", "5"))

current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
print(f"[{current_time}] [配置信息] 外层循环次数: {OUTER_LOOP_COUNT}")
print(f"[{current_time}] [配置信息] 内层循环次数: {INNER_LOOP_COUNT}")


async def get_proxy_from_pool():
    """从代理池获取代理IP"""
    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    if not DY_PROXY:
        raise ValueError("DY_PROXY 环境变量未设置")

    try:
        async with aiohttp.ClientSession() as session:
            start_time = time_module.time()
            async with session.get(DY_PROXY) as response:
                end_time = time_module.time()
                if response.status != 200:
                    raise Exception(f"从代理池获取代理IP失败，状态码: {response.status}")
                proxy_ip = await response.text()
                proxy_ip = proxy_ip.strip()
                print(f"[{current_time}] [代理信息] 成功获取代理IP，耗时: {end_time - start_time:.3f}秒，IP: {proxy_ip}")
                return proxy_ip
    except Exception as e:
        print(f"[{current_time}] [代理错误] 获取代理IP失败: {str(e)}")
        raise


class BlockAll(cookiejar.CookiePolicy):
    return_ok = set_ok = domain_return_ok = path_return_ok = lambda self, *args, **kwargs: False
    netscape = True
    rfc2965 = hide_cookie2 = False


def print_time_log(m):
    current_time = get_network_time().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    print(f"[{current_time}] {m}")


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


requests.packages.urllib3.disable_warnings()
ssl_context = ssl.create_default_context()
ssl_context.set_ciphers("DEFAULT@SECLEVEL=1")
ss = requests.session()
ss.verify = certifi.where()
ss.headers = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 13; 22081212C Build/TKQ1.220829.002) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.97 Mobile Safari/537.36",
    "Referer": "https://wapact.189.cn:9001/JinDouMall/JinDouMall_independentDetails.html"
}
ss.mount('https://', DESAdapter())
ss.cookies.set_policy(BlockAll())

# 全局变量初始化
yc = 1
wt = 0
kswt = 0.1
yf = get_network_time().strftime("%Y%m")
ip_list = []
jp = {"9": {}, "13": {}}

# 加载兑换记录
try:
    with open('电信金豆换话费.log') as fr:
        dhjl = json.load(fr)
    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    print(f"[{current_time}] [数据加载] 成功加载兑换记录文件")
except Exception as e:
    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    print(f"[{current_time}] [数据加载] 首次运行或记录文件不存在，创建新记录: {str(e)}")
    dhjl = {}

if yf not in dhjl:
    dhjl[yf] = {}
else:
    # 将现有字符串记录转换为集合（仅首次加载时执行）
    for di in dhjl[yf]:
        if isinstance(dhjl[yf][di], str):
            # 拆分字符串为列表，去重后转为集合
            phone_list = dhjl[yf][di].strip('#').split('#') if dhjl[yf][di] else []
            dhjl[yf][di] = set(phone_list)

# 加载token缓存
load_token_file = 'chinaTelecom_cache.json'
try:
    with open(load_token_file, 'r') as f:
        load_token = json.load(f)
    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    print(f"[{current_time}] [数据加载] 成功加载token缓存，共{len(load_token)}条记录")
except Exception as e:
    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    print(f"[{current_time}] [数据加载] token缓存文件不存在，创建新缓存: {str(e)}")
    load_token = {}

# 错误代码映射
errcode = {
    "0": "兑换成功✨",
    "412": "兑换次数已达上限💔",
    "413": "商品已兑完💨",
    "420": "未知错误😥",
    "410": "该活动未开始⏳",
    "501": "服务器处理错误💻",
    "Y0001": "当前等级不足，去升级兑当前话费📈",
    "Y0002": "使用翼相连网络600分钟可兑换此奖品📶",
    "Y0003": "共享流量400M可兑换此奖品💧",
    "Y0004": "共享流量2GB可兑换此奖品💧",
    "Y0005": "当前等级不足，去升级兑当前话费📈",
    "E0001": "您的网龄不足10年，暂不能兑换⏳"
}

# 加密相关配置
key = b'1234567`90koiuyhgtfrdews'
iv = 8 * b'\0'

public_key_b64 = '''-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDBkLT15ThVgz6/NOl6s8GNPofdWzWbCkWnkaAm7O2LjkM1H7dMvzkiqdxU02jamGRHLX/ZNMCXHnPcW/sDhiFCBN18qFvy8g6VYb9QtroI09e176s+ZCtiv7hbin2cCTj99iUpnEloZm19lwHyo69u5UMiPMpq0/XKBO8lYhN/gwIDAQAB
-----END PUBLIC KEY-----'''

public_key_data = '''-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC+ugG5A8cZ3FqUKDwM57GM4io6JGcStivT8UdGt67PEOihLZTw3P7371+N47PrmsCpnTRzbTgcupKtUv8ImZalYk65dU8rjC/ridwhw9ffW2LBwvkEnDkkKKRi2liWIItDftJVBiWOh17o6gfbPoNrWORcAdcbpk2L+udld5kZNwIDAQAB
-----END PUBLIC KEY-----'''


def t(h):
    """计算目标时间戳"""
    date = get_network_time()
    date_zero = date.replace(hour=h, minute=59, second=20)
    date_zero_time = time_module.mktime(date_zero.timetuple())
    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    print(f"[{current_time}] [时间计算] 计算小时{h}的目标时间戳: {date_zero_time}")
    return date_zero_time


def encrypt(text):
    """DES3加密"""
    try:
        cipher = DES3.new(key, DES3.MODE_CBC, iv)
        ciphertext = cipher.encrypt(pad(text.encode(), DES3.block_size))
        return ciphertext.hex()
    except Exception as e:
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        print(f"[{current_time}] [加密错误] DES3加密失败: {str(e)}")
        raise


def decrypt(text):
    """DES3解密"""
    try:
        ciphertext = bytes.fromhex(text)
        cipher = DES3.new(key, DES3.MODE_CBC, iv)
        plaintext = unpad(cipher.decrypt(ciphertext), DES3.block_size)
        return plaintext.decode()
    except Exception as e:
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        print(f"[{current_time}] [解密错误] DES3解密失败: {str(e)}")
        raise


def b64(plaintext):
    """RSA加密并Base64编码"""
    try:
        public_key = RSA.import_key(public_key_b64)
        cipher = PKCS1_v1_5.new(public_key)
        ciphertext = cipher.encrypt(plaintext.encode())
        return base64.b64encode(ciphertext).decode()
    except Exception as e:
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        print(f"[{current_time}] [加密错误] RSA加密失败: {str(e)}")
        raise


def encrypt_para(plaintext):
    """参数加密"""
    try:
        public_key = RSA.import_key(public_key_data)
        cipher = PKCS1_v1_5.new(public_key)
        ciphertext = cipher.encrypt(plaintext.encode())
        return ciphertext.hex()
    except Exception as e:
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        print(f"[{current_time}] [加密错误] 参数加密失败: {str(e)}")
        raise


def encode_phone(text):
    """手机号编码"""
    encoded_chars = []
    for char in text:
        encoded_chars.append(chr(ord(char) + 2))
    return ''.join(encoded_chars)


def ophone(t):
    """手机号AES加密"""
    try:
        key = b'34d7cb0bcdf07523'
        utf8_t = t.encode('utf-8')
        cipher = AES.new(key, AES.MODE_ECB)
        ciphertext = cipher.encrypt(pad(utf8_t, AES.block_size))
        return ciphertext.hex()
    except Exception as e:
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        print(f"[{current_time}] [加密错误] 手机号AES加密失败: {str(e)}")
        raise


def send(uid, content):
    """发送微信推送"""
    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    appToken = os.getenv("WXPUSHER_APP_TOKEN")
    uid = os.getenv("WXPUSHER_UID")

    if not appToken or not uid:
        print(f"[{current_time}] [推送错误] WXPUSHER_APP_TOKEN 或 WXPUSHER_UID 未设置，无法发送推送")
        return None

    try:
        start_time = time_module.time()
        r = requests.post(
            'https://wxpusher.zjiecode.com/api/send/message',
            json={"appToken": appToken, "content": content, "contentType": 1, "uids": [uid]}
        ).json()
        end_time = time_module.time()
        print(f"[{current_time}] [推送信息] 推送请求已发送，耗时: {end_time - start_time:.3f}秒，响应: {r}")
        return r
    except Exception as e:
        print(f"[{current_time}] [推送错误] 发送推送失败: {str(e)}")
        return None


def userLoginNormal(phone, password):
    """正常登录获取ticket"""
    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    masked_phone = phone[:3] + '****' + phone[-4:]
    print(f"[{current_time}] [登录操作] 开始登录账号: {masked_phone}")
    
    try:
        # 生成UUID
        alphabet = 'abcdef0123456789'
        uuid = [
            ''.join(random.sample(alphabet, 8)), 
            ''.join(random.sample(alphabet, 4)),
            '4' + ''.join(random.sample(alphabet, 3)), 
            ''.join(random.sample(alphabet, 4)),
            ''.join(random.sample(alphabet, 12))
        ]
        timestamp = get_network_time().strftime("%Y%m%d%H%M%S")
        loginAuthCipherAsymmertric = 'Android 13 22081212C.' + uuid[0] + uuid[1] + phone + timestamp + password[:6] + '0$$$0.'

        # 发送登录请求
        start_time = time_module.time()
        r = ss.post(
            'https://appgologin.189.cn:9031/login/client/userLoginNormal',
            json={
                "headerInfos": {
                    "code": "userLoginNormal", 
                    "timestamp": timestamp,
                    "broadAccount": "", 
                    "broadToken": "",
                    "clientType": "#10.5.0#channel50#22081212C#",
                    "shopId": "20002", 
                    "source": "110003",
                    "sourcePassword": "Sid98s", 
                    "token": "",
                    "userLoginName": encode_phone(phone)
                },
                "content": {
                    "attach": "test", 
                    "fieldData": {
                        "loginType": "4",
                        "accountType": "",
                        "loginAuthCipherAsymmertric": b64(loginAuthCipherAsymmertric),
                        "deviceUid": uuid[0] + uuid[1] + uuid[2],
                        "phoneNum": encode_phone(phone),
                        "isChinatelecom": "0",
                        "systemVersion": "15.4.0",
                        "authentication": encode_phone(password)
                    }
                }
            }
        ).json()
        end_time = time_module.time()
        print(f"[{current_time}] [登录操作] 登录请求完成，耗时: {end_time - start_time:.3f}秒")

        # 处理登录响应
        if not r:
            print(f"[{current_time}] [登录错误] {masked_phone} 登录请求返回空数据")
            return False

        if 'responseData' not in r or not r['responseData']:
            print(f"[{current_time}] [登录错误] {masked_phone} 响应数据格式错误: {r}")
            return False

        if 'data' not in r['responseData'] or not r['responseData']['data']:
            print(f"[{current_time}] [登录错误] {masked_phone} 数据字段缺失: {r}")
            return False

        if 'loginSuccessResult' not in r['responseData']['data']:
            print(f"[{current_time}] [登录错误] {masked_phone} 登录结果缺失: {r}")
            return False

        login_result = r['responseData']['data']['loginSuccessResult']
        if login_result:
            load_token[phone] = login_result
            with open(load_token_file, 'w') as f:
                json.dump(load_token, f)
            print(f"[{current_time}] [登录成功] {masked_phone} 登录成功，已缓存token")
            ticket = get_ticket(phone, login_result['userId'], login_result['token'])
            return ticket

        print(f"[{current_time}] [登录失败] {masked_phone} 登录结果为空: {r}")
        return False
        
    except Exception as e:
        print(f"[{current_time}] [登录错误] {masked_phone} 登录过程出错: {str(e)}")
        return False


def get_ticket(phone, userId, token):
    """获取ticket"""
    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    masked_phone = phone[:3] + '****' + phone[-4:]
    print(f"[{current_time}] [Ticket获取] 开始获取 {masked_phone} 的ticket")
    
    try:
        start_time = time_module.time()
        r = ss.post(
            'https://appgologin.189.cn:9031/map/clientXML',
            data='<Request><HeaderInfos><Code>getSingle</Code><Timestamp>' + get_network_time().strftime("%Y%m%d%H%M%S") +
            '</Timestamp><BroadAccount></BroadAccount><BroadToken></BroadToken><ClientType>#9.6.1#channel50#iPhone 14 Pro Max#</ClientType>' +
            '<ShopId>20002</ShopId><Source>110003</Source><SourcePassword>Sid98s</SourcePassword><Token>' + token +
            '</Token><UserLoginName>' + phone + '</UserLoginName></HeaderInfos><Content><Attach>test</Attach>' +
            '<FieldData><TargetId>' + encrypt(userId) + '</TargetId><Url>4a6862274835b451</Url></FieldData></Content></Request>',
            headers={'user-agent': 'CtClient;10.4.1;Android;13;22081212C;NTQzNzgx!#!MTgwNTg1'}
        )
        end_time = time_module.time()
        print(f"[{current_time}] [Ticket获取] 请求完成，耗时: {end_time - start_time:.3f}秒，状态码: {r.status_code}")

        tk = re.findall('<Ticket>(.*?)</Ticket>', r.text)
        if len(tk) == 0:
            print(f"[{current_time}] [Ticket错误] {masked_phone} 未找到ticket，响应内容: {r.text[:200]}")
            return False
        
        ticket = decrypt(tk[0])
        print(f"[{current_time}] [Ticket成功] {masked_phone} 获取ticket成功")
        return ticket
        
    except Exception as e:
        print(f"[{current_time}] [Ticket错误] {masked_phone} 获取ticket失败: {str(e)}")
        return False


async def exchange(phone, s, title, aid, uid, amount):
    """执行兑换操作"""
    global h
    masked_phone = phone[:3] + '****' + phone[-4:]
    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    print(f"[{current_time}] [兑换准备] {masked_phone} 准备兑换 {title}")

    try:
        # 时间设置
        now = get_network_time()
        if h is None:
            h = now.hour
            print(f"[{current_time}] [时间设置] 自动设置小时为: {h}")

        # 第一轮等待
        if h == 9:
            first_target_time = now.replace(hour=h, minute=59, second=56, microsecond=0)
        elif h == 13:
            first_target_time = now.replace(hour=h, minute=59, second=56, microsecond=0)
        else:
            first_target_time = now

        first_time_diff = (first_target_time - now).total_seconds()
        if 0 <= first_time_diff <= 300:
            print(f"[{current_time}] [等待开始] {masked_phone} 等待 {first_time_diff:.2f} 秒后开始兑换")
            await asyncio.sleep(first_time_diff)

        # 时间段判断
        morning_start = datetime.time(9, 30, 50)
        morning_end = datetime.time(10, 10, 5)
        afternoon_start = datetime.time(13, 30, 40)
        afternoon_end = datetime.time(14, 10, 5)
        current_time_obj = now.time()

        # 代理设置
        proxy = None
        # if (morning_start <= current_time_obj <= morning_end) or (afternoon_start <= current_time_obj <= afternoon_end):
        #     if DY_PROXY:
        #         try:
        #             proxy_ip = await get_proxy_from_pool()
        #             proxy = f"http://{proxy_ip}"
        #             print(f"[{current_time}] [代理使用] {masked_phone} 将使用代理IP: {proxy_ip}")
        #         except ValueError as e:
        #             print(f"[{current_time}] [代理警告] {masked_phone} {e}，将使用本地网络")
        #     else:
        #         print(f"[{current_time}] [网络设置] {masked_phone} 将使用本地网络")
        # else:
        #     print(f"[{current_time}] [网络设置] {masked_phone} 将使用本地网络")

        # 第二轮等待
        # if h == 9:
        #     second_target_time = now.replace(hour=h, minute=59, second=56, microsecond=803600)
        # elif h == 13:
        #     second_target_time = now.replace(hour=h, minute=59, second=56, microsecond=793600)
        # else:
        #     second_target_time = now

        # second_time_diff = (second_target_time - get_network_time()).total_seconds()
        # if 0 <= second_time_diff <= 300:
        #     print(f"[{current_time}] [等待开始] {masked_phone} 等待 {second_time_diff:.2f} 秒后执行兑换")
        #     await asyncio.sleep(second_time_diff)

        # 执行兑换请求
        url = "https://wapact.189.cn:9001/gateway/standExchange/detailNew/exchange"
        request_start_time = datetime.datetime.now()
        current_time_str = request_start_time.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        print(f"[{current_time_str}] [兑换请求] {masked_phone} 发送兑换 {title} 请求")

        try:
            async with s.post(url, json={"activityId": aid}, proxy=proxy) as r:
                request_end_time = datetime.datetime.now()
                response_time_str = request_end_time.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                response_time = (request_end_time - request_start_time).total_seconds()
                
                print(f"[{response_time_str}] [兑换响应] {masked_phone} 兑换请求响应，状态码: {r.status}, 耗时: {response_time:.6f}秒")
                
                response_text = await r.text()
                if len(response_text) > 500:
                    print(f"[{response_time_str}] [响应内容] {masked_phone} 响应内容过长，前500字符: {response_text[:500]}...")
                else:
                    print(f"[{response_time_str}] [响应内容] {masked_phone} 响应内容: {response_text}")

                if r.status == 412:
                    print(f"[{response_time_str}] [兑换错误] {masked_phone} 遇到412错误，终止本次兑换尝试")
                    return

                if r.status == 200:
                    try:
                        r_json = await r.json()
                        if r_json["code"] == 0:
                            if r_json["biz"] != {} and r_json["biz"]["resultCode"] in errcode:
                                result_msg = errcode[r_json["biz"]["resultCode"]]
                                print(f"[{response_time_str}] [兑换结果] {masked_phone} {title} {result_msg}")

                                # 处理成功或达上限的情况
                                if r_json["biz"]["resultCode"] in ["0", "412"]:
                                    if r_json["biz"]["resultCode"] == "0":
                                        msg = f"{masked_phone}: {title}兑换成功"
                                        send(uid, msg)
                                    
                                    # 更新兑换记录
                                    if title not in dhjl[yf]:
                                        dhjl[yf][title] = set()
                                    
                                    if phone not in dhjl[yf][title]:
                                        dhjl[yf][title].add(phone)
                                        # 保存记录
                                        temp_dhjl = {k: {m: list(n) for m, n in v.items()} for k, v in dhjl.items()}
                                        with open('电信金豆换话费.log', 'w') as f:
                                            json.dump(temp_dhjl, f, ensure_ascii=False)
                                        print(f"[{response_time_str}] [记录更新] {masked_phone} {title} 兑换记录已更新")
                        else:
                            print(f"[{response_time_str}] [兑换异常] {masked_phone} 兑换返回非0状态: {r_json}")
                    except json.JSONDecodeError:
                        print(f"[{response_time_str}] [解析错误] {masked_phone} 响应内容不是有效的JSON: {response_text}")
                else:
                    print(f"[{response_time_str}] [兑换失败] {masked_phone} 兑换请求返回非200状态: {r.status}")

        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            error_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
            print(f"[{error_time}] [请求错误] {masked_phone} 兑换请求发生错误: {str(e)}")

    except Exception as e:
        error_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        print(f"[{error_time}] [兑换异常] {masked_phone} 兑换过程发生异常: {str(e)}")
        traceback.print_exc()


async def dh(phone, s, title, aid, wt, uid):
    """处理单个商品的多次兑换尝试"""
    global h
    masked_phone = phone[:3] + '****' + phone[-4:]
    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    print(f"[{current_time}] [批量兑换] {masked_phone} 开始 {title} 的批量兑换尝试")

    cs = 0
    tasks = []
    creat_start_time = datetime.datetime.now()
    
    # 创建兑换任务
    while cs < INNER_LOOP_COUNT:
        amount = title.split('元')[0]
        if (h == 9 and title in morning_exchanges) or (h == 13 and title in afternoon_exchanges):
            tasks.append(exchange(phone, s, title, aid, uid, amount))
            cs += 1
            await asyncio.sleep(0.05)  # 减少任务创建间隔，加快速度
        else:
            print(f"[{current_time}] [时间过滤] {masked_phone} {title} 不在当前兑换时段，跳过")
            break
    
    creat_end_time = datetime.datetime.now()
    create_duration = (creat_end_time - creat_start_time).total_seconds()
    print(f"[{current_time}] [任务创建] {masked_phone} 已创建 {cs} 个兑换任务，耗时: {create_duration:.6f}秒")

    # 等待目标时间
    while wt > get_network_time().timestamp():
        await asyncio.sleep(0.01)  # 减少等待间隔，提高精度
    
    # 执行所有兑换任务
    await asyncio.gather(*tasks)
    finish_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    print(f"[{finish_time}] [批量完成] {masked_phone} {title} 的 {cs} 次兑换尝试已完成")


def aes_ecb_encrypt(plaintext, key):
    """AES ECB模式加密"""
    try:
        key = key.encode('utf-8')
        if len(key) not in [16, 24, 32]:
            raise ValueError(f"密钥长度必须为16/24/32字节，当前为{len(key)}字节")

        padded_data = pad(plaintext.encode('utf-8'), AES.block_size)
        cipher = AES.new(key, AES.MODE_ECB)
        ciphertext = cipher.encrypt(padded_data)
        return base64.b64encode(ciphertext).decode('utf-8')
    except Exception as e:
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        print(f"[{current_time}] [加密错误] AES加密失败: {str(e)}")
        raise


async def ks(phone, ticket, uid):
    """兑换主流程"""
    global h, wt
    masked_phone = phone[:3] + '****' + phone[-4:]
    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    print(f"[{current_time}] [流程开始] {masked_phone} 开始执行兑换主流程")

    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 13; 22081212C Build/TKQ1.220829.002) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.97 Mobile Safari/537.36",
        "Referer": "https://wapact.189.cn:9001/JinDouMall/JinDouMall_independentDetails.html"
    }

    timeout = aiohttp.ClientTimeout(total=20)
    async with aiohttp.ClientSession(
        connector=aiohttp.TCPConnector(ssl=ssl_context), 
        headers=headers, 
        timeout=timeout
    ) as s:
        try:
            # 准备登录数据
            login_data = {
                "ticket": ticket,
                "backUrl": "https%3A%2F%2Fwapact.189.cn%3A9001",
                "platformCode": "P201010301",
                "loginType": 2
            }
            encrypted_data = aes_ecb_encrypt(json.dumps(login_data), 'telecom_wap_2018')
            
            # 登录重试机制
            max_retries = 3
            retries = 0
            login = None
            while retries < max_retries:
                try:
                    login_start_time = time_module.time()
                    login_response = await s.post(
                        'https://wapact.189.cn:9001/unified/user/login',
                        data=encrypted_data,
                        headers={
                            "Content-Type": "application/json;charset=UTF-8",
                            "Accept": "application/json, text/javascript, */*; q=0.01"
                        }
                    )
                    login_end_time = time_module.time()
                    print(f"[{current_time}] [登录请求] {masked_phone} 登录请求完成，耗时: {login_end_time - login_start_time:.3f}秒，状态码: {login_response.status}")

                    if login_response.status == 200:
                        login = await login_response.json()
                        break
                    elif login_response.status == 412:
                        print(f"[{current_time}] [登录重试] {masked_phone} 登录返回412，准备重试")
                        retries += 1
                        await asyncio.sleep(2 **retries)
                    else:
                        print(f"[{current_time}] [登录失败] {masked_phone} 登录状态码异常: {login_response.status}")
                        print(f"[{current_time}] [响应内容] {masked_phone} 登录响应: {await login_response.text()}")
                        retries += 1
                        await asyncio.sleep(2** retries)

                except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                    retries += 1
                    print(f"[{current_time}] [登录异常] {masked_phone} 登录尝试 {retries}/{max_retries} 失败: {str(e)}")
                    await asyncio.sleep(2 **retries)

            if not login or login.get('code') != 0:
                print(f"[{current_time}] [登录失败] {masked_phone} 登录失败，响应: {login}")
                return

            # 设置Authorization
            s.headers["Authorization"] = "Bearer " + login["biz"]["token"]
            print(f"[{current_time}] [登录成功] {masked_phone} 登录成功，已设置Authorization")

            # 查询金豆余额
            try:
                balance_start = time_module.time()
                r = await s.get('https://wapact.189.cn:9001/gateway/golden/api/queryInfo')
                balance_end = time_module.time()
                r_json = await r.json()
                
                if r_json.get("code") == 0 and "biz" in r_json and "amountTotal" in r_json["biz"]:
                    amountTotal = r_json["biz"]["amountTotal"]
                    print(f"[{current_time}] [金豆查询] {masked_phone} 金豆余额: {amountTotal}个，耗时: {balance_end - balance_start:.3f}秒")
                else:
                    print(f"[{current_time}] [金豆异常] {masked_phone} 金豆查询响应异常: {r_json}")
            except Exception as e:
                print(f"[{current_time}] [金豆错误] {masked_phone} 查询金豆余额失败: {str(e)}")

            # 获取商品列表
            try:
                goods_start = time_module.time()
                query_url = 'https://wapact.189.cn:9001/gateway/golden/goldGoods/getGoodsList?floorType=0&userType=1&page=1&order=3&tabOrder='
                query_response = await s.get(query_url)
                goods_end = time_module.time()
                query_json = await query_response.json()
                print(f"[{current_time}] [商品列表] {masked_phone} 获取商品列表完成，耗时: {goods_end - goods_start:.3f}秒")

                if "biz" in query_json and "ExchangeGoodslist" in query_json["biz"]:
                    for item in query_json["biz"]["ExchangeGoodslist"]:
                        if '话费' not in item.get("title", ""):
                            continue
                        # 匹配上午兑换商品
                        for morning_item in morning_exchanges:
                            if morning_item in item["title"]:
                                jp["9"][morning_item] = item["id"]
                        # 匹配下午兑换商品
                        for afternoon_item in afternoon_exchanges:
                            if afternoon_item in item["title"]:
                                jp["13"][afternoon_item] = item["id"]
                    
                else:
                    print(f"[{current_time}] [商品异常] {masked_phone} 商品列表格式异常: {query_json}")
            except Exception as e:
                print(f"[{current_time}] [商品错误] {masked_phone} 获取商品列表失败: {str(e)}")

            # 确定当前时段
            h = get_network_time().hour
            if 11 > h:
                h = 9
            else:
                h = 13

            if len(sys.argv) == 2:
                h = int(sys.argv[1])
            print(f"[{current_time}] [时段确定] {masked_phone} 当前兑换时段: {h}点")

            # 获取当前时段的商品
            d = jp[str(h)]
            wt = t(h) + kswt
            print(f"[{current_time}] [目标时间] {masked_phone} 兑换目标时间戳: {wt}")

            # 过滤已兑换的商品
            valid_products = []
            for di in sorted(d.keys(), key=lambda x: float(x.replace('元话费', '')), reverse=True):
                if phone not in dhjl[yf].get(di, set()):
                    valid_products.append(di)
            print(f"[{current_time}] [商品过滤] {masked_phone} 有效兑换商品: {valid_products}")

            # 外层循环控制
            for loop in range(OUTER_LOOP_COUNT):
                loop_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                print(f"[{loop_time}] [轮次开始] {masked_phone} 开始第 {loop + 1}/{OUTER_LOOP_COUNT} 轮兑换")
                
                # 检查是否需要退出
                if wt - time_module.time() > 30 * 60:
                    print(f"[{loop_time}] [超时退出] {masked_phone} 距离目标时间超过30分钟，退出兑换")
                    return

                # 创建本轮兑换任务
                tasks = []
                for di in valid_products:
                    tasks.append(dh(phone, s, di, d[di], wt, uid))
                
                print(f"[{loop_time}] [任务数量] {masked_phone} 第 {loop + 1} 轮共有 {len(tasks)} 个兑换任务")
                await asyncio.gather(*tasks)

                # 轮次间隔
                if loop < OUTER_LOOP_COUNT - 1:
                    await asyncio.sleep(0.005)  # 减少轮次间隔，加快速度
                    next_loop_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                    print(f"[{next_loop_time}] [轮次间隔] {masked_phone} 第 {loop + 1} 轮完成，准备下一轮")

            final_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
            print(f"[{final_time}] [流程完成] {masked_phone} 所有 {OUTER_LOOP_COUNT} 轮兑换已完成")

        except Exception as e:
            error_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
            print(f"[{error_time}] [流程错误] {masked_phone} 兑换主流程发生错误: {str(e)}")
            traceback.print_exc()
            return


async def main():
    """主函数"""
    global wt, rs, h
    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    print(f"[{current_time}] [程序启动] 电信金豆兑换话费程序开始运行")

    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 13; 22081212C Build/TKQ1.220829.002) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.97 Mobile Safari/537.36",
        "Referer": "https://wapact.189.cn:9001/JinDouMall/JinDouMall_independentDetails.html"
    }

    timeout = aiohttp.ClientTimeout(total=20)
    rs = 0
    accounts = []
    
    # 加载账号
    china_telecom_account = os.getenv('chinaTelecomAccount')
    if china_telecom_account:
        accounts.extend(re.split(r'@|&', china_telecom_account))
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        print(f"[{current_time}] [账号加载] 成功加载 {len(accounts)} 个账号")
    else:
        print(f"[{current_time}] [账号错误] 未检测到任何账号，请检查环境变量 chinaTelecomAccount")
        return

    # 分批处理账号
    batch_size = 20
    total_batches = (len(accounts) + batch_size - 1) // batch_size
    print(f"[{current_time}] [批量设置] 账号将分为 {total_batches} 批处理，每批 {batch_size} 个")

    for i in range(0, len(accounts), batch_size):
        batch_accounts = accounts[i:i + batch_size]
        batch_num = i // batch_size + 1
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        print(f"[{current_time}] [批次开始] 开始处理第 {batch_num}/{total_batches} 批账号，共 {len(batch_accounts)} 个")

        tasks = []
        for account in batch_accounts:
            try:
                account_info = account.split('#')
                if len(account_info) < 2:
                    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                    print(f"[{current_time}] [账号错误] 账号格式错误: {account}，正确格式应为 手机号#密码#uid")
                    continue

                phone = account_info[0]
                password = account_info[1]
                uid = account_info[-1] if len(account_info) > 2 else ""
                masked_phone = phone[:3] + '****' + phone[-4:]
                ticket = False

                # 尝试使用缓存登录
                if phone in load_token:
                    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                    print(f"[{current_time}] [登录方式] {masked_phone} 尝试使用缓存登录")
                    ticket = get_ticket(phone, load_token[phone]['userId'], load_token[phone]['token'])

                # 缓存登录失败则使用密码登录
                if not ticket:
                    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                    print(f"[{current_time}] [登录方式] {masked_phone} 缓存登录失败，尝试密码登录")
                    ticket = userLoginNormal(phone, password)

                # 登录成功则添加到任务列表
                if ticket:
                    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                    print(f"[{current_time}] [任务添加] {masked_phone} 登录成功，添加到兑换任务列表")
                    tasks.append(ks(phone, ticket, uid))
                else:
                    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                    print(f"[{current_time}] [登录失败] {masked_phone} 登录失败，跳过该账号")
            except Exception as e:
                current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                print(f"[{current_time}] [账号处理错误] 处理账号 {account} 时出错: {str(e)}")

        # 等待目标时间
        while wt > datetime.datetime.now().timestamp():
            await asyncio.sleep(0.01)  # 提高等待精度

        # 执行当前批次的所有任务
        if tasks:
            current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
            print(f"[{current_time}] [任务执行] 开始执行第 {batch_num} 批的 {len(tasks)} 个兑换任务")
            await asyncio.gather(*tasks)
        else:
            current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
            print(f"[{current_time}] [任务为空] 第 {batch_num} 批没有可执行的兑换任务")

        # 批次间隔
        batch_end_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        print(f"[{batch_end_time}] [批次完成] 第 {batch_num}/{total_batches} 批账号处理完成")
        if batch_num < total_batches:
            await asyncio.sleep(1)  # 批次间隔


START_LOG = rf'''
+--------------------------------------------------------------------+
|  🌸 欢迎使用 金豆兑换话费 ✨                                                              
+--------------------------------------------------------------------+
'''

if __name__ == "__main__":
    print(START_LOG)
    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    print(f"[{current_time}] [系统信息] 程序会提前【{kswt} 秒】准备")
    
    if len(sys.argv) > 1:
        h = int(sys.argv[1])
        print(f"[{current_time}] [参数设置] 通过命令行参数指定小时: {h}")
    else:
        h = None
        print(f"[{current_time}] [参数设置] 未指定小时，将自动判断")
    
    asyncio.run(main())

# 生成用户视角的兑换记录
current_month = get_network_time().strftime("%Y%m")
try:
    with open('电信金豆换话费.log', 'r') as fr:
        dhjl = json.load(fr)
    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    print(f"[{current_time}] [记录处理] 加载兑换记录用于生成用户视角日志")
except FileNotFoundError:
    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    print(f"[{current_time}] [记录处理] 未找到兑换记录文件")
    dhjl = {}

# 转换记录格式
dhjl2 = {}
if current_month in dhjl:
    records = dhjl[current_month]
    for fee, phones in records.items():
        if isinstance(phones, list):
            phone_list = phones
        else:
            phone_list = phones.strip('#').split('#')
        
        for phone in phone_list:
            masked_phone = phone[:3] + '****' + phone[-4:]
            if masked_phone not in dhjl2:
                dhjl2[masked_phone] = {}
            if current_month not in dhjl2[masked_phone]:
                dhjl2[masked_phone][current_month] = []
            dhjl2[masked_phone][current_month].append(fee)

# 保存转换后的记录
with open('电信金豆换话费2.log', 'w') as fw:
    json.dump(dhjl2, fw, ensure_ascii=False, indent=4)
current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
print(f"[{current_time}] [记录处理] 用户视角兑换记录已保存到 电信金豆换话费2.log")

# 推送时间判断
current_time = get_network_time()
start_time_1 = current_time.replace(hour=10, minute=0, second=30)
end_time_1 = current_time.replace(hour=10, minute=10, second=0)
start_time_2 = current_time.replace(hour=14, minute=0, second=30)
end_time_2 = current_time.replace(hour=14, minute=10, second=0)

in_time_window = (start_time_1 <= current_time < end_time_1) or (start_time_2 <= current_time < end_time_2)
final_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
if in_time_window:
    print(f"[{final_time}] [程序结束] 任务执行完成，当前在推送时间窗口内")
else:
    print(f"[{final_time}] [程序结束] 任务执行完成，当前不在推送时间窗口内")




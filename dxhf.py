#!/usr/bin/env python3
import os
import re
import sys
import ssl
import time
import json
import base64
import random
import certifi
import aiohttp
import asyncio
import certifi
import datetime
import requests
import binascii
from http import cookiejar
from Crypto.Cipher import DES3
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from Crypto.Util.Padding import pad, unpad
from aiohttp import ClientSession, TCPConnector

run_num = os.environ.get('reqNUM') or "100"

MAX_RETRIES = 100
RATE_LIMIT = 100  # 每秒请求数限制

yf = datetime.datetime.now().strftime("%Y%m")
try:
    with open('电信金豆换话费.log') as fr:
        dhjl = json.load(fr)
except:
    dhjl = {}
if yf not in dhjl:
    dhjl[yf] = {}

class RateLimiter:
    def __init__(self, rate_limit):
        self.rate_limit = rate_limit
        self.tokens = rate_limit
        self.updated_at = time.monotonic()

    async def acquire(self):
        while self.tokens < 1:
            self.add_new_tokens()
            await asyncio.sleep(0.1)
        self.tokens -= 1

    def add_new_tokens(self):
        now = time.monotonic()
        time_since_update = now - self.updated_at
        new_tokens = time_since_update * self.rate_limit
        if new_tokens > 1:
            self.tokens = min(self.tokens + new_tokens, self.rate_limit)
            self.updated_at = now

class AsyncSessionManager:
    def __init__(self):
        self.session = None
        self.connector = None

    async def __aenter__(self):
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        ssl_context.set_ciphers('DEFAULT@SECLEVEL=1')
        self.connector = TCPConnector(ssl=ssl_context, limit=1000)
        self.session = ClientSession(connector=self.connector)
        return self.session

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()
        await self.connector.close()

async def retry_request(session, method, url, **kwargs):
    for attempt in range(MAX_RETRIES):
        try:
            await asyncio.sleep(1)
            async with session.request(method, url, **kwargs) as response:
                return await response.json()

        except (aiohttp.ClientConnectionError, aiohttp.ServerTimeoutError) as e:
            print(f"请求失败，第 {attempt + 1} 次重试: {e}")
            if attempt == MAX_RETRIES - 1:
                raise
            await asyncio.sleep(2 ** attempt)

class BlockAll(cookiejar.CookiePolicy):
    return_ok = set_ok = domain_return_ok = path_return_ok = lambda self, *args, **kwargs: False
    netscape = True
    rfc2965 = hide_cookie2 = False

def printn(m):
    current_time = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f'\n[{current_time}] {m}')

context = ssl.create_default_context()
context.set_ciphers('DEFAULT@SECLEVEL=1')  # 低安全级别0/1
context.check_hostname = False  # 禁用主机
context.verify_mode = ssl.CERT_NONE  # 禁用证书

class DESAdapter(requests.adapters.HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        kwargs['ssl_context'] = context
        return super().init_poolmanager(*args, **kwargs)

requests.packages.urllib3.disable_warnings()
ss = requests.session()
ss.headers = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 13; 22081212C Build/TKQ1.220829.002) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.97 Mobile Safari/537.36",
    "Referer": "https://wapact.189.cn:9001/JinDouMall/JinDouMall_independentDetails.html"
}
ss.mount('https://', DESAdapter())
ss.cookies.set_policy(BlockAll())
runTime = 0
key = b'1234567`90koiuyhgtfrdews'
iv = 8 * b'\0'

public_key_b64 = '''-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDBkLT15ThVgz6/NOl6s8GNPofdWzWbCkWnkaAm7O2LjkM1H7dMvzkiqdxU02jamGRHLX/ZNMCXHnPcW/sDhiFCBN18qFvy8g6VYb9QtroI09e176s+ZCtiv7hbin2cCTj99iUpnEloZm19lwHyo69u5UMiPMpq0/XKBO8lYhN/gwIDAQAB
-----END PUBLIC KEY-----'''

public_key_data = '''-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC+ugG5A8cZ3FqUKDwM57GM4io6JGcStivT8UdGt67PEOihLZTw3P7371+N47PrmsCpnTRzbTgcupKtUv8ImZalYk65dU8rjC/ridwhw9ffW2LBwvkEnDkkKKRi2liWIItDftJVBiWOh17o6gfbPoNrWORcAdcbpk2L+udld5kZNwIDAQAB
-----END PUBLIC KEY-----'''

def get_first_three(value):
    if isinstance(value, (int, float)):
        return int(str(value)[:3])
    elif isinstance(value, str):
        return str(value)[:3]
    else:
        raise TypeError("error")

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
    if not isinstance(plaintext, str):
        plaintext = json.dumps(plaintext)
    public_key = RSA.import_key(public_key_data)
    cipher = PKCS1_v1_5.new(public_key)
    ciphertext = cipher.encrypt(plaintext.encode())
    return binascii.hexlify(ciphertext).decode()

def encode_phone(text):
    encoded_chars = []
    for char in text:
        encoded_chars.append(chr(ord(char) + 2))
    return ''.join(encoded_chars)

def userLoginNormal(phone, password):
    alphabet = 'abcdef0123456789'
    uuid = [
        ''.join(random.sample(alphabet, 8)),
        ''.join(random.sample(alphabet, 4)),
        '4' + ''.join(random.sample(alphabet, 3)),
        ''.join(random.sample(alphabet, 4)),
        ''.join(random.sample(alphabet, 12))
    ]
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    loginAuthCipherAsymmertric = 'iPhone 14 15.4.' + uuid[0] + uuid[1] + phone + timestamp + password[:6] + '0$$$0.'
    r = ss.post(
        'https://appgologin.189.cn:9031/login/client/userLoginNormal',
        json={
            "headerInfos": {
                "code": "userLoginNormal",
                "timestamp": timestamp,
                "broadAccount": "",
                "broadToken": "",
                "clientType": "#9.6.1#channel50#iPhone 14 Pro Max#",
                "shopId": "20002",
                "source": "110003",
                "sourcePassword": "Sid98s",
                "token": "",
                "userLoginName": phone
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
                    "authentication": password
                }
            }
        },
        verify=certifi.where()
    ).json()
    l = r.get('responseData', {}).get('data', {}).get('loginSuccessResult')
    if l:
        ticket = get_ticket(phone, l.get('userId'), l.get('token'))
        return ticket
    return False

async def exchangeForDay(phone, session, rid, start_time):
    if time.time() - start_time >= 30:
        printn(f"{get_first_three(phone)}: 兑换时间已到，停止兑换")
        return

    async def conversion_task():
        await conversionRights(phone, rid, session)

    tasks = [asyncio.create_task(conversion_task()) for _ in range(5)]
    await asyncio.gather(*tasks)

    # 继续进行下一轮兑换，直到时间达到30秒
    await exchangeForDay(phone, session, rid, start_time)

def get_ticket(phone, userId, token):
    r = ss.post(
        'https://appgologin.189.cn:9031/map/clientXML',
        data=f'<Request><HeaderInfos><Code>getSingle</Code><Timestamp>{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}</Timestamp><BroadAccount></BroadAccount><BroadToken></BroadToken><ClientType>#9.6.1#channel50#iPhone 14 Pro Max#</ClientType><ShopId>20002</ShopId><Source>110003</Source><SourcePassword>Sid98s</SourcePassword><Token>{token}</Token><UserLoginName>{phone}</UserLoginName></HeaderInfos><Content><Attach>test</Attach><FieldData><TargetId>{encrypt(userId)}</TargetId><Url>4a6862274835b451</Url></FieldData></Content></Request>',
        headers={'user-agent': 'CtClient;10.4.1;Android;13;22081212C;NTQzNzgx!#!MTgwNTg1'},
        verify=certifi.where()
    )
    tk = re.findall('<Ticket>(.*?)</Ticket>', r.text)
    if len(tk) == 0:
        return False
    return decrypt(tk[0])

async def conversionRights(phone, aid, session):
    try:
        ruishu_cookies = await get_ruishu_cookies()
        if not ruishu_cookies:
            printn(f"{get_first_three(phone)}: 无法获取 Ruishu cookies")
            return

        value = {
            "phone": phone,
            "rightsId": aid
        }
        paraV = encrypt_para(value)

        printn(f"{get_first_three(phone)}: 开始兑换")

        response = await asyncio.to_thread(
            session.post,
            'https://wappark.189.cn/jt-sign/paradise/conversionRights',
            json={"para": paraV},
            cookies=ruishu_cookies
        )

        login = response.json()
        printn(f"{get_first_three(phone)}: {login}")

        if '兑换成功' in response.text:
            dhjl[yf]['等级话费'] = dhjl[yf].get('等级话费', "") + "#" + phone
            with open('电信金豆换话费.log', 'w') as f:
                json.dump(dhjl, f, ensure_ascii=False)
            return
        elif '已兑换' in response.text:
            dhjl[yf]['等级话费'] = dhjl[yf].get('等级话费', "") + "#" + phone
            with open('电信金豆换话费.log', 'w') as f:
                json.dump(dhjl, f, ensure_ascii=False)
            return

    except Exception as e:
        printn(f"{get_first_three(phone)}: 兑换请求发生错误: {str(e)}")

async def getLevelRightsList(phone, session):
    try:
        ruishu_cookies = await get_ruishu_cookies()
        if not ruishu_cookies:
            print("无法获取 Ruishu cookies")
            return None

        value = {
            "phone": phone
        }
        paraV = encrypt_para(value)

        response = session.post(
            'https://wappark.189.cn/jt-sign/paradise/getLevelRightsList',
            json={"para": paraV},
            cookies=ruishu_cookies
        )

        data = response.json()
        if data.get('code') == 401:
            print(f"获取失败: {data}, 原因大概是sign过期了")
            return None

        current_level = int(data.get('currentLevel', 1))
        key_name = 'V' + str(current_level)
        ids = [item['id'] for item in data.get(key_name, []) if item.get('name') == '话费']
        return ids

    except Exception as e:
        print(f"获取失败, 重试一次: {str(e)}")
        try:
            ruishu_cookies = await get_ruishu_cookies()
            if not ruishu_cookies:
                print("重试时无法获取 Ruishu cookies")
                return None

            paraV = encrypt_para(value)
            response = session.post(
                'https://wappark.189.cn/jt-sign/paradise/getLevelRightsList',
                json={"para": paraV},
                cookies=ruishu_cookies
            )

            data = response.json()
            if data.get('code') == 401:
                print(f"重试获取失败: {data}, 原因大概是sign过期了")
                return None

            current_level = int(data.get('currentLevel', 1))
            key_name = 'V' + str(current_level)
            ids = [item['id'] for item in data.get(key_name, []) if item.get('name') == '话费']
            return ids

        except Exception as e:
            print(f"重试也失败了: {str(e)}")
            return None

async def get_ruishu_cookies():
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ruishu_path = os.path.join(current_dir, 'Ruishu.py')

        process = await asyncio.create_subprocess_exec(
            sys.executable,
            ruishu_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            print(f"Ruishu.py 执行错误: {stderr.decode()}")
            return None

        cookies = json.loads(stdout.decode().strip())
        return cookies

    except Exception as e:
        print(f"获取 Ruishu cookies 时发生错误: {str(e)}")
        return None

async def qgNight(phone, ticket, start_time):
    session = requests.Session()
    session.mount('https://', DESAdapter())
    session.verify = False  # 禁用证书验证
    sign = await getSign(ticket, session)
    if sign:
        session.headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 13; 22081212C Build/TKQ1.220829.002) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.97 Mobile Safari/537.36",
            "sign": sign
        }
    else:
        print("未获取sign。")
        return

    rightsId = await getLevelRightsList(phone, session)
    if rightsId:
        print("获取到了rightsId: " + rightsId[0])
    else:
        print("未能获取rightsId。")
        return

    await exchangeForDay(phone, session, rightsId[0], start_time)

async def getSign(ticket, session):
    try:
        ruishu_cookies = await get_ruishu_cookies()
        if not ruishu_cookies:
            print("无法获取 Ruishu cookies")
            return None

        cookies = {**ruishu_cookies}

        response = session.get(
            f'https://wappark.189.cn/jt-sign/ssoHomLogin?ticket={ticket}',
            cookies=cookies
        ).json()

        if response.get('resoultCode') == '0':
            sign = response.get('sign')
            return sign
        else:
            print(f"获取sign失败[{response.get('resoultCode')}]: {response}")
    except Exception as e:
        print(f"getSign 发生错误: {str(e)}")
    return None

async def main():
    start_time = time.time()
    tasks = []
    PHONES = os.environ.get('lcld')  # 修改为 lcld 环境变量
    if not PHONES:
        print("环境变量 lcld 未设置或为空，请检查配置。")
        return

    phone_list = PHONES.split('\n')
    for phoneV in phone_list:
        value = phoneV.split('#')
        if len(value) != 2:
            print(f"环境变量格式错误: {phoneV}，应为 账号#密码")
            continue
        phone, password = value[0], value[1]
        if '等级话费' not in dhjl[yf]:
            dhjl[yf]['等级话费'] = ""
        if phone in dhjl[yf]['等级话费']:
            printn(f"{phone} 等级话费 已兑换")
            continue
        printn(f'{get_first_three(phone)} 开始登录')
        ticket = userLoginNormal(phone, password)
        if ticket:
            tasks.append(qgNight(phone, ticket, start_time))
        else:
            printn(f'{phone} 登录失败')
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
    print("所有任务都已执行完毕!")

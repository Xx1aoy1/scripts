# !/usr/bin/python3
# -- coding: utf-8 --
# -------------------------------
#电信兑话费
#export jdhf="phone@服务密码&phone2@服务密码"
# cron:55 59 9,13 * * *
# const $ = new Env('电信金豆换话费')
import requests
import re
import time
import json
import random
import datetime
import base64
import threading
import ssl
import execjs
import os
import sys
import urllib3
import concurrent.futures
import ntplib
import subprocess
import io
import codecs
from operator import itemgetter

from bs4 import BeautifulSoup

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from Crypto.Cipher import DES3
from Crypto.Util.Padding import pad, unpad
from Crypto.Util.strxor import strxor
from Crypto.Cipher import AES
from http import cookiejar  # Python 2: import cookielib as cookiejar
from requests.adapters import HTTPAdapter
from urllib3.util.ssl_ import create_urllib3_context




# 标准输出重定向
original_stdout = sys.stdout
original_stderr = sys.stderr

# 创建UTF-8编码的输出流
utf8_stdout = codecs.getwriter('utf-8')(original_stdout.buffer, 'replace')
utf8_stderr = codecs.getwriter('utf-8')(original_stderr.buffer, 'replace')

# 替换标准输出流
sys.stdout = utf8_stdout
sys.stderr = utf8_stderr

# 初始化通知服务
send = None  # 初始化 send 变量
if os.path.isfile('notify.py'):
    try:
        from notify import send
        print("加载通知服务成功！")
    except Exception as e:
        print(f"加载通知服务异常: {str(e)}")
else:
    print("未找到notify.py，将使用内置通知方式")


class BlockAll(cookiejar.CookiePolicy):
    return_ok = set_ok = domain_return_ok = path_return_ok = lambda self, *args, **kwargs: False
    netscape = True
    rfc2965 = hide_cookie2 = False
    
# 添加日志控制变量
VERBOSE_LOG = True  # 设置为True时输出详细日志，False时只输出重要日志

def printn(m, important=False):  
    # 如果是重要日志或者详细日志模式开启，才输出
    if important or VERBOSE_LOG:
        print(f'\n{m}')

ORIGIN_CIPHERS = ('DEFAULT@SECLEVEL=1')

ip_list = []
class DESAdapter(HTTPAdapter):
    def __init__(self, *args, **kwargs):
        """
        A TransportAdapter that re-enables 3DES support in Requests.
        """
        CIPHERS = ORIGIN_CIPHERS.split(':')
        random.shuffle(CIPHERS)
        CIPHERS = ':'.join(CIPHERS)
        self.CIPHERS = CIPHERS + ':!aNULL:!eNULL:!MD5'
        super().__init__(*args, **kwargs)
 
    def init_poolmanager(self, *args, **kwargs):
        context = create_urllib3_context(ciphers=self.CIPHERS)
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        kwargs['ssl_context'] = context
        return super(DESAdapter, self).init_poolmanager(*args, **kwargs)
 
    def proxy_manager_for(self, *args, **kwargs):
        context = create_urllib3_context(ciphers=self.CIPHERS)
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        kwargs['ssl_context'] = context
        return super(DESAdapter, self).proxy_manager_for(*args, **kwargs)
 

requests.packages.urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE
ssl_context.set_ciphers('DEFAULT@SECLEVEL=0')
ss = requests.session()
ss.verify = False
ss.headers={"User-Agent":"Mozilla/5.0 (Linux; Android 13; 22081212C Build/TKQ1.220829.002) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.97 Mobile Safari/537.36","Referer":"https://wapact.189.cn:9001/JinDouMall/JinDouMall_independentDetails.html"}    
ss.mount('https://', DESAdapter())       
yc = 0.1
wt = 0
kswt = -3
yf = datetime.datetime.now().strftime("%Y%m")

# 添加测试模式变量
is_test_mode = True

# 添加服务器时间偏移量变量
server_time_offset = 0

# 修改jp字典，增加10点和14点的键
jp = {"9":{},"10":{},"12":{},"13":{},"14":{},"23":{}}

# 添加全局商品信息缓存
all_goods_cache = {}
preloaded_accounts = set()

try:
    with open('电信金豆换话费.log') as fr:
        dhjl = json.load(fr)
except:
    dhjl = {}
if yf not in dhjl:
    dhjl[yf] = {}
        
# 添加线程锁，防止并发写入冲突
dhjl_lock = threading.Lock()
goods_cache_lock = threading.Lock()

# 增加账号会话缓存
account_sessions = {}
account_sessions_lock = threading.Lock()

wxp={}
errcode = {
    "0":"兑换成功",
    "412":"兑换次数已达上限",
    "413":"商品已兑完",
    "420":"未知错误",
    "410":"该活动已失效~",
    "Y0001":"当前等级不足，去升级兑当前话费",
    "Y0002":"使用翼相连网络600分钟或连接并拓展网络500分钟可兑换此奖品",
    "Y0003":"使用翼相连共享流量400M或共享WIFI：2GB可兑换此奖品",
    "Y0004":"使用翼相连共享流量2GB可兑换此奖品",
    "Y0005":"当前等级不足，去升级兑当前话费",
    "E0001":"您的网龄不足10年，暂不能兑换"
}

#加密参数
key = b'1234567`90koiuyhgtfrdews'
iv = 8 * b'\0'

public_key_b64 = '''-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDBkLT15ThVgz6/NOl6s8GNPofdWzWbCkWnkaAm7O2LjkM1H7dMvzkiqdxU02jamGRHLX/ZNMCXHnPcW/sDhiFCBN18qFvy8g6VYb9QtroI09e176s+ZCtiv7hbin2cCTj99iUpnEloZm19lwHyo69u5UMiPMpq0/XKBO8lYhN/gwIDAQAB
-----END PUBLIC KEY-----'''

public_key_data = '''-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC+ugG5A8cZ3FqUKDwM57GM4io6JGcStivT8UdGt67PEOihLZTw3P7371+N47PrmsCpnTRzbTgcupKtUv8ImZalYk65dU8rjC/ridwhw9ffW2LBwvkEnDkkKKRi2liWIItDftJVBiWOh17o6gfbPoNrWORcAdcbpk2L+udld5kZNwIDAQAB
-----END PUBLIC KEY-----'''

# 添加NTP服务器列表
ntp_servers = [
    'ntp.myhuaweicloud.com',
    'ntp.aliyun.com',
    'ntp.tencent.com',
    'time.windows.com',
    'time.apple.com',
    'pool.ntp.org'
]

# 获取服务器时间并计算偏移量
def sync_time():
    global server_time_offset
    
    for server in ntp_servers:
        try:
            printn(f"正在与NTP服务器 {server} 同步时间...", important=True)
            client = ntplib.NTPClient()
            response = client.request(server, timeout=5)
            server_time = response.tx_time
            local_time = time.time()
            server_time_offset = server_time - local_time
            
            printn(f"时间同步成功! 服务器时间偏移量: {server_time_offset:.2f}秒", important=True)
            return True
        except Exception as e:
            printn(f"与NTP服务器 {server} 同步时间失败: {str(e)}")
    
    printn("所有NTP服务器同步失败，将使用本地时间", important=True)
    return False

# 获取当前准确时间（考虑服务器偏移）
def get_accurate_time():
    return time.time() + server_time_offset

# 修改t函数，支持测试模式和服务器时间偏移
def t(h):    
    # 测试模式下返回当前时间戳减去5秒，使脚本立即开始执行
    if is_test_mode:
        return get_accurate_time() - 5
        
    date = datetime.datetime.now()
    date_zero = datetime.datetime.now().replace(year=date.year, month=date.month, day=date.day, hour=h, minute=59, second=59)
    date_zero_time = int(time.mktime(date_zero.timetuple()))
    
    # 应用服务器时间偏移
    return date_zero_time + server_time_offset
    

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

# 发送微信推送通知
def send(uid, content):
    if not appToken or not uid:
        printn("未设置appToken或uid，无法发送通知")
        return False
    
    try:
        r = requests.post('https://wxpusher.zjiecode.com/api/send/message',
                         json={"appToken": appToken, "content": content, "contentType": 1, "uids": [uid]}).json()
        printn(f"通知发送结果: {r}", important=True)
        return r.get('success', False)
    except Exception as e:
        printn(f"发送通知失败: {str(e)}", important=True)
        return False

# 使用系统通知脚本发送通知
def send_system_notify(title, content):
    try:
        # 获取当前脚本所在目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        notify_script = os.path.join(current_dir, 'notify.py')
        
        # 检查通知脚本是否存在
        if not os.path.exists(notify_script):
            printn(f"通知脚本不存在: {notify_script}")
            return False
        
        # 调用通知脚本
        cmd = [sys.executable, notify_script, title, content]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            printn(f"系统通知发送成功", important=True)
            return True
        else:
            printn(f"系统通知发送失败: {result.stderr}", important=True)
            return False
    except Exception as e:
        printn(f"发送系统通知时出错: {str(e)}", important=True)
        return False
            
def userLoginNormal(phone,password):
    alphabet = 'abcdef0123456789'
    uuid = [''.join(random.sample(alphabet, 8)),''.join(random.sample(alphabet, 4)),'4'+''.join(random.sample(alphabet, 3)),''.join(random.sample(alphabet, 4)),''.join(random.sample(alphabet, 12))]
    timestamp=datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    loginAuthCipherAsymmertric = 'iPhone 14 15.4.' + uuid[0] + uuid[1] + phone + timestamp + password[:6] + '0$$$0.'
    
    try:
        r = ss.post('https://appgologin.189.cn:9031/login/client/userLoginNormal',json={"headerInfos": {"code": "userLoginNormal", "timestamp": timestamp, "broadAccount": "", "broadToken": "", "clientType": "#9.6.1#channel50#iPhone 14 Pro Max#", "shopId": "20002", "source": "110003", "sourcePassword": "Sid98s", "token": "", "userLoginName": phone}, "content": {"attach": "test", "fieldData": {"loginType": "4", "accountType": "", "loginAuthCipherAsymmertric": b64(loginAuthCipherAsymmertric), "deviceUid": uuid[0] + uuid[1] + uuid[2], "phoneNum": encode_phone(phone), "isChinatelecom": "0", "systemVersion": "15.4.0", "authentication": password}}}).json()
        
        if VERBOSE_LOG:
            printn(f"登录响应: {r}")  # 只在详细日志模式下打印完整响应
        
        if 'responseData' not in r or 'data' not in r['responseData'] or 'loginSuccessResult' not in r['responseData']['data']:
            printn(f"登录失败: 响应数据结构不正确", important=True)
            return False
        
        l = r['responseData']['data']['loginSuccessResult']
        
        if l:
            load_token[phone] = l
            with open(load_token_file, 'w') as f:
                json.dump(load_token, f)
            ticket = get_ticket(phone,l['userId'],l['token']) 
            return ticket
    except Exception as e:
        printn(f"登录过程中发生错误: {str(e)}", important=True)
    
    return False

def get_ticket(phone,userId,token):
    r = ss.post('https://appgologin.189.cn:9031/map/clientXML',data='<Request><HeaderInfos><Code>getSingle</Code><Timestamp>'+datetime.datetime.now().strftime("%Y%m%d%H%M%S")+'</Timestamp><BroadAccount></BroadAccount><BroadToken></BroadToken><ClientType>#9.6.1#channel50#iPhone 14 Pro Max#</ClientType><ShopId>20002</ShopId><Source>110003</Source><SourcePassword>Sid98s</SourcePassword><Token>'+token+'</Token><UserLoginName>'+phone+'</UserLoginName></HeaderInfos><Content><Attach>test</Attach><FieldData><TargetId>'+encrypt(userId)+'</TargetId><Url>4a6862274835b451</Url></FieldData></Content></Request>',headers={'user-agent': 'CtClient;10.4.1;Android;13;22081212C;NTQzNzgx!#!MTgwNTg1'})

    #printn(phone, '获取ticket', re.findall('<Reason>(.*?)</Reason>',r.text)[0])
    
    tk = re.findall('<Ticket>(.*?)</Ticket>',r.text)
    if len(tk) == 0:        
        return False
    
    return decrypt(tk[0])
        
def queryInfo(phone,s):
    global rs
    a = 1
    while a < 10:
        if rs:
            bd = js.call('main').split('=')
            ck[bd[0]] = bd[1]

        r = s.get('https://wapact.189.cn:9001/gateway/golden/api/queryInfo',cookies=ck).json()
        
        try:
            printn(f'{phone} 金豆余额 {r["biz"]["amountTotal"]}', important=True)
            amountTotal=  r["biz"]["amountTotal"]
        except:
            amountTotal = 0
        if amountTotal< 3000:
            if rs == 1:
                bd = js.call('main').split('=')
                ck [bd[0]] = bd[1]
                
            res = s.post('http://wapact.189.cn:9000/gateway/stand/detail/exchange',json={"activityId":jdaid},cookies=ck).text            
            
            if '$_ts=window' in res:
                first_request()
                rs = 1
            
            time.sleep(3)
        else:
            return r
        a += 1
        
    return r

# 预加载商品信息的函数
def preload_goods(phone, s):
    """预加载商品信息，提前准备好抢购数据"""
    global all_goods_cache
    
    # 检查是否已经有其他账号预加载过商品信息
    if all_goods_cache and len(all_goods_cache) > 0:
        # 使用第一个账号的缓存数据
        first_account = list(all_goods_cache.keys())[0]
        with goods_cache_lock:
            all_goods_cache[phone] = all_goods_cache[first_account]
            preloaded_accounts.add(phone)
        
        printn(f"{phone} 使用已缓存的商品信息，跳过请求")
        return all_goods_cache[phone]
    
    try:
        printn(f"{phone} 正在预加载商品信息...")
        if rs:
            bd = js.call('main').split('=')
            ck[bd[0]] = bd[1]
            
        # 获取商品列表
        queryBigDataAppGetOrInfo = s.get('https://waphub.189.cn/gateway/golden/goldGoods/getGoodsList?floorType=0&userType=1&page&1&order=3&tabOrder=',cookies=ck, timeout=30).json()
        
        # 创建一个列表来存储所有话费商品
        goods_list = []
        
        for i in queryBigDataAppGetOrInfo["biz"]["ExchangeGoodslist"]:
            if '话费' not in i["title"]:
                continue
                
            # 将所有话费商品添加到列表中
            goods_list.append({
                "title": i["title"],
                "id": i["id"],
                "face_value": parse_face_value(i["title"])
            })
            
            # 同时也按原来的逻辑分类到不同时间段
            if '0.5元' in i["title"] or '5元' in i["title"]:
                jp["10"][i["title"]] = i["id"]
                jp["9"][i["title"]] = i["id"]  # 兼容原有逻辑
            elif '1元' in i["title"] or '10元' in i["title"]:
                jp["14"][i["title"]] = i["id"]
                jp["13"][i["title"]] = i["id"]  # 兼容原有逻辑
            else:
                jp["12"][i["title"]] = i["id"]
        
        # 按面值从大到小排序
        goods_list.sort(key=lambda x: x["face_value"], reverse=True)
        
        # 使用线程锁保护共享资源
        with goods_cache_lock:
            all_goods_cache[phone] = goods_list
            preloaded_accounts.add(phone)
        
        printn(f"{phone} 预加载商品信息完成，共 {len(goods_list)} 个话费商品", important=True)
        return goods_list
    except Exception as e:
        printn(f"{phone} 预加载商品信息失败: {str(e)}", important=True)
        return []

# 优化的exchange函数，使用线程安全的方式更新记录
def exchange(phone, s, title, aid, uid, session_id):
    try:
        # 复制一份cookies，避免多线程冲突
        local_ck = ck.copy()
        if rs:
            bd = js.call('main').split('=')
            local_ck[bd[0]] = bd[1]
        
        # 添加会话ID，便于追踪请求
        headers = {
            "X-Session-ID": session_id,
            "Connection": "keep-alive",
            "User-Agent": "Mozilla/5.0 (Linux; Android 13; 22081212C Build/TKQ1.220829.002) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.97 Mobile Safari/537.36",
            "Referer": "https://wapact.189.cn:9001/JinDouMall/JinDouMall_independentDetails.html"
        }
        
        # 增加超时时间，从5秒改为15秒
        r = s.post('https://wapact.189.cn:9001/gateway/standExchange/detailNew/exchange',
                  json={"activityId": aid},
                  cookies=local_ck,
                  headers=headers,
                  timeout=15)  # 增加超时时间
        
        if '$_ts=window' in r.text:
            first_request(r.text)
            return
        
        r = r.json()        
        
        if r["code"] == 0:
            if r["biz"] != {} and r["biz"]["resultCode"] in errcode:
                printn(f'{str(datetime.datetime.now())[11:22]} {phone} {title} {errcode[r["biz"]["resultCode"]]} [会话:{session_id}]', important=True)
                
                if r["biz"]["resultCode"] in ["0", "412"]:
                    if r["biz"]["resultCode"] == "0":
                        # 兑换成功，发送通知
                        notify_title = f"电信金豆换话费 - {phone[-4:]}"
                        msg = f"{phone}:{title}兑换成功 [时间:{str(datetime.datetime.now())[11:22]}]"
                        
                        # 使用notify.py中的send函数发送通知
                        if 'send' in globals() and send is not None:
                            try:
                                send(notify_title, msg)
                                printn(f"通过notify.py发送通知成功", important=True)
                            except Exception as e:
                                printn(f"通过notify.py发送通知失败: {str(e)}", important=True)
                                # 如果notify.py发送失败，尝试使用微信推送
                                send_result = send(uid, msg)
                                # 尝试使用系统通知
                                send_system_notify(notify_title, msg)
                        else:
                            # 如果notify.py未加载成功，使用备用通知方式
                            send_result = send(uid, msg)
                            send_system_notify(notify_title, msg)
                        
                        printn(f"兑换成功通知已发送: {msg}", important=True)
                    
                    # 使用线程锁保护共享资源
                    with dhjl_lock:
                        if phone not in dhjl[yf][title]:
                            dhjl[yf][title] += "#"+phone
                            with open('电信金豆换话费.log', 'w') as f:
                                json.dump(dhjl, f, ensure_ascii=False)
        else:
            printn(f'{str(datetime.datetime.now())[11:22]} {phone} {title} 请求失败: {r.get("message", "未知错误")} [会话:{session_id}]')
                     
    except requests.exceptions.Timeout:
        # 专门处理超时异常
        printn(f'{str(datetime.datetime.now())[11:22]} {phone} {title} 请求超时，正在重试... [会话:{session_id}]')
        # 超时后自动重试一次
        try:
            local_ck = ck.copy()
            if rs:
                bd = js.call('main').split('=')
                local_ck[bd[0]] = bd[1]
            
            headers = {
                "X-Session-ID": f"{session_id}-retry",
                "Connection": "keep-alive",
                "User-Agent": "Mozilla/5.0 (Linux; Android 13; 22081212C Build/TKQ1.220829.002) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.97 Mobile Safari/537.36",
                "Referer": "https://wapact.189.cn:9001/JinDouMall/JinDouMall_independentDetails.html"
            }
            
            r = s.post('https://wapact.189.cn:9001/gateway/standExchange/detailNew/exchange',
                      json={"activityId": aid},
                      cookies=local_ck,
                      headers=headers,
                      timeout=20)  # 重试时使用更长的超时时间
            
            if '$_ts=window' in r.text:
                first_request(r.text)
                return
            
            r = r.json()
            
            if r["code"] == 0 and r["biz"] != {} and r["biz"]["resultCode"] in errcode:
                printn(f'{str(datetime.datetime.now())[11:22]} {phone} {title} 重试结果: {errcode[r["biz"]["resultCode"]]} [会话:{session_id}-retry]', important=True)

                if r["biz"]["resultCode"] in ["0", "412"]:
                    if r["biz"]["resultCode"] == "0":
                        # 重试兑换成功，发送通知
                        notify_title = f"电信金豆换话费 - {phone[-4:]}"
                        msg = f"{phone}:{title}兑换成功(重试) [时间:{str(datetime.datetime.now())[11:22]}]"
                        
                        # 使用notify.py中的send函数发送通知
                        if 'send' in globals() and send is not None:
                            try:
                                send(notify_title, msg)
                                printn(f"通过notify.py发送重试成功通知", important=True)
                            except Exception as e:
                                printn(f"通过notify.py发送重试通知失败: {str(e)}", important=True)
                                # 如果notify.py发送失败，尝试使用微信推送
                                send_result = send(uid, msg)
                                # 尝试使用系统通知
                                send_system_notify(notify_title, msg)
                        else:
                            # 如果notify.py未加载成功，使用备用通知方式
                            send_result = send(uid, msg)
                            send_system_notify(notify_title, msg)
                        
                        printn(f"重试兑换成功通知已发送: {msg}", important=True)
                    
                    with dhjl_lock:
                        if phone not in dhjl[yf][title]:
                            dhjl[yf][title] += "#"+phone
                            with open('电信金豆换话费.log', 'w') as f:
                                json.dump(dhjl, f, ensure_ascii=False)
        except Exception as retry_e:
            printn(f'{str(datetime.datetime.now())[11:22]} {phone} {title} 重试也失败: {str(retry_e)} [会话:{session_id}-retry]', important=True)
            
    except Exception as e:
        printn(f'{str(datetime.datetime.now())[11:22]} {phone} {title} 异常: {str(e)} [会话:{session_id}]', important=True)

# 优化的dh函数，使用线程池提高并发效率
def dh(phone, s, title, aid, wt, uid):
    # 测试模式下跳过等待
    if is_test_mode:
        printn(f"{str(datetime.datetime.now())[11:22]} {phone} {title} 测试模式：跳过等待")
    else:
        # 计算精确的等待时间
        current_time = get_accurate_time()
        wait_time = wt - current_time
        
        if wait_time > 0:
            # 如果等待时间大于5秒，先粗略等待到还剩5秒
            if wait_time > 5:
                rough_wait = wait_time - 5
                printn(f"{str(datetime.datetime.now())[11:22]} {phone} {title} 等待 {rough_wait:.2f} 秒后开始精确倒计时")
                time.sleep(rough_wait)
            
            # 精确倒计时最后5秒
            start_time = time.time()
            while time.time() < start_time + min(wait_time, 5):
                remaining = wt - get_accurate_time()
                if remaining <= 0:
                    break
                
                if remaining < 5:
                    printn(f"{str(datetime.datetime.now())[11:22]} {phone} {title} 倒计时: {int(remaining)}秒")
                    # 使用更短的睡眠时间提高精度
                    time.sleep(0.1)
    
    # 记录开始兑换的精确时间
    exchange_start_time = datetime.datetime.now()
    printn(f"{str(exchange_start_time)[11:23]} {phone} {title} 开始兑换")
    
    # 创建线程池，提高并发效率
    with concurrent.futures.ThreadPoolExecutor(max_workers=cfcs) as executor:
        futures = []
        for i in range(cfcs):
            # 为每个请求创建唯一的会话ID
            session_id = f"{phone[-4:]}-{i+1}-{int(time.time()*1000)%10000}"
            # 提交任务到线程池，使用更短的延迟
            future = executor.submit(exchange, phone, s, title, aid, uid, session_id)
            futures.append(future)
        
        # 等待所有任务完成，但最多等待8秒
        done, not_done = concurrent.futures.wait(futures, timeout=8)
        
        if not_done:
            printn(f"{str(datetime.datetime.now())[11:22]} {phone} {title} 有 {len(not_done)} 个请求超时未完成")
    
    # 记录结束时间并计算总耗时
    exchange_end_time = datetime.datetime.now()
    total_time = (exchange_end_time - exchange_start_time).total_seconds()
    printn(f"{str(exchange_end_time)[11:23]} {phone} {title} 抢购任务已全部提交，耗时 {total_time:.3f} 秒")

def lottery(s):
    for cishu in range(3):
        try:
            if rs:
                bd = js.call('main').split('=')
                ck [bd[0]] = bd[1]
            else:
                cookie = {} 
            r = s.post('https://wapact.189.cn:9001/gateway/golden/api/lottery',json={"activityId":"6384b49b1e44396da4f1e4a3"},cookies=ck)
        except:
            pass 
        time.sleep(3)

def aes_ecb_encrypt(plaintext, key):
    key = key.encode('utf-8')
    if len(key) not in [16, 24, 32]:
        raise ValueError("密钥长度必须为16/24/32字节")

    # 对明文进行PKCS7填充
    padded_data = pad(plaintext.encode('utf-8'), AES.block_size)
    # 创建AES ECB加密器
    cipher = AES.new(key, AES.MODE_ECB)

    # 加密并返回Base64编码结果
    ciphertext = cipher.encrypt(padded_data)
    return base64.b64encode(ciphertext).decode('utf-8')

# 解析话费面值，用于排序
def parse_face_value(title):
    # 提取数字部分
    match = re.search(r'(\d+(?:\.\d+)?)', title)
    if match:
        return float(match.group(1))
    return 0

# 优化的ks函数，支持测试模式和10点、14点抢购，并按面值大到小排序
def ks(phone, ticket, uid):
    global wt
    
    wxp[phone] = uid
    # 创建一个新的会话，避免多用户间的冲突
    s = requests.session()
    s.verify = False
    s.headers={"User-Agent":"Mozilla/5.0 (Linux; Android 13; 22081212C Build/TKQ1.220829.002) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.97 Mobile Safari/537.36","Referer":"https://wapact.189.cn:9001/JinDouMall/JinDouMall_independentDetails.html"}
    s.cookies.set_policy(BlockAll())
    s.mount('https://', DESAdapter())  
    s.timeout = 60  # 增加默认超时时间到60秒
    
    if rs:
        bd = js.call('main').split('=')
        ck [bd[0]] = bd[1]

    data = aes_ecb_encrypt(json.dumps({"ticket":ticket,"backUrl":"https%3A%2F%2Fwapact.189.cn%3A9001","platformCode":"P201010301","loginType":2}), 'telecom_wap_2018')

    login = ss.post('https://wapact.189.cn:9001/unified/user/login',data=data, headers={"Content-Type":"application/json;charset=UTF-8","Accept":"application/json, text/javascript, */*; q=0.01"}, cookies=ck).json()
    
    if login['code'] == 0:
        printn(phone+" 获取token成功")
        s.headers["Authorization"] = "Bearer " + login["biz"]["token"]   
        queryInfo(phone,s)
        
        if rs:
            bd = js.call('main').split('=')
            ck [bd[0]] = bd[1]
            
        # 获取商品列表
        queryBigDataAppGetOrInfo = s.get('https://waphub.189.cn/gateway/golden/goldGoods/getGoodsList?floorType=0&userType=1&page&1&order=3&tabOrder=',cookies=ck).json()
        print(queryBigDataAppGetOrInfo)
        # 创建一个列表来存储所有话费商品，以便后续排序
        all_goods = []
        
        for i in queryBigDataAppGetOrInfo["biz"]["ExchangeGoodslist"]:
            if '话费' not in i["title"]:
                continue
                
            # 将所有话费商品添加到列表中
            all_goods.append({
                "title": i["title"],
                "id": i["id"],
                "face_value": parse_face_value(i["title"])
            })
            
            # 同时也按原来的逻辑分类到不同时间段
            if '0.5元' in i["title"] or '5元' in i["title"]:
                jp["10"][i["title"]] = i["id"]
                jp["9"][i["title"]] = i["id"]  # 兼容原有逻辑
            elif '1元' in i["title"] or '10元' in i["title"]:
                jp["14"][i["title"]] = i["id"]
                jp["13"][i["title"]] = i["id"]  # 兼容原有逻辑
            else:
                jp["12"][i["title"]] = i["id"]
        
        # 按面值从大到小排序
        all_goods.sort(key=lambda x: x["face_value"], reverse=True)
        
        # 输出所有可兑换的话费商品
        printn("所有可兑换的话费商品（按面值从大到小排序）:")
        for idx, good in enumerate(all_goods):
            printn(f"{idx+1}. {good['title']} (ID: {good['id']})")

        h = datetime.datetime.now().hour
        if 11 > h > 1:
            h = 9
        elif 23 > h > 1:            
            h = 13
        else:
            h = 23
        
        # 命令行参数处理
        if len(sys.argv) == 2:
            if sys.argv[1] == '--test':
                global is_test_mode
                is_test_mode = True
                printn("测试模式已启用，将跳过等待时间直接执行")
            else:
                h = int(sys.argv[1])
                printn(f"使用命令行指定的时间: {h}:00")
        
        # 根据时间选择对应的商品
        if h == 10:
            d = jp["10"]
            printn(f"将在10:00进行抢购")
        elif h == 14:
            d = jp["14"]
            printn(f"将在14:00进行抢购")
        else:
            d = jp[str(h)]
        
        # 如果没有特定时间段的商品，使用所有话费商品
        if not d:
            printn(f"当前时间段 {h}:00 没有指定商品，将抢购所有话费商品")
            d = {good["title"]: good["id"] for good in all_goods}
        
        # 与服务器同步时间
        sync_time()
        
        wt = t(h) + kswt
        
        # 测试模式下立即执行
        if is_test_mode:
            wt = int(get_accurate_time()) - 5
            printn("测试模式：立即开始抢购")
        
        if jp["12"] != {}:
            d.update(jp["12"])
            if len(d) == len(jp["12"]):
                wt = 0
        
        # 按面值从大到小排序商品
        sorted_goods = []
        for title, aid in d.items():
            face_value = 0
            for good in all_goods:
                if good["title"] == title:
                    face_value = good["face_value"]
                    break
            sorted_goods.append({"title": title, "id": aid, "face_value": face_value})
        
        sorted_goods.sort(key=lambda x: x["face_value"], reverse=True)
        
        printn(f"将按以下顺序抢购商品（面值从大到小）:")
        for idx, good in enumerate(sorted_goods):
            printn(f"{idx+1}. {good['title']} (面值: {good['face_value']})")
        
        # 创建线程池处理多个商品的抢购
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(sorted_goods)) as executor:
            futures = []
            for good in sorted_goods:
                title = good["title"]
                aid = good["id"]
                
                if title not in dhjl[yf]:
                    dhjl[yf][title] = ""
                if phone in dhjl[yf][title]:
                    printn(f"{phone} {title} 已兑换")
                else:
                    printn(f"{phone} {title}")
                    if wt - get_accurate_time() > 20 * 60 and not is_test_mode:
                        print("等待时间超过20分钟")
                        return
                    
                    # 提交抢购任务到线程池
                    future = executor.submit(dh, phone, s, title, aid, wt, uid)
                    futures.append(future)
            
            # 等待所有抢购任务完成
            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    printn(f"抢购任务异常: {str(e)}")
    else:
        printn(f"{phone} 获取token {login['message']}")


def first_request(res=''):
    global js, fw
    url = 'https://wapact.189.cn:9001/gateway/stand/detail/exchange'
    if res == '':
        response = ss.get(url)
        res = response.text
    soup = BeautifulSoup(res, 'html.parser')
    scripts = soup.find_all('script')
    for script in scripts:
        if 'src' in str(script):
            rsurl = re.findall('src="([^"]+)"', str(script))[0]
            
        if '$_ts=window' in script.get_text():
            ts_code = script.get_text()
    
    urls = url.split('/')
    rsurl = urls[0] + '//' + urls[2] + rsurl
    #print(rsurl)    
    ts_code += ss.get(rsurl).text
    content_code = soup.find_all('meta')[1].get('content')
    
    # 修改此部分 - 添加安全的文件读取方式
    js_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "瑞数通杀.js")
    js_code_ym = ""
    
    # 尝试多种编码方式读取文件
    encodings = ['utf-8', 'utf-8-sig', 'gbk', 'gb18030', 'latin-1']
    for encoding in encodings:
        try:
            with open(js_file_path, 'r', encoding=encoding) as f:
                js_code_ym = f.read()
                print(f"成功使用 {encoding} 编码读取JS文件")
                break
        except UnicodeDecodeError:
            continue
        except Exception as e:
            print(f"读取JS文件时发生错误: {str(e)}")
            break
    
    if not js_code_ym:
        print("警告: 无法读取瑞数JS文件，脚本可能无法正常工作")
        return False
        
    # 安全替换和编译JS代码
    try:
        js_code = js_code_ym.replace('content_code', content_code).replace("'ts_code'", ts_code)
        js = execjs.compile(js_code)
    except Exception as e:
        print(f"编译JS代码时发生错误: {str(e)}")
        return False

    for cookie in ss.cookies:
        ck[cookie.name] = cookie.value
    return content_code, ts_code, ck

# 修改main函数，支持测试模式和服务器时间同步
def main():
    global wt, rs, appToken
    
    # 检查是否有测试模式参数
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        global is_test_mode
        is_test_mode = True
        printn("测试模式已启用，将跳过等待时间直接执行")
    
    # 与服务器同步时间
    sync_time()
    
    # 设置微信推送的appToken
    appToken = os.environ.get('appToken') if os.environ.get('appToken') else ""
    
    r = ss.get('https://wapact.189.cn:9001/gateway/stand/detailNew/exchange')
    if '$_ts=window' in r.text:
        rs = 1
        print("0.5元话费,每月限领1次,日上限200份,100金豆,\n1元话费,每月限领1次,日上限200份,200金豆\n5元话费,每月限领1次,日上限180份,1000金豆\n10元话费,每月限领1次,日上限140份,2000金豆")
        print("瑞数加密已开启")
        first_request()
    else:
        print("瑞数加密已关闭")
        rs = 0     
    if os.environ.get('jdhf')!= None:
        chinaTelecomAccount = os.environ.get('jdhf')
    else:
       chinaTelecomAccount = jdhf
    
    # 增加账号并发数量，从5改为10
    max_account_workers = 2  # 增加账号并发数
    printn(f"使用 {max_account_workers} 个线程并发处理账号登录")
    
    # 使用线程池处理多个账号登录
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_account_workers) as executor:
        futures = []
 #       chinaTelecomAccount = '19139864196#875050&19006448262#246810&19975226883#046319&13397715244#046319&15338981884#168668&19035042667#046319&18998597779#170821&18125250002#170821&19113016916#318090&13386358224#046319'
        for i in chinaTelecomAccount.split('&'):
            i = i.split('#')
            phone = i[0]
            password = i[1]
            uid = i[-1]
            
            # 提交登录任务到线程池
            future = executor.submit(process_account, phone, password, uid)
            futures.append(future)
        
        # 等待所有登录任务完成，添加进度显示
        completed = 0
        total = len(futures)
        for future in concurrent.futures.as_completed(futures):
            try:
                completed += 1
                printn(f"账号处理进度: {completed}/{total}")
                future.result()
            except Exception as e:
                printn(f"账号处理异常: {str(e)}")

# 处理单个账号的登录和抢购
def process_account(phone, password, uid):
    ticket = False 
    
    if phone in load_token:
        printn(f'{phone} 使用缓存登录')
        ticket = get_ticket(phone, load_token[phone]['userId'], load_token[phone]['token'])
    
    if ticket == False:
        printn(f'{phone} 使用密码登录')
        ticket = userLoginNormal(phone, password)
       
    if ticket:
        ks(phone, ticket, uid)
    else:
        printn(f'{phone} 登录失败')

jdhf = ""
cfcs = 4  # 并发数
max_retries = 2  # 最大重试次数
retry_timeout = 20  # 重试时的超时时间
jdaid = '60dd79533dc03d3c76bdde30'
ck = {}
appToken = ""  # 添加appToken全局变量
load_token_file = 'chinaTelecom_cache.json'
try:
    with open(load_token_file, 'r') as f:
        load_token = json.load(f)
except:
    load_token = {}

if __name__ == "__main__":
    main()

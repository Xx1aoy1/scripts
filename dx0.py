import os
import re
import sys
import ssl
import time
import json
import base64
import random
import certifi
import datetime
import requests
import binascii
import traceback
import subprocess
import asyncio
import aiohttp
from http import cookiejar
from threading import Event as ThreadingEvent, Lock as ThreadingLock
from asyncio import Event as AsyncioEvent
from Crypto.Cipher import DES3
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from Crypto.Util.Padding import pad, unpad
from concurrent.futures import ThreadPoolExecutor, wait

# --- 基础设置和辅助函数 ---
context = ssl.create_default_context()
context.set_ciphers('DEFAULT@SECLEVEL=1')
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE

class DESAdapter(requests.adapters.HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        kwargs['ssl_context'] = context
        return super().init_poolmanager(*args, **kwargs)

class BlockAll(cookiejar.CookiePolicy):
    return_ok = set_ok = domain_return_ok = path_return_ok = lambda self, *args, **kwargs: False
    netscape = True
    rfc2965 = hide_cookie2 = False

requests.packages.urllib3.disable_warnings()

def printn(m):
    current_time = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f'\n[{current_time}] {m}')

# --- 加密/解密/工具函数（保持不变）---
key = b'1234567`90koiuyhgtfrdews'
iv = 8 * b'\0'

public_key_b64 = '''-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDBkLT15ThVgz6/NOl6s8GNPofdWzWbCkWnkaAm7O2LjkM1H7dMvzkiqdxU02jamGRHLX/ZNMCXHnPcW/sDhiFCBN18qFvy8g6VYb9QtroI09e176s+ZCtiv7hbin2cCTj99iUpnEloZm19lwHyo69u5UMiPMpq0/XKBO8lYhN/gwIDAQAB
-----END PUBLIC KEY-----'''

public_key_data = '''-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC+ugG5A8cZ3FqUKDwM57GM4io6JGcStivT8UdGt67PEOihLZTw3P7371+N47PrmsCpnTRzbTgcupKtUv8ImZalYk65dU8rjC/ridwhw9ffW2LBwvkEnDkkKKRi2liWIItDftJVBiWOh17o6gfbPoNrWORcAdcbpk2L+udld5kZNwIDAQAB
-----END PUBLIC KEY-----'''

def encrypt_des3(text):
    cipher = DES3.new(key, DES3.MODE_CBC, iv)
    return cipher.encrypt(pad(text.encode(), DES3.block_size)).hex()

def decrypt_des3(text):
    cipher = DES3.new(key, DES3.MODE_CBC, iv)
    return unpad(cipher.decrypt(bytes.fromhex(text)), DES3.block_size).decode()

def b64_encrypt_rsa(plaintext):
    public_key = RSA.import_key(public_key_b64)
    cipher = PKCS1_v1_5.new(public_key)
    return base64.b64encode(cipher.encrypt(plaintext.encode())).decode()

def encrypt_para_rsa_new(p):
    k = RSA.import_key(public_key_data)
    c = PKCS1_v1_5.new(k)
    s = k.size_in_bytes() - 11
    d = p.encode() if isinstance(p, str) else json.dumps(p).encode()
    return binascii.hexlify(b''.join(c.encrypt(d[i:i+s]) for i in range(0, len(d), s))).decode()

def encode_phone(text):
    return ''.join([chr(ord(char) + 2) for char in text])

def get_ruishu_cookies():
    try:
        ruishu_script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Ruishu.py')
        if not os.path.exists(ruishu_script_path):
            print(f"❌ 错误: 未找到 {ruishu_script_path} 文件。")
            return None
        result = subprocess.run([sys.executable, ruishu_script_path], capture_output=True, text=True, encoding='utf-8', check=True)
        return json.loads(result.stdout.strip())
    except Exception as e:
        print(f"❌ 获取瑞数Cookie时发生错误: {e}")
        return None

# --- 推送与持久化函数 ---
def send_pushplus_notification(token, title, content):
    if not token:
        printn("ℹ️ 未配置PUSH_PLUS_TOKEN，跳过推送。")
        return
    url = "http://www.pushplus.plus/send"
    payload = {"token": token, "title": title, "content": content, "template": "markdown"}
    try:
        response = requests.post(url, json=payload)
        if response.json().get("code") == 200:
            printn("✅ PUSHPLUS 推送成功!")
        else:
            printn(f"❌ PUSHPLUS 推送失败: {response.json().get('msg')}")
    except Exception as e:
        printn(f"💥 推送时发生异常: {e}")

def load_claimed_accounts(filename):
    try:
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                return json.load(f)
    except (json.JSONDecodeError, IOError):
        pass
    return {}

def save_claimed_account(filename, phone, lock):
    with lock:
        claimed_data = load_claimed_accounts(filename)
        current_month = datetime.datetime.now().strftime("%Y-%m")
        claimed_data[phone] = current_month
        with open(filename, 'w') as f:
            json.dump(claimed_data, f, indent=4)

# =================== 新登录方法 login_v2 (Android) ===================
def login_v2(phone: str, password: str, android_id: str, session: requests.Session):
    """
    使用 Android 设备标识登录，返回包含 uid(token) 的用户信息字典
    """
    m_phone = phone[:3] + '****' + phone[-4:] if len(phone) >= 7 else phone
    printn(f"[登录v2] {m_phone} 开始登录 (AndroidId={android_id[:6]}...)")

    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    # 随机生成设备UUID段
    alphabet = 'abcdef0123456789'
    uuid = [
        ''.join(random.sample(alphabet, 8)),
        ''.join(random.sample(alphabet, 4)),
        '4' + ''.join(random.sample(alphabet, 3)),
        ''.join(random.sample(alphabet, 4)),
        ''.join(random.sample(alphabet, 12))
    ]
    device_part = uuid[0] + uuid[1] + uuid[2]  # 用于deviceUid

    loginAuthCipherAsymmertric = f"Xiaomi 20 8.0.0.{android_id[:12]}{phone}{timestamp}{password}0$$$0."
    body = {
        "headerInfos": {
            "code": "userLoginNormal",
            "timestamp": timestamp,
            "broadAccount": "",
            "broadToken": "",
            "clientType": "#11.0.0#channel8#Xiaomi 20#",
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
                "loginAuthCipherAsymmertric": b64_encrypt_rsa(loginAuthCipherAsymmertric),
                "deviceUid": "",
                "phoneNum": encode_phone(phone),
                "isChinatelecom": "",
                "systemVersion": "8.0.0",
                "androidId": encode_phone(android_id),
                "loginAuthCipher": "",
                "authentication": encode_phone(password)
            }
        }
    }

    try:
        resp = session.post(
            'https://appgologin.189.cn:9031/login/client/userLoginNormal',
            json=body,
            timeout=30
        )
        if resp.status_code != 200:
            printn(f"[登录v2失败] {m_phone} HTTP状态码 {resp.status_code}")
            return None

        res = resp.json()
        login_data = res.get('responseData', {}).get('data', {}).get('loginSuccessResult')
        if not login_data:
            err_msg = res.get('responseData', {}).get('data', {}).get('resultMsg') or '无loginSuccessResult'
            printn(f"[登录v2失败] {m_phone}: {err_msg}")
            return None

        # 第二步：获取Ticket
        xml = f'''<Request>
            <HeaderInfos>
                <Code>getSingle</Code>
                <Timestamp>{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}</Timestamp>
                <BroadAccount></BroadAccount>
                <BroadToken></BroadToken>
                <ClientType>#9.6.1#channel50#iPhone 14 Pro Max#</ClientType>
                <ShopId>20002</ShopId>
                <Source>110003</Source>
                <SourcePassword>Sid98s</SourcePassword>
                <Token>{login_data["token"]}</Token>
                <UserLoginName>{phone}</UserLoginName>
            </HeaderInfos>
            <Content>
                <Attach>test</Attach>
                <FieldData>
                    <TargetId>{encrypt_des3(login_data["userId"])}</TargetId>
                    <Url>4a6862274835b451</Url>
                </FieldData>
            </Content>
        </Request>'''
        xml_resp = session.post(
            'https://appgologin.189.cn:9031/map/clientXML',
            data=xml,
            headers={'Content-Type': 'application/xml'},
            timeout=30
        )
        if xml_resp.status_code != 200:
            printn(f"[获取Ticket失败] {m_phone} 状态码 {xml_resp.status_code}")
            return None

        xml_text = xml_resp.text
        if '过期' in xml_text or '校验错误' in xml_text:
            printn(f"[获取Ticket失败] {m_phone}: {xml_text[:50]}")
            return None

        if '<Ticket>' not in xml_text:
            printn(f"[Ticket异常] {m_phone} 响应无Ticket标签")
            return None

        try:
            ticket = xml_text.split('<Ticket>')[1].split('</Ticket>')[0]
            uid = decrypt_des3(ticket)
        except Exception as e:
            printn(f"[解析Ticket失败] {m_phone}: {e}")
            return None

        # 第三步：统一登录获取Bearer（可选，后续可能用到）
        # 注意：原抢购逻辑不依赖Bearer，仅需ticket，但这里保留获取
        auth_body = json.dumps({"ticket": uid, "backUrl": "https%3A%2F%2Fwapact.189.cn%3A9001", "platformCode": "P201010301", "loginType": 2})
        # 使用AES加密（原脚本未定义，但此处不需要，因为原抢购流程使用ticket即可）
        # 原脚本中的getSign使用ticket，所以无需Bearer，注释掉统一登录步骤

        user_info = {
            **login_data,
            'uid': uid,
            'phoneNbr': phone,
            'ticket': uid   # 兼容后续
        }
        printn(f"[登录v2成功] {m_phone} 获取ticket成功")
        return user_info
    except Exception as e:
        printn(f"[登录v2异常] {m_phone}: {e}")
        traceback.print_exc()
        return None

# =================== 原抢购相关函数（仅替换登录调用） ===================

def getSign(ticket, session, rs_cookies):
    try:
        response = session.get(
            f'https://wappark.189.cn/jt-sign/ssoHomLogin?ticket={ticket}',
            cookies=rs_cookies,
            headers={
                'User-Agent': "Mozilla/5.0 (Linux; Android 13; 22081212C Build/TKQ1.220829.002) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.97 Mobile Safari/537.36"
            }
        )
        try:
            json_data = response.json()
        except (json.JSONDecodeError, ValueError):
            json_data = {}
        if json_data.get('resoultCode') == '0':
            return json_data.get('sign'), json_data.get('accId')
        else:
            print(f"❌ 获取sign失败: {json_data}")
            return None, None
    except Exception as e:
        print(f"❌ getSign 异常: {e}")
        return None, None

def getLevelRightsList(phone, accId, session):
    try:
        value = {"type": "hg_qd_djqydh", "accId": accId, "shopId": "20001"}
        paraV = encrypt_para_rsa_new(value)
        response = session.post(
            'https://wappark.189.cn/jt-sign/paradise/queryLevelRightInfo',
            json={"para": paraV}
        )
        try:
            data = response.json()
        except (json.JSONDecodeError, ValueError):
            data = {}
        if data.get('code') == 401:
            print(f"❌ {phone} 获取权益列表失败: {data}")
            return None
        key_name = f"V{data['currentLevel']}"
        ids = [item['activityId'] for item in data.get(key_name, []) if '话费' in item.get('title', '')]
        return ids
    except Exception as e:
        print(f"❌ getLevelRightsList 异常: {e}")
        return None

# === 异步抢购函数（不变） ===
async def async_staggered_burst_worker(
    session, phone, rightsId, accId, sign, rs_cookies,
    global_stop_event, local_stop_event,
    task_index, base_target_time,
    result_log, result_lock, file_lock,
    num_accounts_to_run
):
    fire_time = base_target_time + datetime.timedelta(milliseconds=(interval * task_index))
    wait_seconds = (fire_time - datetime.datetime.now()).total_seconds()
    if wait_seconds > 0 and not debug:
        await asyncio.sleep(wait_seconds)

    if local_stop_event.is_set() or global_stop_event.is_set():
        return

    try:
        value = {"id": rightsId, "accId": accId, "showType": "9003", "showEffect": "8", "czValue": "0"}
        paraV = encrypt_para_rsa_new(value)
        headers = {
            "sign": sign,
            "Referer": "https://wappark.189.cn/resources/dist/signInActivity.html",
            "User-Agent": "Mozilla/5.0 (Linux; Android 13; 22081212C Build/TKQ1.220829.002) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.97 Mobile Safari/537.36"
        }

        url = "https://wappark.189.cn/jt-sign/paradise/receiverRights"

        async with session.post(url, json={"para": paraV}, cookies=rs_cookies, headers=headers) as response:
            request_time = datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3]

            text = ""
            try:
                text = await response.text(encoding='utf-8', errors='replace')
            except asyncio.TimeoutError:
                printn(f"⏰【{phone}】@{request_time} [任务{task_index}] 响应读取超时")
                return
            except Exception as e:
                text = f"[响应读取异常: {type(e).__name__} - {str(e)}]"

            res_json = {}
            res_text = ""
            try:
                clean_text = text.strip()
                if clean_text.startswith('\ufeff'):
                    clean_text = clean_text[1:]
                if clean_text:
                    res_json = json.loads(clean_text)
                    res_text = json.dumps(res_json, ensure_ascii=False)
                else:
                    res_text = "[空响应]"
            except (json.JSONDecodeError, ValueError, TypeError):
                res_text = f"非JSON响应: {text[:100]}"

            if "已领完" in res_text or "活动已结束" in res_text:
                printn(f"💨【{phone}】@{request_time} [任务{task_index}] 已售罄! 停止该账号后续请求。")
                if not local_stop_event.is_set():
                    local_stop_event.set()
                with result_lock:
                    if phone not in result_log or result_log.get(phone, {}).get('status') != 'SUCCESS':
                        result_log[phone] = {'status': 'SOLD_OUT', 'message': '已售罄'}
                    finished_count = len([r for r in result_log.values() if r.get('status') in ('SUCCESS', 'SOLD_OUT')])
                    has_success = any(res.get('status') == 'SUCCESS' for res in result_log.values())
                    if not has_success and finished_count == num_accounts_to_run and not global_stop_event.is_set():
                        global_stop_event.set()
                        printn(f"🛑【全局共识】所有账号均确认售罄或失败，触发全局停止信号！")

            elif "成功" in res_text or "已领取过该权益" in res_text:
                printn(f"🎉【{phone}】@{request_time} [任务{task_index}] 成功或已领取!")
                if not local_stop_event.is_set():
                    local_stop_event.set()
                    printn(f"🛑【{phone}】个人停止信号已发出 (原因: 成功)。")
                with result_lock:
                    result_log[phone] = {'status': 'SUCCESS', 'message': res_json.get('resoultMsg', '成功/已领取')}
                loop = asyncio.get_running_loop()
                await loop.run_in_executor(None, save_claimed_account, claimed_log_file, phone, file_lock)

            elif "当前抢购人数过多" in res_text:
                printn(f"👥【{phone}】@{request_time} [任务{task_index}] 人数过多，继续尝试...")

            else:
                printn(f"💬【{phone}】@{request_time} [任务{task_index}] 响应: {res_text}")

    except asyncio.CancelledError:
        pass
    except asyncio.TimeoutError:
        request_time = datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3]
        printn(f"⏰【{phone}】@{request_time} [任务{task_index}] 请求超时 (连接或响应)")
    except Exception as e:
        request_time = datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3]
        printn(f"🚨【{phone}】@{request_time} [任务{task_index}] 未预期异常: {e.__class__.__name__} - {str(e)}")

def run_attack_campaign(phone, ticket, ss, global_stop_event, enable_ruishu, result_log, result_lock, file_lock, num_accounts_to_run):
    try:
        if global_stop_event.is_set():
            return
        printn(f"⚙️【{phone}】开始准备凭证 (同步模式)...")
        rs_cookies = get_ruishu_cookies() if enable_ruishu else {}
        if enable_ruishu and not rs_cookies:
            raise Exception("瑞数已启用但获取Cookie失败")

        sign, accId = getSign(ticket, ss, rs_cookies)
        if not sign:
            raise Exception("获取Sign失败")

        ss.headers.update({
            "sign": sign,
            "Referer": "https://wappark.189.cn/resources/dist/signInActivity.html"
        })
        rightsIds = getLevelRightsList(phone, accId, ss)
        if not rightsIds:
            raise Exception("未能获取到权益ID")

        rightsId = rightsIds[0]
        printn(f"✅【{phone}】凭证准备就绪，切换至异步并发抢购...")

        asyncio.run(run_async_bursts(phone, rightsId, accId, sign, rs_cookies, global_stop_event, result_log, result_lock, file_lock, num_accounts_to_run))

        with result_lock:
            if phone not in result_log:
                result_log[phone] = {'status': 'UNKNOWN', 'message': '抢购结束但未记录明确状态'}
        printn(f"🏁【{phone}】抢购任务已结束。")
    except Exception as e:
        printn(f"💥【{phone}】准备或执行阶段出现严重异常: {e}")
        with result_lock:
            result_log[phone] = {'status': 'FAIL', 'message': str(e)}

async def run_async_bursts(phone, rightsId, accId, sign, rs_cookies, global_stop_event, result_log, result_lock, file_lock, num_accounts_to_run):
    now = datetime.datetime.now()
    target_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if now >= target_time:
        target_time += datetime.timedelta(days=1)
    base_target_time = target_time + datetime.timedelta(milliseconds=inadvance)

    local_stop_event = AsyncioEvent()
    connector = aiohttp.TCPConnector(ssl=ssl.create_default_context(cafile=certifi.where()))
    timeout = aiohttp.ClientTimeout(total=15, connect=10)

    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as async_session:
        tasks = [
            async_staggered_burst_worker(
                async_session, phone, rightsId, accId, sign, rs_cookies,
                global_stop_event, local_stop_event, i, base_target_time,
                result_log, result_lock, file_lock, num_accounts_to_run
            )
            for i in range(count_per_account)
        ]
        await asyncio.gather(*tasks, return_exceptions=True)

# =================== 修改后的账号处理函数 ===================
def process_account(account_str, global_stop_event, enable_ruishu, result_log, result_lock, file_lock, num_accounts_to_run):
    """
    账号格式：手机号@密码@AndroidID
    """
    parts = account_str.split('@')
    if len(parts) < 3:
        printn(f"⚠️ 账号格式错误：缺少AndroidID，应为 '手机号@密码@AndroidID'，实际为 '{account_str}'，跳过该账号。")
        # 记录失败状态
        with result_lock:
            phone = parts[0] if parts else 'unknown'
            result_log[phone] = {'status': 'LOGIN_FAIL', 'message': '缺少AndroidID'}
        return

    phone, password, android_id = parts[0], parts[1], parts[2]
    if not android_id.strip():
        printn(f"⚠️ 账号 {phone} 的AndroidID为空，请填写有效的AndroidID（从小程序“云链小栈”获取），跳过该账号。")
        with result_lock:
            result_log[phone] = {'status': 'LOGIN_FAIL', 'message': 'AndroidID为空'}
        return

    if not debug:
        delay = random.uniform(0.1, 2.0)
        time.sleep(delay)
        printn(f'👤【{phone}】(延迟{delay:.2f}s后) 开始登录...')
    else:
        printn(f'👤【{phone}】开始登录...')

    # 创建会话
    ss = requests.session()
    ss.headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 13; 22081212C Build/TKQ1.220829.002) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.97 Mobile Safari/537.36"
    }
    ss.mount('https://', DESAdapter())
    ss.cookies.set_policy(BlockAll())
    ss.timeout = 30

    # 使用 login_v2 登录
    user_info = login_v2(phone, password, android_id, ss)
    if user_info:
        ticket = user_info['uid']   # 即 ticket
        run_attack_campaign(phone, ticket, ss, global_stop_event, enable_ruishu, result_log, result_lock, file_lock, num_accounts_to_run)
    else:
        printn(f'❌【{phone}】登录失败')
        with result_lock:
            result_log[phone] = {'status': 'LOGIN_FAIL', 'message': '登录失败'}

# =================== 主函数 ===================
def main():
    start_time = datetime.datetime.now()
    PHONES = os.environ.get('dxqy')
    push_plus_token = os.environ.get('PUSH_PLUS_TOKEN')
    if not PHONES:
        printn("ℹ️ 未检测到环境变量 `dxqy`，将使用脚本内嵌的账号信息。")
        PHONES = "你的手机号@你的服务密码@你的AndroidID"  # 务必填写完整格式，AndroidID请从小程序“云链小栈”中获取
    all_accounts = [p.strip() for p in PHONES.split('&') if p.strip() and '@' in p and "你的手机号" not in p]
    if not all_accounts:
        printn("❌ 请在环境变量或脚本中设置正确的账号信息（格式：手机号@密码@AndroidID，AndroidID请从小程序“云链小栈”中获取）。")
        return

    # 检查每个账号是否有AndroidID
    valid_accounts = []
    for acc in all_accounts:
        parts = acc.split('@')
        if len(parts) < 3 or not parts[2].strip():
            printn(f"⚠️ 账号 '{acc}' 缺少AndroidID，将被跳过。请补充完整格式：手机号@密码@AndroidID，缺少AndroidID，格式应为 手机号@密码@AndroidID，AndroidID请从小程序“云链小栈”中获取。跳过该账号")
            continue
        valid_accounts.append(acc)

    if not valid_accounts:
        printn("❌ 没有有效的账号（均缺少AndroidID），缺少AndroidID，格式应为 手机号@密码@AndroidID，AndroidID请从小程序“云链小栈”中获取。跳过该账号。")
        return

    # 加载已领取记录
    claimed_data = load_claimed_accounts(claimed_log_file)
    current_month = datetime.datetime.now().strftime("%Y-%m")
    accounts_to_run = []
    skipped_accounts = []
    for acc in valid_accounts:
        phone = acc.split('@')[0]
        if claimed_data.get(phone) == current_month:
            skipped_accounts.append(f"✅ {phone[:3]}***{phone[-4:]}: 本月已领取")
        else:
            accounts_to_run.append(acc)

    printn("="*20 + " 账号过滤 " + "="*20)
    print(f"总有效账号数: {len(valid_accounts)}, 本次运行: {len(accounts_to_run)}, 本月已领取跳过: {len(skipped_accounts)}")
    for s in skipped_accounts:
        print(s)
    printn("="*52)
    if not accounts_to_run:
        printn("🏁 所有账号本月均已领取，任务结束!")
        return

    global_stop_event = ThreadingEvent()
    result_log = {}
    result_lock = ThreadingLock()
    file_lock = ThreadingLock()
    num_accounts_to_run = len(accounts_to_run)

    now = datetime.datetime.now()
    prepare_time = now.replace(hour=23, minute=59, second=0, microsecond=0)
    if now >= prepare_time:
        prepare_time += datetime.timedelta(days=1)
    wait_seconds = (prepare_time - now).total_seconds()
    if wait_seconds > 0 and not debug:
        printn(f"⏳ 主程序等待 {wait_seconds:.0f} 秒，将在 {prepare_time.strftime('%H:%M:%S')} 开始并行登录...")
        time.sleep(wait_seconds)
    elif debug:
        printn(f"🐛 [DEBUG模式] 跳过主程序等待，立即开始登录...")

    with ThreadPoolExecutor(max_workers=len(accounts_to_run)) as executor:
        futures = [
            executor.submit(
                process_account, acc, global_stop_event, ENABLE_RUISHU,
                result_log, result_lock, file_lock, num_accounts_to_run
            )
            for acc in accounts_to_run
        ]
        wait(futures)

    end_time = datetime.datetime.now()
    duration = (end_time - start_time).total_seconds()

    summary_title = f"电信权益抢购总结 ({end_time.strftime('%Y-%m-%d %H:%M')})"
    success_accounts = skipped_accounts.copy()
    fail_accounts = []

    final_state = '全部完成'
    if global_stop_event.is_set():
        final_state = '已售罄 (全局共识)'

    for acc in accounts_to_run:
        phone = acc.split('@')[0]
        res = result_log.get(phone)
        if res:
            if res['status'] == 'SUCCESS':
                success_accounts.append(f"🎉 {phone[:3]}***{phone[-4:]}: {res['message']}")
            else:
                fail_accounts.append(f"❌ {phone[:3]}***{phone[-4:]}: {res['message']}")
        else:
            fail_accounts.append(f"ℹ️ {phone[:3]}***{phone[-4:]}: 未执行或无明确结果")

    summary_content = (f"### 任务报告\n- **总耗时**: {duration:.2f} 秒\n- **最终状态**: {final_state}\n---\n### 成功/已领取列表 ({len(success_accounts)}/{len(valid_accounts)})\n")
    summary_content += "\n".join(success_accounts) if success_accounts else "无"
    summary_content += f"\n\n### 失败/未成功列表 ({len(fail_accounts)}/{len(valid_accounts)})\n"
    summary_content += "\n".join(fail_accounts) if fail_accounts else "无"

    printn("="*22 + " 抢购总结 " + "="*22)
    print(summary_content)
    printn("="*52)
    send_pushplus_notification(push_plus_token, summary_title, summary_content)
    printn("🏁 所有账号的任务均已结束!")

if __name__ == '__main__':
    inadvance = -100          # 提前100毫秒（可调）
    count_per_account = 2     # 每账号抢购次数
    interval = 1            # 请求间隔（毫秒）
    hour = 0
    minute = 0
    debug = False             # 测试时改为True
    ENABLE_RUISHU = False
    claimed_log_file = "claimed_accounts.json"

    print("="*52)
    print("  电信等级会员权益兑换（终极加固版）")
    print("="*52)
    print(f"🕒 目标时间: {hour:02d}:{minute:02d} | 🎯 每号抢购数: {count_per_account} | 💥 抢购间隔: {interval}ms")
    print(f"⚡️ 首发提前: {-inadvance}ms")
    print(f"🐞 Debug模式: {'开启' if debug else '关闭'}")
    print(f"🤖 瑞数Cookie: {'启用' if ENABLE_RUISHU else '禁用'}")
    print(f"📓 领取记录文件: {claimed_log_file}")
    print("="*52)
    main()

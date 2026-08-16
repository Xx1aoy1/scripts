#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
移动云盘自动签到 v5.0.7

包含以下功能:
1. 每日自动签到 (签到/抽奖/摇一摇/新版云朵领取)
2. 多账号并发支持 (环境变量 & 分隔)
3. 云朵中心新版任务自动处理 (上传/分享/AI相机/月任务补传等)
4. 临时文件智能清理与详细日志推送

更新说明:

### 20260614
v5.0.7:
- 新增红包派对任务链：签到、浏览、云机使用、安装应用、趣味答题、余额奖励日志。
- 30GB定向流量保持手动跳过，补充答题答案与未知题重取。

### 20260531
v5.0.6:
- 修复云朵中心任务列表（重构为 POST JSON 模式）。

### 20260503
v5.0.5:
- 修复分享文件任务流程。
- 新增去体验AI相机任务。
- 新增五一福利任务。

### 20260425
v5.0.4:
- 整合 Authorization 自动刷新。
- 新增账号级 deviceId/token 缓存。
- 优化 JWT 失败重试、设备信息与启动提示。

配置说明:
变量名: ydyp
赋值方式:
1. 抓包 authTokenRefresh.do 请求头 Authorization 值。
2. 填入青龙环境变量，格式：Authorization值#手机号 (多账号用 & 分隔)。

变量名: ydyp_device_id 或 YDYP_DEVICE_ID
用途: 签到和领取云朵优先使用的 deviceId

抓包方式:
1. 打开移动云盘 APP 进入云朵中心。
2. 搜索 startSignIn、receiveV2 或 infoV3 请求。
3. 复制请求头 deviceId 值，或复制 Cookie 中 .thumbcache_* 的原值。
4. 填入 ydyp_device_id；脚本会自动兼容请求头值和 .thumbcache_* 原值。

deviceId 配置说明:
1. 已填写 ydyp_device_id 或 YDYP_DEVICE_ID 时，优先使用环境变量。
2. 未填写环境变量时，脚本会按手机号读取或创建 ydyp_device_ids.json 账号记录。
3. 缓存中已填写 deviceId 时优先复用；缓存为空时自动生成并保存 deviceId。

⚠️ 依赖安装:
pip3 install requests pycryptodome

定时规则建议 (Cron):
0 0 8,16,20 * * * (每日早中晚执行)

Author: YaoHuo8648
Email: zheyizzf@188.com
Update: 2026.06.14
"""

import base64
import hashlib
import json
import os
import random
import re
import time
import uuid
from datetime import datetime, timezone, timedelta
from os import path
from pathlib import Path
from urllib.parse import unquote

import requests

try:
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import pad
except ImportError:
    AES = None
    pad = None

SCRIPT_VERSION = '5.0.7'

TOKEN_STORAGE_FILENAME = 'ydyp_token_storage.json'
DEVICE_ID_STORAGE_FILENAME = 'ydyp_device_ids.json'  # 简易 deviceId 存储：手机号 -> deviceId

# ⭐ 统一设备信息：iPhone 16 Pro + iOS 18_7 + 版本 12.5.4（抓包真实值）
ua = ''
market_ua = ''
cloud_file_dummy_content = b'0'
cloud_file_dummy_hash = hashlib.sha256(cloud_file_dummy_content).hexdigest()
TOKEN_VALID_TIME = 21600000
TOKEN_REFRESH_ADVANCE = 24 * 60 * 60 * 1000
TOKEN_REFRESH_COOLDOWN = 864000
REFRESH_TOKEN_AES_KEY = 'c7lXOigXahPnTViq'
AI_TOOL_ACCOUNT_AES_KEY = 'xuL97!x7GGxG%8V4'
AI_TOOL_ACCOUNT_AES_IV = '5OuCxk4XNu0NA*%x'
TOKEN_EXPIRE_SECONDS_FALLBACK = 2592000
RED_PACKET_SOURCE_ID = '001216'
RED_PACKET_VERSION = 'SYS_CONFIG_Y'
RED_PACKET_BASE_URL = 'https://cpactiv.buy.139.com/cloudphone-market'
RED_PACKET_PAGE_URL = 'https://cpactiv.buy.139.com/#/redEnvelopeParty/home?channelSrc=red-cmccapp'
RED_PACKET_APP_ID = '12345681'
RED_PACKET_SIGN_KEY = 'e10adc3949ba59abbe56e057f20f883e'
RED_PACKET_CHANNEL_SRC = 'red-cmccapp'
RED_PACKET_BROWSE_TASKS = {'NOVICE_2', 'NOVICE_3', 'MONTHLY_1'}
RED_PACKET_DIRECT_TASKS = {'MONTHLY_4', 'MONTHLY_5'}
RED_PACKET_KNOWN_ANSWERS = {
    '如何查看并更新移动云手机客户端最新版本？': '进入“我的”-点击“关于云手机”-点击“检查新版本”',
    '移动云手机可领取定向流量，每月赠送的定向流量是（  ）。': '30GB',
    '移动云手机端内订购的专业版分辨率已升级到1080P，该说法是否正确？': '正确',
    '移动云手机支持视频录制，该说法是否正确？': '正确',
    '云手机支持通过手机、平板、电脑等多种终端设备登录使用，该说法是否正确？': '正确',
    '使用中国移动号码登录移动云手机，是否支持手机号一键登录？': '支持',
    '只有中国移动运营商号码能使用移动云手机？': '不正确',
    '移动云手机是否需要充电使用？': '不需要',
    '移动云手机支持截图，该说法是否正确？': '正确',
    '移动云手机AI灵犀助手已接入DeepSeek，是否正确？': '正确',
    '移动云手机内支持画面清晰度切换，该说法是否正确？': '正确',
    '移动云手机支持连接蓝牙使用吗？': '不支持',
    '在云手机内安装游戏应用是否占本地手机存储空间？': '否，不占本地空间',
    '如何更换云机内的桌面主题或壁纸？': '云机内-【设置】-壁纸/个性主题',
    '如何将云手机里的应用添加至本地手机桌面？': '云手机桌面-长按应用-发送图标到本地',
}
RED_PACKET_MANUAL_TASKS = {
    'NOVICE_1': '需跳转领取定向流量',
}

err_accounts = ''  # 异常账号
all_logs = ''      # 所有用户的详细运行日志 (原 err_message)
user_amount = ''   # 用户云朵·数量
GLOBAL_DEBUG = False


def current_millis():
    return int(time.time() * 1000)


def normalize_authorization(token):
    token = (token or '').strip()
    if token and not token.startswith('Basic '):
        return f'Basic {token}'
    return token


def random_string(length=16):
    chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    return ''.join(random.choice(chars) for _ in range(length))


def generate_uuid():
    return ''.join([
        random_string(8), '-',
        random_string(4), '-4',
        random_string(3), '-',
        random.choice('89ab'), random_string(3), '-',
        random_string(12)
    ])


# 真实抓包 deviceId（base64 格式，iOS iPhone 16 Pro + iOS 18_7）
REAL_DEVICE_ID = ''

def generate_device_id():
    if REAL_DEVICE_ID:
        return REAL_DEVICE_ID
    device_info = {
        'deviceId': uuid.uuid4().hex.upper(),
        'brand': 'Apple',
        'model': 'iPhone 16 Pro',
        'system': 'iOS 18.7',
        'timestamp': current_millis()
    }
    raw = json.dumps(device_info, ensure_ascii=False, separators=(',', ':'))
    return base64.b64encode(raw.encode('utf-8')).decode('utf-8')


def get_env_device_id():
    return (os.getenv('ydyp_device_id') or os.getenv('YDYP_DEVICE_ID') or '').strip()


def build_x_device_info(device_id, net_type='wifi', terminal_type='8',
                        version='12.5.4', brand='Apple', model='iPhone 16 Pro',
                        system='iOS 18.7'):
    """构造 x-DeviceInfo 头，与 UA 保持一致"""
    return f"{net_type}||{terminal_type}|{version}|{brand}|{model}|{device_id}||{system.lower()}|||||"


def aes_encrypt(data, key):
    if AES is None or pad is None:
        raise ImportError('未安装 pycryptodome，无法执行 Token 自动刷新')
    key_bytes = key.encode('utf-8')
    if not isinstance(data, str):
        data = json.dumps(data, ensure_ascii = False, separators = (',', ':'))
    cipher = AES.new(key_bytes, AES.MODE_ECB)
    encrypted = cipher.encrypt(pad(data.encode('utf-8'), AES.block_size))
    return base64.b64encode(encrypted).decode('utf-8')


def extract_raw_token(token, account):
    token = normalize_authorization(token)
    if token.startswith('Basic '):
        token = token[6:]
    try:
        decoded = base64.b64decode(token).decode('utf-8')
        parts = decoded.split(':')
        if len(parts) >= 3:
            return parts[2]
    except Exception:
        pass
    return token


def build_authorization(account, raw_token):
    return f"Basic {base64.b64encode(f'mobile:{account}:{raw_token}'.encode()).decode()}"


def parse_expire_time_to_millis(expire_time):
    try:
        expire_seconds = int(float(expire_time))
    except (TypeError, ValueError):
        expire_seconds = TOKEN_EXPIRE_SECONDS_FALLBACK
    if expire_seconds <= 0:
        expire_seconds = TOKEN_EXPIRE_SECONDS_FALLBACK
    return current_millis() + expire_seconds * 1000


def get_storage_base_dir():
    """获取缓存目录，优先保存到当前运行脚本所在目录（适配青龙脚本管理目录）"""
    custom_storage_dir = (os.environ.get('ydyp_storage_dir') or os.environ.get('YDYP_STORAGE_DIR') or '').strip()
    if custom_storage_dir:
        base_dir = Path(custom_storage_dir)
    else:
        # 在青龙中，__file__ 即当前实际运行脚本所在的仓库/目录；
        # 优先保存在这里，便于跟随当前脚本一起管理与备份。
        base_dir = Path(path.abspath(path.dirname(__file__)))
    base_dir.mkdir(parents = True, exist_ok = True)
    return base_dir


def get_storage_file_path(filename):
    return get_storage_base_dir() / filename


def get_token_storage_path():
    """获取 token 存储文件路径，默认保存到当前运行脚本目录"""
    return get_storage_file_path(TOKEN_STORAGE_FILENAME)


def load_token_storage():
    storage_path = get_token_storage_path()
    if storage_path.is_dir():
        storage_path = storage_path / TOKEN_STORAGE_FILENAME
    if not storage_path.exists():
        return {'accounts': {}}
    try:
        with open(storage_path, 'r', encoding = 'utf-8') as file:
            data = json.load(file)
            if isinstance(data, dict):
                data.setdefault('accounts', {})
                return data
    except Exception as e:
        print(f'加载Token缓存失败: {e}')
        pass
    return {'accounts': {}}


def save_token_storage(data):
    storage_path = get_token_storage_path()
    if storage_path.is_dir():
        storage_path = storage_path / TOKEN_STORAGE_FILENAME
    data['updatedAt'] = current_millis()
    try:
        storage_path.parent.mkdir(parents = True, exist_ok = True)
        with open(storage_path, 'w', encoding = 'utf-8') as file:
            json.dump(data, file, ensure_ascii = False, indent = 2)
    except Exception as e:
        print(f'保存Token缓存失败: {e}')


# ============ 简易 deviceId 存储（手机号 -> deviceId）============
def get_device_id_storage_path():
    """获取 deviceId/token 简易存储文件路径，默认保存到当前运行脚本目录"""
    return get_storage_file_path(DEVICE_ID_STORAGE_FILENAME)


def load_device_id_storage():
    """加载 deviceId 存储 {手机号: deviceId}"""
    storage_path = get_device_id_storage_path()
    if not storage_path.exists():
        return {}
    try:
        with open(storage_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f'加载deviceId缓存失败: {e}')
        return {}


def save_device_id(device_id, account):
    """保存单个账号的 deviceId"""
    storage_path = get_device_id_storage_path()
    data = load_device_id_storage()
    account_data = data.get(account, {})
    account_data['deviceId'] = device_id
    data[account] = account_data
    try:
        with open(storage_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f'保存deviceId失败: {e}')


def save_token_info(account, token, expires_at, last_refresh_at):
    """保存 token 刷新信息"""
    storage_path = get_device_id_storage_path()
    data = load_device_id_storage()
    account_data = data.get(account, {})
    account_data['token'] = token
    account_data['expiresAt'] = expires_at
    account_data['lastRefreshAt'] = last_refresh_at
    data[account] = account_data
    try:
        with open(storage_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f'保存token信息失败: {e}')


def ensure_account_storage_entry(account, token=''):
    """确保账号在简易存储中存在；新账号默认创建空 deviceId，便于手动填写"""
    storage_path = get_device_id_storage_path()
    data = load_device_id_storage()
    account_data = data.get(account)
    if not isinstance(account_data, dict):
        account_data = {}
    changed = False
    if 'deviceId' not in account_data:
        account_data['deviceId'] = ''
        changed = True
    normalized_token = normalize_authorization(token)
    if normalized_token and account_data.get('token') != normalized_token:
        account_data['token'] = normalized_token
        changed = True
    if 'expiresAt' not in account_data:
        account_data['expiresAt'] = 0
        changed = True
    if 'lastRefreshAt' not in account_data:
        account_data['lastRefreshAt'] = 0
        changed = True
    if changed or account not in data:
        data[account] = account_data
        try:
            with open(storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f'初始化账号缓存失败: {e}')


def get_token_info(account):
    """获取 token 刷新信息"""
    data = load_device_id_storage()
    return data.get(account, {})


def get_device_id(account):
    """获取指定账号的 deviceId"""
    data = load_device_id_storage()
    account_data = data.get(account, {})
    return account_data.get('deviceId', '')


def print_startup_info(account_count):
    print(f"移动云盘自动签到 v{SCRIPT_VERSION}")
    print(f"移动云盘共获取到{account_count}个账号")


def print_device_id_notice():
    if get_env_device_id():
        print("已检测到 ydyp_device_id，将优先使用环境变量 deviceId")
        return
    cached_data = load_device_id_storage()
    cached_accounts = [account for account, info in cached_data.items()
                       if isinstance(info, dict) and info.get('deviceId')]
    if cached_accounts:
        print(f"已发现本地缓存 deviceId {len(cached_accounts)} 个账号；新账号将自动写入 ydyp_device_ids.json，deviceId 默认留空，等待手动填写")
        return
    print("未检测到 ydyp_device_id；脚本将优先读取本地缓存，缓存为空时自动生成并保存 deviceId")


def print_storage_path_notice():
    print(f"缓存文件目录: {get_storage_base_dir()}")
    print(f"deviceId/token缓存文件: {get_device_id_storage_path()}")


# 发送通知
def load_send():
    cur_path = path.abspath(path.dirname(__file__))
    notify_file = cur_path + "/notify.py"

    if path.exists(notify_file):
        try:
            from notify import send  # 导入模块的send为notify_send
            print("加载通知服务成功！")
            return send  # 返回导入的函数
        except ImportError:
            print("加载通知服务失败~")
    else:
        print("加载通知服务失败~")

    return False


class YP:
    def __init__(self, cookie):
        try:
            self.notebook_id = None
            self.note_token = None
            self.note_auth = None
            self.auth_token = None
            self.click_num = 15
            self.draw = 1
            self.client_version = '12.5.4'
            self.market_base_url = 'https://m.mcloud.139.com'
            self.market_source_id = '1097'
            self.sso_token = None
            self.user_domain_id = ''
            self.market_device_id = ''
            self.market_x_device_info = ''
            self.market_device_from_env = False
            self.market_device_is_placeholder = False
            self.market_headers = {}
            self.market_cookies = {}
            self.red_packet_token = ''
            self.red_packet_mobile = ''
            self.session = requests.Session()
            self.user_log_lines = []

            self.timestamp = str(int(round(time.time() * 1000)))
            self.cookies = {'sensors_stay_time': self.timestamp}

            parts = cookie.split("#")
            if len(parts) < 2:
                raise ValueError(f"⚠️ 变量值格式错误: {cookie}")

            self.Authorization = normalize_authorization(parts[0])
            self.account = parts[1].strip()
            self.token_storage = load_token_storage()
            self.refresh_capable = AES is not None and pad is not None
            self.load_persisted_authorization()
            self.load_or_create_market_device_profile()
            self.auth_token = extract_raw_token(self.Authorization, self.account)
            
            if len(self.account) >= 11:
                self.encrypt_account = self.account[:3] + "****" + self.account[-4:]
            else:
                self.encrypt_account = self.account
                
            self.fruit_url = 'https://happy.mail.10086.cn/jsp/cn/garden/'

            self.jwtHeaders = {
                'User-Agent': ua,
                'Accept': '*/*',
                'Host': 'caiyun.feixin.10086.cn:7071',
            }
            self.treeHeaders = {
                'Host': 'happy.mail.10086.cn',
                'Accept': 'application/json, text/plain, */*',
                'User-Agent': ua,
                'Referer': 'https://happy.mail.10086.cn/jsp/cn/garden/wap/index.html?sourceid=1003',
                'Cookie': '',
            }

        except Exception as e:
            print(f"{e}")
            self.Authorization = None

    def get_storage_record(self):
        """获取存储记录，优先从新版简易存储读取"""
        # 优先从新版简易存储读取
        new_storage = get_token_info(self.account)
        if new_storage.get('token') or new_storage.get('deviceId'):
            return new_storage
        # 后备：从旧版 token_storage 读取
        return (self.token_storage.get('accounts') or {}).get(self.account, {}) or {}

    def load_persisted_authorization(self):
        """加载已保存的 Authorization，优先从简易存储读取"""
        # 优先从新版简易存储读取
        new_storage = get_token_info(self.account)
        stored_token = normalize_authorization(new_storage.get('token', ''))
        if stored_token:
            self.Authorization = stored_token
            # 同时也写入旧版存储，保持兼容
            token_storage = load_token_storage()
            if self.account not in token_storage.get('accounts', {}):
                token_storage['accounts'][self.account] = {}
            token_storage['accounts'][self.account]['token'] = stored_token
            save_token_storage(token_storage)
            return
        # 后备：从旧版 token_storage 读取
        stored = self.get_storage_record()
        stored_token = normalize_authorization(stored.get('token', ''))
        if stored_token:
            self.Authorization = stored_token

    def load_or_create_market_device_profile(self):
        """加载 deviceId；未配置环境变量且缓存为空时自动生成并保存"""
        ensure_account_storage_entry(self.account, self.Authorization)

        env_device_id = get_env_device_id()
        if env_device_id:
            self.market_device_id = env_device_id
            self.market_x_device_info = build_x_device_info(env_device_id)
            self.market_device_from_env = True
            self.market_device_is_placeholder = False
            return

        stored_device_id = get_device_id(self.account)
        if stored_device_id:
            self.market_device_id = stored_device_id
            self.market_x_device_info = build_x_device_info(stored_device_id)
            self.market_device_is_placeholder = False
            return

        self.market_device_id = generate_device_id()
        self.market_x_device_info = build_x_device_info(self.market_device_id)
        self.market_device_is_placeholder = False
        if self.market_device_id:
            save_device_id(self.market_device_id, self.account)

    def save_authorization_record(self, token=None, user_domain_id=None, refreshed=False, expires_at=None,
                                  market_device_id=None, x_device_info=None, market_device_generated=None):
        token = normalize_authorization(token or self.Authorization)
        accounts = self.token_storage.setdefault('accounts', {})
        old_record = accounts.get(self.account, {}) or {}
        if not token:
            token = normalize_authorization(old_record.get('token', ''))
        last_refresh_at = old_record.get('lastRefreshAt', 0)
        if refreshed:
            last_refresh_at = current_millis()
        record_expires_at = expires_at or old_record.get('expiresAt') or (current_millis() + TOKEN_VALID_TIME)
        record = {
            **old_record,
            'account': self.account,
            'token': token,
            'authToken': extract_raw_token(token, self.account),
            'expiresAt': int(record_expires_at),
            'updatedAt': current_millis(),
            'lastRefreshAt': last_refresh_at,
        }
        if user_domain_id or old_record.get('userDomainId'):
            record['userDomainId'] = user_domain_id or old_record.get('userDomainId')
        final_market_device_id = market_device_id or old_record.get('marketDeviceId')
        final_x_device_info = x_device_info or old_record.get('xDeviceInfo')
        if final_market_device_id:
            record['marketDeviceId'] = final_market_device_id
        if final_x_device_info:
            record['xDeviceInfo'] = final_x_device_info
        if market_device_generated is None:
            if 'marketDeviceGenerated' in old_record:
                record['marketDeviceGenerated'] = old_record.get('marketDeviceGenerated')
        else:
            record['marketDeviceGenerated'] = bool(market_device_generated)
        accounts[self.account] = record
        save_token_storage(self.token_storage)

    def should_refresh_authorization(self, force=False):
        if force:
            return True, '强制刷新'
        stored = self.get_storage_record()
        now = current_millis()
        expires_at = int(stored.get('expiresAt') or 0)
        if not stored.get('token'):
            return True, '本地无缓存Token'
        if now >= expires_at:
            return True, '缓存Token已过期'
        if expires_at - now <= TOKEN_REFRESH_ADVANCE:
            hours = (expires_at - now) / 3600000
            return True, f'将在 {hours:.1f} 小时后过期'
        days = (expires_at - now) / 86400000
        return False, f'Token 状态良好（剩余 {days:.1f} 天）'

    def refresh_authorization_token(self, force=False):
        need_refresh, reason = self.should_refresh_authorization(force = force)
        if not need_refresh:
            self.log(f'-Authorization状态: {reason}')
            return True
        if not self.refresh_capable:
            self.log('-未安装 pycryptodome，跳过Authorization自动刷新')
            return True

        # 使用微信小程序UA刷新Token（源码：miniprogram|||1.0）
        refresh_headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.47(0x18002f2c) NetType/WIFI Language/zh_CN miniProgram/wx4e4ed37286c816c2',
            'x-yun-tid': generate_uuid(),
            'Authorization': self.Authorization,
            'x-yun-api-version': 'v1',
            'x-yun-module-type': '100',
            'x-yun-op-type': '1',
            'x-yun-app-channel': '10214200',
            'x-yun-client-info': '||8||||||||||||',
            'hcy-cool-flag': '1',
        }
        stored = self.get_storage_record()
        if stored.get('userDomainId'):
            refresh_headers['x-yun-uni'] = stored['userDomainId']

        encrypted_data = aes_encrypt({'phoneNumber': self.account}, REFRESH_TOKEN_AES_KEY)
        refresh_data = self.request_json('https://user-njs.yun.139.com/user/auth/refreshToken',
                                         headers = refresh_headers,
                                         data = {'data': encrypted_data},
                                         method = 'POST',
                                         retries = 1)
        if not refresh_data:
            self.log(f'-Authorization刷新失败: 接口无响应 ({reason})')
            return True
        code = str(refresh_data.get('code', ''))
        data = refresh_data.get('data')
        success = refresh_data.get('success', False)
        is_success = (code in ('0', '00', '000', '0000')) or bool(success) or (code.startswith('0') and len(code) <= 4)
        if not is_success or not isinstance(data, dict):
            self.log(f"-Authorization刷新失败: {refresh_data.get('message') or refresh_data.get('msg', '未知错误')} (code={code or 'unknown'})")
            return True
        raw_token = data.get('token')
        if not raw_token:
            self.log('-Authorization刷新失败: 响应缺少token')
            return True
        expires_at = parse_expire_time_to_millis(data.get('expireTime'))
        self.Authorization = build_authorization(self.account, raw_token)
        self.auth_token = raw_token
        self.save_authorization_record(token = self.Authorization, refreshed = True, expires_at = expires_at)
        self.log(f'-Authorization自动刷新成功: {reason}')
        self.log(f"-Authorization有效期: {datetime.fromtimestamp(expires_at / 1000).strftime('%Y-%m-%d %H:%M:%S')}")
        return True

    def sync_token_storage(self):
        """同步存储 token 和 deviceId 到简易存储"""
        # 保存 token 刷新信息到简易存储
        stored = self.get_storage_record()
        expires_at = stored.get('expiresAt', current_millis() + TOKEN_VALID_TIME)
        last_refresh_at = stored.get('lastRefreshAt', 0)
        save_token_info(self.account, self.Authorization, expires_at, last_refresh_at)
        # 仅当账号已手动配置真实 deviceId 时才回写缓存；
        # 运行时兜底 deviceId 不落盘，避免覆盖成自动值。
        if self.market_device_id and not self.market_device_is_placeholder:
            save_device_id(self.market_device_id, self.account)
        # 同时保持旧版存储兼容
        self.save_authorization_record(token = self.Authorization, user_domain_id = self.user_domain_id)

    def log(self, content):
        print(content)
        self.user_log_lines.append(content)


    @staticmethod
    def catch_errors(func):
        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except Exception as e:
                err_str = f"错误: {str(e)}"
                print(err_str)
                self.user_log_lines.append(err_str)
            return None

        return wrapper

    @catch_errors
    def run(self):
        self.refresh_authorization_token()
        if self.jwt():
            self.signin_status()
            self.click()
            self.get_tasklist(url = 'sign_in_3', app_type = 'cloud_app')
            self.log(f'\n📰 公众号任务')
            self.wxsign()
            self.shake()
            self.surplus_num()
            self.log(f'\n🔥 热门任务')
            self.backup_cloud()
            self.log(f'\n📧 139邮箱任务')
            self.get_tasklist(url = 'newsign_139mail', app_type = 'email_app')
            self.receive()
            self.red_envelope_party()
            global all_logs
            user_log_str = "\n".join(self.user_log_lines)
            all_logs += f"用户【{self.encrypt_account}】日志:\n{user_log_str}\n\n"
            
        else:
            global err_accounts
            # 失效账号
            err_accounts += f'{self.encrypt_account}\n'

    @catch_errors
    def send_request(self, url, headers=None, cookies=None, data=None, params=None, method='GET', debug=None,
                     retries=5):

        debug = debug if debug is not None else GLOBAL_DEBUG

        request_headers = dict(headers or {})
        request_cookies = dict(cookies or {})
        if isinstance(data, dict):
            request_args = {'json': data}
        elif isinstance(data, str):
            request_args = {'data': data.encode('utf-8')}
        else:
            request_args = {'data': data}

        for attempt in range(retries):
            try:
                response = self.session.request(method, url, params = params, headers = request_headers or None,
                                                cookies = request_cookies or None, **request_args)
                response.raise_for_status()
                if debug:
                    print(f'\n【{url}】响应数据:\n{response.text}')
                return response
            except (requests.RequestException, ConnectionError, TimeoutError) as e:
                print(f"请求异常: {e}")
                if attempt >= retries - 1:
                    print("达到最大重试次数。")
                    return None
                time.sleep(1)

    def request_json(self, url, headers=None, cookies=None, data=None, params=None, method='GET', debug=None,
                     retries=5):
        response = self.send_request(url, headers = headers, cookies = cookies, data = data, params = params,
                                     method = method, debug = debug, retries = retries)
        if response is None:
            return None
        try:
            return response.json()
        except ValueError as e:
            self.log(f'响应解析失败: {e}')
            return None

    @staticmethod
    def get_today_sign_state(result):
        today_sign_in = result.get('todaySignIn')
        if isinstance(today_sign_in, bool):
            return today_sign_in
        for day in result.get('cal') or []:
            if day.get('t'):
                return bool(day.get('s'))
        return None

    @staticmethod
    def extract_user_domain_id(jwt_token):
        try:
            payload = jwt_token.split('.')[1]
            payload += '=' * (-len(payload) % 4)
            data = json.loads(base64.urlsafe_b64decode(payload).decode())
            sub = data.get('sub', '')
            if isinstance(sub, str):
                sub = json.loads(sub)
            return sub.get('userDomainId', '')
        except (IndexError, KeyError, TypeError, ValueError, json.JSONDecodeError):
            return ''

    def build_market_context(self, jwt_token):
        self.user_domain_id = self.extract_user_domain_id(jwt_token)
        self.market_headers = {
            'User-Agent': market_ua,
            'Accept': '*/*',
            'jwtToken': jwt_token,
            'X-Requested-With': 'com.chinamobile.mcloud',
            'Referer': self.build_market_page_url(),
        }
        self.market_cookies = {'jwtToken': jwt_token}
        if self.user_domain_id:
            self.market_cookies['userDomainId'] = self.user_domain_id
        self.seed_market_device_cookie()
        self.sync_token_storage()

    def build_market_page_url(self, source_id=None):
        current_source_id = source_id or self.market_source_id
        return f'{self.market_base_url}/portal/mobilecloud/index.html?path=newsignin&sourceid={current_source_id}&enableShare=1&token={self.sso_token or ""}&targetSourceId=001005'

    def get_market_device_id(self):
        if self.market_device_id:
            return self.market_device_id
        for cookie in self.session.cookies:
            if cookie.name.startswith('.thumbcache_') and cookie.value:
                return unquote(cookie.value)
        return ''

    def seed_market_device_cookie(self):
        device_id = self.market_device_id
        if not device_id:
            return
        cookie_value = device_id[1:] if self.market_device_from_env and device_id.startswith('B') else device_id
        if any(cookie.name.startswith('.thumbcache_') and unquote(cookie.value) == cookie_value
               for cookie in self.session.cookies):
            return
        self.session.cookies.set(f'.thumbcache_{self.account}', cookie_value, domain='m.mcloud.139.com', path='/')

    def build_market_headers(self, extra_headers=None, referer=None):
        headers = dict(self.market_headers)
        headers['Referer'] = referer or headers.get('Referer') or self.build_market_page_url()
        device_id = self.get_market_device_id()
        if device_id:
            headers['deviceId'] = device_id
        if self.market_x_device_info:
            headers['x-DeviceInfo'] = self.market_x_device_info
        if extra_headers:
            headers.update(extra_headers)
        return headers

    def build_receive_headers(self, source_id=None):
        return self.build_market_headers({
            'showLoading': 'true',
            'appVersion': f'{self.client_version}.0',
            'activityId': 'sign_in_3',
        }, referer = self.build_market_page_url(source_id))

    def request_market_json(self, url, params=None, data=None, method='GET', debug=None, retries=5, headers=None,
                            cookies=None):
        request_cookies = dict(self.market_cookies)
        if cookies:
            request_cookies.update(cookies)
        return self.request_json(url, headers = self.build_market_headers(headers), cookies = request_cookies,
                                 data = data, params = params, method = method, debug = debug, retries = retries)

    def post_signin_journaling(self, keyword, source_id=None):
        current_source_id = source_id or self.market_source_id
        payload = f'module=uservisit&optkeyword={keyword}&sourceid={current_source_id}&marketName=sign_in_3'
        response = self.send_request(f'{self.market_base_url}/ycloud/visitlog/journaling',
                                     headers = self.build_market_headers(
                                         {'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'},
                                         referer = self.build_market_page_url(current_source_id)
                                     ),
                                     cookies = self.market_cookies, data = payload, method = 'POST', retries = 1)
        return response is not None

    def prepare_signin_center_session(self, for_receive=False, source_id=None):
        current_source_id = source_id or self.market_source_id
        page_url = self.build_market_page_url(current_source_id)
        self.send_request(page_url, headers = self.build_market_headers(referer = page_url),
                          cookies = self.market_cookies, retries = 1)
        for keyword in (
            'newsignin_index_pv',
            'newsignin_index_client',
            'newsignin_index_app_client',
            'newsignin_index_cookie_login',
            'newsignin_index_cookie',
            'newsignin_index_app_cookie_login',
        ):
            self.post_signin_journaling(keyword, current_source_id)
        if for_receive:
            self.post_signin_journaling('newsignin_index_receive_type', current_source_id)
        return True

    def click_task(self, task_id, key='task'):
        return self.request_market_json(f'{self.market_base_url}/market/signin/task/click?key={key}&id={task_id}')

    def build_red_packet_headers(self, token=''):
        request_id = f'{datetime.now().strftime("%Y%m%d%H%M%S")}{current_millis()}{random_string(8)}'
        timestamp = current_millis()
        headers = {
            'requestId': request_id,
            'appId': RED_PACKET_APP_ID,
            'token': token or '',
        }
        raw = ''.join(str(headers[key]) for key in headers if headers[key] is not None)
        headers['sign'] = hashlib.md5(f'{raw}{RED_PACKET_SIGN_KEY}{timestamp}'.encode()).hexdigest()
        headers['timestamp'] = str(timestamp)
        headers.update({
            'User-Agent': ua,
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json;charset=UTF-8',
            'Origin': 'https://cpactiv.buy.139.com',
            'Referer': RED_PACKET_PAGE_URL,
            'x-origin': RED_PACKET_PAGE_URL,
            'x-channelSrc': RED_PACKET_CHANNEL_SRC,
            'x-DeviceInfo': self.build_red_packet_device_info(),
        })
        return headers

    def build_red_packet_device_info(self):
        screen = '390X844'
        uuid_value = f'{current_millis()}{random_string(10)}'
        return '|'.join(['wifi', 'h5', '1.0.0', 'v1.0.0', '', ua, uuid_value, '', '', screen, 'zh', '', ''])

    def request_red_packet_json(self, path_url, data=None, token=None, debug=None, retries=5):
        url = f'{RED_PACKET_BASE_URL}{path_url}'
        return self.request_json(url, headers = self.build_red_packet_headers(token if token is not None else self.red_packet_token),
                                 data = data or {}, method = 'POST', debug = debug, retries = retries)

    def login_red_packet(self):
        if self.red_packet_token:
            return True
        sso_token = self.query_spec_token(RED_PACKET_SOURCE_ID)
        if not sso_token:
            self.log('-红包派对登录失败: SSO token获取失败')
            return False
        login_data = self.request_red_packet_json('/user/tokenValidate', data = {
            'version': '1.0',
            'pintype': 13,
            'token': sso_token,
            'deviceId': '',
            'loginConfig': '',
        }, token = '')
        if not login_data:
            self.log('-红包派对登录失败: 接口无响应')
            return False
        header = login_data.get('header') or {}
        result = login_data.get('data') or {}
        if str(header.get('status')) == '200' and result.get('token'):
            self.red_packet_token = result.get('token')
            self.red_packet_mobile = result.get('account') or result.get('mobile') or result.get('phone') or self.account
            return True
        msg = header.get('errMsg') or header.get('respMsg') or result.get('errorMsg') or '未知错误'
        self.log(f'-红包派对登录失败: {msg}')
        return False

    def get_red_packet_task_list(self):
        return self.request_red_packet_json('/redpacket/configTaskLoginList', data = {'version': RED_PACKET_VERSION})

    def get_red_packet_account_info(self):
        return self.request_red_packet_json('/redpacket/userAccountInfo', data = {
            'version': RED_PACKET_VERSION,
            'platformType': 1,
        })

    def get_red_packet_toast_info(self, task_code=None):
        data = {'version': RED_PACKET_VERSION}
        if task_code:
            data['configTaskCode'] = task_code
        return self.request_red_packet_json('/redpacket/userToastInfo', data = data)

    @staticmethod
    def red_packet_status_text(status):
        return {
            0: '未完成',
            1: '已完成',
            3: '奖品已兑完',
            4: '明天再来',
        }.get(status, str(status))

    @staticmethod
    def get_red_packet_task_amount(task):
        amount = task.get('prizeAmount')
        if amount is None:
            amount = task.get('taskAmount')
        try:
            return f'{float(amount) / 100:.2f}元' if amount is not None else ''
        except (TypeError, ValueError):
            return ''

    def complete_red_packet_task(self, task):
        return self.request_red_packet_json('/redpacket/userCompleteTask', data = {
            'version': RED_PACKET_VERSION,
            'platformType': 1,
            'taskId': task.get('id'),
        })

    def browse_red_packet_task(self, task_code):
        return self.request_red_packet_json('/redpacket/userBrowse', data = {
            'taskCode': task_code,
            'version': RED_PACKET_VERSION,
        })

    @staticmethod
    def red_packet_data(data):
        return (data or {}).get('data') or {}

    def red_packet_error(self, data, default='未知错误'):
        header = (data or {}).get('header') or {}
        result = self.red_packet_data(data)
        return result.get('errorMsg') or header.get('errMsg') or header.get('respMsg') or default

    def is_red_packet_ok(self, data):
        return bool(data) and str(((data or {}).get('header') or {}).get('status')) == '200'

    def complete_red_packet_action(self, task):
        task_name = task.get('taskName', '')
        data = self.complete_red_packet_task(task)
        if not data:
            self.log(f'-红包派对任务失败: {task_name} 接口无响应')
            return False
        result = self.red_packet_data(data)
        if result and result.get('status') not in (None, 1):
            self.log(f"-红包派对任务失败: {task_name} {self.red_packet_error(data)}")
            return False
        return True

    def user_sign_red_packet(self):
        data = self.request_red_packet_json('/redpacket/userSign', data = {
            'version': RED_PACKET_VERSION,
            'platformType': 1,
        })
        if not data:
            self.log('-红包派对签到失败: 接口无响应')
            return False
        result = self.red_packet_data(data)
        if self.is_red_packet_ok(data) and result.get('status') == 1:
            self.log('-已完成: 每日签到')
            self.log_red_packet_reward('SIGN_1', '每日签到')
            return True
        self.log(f'-红包派对签到失败: {self.red_packet_error(data)}')
        return False

    def get_red_packet_today_sign(self, task_list=None):
        if task_list is None:
            data = self.get_red_packet_task_list()
            if not self.is_red_packet_ok(data):
                return None
            task_list = self.red_packet_data(data)
        for item in task_list.get('configTaskSignList') or []:
            if item.get('isToday') == 1:
                return item
        return None

    def get_red_packet_cloud_phones(self):
        phones = []
        for status in ('ACTIVE', 'PENDING'):
            data = self.request_red_packet_json('/thirdapi/huawei/thirdQueryUserRelationshipV2', data = {
                'pageNumber': 1,
                'pageSize': 10,
                'status': status,
            })
            body = self.red_packet_data(data)
            nested = body.get('data') if isinstance(body, dict) else {}
            detail = nested if isinstance(nested, dict) else body
            phones.extend(detail.get('subscribeDetails') or [])
        return phones

    def get_red_packet_hw_token(self):
        data = self.request_red_packet_json('/user/gethwToken', data = {'token': self.red_packet_token})
        body = self.red_packet_data(data)
        return body.get('hwToken') or ((body.get('data') or {}).get('hwToken') if isinstance(body, dict) else '')

    def get_red_packet_rcs_token(self, target_source_id='0'):
        data = self.request_red_packet_json('/user/getRcsToken', data = {
            'token': self.red_packet_token,
            'targetSourceId': target_source_id,
        })
        body = self.red_packet_data(data)
        return body.get('token') or ''

    def get_red_packet_app_list(self):
        data = self.request_red_packet_json('/redpacket/configAppList', data = {'platformType': 1})
        if not self.is_red_packet_ok(data):
            return []
        return self.red_packet_data(data).get('list') or []

    def get_red_packet_install_status(self, hw_token, instance_id, package_name):
        data = self.request_red_packet_json('/app/activity/instanceApkInstallStatus', data = {
            'hwToken': hw_token,
            'apkList': [package_name],
            'instanceIdList': [instance_id],
        })
        body = self.red_packet_data(data)
        items = body.get('data') if isinstance(body, dict) else body
        if isinstance(items, dict):
            items = items.get('list') or []
        if not items:
            return None
        instance_list = (items[0] or {}).get('instanceList') or []
        if not instance_list:
            return None
        return instance_list[0].get('installStatus')

    def poll_red_packet_install_task(self, hw_token, task_id):
        for _ in range(60):
            data = self.request_red_packet_json('/app/activity/appInstallTaskStatus', data = {
                'taskId': task_id,
                'hwToken': hw_token,
            })
            body = self.red_packet_data(data)
            status_data = body.get('data') if isinstance(body, dict) and isinstance(body.get('data'), dict) else body
            status = (status_data or {}).get('taskStatus')
            if status == 2:
                return True
            if status == 3:
                return False
            self.sleep(1, 1.2)
        return False

    def report_red_packet_install_app(self, task, app, existed=None):
        data = {
            'taskId': task.get('id'),
            'appId': app.get('id'),
            'version': RED_PACKET_VERSION,
            'platformType': 1,
        }
        if existed is not None:
            data['existed'] = existed
        return self.request_red_packet_json('/redpacket/userInstallApp', data = data)

    def install_red_packet_app(self, task):
        if not self.complete_red_packet_action(task):
            return False
        phones = self.get_red_packet_cloud_phones()
        if not phones:
            self.log(f"-需手动完成: {task.get('taskName', '')} (无云手机)")
            return False
        phone = next((item for item in phones if ((item.get('subsProdInstances') or [{}])[0]).get('lockStatus') != 'Y'), phones[0])
        instance_id = phone.get('instanceId')
        if not instance_id or ((phone.get('subsProdInstances') or [{}])[0]).get('lockStatus') == 'Y':
            self.log(f"-需手动完成: {task.get('taskName', '')} (云机锁屏)")
            return False
        apps = self.get_red_packet_app_list()
        if not apps:
            self.log(f"-红包派对任务失败: {task.get('taskName', '')} 应用列表为空")
            return False
        hw_token = self.get_red_packet_hw_token()
        if not hw_token:
            self.log(f"-红包派对任务失败: {task.get('taskName', '')} hwToken获取失败")
            return False
        for app in apps:
            package_name = app.get('packageName')
            if not package_name:
                continue
            if self.get_red_packet_install_status(hw_token, instance_id, package_name) == 2:
                self.report_red_packet_install_app(task, app, existed = 1)
                refreshed = self.refresh_red_packet_task(task.get('taskCode')) or {}
                if refreshed.get('userStatus') == 1:
                    self.log(f"-已完成: {task.get('taskName', '')}")
                    self.log_red_packet_reward(task.get('taskCode'), task.get('taskName', ''))
                    return True
                continue
            install_data = self.request_red_packet_json('/app/activity/apkInstall', data = {
                'instanceId': instance_id,
                'appId': app.get('packageId'),
                'hwToken': hw_token,
            })
            body = self.red_packet_data(install_data)
            install_result = body.get('data') if isinstance(body, dict) and isinstance(body.get('data'), dict) else body
            if not (install_result or {}).get('success'):
                continue
            if self.poll_red_packet_install_task(hw_token, install_result.get('taskId')):
                self.report_red_packet_install_app(task, app)
                refreshed = self.refresh_red_packet_task(task.get('taskCode')) or {}
                if refreshed.get('userStatus') == 1:
                    self.log(f"-已完成: {task.get('taskName', '')}")
                    self.log_red_packet_reward(task.get('taskCode'), task.get('taskName', ''))
                    return True
                self.log(f"-已安装应用: {app.get('apkName') or package_name}")
                return True
        self.log(f"-红包派对任务失败: {task.get('taskName', '')} 未找到可安装应用")
        return False

    def complete_red_packet_cloud_use(self, task):
        if not self.complete_red_packet_action(task):
            return False
        phones = self.get_red_packet_cloud_phones()
        if phones:
            self.get_red_packet_rcs_token()
        refreshed = self.refresh_red_packet_task(task.get('taskCode')) or {}
        if refreshed.get('userStatus') == 1:
            self.log(f"-已完成: {task.get('taskName', '')}")
            self.log_red_packet_reward(task.get('taskCode'), task.get('taskName', ''))
            return True
        self.log(f"-需手动完成: {task.get('taskName', '')} (需云机内实际使用)")
        return True

    def get_red_packet_topic(self):
        data = self.request_red_packet_json('/redpacket/configTopicList', data = {})
        topics = self.red_packet_data(data).get('list') or []
        return topics[0] if topics else None

    def answer_red_packet_topic(self, task):
        if not self.complete_red_packet_action(task):
            return False
        question = ''
        for _ in range(15):
            topic = self.get_red_packet_topic()
            if not topic:
                self.log(f"-红包派对任务失败: {task.get('taskName', '')} 题库为空")
                return False
            question = topic.get('topicContent', '')
            answer_text = RED_PACKET_KNOWN_ANSWERS.get(question)
            try:
                options = json.loads(topic.get('topicOption') or '[]')
            except (TypeError, ValueError):
                options = []
            if answer_text and answer_text in options:
                break
            self.sleep(0.1, 0.2)
        else:
            self.log(f'-需手动完成: {task.get("taskName", "")} (未知题目: {question})')
            return False
        answer = 'ABCD'[options.index(answer_text)]
        data = self.request_red_packet_json('/redpacket/userTopicAnswer', data = {
            'taskId': int(task.get('id')),
            'topicId': int(topic.get('id')),
            'answer': answer,
            'version': RED_PACKET_VERSION,
            'platformType': 1,
        })
        result = self.red_packet_data(data)
        if self.is_red_packet_ok(data) and result.get('status') == 1:
            self.log(f"-已完成: {task.get('taskName', '')}")
            self.log_red_packet_reward(task.get('taskCode'), task.get('taskName', ''))
            return True
        self.log(f"-红包派对任务失败: {task.get('taskName', '')} {self.red_packet_error(data)}")
        return False

    def log_red_packet_reward(self, task_code, default_name=''):
        data = self.get_red_packet_toast_info(task_code)
        if not data or str((data.get('header') or {}).get('status')) != '200':
            return
        prize = (data.get('data') or {}).get('lastUserPrize') or {}
        amount = prize.get('prizeAmount')
        if amount:
            try:
                self.log(f"-红包派对奖励: {prize.get('prizeName') or default_name} +{float(amount) / 100:.2f}元")
            except (TypeError, ValueError):
                self.log(f"-红包派对奖励: {prize.get('prizeName') or default_name} +{amount}")

    def refresh_red_packet_task(self, task_code):
        data = self.get_red_packet_task_list()
        if not data or str((data.get('header') or {}).get('status')) != '200':
            return None
        task_list = data.get('data') or {}
        for group in ('configTaskNoviceList', 'configTaskDailyList', 'configTaskMonthlyList'):
            for task in task_list.get(group) or []:
                if task.get('taskCode') == task_code:
                    return task
        return None

    def finish_red_packet_task(self, task, browse=False):
        task_name = task.get('taskName', '')
        task_code = task.get('taskCode', '')
        complete_data = self.complete_red_packet_task(task)
        if not complete_data:
            self.log(f'-红包派对任务失败: {task_name} 接口无响应')
            return False
        result = complete_data.get('data') or {}
        if result and result.get('status') not in (None, 1):
            self.log(f"-红包派对任务失败: {task_name} {result.get('errorMsg', '未知错误')}")
            return False
        if browse:
            self.sleep(15, 16)
            browse_data = self.browse_red_packet_task(task_code)
            if not browse_data or str((browse_data.get('header') or {}).get('status')) != '200':
                msg = ((browse_data or {}).get('data') or {}).get('errorMsg') or '浏览确认失败'
                self.log(f'-红包派对任务失败: {task_name} {msg}')
                return False
        refreshed = self.refresh_red_packet_task(task_code) or {}
        status = refreshed.get('userStatus', task.get('userStatus'))
        if status == 1:
            self.log(f'-已完成: {task_name}')
            self.log_red_packet_reward(task_code, task_name)
            return True
        self.log(f'-已登记: {task_name} ({self.red_packet_status_text(status)})')
        return True

    def log_red_packet_balance(self):
        data = self.get_red_packet_account_info()
        if not data or str((data.get('header') or {}).get('status')) != '200':
            self.log('-红包派对余额查询失败')
            return
        info = (data.get('data') or {}).get('info') or {}
        try:
            can_amount = float(info.get('canAmount') or 0) / 100
            total_amount = float(info.get('totalAmount') or 0) / 100
            self.log(f'-红包派对余额: 可用{can_amount:.2f}元，累计{total_amount:.2f}元')
        except (TypeError, ValueError):
            self.log('-红包派对余额查询失败: 响应异常')

    def handle_red_packet_task(self, task):
        task_name = task.get('taskName', '')
        task_code = task.get('taskCode', '')
        status = int(task.get('userStatus') or 0)
        amount = self.get_red_packet_task_amount(task)
        suffix = f' ({amount})' if amount else ''
        if status == 1:
            self.log(f'-已完成: {task_name}{suffix}')
            return
        if status in (3, 4):
            self.log(f'-暂不可做: {task_name} ({self.red_packet_status_text(status)})')
            return
        if task_code in RED_PACKET_BROWSE_TASKS:
            self.log(f'-去完成: {task_name}{suffix}')
            self.finish_red_packet_task(task, browse = True)
            return
        if task_code in RED_PACKET_DIRECT_TASKS:
            self.log(f'-去完成: {task_name}{suffix}')
            self.finish_red_packet_task(task)
            return
        if task_code == 'DAILY_1':
            self.log(f'-去完成: {task_name}{suffix}')
            self.complete_red_packet_cloud_use(task)
            return
        if task_code == 'MONTHLY_2':
            self.log(f'-去完成: {task_name}{suffix}')
            self.install_red_packet_app(task)
            return
        if task_code == 'MONTHLY_3':
            self.log(f'-去完成: {task_name}{suffix}')
            self.answer_red_packet_topic(task)
            return
        reason = RED_PACKET_MANUAL_TASKS.get(task_code, '未知任务')
        self.log(f'-需手动完成: {task_name}{suffix} ({reason})')

    def handle_red_packet_sign(self, task_list):
        today = self.get_red_packet_today_sign(task_list)
        if not today:
            return
        status = int(today.get('status') or 0)
        amount = today.get('signAmount')
        suffix = f' ({float(amount) / 100:.2f}元)' if amount else ''
        if status == 1:
            self.log(f'-已完成: 每日签到{suffix}')
        elif status == 0:
            self.log(f'-去完成: 每日签到{suffix}')
            self.user_sign_red_packet()
        else:
            self.log(f'-暂不可做: 每日签到 ({self.red_packet_status_text(status)})')

    def red_packet_task_groups(self):
        return [
            ('configTaskNoviceList', '\n🧧 红包派对新手任务'),
            ('configTaskDailyList', '\n🧧 红包派对每日任务'),
            ('configTaskMonthlyList', '\n🧧 红包派对每月任务'),
        ]

    def red_envelope_party(self):
        self.log(f'\n🧧 红包派对任务')
        if not self.login_red_packet():
            return
        data = self.get_red_packet_task_list()
        if not data:
            self.log('获取红包派对任务失败: 接口无响应')
            return
        header = data.get('header') or {}
        if str(header.get('status')) != '200':
            self.log(f"获取红包派对任务失败: {header.get('errMsg') or header.get('respMsg') or '未知错误'}")
            return
        task_list = data.get('data') or {}
        self.log_red_packet_balance()
        self.handle_red_packet_sign(task_list)
        for group, title in self.red_packet_task_groups():
            tasks = task_list.get(group) or []
            if not tasks:
                continue
            self.log(title)
            for task in tasks:
                self.handle_red_packet_task(task)
        self.log_red_packet_balance()

    def get_notice_status(self):
        send_data = self.request_json('https://caiyun.feixin.10086.cn/market/msgPushOn/task/status',
                                      headers = self.jwtHeaders) or {}
        if send_data.get('code') != 0:
            return {}
        return send_data.get('result', {}) or {}

    def format_notice_task_log(self, task_name, notice_status):
        if not notice_status:
            return f'-需手动完成: {task_name}'
        push_on = int(notice_status.get('pushOn') or 0)
        first_status = int(notice_status.get('firstTaskStatus') or 0)
        second_status = int(notice_status.get('secondTaskStatus') or 0)
        on_duration = int(notice_status.get('onDuaration') or 0)
        total = int(notice_status.get('total') or 31)
        if push_on != 1:
            return f'-需手动完成: {task_name} (通知未开启)'
        if second_status == 3:
            return f'-已完成: {task_name}'
        if first_status != 3:
            return f'-待领取: {task_name} (首日奖励可领取)'
        if second_status == 2:
            return f'-待领取: {task_name} (已开启{on_duration}/{total}天)'
        return f'-进行中: {task_name} (已开启{on_duration}/{total}天)'

    def build_cloud_file_headers(self):
        """云盘文件操作请求头：沿用 v5.0.3 已验证可用的上传头，避免 00010014"""
        return {
            'x-yun-op-type': '1',
            'x-yun-sub-op-type': '100',
            'x-yun-api-version': 'v1',
            'x-yun-client-info': '6|127.0.0.1|1|12.1.0|realme|RMX5060|BCFF2BBA6881DD8E4971803C63DDB5E4|02-00-00-00-00-00|android 15|1264X2592|zh||||032|0|',
            'x-yun-app-channel': '10000023',
            'Authorization': self.Authorization,
            'Content-Type': 'application/json; charset=UTF-8',
            'User-Agent': 'okhttp/4.12.0',
            'Host': 'personal-kd-njs.yun.139.com',
            'Connection': 'Keep-Alive'
        }

    def build_share_headers(self):
        """分享文件请求头：沿用 v5.0.3 已验证可用的分享头"""
        return {
            'Authorization': self.Authorization,
            'x-yun-api-version': 'v1',
            'x-yun-app-channel': '10000023',
            'x-yun-client-info': f'||9|{self.client_version}|Chrome|143.0.7499.146|codextestshare||Windows 10||zh-CN|||Q2hyb21l||',
            'x-yun-module-type': '100',
            'x-yun-svc-type': '1',
            'x-SvcType': '1',
            'x-yun-channel-source': '10000023',
            'x-huawei-channelSrc': '10000023',
            'Content-Type': 'application/json;charset=UTF-8',
            'CMS-DEVICE': 'default',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
            'Referer': 'https://yun.139.com/shareweb/',
            'Origin': 'https://yun.139.com',
        }

    def create_cloud_file(self, prefix, extension='txt'):
        beijing_tz = timezone(timedelta(hours=8))
        now = datetime.now(beijing_tz)
        file_size = len(cloud_file_dummy_content)
        file_name = f"{prefix}{now.strftime('%Y%m%d_%H%M%S')}.{extension.lstrip('.')}"
        payload = {
            "contentHash": cloud_file_dummy_hash,
            "contentHashAlgorithm": "SHA256",
            "contentType": "application/oct-stream",
            "fileRenameMode": "force_rename",
            "localCreatedAt": now.isoformat(timespec='milliseconds'),
            "name": file_name,
            "parallelUpload": True,
            "parentFileId": "/",
            "partInfos": [{
                "end": file_size,
                "partNumber": 1,
                "partSize": file_size,
                "start": 0
            }],
            "size": file_size,
            "type": "file"
        }
        response = self.send_request('https://personal-kd-njs.yun.139.com/hcy/file/create',
                                     headers = self.build_cloud_file_headers(), data = payload, method = 'POST')
        if not response or response.status_code != 200:
            return None
        try:
            res_json = response.json()
        except ValueError:
            return None
        if not res_json.get("success"):
            return None
        data = res_json.get("data", {})
        return {
            "fileId": data.get("fileId"),
            "fileName": data.get("fileName", file_name),
        }

    def list_cloud_root_files(self):
        items = []
        page_cursor = ''
        while True:
            response = self.request_json('https://personal-kd-njs.yun.139.com/hcy/file/list',
                                         headers = self.build_cloud_file_headers(),
                                         data = {
                                             'imageThumbnailStyleList': ['Small', 'Large'],
                                             'orderBy': 'updated_at',
                                             'orderDirection': 'DESC',
                                             'pageInfo': {'pageCursor': page_cursor, 'pageSize': 100},
                                             'parentFileId': '/',
                                         },
                                         method = 'POST')
            if not response:
                return items
            if not response.get('success'):
                self.log(f"获取云盘文件列表失败: {response.get('message', '未知错误')}")
                return items
            data = response.get('data', {})
            items.extend(data.get('items', []))
            page_cursor = data.get('nextPageCursor') or ''
            if not page_cursor:
                return items

    @staticmethod
    def is_cleanup_upload_file(item):
        if item.get('type') != 'file' or item.get('parentFileId') != '/':
            return False
        name = item.get('name', '')
        if not (name.endswith('.txt') and (name.startswith('auto_upload_') or name.startswith('auto_share_'))):
            if not (name.endswith('.jpg') and name.startswith('auto_mayday_')):
                return False
        size = item.get('size')
        content_hash = item.get('contentHash')
        return size in (0, 1, None) or content_hash == cloud_file_dummy_hash

    def trash_cloud_files(self, file_ids):
        if not file_ids:
            return True
        response = self.request_json('https://personal-kd-njs.yun.139.com/hcy/recyclebin/batchTrash',
                                     headers = self.build_cloud_file_headers(),
                                     data = {'fileIds': file_ids},
                                     method = 'POST')
        if not response:
            self.log('清理上传文件失败: 接口无响应')
            return False
        if response.get('success'):
            return True
        self.log(f"清理上传文件失败: {response.get('message', '未知错误')}")
        return False

    def cleanup_uploaded_files(self, current_file=None):
        file_ids = []
        if current_file and current_file.get('fileId'):
            file_ids.append(current_file['fileId'])
        for item in self.list_cloud_root_files():
            if self.is_cleanup_upload_file(item):
                file_ids.append(item.get('fileId'))
        seen = set()
        unique_file_ids = []
        for file_id in file_ids:
            if not file_id or file_id in seen:
                continue
            seen.add(file_id)
            unique_file_ids.append(file_id)
        if not unique_file_ids:
            return True
        if self.trash_cloud_files(unique_file_ids):
            self.log(f'-已清理上传文件: {len(unique_file_ids)}个')
            return True
        return False

    def complete_share_file_task(self, task):
        share_file = self.create_cloud_file('auto_share_')
        if not share_file:
            self.log('分享文件失败: 创建临时文件失败')
            return None
        try:
            response = self.request_json('https://yun.139.com/orchestration/personalCloud-rebuild/outlink/v1.0/getOutLink',
                                         headers = self.build_share_headers(),
                                         data = {
                                             'getOutLinkReq': {
                                                 'subLinkType': 0,
                                                 'encrypt': 1,
                                                 'coIDLst': [share_file.get('fileId')],
                                                 'caIDLst': [],
                                                 'pubType': 1,
                                                 'dedicatedName': share_file.get('fileName', ''),
                                                 'period': 1,
                                                 'periodUnit': 1,
                                                 'viewerLst': [],
                                                 'extInfo': {'isWatermark': 0, 'shareChannel': '3001'},
                                                 'commonAccountInfo': {'account': self.account, 'accountType': 1},
                                             }
                                         },
                                         method = 'POST', retries = 1)
        finally:
            self.trash_cloud_files([share_file.get('fileId')])
        data = response.get('data', {}) if response else {}
        result = data.get('result', {}) or data.get('getOutLinkRes', {})
        outlinks = result.get('getOutLinkResSet') or []
        success = False
        if response:
            success = (
                response.get('success') and result.get('resultCode') == '0'
            ) or (
                str(response.get('code')) == '0' and bool(outlinks)
            )
        if not success:
            if response:
                msg = result.get('resultDesc') or response.get('message') or response.get('msg', '未知错误')
            else:
                msg = '接口无响应'
            self.log(f'分享文件失败: {msg}')
            return None
        return self.query_cloud_task(task.get('id', 434), 'month') or task

    def build_ai_headers(self, use_client_info=False):
        """AI相机请求头，与主UA保持一致"""
        device_id = self.market_device_id or generate_device_id()
        headers = {
            'Connection': 'keep-alive',
            'sec-ch-ua-platform': '"iOS"',
            'Authorization': self.Authorization,
            'x-yun-api-version': 'v1',
            'x-yun-tid': str(uuid.uuid4()),
            'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="130", "Mobile Safari";v="130"',
            'sec-ch-ua-mobile': '?1',
            'X-Requested-With': 'com.chinamobile.mcloud',
            'Origin': 'https://frontend.mcloud.139.com',
            'Referer': 'https://frontend.mcloud.139.com/',
            'User-Agent': market_ua,
            'Content-Type': 'application/json',
            'Sec-Fetch-Site': 'same-site',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'zh,zh-CN;q=0.9,en-US;q=0.8,en;q=0.7',
        }
        if use_client_info:
            headers['Accept'] = 'text/event-stream'
            headers['x-yun-client-info'] = f'4||1|{self.client_version}|Apple|iPhone 16 Pro|{device_id.lstrip("B")}|iOS 18.7|||||'
            headers['x-yun-app-channel'] = '101'
            return headers
        headers['Accept'] = '*/*'
        headers['x-DeviceInfo'] = f'||36|{self.client_version}|Apple|iPhone 16 Pro|{device_id.lstrip("B")}|iOS 18.7|||||'
        return headers

    def encrypt_ai_tool_account(self):
        if AES is None or pad is None:
            raise ImportError('未安装 pycryptodome，无法加密AI工具账号')
        cipher = AES.new(AI_TOOL_ACCOUNT_AES_KEY.encode('utf-8'), AES.MODE_CBC, AI_TOOL_ACCOUNT_AES_IV.encode('utf-8'))
        encrypted = cipher.encrypt(pad(self.account.encode('utf-8'), AES.block_size))
        raw = AI_TOOL_ACCOUNT_AES_IV + base64.b64encode(encrypted).decode('utf-8')
        return base64.b64encode(raw.encode('utf-8')).decode('utf-8')

    def build_ai_tool_ad_headers(self):
        return {
            'Authorization': self.Authorization,
            'User-Agent': market_ua,
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json',
            'Origin': 'https://yun.139.com',
            'Referer': 'https://yun.139.com/aiTools/',
            'x-yun-tid': str(uuid.uuid4()),
        }

    def get_ai_camera_sample_base64(self):
        sample_path = path.join(path.abspath(path.dirname(__file__)), 'assets', 'ai_camera_sample.jpg')
        if not path.exists(sample_path):
            return ''
        with open(sample_path, 'rb') as file:
            return f"data:image/jpg;base64,{base64.b64encode(file.read()).decode()}"

    @staticmethod
    def is_ai_chat_success(text):
        payloads = []
        for line in (text or '').splitlines():
            if line.startswith('data:'):
                payloads.append(line[5:].strip())
        if not payloads and text:
            payloads.append(text.strip())
        for payload in payloads:
            if not payload or payload == '[DONE]':
                continue
            try:
                data = json.loads(payload)
            except ValueError:
                continue
            if data.get('success') or data.get('code') == '0000':
                return True
        return False

    def complete_ai_camera_task(self):
        if not self.user_domain_id:
            self.log('AI相机任务失败: 缺少用户信息')
            return False
        image_data = self.get_ai_camera_sample_base64()
        if not image_data:
            self.log('AI相机任务失败: 缺少样图')
            return False
        recognize_payload = json.dumps({
            'channelId': '101',
            'userId': self.user_domain_id,
            'recognizeType': '1',
            'base64': image_data,
            'sendType': '2',
            'imageExt': 'jpg',
            'uploadToCloud': True,
            'timeout': 30000,
        }, ensure_ascii = False, separators = (',', ':'))
        recognize_data = self.request_json('https://ai.yun.139.com/api/image/aiRecognize',
                                           headers = self.build_ai_headers(),
                                           data = recognize_payload,
                                           method = 'POST')
        if not recognize_data:
            self.log('AI相机识图失败: 接口无响应')
            return False
        if not recognize_data.get('success'):
            self.log(f"AI相机识图失败: {recognize_data.get('message', '未知错误')}")
            return False
        recognize_result = recognize_data.get('data') or {}
        file_id = recognize_result.get('fileId')
        if not file_id:
            self.log('AI相机识图失败: 缺少文件ID')
            return False
        task_id = str(recognize_result.get('taskId') or int(time.time() * 1000))
        file_name = f'{int(task_id) + 1}.jpeg' if task_id.isdigit() else f'{task_id}.jpeg'
        input_time = datetime.now(timezone(timedelta(hours = 8))).isoformat(timespec = 'milliseconds')
        chat_payload = json.dumps({
            'userId': self.user_domain_id,
            'sessionId': '',
            'applicationType': 'chat',
            'applicationId': '',
            'sourceChannel': '101',
            'dialogueInput': {
                'dialogue': '？',
                'prompt': '',
                'inputTime': input_time,
                'enableForceLlm': False,
                'enableForceNetworkSearch': True,
                'enableModelThinking': False,
                'enableAllNetworkSearch': False,
                'enableKnowledgeAndNetworkSearch': False,
                'enableRegenerate': False,
                'versionInfo': {'h5Version': '2.7.6'},
                'extInfo': '{}',
                'sortInfo': {},
                'toolSetting': {'imageToolSetting': {'enableLlmDescribe': True}},
                'attachment': {
                    'attachmentTypeList': [3],
                    'fileList': [{'fileId': file_id, 'name': file_name}],
                },
            },
        }, ensure_ascii = False, separators = (',', ':'))
        chat_response = self.send_request('https://ai.yun.139.com/api/outer/assistant/chat/v2/add',
                                          headers = self.build_ai_headers(use_client_info = True),
                                          data = chat_payload,
                                          method = 'POST')
        if not chat_response:
            self.log('AI相机对话失败: 接口无响应')
            return False
        if self.is_ai_chat_success(chat_response.text):
            return True
        try:
            chat_data = chat_response.json()
        except ValueError:
            chat_data = None
        if chat_data and (chat_data.get('success') or chat_data.get('code') == '0000'):
            return True
        if chat_data:
            self.log(f"AI相机对话失败: {chat_data.get('message') or chat_data.get('msg', '未知错误')}")
            return False
        self.log('AI相机对话失败: 响应解析失败')
        return False

    def complete_travel_guide_ai_task(self):
        if not self.user_domain_id:
            self.log('出行攻略问AI失败: 缺少用户信息')
            return False
        input_time = datetime.now(timezone(timedelta(hours = 8))).isoformat(timespec = 'milliseconds')
        chat_payload = json.dumps({
            'userId': self.user_domain_id,
            'sessionId': '',
            'applicationType': 'chat',
            'applicationId': '',
            'sourceChannel': '101',
            'dialogueInput': {
                'dialogue': '给我一份五一出行攻略',
                'prompt': '',
                'inputTime': input_time,
                'enableForceLlm': False,
                'enableForceNetworkSearch': True,
                'enableModelThinking': False,
                'enableAllNetworkSearch': False,
                'enableKnowledgeAndNetworkSearch': False,
                'enableRegenerate': False,
                'versionInfo': {'h5Version': '2.7.6'},
                'extInfo': '{}',
                'sortInfo': {},
                'toolSetting': {'imageToolSetting': {'enableLlmDescribe': True}},
                'attachment': {},
            },
        }, ensure_ascii = False, separators = (',', ':'))
        chat_response = self.send_request('https://ai.yun.139.com/api/outer/assistant/chat/v2/add',
                                          headers = self.build_ai_headers(use_client_info = True),
                                          data = chat_payload,
                                          method = 'POST')
        if not chat_response:
            self.log('出行攻略问AI失败: 接口无响应')
            return False
        response_text = chat_response.text or ''
        if chat_response.status_code == 200 and not response_text.strip():
            return True
        if self.is_ai_chat_success(response_text):
            return True
        try:
            chat_data = chat_response.json()
        except ValueError:
            chat_data = None
        if chat_data and (chat_data.get('success') or chat_data.get('code') == '0000'):
            return True
        if chat_data:
            self.log(f"出行攻略问AI失败: {chat_data.get('message') or chat_data.get('msg', '未知错误')}")
            return False
        self.log('出行攻略问AI失败: 响应解析失败')
        return False

    @staticmethod
    def get_task_progress(task):
        progress_parts = []
        currstep = task.get('currstep', 0)
        process = task.get('process', 0)
        if currstep:
            progress_parts.append(f'阶段{currstep}')
        if process:
            progress_parts.append(f'进度{process}')
        if not progress_parts:
            return ''
        return f" ({'，'.join(progress_parts)})"

    @staticmethod
    def strip_task_name(task):
        return re.sub(r'<[^>]+>', '', task.get('name', ''))

    @staticmethod
    def get_task_step_types(task):
        return set(task.get('stepTypeSet') or [])

    def get_task_click_keys(self, task):
        task_id = task.get('id')
        currstep = task.get('currstep', 0)
        step_types = self.get_task_step_types(task)
        if task_id == 409:
            if currstep > 0:
                return ['task2']
            return ['task', 'task2']
        if 'click' in step_types and currstep == 0:
            return ['task']
        return []

    def get_cloud_task_groups(self):
        return [
            ('beiyong1', '\n🎁 五一福利任务'),
            ('cloudEmail', '\n📮 联动任务'),
            ('time', '\n✨ 新版热门任务'),
            ('day', '\n📆 云盘每日任务'),
            ('month', '\n📆 云盘每月任务'),
        ]

    def query_cloud_task(self, task_id, group='time'):
        return_data = self.request_market_json(f'{self.market_base_url}/market/signin/task/taskListV2', data = {
            'marketname': 'sign_in_3',
            'clientVersion': self.client_version,
            'group': group,
        }, method = 'POST')
        if not return_data or return_data.get('code') != 0:
            return None
        for task in return_data.get('result', {}).get(group, []):
            if task.get('id') == task_id:
                return task
        return None

    def complete_monthly_upload_task(self, task):
        target_count = 100
        current_process = int(task.get('process') or 0)
        for attempt in range(3):
            remaining = max(0, target_count - current_process)
            if remaining == 0:
                return True
            self.log(f'-{"开始" if attempt == 0 else "继续"}补上传进度: 当前{current_process}/{target_count}，还需{remaining}次')
            success = 0
            for _ in range(remaining):
                if self.create_cloud_file('auto_upload_'):
                    success += 1
            if success:
                self.log(f'-批量上传完成: {success}次')
            refreshed_task = self.query_cloud_task(task.get('id', 522), 'time')
            if not refreshed_task:
                return False
            refreshed_process = int(refreshed_task.get('process') or 0)
            if refreshed_task.get('state') == 'FINISH' or refreshed_process >= target_count:
                return True
            if refreshed_process <= current_process:
                self.log(f'-月上传任务进度: {refreshed_process}/{target_count}')
                return False
            current_process = refreshed_process
        self.log(f'-月上传任务进度: {current_process}/{target_count}')
        return False

    def complete_mayday_memory_task(self, task):
        target_count = 10
        task_id = task.get('id', 587)
        current_process = int(task.get('process') or 0)
        remaining = max(0, target_count - current_process)
        if remaining == 0:
            return True
        self.log(f'-开始补五一回忆上传: 当前{current_process}/{target_count}，还需{remaining}张')
        success = 0
        for _ in range(remaining):
            if self.create_cloud_file('auto_mayday_', extension = 'jpg'):
                success += 1
        if success:
            self.log(f'-五一回忆上传完成: {success}张')
            self.click_task(task_id)
        refreshed_task = self.query_cloud_task(task_id, 'beiyong1')
        if not refreshed_task:
            return False
        refreshed_process = int(refreshed_task.get('process') or 0)
        if refreshed_task.get('state') == 'FINISH' or refreshed_process >= target_count:
            return True
        self.log(f'-五一回忆任务进度: {refreshed_process}/{target_count}')
        return False

    def complete_holiday_nine_grid_task(self):
        try:
            encrypted_account = self.encrypt_ai_tool_account()
        except ImportError:
            self.log('生成假期九宫格失败: 缺少加密依赖')
            return False
        template_data = self.request_json(
            'https://ad.mcloud.139.com/advertapi/adv-config/adv-config/AdInfoFilter/getAdInfos',
            headers = self.build_ai_tool_ad_headers(),
            data = {
                'account': encrypted_account,
                'adpostid': '66340',
                'channel': '10000023',
                'version': '10.5.0',
                'client': 'iphone',
            },
            method = 'POST',
        )
        if not template_data:
            self.log('生成假期九宫格失败: 模板接口无响应')
            return False
        if str(template_data.get('returnCode')) != '0':
            self.log(f"生成假期九宫格失败: {template_data.get('returnMsg', '未知错误')}")
            return False
        click_data = self.click_task(589)
        if click_data and str(click_data.get('code')) == '0':
            return True
        msg = click_data.get('msg', '未知错误') if click_data else '接口无响应'
        self.log(f'生成假期九宫格失败: {msg}')
        return False

    def get_cloud_tasklist_v2(self):
        for group, title in self.get_cloud_task_groups():
            return_data = self.request_market_json(f'{self.market_base_url}/market/signin/task/taskListV2', data = {
                'marketname': 'sign_in_3',
                'clientVersion': self.client_version,
                'group': group,
            }, method = 'POST')
            if not return_data:
                self.log(f'获取任务列表失败: {group}')
                continue
            if return_data.get('code') != 0:
                self.log(f"获取任务列表失败: {group} {return_data.get('msg', '未知错误')}")
                continue
            tasks = return_data.get('result', {}).get(group, [])
            if not tasks:
                continue
            self.log(title)
            for task in tasks:
                self.handle_cloud_v2_task(group, task)
        self.cleanup_uploaded_files()

    def handle_cloud_v2_task(self, group, task):
        task_id = task.get('id')
        task_name = self.strip_task_name(task)
        task_status = task.get('state', '')
        if task_status == 'FINISH':
            self.log(f'-已完成: {task_name}')
            return
        if group == 'day' and task_id == 106:
            self.log(f'-去完成: {task_name}')
            self.do_task(task_id, task_type = 'day', app_type = 'cloud_app')
            return
        if task_id == 522:
            self.log(f'-去完成: {task_name}')
            if self.complete_monthly_upload_task(task):
                self.log(f'-已完成: {task_name}')
                return
            refreshed_task = self.query_cloud_task(task_id, group) or task
            self.log(f'-需手动完成: {task_name}{self.get_task_progress(refreshed_task)}')
            return
        if task_id == 434:
            self.log(f'-去完成: {task_name}')
            refreshed_task = self.complete_share_file_task(task)
            if refreshed_task:
                refreshed_name = self.strip_task_name(refreshed_task)
                if refreshed_task.get('state') == 'FINISH':
                    self.log(f'-已完成: {refreshed_name}')
                    return
                self.log(f'-分享成功: {refreshed_name}{self.get_task_progress(refreshed_task)}')
                return
            self.log(f'-需手动完成: {task_name}{self.get_task_progress(task)}')
            return
        if task_id == 585:
            self.log(f'-去完成: {task_name}')
            if 'click' in self.get_task_step_types(task) and int(task.get('currstep') or 0) == 0:
                click_data = self.click_task(task_id)
                if not click_data or click_data.get('code') != 0:
                    msg = click_data.get('msg', '未知错误') if click_data else '接口无响应'
                    self.log(f'-任务登记失败: {task_name} {msg}')
                    return
            if self.complete_ai_camera_task():
                refreshed_task = self.query_cloud_task(task_id, group) or task
                refreshed_name = self.strip_task_name(refreshed_task)
                if refreshed_task.get('state') == 'FINISH':
                    self.log(f'-已完成: {refreshed_name}')
                else:
                    self.log(f'-AI相机已体验: {refreshed_name}{self.get_task_progress(refreshed_task)}')
                return
            refreshed_task = self.query_cloud_task(task_id, group) or task
            self.log(f'-需手动完成: {task_name}{self.get_task_progress(refreshed_task)}')
            return
        if task_id == 587:
            self.log(f'-去完成: {task_name}')
            if 'click' in self.get_task_step_types(task) and int(task.get('currstep') or 0) == 0:
                click_data = self.click_task(task_id)
                if not click_data or click_data.get('code') != 0:
                    msg = click_data.get('msg', '未知错误') if click_data else '接口无响应'
                    self.log(f'-任务登记失败: {task_name} {msg}')
                    return
            if self.complete_mayday_memory_task(task):
                refreshed_task = self.query_cloud_task(task_id, group) or task
                refreshed_name = self.strip_task_name(refreshed_task)
                if refreshed_task.get('state') == 'FINISH':
                    self.log(f'-已完成: {refreshed_name}')
                else:
                    self.log(f'-五一回忆已上传: {refreshed_name}{self.get_task_progress(refreshed_task)}')
                return
            refreshed_task = self.query_cloud_task(task_id, group) or task
            self.log(f'-需手动完成: {task_name}{self.get_task_progress(refreshed_task)}')
            return
        if task_id == 588:
            self.log(f'-去完成: {task_name}')
            if 'click' in self.get_task_step_types(task) and int(task.get('currstep') or 0) == 0:
                click_data = self.click_task(task_id)
                if not click_data or click_data.get('code') != 0:
                    msg = click_data.get('msg', '未知错误') if click_data else '接口无响应'
                    self.log(f'-任务登记失败: {task_name} {msg}')
                    return
            if self.complete_travel_guide_ai_task():
                refreshed_task = self.query_cloud_task(task_id, group) or task
                refreshed_name = self.strip_task_name(refreshed_task)
                if refreshed_task.get('state') == 'FINISH':
                    self.log(f'-已完成: {refreshed_name}')
                else:
                    self.log(f'-出行攻略已生成: {refreshed_name}{self.get_task_progress(refreshed_task)}')
                return
            refreshed_task = self.query_cloud_task(task_id, group) or task
            self.log(f'-需手动完成: {task_name}{self.get_task_progress(refreshed_task)}')
            return
        if task_id == 589:
            self.log(f'-去完成: {task_name}')
            if 'click' in self.get_task_step_types(task) and int(task.get('currstep') or 0) == 0:
                click_data = self.click_task(task_id)
                if not click_data or click_data.get('code') != 0:
                    msg = click_data.get('msg', '未知错误') if click_data else '接口无响应'
                    self.log(f'-任务登记失败: {task_name} {msg}')
                    return
            if self.complete_holiday_nine_grid_task():
                refreshed_task = self.query_cloud_task(task_id, group) or task
                refreshed_name = self.strip_task_name(refreshed_task)
                if refreshed_task.get('state') == 'FINISH':
                    self.log(f'-已完成: {refreshed_name}')
                else:
                    self.log(f'-假期九宫格已生成: {refreshed_name}{self.get_task_progress(refreshed_task)}')
                return
            refreshed_task = self.query_cloud_task(task_id, group) or task
            self.log(f'-需手动完成: {task_name}{self.get_task_progress(refreshed_task)}')
            return
        if group == 'beiyong1':
            self.log(f'-需手动完成: {task_name}{self.get_task_progress(task)}')
            return
        if task_id == 406:
            self.complete_notice_task(task_name)
            return
        task_keys = self.get_task_click_keys(task)
        if task_keys:
            self.log(f'-去完成: {task_name}')
            for task_key in task_keys:
                click_data = self.click_task(task_id, task_key)
                if click_data and click_data.get('code') == 0:
                    continue
                msg = click_data.get('msg', '未知错误') if click_data else '接口无响应'
                self.log(f'-任务登记失败: {task_name} {msg}')
                return
            self.log(f'-已登记任务: {task_name}')
            return
        self.log(f'-需手动完成: {task_name}{self.get_task_progress(task)}')


    def sleep(self, min_delay=1, max_delay=1.5):
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)


    def query_spec_token(self, source_id):
        sso_url = 'https://orches.yun.139.com/orchestration/auth-rebuild/token/v1.0/querySpecToken'
        sso_headers = {
            'Authorization': self.Authorization,
            'User-Agent': ua,
            'Content-Type': 'application/json',
            'Accept': '*/*',
            'Host': 'orches.yun.139.com'
        }
        sso_payload = {"account": self.account, "toSourceId": source_id}
        sso_data = self.request_json(sso_url, headers = sso_headers, data = sso_payload, method = 'POST')
        if not sso_data:
            self.log('刷新Token失败: 接口无响应')
            return None
        if sso_data.get('success'):
            return sso_data.get('data', {}).get('token')
        self.log(f"刷新Token失败: {sso_data.get('message', '未知错误')}")
        return None

    def sso(self):
        refresh_token = self.query_spec_token('001005')
        if refresh_token:
            self.sso_token = refresh_token
            return refresh_token
        else:
            return None

    def jwt(self):
        token = self.sso()
        if token is None:
            self.log('-尝试强制刷新Authorization后重试')
            self.refresh_authorization_token(force = True)
            token = self.sso()
        if token is not None:
            jwt_url = f"https://caiyun.feixin.10086.cn:7071/portal/auth/tyrzLogin.action?ssoToken={token}"
            jwt_data = self.request_json(jwt_url, headers = self.jwtHeaders, method = 'POST')
            if not jwt_data:
                self.log('JWT获取失败: 接口无响应')
                return False
            if jwt_data['code'] != 0:
                self.log('-尝试强制刷新Authorization后重新获取JWT')
                self.refresh_authorization_token(force = True)
                token = self.sso()
                if token is None:
                    self.log('-ck可能失效了')
                    return False
                jwt_url = f"https://caiyun.feixin.10086.cn:7071/portal/auth/tyrzLogin.action?ssoToken={token}"
                jwt_data = self.request_json(jwt_url, headers = self.jwtHeaders, method = 'POST')
                if not jwt_data:
                    self.log('JWT获取失败: 接口无响应')
                    return False
            if jwt_data['code'] != 0:
                self.log(f"JWT获取失败: {jwt_data['msg']}")
                return False
            jwt_token = jwt_data['result']['token']
            self.jwtHeaders['jwtToken'] = jwt_token
            self.cookies['jwtToken'] = jwt_token
            self.build_market_context(jwt_token)
            self.save_authorization_record(token = self.Authorization, user_domain_id = self.user_domain_id)
            return True
        else:
            self.log('-ck可能失效了')
            return False

    @catch_errors
    def signin_status(self):
        self.sleep()
        self.prepare_signin_center_session()
        check_url = f'{self.market_base_url}/market/signin/page/infoV3'
        check_data = self.request_market_json(check_url, params = {'client': 'app'})
        if not check_data:
            self.log('查询签到失败: 接口无响应')
            return
        if check_data.get('code') != 0:
            self.log(f"查询签到失败: {check_data.get('msg', '未知错误')}")
            return
        if self.get_today_sign_state(check_data.get('result', {})):
            self.log('✅已签到')
            return
        signin_data = self.request_market_json(f'{self.market_base_url}/market/signin/page/startSignIn',
                                               params = {'client': 'app'})
        if not signin_data:
            self.log('签到失败: 接口无响应')
            return
        if signin_data.get('code') == 0 and self.get_today_sign_state(signin_data.get('result', {})):
            self.log('✅签到成功')
            return
        latest_data = self.request_market_json(check_url, params = {'client': 'app'})
        if latest_data and latest_data.get('code') == 0 and self.get_today_sign_state(latest_data.get('result', {})):
            self.log('✅签到成功')
            return
        self.log(f"签到失败: {signin_data.get('msg', '未知错误')}")
        if signin_data.get('code') in (614, 615) and not get_env_device_id() and not get_device_id(self.account):
            self.log('-当前账号在 ydyp_device_ids.json 中尚未填写 deviceId，请抓包后手动补充')

    def click(self):
        successful_click = 0

        try:
            for _ in range(self.click_num):
                return_data = self.click_task(319) or {}
                time.sleep(0.2)

                if 'result' in return_data:
                    self.log(f'✅戳一戳: {return_data["result"]}')
                    successful_click += 1

            if successful_click == 0:
                print(f'❌戳一戳: 未获得 x {self.click_num}')
        except Exception as e:
            print(f'错误信息:{e}')


    @catch_errors
    def refresh_notetoken(self):
        note_url = 'http://mnote.caiyun.feixin.10086.cn/noteServer/api/authTokenRefresh.do'
        note_payload = {
            "authToken": self.auth_token,
            "userPhone": self.account
        }
        note_headers = {
            'X-Tingyun-Id': 'p35OnrDoP8k;c=2;r=1122634489;u=43ee994e8c3a6057970124db00b2442c::8B3D3F05462B6E4C',
            'Charset': 'UTF-8',
            'Connection': 'Keep-Alive',
            'User-Agent': 'mobile',
            'APP_CP': 'ios',
            'CP_VERSION': '3.2.0',
            'x-huawei-channelsrc': '10001400',
            'Host': 'mnote.caiyun.feixin.10086.cn',
            'Content-Type': 'application/json; charset=UTF-8',
            'Accept-Encoding': 'gzip'
        }

        try:
            response = self.send_request(note_url, headers = note_headers, data = note_payload, method = "POST")
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print('出错了:', e)
            return

        self.note_token = response.headers.get('NOTE_TOKEN')
        self.note_auth = response.headers.get('APP_AUTH')


    def get_tasklist(self, url, app_type):
        if url == 'sign_in_3' and app_type == 'cloud_app':
            self.get_cloud_tasklist_v2()
            return
        url = f'https://caiyun.feixin.10086.cn/market/signin/task/taskList?marketname={url}'
        return_data = self.send_request(url, headers = self.jwtHeaders, cookies = self.cookies).json()
        self.sleep()
        task_list = return_data.get('result', {})

        try:
            for task_type, tasks in task_list.items():
                if task_type in ["new", "hidden", "hiddenabc"]:
                    continue
                if app_type == 'cloud_app':
                    if task_type == "month":
                        self.log('\n📆 云盘每月任务')
                        for month in tasks:
                            task_id = month.get('id')
                            if task_id in [110, 113, 417, 409]:
                                continue
                            task_name = re.sub(r'<[^>]+>', '', month.get('name', ''))
                            task_status = month.get('state', '')

                            if task_status == 'FINISH':
                                self.log(f'-已完成: {task_name}')
                                continue
                            self.log(f'-去完成: {task_name}')
                            self.do_task(task_id, task_type = 'month', app_type = 'cloud_app')
                            time.sleep(2)
                    elif task_type == "day":
                        self.log('\n📆 云盘每日任务')
                        for day in tasks:
                            task_id = day.get('id')
                            if task_id == 404:
                                continue
                            task_name = re.sub(r'<[^>]+>', '', day.get('name', ''))
                            task_status = day.get('state', '')

                            if task_status == 'FINISH':
                                self.log(f'-已完成: {task_name}')
                                continue
                            self.log(f'-去完成: {task_name}')
                            self.do_task(task_id, task_type = 'day', app_type = 'cloud_app')
                elif app_type == 'email_app':
                    if task_type == "month":
                        self.log('\n📆 139邮箱每月任务')
                        for month in tasks:
                            task_id = month.get('id')
                            task_name = re.sub(r'<[^>]+>', '', month.get('name', ''))
                            task_status = month.get('state', '')
                            if task_id in [1004, 1005, 1015, 1020]:
                                continue

                            if task_status == 'FINISH':
                                self.log(f'-已完成: {task_name}')
                                continue
                            self.log(f'-去完成: {task_name}')
                            self.do_task(task_id, task_type = 'month', app_type = 'email_app')
                            time.sleep(2)
        except Exception as e:
            self.log(f'获取任务列表错误:{e}')


    @catch_errors
    def do_task(self, task_id, task_type, app_type):
        self.sleep()
        if app_type == 'cloud_app':
            self.click_task(task_id)
        else:
            task_url = f'https://caiyun.feixin.10086.cn/market/signin/task/click?key=task&id={task_id}'
            self.send_request(task_url, headers = self.jwtHeaders, cookies = self.cookies)

        if app_type == 'cloud_app':
            if task_type == 'day':
                if task_id == 106:
                    self.log('-开始上传文件，默认0kb')
                    self.updata_file()
                elif task_id == 107:
                    self.refresh_notetoken()
                    print('-获取默认笔记id')
                    note_url = 'http://mnote.caiyun.feixin.10086.cn/noteServer/api/syncNotebookV3.do'
                    headers = {
                        'X-Tingyun-Id': 'p35OnrDoP8k;c=2;r=1122634489;u=43ee994e8c3a6057970124db00b2442c::8B3D3F05462B6E4C',
                        'Charset': 'UTF-8',
                        'Connection': 'Keep-Alive',
                        'User-Agent': 'mobile',
                        'APP_CP': 'ios',
                        'CP_VERSION': '3.2.0',
                        'x-huawei-channelsrc': '10001400',
                        'APP_NUMBER': self.account,
                        'APP_AUTH': self.note_auth,
                        'NOTE_TOKEN': self.note_token,
                        'Host': 'mnote.caiyun.feixin.10086.cn',
                        'Content-Type': 'application/json; charset=UTF-8',
                        'Accept': '*/*'
                    }
                    payload = {
                        "addNotebooks": [],
                        "delNotebooks": [],
                        "notebookRefs": [],
                        "updateNotebooks": []
                    }
                    return_data = self.send_request(url = note_url, headers = headers, data = payload,
                                                    method = 'POST').json()
                    if return_data is None:
                        return print('出错了')
                    self.notebook_id = return_data['notebooks'][0]['notebookId']
                    print('开始创建笔记')
                    self.create_note(headers)



    @catch_errors
    def updata_file(self):
        upload_info = self.create_cloud_file('auto_upload_')
        if not upload_info:
            self.log('-上传失败: 接口无响应')
            return
        self.log(f"-上传文件成功，文件名: {upload_info.get('fileName', '')}")
        self.cleanup_uploaded_files(upload_info)


    def create_note(self, headers):
        note_id = self.get_note_id(32)
        createtime = str(int(round(time.time() * 1000)))
        time.sleep(3)
        updatetime = str(int(round(time.time() * 1000)))
        note_url = 'http://mnote.caiyun.feixin.10086.cn/noteServer/api/createNote.do'
        payload = {
            "archived": 0,
            "attachmentdir": note_id,
            "attachmentdirid": "",
            "attachments": [],
            "audioInfo": {
                "audioDuration": 0,
                "audioSize": 0,
                "audioStatus": 0
            },
            "contentid": "",
            "contents": [{
                "contentid": 0,
                "data": "<font size=\"3\">000000</font>",
                "noteId": note_id,
                "sortOrder": 0,
                "type": "RICHTEXT"
            }],
            "cp": "",
            "createtime": createtime,
            "description": "ios",
            "expands": {
                "noteType": 0
            },
            "latlng": "",
            "location": "",
            "noteid": note_id,
            "notestatus": 0,
            "remindtime": "",
            "remindtype": 1,
            "revision": "1",
            "sharecount": "0",
            "sharestatus": "0",
            "system": "mobile",
            "tags": [{
                "id": self.notebook_id,
                "orderIndex": "0",
                "text": "默认笔记本"
            }],
            "title": "00000",
            "topmost": "0",
            "updatetime": updatetime,
            "userphone": self.account,
            "version": "1.00",
            "visitTime": ""
        }
        create_note_data = self.send_request(note_url, headers = headers, data = payload, method = "POST")
        if create_note_data.status_code == 200:
            self.log('-创建笔记成功')
        else:
            self.log('-创建失败')


    def get_note_id(self, length):
        characters = '19f3a063d67e4694ca63a4227ec9a94a19088404f9a28084e3e486b928039a299bf756ebc77aa4f6bfa250308ec6a8be8b63b5271a00350d136d117b8a72f39c5bd15cdfd350cba4271dc797f15412d9f269e666aea5039f5049d00739b320bb9e8585a008b52c1cbd86970cae9476446f3e41871de8d9f6112db94b05e5dc7ea0a942a9daf145ac8e487d3d5cba7cea145680efc64794d43dd15c5062b81e1cda7bf278b9bc4e1b8955846e6bc4b6a61c28f831f81b2270289e5a8a677c3141ddc9868129060c0c3b5ef507fbd46c004f6de346332ef7f05c0094215eae1217ee7c13c8dca6d174cfb49c716dd42903bb4b02d823b5f1ff93c3f88768251b56cc'
        note_id = ''.join(random.choice(characters) for _ in range(length))
        return note_id


    @catch_errors
    def wxsign(self):
        self.sleep()
        url = 'https://caiyun.feixin.10086.cn/market/playoffic/followSignInfo?isWx=true'
        return_data = self.send_request(url, headers = self.jwtHeaders, cookies = self.cookies).json()

        if return_data['msg'] != 'success':
            return self.log(return_data['msg'])
        if not return_data['result'].get('todaySignIn'):
            return self.log('❌签到失败,可能未绑定公众号')
        return self.log('✅公众号签到成功')

    def shake(self):
        url = "https://caiyun.feixin.10086.cn:7071/market/shake-server/shake/shakeIt?flag=1"
        successful_shakes = 0

        try:
            for _ in range(self.click_num):
                return_data = self.send_request(url = url, cookies = self.cookies, headers = self.jwtHeaders,
                                                method = 'POST').json()
                time.sleep(1)
                shake_prize_config = return_data["result"].get("shakePrizeconfig")

                if shake_prize_config:
                    self.log(f"🎉摇一摇获得: {shake_prize_config['name']}")
                    successful_shakes += 1
        except Exception as e:
            print(f'错误信息: {e}')
        if successful_shakes == 0:
            print(f'❌未摇中 x {self.click_num}')


    @catch_errors
    def surplus_num(self):
        self.sleep()
        draw_info_url = 'https://caiyun.feixin.10086.cn/market/playoffic/drawInfo'
        draw_url = "https://caiyun.feixin.10086.cn/market/playoffic/draw"

        draw_info_data = self.send_request(draw_info_url, headers = self.jwtHeaders).json()

        if draw_info_data.get('msg') == 'success':
            remain_num = draw_info_data['result'].get('surplusNumber', 0)
            self.log(f'剩余抽奖次数{remain_num}')
            if remain_num > 50 - self.draw:
                for _ in range(self.draw):
                    self.sleep()
                    draw_data = self.send_request(url = draw_url, headers = self.jwtHeaders).json()

                    if draw_data.get("code") == 0:
                        prize_name = draw_data["result"].get("prizeName", "")
                        self.log("✅抽奖成功，获得:" + prize_name)
                    else:
                        print("❌抽奖失败")

        else:
            self.log(f"抽奖查询失败: {draw_info_data.get('msg')}")


    @catch_errors
    def do_fruit_task(self, task_name, task_id, water_num):
        self.log(f'-去完成: {task_name}')
        do_task_url = f'{self.fruit_url}task/doTask.do?taskId={task_id}'
        do_task_data = self.send_request(do_task_url, headers = self.treeHeaders).json()

        if do_task_data.get('success'):
            get_water_url = f'{self.fruit_url}task/givenWater.do?taskId={task_id}'
            get_water_data = self.send_request(get_water_url, headers = self.treeHeaders).json()

            if get_water_data.get('success'):
                self.log(f'-已完成任务获得水滴: {water_num}')
            else:
                self.log(f'❌领取失败: {get_water_data.get("msg", "")}')
        else:
            self.log(f'❌参与任务失败: {do_task_data.get("msg", "")}')


    @catch_errors
    def cloud_game(self):
        game_info_url = 'https://caiyun.feixin.10086.cn/market/signin/hecheng1T/info?op=info'
        bigin_url = 'https://caiyun.feixin.10086.cn/market/signin/hecheng1T/beinvite'
        end_url = 'https://caiyun.feixin.10086.cn/market/signin/hecheng1T/finish?flag=true'

        game_info_data = self.send_request(game_info_url, headers = self.jwtHeaders, cookies = self.cookies).json()
        if game_info_data and game_info_data.get('code', -1) == 0:
            currnum = game_info_data.get('result', {}).get('info', {}).get('curr', 0)
            count = game_info_data.get('result', {}).get('history', {}).get('0', {}).get('count', '')
            rank = game_info_data.get('result', {}).get('history', {}).get('0', {}).get('rank', '')

            self.log(f'今日剩余游戏次数: {currnum} 合成次数: {count}')

            for _ in range(currnum):
                self.send_request(bigin_url, headers = self.jwtHeaders, cookies = self.cookies).json()
                print('-开始游戏,等待10-15秒完成游戏')
                time.sleep(random.randint(10, 15))
                end_data = self.send_request(end_url, headers = self.jwtHeaders, cookies = self.cookies).json()
                if end_data and end_data.get('code', -1) == 0:
                    self.log('游戏成功')
        else:
            print("-获取游戏信息失败")

    @catch_errors
    def receive(self):
        prize_url = f"https://caiyun.feixin.10086.cn/market/prizeApi/checkPrize/getUserPrizeLogPage?currPage=1&pageSize=15&_={self.timestamp}"
        self.prepare_signin_center_session(for_receive = True)
        info_data = self.request_market_json(f'{self.market_base_url}/market/signin/page/infoV3',
                                             params = {'client': 'app'})
        if not info_data:
            self.log('查询云朵失败: 接口无响应')
            return
        if info_data.get('code') != 0:
            self.log(f"查询云朵失败: {info_data.get('msg', '未知错误')}")
            return
        info_result = info_data.get('result', {})
        pending_amount = info_result.get('toReceive', 0)
        total_amount = info_result.get('total', '')
        if pending_amount:
            receive_headers = self.build_receive_headers()
            receive_cookies = dict(self.market_cookies)
            receive_data = self.request_json(f'{self.market_base_url}/market/signin/page/receiveV2',
                                             params = {'client': 'app'},
                                             headers = receive_headers,
                                             cookies = receive_cookies)
            if not receive_data:
                self.log('领取云朵失败: 接口无响应')
                self.log(f'-当前待领取:{pending_amount}云朵')
            elif receive_data.get('code') == 0:
                receive_result = receive_data.get('result', {})
                self.log(f'-领取云朵:{receive_result.get("receive", pending_amount)}云朵')
                total_amount = receive_result.get('total', total_amount)
            else:
                latest_info_data = self.request_market_json(f'{self.market_base_url}/market/signin/page/infoV3',
                                                            params = {'client': 'app'})
                latest_result = latest_info_data.get('result', {}) if latest_info_data and latest_info_data.get('code') == 0 else {}
                latest_pending = latest_result.get('toReceive', pending_amount)
                latest_total = latest_result.get('total', total_amount)
                pending_delta = pending_amount - latest_pending if isinstance(pending_amount, int) and isinstance(latest_pending, int) else 0
                total_delta = latest_total - total_amount if isinstance(total_amount, int) and isinstance(latest_total, int) else 0
                claimed_amount = total_delta or pending_delta or (pending_amount if latest_pending == 0 else 0)
                if claimed_amount > 0:
                    self.log(f'-领取云朵:{claimed_amount}云朵')
                    total_amount = latest_total
                else:
                    self.log(f"领取云朵失败: {receive_data.get('msg', '未知错误')}")
                    if receive_data.get('code') in (614, 615) and not get_env_device_id() and not get_device_id(self.account):
                        self.log('-当前账号在 ydyp_device_ids.json 中尚未填写 deviceId，请抓包后手动补充')
                    self.log(f'-当前待领取:{pending_amount}云朵')
        else:
            self.log('-当前待领取:0云朵')
        self.sleep()
        prize_data = self.request_json(prize_url, headers = self.jwtHeaders, cookies = self.cookies) or {}
        result = prize_data.get('result', {}).get('result') or []
        rewards = ''
        for value in result:
            if value.get('flag') == 1:
                rewards += f'待领取奖品: {value.get("prizeName")}\n'
        self.log(f'-当前云朵数量:{total_amount}云朵')
        if rewards:
            self.log(rewards)
        global user_amount
        user_amount += f'用户【{self.encrypt_account}】:{total_amount}云朵\n'


    @catch_errors
    def backup_cloud(self):
        backup_url = 'https://caiyun.feixin.10086.cn/market/backupgift/info'
        backup_data = self.send_request(backup_url, headers = self.jwtHeaders).json()
        state = backup_data.get('result', {}).get('state', '')
        if state == -1:
            self.log('本月未备份,暂无连续备份奖励')

        elif state == 0:
            self.log('-领取本月连续备份奖励')
            cur_url = 'https://caiyun.feixin.10086.cn/market/backupgift/receive'
            cur_data = self.send_request(cur_url, headers = self.jwtHeaders).json()
            self.log(f'-获得云朵数量:{cur_data.get("result").get("result")}')

        elif state == 1:
            print('-已领取本月连续备份奖励')
        self.sleep()
        expend_url = 'https://caiyun.feixin.10086.cn/market/signin/page/taskExpansion'
        expend_data = self.send_request(expend_url, headers = self.jwtHeaders, cookies = self.cookies).json()
        curMonthBackup = expend_data.get('result', {}).get('curMonthBackup', '')
        preMonthBackup = expend_data.get('result', {}).get('preMonthBackup', '')
        curMonthBackupTaskAccept = expend_data.get('result', {}).get('curMonthBackupTaskAccept', '')
        nextMonthTaskRecordCount = expend_data.get('result', {}).get('nextMonthTaskRecordCount', '')
        acceptDate = expend_data.get('result', {}).get('acceptDate', '')

        if curMonthBackup:
            self.log(f'- 本月已备份，下月可领取膨胀云朵: {nextMonthTaskRecordCount}')
        else:
            self.log('- 本月还未备份，下月暂无膨胀云朵')

        if preMonthBackup:
            if curMonthBackupTaskAccept:
                print('- 上月已备份，膨胀云朵已领取')
            else:

                receive_url = f'https://caiyun.feixin.10086.cn/market/signin/page/receiveTaskExpansion?acceptDate={acceptDate}'
                receive_data = self.send_request(receive_url, headers = self.jwtHeaders,
                                                 cookies = self.cookies).json()
                if receive_data.get("code") != 0:
                    self.log(f'-领取失败:{receive_data.get("msg")}')
                else:
                    cloudCount = receive_data.get('result', {}).get('cloudCount', '')
                    self.log(f'- 膨胀云朵领取成功: {cloudCount}朵')
        else:
            print('-上月未备份，本月无膨胀云朵领取')

    @catch_errors
    def complete_notice_task(self, task_name):
        notice_status = self.get_notice_status()
        if not notice_status:
            self.log(f'-需手动完成: {task_name}')
            return
        push_on = int(notice_status.get('pushOn') or 0)
        first_status = int(notice_status.get('firstTaskStatus') or 0)
        second_status = int(notice_status.get('secondTaskStatus') or 0)
        on_duration = int(notice_status.get('onDuaration') or 0)
        total = int(notice_status.get('total') or 31)
        if push_on != 1:
            self.log(f'-需手动完成: {task_name} (通知未开启)')
            return
        reward_url = 'https://caiyun.feixin.10086.cn/market/msgPushOn/task/obtain'
        if first_status != 3:
            reward1_data = self.request_json(reward_url, headers = self.jwtHeaders, data = {"type": 1}, method = 'POST')
            if reward1_data and reward1_data.get('code') == 0:
                self.log(f'-已领取: {task_name} (首日奖励)')
            else:
                self.log(f'-待领取: {task_name} (首日奖励)')
        if second_status == 2:
            reward2_data = self.request_json(reward_url, headers = self.jwtHeaders, data = {"type": 2}, method = 'POST')
            if reward2_data and reward2_data.get('code') == 0:
                self.log(f'-已领取: {task_name} (连续奖励，已开启{on_duration}/{total}天)')
            else:
                self.log(f'-待领取: {task_name} (已开启{on_duration}/{total}天)')
        elif second_status == 3:
            self.log(f'-已完成: {task_name}')
        else:
            self.log(f'-进行中: {task_name} (已开启{on_duration}/{total}天)')


if __name__ == "__main__":
    env_name = 'ydyp'
    token = os.getenv(env_name)
    if not token:
        print(f'⛔️未获取到ck变量：请检查变量 {env_name} 是否填写')
        exit(0)

    cookies = re.split(r'[&]', token)
    print_startup_info(len(cookies))
    print_device_id_notice()
    print_storage_path_notice()

    for i, account_info in enumerate(cookies, start=1):
        print(f"\n======== ▷ 第 {i} 个账号 ◁ ========")
        yp_instance = YP(account_info)
    
        if not yp_instance.Authorization:
            print(f"⛔️ 账号 {i} 无效，跳过执行")
            continue
    
        yp_instance.run()
        print("\n准备进行下一个账号")
        time.sleep(random.randint(1, 3))



    msg = ""
    if err_accounts:
        msg += f"失效账号:\n{err_accounts}\n"
    
    msg += f"任务详情:\n{all_logs}\n"
    msg += f"云朵汇总:\n{user_amount}"
    

    print("\n================ 运行总结 ================")
    if err_accounts:
        print(f"❌ 失效账号:\n{err_accounts}")
    if user_amount:
        print(f"☁️ 云朵汇总:\n{user_amount}")
    

    msg = msg.replace('-', ' ').replace('.', ' ').replace('!', '！').replace('(', '（').replace(')', '）')
    msg = msg.replace('_', ' ').replace('=', ' ').replace('~', ' ').replace('{', ' ').replace('}', ' ').replace('|', ' ')
        
    send = load_send()

    if send:
        send('中国移动云盘任务信息', msg)

# -*- coding: utf-8 -*-
"""
顺丰速运+ 小程序 —— 中秋博饼集礼盒活动（MID_AUTUMN_2026）自动脚本
活动时间：2026-09-11 10:00 ~ 2026-10-08 19:00

用法：
  1. 环境变量 sfsyUrl 填账号（多账号换行分隔，支持 URL 或 Cookie 格式）
  2. 可选环境变量：
     SFBF          并发数（默认 1）
     ENABLE_PROXY  是否启用代理（默认 false）
     SF_PROXY_API_URL  代理接口地址

流程：
  进入活动页(带邀请互刷) → 每日礼包 → 【小程序 + APP 双渠道任务分别做、分别领】
  → 博饼(每日3次,失败自动重试,拿全奖励) → 博饼后补领游戏任务奖励
  → 集礼盒(消耗次数集碎片) → 开礼盒抽奖 / 周四抽奖

渠道：
  小程序(26zhongqiu07/MINI_PROGRAM) 与 APP(26zhongqiu01/SFAPP) 任务不同，默认都跑；
  SF_CHANNEL=mp 或 =app 可只跑单渠道

可选：
  SF_DRY_RUN=true    自检模式：仅查询不消耗（先用它验证账号再实跑）
  SF_VERBOSE=true    详细日志（默认精简，每个账号约10行）
  SF_SUBSCRIBE=true  开启每日礼包订阅（默认关闭，该接口常报"活动太火爆"）
  SF_INVITE_TYPE=1   邀请参数类型（中秋默认1，可试 4=端午系）
  SF_RESULT_FILE     结果文件路径（默认 sf_midautumn_results.jsonl）
"""
import hashlib
import json
import os
import random
import re
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from urllib.parse import unquote
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# 禁用SSL警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

inviteId = ['B9D26F54D0684410B133577D5F9B565D', '787450A526F644BCAEAF53D3A928B034',
            '6FB4C632AE034028A36E45D976FF40A7', '1F3180464F444406A4DE0B6F4D84E841',
            'C365C74E0B0844FB8C78656FF8375ECD', 'E5844EF6D2E34B2BB11CFABF13FDB2B4',
            'D78098B2D29A496CA447D39140C0377F', '7054A99B93194C90A0B2A9C11A9322E0',
            'FC9A7128E1AE4E419E385FF0DF91B799']

# ==================== 配置常量 ====================
PROXY_TIMEOUT = 15
MAX_PROXY_RETRIES = 5
REQUEST_RETRY_COUNT = 3
CONCURRENT_NUM = int(os.getenv('SFBF', '1'))
if CONCURRENT_NUM > 20:
    CONCURRENT_NUM = 20
elif CONCURRENT_NUM < 1:
    CONCURRENT_NUM = 1

# 代理开关（默认启用）
ENABLE_PROXY = os.getenv('ENABLE_PROXY', 'flase').lower() == 'true'

# 自检模式：仅查询不消耗（账号验证用）
DRY_RUN = os.getenv('SF_DRY_RUN', 'false').lower() == 'true'

# 详细日志模式（默认精简输出，一个账号约10行）
VERBOSE = os.getenv('SF_VERBOSE', 'false').lower() == 'true'

# 每日礼包订阅（默认关闭：该接口常返回"活动太火爆了"）
ENABLE_SUBSCRIBE = os.getenv('SF_SUBSCRIBE', 'false').lower() == 'true'

# 结果保存文件（追加，一行一个账号）
RESULT_FILE = os.getenv('SF_RESULT_FILE', 'sf_midautumn_results.jsonl')

print_lock = Lock()

# ===== 中秋博饼集礼盒活动配置 =====
ACTIVITY_CODE = "MID_AUTUMN_2026"
CHANNEL = "26zhongqiu07"          # 渠道（header 与每日礼包参数）
CHANNEL_TYPE = "MINI_PROGRAM"     # 任务/领奖渠道
CITY_CODE = "551"                 # 每日礼包城市码
TOKEN = 'wwesldfs29aniversaryvdld29'
SYS_CODE = 'MCS-MIMP-CORE'

# 邀请参数类型（不同活动取值不同：中秋默认1，可试 4=端午系）
INVITE_TYPE = int(os.getenv('SF_INVITE_TYPE', '1'))

# ===== 双渠道：小程序 + APP（活动任务按渠道区分，两边都要跑） =====
CHANNELS = [
    {'name': '小程序', 'channel': '26zhongqiu07', 'channelType': 'MINI_PROGRAM', 'platform': 'MINI_PROGRAM'},
    {'name': 'APP',    'channel': '26zhongqiu01', 'channelType': 'SFAPP',        'platform': 'SFAPP'},
]
# SF_CHANNEL=mp 或 =app 可只跑单渠道（默认双渠道都跑）
CHANNEL_FILTER = os.getenv('SF_CHANNEL', 'mp,app').lower()
CHANNELS = [c for c in CHANNELS
            if (c['channelType'] == 'MINI_PROGRAM' and 'mp' in CHANNEL_FILTER)
            or (c['channelType'] == 'SFAPP' and 'app' in CHANNEL_FILTER)]

# 每日礼包订阅码
SUBSCRIBE_CODE = "MID_AUTUMN_2026_DAILY_BAIWAN"

# 需要跳过的任务类型（需实际操作 / 外部行为）
SKIP_TASK_TYPES = [
    'SEND_SUCCESS_RECALL',              # 去寄一单快递
    'LOOK_BIG_PACKAGE_GET_CASH',        # 寄大件重货
    'OPEN_FAMILY_HOME_MUTUAL',          # 开通家庭共享账户
    'SHUNYUN_CARD',                     # 去购买顺运卡
    'CHARGE_NEW_EXPRESS_CARD',          # 一键集齐本周礼盒（充值）
    'OPEN_APP_NOTIFICATION',            # 开启APP消息推送提醒
]

# 博饼名次 → 中文（level 数字映射，防御性展示）
BOBING_RANK_CN = {
    1: '状元', 2: '榜眼', 3: '探花', 4: '进士', 5: '举人', 6: '秀才', 0: '参与奖',
}


# ==================== 日志 ====================
class Logger:
    def __init__(self, verbose: bool = False):
        self.messages: List[str] = []
        self.lock = Lock()
        self.verbose = verbose

    def _log(self, icon: str, msg: str):
        line = f"{icon} {msg}"
        with print_lock:
            print(line)
        with self.lock:
            self.messages.append(line)

    def info(self, msg): self._log('📝', msg)
    def success(self, msg): self._log('✅', msg)
    def warning(self, msg): self._log('⚠️', msg)
    def error(self, msg): self._log('❌', msg)
    def task(self, msg): self._log('🎯', msg)
    def medal(self, msg): self._log('🏅', msg)
    def dice(self, msg): self._log('🎲', msg)

    def detail(self, msg):
        """详细日志：仅 SF_VERBOSE=true 时输出"""
        if self.verbose:
            self._log('📄', msg)


# ==================== 代理管理器 ====================
class ProxyManager:
    def __init__(self, api_url: str):
        self.api_url = api_url

    def get_proxy(self) -> Optional[Dict[str, str]]:
        if not ENABLE_PROXY:
            return None
        try:
            if not self.api_url:
                return None
            response = requests.get(self.api_url, timeout=10)
            if response.status_code == 200:
                try:
                    data = response.json()
                    if 'data' in data and 'list' in data['data'] and data['data']['list']:
                        proxy_info = data['data']['list'][0]
                        ip = proxy_info.get('ip')
                        port = proxy_info.get('port')
                        if ip and port:
                            proxy = f'http://{ip}:{port}'
                            with print_lock:
                                print(f"✅ 获取代理: {proxy}")
                            return {'http': proxy, 'https': proxy}
                except (json.JSONDecodeError, KeyError, IndexError):
                    proxy_text = response.text.strip()
                    if ':' in proxy_text:
                        proxy = proxy_text if proxy_text.startswith('http') else f'http://{proxy_text}'
                        display = proxy
                        if '@' in proxy:
                            parts = proxy.split('@')
                            display = f"http://***:***@{parts[-1]}"
                        with print_lock:
                            print(f"✅ 获取代理: {display}")
                        return {'http': proxy, 'https': proxy}
                with print_lock:
                    print(f"❌ 获取代理失败: 无法解析代理数据")
                return None
            else:
                with print_lock:
                    print(f"❌ 获取代理失败: HTTP {response.status_code}")
                return None
        except Exception as e:
            with print_lock:
                print(f"❌ 获取代理异常: {str(e)[:100]}")
            return None


# ==================== HTTP客户端 ====================
class SFHttpClient:
    def __init__(self, proxy_manager: ProxyManager):
        self.proxy_manager = proxy_manager
        self.session = requests.Session()
        self.session.verify = False

        if ENABLE_PROXY:
            proxy = self.proxy_manager.get_proxy()
            if proxy:
                self.session.proxies = proxy
            else:
                if self.proxy_manager.api_url:
                    print("⚠️ 代理获取失败，将不使用代理")

        self.headers = {
            'Host': 'mcs-mimp-web.sf-express.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090a13) UnifiedPCWindowsWechat(0xf254173b) XWEB/19027',
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json',
            'channel': CHANNEL,
            'platform': 'MINI_PROGRAM',
            'accept-language': 'zh-CN,zh;q=0.9',
        }

    def set_channel(self, channel: str, platform: str):
        """切换渠道请求头（小程序/APP 任务不同）"""
        self.headers['channel'] = channel
        self.headers['platform'] = platform

    def _generate_sign(self) -> Dict[str, str]:
        timestamp = str(int(round(time.time() * 1000)))
        data = f'token={TOKEN}&timestamp={timestamp}&sysCode={SYS_CODE}'
        signature = hashlib.md5(data.encode()).hexdigest()
        return {
            'syscode': SYS_CODE,
            'timestamp': timestamp,
            'signature': signature,
        }

    def request(self, url: str, data: Optional[Dict] = None, method: str = 'POST') -> Optional[Dict]:
        retry_count = 0
        max_proxy_retries = MAX_PROXY_RETRIES if ENABLE_PROXY else 1
        proxy_retry_count = 0

        while proxy_retry_count < max_proxy_retries:
            sign_data = self._generate_sign()
            headers = {**self.headers, **sign_data}

            try:
                if method == 'POST':
                    resp = self.session.post(url, headers=headers, json=data or {}, timeout=PROXY_TIMEOUT)
                else:
                    resp = self.session.get(url, headers=headers, timeout=PROXY_TIMEOUT)
                resp.raise_for_status()

                try:
                    result = resp.json()
                    if result is None:
                        retry_count += 1
                        if retry_count < REQUEST_RETRY_COUNT:
                            time.sleep(2)
                            continue
                        return None
                    return result
                except (json.JSONDecodeError, ValueError):
                    retry_count += 1
                    if retry_count < REQUEST_RETRY_COUNT:
                        time.sleep(2)
                        continue
                    return None

            except requests.exceptions.RequestException as e:
                retry_count += 1
                error_str = str(e)

                if ENABLE_PROXY and ('ProxyError' in error_str or 'SSLError' in error_str or 'ConnectionError' in error_str):
                    proxy_retry_count += 1
                    if proxy_retry_count < MAX_PROXY_RETRIES:
                        new_proxy = self.proxy_manager.get_proxy()
                        if new_proxy:
                            self.session.proxies = new_proxy
                        retry_count = 0
                    time.sleep(2)
                    continue

                if retry_count < REQUEST_RETRY_COUNT:
                    time.sleep(2)
                    continue
                return None

            except Exception:
                return None

        return None

    def login(self, url: str) -> tuple:
        """登录（兼容URL和CK格式）"""
        try:
            decoded_input = unquote(url)
            if decoded_input.startswith('sessionId=') or '_login_mobile_=' in decoded_input:
                cookie_dict = {}
                for item in decoded_input.split(';'):
                    item = item.strip()
                    if '=' in item:
                        k, v = item.split('=', 1)
                        cookie_dict[k] = v
                for k, v in cookie_dict.items():
                    self.session.cookies.set(k, v, domain='mcs-mimp-web.sf-express.com')
                user_id = cookie_dict.get('_login_user_id_', '')
                phone = cookie_dict.get('_login_mobile_', '')
                return (True, user_id, phone) if phone else (False, '', '')
            else:
                self.session.get(unquote(url), headers=self.headers, timeout=PROXY_TIMEOUT)
                cookies = self.session.cookies.get_dict()
                user_id = cookies.get('_login_user_id_', '')
                phone = cookies.get('_login_mobile_', '')
                return (True, user_id, phone) if phone else (False, '', '')
        except Exception as e:
            print(f'登录异常: {str(e)}')
            return False, '', ''


# ==================== 中秋博饼集礼盒活动执行器 ====================
class MidAutumnExecutor:
    def __init__(self, http: SFHttpClient, logger: Logger, user_id: str, dry_run: bool = False, inviter_id: str = ''):
        self.http = http
        self.logger = logger
        self.user_id = user_id
        self.dry_run = dry_run
        self.inviter_id = inviter_id
        # 当前渠道状态（默认小程序；双渠道任务阶段会切换）
        self.channel = CHANNEL
        self.channel_type = CHANNEL_TYPE
        self.channel_name = '小程序'
        self.channel_key = 'mp'

    def _use_channel(self, cfg: Dict) -> None:
        """切换渠道：请求头 + 任务/领奖参数 + 统计键"""
        self.channel = cfg['channel']
        self.channel_type = cfg['channelType']
        self.channel_name = cfg['name']
        self.channel_key = 'mp' if cfg['channelType'] == 'MINI_PROGRAM' else 'app'
        self.http.set_channel(cfg['channel'], cfg['platform'])

    def _count_task(self, result: Dict) -> None:
        """任务计数：总计 + 当前渠道计数"""
        result['tasks_completed'] = result.get('tasks_completed', 0) + 1
        result[f'tasks_{self.channel_key}'] = result.get(f'tasks_{self.channel_key}', 0) + 1

    # ---------- 通用请求封装 ----------
    def _post(self, url: str, data: Optional[Dict] = None) -> Optional[Dict]:
        resp = self.http.request(url, data=data or {})
        if resp and resp.get('success'):
            return resp.get('obj')
        return None

    def _post_full(self, url: str, data: Optional[Dict] = None) -> Optional[Dict]:
        return self.http.request(url, data=data or {})

    @staticmethod
    def _err(resp: Optional[Dict]) -> str:
        return resp.get('errorMessage', '未知错误') if resp else '请求失败'

    def _consume(self, action: str) -> bool:
        """自检模式：消耗型操作统一跳过"""
        if self.dry_run:
            self.logger.info(f'[自检模式] 跳过消耗操作: {action}')
            return False
        return True

    # ---------- 首页 / 邀请 ----------
    def get_activity_index(self, invite_type: int = 0, invite_user_id: str = '', no_login: bool = False) -> Optional[Dict]:
        """进入活动首页；带邀请参数时注册"被邀请访问"关系（no_login 走未登录接口，用于首次访问场景）"""
        if no_login:
            url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonNoLoginPost/~memberNonactivity~midAutumn2026IndexService~index'
        else:
            url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~midAutumn2026IndexService~index'
        if invite_type > 0 and invite_user_id:
            data = {"inviteType": invite_type, "inviteUserId": invite_user_id}
        else:
            data = {}
        resp = self._post_full(url, data)
        return resp.get('obj') if resp and resp.get('success') else None

    def _pick_inviter(self) -> str:
        """选择邀请人ID：优先主程序轮转分配的账号，否则从固定邀请池随机"""
        if self.inviter_id:
            return self.inviter_id
        available_invites = [inv for inv in inviteId if inv != self.user_id]
        return random.choice(available_invites) if available_invites else ''

    def get_invite_list(self) -> Optional[List[Dict]]:
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~midAutumn2026TaskService~taskInviteList'
        resp = self._post_full(url)
        if resp and resp.get('success'):
            return resp.get('obj', [])
        return None

    # ---------- 查询类（进入页面触发） ----------
    def is_activity_subscribe(self) -> bool:
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~commonSubscribeService~isSubscribe'
        resp = self._post_full(url, {"code": SUBSCRIBE_CODE})
        if resp and resp.get('success'):
            return resp.get('obj', {}).get('subscribe', False)
        return False

    def do_subscribe(self) -> bool:
        """订阅每日礼包提醒（未订阅时补订阅）"""
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~commonSubscribeService~subscribe'
        resp = self._post_full(url, {"code": SUBSCRIBE_CODE})
        if resp and resp.get('success'):
            self.logger.success('每日礼包订阅成功')
            return True
        self.logger.warning(f'每日礼包订阅失败: {self._err(resp)}')
        return False

    def get_dilate_change(self) -> Optional[Dict]:
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~midAutumn2026DilateService~getDilateChange'
        return self._post(url)

    def get_widget_status(self) -> Optional[Dict]:
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~midAutumn2026DilateService~getWidgetStatus'
        return self._post(url)

    def get_dilate_status(self) -> Optional[Dict]:
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~midAutumn2026DilateService~getDilateStatus'
        return self._post(url)

    def get_express_activity_info(self) -> Optional[Dict]:
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~midAutumn2026ExpressService~getExpressSpecialActivityInfo'
        return self._post(url)

    def query_extra_reward_cards(self) -> Optional[List]:
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~midAutumn2026CollectService~queryExtraRewardCards'
        return self._post(url)

    def query_shunyun_recommend(self) -> Optional[Dict]:
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~midAutumn2026ShunYunCardService~queryRecommend'
        return self._post(url)

    def query_emp_gift_detail(self) -> Optional[Dict]:
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~midAutumn2026EmpGiftService~queryDetail'
        return self._post(url)

    def query_family_status(self) -> Optional[Dict]:
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~midAutumn2026FamilyService~familyStatus'
        return self._post(url)

    # ---------- 每日礼包 ----------
    def get_daily_gift_status(self) -> Optional[Dict]:
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~midAutumn2026DailyService~getDailyGiftStatus'
        data = {"cityCode": CITY_CODE, "channel": self.channel}
        resp = self._post_full(url, data)
        return resp.get('obj') if resp and resp.get('success') else None

    def receive_daily_gift(self) -> Optional[Dict]:
        if not self._consume('领取每日礼包'):
            return None
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~midAutumn2026DailyService~receiveDailyGift'
        data = {"cityCode": CITY_CODE, "channel": self.channel}
        resp = self._post_full(url, data)
        if resp and resp.get('success'):
            return resp.get('obj')
        else:
            self.logger.warning(f'领取每日礼包失败: {self._err(resp)}')
            return None

    def do_daily_gift(self, result: Dict) -> None:
        time.sleep(1)
        gift = self.get_daily_gift_status()
        if not gift:
            self.logger.warning('每日礼包: 状态获取失败')
            return
        if gift.get('received'):
            self.logger.info('每日礼包: 今日已领取')
            return
        if gift.get('canReceive'):
            time.sleep(1)
            received = self.receive_daily_gift()
            if received:
                products = received.get('dailyGiftProductList', [])
                if products:
                    names = [p.get('productName', '未知') for p in products]
                    result['daily_gift_count'] = len(names)
                    if self.logger.verbose:
                        self.logger.success('每日礼包领取成功: ' + ', '.join(names))
                    else:
                        self.logger.success(f'每日礼包: 领取成功 {len(names)} 张券（{names[0]} 等）')
                else:
                    self.logger.success('每日礼包: 领取成功')
                result['daily_gift_received'] = True
        else:
            self.logger.info('每日礼包: 暂不可领取')

    # ---------- 任务 ----------
    def get_task_list(self) -> Optional[List[Dict]]:
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~activityTaskService~taskList'
        data = {"activityCode": ACTIVITY_CODE, "channelType": self.channel_type}
        resp = self.http.request(url, data=data)
        if resp and resp.get('success'):
            return resp.get('obj', [])
        else:
            self.logger.error(f'获取任务列表失败: {self._err(resp)}')
            return None

    def get_user_rest_integral(self) -> int:
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~activityTaskService~getUserRestIntegral'
        resp = self._post_full(url)
        if resp and resp.get('success'):
            return resp.get('obj', 0)
        return 0

    def finish_task(self, task_code: str) -> bool:
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonRoutePost/memberEs/taskRecord/finishTask'
        resp = self.http.request(url, data={"taskCode": task_code})
        return bool(resp and resp.get('success'))

    def check_task(self, task_code: str) -> bool:
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonRoutePost/memberEs/taskRecord/checkTask'
        resp = self.http.request(url, data={"taskCode": task_code})
        return bool(resp and resp.get('success'))

    def integral_exchange(self) -> bool:
        """积分兑换集礼盒次数（10积分/次，每日1次）"""
        if not self._consume('积分兑换集礼盒次数'):
            return False
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~midAutumn2026TaskService~integralExchange'
        data = {"exchangeNum": 1, "activityCode": ACTIVITY_CODE}
        resp = self._post_full(url, data)
        if resp and resp.get('success'):
            self.logger.detail('积分兑换集礼盒次数成功（消耗10积分）')
            return True
        else:
            self.logger.warning(f'积分兑换失败: {self._err(resp)}')
            return False

    def receive_vip_benefit(self) -> bool:
        """领取寄件券类会员权益（专用接口）"""
        if not self._consume('领取寄件会员权益'):
            return False
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberManage~memberEquity~commonEquityReceive'
        resp = self.http.request(url, data={"key": "surprise_benefit"})
        if resp and resp.get('success'):
            self.logger.detail('[领取寄件会员权益] 完成成功')
            return True
        else:
            self.logger.warning(f'[领取寄件会员权益] 完成失败: {self._err(resp)}')
            return False

    def fetch_task_reward(self) -> Optional[Dict]:
        """领取已完成任务的奖励（给集礼盒次数）"""
        if not self._consume('领取任务奖励'):
            return None
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~midAutumn2026TaskService~fetchTaskReward'
        data = {"channelType": self.channel_type, "activityCode": ACTIVITY_CODE}
        resp = self._post_full(url, data)
        if resp and resp.get('success'):
            return resp.get('obj', {})
        else:
            self.logger.warning(f'领取任务奖励失败: {self._err(resp)}')
            return None

    def get_charge_task_reward(self) -> Optional[Dict]:
        """一键集齐本周礼盒奖励（充值任务，空body）"""
        if not self._consume('一键集齐本周礼盒奖励'):
            return None
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~midAutumn2026TaskService~getChargeTaskReward'
        resp = self._post_full(url)
        if resp and resp.get('success'):
            obj = resp.get('obj', {})
            received = obj.get('receivedAccountList', [])
            if received:
                for item in received:
                    self.logger.detail(f'一键集齐: 获得 {item.get("currency", "?")} x{item.get("amount", 0)}')
            return obj
        return None

    def _claim_task_rewards(self, result: Dict) -> None:
        """领取当前渠道已完成任务的奖励（给集礼盒次数）"""
        time.sleep(1)
        reward = self.fetch_task_reward()
        gained: List[str] = []
        if reward:
            received_list = reward.get('receivedAccountList', [])
            if received_list:
                for item in received_list:
                    gained.append(f"{item.get('currency', '?')}x{item.get('amount', 0)}")
                result['claim_rewards'] = received_list
        if gained:
            self.logger.success(f'任务奖励[{self.channel_name}]: ' + ', '.join(gained))
        elif self.logger.verbose:
            self.logger.info(f'任务奖励[{self.channel_name}]: 无')

    def do_tasks(self, result: Dict) -> None:
        """执行所有可自动完成的任务"""
        tasks = self.get_task_list()
        if tasks is None:
            return
        self.logger.detail(f'共发现 {len(tasks)} 个任务')

        done_names: List[str] = []
        for task in tasks:
            task_name = task.get('taskName', '未知')
            task_type = task.get('taskType', '')
            task_code = task.get('taskCode', '')
            status = task.get('status')
            process = task.get('process', '')
            rest_finish = task.get('restFinishTime', 0)
            virtual_token = task.get('virtualTokenNum', 0)

            # 已完成
            if status == 3 or (status == 1 and rest_finish <= 0):
                self.logger.detail(f'[{task_name}] 已完成 ({process})')
                continue

            # 邀好友任务：进度靠"被邀请人首次访问"注册（每邀1位+1，需邀满N位），只报进度不执行动作
            if task_type == 'INVITEFRIENDS_PARTAKE_ACTIVITY':
                result['invite_process'] = process
                self.logger.info(f'邀请任务: {process}（邀满{task.get("maxFinishTime", 4)}位好友首次访问，每邀1位+{virtual_token}次）')
                continue

            if task_type in SKIP_TASK_TYPES:
                self.logger.detail(f'[{task_name}] 跳过（需实际操作）')
                continue

            # 玩博饼游戏（通过博饼 draw 完成，稍后统一处理）
            if task_type == 'PLAY_ACTIVITY_GAME':
                self.logger.detail(f'[{task_name}] 通过博饼游戏完成（稍后执行）')
                continue

            # 积分兑换
            if task_type == 'INTEGRAL_EXCHANGE':
                if self.dry_run:
                    self.logger.info(f'[{task_name}] 自检模式，可自动完成')
                    continue
                if self.integral_exchange():
                    self._count_task(result)
                    done_names.append(task_name)
                continue

            # 领取寄件券类会员权益
            if task_type == 'RECEIVE_VIP_BENEFIT':
                if self.dry_run:
                    self.logger.info(f'[{task_name}] 自检模式，可自动完成')
                    continue
                if self.receive_vip_benefit():
                    self._count_task(result)
                    done_names.append(task_name)
                continue

            # 关注类任务（公众号/抖音/小红书）：账号已关注对应平台即可用 taskCode 完成
            if task_type.startswith('FOLLOW_') and task_code:
                if self.dry_run:
                    self.logger.info(f'[{task_name}] 自检模式，可自动完成')
                    continue
                ok = self.finish_task(task_code)
                if not ok:
                    ok = self.check_task(task_code) and self.finish_task(task_code)
                if ok:
                    done_names.append(task_name)
                    self._count_task(result)
                    self.logger.detail(f'[{task_name}] 完成成功，可获得 {virtual_token} 次集礼盒机会')
                else:
                    self.logger.warning(f'[{task_name}] 完成失败（需先在对应平台关注顺丰账号）')
                time.sleep(1)
                continue

            # 有 taskCode 的任务尝试自动完成（浏览类）
            if task_code:
                if self.dry_run:
                    self.logger.info(f'[{task_name}] 自检模式，可自动完成')
                    time.sleep(0.3)
                    continue
                if self.finish_task(task_code):
                    done_names.append(task_name)
                    self._count_task(result)
                    self.logger.detail(f'[{task_name}] 完成成功，可获得 {virtual_token} 次集礼盒机会')
                else:
                    self.logger.warning(f'[{task_name}] 完成失败')
                time.sleep(1)
            else:
                self.logger.detail(f'[{task_name}] 跳过（无taskCode, {task_type}）')

        # 领取任务奖励（给集礼盒次数）
        self._claim_task_rewards(result)

        if done_names:
            self.logger.success(f'任务[{self.channel_name}]: 完成 {len(done_names)} 个（' + '/'.join(done_names) + '）')
        elif self.dry_run:
            self.logger.info(f'任务[{self.channel_name}]: 自检模式，未实际执行（可自动完成的任务已在上方列出）')
        elif self.logger.verbose:
            self.logger.info(f'任务[{self.channel_name}]: 无自动可完成任务')

    # ---------- 博饼游戏 ----------
    def bobing_index(self) -> Optional[Dict]:
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~midAutumn2026BobingService~index'
        return self._post(url)

    def bobing_summary(self) -> Optional[Dict]:
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~midAutumn2026BobingService~summary'
        return self._post(url)

    def bobing_draw(self) -> Optional[Dict]:
        """博饼抽一次（失败自动重试，保证不浪费次数）"""
        if not self._consume('博饼'):
            return None
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~midAutumn2026BobingService~draw'
        for attempt in range(REQUEST_RETRY_COUNT):
            resp = self._post_full(url)
            if resp and resp.get('success'):
                return resp.get('obj')
            self.logger.warning(f'博饼失败(第{attempt+1}次): {self._err(resp)}')
            time.sleep(1)
        return None

    def do_bobing(self, result: Dict) -> None:
        """玩博饼游戏（每日免费次数）"""
        summary = self.bobing_summary()
        if not summary:
            self.logger.warning('博饼: 状态获取失败')
            return
        rest = summary.get('restCount', 0)
        daily = summary.get('dailyLimit', 0)
        self.logger.detail(f'博饼: 剩余次数 {rest}/{daily}')

        if rest <= 0:
            self.logger.info('博饼: 今日免费次数已用完')
            return

        detail = result.setdefault('bobing_detail', [])
        rank_list: List[str] = []
        for i in range(rest):
            time.sleep(1)
            draw = self.bobing_draw()
            if not draw:
                self.logger.warning(f'博饼第 {i+1} 次失败，停止')
                break

            dice_list = draw.get('dice', [])
            rank = draw.get('rank', '')
            level = draw.get('level', -1)
            keju = draw.get('keju', '')
            sub_award = draw.get('subAward', '')
            rest_count = draw.get('restCount', 0)

            rank_cn = keju or sub_award or BOBING_RANK_CN.get(level, '') or rank

            # 收集本次奖励名（兼容多种返回字段，确保不漏领）
            rewards: List[str] = []
            for key in ('productList', 'productDTOList', 'couponList', 'giftList', 'awardList'):
                for p in draw.get(key, []) or []:
                    rewards.append(p.get('productName') or p.get('couponName') or p.get('giftBagName') or '未知')
            if not rewards:
                for acc in draw.get('receivedAccountList', []) or []:
                    rewards.append(f"{acc.get('currency', '?')}x{acc.get('amount', 0)}")

            if self.logger.verbose:
                line = f'第 {i+1} 次: 骰子 {dice_list} → {rank_cn}'
                if rewards:
                    line += '，获得: ' + ', '.join(rewards)
                else:
                    line += '（+1次集礼盒）'
                self.logger.dice(line)

            rank_list.append(rank_cn + (f'[{",".join(rewards)}]' if rewards else ''))
            result['bobing_count'] = result.get('bobing_count', 0) + 1
            detail.append({
                'index': i + 1,
                'dice': dice_list,
                'rank': rank_cn,
                'rewards': rewards,
                'rest_count': rest_count,
            })

            if rest_count <= 0:
                break

        self.logger.success(f'博饼: {result.get("bobing_count", 0)}次 → ' + '，'.join(rank_list))

    # ---------- 集礼盒 ----------
    def collect_query_status(self) -> Optional[Dict]:
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~midAutumn2026CollectService~queryStatus'
        return self._post(url)

    def collect(self) -> Optional[Dict]:
        if not self._consume('集礼盒'):
            return None
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~midAutumn2026CollectService~collect'
        resp = self._post_full(url)
        if resp and resp.get('success'):
            return resp.get('obj')
        else:
            self.logger.warning(f'集礼盒失败: {self._err(resp)}')
            return None

    def query_weekly_collect_record(self) -> Optional[List]:
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~midAutumn2026CollectService~queryWeeklyCollectRecord'
        return self._post(url)

    @staticmethod
    def _get_currency_balance(obj: Optional[Dict], currency: str) -> int:
        if not obj:
            return 0
        for acc in obj.get('currentAccountList', []):
            if acc.get('currency') == currency:
                return acc.get('balance', 0)
        return 0

    def do_collect(self, result: Dict) -> None:
        """集礼盒：消耗集礼盒次数，收集碎片"""
        status = self.collect_query_status()
        if not status:
            self.logger.warning('集礼盒: 状态获取失败')
            return

        collect_balance = self._get_currency_balance(status, 'COLLECT')
        completed = status.get('completedBoxCount', 0)
        if self.logger.verbose:
            fragments = {acc.get('currency'): acc.get('balance', 0)
                         for acc in status.get('currentAccountList', [])
                         if str(acc.get('currency', '')).startswith('FRAGMENT')}
            box_no = status.get('currentBoxNo', 0)
            box_status = status.get('currentBoxStatus', '')
            self.logger.info(f'集礼盒: 次数 {collect_balance}，已完成礼盒 {completed}，当前礼盒 第{box_no}个({box_status})')
            if fragments:
                self.logger.info('当前碎片: ' + ', '.join(f'{k}={v}' for k, v in fragments.items()))

        if collect_balance <= 0:
            self.logger.info('集礼盒: 无次数可用')
            return

        # 循环集礼盒，直到次数耗尽
        max_collect = 60
        cnt = 0
        gained: Dict[str, int] = {}
        while cnt < max_collect:
            time.sleep(1)
            c = self.collect()
            if not c:
                self.logger.warning('集礼盒返回空，停止')
                break

            received = c.get('receivedAccountList', [])
            if received:
                for item in received:
                    currency = item.get('currency', '未知')
                    amount = item.get('amount', 0)
                    gained[currency] = gained.get(currency, 0) + amount
                    if self.logger.verbose:
                        self.logger.medal(f'  获得碎片: {currency} x{amount}')
                result['collect_count'] = result.get('collect_count', 0) + 1

            collect_balance = self._get_currency_balance(c, 'COLLECT')
            if self.logger.verbose:
                if c.get('boxCompleted'):
                    self.logger.success(f'🎁 礼盒集齐！已完成 {c.get("completedBoxCount", 0)} 个礼盒')
                self.logger.info(f'  剩余集礼盒次数: {collect_balance}')

            if c.get('collectFinished'):
                if self.logger.verbose:
                    self.logger.success('所有礼盒已集齐，集礼盒结束')
                break
            if collect_balance <= 0:
                break
            cnt += 1

        gained_str = '，'.join(f'{k}x{v}' for k, v in gained.items()) if gained else '无'
        self.logger.success(f'集礼盒: {result.get("collect_count", 0)}次 → {gained_str}')

    # ---------- 抽奖 ----------
    def get_prize_pool(self) -> Optional[Dict]:
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~midAutumn2026LotteryService~prizePool'
        return self._post(url)

    def prize_draw(self, lottery_type: str) -> Optional[Dict]:
        if not self._consume(f'抽奖({lottery_type})'):
            return None
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~midAutumn2026LotteryService~prizeDraw'
        data = {"lotteryType": lottery_type}
        resp = self._post_full(url, data)
        if resp and resp.get('success'):
            return resp.get('obj')
        else:
            self.logger.warning(f'抽奖失败({lottery_type}): {self._err(resp)}')
            return None

    def do_lottery(self, result: Dict) -> None:
        """开礼盒单次抽奖 + 周四抽奖"""
        pool = self.get_prize_pool()
        if not pool:
            self.logger.warning('抽奖: 奖池获取失败')
            return

        # 单次抽奖奖池（集齐礼盒可抽）
        box_pool = pool.get('boxPool', {})
        remaining = box_pool.get('remainingDrawTimes', 0)
        if self.logger.verbose:
            box_gifts = box_pool.get('giftList', [])
            if box_gifts:
                self.logger.info('单抽奖品: ' + ', '.join(g.get('giftBagName', '?') for g in box_gifts))

        box_hits: List[str] = []
        if remaining > 0:
            for i in range(remaining):
                time.sleep(1)
                d = self.prize_draw("BOX")
                if not d:
                    self.logger.warning('单次抽奖失败，停止')
                    break
                name = d.get('giftBagName', '')
                worth = d.get('giftBagWorth', 0)
                pdto = d.get('productDTOList', [])
                if pdto:
                    p = pdto[0]
                    name = p.get('productName', p.get('couponName', name))
                box_hits.append(name or '奖励')
                result['box_draw_count'] = result.get('box_draw_count', 0) + 1
                result.setdefault('box_draw_results', []).append({'name': name, 'worth': worth})
                if self.logger.verbose:
                    self.logger.success(f'单次抽奖获得: {name or "奖励"} (价值{worth}元)')

        # 周四抽奖奖池
        weekly_pool = pool.get('weeklyPool', {})
        is_thursday = weekly_pool.get('isThursday', False)
        drawn = weekly_pool.get('drawn', False)

        weekly_hit = ''
        if is_thursday and not drawn:
            time.sleep(1)
            d = self.prize_draw("WEEKLY")
            if d:
                name = d.get('giftBagName', '')
                worth = d.get('giftBagWorth', 0)
                pdto = d.get('productDTOList', [])
                if pdto:
                    p = pdto[0]
                    name = p.get('productName', p.get('couponName', name))
                weekly_hit = name or '奖励'
                result['weekly_draw_count'] = result.get('weekly_draw_count', 0) + 1
                result.setdefault('weekly_draw_results', []).append({'name': name, 'worth': worth})
                if self.logger.verbose:
                    self.logger.success(f'周四抽奖获得: {weekly_hit} (价值{worth}元)')
            else:
                self.logger.warning('周四抽奖失败')

        if self.logger.verbose:
            self.logger.info(f'周四抽奖：isThursday={is_thursday}, drawn={drawn}')

        bits = [f'单抽{result.get("box_draw_count", 0)}次']
        if box_hits:
            bits.append('、'.join(box_hits))
        if is_thursday and not drawn and weekly_hit:
            bits.append('周四: ' + weekly_hit)
        elif is_thursday and drawn:
            bits.append('周四已参与')
        elif not is_thursday:
            bits.append('周四未开')
        self.logger.success('抽奖: ' + ' / '.join(bits))

    # ---------- 主流程 ----------
    def run(self) -> Dict[str, Any]:
        result: Dict[str, Any] = {
            'tasks_completed': 0,
            'bobing_count': 0,
            'collect_count': 0,
            'box_draw_count': 0,
            'weekly_draw_count': 0,
        }

        # 0. 进入活动首页（首次访问即带邀请参数，注册"被邀请访问"关系）
        inviter = self._pick_inviter()
        index_info = None
        if inviter and not self.dry_run:
            self.logger.detail(f'邀请访问: 携带邀请人 {inviter} (inviteType={INVITE_TYPE})')
            index_info = self.get_activity_index(invite_type=INVITE_TYPE, invite_user_id=inviter, no_login=True)
        if not index_info:
            index_info = self.get_activity_index()
        if index_info:
            ac_start = index_info.get("acStartTime", "")
            ac_end = index_info.get("acEndTime", "")
            send_num = index_info.get("sendNum", 0)
            pay_amount = index_info.get("payAmount", 0)
            self.logger.info(f'活动: {ac_start} ~ {ac_end}（寄件{send_num} / 支付{pay_amount}元）')

        # 1. 订阅状态（可选）+ 膨胀 + 挂件（进入页面触发）
        if ENABLE_SUBSCRIBE:
            subscribed = self.is_activity_subscribe()
            if subscribed:
                self.logger.info('订阅: 已订阅')
            else:
                self.logger.info('订阅: 未订阅，尝试订阅每日礼包...')
                self.do_subscribe()
        else:
            self.logger.detail('订阅: 跳过（SF_SUBSCRIBE=true 可开启）')
        self.get_dilate_change()
        widget = self.get_widget_status()
        if widget:
            dilate_widget = widget.get('dilateWidget', {})
            if dilate_widget:
                self.logger.detail(f'挂件领取状态: {dilate_widget.get("receiveStatus", "未知")}')
        dilate_status = self.get_dilate_status()
        if dilate_status:
            self.logger.detail(f'膨胀状态: dilateStatus={dilate_status.get("dilateStatus", "未知")}')

        # 2. 邀请列表（首次访问已注册邀请关系，这里查看结果）
        invite_list = self.get_invite_list()
        if invite_list:
            self.logger.success(f'邀请: {len(invite_list)} 位好友已访问')
            result['invited_friends'] = len(invite_list)
        else:
            self.logger.detail('暂无已邀请好友')

        # 3. 每日礼包
        self.do_daily_gift(result)

        # 4. 额外奖励卡片
        cards = self.query_extra_reward_cards()
        if cards:
            for card in cards:
                self.logger.detail(f'额外奖励 [{card.get("extraType", "")}]: 倒计时 {card.get("countdownHours", 0)}h')

        # 5. 双渠道任务（小程序与APP任务不同，分开做分开领）
        for idx, cfg in enumerate(CHANNELS):
            self._use_channel(cfg)
            self.logger.info(f'任务渠道: {cfg["name"]}')
            self.do_tasks(result)
            if idx == 0:
                # 一键集齐本周礼盒（账号级，跑一次即可）
                self.get_charge_task_reward()

        # 6. 博饼游戏（账号级每日一次，两个渠道的"玩博饼赢周边"任务共用）
        self.do_bobing(result)

        # 7. 博饼后补领游戏任务奖励（每渠道一次，把"玩博饼赢周边"+3次集礼盒拿全）
        if result.get('bobing_count', 0) > 0:
            for cfg in CHANNELS:
                self._use_channel(cfg)
                self._claim_task_rewards(result)

        # 8. 集礼盒
        self.do_collect(result)

        # 9. 抽奖
        self.do_lottery(result)

        # 10. 最终状态
        final_status = self.collect_query_status()
        if final_status:
            collect_balance = self._get_currency_balance(final_status, 'COLLECT')
            completed = final_status.get('completedBoxCount', 0)
            self.logger.info(f'最终: 集礼盒次数 {collect_balance}，已完成礼盒 {completed}')

        return result


# ==================== 账号执行 ====================
def run_account(account_url: str, index: int, inviter_id: str = '') -> Dict[str, Any]:
    logger = Logger(verbose=VERBOSE)
    proxy_url = os.getenv('SF_PROXY_API_URL', '')
    proxy_manager = ProxyManager(proxy_url)

    http = SFHttpClient(proxy_manager)
    retry_count = 0
    login_success = False
    phone = ''
    user_id = ''

    while retry_count < MAX_PROXY_RETRIES and not login_success:
        try:
            if retry_count > 0:
                http = SFHttpClient(proxy_manager)
            success, user_id, phone = http.login(account_url)
            if success:
                login_success = True
                break
        except Exception:
            pass
        retry_count += 1
        if retry_count < MAX_PROXY_RETRIES:
            time.sleep(2)

    if not login_success:
        logger.error(f'账号{index + 1} 登录失败')
        return {'success': False, 'phone': '', 'index': index,
                'tasks_completed': 0, 'bobing_count': 0, 'collect_count': 0,
                'box_draw_count': 0, 'weekly_draw_count': 0}

    masked_phone = phone[:3] + "****" + phone[7:] if len(phone) >= 7 else phone
    logger.success(f'账号{index + 1}: 【{phone}】登录成功')

    time.sleep(random.uniform(1, 3))

    executor = MidAutumnExecutor(http, logger, user_id, dry_run=DRY_RUN, inviter_id=inviter_id)
    activity_result = executor.run()

    return {
        'success': True,
        'phone': phone,
        'index': index,
        **activity_result,
    }


# ==================== 主程序 ====================
def _extract_user_id(line: str) -> str:
    """从账号配置行提取 _login_user_id_（邀请互刷用）"""
    m = re.search(r'_login_user_id_=([A-Za-z0-9]+)', line)
    return m.group(1) if m else ''


def main():
    env_name = 'sfsyUrl'
    env_value = os.getenv(env_name)
    if not env_value:
        print(f"❌ 未找到环境变量 {env_name}，请检查配置")
        return

    account_urls = [url.strip() for url in env_value.split('\n') if url.strip()]
    if not account_urls:
        print(f"❌ 环境变量 {env_name} 为空或格式错误")
        return

    print(f"📱 共获取到 {len(account_urls)} 个账号")

    # 邀请互刷：账号 i 用账号 (i+1)%N 的ID访问活动页，
    # 保证每个账号都收到一条"被邀请访问"记录（邀好友任务）
    account_ids = [_extract_user_id(u) for u in account_urls]
    inviter_ids = []
    n = len(account_ids)
    for i, uid in enumerate(account_ids):
        if n >= 2:
            j = (i + 1) % n
            inviter_ids.append(account_ids[j] if account_ids[j] and account_ids[j] != uid else '')
        else:
            inviter_ids.append('')

    all_results = []

    if CONCURRENT_NUM <= 1:
        for idx, url in enumerate(account_urls):
            result = run_account(url, idx, inviter_ids[idx])
            all_results.append(result)
            if idx < len(account_urls) - 1:
                print("-" * 60)
                time.sleep(2)
    else:
        with ThreadPoolExecutor(max_workers=CONCURRENT_NUM) as pool:
            futures = {pool.submit(run_account, url, idx, inviter_ids[idx]): idx for idx, url in enumerate(account_urls)}
            for future in as_completed(futures):
                all_results.append(future.result())

    all_results.sort(key=lambda x: x['index'])

    # 结果落盘（一行一个账号，JSON）
    try:
        with open(RESULT_FILE, 'a', encoding='utf-8') as f:
            for r in all_results:
                f.write(json.dumps(r, ensure_ascii=False) + '\n')
        print(f"📄 结果已保存到 {RESULT_FILE}")
    except OSError as e:
        print(f"⚠️ 结果保存失败: {e}")

    print("=" * 60)
    print(f"📊 中秋博饼集礼盒活动汇总{'（自检模式）' if DRY_RUN else ''}")
    print("=" * 60)
    for result in all_results:
        phone = result.get('phone', '未知')
        masked_phone = phone[:3] + "****" + phone[7:] if len(phone) >= 7 else phone
        if result.get('success'):
            print(f"  {masked_phone}: 小程序任务 {result.get('tasks_mp', 0)} / APP任务 {result.get('tasks_app', 0)} | "
                  f"邀请 {result.get('invited_friends', 0)}人({result.get('invite_process', '-')}) | "
                  f"博饼 {result.get('bobing_count', 0)}次 | "
                  f"集礼盒 {result.get('collect_count', 0)}次 | "
                  f"单次抽奖 {result.get('box_draw_count', 0)}次 | "
                  f"周四抽奖 {result.get('weekly_draw_count', 0)}次")
        else:
            print(f"  {masked_phone}: 登录失败")
    print("=" * 60)


if __name__ == '__main__':
    main()

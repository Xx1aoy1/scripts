"""

顺丰2026世界杯活动 - 射门游戏 + 比赛竞猜 + 每日礼物
Author: Auto-generated (参考端午活动脚本)
Version: 1.1.0
Date: 2026-07-04

更新日志:
  1.1.0 (2026-07-04) 新增下注结算(settleBet)阶段、赔率显示、潜在收益/今日盈亏列
  1.0.0 (2026-07-03) 初版：每日礼物 + 任务(白名单) + 射门游戏 + 比赛下注

活动周期: 2026-07-02 ~ 2026-07-20
货币: GOLD_COIN (金币)
活动码: WORLD_CUP

"""

import hashlib
import json
import os
import random
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from urllib.parse import unquote
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

inviteId = ['C6E5C3BDD7624520AB869D2AF9E75D95']

PROXY_TIMEOUT = 15
MAX_PROXY_RETRIES = 5
REQUEST_RETRY_COUNT = 3
CONCURRENT_NUM = int(os.getenv('SFBF', '1'))
if CONCURRENT_NUM > 20:
    CONCURRENT_NUM = 20
elif CONCURRENT_NUM < 1:
    CONCURRENT_NUM = 1

print_lock = Lock()

ACTIVITY_CODE = "WORLD_CUP"
TOKEN = 'wwesldfs29aniversaryvdld29'
SYS_CODE = 'MCS-MIMP-CORE'

CURRENCY_NAMES = {'GOLD_COIN': '金币'}
CHANNEL = '26sjbapp'
PLATFORM = 'SFAPP'
CITY_CODE = '021'

# ===== 活动阶段开关（True=开启 / False=关闭）=====
ENABLE_DAILY_GIFT = True   # 每日礼物
ENABLE_TASKS      = True   # 任务（仅执行 AUTO_FINISH_TASK_CODES 白名单里的）
ENABLE_GAME       = True   # 射门游戏
ENABLE_BET        = True   # 比赛竞猜（下注）
ENABLE_SETTLE     = True   # 下注结算（早上跑完后，结算前一天已开赛的下注盈亏）

# ===== 下注参数 =====
# 服务端最低下注金币为 10，< 10 会报 notSuccess。修改前请先抓包确认下限。
BET_COIN = 10  # 每场比赛下注金币数

SKIP_TASK_TYPES = [
    'BUY_ADD_VALUE_SERVICE_PACKET',
    'SEND_INTERNATIONAL_PACKAGE',
    'LOOK_BIG_PACKAGE_GET_CASH',
    'SEND_SUCCESS_RECALL',
    'CHARGE_NEW_EXPRESS_CARD',
    'CHARGE_COLLECT_ALL',
    'OPEN_FAMILY_HOME_MUTUAL',
    'INVITEFRIENDS_PARTAKE_ACTIVITY',
    'BROWSE_INTEGRAL_PLANET',
    'BROWSE_FAMILY_HOME_MUTUAL',
]
# 浏览类任务一律跳过（含 BROWSE_/VIEWPAGE_ 前缀），不发起 finishTask
SKIP_TASK_PREFIXES = ('BROWSE_', 'VIEWPAGE_')

# 仅对这些 taskCode 直接调用 finishTask
AUTO_FINISH_TASK_CODES = {
    '0CD7AFA68009402DBE5BF9D3C10D0115',  # 浏览积分商城（验证通过）
    '895011E183CE4E61BBACE8A63B98596A',  # 去看看互寄8折权益（未验证，可移除）
}


class Logger:
    def __init__(self):
        self.messages: List[str] = []
        self.lock = Lock()

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
    def goal(self, msg): self._log('⚽', msg)


class ProxyManager:
    def __init__(self, api_url: str):
        self.api_url = api_url

    def get_proxy(self) -> Optional[Dict[str, str]]:
        try:
            if not self.api_url:
                return None
            response = requests.get(self.api_url, timeout=10)
            if response.status_code == 200:
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
                print(f"❌ 获取代理失败: HTTP {response.status_code}")
            return None
        except Exception as e:
            with print_lock:
                print(f"❌ 获取代理异常: {str(e)[:100]}")
            return None


class SFHttpClient:
    def __init__(self, proxy_manager: ProxyManager):
        self.proxy_manager = proxy_manager
        self.session = requests.Session()
        self.session.verify = False

        proxy = self.proxy_manager.get_proxy()
        if proxy:
            self.session.proxies = proxy
        else:
            if self.proxy_manager.api_url:
                with print_lock:
                    print("⚠️ 代理获取失败，将不使用代理")

        self.headers = {
            'Host': 'mcs-mimp-web.sf-express.com',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 mediaCode=SFEXPRESSAPP-iOS-ML',
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json',
            'channel': CHANNEL,
            'platform': PLATFORM,
            'accept-language': 'zh-CN,zh;q=0.9',
        }

    def _generate_sign(self) -> Dict[str, str]:
        timestamp = str(int(round(time.time() * 1000)))
        data = f'token={TOKEN}&timestamp={timestamp}&sysCode={SYS_CODE}'
        signature = hashlib.md5(data.encode()).hexdigest()
        return {
            'sysCode': SYS_CODE,
            'timestamp': timestamp,
            'signature': signature,
        }

    def request(self, url: str, data: Optional[Dict] = None, method: str = 'POST') -> Optional[Dict]:
        retry_count = 0
        proxy_retry_count = 0

        while proxy_retry_count < MAX_PROXY_RETRIES:
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

                if 'ProxyError' in error_str or 'SSLError' in error_str or 'ConnectionError' in error_str:
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


class WorldCupExecutor:
    BASE_URL = 'https://mcs-mimp-web.sf-express.com/mcs-mimp'

    def __init__(self, http: SFHttpClient, logger: Logger, user_id: str):
        self.http = http
        self.logger = logger
        self.user_id = user_id
        self.level_list: List[Dict] = []

    def _post(self, path: str, data: Optional[Dict] = None) -> Optional[Dict]:
        url = f'{self.BASE_URL}{path}'
        return self.http.request(url, data=data or {})

    def get_activity_index(self) -> Optional[Dict]:
        resp = self._post('/commonPost/~memberNonactivity~worldCupIndexService~index')
        if resp and resp.get('success'):
            return resp.get('obj', {})
        return None

    def get_game_index(self) -> Optional[Dict]:
        resp = self._post('/commonPost/~memberNonactivity~worldCupGameService~index')
        if resp and resp.get('success'):
            return resp.get('obj', {})
        return None

    def get_bet_status(self) -> Optional[Dict]:
        resp = self._post('/commonPost/~memberNonactivity~worldCupMatchService~betStatus')
        if resp and resp.get('success'):
            return resp.get('obj', {})
        return None

    def get_daily_gift_status(self) -> Optional[Dict]:
        data = {"cityCode": CITY_CODE}
        resp = self._post('/commonPost/~memberNonactivity~worldCupDailyService~getDailyGiftStatus', data)
        if resp and resp.get('success'):
            return resp.get('obj', {})
        return None

    def receive_daily_gift(self) -> Optional[Dict]:
        data = {"cityCode": CITY_CODE}
        resp = self._post('/commonPost/~memberNonactivity~worldCupDailyService~receiveDailyGift', data)
        if resp and resp.get('success'):
            return resp.get('obj', {})
        return None

    def get_task_list(self) -> Optional[List[Dict]]:
        data = {"activityCode": ACTIVITY_CODE, "channelType": PLATFORM}
        resp = self._post('/commonPost/~memberNonactivity~activityTaskService~taskList', data)
        if resp and resp.get('success'):
            return resp.get('obj', [])
        return None

    def finish_task(self, task_code: str) -> bool:
        url = f'{self.BASE_URL}/commonPost/~memberEs~taskRecord~finishTask'
        data = {"taskCode": task_code}
        resp = self.http.request(url, data=data)
        return bool(resp and resp.get('success'))

    def fetch_task_reward(self) -> Optional[Dict]:
        data = {"channelType": PLATFORM, "activityCode": ACTIVITY_CODE}
        resp = self._post('/commonPost/~memberNonactivity~worldCupTaskService~fetchTaskReward', data)
        if resp and resp.get('success'):
            return resp.get('obj', {})
        return None

    def report_pass(self, level: int, shot_num: int) -> Optional[Dict]:
        data = {"level": level, "shotNum": shot_num}
        resp = self._post('/commonPost/~memberNonactivity~worldCupGameService~passReport', data)
        if resp and resp.get('success'):
            return resp.get('obj', {})
        err = resp.get('errorMessage', '未知错误') if resp else '请求失败'
        self.logger.warning(f'第{level}关上报失败: {err}')
        return None

    def place_bet(self, match_id: str, bet_result: int, bet_coin: int) -> bool:
        """下注
        bet_result: 0=主胜 1=平 2=客胜 (与 odds 数组顺序一致)
        bet_coin: 下注金币数
        """
        data = {"matchId": match_id, "betResult": bet_result, "betCoin": bet_coin}
        resp = self._post('/commonPost/~memberNonactivity~worldCupMatchService~placeBet', data)
        if resp and resp.get('success'):
            return True
        err = resp.get('errorMessage', '未知错误') if resp else '请求失败'
        self.logger.warning(f'下注失败(match={match_id}, result={bet_result}): {err}')
        return False

    def settle_bet(self) -> Optional[list]:
        """结算下注
        返回已开赛并结算的下注列表；空数组表示今天没有可结算的
        """
        resp = self._post('/commonPost/~memberNonactivity~worldCupMatchService~settleBet', {})
        if resp and resp.get('success'):
            return resp.get('obj', []) or []
        err = resp.get('errorMessage', '未知错误') if resp else '请求失败'
        self.logger.warning(f'结算请求失败: {err}')
        return None

    def do_invite(self):
        try:
            available_invites = [inv for inv in inviteId if inv != self.user_id]
            if not available_invites:
                return
            random_invite = random.choice(available_invites)
            url = f'{self.BASE_URL}/commonPost/~memberNonactivity~worldCupIndexService~index'
            self.http.request(url, data={"inviteType": 1, "inviteUserId": random_invite})
        except Exception as e:
            self.logger.error(f"邀请初始化异常: {str(e)}")

    def do_daily_gift(self, result: Dict) -> None:
        self.logger.task('[每日礼物] 检查状态...')
        status = self.get_daily_gift_status()
        if status is None:
            self.logger.warning('[每日礼物] 获取状态失败')
            return
        if status.get('received'):
            self.logger.success('[每日礼物] 今日已领取')
            return
        if not status.get('canReceive'):
            self.logger.info('[每日礼物] 今日不可领取')
            return
        self.logger.task('[每日礼物] 尝试领取...')
        if self.receive_daily_gift():
            self.logger.success('[每日礼物] 领取成功')
            result['daily_gift'] = True
        else:
            self.logger.warning('[每日礼物] 领取失败')

    def do_tasks(self, result: Dict) -> None:
        self.logger.info('正在获取世界杯活动任务列表...')
        tasks = self.get_task_list()
        if tasks is None:
            return
        self.logger.info(f'共发现 {len(tasks)} 个任务')

        for task in tasks:
            task_name = task.get('taskName', '未知')
            task_type = task.get('taskType', '')
            task_code = task.get('taskCode', '')
            status = task.get('status')
            rest_finish = task.get('restFinishTime', 0)
            can_receive = task.get('canReceiveTokenNum', 0)
            max_finish = task.get('maxFinishTime', 0)

            if task_code not in AUTO_FINISH_TASK_CODES:
                continue

            self.logger.info(f'[{task_name}]')

            if status == 3 or (status == 1 and rest_finish <= 0):
                self.logger.success(f'[{task_name}] 已完成')
                continue

            if self.finish_task(task_code):
                self.logger.success(f'[{task_name}] 完成成功')
                result['tasks_completed'] += 1
            else:
                self.logger.warning(f'[{task_name}] 完成失败')
            time.sleep(1)

    def do_fetch_rewards(self, result: Dict) -> None:
        self.logger.info('领取任务奖励...')
        reward_resp = self.fetch_task_reward()
        if reward_resp:
            received = reward_resp.get('receivedAccountList', [])
            if received:
                for item in received:
                    currency = item.get('currency', '')
                    amount = item.get('amount', 0)
                    self.logger.success(f'领取: {currency} x{amount}')
            else:
                self.logger.info('无新奖励可领取')

    def play_game(self, result: Dict) -> None:
        self.logger.info('⚽ 开始挑战射门游戏...')
        game_info = self.get_game_index()
        if game_info is None:
            self.logger.warning('获取游戏配置失败')
            return

        self.level_list = game_info.get('levelList', [])
        cur_stage = game_info.get('curStage', 1)
        cur_level = game_info.get('curLevel', 1)

        if not self.level_list:
            self.logger.warning('游戏关卡列表为空')
            return

        self.logger.info(f'当前进度: 第{cur_stage}阶段 第{cur_level}关')

        for level_cfg in self.level_list:
            level_no = level_cfg.get('level')
            target = level_cfg.get('target', 0)
            reward = level_cfg.get('rewardCoins', 0)

            if level_no < cur_level:
                continue

            self.logger.task(f'挑战第{level_no}关（目标 {target} 次进球，奖励 {reward} 金币）')

            pass_result = self.report_pass(level_no, target)

            attempts = 0
            while attempts < 3 and (pass_result is None or not pass_result.get('coinNum', 0) >= reward):
                time.sleep(1)
                pass_result = self.report_pass(level_no, target)
                attempts += 1

            if pass_result:
                result['stages_passed'].append({
                    'level': level_no,
                    'coins': pass_result.get('coinNum', 0),
                    'reward': reward,
                })
                result['game_coins'] += pass_result.get('coinNum', 0)
                self.logger.goal(f'第{level_no}关完成，获得 {pass_result.get("coinNum", 0)} 金币')
            else:
                self.logger.warning(f'第{level_no}关未通过')

    def do_bet(self, result: Dict) -> None:
        self.logger.info('⚽ 查询比赛竞猜状态...')
        bet_status = self.get_bet_status()
        if bet_status is None:
            return

        account = bet_status.get('currentAccount', {})
        balance = account.get('balance', 0)
        self.logger.info(f'当前金币余额: {balance}')

        matches = bet_status.get('matchList', [])
        # 未开赛 + 未下过注（recordStatus=0）
        pending = [
            m for m in matches
            if m.get('matchStatus') == 'Fixture' and m.get('recordStatus', 0) == 0
        ]
        self.logger.info(f'共 {len(matches)} 场比赛，{len(pending)} 场可下注')
        self.logger.info(f'单场下注: {BET_COIN} 金币')

        if balance < BET_COIN:
            self.logger.warning(f'余额不足 {BET_COIN} 金币，跳过下注')
            result['final_balance'] = balance
            result['final_total'] = account.get('totalAmount', 0)
            return

        choice_map = {0: '主胜', 1: '平', 2: '客胜'}

        for m in pending:
            match_id = m.get('matchId')
            team_a = m.get('teamAName', '?')
            team_b = m.get('teamBName', '?')
            odds_str = m.get('odds', '?,?,?')
            bet_result = random.randint(0, 2)

            try:
                odds_list = [float(x) for x in odds_str.split(',')]
                picked_odds = odds_list[bet_result] if bet_result < len(odds_list) else 0.0
            except (ValueError, IndexError):
                picked_odds = 0.0

            potential_payout = round(BET_COIN * picked_odds, 2)
            potential_profit = round(potential_payout - BET_COIN, 2)

            self.logger.task(
                f'下注: {team_a} vs {team_b}（赔率 {odds_str}）→ '
                f'{choice_map[bet_result]} {BET_COIN} 金币 '
                f'| 命中得 {potential_payout}（净赚 {potential_profit}）'
            )

            time.sleep(1)
            if self.place_bet(match_id, bet_result=bet_result, bet_coin=BET_COIN):
                self.logger.success(
                    f'下注成功: {team_a} vs {team_b}（赔率 {picked_odds}，命中得 {potential_payout}）'
                )
                result['bets_placed'] += 1
                result['bet_details'].append({
                    'match': f'{team_a} vs {team_b}',
                    'choice': choice_map[bet_result],
                    'odds': picked_odds,
                    'bet_coin': BET_COIN,
                    'potential_payout': potential_payout,
                    'potential_profit': potential_profit,
                })
            else:
                self.logger.warning(f'下注失败: {team_a} vs {team_b}')

        status_after = self.get_bet_status()
        if status_after:
            acc_after = status_after.get('currentAccount', {})
            result['final_balance'] = acc_after.get('balance', 0)
            result['final_total'] = acc_after.get('totalAmount', 0)
        else:
            result['final_balance'] = balance
            result['final_total'] = account.get('totalAmount', 0)

    def do_settle(self, result: Dict) -> None:
        """结算已开赛下注的实际盈亏"""
        self.logger.info('💰 结算昨日下注结果...')
        settled = self.settle_bet()
        if settled is None:
            self.logger.warning('结算接口失败，跳过')
            return

        if not settled:
            self.logger.info('今日无新结算记录')
            return

        choice_map = {0: '主胜', 1: '平', 2: '客胜'}

        total_pnl = 0
        wins = 0
        losses = 0

        for m in settled:
            match_id = m.get('matchId', '?')
            team_a = m.get('teamAName', '?')
            team_b = m.get('teamBName', '?')
            score = f"{m.get('teamAScore', '?')}:{m.get('teamBScore', '?')}"
            bet_coin = m.get('betCoin', 0)
            bet_result = m.get('betResult', -1)
            bet_odds_str = m.get('betOdds', '?,?,?')
            win_coin = m.get('betWinCoin', 0)

            pnl = win_coin - bet_coin
            total_pnl += pnl

            try:
                odds_list = [float(x) for x in bet_odds_str.split(',')]
                picked_odds = odds_list[bet_result] if 0 <= bet_result < len(odds_list) else 0.0
            except (ValueError, IndexError):
                picked_odds = 0.0

            if pnl > 0:
                wins += 1
                icon = '🎉'
                pnl_str = f'+{pnl}'
            elif pnl < 0:
                losses += 1
                icon = '💔'
                pnl_str = f'{pnl}'
            else:
                icon = '➖'
                pnl_str = '0'

            self.logger.info(
                f'  {icon} {team_a} vs {team_b}（{score}）→ '
                f'押{choice_map.get(bet_result, "?")} 赔率 {picked_odds} | '
                f'投 {bet_coin} 得 {win_coin} | {pnl_str}'
            )

            result['settle_details'].append({
                'match': f'{team_a} vs {team_b}',
                'score': score,
                'choice': choice_map.get(bet_result, '?'),
                'bet_coin': bet_coin,
                'win_coin': win_coin,
                'pnl': pnl,
            })

        result['settle_pnl'] = total_pnl
        result['settle_wins'] = wins
        result['settle_losses'] = losses

        if total_pnl > 0:
            self.logger.success(f'结算完成: {wins}胜{losses}负，净赚 +{total_pnl} 金币')
        elif total_pnl < 0:
            self.logger.warning(f'结算完成: {wins}胜{losses}负，净亏 {total_pnl} 金币')
        else:
            self.logger.info(f'结算完成: {wins}胜{losses}负，持平')

        # 重新拉一次余额，反映结算后的真实金币数
        status_after = self.get_bet_status()
        if status_after:
            acc_after = status_after.get('currentAccount', {})
            result['final_balance'] = acc_after.get('balance', 0)
            result['final_total'] = acc_after.get('totalAmount', 0)

    def show_status(self) -> None:
        self.logger.info('=' * 20 + '  世界杯活动状态  ' + '=' * 20)
        bet_status = self.get_bet_status()
        if bet_status:
            account = bet_status.get('currentAccount', {})
            self.logger.info(f'金币余额: {account.get("balance", 0)} / 累计: {account.get("totalAmount", 0)}')

        daily = self.get_daily_gift_status()
        if daily:
            status_str = '已领取' if daily.get('received') else ('可领取' if daily.get('canReceive') else '不可领取')
            self.logger.info(f'每日礼物: {status_str}')

        game = self.get_game_index()
        if game:
            self.logger.info(f'游戏阶段: 第{game.get("curStage", 1)}阶段 第{game.get("curLevel", 1)}关')

        index = self.get_activity_index()
        if index:
            self.logger.info(f'活动周期: {index.get("acStartTime", "")} ~ {index.get("acEndTime", "")}')
            self.logger.info(f'可领金币: {index.get("availableRewardCoins", 0)}')

        self.logger.info('=' * 56)

    def run(self) -> Dict[str, Any]:
        result = {
            'tasks_completed': 0,
            'game_coins': 0,
            'stages_passed': [],
            'daily_gift': False,
            'bets_placed': 0,
            'bet_details': [],
            'settle_pnl': 0,
            'settle_wins': 0,
            'settle_losses': 0,
            'settle_details': [],
            'final_balance': 0,
            'final_total': 0,
        }

        self.do_invite()

        index_info = self.get_activity_index()
        if index_info:
            self.logger.success(f'已加入世界杯活动，可领 {index_info.get("availableRewardCoins", 0)} 金币')

        if ENABLE_DAILY_GIFT:
            self.do_daily_gift(result)
        if ENABLE_TASKS:
            self.do_tasks(result)
            self.do_fetch_rewards(result)
        if ENABLE_GAME:
            self.play_game(result)
        if ENABLE_BET:
            self.do_bet(result)
        else:
            self.logger.info('⚽ [开关] 比赛下注已关闭，跳过')
        if ENABLE_SETTLE:
            self.do_settle(result)
        else:
            self.logger.info('💰 [开关] 下注结算已关闭，跳过')

        return result


def run_account(account_url: str, index: int) -> Dict[str, Any]:
    logger = Logger()
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
        return {
            'success': False, 'phone': '', 'index': index,
            'tasks_completed': 0, 'game_coins': 0, 'stages_passed': [],
            'daily_gift': False, 'bets_placed': 0, 'bet_details': [],
            'settle_pnl': 0, 'settle_wins': 0, 'settle_losses': 0, 'settle_details': [],
            'final_balance': 0, 'final_total': 0,
        }

    masked_phone = phone[:3] + "****" + phone[7:] if len(phone) >= 7 else phone
    logger.success(f'账号{index + 1}: 【{masked_phone}】登录成功')

    time.sleep(random.uniform(1, 3))

    executor = WorldCupExecutor(http, logger, user_id)
    activity_result = executor.run()

    return {
        'success': True,
        'phone': phone,
        'index': index,
        **activity_result,
    }


def main():
    env_name = 'sfsyUrl'
    env_value = os.getenv(env_name)
    if not env_value:
        print(f"❌ 未找到环境变量 {env_name}，请检查配置")
        return

    account_urls = [url.strip() for url in env_value.split('&') if url.strip()]
    if not account_urls:
        print(f"❌ 环境变量 {env_name} 为空或格式错误")
        return

    random.shuffle(account_urls)

    print("=" * 60)
    print(f"⚽ 顺丰2026世界杯活动 - 射门挑战 + 比赛竞猜")
    print(f"👨‍💻 Author: Auto-generated")
    print(f"📱 共获取到 {len(account_urls)} 个账号")
    print(f"⚙️ 并发数量: {CONCURRENT_NUM}")
    print(f"🎯 阶段开关: 礼物={ENABLE_DAILY_GIFT} 任务={ENABLE_TASKS} 游戏={ENABLE_GAME} 下注={ENABLE_BET} 结算={ENABLE_SETTLE}")
    print(f"💰 单场下注: {BET_COIN} 金币（最低 10）")
    print(f"⏰ 执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    all_results = []

    if CONCURRENT_NUM <= 1:
        for idx, url in enumerate(account_urls):
            result = run_account(url, idx)
            all_results.append(result)
            if idx < len(account_urls) - 1:
                print("-" * 60)
                time.sleep(2)
    else:
        with ThreadPoolExecutor(max_workers=CONCURRENT_NUM) as pool:
            futures = {pool.submit(run_account, url, idx): idx for idx, url in enumerate(account_urls)}
            for future in as_completed(futures):
                all_results.append(future.result())

    all_results.sort(key=lambda x: x['index'])

    print(f"\n" + "=" * 90)
    print(f"📊 世界杯活动汇总")
    print("=" * 90)
    print(f"{'序号':<6} {'手机号':<15} {'金币余额':<10} {'通关数':<6} {'下注数':<6} {'潜在收益':<10} {'今日盈亏':<10} {'每日礼物':<8}")
    print("-" * 100)

    total_coins = 0
    total_balance = 0
    total_payout = 0.0
    total_pnl = 0

    for r in all_results:
        idx = r['index'] + 1
        phone = r['phone'][:3] + "****" + r['phone'][7:] if r.get('phone') and len(r['phone']) >= 7 else r.get('phone', '未登录')
        daily = '✅' if r.get('daily_gift') else '❌'
        balance = r.get('final_balance', 0)
        stages = len(r.get('stages_passed', []))
        bets = r.get('bets_placed', 0)
        payout = sum(d.get('potential_payout', 0) for d in r.get('bet_details', []))
        pnl = r.get('settle_pnl', 0)
        wins = r.get('settle_wins', 0)
        losses = r.get('settle_losses', 0)
        if wins + losses > 0:
            pnl_str = f'{pnl:+d} ({wins}胜{losses}负)'
        else:
            pnl_str = '-'
        total_payout += payout
        total_pnl += pnl

        total_balance += balance
        total_coins += r.get('game_coins', 0)

        print(f"{idx:<6} {phone:<15} {balance:<10} {stages:<6} {bets:<6} {payout:<10} {pnl_str:<10} {daily:<8}")

    print("-" * 100)
    print(f"{'汇总':<6} {'账号: ' + str(len(all_results)):<15} 总金币余额: {total_balance} | 游戏产出: {total_coins} | 累计盈亏: {total_pnl:+d}")
    print("=" * 90)
    print("\n🎊 所有账号执行完成!")


if __name__ == '__main__':
    main()

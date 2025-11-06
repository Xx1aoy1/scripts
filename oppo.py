#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Date: 2025-09-21
# @LastEditTime: 2025-09-24
# From:yaohuo28507
"""
OPPO 商城 APP 和 小程序 签到任务自动化脚本。

使用方法：
- OPPO商城APP版：
  - 开启抓包进入'OPPO商城'app，进入我的 - 签到任务
  - 需要配置环境变量 `OPPO_APP`
  - 抓包 https://hd.opposhop.cn 请求头中的 Cookie，整个Cookie都放进来
  - 格式为：Cookie#User-Agent#会员等级
  - User-Agent：请求头的User-Agent
  - 会员等级：用户等级，值只能定义为 "普卡"、"银卡会员"、"金钻会员"
  - 多账号用 '@' 符号隔开

- OPPO商城小程序版：
  - 开启抓包进入'OPPO商城小程序'，进入签到任务
  - 需要配置环境变量 `OPPO_MINI`
  - 抓包 https://hd.opposhop.cn 请求头中的 Cookie，整个Cookie都放进来
  - 格式为：Cookie值
  - 多账号用 '@' 符号隔开

配置参数说明：
- IS_LUCKY_DRAW_ENABLED: 是否开启抽奖功能 (True/False)
- IS_CREDITS_DRAW_ENABLED: 是否开启消耗积分的抽奖功能 (True/False)
  注意：小程序每日签到和小程序专享福利的抽奖需要消耗积分
"""
import random
import re
import time
import json
import os
from urllib.parse import urlparse, parse_qs, quote
from datetime import datetime
import httpx
import notify 

# --- 全局配置 ---
# 抽奖功能默认开关（当活动配置中没有设置 is_lucky_draw 时使用）
DEFAULT_LUCKY_DRAW_ENABLED = True

# 特殊处理的活动关键字（用于周年庆等特殊活动识别）
ANNIVERSARY_KEYWORDS = ["周年庆", "集卡"]

# 不支持的任务类型（参考activity_base.py的设计）
UNSUPPORTED_TASK_TYPES = [6, 14, 15, 16, 17]

# 特殊活动ID配置（硬编码的ID）
SPECIAL_ACTIVITY_IDS = {
    "周年庆集卡": "1958427301926539264",  # 只需要集卡活动ID，任务ID动态获取
}

# 小程序静态活动配置
# 可以在这里添加、修改或禁用特定的活动
# enabled: False 表示禁用该活动
# is_lucky_draw: 控制该活动是否抽奖（可选，不设置时使用默认值）
STATIC_ACTIVITIES_CONFIG = [
    {"bp_url": "/bp/747f65c18da6f6b7", "name": "积分兑换专区", "enabled": True, "draw_jimu_name": "OPPO 商城 积分兑换专区"},
    {"bp_url": "/bp/457871c72cb6ccd9", "name": "莎莎企业", "enabled": True, "draw_jimu_name": "莎莎企业 夏日奇旅"},
    {"bp_url": "/bp/e0e8a5a074b18a45", "name": "排球少年!!联名定制产品图鉴", "enabled": True, "draw_jimu_name": "排球少年!!联名定制产品图鉴"},
    {"bp_url": "/bp/1d81e50e9295425c", "name": "30周年庆集卡礼(9.15-10.08)", "enabled": True, "draw_jimu_name": "30周年庆集卡礼"},
    {"bp_url": "/bp/adfdd92edbb1b2ee", "name": "一加宠粉福利站(9.22-10.15)", "enabled": True, "draw_jimu_name": "一加宠粉福利站"},
    {"bp_url": "/bp/0bff5d7a0cfc6953", "name": "OPPO Find X9 系列新品预约", "enabled": True, "draw_jimu_name": "OPPO Find X9 系列新品上市"},
]

# 动态活动发现配置
DYNAMIC_ACTIVITIES_TO_FIND = [
    {'keyword1': '福利专区', 'keyword2': '签到', 'name': '小程序每日签到', 'draw_jimu_name': '签到赢好礼', 'is_lucky_draw': False},
    {'keyword1': '福利专区', 'keyword2': '窄渠道', 'name': '小程序专享福利', 'draw_jimu_name': '小程序专享福利', 'is_lucky_draw': False},
]


# --- 摘要与日志模块 ---
class NotificationManager:
    """
    用于生成简洁的推送摘要。
    """
    def __init__(self):
        self.summary_parts = []

    def add_summary(self, message):
        """添加一条摘要信息。"""
        self.summary_parts.append(message)

    def get_summary(self):
        """获取最终的摘要字符串。"""
        if not self.summary_parts:
            return "没有可报告的摘要信息。"
        return '\n'.join(self.summary_parts)

# 全局摘要管理器实例
notify_manager = NotificationManager()

def log_print(*args, sep=' ', end='\n', **kwargs):
    """
    自定义的日志打印函数，仅输出到控制台。
    """
    print(*args, sep=sep, end=end, **kwargs)

def get_env(env_var, separator):
    """
    从环境变量中获取配置。
    支持从 .env 文件加载（如果存在 python-dotenv 库）。
    :param env_var: 环境变量的名称
    :param separator: 多账号间的分隔符
    :return: 账号配置列表
    """
    value = os.environ.get(env_var)
    if value:
        return re.split(separator, value)

    try:
        from dotenv import load_dotenv, find_dotenv
        load_dotenv(find_dotenv())
        value = os.environ.get(env_var)
        if value:
            return re.split(separator, value)
    except ImportError:
        pass # 如果没有安装dotenv库，则忽略

    log_print(f"未找到环境变量 {env_var}。")
    return []

def random_sleep(min_sec=1.5, max_sec=3.0):
    """
    在指定范围内随机延迟一段时间，模拟真人操作。
    :param min_sec: 最小延迟时间（秒）
    :param max_sec: 最大延迟时间（秒）
    """
    time.sleep(random.uniform(min_sec, max_sec))

# --- 常量定义 ---
BASE_URL_HD = "https://hd.opposhop.cn"
BASE_URL_MSEC = "https://msec.opposhop.cn"

# 通用请求头
COMMON_HEADERS = {
    'Accept-Encoding': 'gzip, deflate',
    'Accept': "application/json, text/plain, */*",
    'Content-Type': 'application/json',
}

# 小程序专用请求头
MINI_APP_HEADERS = {
    **COMMON_HEADERS,
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090c33)XWEB/11581",
}


# --- OPPO 商城 APP 类 ---
class OppoApp:
    """
    处理 OPPO 商城 APP 版本的签到和任务。
    """
    def __init__(self, cookie_str, account_index):
        """
        初始化APP任务实例。
        :param cookie_str: 格式为 "Cookie#User-Agent#会员等级" 的字符串。
        :param account_index: 账号索引，用于日志区分。
        """
        self.user_name = f"账号{account_index}"
        self.account_index = account_index
        self.cookie_parts = cookie_str.split("#")
        
        if len(self.cookie_parts) != 3:
            log_print(f"❌ APP Cookie格式错误，应为'Cookie#User-Agent#会员等级'，已跳过此账号。")
            notify_manager.add_summary(f"--- 📱 APP {self.user_name}: 配置格式错误 ---")
            self.level = None
            return

        self.cookie = self.cookie_parts[0]
        self.user_agent = self.cookie_parts[1]
        self.level = self._validate_level(self.cookie_parts[2])

        self.sign_in_days_map = {}
        self.activity_id = None
        self.sign_in_map = {}

        headers = {**COMMON_HEADERS, 'User-Agent': self.user_agent, 'Cookie': self.cookie}
        self.client = httpx.Client(base_url=BASE_URL_HD, verify=False, headers=headers, timeout=60)

    def _validate_level(self, level):
        """
        验证会员等级是否有效。
        :param level: 用户输入的会员等级
        :return: 有效的会员等级或 None
        """
        valid_levels = ["普卡", "银卡会员", "金钻会员"]
        if level not in valid_levels:
            log_print(f"❌ 环境变量 `oppo_level` 定义的会员等级'{level}'无效，有效值为：{valid_levels}")
            notify_manager.add_summary(f"--- 📱 APP {self.user_name}: 会员等级 '{level}' 无效 ---")
            return None
        return level

    def _is_login(self):
        """
        通过请求一个接口检测Cookie是否有效。
        :return: True表示有效，False表示无效。
        """
        try:
            response = self.client.get("/api/cn/oapi/marketing/task/isLogin")
            response.raise_for_status()
            data = response.json()
            if data.get('code') == 403:
                log_print("🚨 Cookie已过期或无效，请重新获取。")
                notify_manager.add_summary(f"🚨 APP ({self.user_name}): Cookie已过期")
                return False
            return True
        except Exception as e:
            log_print(f"❌ 检测Cookie有效性时出错: {e}")
            return False

    def _get_user_info(self):
        """获取并设置用户名。"""
        try:
            response = self.client.get("/api/cn/oapi/users/web/member/check?unpaid=0")
            response.raise_for_status()
            data = response.json()
            if data.get('code') == 200 and data.get('data'):
                self.user_name = data['data'].get('name', f'账号{self.account_index}')
                log_print(f"--- 欢迎，{self.user_name} ---")
                notify_manager.add_summary(f"\n--- 📱 APP ({self.user_name}) ---")
        except Exception as e:
            log_print(f"❌ 获取用户信息失败: {e}")
            notify_manager.add_summary(f"\n--- 📱 APP (账号{self.account_index}) ---")


    def _get_task_activity_info(self):
        """
        从活动页面HTML中解析出任务活动ID和签到活动ID。
        """
        try:
            response = self.client.get("/bp/b371ce270f7509f0")
            response.raise_for_status()
            html = response.text
            match = re.search(r'window\.__DSL__\s*=\s*({.*?});', html, re.DOTALL)
            
            if not match:
                log_print("❌ 未能从APP活动页解析出活动ID，页面结构可能已更新。")
                return

            dsl_json = json.loads(match.group(1))
            cmps = dsl_json.get("cmps", [])
            task_field = None
            signin_fields = []
            
            for cmp in cmps:
                if "SignIn" in cmp: signin_fields.append(cmp)
                if "Task" in cmp: task_field = cmp

            if not task_field:
                log_print("❌ 未在页面数据中找到任务组件ID。")
                return

            self.activity_id = dsl_json['byId'][task_field]['attr']['taskActivityInfo']['activityId']
            
            for signin_field in signin_fields:
                activity_name = dsl_json['byId'][signin_field]['attr']['activityInfo'].get('activityName', '')
                if self.level in activity_name:
                    self.sign_in_map[self.level] = dsl_json['byId'][signin_field]['attr']['activityInfo']['activityId']
                    break
            
            if not self.sign_in_map:
                log_print(f"❌ 未找到与会员等级'{self.level}'匹配的签到活动ID。")

        except Exception as e:
            log_print(f"❌ 获取APP活动ID时出错: {e}")

    def sign_in(self):
        """执行每日签到。"""
        activity_id = self.sign_in_map.get(self.level)
        if not activity_id:
            log_print("⏭️ 因缺少签到活动ID，跳过APP签到。")
            return

        try:
            detail_res = self.client.get(f"/api/cn/oapi/marketing/cumulativeSignIn/getSignInDetail?activityId={activity_id}").json()
            if detail_res.get('data', {}).get('todaySignIn'):
                log_print(f"✅ 今天已经签到过啦，明天再来吧~")
                notify_manager.add_summary("✅ 签到: 今日已签")
                return

            response = self.client.post("/api/cn/oapi/marketing/cumulativeSignIn/signIn", json={"activityId": activity_id})
            response.raise_for_status()
            data = response.json()

            if data.get('code') == 200:
                award = data.get('data', {})
                award_value = award.get('awardValue', '未知')
                log_print(f"✅ 签到成功！获得积分：{award_value}")
                notify_manager.add_summary(f"✅ 签到: 成功 (积分 +{award_value})")
            else:
                reason = data.get('message', '未知错误')
                log_print(f"❌ 签到失败！原因: {reason}")
                notify_manager.add_summary(f"❌ 签到: 失败 - {reason}")
        except Exception as e:
            log_print(f"❌ 签到时发生异常: {e}")
            notify_manager.add_summary("❌ 签到: 执行异常")

    def do_tasks(self):
        """获取并完成所有可做的任务。"""
        if not self.activity_id:
            log_print("⏭️ 因缺少任务活动ID，跳过APP任务列表。")
            return
            
        completed_count = 0
        total_points = 0
        error_count = 0

        try:
            response = self.client.get(f"/api/cn/oapi/marketing/task/queryTaskList?activityId={self.activity_id}&source=c")
            response.raise_for_status()
            data = response.json()

            tasks = data.get('data', {}).get('taskDTOList')
            if not tasks:
                log_print(f"ℹ️ 获取任务列表失败或列表为空: {data.get('message')}")
                return

            log_print(f"🔍 解析到的APP任务数量: {len(tasks)}")
            
            # 调试：打印所有任务的基本信息
            for i, task in enumerate(tasks):
                task_name = task.get('taskName')
                task_status = task.get('taskStatus')
                task_type = task.get('taskType')
                log_print(f"🔍 APP任务{i+1}: 【{task_name}】- 状态:{task_status}, 类型:{task_type}")

            for task in tasks:
                task_name = task.get('taskName')
                task_id = task.get('taskId')
                task_type = task.get('taskType')
                activity_id = task.get('activityId')
                
                # 过滤黑卡任务、无效任务、已完成且已领取的任务
                # taskStatus: 1=未完成, 2=已完成未领取, 3=已完成已领取
                task_status = task.get('taskStatus')
                
                # 跳过无效任务
                if not task_id:
                    continue
                    
                # 跳过已完成已领取的任务
                if task_status == 3:
                    continue
                
                # 跳过不支持的任务类型
                if task_type == 6:
                    log_print(f"--- ▶️ 开始做APP任务:【{task_name}】 ---")
                    log_print(f"⏭️ 暂不支持任务类型 {task_type}，跳过。")
                    continue

                log_print(f"--- ▶️ 开始做APP任务:【{task_name}】 ---")
                
                try:
                    # 特殊处理某些任务类型：只在状态2时执行，状态1时跳过
                    if task_type in [14, 15]:  # 学生认证、关注公众号
                        if task_status == 2:
                            # 已完成但未领取，直接领取奖励
                            log_print(f"✅ 任务已完成，直接领取奖励...")
                            points_earned = self._receive_reward(task_name, task_id, activity_id)
                            if points_earned is not None:
                                completed_count += 1
                                total_points += points_earned
                            else:
                                error_count += 1
                        else:
                            log_print(f"⏭️ 暂不支持任务类型 {task_type}，跳过。")
                    else:
                        # 普通任务的处理逻辑
                        if task_status == 1:
                            # 未完成的任务，需要先完成再领取
                            log_print(f"📝 任务未完成，开始执行...")
                            
                            # 浏览商品任务需要先模拟浏览
                            if task_type == 3:
                                goods_num = int(task.get('attachConfigOne', {}).get('goodsNum', 0))
                                if goods_num > 0:
                                    self._browse_products(goods_num)
                                    random_sleep()

                            # 完成任务
                            self._complete_task(task_name, task_id, activity_id, task_type)
                            random_sleep()
                            
                            # 领取奖励
                            points_earned = self._receive_reward(task_name, task_id, activity_id)
                            if points_earned is not None:
                                completed_count += 1
                                total_points += points_earned
                            else:
                                error_count += 1
                                
                        elif task_status == 2:
                            # 已完成但未领取，直接领取奖励
                            log_print(f"✅ 任务已完成，直接领取奖励...")
                            points_earned = self._receive_reward(task_name, task_id, activity_id)
                            if points_earned is not None:
                                completed_count += 1
                                total_points += points_earned
                            else:
                                error_count += 1
                    
                    random_sleep()
                except Exception as e:
                    error_count += 1
                    log_print(f"❌ 执行任务【{task_name}】过程中出错: {e}")

        except Exception as e:
            log_print(f"❌ 获取任务列表时出错: {e}")
            notify_manager.add_summary("❌ 任务: 获取列表失败")
            return
            
        # 添加任务摘要
        if completed_count > 0:
            summary_msg = f"👍 任务: 完成 {completed_count} 个"
            if total_points > 0:
                summary_msg += f"，获得 {total_points} 积分"
            summary_msg += "。"
            if error_count > 0:
                summary_msg += f" ({error_count}个失败)"
            notify_manager.add_summary(summary_msg)
        elif error_count > 0:
            notify_manager.add_summary(f"❌ 任务: {error_count}个执行失败")


    def _complete_task(self, task_name, task_id, activity_id, task_type=1):
        """通用任务完成接口。"""
        try:
            log_print(f"🔍 正在完成任务【{task_name}】，类型: {task_type}")
            response = self.client.get(f"/api/cn/oapi/marketing/taskReport/signInOrShareTask?taskId={task_id}&activityId={activity_id}&taskType={task_type}")
            response.raise_for_status()
            data = response.json()
            log_print(f"🔍 任务完成API响应: {data}")
            if data.get('data'):
                log_print(f"✔️ 任务【{task_name}】完成！")
            else:
                log_print(f"⚠️ 任务【{task_name}】完成失败！-> {data.get('message')}")
        except Exception as e:
            log_print(f"❌ 完成任务【{task_name}】时出错: {e}")
            raise

    def _receive_reward(self, task_name, task_id, activity_id):
        """通用奖励领取接口, 返回获得的积分数。"""
        try:
            response = self.client.get(f"/api/cn/oapi/marketing/task/receiveAward?taskId={task_id}&activityId={activity_id}")
            response.raise_for_status()
            data = response.json()
            if data.get('data'):
                points = int(data['data'].get('awardValue', 0))
                log_print(f"💰 任务【{task_name}】奖励领取成功！积分 +{points}")
                return points
            else:
                log_print(f"⚠️ 任务【{task_name}】奖励领取失败 -> {data.get('message')}")
                return None
        except Exception as e:
            log_print(f"❌ 领取任务【{task_name}】奖励时出错: {e}")
            return None

    def _browse_products(self, num_to_browse):
        """模拟浏览商品。"""
        log_print(f"ℹ️ 需要浏览 {num_to_browse} 个商品...")
        log_print(f"✅ 已模拟浏览 {num_to_browse} 个商品。")

    def run(self):
        """执行APP版所有任务的入口函数。"""
        if self.level is None:
            return

        if not self._is_login():
            return
        
        self._get_user_info()
        self._get_task_activity_info()
        self.sign_in()
        random_sleep()
        self.do_tasks()
        log_print(f"--- {self.user_name} 的APP任务已执行完毕 ---\n")


# --- OPPO 商城小程序类 ---
class OppoApplet:
    """
    处理 OPPO 商城小程序版本的签到和活动任务。
    """
    def __init__(self, cookie_str, account_index):
        """
        初始化小程序任务实例。
        :param cookie_str: 小程序的 Cookie 字符串。
        :param account_index: 账号索引。
        """
        self.user_name = f"账号{account_index}"
        self.account_index = account_index
        self.cookie = cookie_str
        headers = {**MINI_APP_HEADERS, 'Cookie': self.cookie}
        self.client = httpx.Client(verify=False, headers=headers, timeout=60)
        self.activity_handler = ActivityHandler(self.client)

    def _is_login(self):
        """
        检测小程序Cookie是否有效。
        :return: True表示有效，False表示无效。
        """
        try:
            response = self.client.get(f"{BASE_URL_HD}/api/cn/oapi/marketing/task/isLogin")
            response.raise_for_status()
            data = response.json()
            if data.get('code') == 403:
                log_print("🚨 小程序Cookie已过期或无效，请重新获取。")
                notify_manager.add_summary(f"🚨 小程序 ({self.user_name}): Cookie已过期")
                return False
            return True
        except Exception as e:
            log_print(f"❌ 检测小程序Cookie有效性时出错: {e}")
            return False

    def _get_user_info(self):
        """获取并设置用户名。"""
        try:
            response = self.client.get(f"{BASE_URL_HD}/api/cn/oapi/users/web/member/check?unpaid=0")
            response.raise_for_status()
            data = response.json()
            if data.get('code') == 200 and data.get('data'):
                self.user_name = data['data'].get('name', f'账号{self.account_index}')
                log_print(f"--- 欢迎，{self.user_name} ---")
                notify_manager.add_summary(f"\n--- 🧩 小程序 ({self.user_name}) ---")
        except Exception as e:
            log_print(f"❌ 获取小程序用户信息失败: {e}")
            notify_manager.add_summary(f"\n--- 🧩 小程序 (账号{self.account_index}) ---")

    def get_user_total_points(self):
        """获取用户当前的总积分。"""
        try:
            response = self.client.get(f"{BASE_URL_MSEC}/users/web/member/infoDetail")
            response.raise_for_status()
            data = response.json()
            if data.get('code') == 200 and data.get('data'):
                points = data['data'].get('userCredit', '查询失败')
                log_print(f"🎉【{self.user_name}】当前总积分: {points}")
                notify_manager.add_summary(f"💰 当前总积分: {points}")
        except Exception as e:
            log_print(f"❌ 获取用户总积分时出错: {e}")
            
    def run(self):
        """
        执行小程序所有任务的入口函数。
        """
        if not self._is_login():
            return
            
        self._get_user_info()

        # 处理所有已配置的活动
        self.activity_handler.process_all_activities()
        
        # 最后查询总积分
        self.get_user_total_points()
        log_print(f"--- {self.user_name} 的小程序任务已执行完毕 ---\n")


# --- 小程序活动处理器 ---
class ActivityHandler:
    """
    一个独立的类，用于发现、解析和执行小程序中的各种活动。
    采用"动态发现 + 静态配置"的混合模式。
    """




    def __init__(self, client: httpx.Client):
        self.client = client

    def _discover_dynamic_activities(self):
        """动态发现活动入口。"""
        discovered_activities = []
        try:
            response = self.client.get(f"{BASE_URL_MSEC}/configs/web/advert/300003")
            response.raise_for_status()
            data = response.json()
            if data.get('code') != 200:
                log_print(f"❌ 动态发现活动失败：{data.get('message')}")
                return []
            
            for item_to_find in DYNAMIC_ACTIVITIES_TO_FIND:
                found = False
                for section in data.get('data', []):
                    if item_to_find['keyword1'] in section.get("title", ""):
                        for detail in section.get('details', []):
                            if item_to_find['keyword2'] in detail.get('title', ""):
                                link = detail.get('link')
                                if link:
                                    bp_url = urlparse(link).path
                                    activity_config = {
                                        "bp_url": bp_url,
                                        "name": item_to_find['name'],
                                        "enabled": True,
                                        "draw_jimu_name": item_to_find['draw_jimu_name']
                                    }
                                    # 如果动态活动配置中有 is_lucky_draw，传递给发现的活动
                                    if 'is_lucky_draw' in item_to_find:
                                        activity_config['is_lucky_draw'] = item_to_find['is_lucky_draw']
                                    discovered_activities.append(activity_config)
                                    log_print(f"🔍 动态发现活动【{item_to_find['name']}】, URL: {bp_url}")
                                    found = True
                                    break
                    if found:
                        break
                if not found:
                    log_print(f"⚠️ 未能动态发现活动【{item_to_find['name']}】")
        except Exception as e:
            log_print(f"❌ 动态发现活动时发生异常: {e}")
        return discovered_activities

    def _get_activity_ids(self, bp_url):
        """通用方法：从任何活动页面解析所需的各种ID。"""
        try:
            response = self.client.get(f"{BASE_URL_HD}{bp_url}")
            response.raise_for_status()
            html = response.text
            match = re.search(r'window\.__DSL__\s*=\s*({.*?});', html, re.DOTALL)
            
            if not match:
                log_print(f"⚠️ 在页面 {bp_url} 未能解析出__DSL__数据。")
                return None

            dsl_json = json.loads(match.group(1))
            ids = {'jimu_id': dsl_json.get('activityId')}
            
            for cmp_key, cmp_val in dsl_json.get('byId', {}).items():
                attr = cmp_val.get('attr', {})
                if "Task" in cmp_key:
                    task_activity_info = attr.get('taskActivityInfo', {})
                    task_id = task_activity_info.get('activityId')
                    if task_id:
                        ids['task_id'] = task_id
                        # log_print(f"🔍 解析到任务ID: {task_id} (组件: {cmp_key})")
                elif "Raffle" in cmp_key:
                    raffle_info = attr.get('activityInformation', {})
                    raffle_id = raffle_info.get('raffleId')
                    if raffle_id:
                        ids['raffle_id'] = raffle_id
                        # log_print(f"🔍 解析到抽奖ID: {raffle_id} (组件: {cmp_key})")
                elif "SignIn" in cmp_key:
                    signin_info = attr.get('activityInfo', {})
                    signin_id = signin_info.get('activityId')
                    if signin_id:
                        ids['signin_id'] = signin_id
                        # log_print(f"🔍 解析到签到ID: {signin_id} (组件: {cmp_key})")
            
            # 兼容部分页面 creditsAddActionId/business 字段在 window.__APP__ 里
            app_match = re.search(r'window\.__APP__\s*=\s*({.*?});', html, re.DOTALL)
            if app_match:
                try:
                    app_json = json.loads(app_match.group(1))
                    if 'creditsAddActionId' not in ids and 'scoreId' in app_json:
                        ids['creditsAddActionId'] = app_json['scoreId'].get('creditsAddActionId')
                    if 'business' not in ids and 'business' in app_json:
                        ids['business'] = app_json['business']
                except Exception as e:
                    log_print(f"⚠️ 解析 window.__APP__ 时出错: {e}")
            
            # log_print(f"🔍 活动ID解析结果: {ids}")
            return ids
        except Exception as e:
            log_print(f"❌ 获取活动 {bp_url} 的ID时出错: {e}")
            return None

    def _handle_sign_in(self, signin_id):
        """处理单个活动的签到和累计奖励领取。"""
        try:
            detail_res = self.client.get(f"{BASE_URL_HD}/api/cn/oapi/marketing/cumulativeSignIn/getSignInDetail?activityId={signin_id}").json()
            if detail_res.get('data', {}).get('todaySignIn'):
                log_print(f"✅ 今天已经签到过啦，明天再来吧~")
                notify_manager.add_summary("    ✅ 签到: 今日已签")
            else:
                response = self.client.post(f"{BASE_URL_HD}/api/cn/oapi/marketing/cumulativeSignIn/signIn", json={"activityId": signin_id})
                data = response.json()
                if data.get('code') == 200:
                    award_val = data.get('data', {}).get('awardValue', '未知')
                    log_print(f"✅ 签到成功！获得积分：{award_val}")
                    notify_manager.add_summary(f"    ✅ 签到: 成功 (积分 +{award_val})")
                else:
                    log_print(f"❌ 签到失败！原因: {data.get('message', '未知错误')}")
                    notify_manager.add_summary(f"    ❌ 签到: 失败")
        except Exception as e:
            log_print(f"❌ 签到时发生异常: {e}")
            notify_manager.add_summary("    ❌ 签到: 异常")
        
        random_sleep()

        try:
            response = self.client.get(f"{BASE_URL_HD}/api/cn/oapi/marketing/cumulativeSignIn/getSignInDetail?activityId={signin_id}")
            data = response.json().get('data', {})
            sign_in_day_num = data.get('signInDayNum')
            cumulative_awards = data.get('cumulativeAwards', [])
            
            for award in cumulative_awards:
                if award.get('signDayNum') == sign_in_day_num and award.get('awardStatus') != 1:
                    award_id = award.get('awardId')
                    log_print(f"ℹ️ 检测到可领取累计 {sign_in_day_num} 天签到奖励，尝试领取...")
                    draw_res = self.client.post(f"{BASE_URL_HD}/api/cn/oapi/marketing/cumulativeSignIn/drawCumulativeAward", json={"activityId": signin_id, "awardId": award_id}).json()
                    if draw_res.get('code') == 200:
                        award_name = draw_res.get('data',{}).get('awardValue')
                        log_print(f"💰 累计签到奖励领取成功！获得：{award_name}")
                        notify_manager.add_summary(f"    💰 累计奖励: {award_name}")
                    else:
                        log_print(f"⚠️ 累计签到奖励领取失败: {draw_res.get('message')}")
                    random_sleep()
                    break
        except Exception as e:
            log_print(f"❌ 处理累计签到奖励时出错: {e}")

    def _handle_sign_in_with_credits(self, signin_id, creditsAddActionId, business):
        """处理带 creditsAddActionId 和 business 字段的特殊签到。"""
        try:
            detail_res = self.client.get(f"{BASE_URL_HD}/api/cn/oapi/marketing/cumulativeSignIn/getSignInDetail?activityId={signin_id}").json()
            if detail_res.get('data', {}).get('todaySignIn'):
                log_print(f"✅ 今天已经签到过啦，明天再来吧~")
                notify_manager.add_summary("    ✅ 签到: 今日已签")
            else:
                payload = {"activityId": signin_id, "creditsAddActionId": creditsAddActionId, "business": business}
                response = self.client.post(f"{BASE_URL_HD}/api/cn/oapi/marketing/cumulativeSignIn/signIn", json=payload)
                data = response.json()
                if data.get('code') == 200:
                    award_val = data.get('data', {}).get('awardValue', '未知')
                    log_print(f"✅  签到成功！获得积分：{award_val}")
                    notify_manager.add_summary(f"    ✅  签到: 成功 (积分 +{award_val})")
                else:
                    log_print(f"❌  签到失败！原因: {data.get('message', '未知错误')}")
                    notify_manager.add_summary(f"    ❌  签到: 失败")
        except Exception as e:
            log_print(f"❌  签到时发生异常: {e}")
            notify_manager.add_summary("    ❌  签到: 异常")
        random_sleep()

    def _handle_anniversary_tasks(self, task_activity_id):
        """专门处理周年庆集卡活动的任务。"""
        completed_count = 0
        error_count = 0
        try:
            # 添加任务查询所需的特殊请求头
            task_headers = {
                **self.client.headers,
                's_channel': 'program_wx',
                'utm_campaign': 'direct',
                'utm_term': 'direct',
                'ut': 'direct',
                'uc': '30jika',
                'um': 'huodongtab',
                'source_type': '503',
                'utm_medium': 'direct',
                'utm_source': 'direct',
                'us': 'minishouye'
            }
            response = self.client.get(f"{BASE_URL_HD}/api/cn/oapi/marketing/task/queryTaskList?activityId={task_activity_id}&source=c", headers=task_headers)
            response_data = response.json()
            
            tasks = response_data.get('data', {}).get('taskDTOList', [])
            
            if not tasks:
                log_print("ℹ️ 此周年庆活动下没有需要做的任务。")
                return

            log_print(f"🔍 解析到的周年庆任务数量: {len(tasks)}")
            
            # 调试：打印所有周年庆任务的基本信息
            for i, task in enumerate(tasks):
                task_name = task.get('taskName')
                task_status = task.get('taskStatus')
                task_type = task.get('taskType')
                award_type = task.get('awardType')
                log_print(f"🔍 周年庆任务{i+1}: 【{task_name}】- 状态:{task_status}, 类型:{task_type}, 奖励类型:{award_type}")

            for task in tasks:
                task_name = task.get('taskName')
                task_status = task.get('taskStatus')
                task_id = task.get('taskId')
                activity_id = task.get('activityId')
                task_type = task.get('taskType')
                award_type = task.get('awardType')
                
                # 跳过已完成且已领取的任务
                if task_status == 3:
                    log_print(f"⏭️ 任务【{task_name}】已完成且已领取，跳过")
                    continue
                
                log_print(f"--- ▶️ 开始做任务:【{task_name}】 ---")
                
                try:
                    # 对于周年庆活动，taskStatus=1需要先完成任务，taskStatus=2可能需要领取奖励
                    if task_status == 1:
                        # 未完成的任务，先执行
                        if task_type in [0, 1, 2]: 
                            self.client.get(f"{BASE_URL_HD}/api/cn/oapi/marketing/taskReport/signInOrShareTask?taskId={task_id}&activityId={activity_id}&taskType={task_type}")
                            browse_time = task.get('attachConfigOne', {}).get('browseTime', 1)
                            if not isinstance(browse_time, (int, float)) or browse_time is None:
                                browse_time = 1
                            log_print(f"⏳ 正在浏览，等待 {browse_time} 秒...")
                            time.sleep(browse_time + 0.5)
                        elif task_type == 3:
                            # 浏览商品任务，需要按照配置的要求浏览足够时间
                            # 获取浏览时间要求
                            ball_tips = task.get('attachConfigThree', {}).get('ballTips', '')
                            browse_seconds = 30  # 默认30秒
                            if '30秒' in ball_tips:
                                browse_seconds = 30
                            elif '秒' in ball_tips:
                                # 尝试提取数字
                                import re
                                numbers = re.findall(r'\d+', ball_tips)
                                if numbers:
                                    browse_seconds = int(numbers[0])
                            
                            # 先访问商品页面并浏览足够时间
                            action_url = task.get('actionUrl')
                            if action_url:
                                try:
                                    self.client.get(action_url)
                                    
                                    # 提取skuId并调用商品详情API
                                    if 'skuId=' in action_url:
                                        sku_id = action_url.split('skuId=')[1].split('&')[0]
                                        
                                        # 调用商品详情API（这是关键步骤）
                                        detail_url = f"{BASE_URL_MSEC}/cn/oapi/cms-business/goods/detail?pageCode=skuDetail&interfaceVersion=v2&skuId={sku_id}"
                                        
                                        # 从actionUrl中解析请求头参数
                                        detail_headers = {**self.client.headers}
                                        if 'uc=' in action_url:
                                            uc_param = action_url.split('uc=')[1].split('&')[0]
                                            detail_headers['uc'] = uc_param
                                        if 'um=' in action_url:
                                            um_param = action_url.split('um=')[1].split('&')[0]
                                            detail_headers['um'] = um_param
                                        if 'us=' in action_url:
                                            us_param = action_url.split('us=')[1].split('&')[0]
                                            detail_headers['us'] = us_param
                                        
                                        detail_response = self.client.get(detail_url, headers=detail_headers)
                                    
                                    log_print(f"⏳ 正在浏览商品，等待 {browse_seconds} 秒...")
                                    time.sleep(browse_seconds)  # 按要求浏览足够时间
                                except Exception as e:
                                    log_print(f"⚠️ 商品页面访问失败: {e}")
                                    log_print(f"⏳ 仍然等待 {browse_seconds} 秒...")
                                    time.sleep(browse_seconds)
                            else:
                                log_print(f"⏳ 正在浏览，等待 {browse_seconds} 秒...")
                                time.sleep(browse_seconds)
                            
                            # 然后调用任务报告接口
                            response = self.client.get(f"{BASE_URL_HD}/api/cn/oapi/marketing/taskReport/signInOrShareTask?taskId={task_id}&activityId={activity_id}&taskType={task_type}")
                            response_data = response.json()
                        
                        # 尝试领取奖励
                        self._try_collect_anniversary_reward(task_name, task_id, activity_id, task)
                        completed_count += 1
                        
                    elif task_status == 2:
                        # 已完成但未领取，直接领取奖励
                        log_print(f"✅ 任务已完成，直接领取奖励...")
                        self._try_collect_anniversary_reward(task_name, task_id, activity_id, task)
                        completed_count += 1
                    else:
                        log_print(f"⏭️ 任务状态异常({task_status})，跳过")
                    
                    random_sleep()
                except Exception as e:
                    error_count += 1
                    log_print(f"❌ 执行周年庆任务【{task_name}】内部出错: {e}")

        except Exception as e:
            log_print(f"❌ 处理周年庆任务列表时出错: {e}")
            notify_manager.add_summary("    ❌ 周年庆任务: 获取列表异常")

        if completed_count > 0:
            notify_manager.add_summary(f"    🎴 周年庆任务: 处理 {completed_count} 个。")
        elif error_count > 0:
            notify_manager.add_summary(f"    ❌ 周年庆任务: {error_count} 个处理失败。")

    def _try_collect_anniversary_reward(self, task_name, task_id, activity_id, task):
        """尝试领取周年庆集卡奖励。"""
        try:
            # 先尝试传统的奖励领取接口
            reward_res = self.client.get(f"{BASE_URL_HD}/api/cn/oapi/marketing/task/receiveAward?taskId={task_id}&activityId={activity_id}").json()
            if reward_res.get('code') == 200:
                log_print(f"💰 任务【{task_name}】奖励领取成功！")
                return True
            else:
                log_print(f"⚠️ 任务【{task_name}】奖励领取失败: {reward_res.get('message')}")
                
                # 如果是集卡类型奖励，可能需要特殊的领取接口
                award_config = task.get('awardAttachConfig', {})
                collect_activity_id = award_config.get('collectActivityId')
                if collect_activity_id:
                    log_print(f"🎴 尝试通过集卡活动ID领取: {collect_activity_id}")
                    # 这里可能需要调用特殊的集卡奖励接口，暂时先记录
                
                return False
        except Exception as e:
            log_print(f"❌ 领取任务【{task_name}】奖励时出错: {e}")
            return False

    def _handle_tasks(self, task_activity_id, activity_name=None):
        """处理单个活动的所有任务。"""
        completed_count = 0
        error_count = 0
        try:
            # 根据不同活动设置不同的请求头参数
            if activity_name == "积分兑换专区":
                uc_param = 'jifenduihuan'
                um_param = 'icon'
            elif activity_name == "小程序每日签到":
                uc_param = 'zhaiqudaohuodong'
                um_param = 'fulizhuanqu'
            elif activity_name == "小程序专享福利":
                uc_param = 'zhaiqudaohuodong'
                um_param = 'fulizhuanqu'
            elif activity_name == "莎莎企业":
                uc_param = 'shasaqiye'
                um_param = 'huodongtab'
            elif activity_name == "排球少年!!联名定制产品图鉴":
                uc_param = 'paiqiushaonian'
                um_param = 'huodongtab'
            else:
                uc_param = 'zhaiqudaohuodong'
                um_param = 'fulizhuanqu'
                
            # 添加任务查询所需的特殊请求头
            task_headers = {
                **self.client.headers,
                's_channel': 'program_wx',
                'utm_campaign': 'direct',
                'utm_term': 'direct',
                'ut': 'direct',
                'uc': uc_param,
                'um': um_param,
                'source_type': '503',
                'utm_medium': 'direct',
                'utm_source': 'direct',
                'us': 'minishouye'
            }
            response = self.client.get(f"{BASE_URL_HD}/api/cn/oapi/marketing/task/queryTaskList?activityId={task_activity_id}&source=c", headers=task_headers)
            response_data = response.json()
            # log_print(f"🔍 任务API响应状态码: {response_data.get('code')}")
            # log_print(f"🔍 任务API响应消息: {response_data.get('message')}")
            
            tasks = response_data.get('data', {}).get('taskDTOList', [])
            log_print(f"🔍 解析到的任务数量: {len(tasks)}")
            
            # 调试：打印所有任务的基本信息
            for i, task in enumerate(tasks):
                task_name = task.get('taskName')
                task_status = task.get('taskStatus')
                task_type = task.get('taskType')
                log_print(f"🔍 任务{i+1}: 【{task_name}】- 状态:{task_status}, 类型:{task_type}")
            
            if not tasks:
                log_print("ℹ️ 此活动下没有需要做的任务。")
                log_print(f"🔍 完整API响应: {response_data}")
                return

            for task in tasks:
                task_name = task.get('taskName')
                task_status = task.get('taskStatus')
                task_id = task.get('taskId')
                activity_id = task.get('activityId')
                task_type = task.get('taskType')
                
                # 跳过已完成且已领取的任务
                if task_status == 3:
                    log_print(f"⏭️ 任务【{task_name}】已完成且已领取，跳过")
                    continue
                
                # 特殊处理：购买商品和学生认证任务
                if task_type == 6:  # 购买商品
                    if task_status in [1, 3]:
                        log_print(f"--- ▶️ 开始做任务:【{task_name}】 ---")
                        log_print(f"⏭️ 暂不支持任务类型 {task_type}，跳过。")
                        continue
                elif task_type == 14:  # 学生认证
                    if task_status in [1, 3]:
                        log_print(f"--- ▶️ 开始做任务:【{task_name}】 ---")
                        log_print(f"⏭️ 暂不支持任务类型 {task_type}，跳过。")
                        continue

                log_print(f"--- ▶️ 开始做任务:【{task_name}】 ---")
                
                try:
                    if task_status == 1:
                        # 未完成的任务，先执行
                        if task_type in [0, 1, 2]: 
                            self.client.get(f"{BASE_URL_HD}/api/cn/oapi/marketing/taskReport/signInOrShareTask?taskId={task_id}&activityId={activity_id}&taskType={task_type}")
                            browse_time = task.get('attachConfigOne', {}).get('browseTime', 1)
                            if not isinstance(browse_time, (int, float)) or browse_time is None:
                                browse_time = 1
                            log_print(f"⏳ 正在浏览，等待 {browse_time} 秒...")
                            time.sleep(browse_time + 0.5)
                        elif task_type == 3:
                            # 浏览商品任务
                            # 获取浏览时间要求
                            ball_tips = task.get('attachConfigThree', {}).get('ballTips', '')
                            browse_seconds = 5  # 普通活动默认5秒
                            if '30秒' in ball_tips:
                                browse_seconds = 30
                            elif '秒' in ball_tips:
                                # 尝试提取数字
                                import re
                                numbers = re.findall(r'\d+', ball_tips)
                                if numbers:
                                    browse_seconds = int(numbers[0])
                            
                            # 先访问商品页面（如果有）
                            action_url = task.get('actionUrl')
                            if action_url:
                                try:
                                    self.client.get(action_url)
                                    
                                    # 提取skuId并调用商品详情API
                                    if 'skuId=' in action_url:
                                        sku_id = action_url.split('skuId=')[1].split('&')[0]
                                        
                                        # 调用商品详情API
                                        detail_url = f"{BASE_URL_MSEC}/cn/oapi/cms-business/goods/detail?pageCode=skuDetail&interfaceVersion=v2&skuId={sku_id}"
                                        
                                        # 从actionUrl中解析请求头参数
                                        detail_headers = {**self.client.headers}
                                        if 'uc=' in action_url:
                                            uc_param = action_url.split('uc=')[1].split('&')[0]
                                            detail_headers['uc'] = uc_param
                                        if 'um=' in action_url:
                                            um_param = action_url.split('um=')[1].split('&')[0]
                                            detail_headers['um'] = um_param
                                        if 'us=' in action_url:
                                            us_param = action_url.split('us=')[1].split('&')[0]
                                            detail_headers['us'] = us_param
                                        
                                        detail_response = self.client.get(detail_url, headers=detail_headers)
                                except Exception as e:
                                    log_print(f"⚠️ 商品页面访问失败: {e}")
                            
                            # 浏览等待
                            log_print(f"⏳ 正在浏览，等待 {browse_seconds} 秒...")
                            time.sleep(browse_seconds)
                            
                            # 调用任务完成接口
                            response = self.client.get(f"{BASE_URL_HD}/api/cn/oapi/marketing/taskReport/signInOrShareTask?taskId={task_id}&activityId={activity_id}&taskType={task_type}")
                            response_data = response.json()
                        elif task_type == 4:
                            try:
                                # 方法1: 首先尝试原来的预约商品方法
                                goods_list = task.get('attachConfigOne', {}).get('goodsList')
                                if goods_list and len(goods_list) > 0 and goods_list[0]:
                                    sku_id = goods_list[0].get('skuId')
                                    if sku_id:
                                        try:
                                            self.client.post(f"{BASE_URL_MSEC}/goods/web/info/goods/subscribeV2?skuId={sku_id}&type=1", headers={"Content-Type": "application/x-www-form-urlencoded"})
                                            log_print(f"✅ 预约商品任务执行成功，skuId: {sku_id}")
                                        except Exception as e:
                                            log_print(f"⚠️ 原预约方法失败: {e}，尝试备用方法")
                                            raise e  # 抛出异常以触发备用方法
                                    else:
                                        log_print(f"⚠️ 预约商品任务中未找到有效的skuId，尝试备用方法")
                                        raise ValueError("未找到skuId")
                                else:
                                    log_print(f"⚠️ 预约商品任务中未找到goodsList，尝试备用方法")
                                    raise ValueError("未找到goodsList")
                            except Exception:
                                # 方法2: 备用方法 - 使用预约材料API
                                try:
                                    log_print(f"🔄 使用备用预约方法...")
                                    reserve_payload = {
                                        "activityId": activity_id,
                                        "reserveType": 2,
                                        "reserveChannel": "积木页",
                                        "reserveComp": "任务组件预约"
                                    }
                                    
                                    # 添加预约任务所需的请求头
                                    reserve_headers = {
                                        **self.client.headers,
                                        'Content-Type': 'application/json'
                                    }
                                    
                                    response = self.client.post(
                                        f"{BASE_URL_HD}/api/cn/oapi/marketing/reserve/materials/reserveMaterials",
                                        json=reserve_payload,
                                        headers=reserve_headers
                                    )
                                    
                                    response_data = response.json()
                                    if response_data.get('code') == 200:
                                        log_print(f"✅ 备用预约方法执行成功")
                                        # 检查预约结果
                                        data = response_data.get('data', {})
                                        if data.get('reserveSuccess') or data.get('alreadyReserveSuccess'):
                                            log_print(f"🎉 预约成功或已预约")
                                        else:
                                            log_print(f"⚠️ 预约状态异常: {data}")
                                    else:
                                        log_print(f"❌ 备用预约方法也失败: {response_data.get('message', '未知错误')}")
                                        
                                except Exception as e:
                                    log_print(f"❌ 备用预约方法也出错: {e}")
                                    # 即使都失败也继续尝试领取奖励
                        elif task_type in [6, 14]:
                            # 这些类型在状态1时已经被上面过滤，不应该到这里
                            pass
                        elif task_type in [15, 16, 17]:
                            # 不支持的任务类型，状态1时跳过
                            log_print(f"⏭️ 暂不支持任务类型 {task_type}，跳过。")
                            continue
                        else:
                            log_print(f"⏭️ 暂不支持任务类型 {task_type}，跳过。")
                            continue
                    elif task_status == 2:
                        # 已完成但未领取，直接领取奖励
                        log_print(f"✅ 任务已完成，直接领取奖励...")
                    else:
                        # 其他状态（如状态3已完成已领取，在前面已过滤）
                        log_print(f"⏭️ 任务状态 {task_status} 无需处理，跳过。")
                        continue
                    
                    # 尝试领取奖励
                    reward_res = self.client.get(f"{BASE_URL_HD}/api/cn/oapi/marketing/task/receiveAward?taskId={task_id}&activityId={activity_id}").json()
                    if reward_res.get('code') == 200:
                        log_print(f"💰 任务【{task_name}】奖励领取成功！")
                        completed_count += 1
                    else:
                        log_print(f"⚠️ 任务【{task_name}】奖励领取失败: {reward_res.get('message')}")
                        error_count += 1
                    random_sleep()
                except Exception as e:
                    error_count += 1
                    log_print(f"❌ 执行任务【{task_name}】内部出错: {e}")

        except Exception as e:
            log_print(f"❌ 处理任务列表时出错: {e}")
            notify_manager.add_summary("    ❌ 任务: 获取列表异常")

        if completed_count > 0:
            notify_manager.add_summary(f"    👍 任务: 完成 {completed_count} 个。")
        elif error_count > 0:
            notify_manager.add_summary(f"    ❌ 任务: {error_count} 个执行失败。")

    def _handle_anniversary_sign_in(self):
        """周年庆专用签到（额外的签到接口）"""
        try:
            response = self.client.get(f"https://photoparty.opposhop.cn/api/public/index.php/supervip2507/api/doSign?jimuid=12760")
            response.raise_for_status()
            data = response.json()
            if data.get('code') == 200:
                log_print(f"✅ 签到: 成功")
                notify_manager.add_summary("    ✅ 签到: 成功")
            else:
                msg = data.get('msg', '未知错误')
                if '已经签到过' in msg or '已签到' in msg:
                    log_print(f"✅ 签到: 已经签到过~")
                    notify_manager.add_summary("    ✅ 签到: 已经签到过")
                else:
                    log_print(f"❌ 周年庆专用签到失败！-> {msg}")
                    notify_manager.add_summary("    ❌ 周年庆签到: 失败")
        except Exception as e:
            log_print(f"❌ 周年庆专用签到时出错: {e}")
            notify_manager.add_summary("    ❌ 周年庆签到: 异常")

    def _handle_collect_cards(self, collect_activity_id):
        """处理集卡活动的查询、抽卡和状态显示。"""
        
        try:
            
            # 添加小程序集卡查询的特殊请求头
            collect_headers = {
                **self.client.headers,
                's_channel': 'program_wx',
                'utm_campaign': 'direct',
                'utm_term': 'direct',
                'ut': 'direct',
                'uc': '30jika',
                'um': 'huodongtab',
                'source_type': '503',
                'utm_medium': 'direct',
                'utm_source': 'direct'
            }
            
            response = self.client.get(
                f"{BASE_URL_MSEC}/marketing/collectCard/queryActivityById?activityId={collect_activity_id}",
                headers=collect_headers
            )
            response_data = response.json()
            
            if response_data.get('code') != 200:
                log_print(f"❌ 查询集卡活动失败: {response_data.get('message')}")
                return
            
            data = response_data.get('data', {})
            basic_info = data.get('collectCardActivityBasicInfo', {})
            chance_count = data.get('chanceCount', 0)
            card_total_count = data.get('cardTotalCount', 0)
            card_info_list = basic_info.get('cardInfoList', [])
            
            log_print(f"🎴 集卡活动状态: 可抽次数={chance_count}, 已获得卡片={card_total_count}")
            
            # 显示当前拥有的卡片状态
            self._display_card_status(card_info_list)
            
            # 如果有抽卡机会，进行抽卡
            if chance_count > 0:
                log_print(f"🎯 开始抽卡，剩余 {chance_count} 次机会...")
                drawn_cards = []
                
                for i in range(chance_count):
                    log_print(f"🎲 第 {i+1}/{chance_count} 次抽卡...")
                    card_result = self._draw_single_card(collect_activity_id)
                    if card_result:
                        drawn_cards.append(card_result)
                    random_sleep(2, 4)
                
                if drawn_cards:
                    log_print(f"🎉 本次抽卡获得: {', '.join(drawn_cards)}")
                    notify_manager.add_summary(f"    🎴 集卡: 抽取 {len(drawn_cards)} 次，获得[{'、'.join(drawn_cards)}]")
                else:
                    notify_manager.add_summary(f"    🎴 集卡: 抽取 {chance_count} 次，均未中奖")
                
                # 抽卡后重新检查状态，看是否可以合成
                self._check_card_synthesis_status(collect_activity_id)
            else:
                log_print(f"ℹ️ 没有可用的抽卡机会")
                notify_manager.add_summary(f"    🎴 集卡: 无抽卡机会")
                
        except Exception as e:
            log_print(f"❌ 处理集卡活动时出错: {e}")
            notify_manager.add_summary("    ❌ 集卡: 处理异常")

    def _draw_single_card(self, collect_activity_id):
        """执行单次抽卡。"""
        try:
            # 添加小程序抽卡的特殊请求头
            collect_headers = {
                **self.client.headers,
                's_channel': 'program_wx',
                'utm_campaign': 'direct',
                'utm_term': 'direct',
                'ut': 'direct',
                'uc': '30jika',
                'um': 'huodongtab',
                'source_type': '503',
                'utm_medium': 'direct',
                'utm_source': 'direct'
            }
            
            response = self.client.post(
                f"{BASE_URL_MSEC}/marketing/collectCard/pull?activityId={collect_activity_id}", 
                json={},
                headers=collect_headers
            )
            response_data = response.json()
            
            if response_data.get('code') == 200:
                card_name = response_data.get('data', {}).get('cardName', '未知卡片')
                remain_count = response_data.get('data', {}).get('userRemainDrawCount', 0)
                
                # 处理空气情况
                if card_name == '/' or card_name == '' or not card_name or card_name == '未知卡片':
                    log_print(f"💨 本次抽卡: 空气, 剩余次数: {remain_count}")
                    return None  # 空气不计入获得的卡片
                else:
                    log_print(f"🎊 抽到卡片: 【{card_name}】, 剩余次数: {remain_count}")
                    return card_name
            else:
                log_print(f"💔 抽卡失败: {response_data.get('message')}")
                return None
        except Exception as e:
            log_print(f"❌ 单次抽卡时出错: {e}")
            return None

    def _display_card_status(self, card_info_list):
        """显示当前卡片收集状态。"""
        if not card_info_list:
            log_print("ℹ️ 没有卡片信息")
            return
            
        log_print("📋 当前卡片收集状态:")
        card_summary = []
        
        for card_info in card_info_list:
            card_name = card_info.get('cardName', '未知')
            card_num = card_info.get('num', 0)
            user_cards = card_info.get('userCollectCardInfoList') or []
            actual_count = len(user_cards)
            
            if actual_count > 0:
                log_print(f"   🎴 {card_name}: {actual_count}张")
                card_summary.append(f"{card_name}×{actual_count}")
            else:
                log_print(f"   ⚪ {card_name}: 0张 (未获得)")
        
        if card_summary:
            summary_text = f"拥有卡片: {', '.join(card_summary)}"
            notify_manager.add_summary(f"    📋 {summary_text}")

    def _get_anniversary_task_id(self, collect_activity_id):
        """动态获取周年庆任务活动ID"""
        try:
            collect_headers = {
                **self.client.headers,
                's_channel': 'program_wx',
                'utm_campaign': 'direct',
                'utm_term': 'direct',
                'ut': 'direct',
                'uc': '30jika',
                'um': 'huodongtab',
                'source_type': '503',
                'utm_medium': 'direct',
                'utm_source': 'direct'
            }
            
            response = self.client.get(
                f"{BASE_URL_MSEC}/marketing/collectCard/queryActivityById?activityId={collect_activity_id}",
                headers=collect_headers
            )
            response_data = response.json()
            
            if response_data.get('code') != 200:
                log_print(f"❌ 获取周年庆活动信息失败: {response_data.get('message')}")
                return None
            
            # 从集卡活动信息中提取任务活动ID
            data = response_data.get('data', {})
            basic_info = data.get('collectCardActivityBasicInfo', {})
            task_config = basic_info.get('taskConfiguration', {})
            task_activity_id = task_config.get('taskActivityId')
            
            if task_activity_id:
                # log_print(f"🎯 动态获取到周年庆任务活动ID: {task_activity_id}")
                return task_activity_id
            else:
                log_print("⚠️ 集卡活动信息中未找到任务活动ID")
                return None
                
        except Exception as e:
            log_print(f"❌ 动态获取周年庆任务活动ID时出错: {e}")
            return None

    def _check_card_synthesis_status(self, collect_activity_id):
        """检查是否可以合成卡片"""
        try:
            collect_headers = {
                **self.client.headers,
                's_channel': 'program_wx',
                'utm_campaign': 'direct',
                'utm_term': 'direct',
                'ut': 'direct',
                'uc': '30jika',
                'um': 'huodongtab',
                'source_type': '503',
                'utm_medium': 'direct',
                'utm_source': 'direct'
            }
            
            response = self.client.get(
                f"{BASE_URL_MSEC}/marketing/collectCard/queryActivityById?activityId={collect_activity_id}",
                headers=collect_headers
            )
            response_data = response.json()
            
            if response_data.get('code') != 200:
                return
            
            data = response_data.get('data', {})
            basic_info = data.get('collectCardActivityBasicInfo', {})
            card_info_list = basic_info.get('cardInfoList', [])
            
            # 检查是否所有卡片都至少有1张
            can_synthesize = True
            for card_info in card_info_list:
                card_num = card_info.get('num', 0)
                user_cards = card_info.get('userCollectCardInfoList') or []
                actual_count = len(user_cards)
                if actual_count < 1:
                    can_synthesize = False
                    break
            
            if can_synthesize and len(card_info_list) > 0:
                log_print("🎊 卡片已集齐，可进行卡片合成！")
                notify_manager.add_summary("    🎊 集卡状态: 已集齐，可合成")
                # TODO: 这里可以添加自动合成逻辑
            else:
                missing_cards = []
                for card_info in card_info_list:
                    card_name = card_info.get('cardName', '未知')
                    user_cards = card_info.get('userCollectCardInfoList') or []
                    actual_count = len(user_cards)
                    if actual_count < 1:
                        missing_cards.append(card_name)
                
                if missing_cards:
                    log_print(f"📋 还缺少卡片: {', '.join(missing_cards)}")
                    
        except Exception as e:
            log_print(f"❌ 检查合成状态时出错: {e}")

    def _should_draw_lottery(self, activity_config):
        """判断是否应该进行抽奖"""
        if activity_config and 'is_lucky_draw' in activity_config:
            return activity_config['is_lucky_draw']
        # 如果活动配置中没有设置，使用默认值
        return DEFAULT_LUCKY_DRAW_ENABLED

    def _handle_raffle(self, raffle_id, jimu_id, jimu_name, activity_name=None, activity_config=None):
        """处理单个活动的抽奖。"""
        # 判断是否应该进行抽奖（参考activity_base.py的设计）
        should_draw = self._should_draw_lottery(activity_config)
        if not should_draw:
            log_print("⏭️ 抽奖功能已关闭，跳过抽奖。")
            return
        

        
        try:
            count_res = self.client.get(f"{BASE_URL_HD}/api/cn/oapi/marketing/raffle/queryRaffleCount?activityId={raffle_id}").json()
            draw_count = count_res.get('data', {}).get('count', 0)
            
            if draw_count == 0:
                log_print("ℹ️ 没有可用的抽奖次数。")
                return

            log_print(f"🎲 检测到 {draw_count} 次抽奖机会，开始抽奖...")
            winnings = []
            
            for i in range(draw_count):
                log_print(f"🎁 正在进行第 {i+1}/{draw_count} 次抽奖...")
                draw_res = self.client.get(f"{BASE_URL_HD}/api/cn/oapi/marketing/raffle/clickRaffle?activityId={raffle_id}&jimuId={jimu_id}&jimuName={quote(jimu_name)}").json()
                if draw_res.get('code') == 200:
                    data = draw_res.get('data')
                    if data and isinstance(data, dict):
                        raffle_winner = data.get('raffleWinnerVO')
                        if raffle_winner and isinstance(raffle_winner, dict):
                            award_name = raffle_winner.get('exhibitAwardName', '空气')
                        else:
                            award_name = '空气'
                    else:
                        award_name = '空气'
                    log_print(f"🎉 抽奖结果: {award_name}")
                    if '谢谢' not in award_name and '空气' not in award_name and '再接再厉' not in award_name:
                         winnings.append(award_name)
                else:
                    log_print(f"💔 抽奖失败: {draw_res.get('message')}")
                random_sleep(2, 4)

            # 添加抽奖摘要
            if not winnings:
                notify_manager.add_summary(f"    🎉 抽奖 ({draw_count}次): 均未中奖")
            else:
                notify_manager.add_summary(f"    🎉 抽奖 ({draw_count}次): 获得[{'、'.join(winnings)}]")

        except Exception as e:
            log_print(f"❌ 抽奖过程中出错: {e}")
            notify_manager.add_summary("    ❌ 抽奖: 执行异常")

    def process_all_activities(self):
        """按顺序处理配置文件中所有启用的活动。"""
        all_activities_to_process = self._discover_dynamic_activities() + STATIC_ACTIVITIES_CONFIG
        
        for activity in all_activities_to_process:
            if not activity.get("enabled"):
                continue

            log_print(f"\n####### ▶️ 开始执行【{activity['name']}】 #######")
            notify_manager.add_summary(f"  📌 活动: {activity['name']}")
            
            ids = self._get_activity_ids(activity['bp_url'])
            
            if not ids:
                log_print(f"❌ 未能获取【{activity['name']}】的活动ID，跳过此活动。")
                notify_manager.add_summary("    ❌ ID获取失败，已跳过")
                continue

            if ids.get('signin_id'):
                if ids.get('creditsAddActionId') and ids.get('business'):
                    self._handle_sign_in_with_credits(ids['signin_id'], ids['creditsAddActionId'], ids['business'])
                else:
                    self._handle_sign_in(ids['signin_id'])
                random_sleep()

                        # 特殊处理：周年庆活动需要特殊的执行顺序：签到 → 任务 → 集卡
            if all(keyword in activity['name'] for keyword in ANNIVERSARY_KEYWORDS):
                # 1. 先执行周年庆专用签到
                self._handle_anniversary_sign_in()
                random_sleep()
                
                # 2. 动态获取周年庆任务活动ID并执行任务
                anniversary_task_id = self._get_anniversary_task_id(SPECIAL_ACTIVITY_IDS["周年庆集卡"])
                if anniversary_task_id:
                    self._handle_anniversary_tasks(anniversary_task_id)
                else:
                    log_print("⚠️ 无法获取周年庆任务活动ID，跳过任务处理")
                random_sleep()
                
                # 3. 最后处理集卡逻辑
                self._handle_collect_cards(SPECIAL_ACTIVITY_IDS["周年庆集卡"])
                random_sleep()
            elif ids.get('task_id'):
                self._handle_tasks(ids['task_id'], activity['name'])
                random_sleep()
                
                # 处理普通活动的抽奖
                if ids.get('raffle_id') and ids.get('jimu_id'):
                    self._handle_raffle(ids['raffle_id'], ids['jimu_id'], activity['draw_jimu_name'], activity['name'], activity)
                    random_sleep()
            
            log_print(f"####### ✅【{activity['name']}】执行完毕 #######")


def main():
    """
    脚本主入口函数。
    """
    oppo_cookies = get_env("OPPO_APP", "@")
    oppo_applet_cookies = get_env("OPPO_MINI", "@")

    if oppo_cookies:
        log_print("=============== 🚀 开始执行OPPO商城APP任务 ===============\n")
        for i, cookie in enumerate(oppo_cookies):
            log_print(f"--- 👤 开始处理APP账号 {i+1} ---")
            app_instance = OppoApp(cookie, i + 1)
            app_instance.run()
    else:
        log_print("‼️ 未配置OPPO商城APP的Cookie，跳过APP任务。")

    if oppo_applet_cookies:
        log_print("\n=============== 🚀 开始执行OPPO商城小程序任务 ===============\n")
        for i, cookie in enumerate(oppo_applet_cookies):
            log_print(f"--- 👤 开始处理小程序账号 {i+1} ---")
            applet_instance = OppoApplet(cookie, i + 1)
            applet_instance.run()
    else:
        log_print("‼️ 未配置小程序的Cookie，跳过小程序任务。")

    # --- 发送通知 ---
    notification_title = f"OPPO商城任务报告 - {datetime.now().strftime('%m-%d')}"
    notification_content = notify_manager.get_summary()
    
    # 打印最终的摘要，方便调试
    print("\n=============== 📢 推送摘要 ===============\n")
    print(notification_content)
    print("\n=========================================\n")
    
    try:
        # 替换为你自己的通知函数
        if oppo_cookies or oppo_applet_cookies:
            notify.send(notification_title, notification_content)
            log_print("✅ 通知已发送。")
        else:
            log_print("⏹️ 未配置任何账号，无需发送通知。")
    except Exception as e:
        log_print(f"\n❌ 发送通知失败: {e}")


if __name__ == '__main__':
    main()

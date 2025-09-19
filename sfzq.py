#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Date: 2025-09-19
# @LastEditTime: 2025-09-19

"""
From:yaohuo28507
SFSY - 2025中秋活动独立脚本

本脚本从 sf0917.py 中提取，专注于执行2025年中秋节的特定活动任务。
功能包括：
1. 账号登录
2. 检查活动状态
3. 自动完成活动任务 (包括游戏)
4. 领取任务奖励
5. 拆盒拼图游戏

请在青龙面板的环境变量中设置 `SFSY` 或 `sfsyUrl`，值为您的账号URL，多个账号用换行分隔。
"""

import os
import random
import time
import json
from datetime import datetime
from typing import Optional, Dict
from urllib.parse import unquote
import requests
import urllib3
from urllib3.exceptions import InsecureRequestWarning

urllib3.disable_warnings(InsecureRequestWarning)

send_msg = ''

def log(message: str = '') -> None:
    global send_msg
    print(message)
    if message:
        send_msg += f'{message}\n'

inviteId = [
    '62007719D42847EB9E332E1C8C552959'
]

class SFMidAutumnBot:
    """顺丰2025中秋活动自动化机器人"""

    BASE_URL = 'https://mcs-mimp-web.sf-express.com'
    
    SKIP_TASKS = [
        '领取寄件会员权益',
        '积分兑拆盒次数', 
        '去寄快递',
        '使用AI寄件',
        '开通至尊会员',
        '充值新速运通全国卡',
        '开通家庭8折互寄权益'
    ]

    def __init__(self, account_url: str, index: int):
        self.index = index + 1
        self.account_url = account_url.split('@')[0]
        self.session = requests.Session()
        self.session.verify = False

        self.headers = {
            'host': 'mcs-mimp-web.sf-express.com',
            'accept': 'application/json, text/plain, */*',
            'content-type': 'application/json',
            'accept-language': 'zh-CN,zh-Hans;q=0.9',
            'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.53(0x18003531) NetType/WIFI Language/zh_CN miniProgram/wxd4185d00bf7e08ac'
        }

        self.user_id = ''
        self.mobile = ''
        self.phone = ''
        
        self.taskName = ''
        self.taskCode = ''
        self.taskType = ''

        log(f"\n{'=' * 15} 账号 {self.index} [中秋活动] {'=' * 15}")

    def get_signature(self) -> None:
        timestamp = str(int(time.time() * 1000))
        sys_code = 'MCS-MIMP-CORE'
        self.headers.update({
            'sysCode': sys_code,
            'timestamp': timestamp,
        })

    def request(self, url: str, data: Dict = None, method: str = 'POST') -> Optional[Dict]:
        self.get_signature()
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, headers=self.headers, timeout=10)
            else:
                response = self.session.post(url, headers=self.headers, json=data or {}, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"请求异常: {e}")
            return None

    def login(self) -> bool:
        try:
            response = self.session.get(self.account_url, headers=self.headers, timeout=10)
            cookies = self.session.cookies.get_dict()

            self.user_id = cookies.get('_login_user_id_', '')
            self.phone = cookies.get('_login_mobile_', '')

            if self.phone:
                self.mobile = self.phone[:3] + "*" * 4 + self.phone[7:]
                log(f'✓ 用户【{self.mobile}】登录成功')
                return True
            else:
                log('✗ 登录失败：无法从Cookie获取用户信息')
                return False
        except Exception as e:
            log(f'✗ 登录请求异常: {e}')
            return False

    def dragon_midAutumn2025_index(self) -> bool:
        log('\n====== 🥮 中秋活动检查 ======')
        try:
            available_invites = [invite for invite in inviteId if invite != self.user_id]
            if available_invites:
                invite_user_id = random.choice(available_invites)
                payload = {"inviteUserId": invite_user_id}
            else:
                payload = {}
                log('ℹ️ 没有可用的邀请ID，跳过邀请功能')
            
            self.headers.update({
                'channel': '25zqxcxty3',
                'platform': 'MINI_PROGRAM',
                'referer': f'https://mcs-mimp-web.sf-express.com/origin/a/mimp-activity/midAutumn2025?mobile={self.mobile}&userId={self.user_id}',
            })
            url = f'{self.BASE_URL}/mcs-mimp/commonNoLoginPost/~memberNonactivity~midAutumn2025IndexService~index'
            
            response = self.request(url, payload)
            if response and response.get('success'):
                end_time_str = response.get('obj', {}).get('acEndTime')
                if end_time_str and datetime.now() < datetime.strptime(end_time_str, "%Y-%m-%d %H:%M:%S"):
                    log('✓ 中秋活动进行中...')
                    return True
            log('ℹ️ 中秋活动已结束或无法参与')
            return False
        except Exception as e:
            log(f'❌ 检查活动状态异常: {str(e)}')
            return False

    def dragon_midAutumn2025_tasklist(self):
        log('📖 获取中秋活动任务列表')
        url = f'{self.BASE_URL}/mcs-mimp/commonPost/~memberNonactivity~activityTaskService~taskList'
        data = {"activityCode": "MIDAUTUMN_2025", "channelType": "MINI_PROGRAM"}
        response = self.request(url, data)
        if response and response.get('success'):
            for task in response.get('obj', []):
                self.taskName = task['taskName']
                self.taskCode = task.get('taskCode')
                self.taskType = task['taskType']
                
                skip_tasks_enabled = os.environ.get('SKIP_TASKS', 'true').lower() in ['true', '1', 'yes']
                if skip_tasks_enabled and self.taskName in self.SKIP_TASKS:
                    print(f'> ⏭️ 跳过任务【{self.taskName}】')
                    continue
                
                if task['status'] == 3:
                    print(f'> ✅ 任务【{self.taskName}】已完成')
                    continue

                print(f'> 执行任务【{self.taskName}】')
                if self.taskType == 'PLAY_ACTIVITY_GAME':
                    self.dragon_midAutumn2025_game_init()
                elif self.taskName == '看看生活服务':
                    self.dragon_midAutumn2025_finish_task()
                time.sleep(random.uniform(2, 4))
        else:
            log('❌ 获取中秋任务列表失败')

    def dragon_midAutumn2025_game_init(self) -> None:
        print('🎮 初始化中秋游戏...')
        url = f'{self.BASE_URL}/mcs-mimp/commonPost/~memberNonactivity~midAutumn2025GameService~init'
        self.headers.update(
            {'referer': 'https://mcs-mimp-web.sf-express.com/origin/a/mimp-activity/midAutumn2025Game'})
        response = self.request(url)
        if response and response.get('success'):
            obj = response.get('obj', {})
            if not obj.get('alreadyDayPass', False):
                current_index = obj.get('currentIndex', 0)
                print(f'今日未通关，从第【{current_index}】关开始...')
                self.dragon_midAutumn2025_game_win(current_index)
            else:
                print('今日已通关，跳过游戏！')
        else:
            print('❌ 游戏初始化失败')

    def dragon_midAutumn2025_game_win(self, start_level: int):
        url = f'{self.BASE_URL}/mcs-mimp/commonPost/~memberNonactivity~midAutumn2025GameService~win'
        for i in range(start_level, 5):
            print(f'闯关...第【{i}】关')
            response = self.request(url, {"levelIndex": i})
            if response and response.get('success'):
                award = response.get('obj', {}).get('currentAward', {})
                if award:
                    print(f'> 🎉 获得：【{award.get("currency")}】x{award.get("amount")}')
                else:
                    print('> 本关无即时奖励')
                time.sleep(random.uniform(2, 4))
            else:
                error_msg = response.get("errorMessage", "未知错误") if response else "请求失败"
                print(f'❌ 第【{i}】关闯关失败: {error_msg}')
                break

    def dragon_midAutumn2025_finish_task(self):
        url_map = {
            'BROWSE_VIP_CENTER': f'{self.BASE_URL}/mcs-mimp/commonPost/~memberEs~taskRecord~finishTask',
            'default': f'{self.BASE_URL}/mcs-mimp/commonRoutePost/memberEs/taskRecord~finishTask'
        }
        url = url_map.get(self.taskType, url_map['BROWSE_VIP_CENTER'])
        response = self.request(url, {"taskCode": self.taskCode})
        if response and response.get('success'):
            print(f'> ✅ 完成任务【{self.taskName}】成功')
        else:
            print(f'> ❌ 完成任务【{self.taskName}】失败')

    def dragon_midAutumn2025_Reward(self):
        url = f'{self.BASE_URL}/mcs-mimp/commonPost/~memberNonactivity~midAutumn2025BoxService~receiveCountdownReward'
        response = self.request(url)
        if response and response.get('success'):
            received_list = response.get('obj', {}).get('receivedAccountList', [])
            if received_list:
                for item in received_list:
                    print(f'> 🎉 领取倒计时奖励：【{item.get("currency")}】x{item.get("amount")}')
        else:
            error_msg = response.get("errorMessage", "未知错误") if response else "请求失败"
            print(f'❌ 领取倒计时奖励失败: {error_msg}')

    def dragon_midAutumn2025_fetchTasksReward(self):
        url = f'{self.BASE_URL}/mcs-mimp/commonPost/~memberNonactivity~midAutumn2025TaskService~fetchTasksReward'
        data = {"activityCode": "MIDAUTUMN_2025", "channelType": "MINI_PROGRAM"}
        response = self.request(url, data)
        if response and response.get('success'):
            status_url = f'{self.BASE_URL}/mcs-mimp/commonPost/~memberNonactivity~midAutumn2025BoxService~boxStatus'
            status_response = self.request(status_url, {})
            if status_response and status_response.get('success'):
                remain_chance = status_response.get('obj', {}).get('remainBoxChance')
                log(f'ℹ️ 当前剩余拆盒次数：【{remain_chance}】')
                if remain_chance > 0:
                    log('🎯 检测到剩余拆盒次数，开始拆盒')
                    self.dragon_midAutumn2025_puzzle_game()
                    # return True  # 返回True表示已经执行了拆盒游戏
            else:
                error_msg = status_response.get("errorMessage", "未知错误") if status_response else "请求失败"
                print(f'❌ 查询拆盒次数失败: {error_msg}')
        else:
            error_msg = response.get("errorMessage", "未知错误") if response else "请求失败"
            print(f'❌ 领取任务奖励次数失败: {error_msg}')
        # return False  # 返回False表示没有执行拆盒游戏

    def dragon_midAutumn2025_boxStatus(self):
        url = f'{self.BASE_URL}/mcs-mimp/commonPost/~memberNonactivity~midAutumn2025BoxService~boxStatus'
        response = self.request(url, {})
        if response and response.get('success'):
            return response.get('obj', {})
        else:
            error_msg = response.get("errorMessage", "未知错误") if response else "请求失败"
            log(f'❌ 查询盒子状态失败: {error_msg}')
            return None

    def generate_random_board(self, board_length: int, target_shapes: list):
        board = []
        for i in range(board_length):
            row = []
            for j in range(board_length):
                row.append({"t": "", "s": "n"})
            board.append(row)
        
        return json.dumps(board, separators=(', ', ': '))

    def dragon_midAutumn2025_unBox(self):
        url = f'{self.BASE_URL}/mcs-mimp/commonPost/~memberNonactivity~midAutumn2025BoxService~unBox'
        response = self.request(url, {})
        if response and response.get('success'):
            obj = response.get('obj', {})
            token = obj.get('token')
            empty_box = obj.get('emptyBox', True)
            return token, empty_box
        else:
            error_msg = response.get("errorMessage", "未知错误") if response else "请求失败"
            log(f'❌ 获取拆盒token失败: {error_msg}')
            return None, False

    def dragon_midAutumn2025_reportBox(self, token: str, board_data: str, target_shapes: list, level_pass: bool = False):
        url = f'{self.BASE_URL}/mcs-mimp/commonPost/~memberNonactivity~midAutumn2025BoxService~reportBox'
        
        if isinstance(board_data, str):
            try:
                board_list = json.loads(board_data)
                board_str = json.dumps(board_list, separators=(', ', ': '))
            except:
                board_str = board_data
        else:
            board_str = json.dumps(board_data, separators=(', ', ': '))
        
        report_data = {
            "token": token,
            "boardStatus": {
                "b": board_str,
                "t": target_shapes
            },
            "levelPass": level_pass,
            "emptyBox": True,
            "taskType": ""
        }
        
        response = self.request(url, report_data)
        if response and response.get('success'):
            obj = response.get('obj', {})
            return obj
        else:
            error_msg = response.get("errorMessage", "未知错误") if response else "请求失败"
            log(f'❌ 提交拆盒结果失败: {error_msg}')
            return None

    def get_shape_variants(self, shape_type: str, placement: str, rotatable: bool):
        variants = []
        
        if shape_type == 'I':
            if rotatable:
                variants = [
                    {'orientation': 'horizontal', 'offsets': [(0, 1), (0, 2), (0, 3)]},
                    {'orientation': 'vertical', 'offsets': [(1, 0), (2, 0), (3, 0)]}
                ]
            else:
                if placement == 'd':
                    variants = [{'orientation': 'horizontal', 'offsets': [(0, 1), (0, 2), (0, 3)]}]
                else:
                    variants = [{'orientation': 'vertical', 'offsets': [(1, 0), (2, 0), (3, 0)]}]
        
        elif shape_type == 'L':
            if rotatable:
                # L形状的四种旋转
                variants = [
                    {'orientation': 'L1', 'offsets': [(1, 0), (1, 1), (1, 2)]},    # L . . / L L L
                    {'orientation': 'L2', 'offsets': [(0, 1), (1, 0), (2, 0)]},    # L L / L . / L .
                    {'orientation': 'L3', 'offsets': [(-1, 0), (-1, -1), (-1, -2)]}, # L L L / . . L
                    {'orientation': 'L4', 'offsets': [(0, -1), (-1, 0), (-2, 0)]},   # . L / . L / L L
                ]
            else:
                # 不可旋转时，只使用标准的L形状
                variants = [
                    {'orientation': 'L_standard', 'offsets': [(1, 0), (1, 1), (1, 2)]}  # L . . / L L L
                ]
        
        elif shape_type == 'T':
            if rotatable:
                # T形状的四种旋转（以中心点为基准）
                variants = [
                    {'orientation': 'T1', 'offsets': [(-1, 0), (0, -1), (0, 1)]},   # . T . / T T T
                    {'orientation': 'T2', 'offsets': [(0, 1), (-1, 0), (1, 0)]},    # T . / T T / T .
                    {'orientation': 'T3', 'offsets': [(1, 0), (0, -1), (0, 1)]},    # T T T / . T .
                    {'orientation': 'T4', 'offsets': [(0, -1), (-1, 0), (1, 0)]}    # . T / T T / . T
                ]
            else:
                # 不可旋转时，只使用标准的T形状
                variants = [
                    {'orientation': 'T_standard', 'offsets': [(-1, 0), (0, -1), (0, 1)]}  # . T . / T T T
                ]
        
        elif shape_type == 'Z':
            if rotatable:
                # Z形状的两种旋转：水平Z和垂直Z
                variants = [
                    {'orientation': 'Z_horizontal', 'offsets': [(0, 1), (1, 1), (1, 2)]},  # Z Z . / . Z Z
                    {'orientation': 'Z_vertical', 'offsets': [(1, 0), (1, -1), (2, -1)]}   # Z . / Z Z / . Z
                ]
            else:
                # 不可旋转时，只使用标准的水平Z形状
                variants = [
                    {'orientation': 'Z_standard', 'offsets': [(0, 1), (1, 1), (1, 2)]}  # Z Z . / . Z Z
                ]
        
        elif shape_type == 'O':
            variants = [{'orientation': 'O', 'offsets': [(0, 1), (1, 0), (1, 1)]}]
        
        return variants

    def count_completed_patterns(self, board: list, target_shapes: list, rotatable: bool):
        completed_count = 0
        
        for target_shape in target_shapes:
            shape_type = target_shape.get('s', 'I')
            placement = target_shape.get('p', 'd')
            
            variants = self.get_shape_variants(shape_type, placement, rotatable)
            
            existing_positions = []
            for row_idx, row in enumerate(board):
                for col_idx, cell in enumerate(row):
                    if cell.get('t') == shape_type and cell.get('s') == 'y':
                        existing_positions.append((row_idx, col_idx))
            
            if not existing_positions:
                continue
            
            original_positions = existing_positions.copy()
            log(f'> 🔍 检查 {shape_type} 形状 (placement: {placement})，已有位置: {original_positions}')
            
            found_complete = False
            remaining_positions = existing_positions.copy()
            
            for variant in variants:
                offsets = variant['offsets']
                orientation = variant['orientation']
                
                temp_remaining = remaining_positions.copy()
                for start_pos in temp_remaining:
                    start_row, start_col = start_pos
                    pattern_positions = [(start_row, start_col)]
                    
                    for dr, dc in offsets:
                        pattern_positions.append((start_row + dr, start_col + dc))
                    
                    if all(pos in remaining_positions for pos in pattern_positions):
                        log(f'> ✅ 发现完整 {shape_type} 图案 ({orientation}): {pattern_positions}')
                        completed_count += 1
                        for pos in pattern_positions:
                            if pos in remaining_positions:
                                remaining_positions.remove(pos)
                        found_complete = True
                        break
                
                if found_complete:
                    break
            
            if not found_complete:
                log(f'> ⚠️ {shape_type} 形状不完整，需要完成图案')
            elif remaining_positions:
                log(f'> ⚠️ {shape_type} 形状部分完成，剩余未匹配位置: {remaining_positions}')
        
        return completed_count

    def is_shape_complete(self, board: list, shape_type: str, placement: str, rotatable: bool):
        variants = self.get_shape_variants(shape_type, placement, rotatable)
        
        existing_positions = []
        for row_idx, row in enumerate(board):
            for col_idx, cell in enumerate(row):
                if cell.get('t') == shape_type and cell.get('s') == 'y':
                    existing_positions.append((row_idx, col_idx))
        
        if not existing_positions:
            return False
        
        for variant in variants:
            offsets = variant['offsets']
            
            for start_pos in existing_positions:
                start_row, start_col = start_pos
                pattern_positions = [(start_row, start_col)]
                
                for dr, dc in offsets:
                    pattern_positions.append((start_row + dr, start_col + dc))
                
                if all(pos in existing_positions for pos in pattern_positions):
                    return True
        
        return False

    def find_best_move(self, board: list, target_shapes: list, unopened_positions: list, board_length: int, rotatable: bool = False, target_count: int = 1):
        completed_patterns = self.count_completed_patterns(board, target_shapes, rotatable)
        log(f'> 📊 已完成图案：{completed_patterns}/{target_count}')
        
        if completed_patterns >= target_count:
            log(f'> 🎉 已完成 {completed_patterns}/{target_count} 个目标图案，无需继续拆盒')
            return None, None
        
        incomplete_shapes = []
        for target_shape in target_shapes:
            shape_type = target_shape.get('s', 'I')
            placement = target_shape.get('p', 'd')
            
            is_complete = self.is_shape_complete(board, shape_type, placement, rotatable)
            if is_complete:
                log(f'> ✅ {shape_type} 形状已完成，跳过')
                continue
            else:
                log(f'> 🔧 {shape_type} 形状未完成，加入处理队列')
                incomplete_shapes.append(target_shape)
        
        for target_shape in incomplete_shapes:
            shape_type = target_shape.get('s', 'I')
            placement = target_shape.get('p', 'd')
            
            existing_positions = []
            for row_idx, row in enumerate(board):
                for col_idx, cell in enumerate(row):
                    if cell.get('t') == shape_type and cell.get('s') == 'y':
                        existing_positions.append((row_idx, col_idx))
            
            if existing_positions:
                best_move = self.find_completion_move(board, shape_type, placement, existing_positions, unopened_positions, board_length, rotatable)
                if best_move:
                    return best_move, shape_type
            else:
                best_move = self.find_start_position(board, shape_type, placement, unopened_positions, board_length, rotatable)
                if best_move:
                    return best_move, shape_type
        
        if not incomplete_shapes:
            log(f'> 🎊 所有形状都已完成！')
            return None, None
        
        return None, None

    def find_completion_move(self, board, shape_type, placement, existing_positions, unopened_positions, board_length, rotatable):
        variants = self.get_shape_variants(shape_type, placement, rotatable)
        
        log(f'> 🔧 尝试完成 {shape_type} 形状，已有 {len(existing_positions)} 个位置')
        
        best_candidates = []
        
        for variant in variants:
            offsets = variant['offsets']
            orientation = variant['orientation']
            
            for start_pos in existing_positions:
                start_row, start_col = start_pos
                pattern_positions = [(start_row, start_col)]
                
                for dr, dc in offsets:
                    pattern_positions.append((start_row + dr, start_col + dc))
                
                matched_count = sum(1 for pos in pattern_positions if pos in existing_positions)
                missing_positions = [pos for pos in pattern_positions if pos not in existing_positions and pos in unopened_positions]
                
                if matched_count > 1 and missing_positions:
                    score = matched_count * 10 + len(missing_positions)
                    best_candidates.append((score, missing_positions[0], orientation, matched_count))
                    log(f'> 📊 变体 {orientation}: 匹配{matched_count}个，缺失{len(missing_positions)}个，分数{score}')
        
        if best_candidates:
            best_candidates.sort(reverse=True, key=lambda x: x[0])
            score, best_pos, orientation, matched = best_candidates[0]
            log(f'> 🎯 选择最佳完成位置: {best_pos} (变体: {orientation}, 已匹配: {matched})')
            return best_pos
        
        for row, col in existing_positions:
            adjacent_positions = [(row-1, col), (row+1, col), (row, col-1), (row, col+1)]
            for candidate in adjacent_positions:
                if (candidate in unopened_positions and 
                    0 <= candidate[0] < board_length and 0 <= candidate[1] < board_length):
                    log(f'> 🔄 使用相邻扩展: {candidate}')
                    return candidate
        
        return None

    def find_start_position(self, board, shape_type, placement, unopened_positions, board_length, rotatable):
        variants = self.get_shape_variants(shape_type, placement, rotatable)
        scored_positions = []
        
        for row, col in unopened_positions:
            max_score = 0
            
            for variant in variants:
                score = 0
                offsets = variant['offsets']
                
                can_place = True
                for dr, dc in offsets:
                    new_row, new_col = row + dr, col + dc
                    if (not (0 <= new_row < board_length and 0 <= new_col < board_length) or
                        (new_row, new_col) not in unopened_positions):
                        can_place = False
                        break
                
                if can_place:
                    score += 20
                    score += len(offsets) * 5
                    
                    if row == 0 or row == board_length - 1:
                        score += 3
                    if col == 0 or col == board_length - 1:
                        score += 3
                else:
                    available_offsets = 0
                    for dr, dc in offsets:
                        new_row, new_col = row + dr, col + dc
                        if (0 <= new_row < board_length and 0 <= new_col < board_length and
                            (new_row, new_col) in unopened_positions):
                            available_offsets += 1
                    score += available_offsets * 2
                
                max_score = max(max_score, score)
            
            scored_positions.append((max_score, (row, col)))
        
        if scored_positions:
            scored_positions.sort(reverse=True, key=lambda x: x[0])
            return scored_positions[0][1]
        
        return None

    def simulate_board_click(self, board_data: str, target_shapes: list, board_length: int, rotatable: bool = False, target_count: int = 1):
        try:
            board = json.loads(board_data)
            
            unopened_positions = []
            for row_idx, row in enumerate(board):
                for col_idx, cell in enumerate(row):
                    if cell.get('s') == 'n':
                        unopened_positions.append((row_idx, col_idx))
            
            if not unopened_positions:
                log('⚠️ 棋盘上没有未开启的格子')
                return (random.randint(0, board_length - 1), random.randint(0, board_length - 1)), board_data, False
            
            best_move, shape_type = self.find_best_move(board, target_shapes, unopened_positions, board_length, rotatable, target_count)
            
            if best_move:
                selected_row, selected_col = best_move
                log(f'> 🎯 智能选择位置: ({selected_row}, {selected_col}) 形状: {shape_type}')
                
                board[selected_row][selected_col] = {"t": shape_type, "s": "y"}
                
                completed_patterns = self.count_completed_patterns(board, target_shapes, rotatable)
                will_complete_all = completed_patterns >= target_count
                
                updated_board_data = json.dumps(board, separators=(', ', ': '))
                
                return (selected_row, selected_col), updated_board_data, will_complete_all
            else:
                log(f'> ✅ 所有目标图案已完成，无需继续拆盒')
                return None, board_data, False
            
        except Exception as e:
            log(f'解析棋盘数据失败: {e}')
            return (random.randint(0, board_length - 1), random.randint(0, board_length - 1)), board_data, False

    def dragon_midAutumn2025_puzzle_game(self):
        log('\n====== 🧩 拆盒拼图游戏 ======')
        
        box_status = self.dragon_midAutumn2025_boxStatus()
        if not box_status:
            return
        
        remain_chance = box_status.get('remainBoxChance', 0)
        if remain_chance <= 0:
            log('ℹ️ 没有剩余的拆盒机会')
            return
        
        current_level = box_status.get('currentLevelConfig', {})
        level = current_level.get('level', 1)
        board_length = current_level.get('boardLength', 4)
        target_shape_num = current_level.get('targetShapeNum', 2)
        rotatable = current_level.get('rotatable', False)
        level_box_times = box_status.get('levelBoxTimes', 0)
        
        log(f'🎯 当前关卡：第【{level}】关')
        log(f'📋 棋盘大小：{board_length}x{board_length}')
        log(f'🎲 目标图形数量：{target_shape_num}')
        log(f'🔄 图形可旋转：{"是" if rotatable else "否"}')
        log(f'🎫 剩余拆盒机会：{remain_chance}')
        log(f'📊 当前关卡已拆盒次数：{level_box_times}')
        
        board_status = box_status.get('boardStatus', {})
        target_shapes = board_status.get('t', [])
        board_data = board_status.get('b')
        
        log(f'🎮 开始拼图游戏，目标形状：{[shape.get("s") for shape in target_shapes]}')
        
        if board_data:
            try:
                import json
                board = json.loads(board_data)
                completed_patterns = self.count_completed_patterns(board, target_shapes, rotatable)
                log(f'🎯 当前已完成图案：{completed_patterns}/{target_shape_num}')
                
                if completed_patterns >= target_shape_num:
                    log(f'🎊 图案已全部完成，随机开出最后一个盒子并通关！')
                    token, _ = self.dragon_midAutumn2025_unBox()
                    if token:
                        unopened_positions = []
                        for row_idx, row in enumerate(board):
                            for col_idx, cell in enumerate(row):
                                if cell.get('s') == 'n':
                                    unopened_positions.append((row_idx, col_idx))
                        
                        if unopened_positions:
                            random_pos = random.choice(unopened_positions)
                            click_row, click_col = random_pos
                            
                            board[click_row][click_col] = {"s": "y"}
                            
                            updated_board_data = json.dumps(board, separators=(', ', ': '))
                            
                            log(f'> 🎯 随机选择位置: ({click_row}, {click_col}) 开出无图案盒子')
                            
                            final_result = self.dragon_midAutumn2025_reportBox(token, updated_board_data, target_shapes, True)
                            if final_result:
                                log('✅ 通关提交成功')
                                time.sleep(random.uniform(1, 2))
                                updated_status = self.dragon_midAutumn2025_boxStatus()
                                if updated_status:
                                    current_level_after = updated_status.get('currentLevelConfig', {}).get('level', level)
                                    if current_level_after > level:
                                        log(f'> 🎊 恭喜通过第【{level}】关，进入第【{current_level_after}】关！')
                                        time.sleep(random.uniform(2, 3))
                                        self.dragon_midAutumn2025_puzzle_game()
                                return
                            else:
                                log('❌ 通关提交失败，继续游戏')
                        else:
                            log('⚠️ 没有未开启的位置，继续游戏')
            except Exception as e:
                log(f'⚠️ 检查已完成图案时出错：{e}')
        
        should_pass = level_box_times >= target_shape_num * 4
        if should_pass:
            log(f'✨ 已达到通关条件 ({level_box_times} >= {target_shape_num * 4})，尝试通关...')
        
        current_board_data = board_data
        current_level_box_times = level_box_times
        attempt = 0
        
        while True:
            log(f'🎁 第【{attempt + 1}】次拆盒...')
            
            current_status = self.dragon_midAutumn2025_boxStatus()
            if not current_status:
                log('❌ 无法获取当前盒子状态')
                break
            
            current_remain_chance = current_status.get('remainBoxChance', 0)
            if current_remain_chance <= 0:
                log('ℹ️ 拆盒机会已用完')
                break
                
            current_board_status = current_status.get('boardStatus', {})
            current_target_shapes = current_board_status.get('t', target_shapes)
            if not current_board_data:
                current_board_data = current_board_status.get('b')
            current_level_box_times = current_status.get('levelBoxTimes', current_level_box_times)
            
            should_pass = current_level_box_times >= target_shape_num * 4
            
            token, empty_box = self.dragon_midAutumn2025_unBox()
            if not token:
                log('❌ 获取拆盒token失败')
                break
            
            time.sleep(random.uniform(0.5, 1.0))
            
            if not current_board_data:
                log('🎲 生成新关卡的空棋盘...')
                current_board_data = self.generate_random_board(board_length, current_target_shapes)
            
            result = self.simulate_board_click(current_board_data, current_target_shapes, board_length, rotatable, target_shape_num)
            
            if result[0] is None:
                log('> ✅ 所有目标图案已完成，随机开出最后一个盒子并通关')
                try:
                    import json
                    board = json.loads(current_board_data)
                    
                    unopened_positions = []
                    for row_idx, row in enumerate(board):
                        for col_idx, cell in enumerate(row):
                            if cell.get('s') == 'n':
                                unopened_positions.append((row_idx, col_idx))
                    
                    if unopened_positions:
                        random_pos = random.choice(unopened_positions)
                        click_row, click_col = random_pos
                        
                        board[click_row][click_col] = {"s": "y"}
                        
                        updated_board_data = json.dumps(board, separators=(', ', ': '))
                        
                        log(f'> 🎯 随机选择位置: ({click_row}, {click_col}) 开出无图案盒子')
                        
                        final_result = self.dragon_midAutumn2025_reportBox(token, updated_board_data, current_target_shapes, True)
                        if final_result:
                            log('> 🎉 通关提交成功！')
                            time.sleep(random.uniform(1, 2))
                            updated_status = self.dragon_midAutumn2025_boxStatus()
                            if updated_status:
                                current_level_after = updated_status.get('currentLevelConfig', {}).get('level', level)
                                if current_level_after > level:
                                    log(f'> 🎊 恭喜通过第【{level}】关，进入第【{current_level_after}】关！')
                                    time.sleep(random.uniform(2, 3))
                                    self.dragon_midAutumn2025_puzzle_game()
                                    return
                                else:
                                    log('> ✅ 拼图游戏完成')
                                    break
                        else:
                            log('> ❌ 通关提交失败')
                            break
                    else:
                        log('> ⚠️ 没有未开启的位置，无法继续')
                        break
                        
                except Exception as e:
                    log(f'> ❌ 处理通关逻辑时出错: {e}')
                    break
            
            (click_row, click_col), updated_board_data, will_complete_all = result
            current_board_data = updated_board_data
            log(f'> 点击位置：({click_row}, {click_col})')
            
            final_level_pass = should_pass or will_complete_all
            if will_complete_all:
                log('> 🎉 这次点击将完成所有图案，设置通关标志')
            
            result = self.dragon_midAutumn2025_reportBox(token, updated_board_data, current_target_shapes, final_level_pass)
            if result:
                reward = result.get('reward')
                if reward:
                    currency = reward.get('currency', '')
                    amount = reward.get('amount', 0)
                    log(f'> 🎉 获得奖励：【{currency}】x{amount}')
                
                remaining = result.get('remainBoxChance', 0)
                if remaining <= 0:
                    log('> ℹ️ 拆盒机会已用完')
                    break
                
                log(f'> 剩余机会：{remaining}')
                
                if will_complete_all:
                    log('> 🎉 拼图完成，检查通关状态...')
                    time.sleep(random.uniform(1, 2))
                    updated_status = self.dragon_midAutumn2025_boxStatus()
                    if updated_status:
                        current_level_after = updated_status.get('currentLevelConfig', {}).get('level', level)
                        if current_level_after > level:
                            log(f'> 🎊 恭喜通过第【{level}】关，进入第【{current_level_after}】关！')
                            time.sleep(random.uniform(2, 3))
                            self.dragon_midAutumn2025_puzzle_game()
                            return
                        elif updated_status.get('levelBoxTimes', 0) == 0 and current_level_box_times > 0:
                            log(f'> 🎊 恭喜通过第【{level}】关！')
                            time.sleep(random.uniform(2, 3))
                            self.dragon_midAutumn2025_puzzle_game()
                            return
                        else:
                            log('> ✅ 拼图完成，本关结束')
                            break
                else:
                    time.sleep(random.uniform(1, 2))
                    updated_status = self.dragon_midAutumn2025_boxStatus()
                    if updated_status:
                        current_level_after = updated_status.get('currentLevelConfig', {}).get('level', level)
                        if current_level_after > level:
                            log(f'> 🎊 恭喜通过第【{level}】关，进入第【{current_level_after}】关！')
                            time.sleep(random.uniform(2, 3))
                            self.dragon_midAutumn2025_puzzle_game()
                            return
                        elif updated_status.get('levelBoxTimes', 0) == 0 and current_level_box_times > 0:
                            log(f'> 🎊 恭喜通过第【{level}】关！')
                            time.sleep(random.uniform(2, 3))
                            self.dragon_midAutumn2025_puzzle_game()
                            return
                        
                        current_level_box_times = updated_status.get('levelBoxTimes', current_level_box_times)
            else:
                log('> ❌ 拆盒失败')
                if final_level_pass:
                    log('> 尝试不设置通关标志重新拆盒...')
                    result_retry = self.dragon_midAutumn2025_reportBox(token, updated_board_data, current_target_shapes, False)
                    if result_retry:
                        log('> ✅ 重试成功')
                        attempt += 1
                        continue
                break
            
            attempt += 1
        
        log('🧩 拼图游戏结束')
            
    def run(self):
        if not self.login():
            log('❌ 账号登录失败，跳过后续任务')
            return

        time.sleep(random.uniform(2, 4))

        if self.dragon_midAutumn2025_index():
            #self.dragon_midAutumn2025_fetchTasksReward()
            self.dragon_midAutumn2025_tasklist()
            self.dragon_midAutumn2025_puzzle_game()
            self.dragon_midAutumn2025_Reward()
            self.dragon_midAutumn2025_fetchTasksReward()
        
        log(f'✅ 账号 {self.index} 中秋活动任务执行完毕')

def main():
    """主程序入口"""
    log("""
    本文件仅可用于交流编程技术心得, 请勿用于其他用途, 请在下载后24小时内删除本文件!
    如软件功能对个人或网站造成影响，请联系作者协商删除。
    一切因使用本文件而引致之任何意外、疏忽、合约毁坏、诽谤、版权或知识产权侵犯及其所造成的损失，脚本作者既不负责亦不承担任何法律责任。
    作者不承担任何法律责任，如作他用所造成的一切后果和法律责任由使用者承担！
    """)
    print("🚀 SFSY-2025中秋活动独立脚本启动")
    
    skip_tasks_enabled = os.environ.get('SKIP_TASKS', 'true').lower() in ['true', '1', 'yes']
    if skip_tasks_enabled:
        skip_task_names = ['领取寄件会员权益', '积分兑拆盒次数', '去寄快递', '使用AI寄件', '开通至尊会员', '充值新速运通全国卡', '开通家庭8折互寄权益']
        print(f"⏭️ 跳过任务功能：已启用，将跳过 {len(skip_task_names)} 个任务")
    else:
        print("⏭️ 跳过任务功能：已禁用，将执行所有任务")
    
    env_name = 'sfsyUrl'
    if env_name in os.environ:
        tokens = os.environ[env_name].split('&')
    else:
        log('❌ 未找到环境变量 `SFSY` 或 `sfsyUrl`')
        return

    decoded_tokens = []
    for token_item in tokens:
        if token_item.strip():
            # 对每个账号信息进行URL解码
            decoded_token = unquote(token_item.strip())
            decoded_tokens.append(decoded_token)
    if not decoded_tokens:
        log('❌ 环境变量中没有找到有效的账号URL')
        return

    log(f'📊 共获取到 {len(decoded_tokens)} 个账号')

    for index, token in enumerate(decoded_tokens):
        try:
            bot = SFMidAutumnBot(token, index)
            bot.run()
        except Exception as e:
            log(f'❌ 账号 {index + 1} 执行出现未知异常: {e}')

        if index < len(decoded_tokens) - 1:
            delay = random.uniform(5, 8)
            print(f'\n...等待 {delay:.1f} 秒后处理下一个账号...')
            time.sleep(delay)

    log('\n🎉 所有账号任务执行完毕')
    # 如果需要企业微信等通知，可以在这里添加 `send` 函数的调用
    # from notify import send
    # if send_msg:
    #     send('顺丰中秋活动通知', send_msg)

if __name__ == '__main__':
    main()


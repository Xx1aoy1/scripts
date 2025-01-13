import requests
import json
from datetime import datetime
import urllib3
import time
import generate_mapdata
import os
import re
from notify import pushplus_bot
# 禁用 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
raw_tokens = os.getenv("nfsqtoken", "")
account_tokens = re.split(r"[&\n]+", raw_tokens.strip())
account_tokens = [token.strip() for token in account_tokens if token.strip()]
provice_name=os.getenv("provice_name")
# account_tokens = "658e24f7863e4f75b61c315706389d2e4e077c5ed9604d34a996280f3ea738a8&632357bc47b1478ab3de8d67fd1fcbbdc5487448bc494a1480421072f93d6f4d&becffa4bf4e54d9db610a800f3387db3d99c2c34ee9b49a8819da936e6b16f1b".split("&")#多账号用&来进行分开
# account_tokens="658e24f7863e4f75b61c315706389d2e4e077c5ed9604d34a996280f3ea738a8#小王#0cb95401-9b27-4219-9014-f809c7fb9601".split("&")
# provice_name='河北省'
# Headers 配置模板
headers_template = {
    'content-type': 'application/json',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090a13) UnifiedPCWindowsWechat(0xf254010d) XWEB/11607'
}

def send_push_notification(title, content):
    """
    封装推送功能，调用 pushplus_bot 方法。
    """
    pushplus_bot(title, content)

# 获取任务列表
def get_tasks(headers):
    print(f"开始获取任务")

    # 请求任务接口
    res1 = requests.get(
        "https://gateway.jmhd8.com/geement.marketingplay/api/v1/task?pageNum=1&pageSize=10&task_status=2&status=1&group_id=24121016331837",
        headers=headers,
        verify=False
    )

    # 检查响应状态码
    if res1.status_code != 200:
        print(f"请求失败，状态码: {res1.status_code}")
        return []

    # 解析任务数据
    rw = res1.json()
    if not rw.get("data"):
        print("没有任务数据")
        return []

    tasks = []
    # 遍历任务并提取数据
    for task in rw["data"]:
        task_name = task["name"]
        task_id = task["id"]
        reward_name = task["reward"][0]["relationship_name"]
        reward_count = task["reward"][0]["reward_count"]
        allow_complete_count = task["allow_complete_count"]
        complete_count = task["complete_count"]
        task_status = "有效" if task["task_status"] == 2 else "无效"

        # 打印任务信息
        print(f"任务名称: {task_name}")
        print(f"任务ID: {task_id}")
        print(f"奖励名称: {reward_name}")
        print(f"每次奖励数量: {reward_count}")
        print(f"允许完成次数: {allow_complete_count}")
        print(f"已完成次数: {complete_count}")
        print(f"任务状态: {task_status}")
        print("-" * 50)

        # 将任务数据添加到列表
        tasks.append({
            "task_name": task_name,
            "task_id": task_id,
            "allow_complete_count": allow_complete_count,
            "complete_count": complete_count,
            "reward_count": reward_count,
            "task_status": task_status
        })

    return tasks


# 执行单个任务
def task(task_name, task_id, allow_complete_count, complete_count, headers):
    print(f"开始执行任务: {task_name}")
    for i in range(complete_count, allow_complete_count):
        print(f"正在执行第 {i + 1} 次任务...")

        # 动态获取时间
        formatted_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        res = requests.get(
            f"https://gateway.jmhd8.com/geement.marketingplay/api/v1/task/join?action_time={formatted_date}&task_id={task_id}",
            headers=headers,
            verify=False
        )

        # 解析任务执行结果
        res_data = res.json()
        if res.status_code == 200 and res_data.get('success'):
            print(f"第 {i + 1} 次任务成功: {res_data.get('msg')}")
        else:
            print(f"第 {i + 1} 次任务失败: {res_data.get('msg') if res_data.get('msg') else '未知错误'}")
        print("-" * 50)
#执行游戏任务
def gametask(headers,mapdata):
    win_date = datetime.now().strftime('%Y-%m-%d')

    gurl = f"https://thirtypro.jmhd8.com/api/v1/nongfuwater/snake/checkerboard/lottery"

    # 定义最大尝试次数（可根据需求调整）
    max_attempts = 10  # 假设最多尝试 100 次
    for attempt in range(1, max_attempts + 1):
        print(f"正在玩第 {attempt} 次游戏...")

        # 发送请求
        resg = requests.post(gurl, headers=headers, verify=False, json=mapdata)
        resg_data = resg.json()
        # print(resg_data)

        # 检查请求是否成功
        if resg.status_code != 200:
            print(f"请求失败，状态码: {resg.status_code}")
            print(resg.json())  # 打印错误信息
            break

        # 检查返回的数据
        if not resg_data.get("success", False):
            print(f"游戏失败: {resg_data.get('msg', '未知错误')}")

            # 如果提示当天棋盘格次数已用尽，则退出循环
            if "当天的棋盘格次数已用尽" in resg_data.get("msg", ""):
                break
            continue

        # 检查是否有中奖信息
        if "data" in resg_data and resg_data["data"] is not None and "prizedto" in resg_data["data"]:
            prize_info = resg_data["data"]["prizedto"]

            # 提取奖品名称和等级
            prize_name = prize_info.get("prize_name", "未知奖品")
            prize_level = prize_info.get("prize_level", "未知等级")

            # 如果中奖，打印中奖信息
            print(f"恭喜！抽中奖品：{prize_name}（等级：{prize_level}）")

            # 检查资格卡券不足的情况
            if "资格卡券不足" in resg_data.get("msg", ""):
                print("资格卡券不足，抽奖结束。")
                break
        else:
            print("未中奖或返回数据格式错误")

    print("游戏结束。")


def choujiang(headers,mapdata):
    print(f'当前抽奖城市为{mapdata["provice_name"]}')


    url = "https://gateway.jmhd8.com/geement.marketinglottery/api/v1/marketinglottery"
    attempt = 0  # 抽奖次数计数器
    while True:
        attempt += 1
        print(f"第 {attempt} 次抽奖开始...")

        # 发起 POST 请求
        res4 = requests.session().post(url, headers=headers, json=mapdata, verify=False)

        # 检查 HTTP 状态码
        if res4.status_code != 200:
            print(f"请求失败，状态码: {res4.status_code}")
            print(res4.json())  # 打印错误信息
            break

        # 解析返回 JSON 数据
        res4_data = res4.json()
        # print(res4_data)
        # 检查是否有资格
        if not res4_data.get("success", False):
            print(f"抽奖失败：{res4_data.get('msg', '未知错误')}")
            break  # 跳出循环

        # 处理抽奖结果
        if "data" in res4_data and "prizedto" in res4_data["data"]:
            prize_info = res4_data["data"]["prizedto"]

            # 提取奖品名称和等级
            prize_name = prize_info.get("prize_name", "未知奖品")
            prize_level = prize_info.get("prize_level", "未知等级")

            print(f"第 {attempt} 次抽奖结果: 奖品名称: {prize_name}, 等级: {prize_level}")

            if "资格卡券不足" in res4_data.get("msg", ""):
                print("资格卡券不足，抽奖结束。")
                break

            # 如果中奖，打印中奖信息
            if prize_name and prize_level:
                print(f"恭喜！抽中奖品：{prize_name}（等级：{prize_level}）")
        else:
            print("未中奖或返回数据格式错误")

        # 等待 2 秒后进行下一次抽奖
        time.sleep(2)

def property(username,headers,all_prizes,provice_name):
    print("-" * 50)
    print(headers)
    print(f'{username}:中奖情况')
    url = "https://gateway.jmhd8.com/geement.actjextra/api/v1/act/win/goods/simple?act_codes=ACT2412101428048%2CACT24121014352835%2CACT24121014371732"
    rs5=requests.get(url, headers=headers, verify=False)
    rs5_data = rs5.json()
    # print(rs5_data)
    if not rs5_data.get("success"):
        print("未成功获取数据")
        return
    prize_list = rs5_data.get("data", [])
    log_entries = []
    for prize in prize_list:
        # 提取相关信息
        win_goods_name = prize.get("win_goods_name", "未知奖品")
        scan_time = prize.get("scan_time", "未知时间")
        win_prize_name = prize.get("win_prize_name", "未知奖项")
        win_goods_type = prize.get("win_goods_type", "未知类型")
        act_name = prize.get("act_name", "未知活动")
        win_prize_level = prize.get("win_prize_level", "未知等级")

        # 奖品类型描述
        win_goods_type_desc = (
            "图片显示" if win_goods_type == 60 else "其他类型"
        )
        print("-" * 50)
        print(f"中奖账号: {username}")
        print(f"中奖地区: {provice_name}")
        print(f"奖品名称: {win_goods_name}")
        print(f"获奖时间: {scan_time}")
        print(f"奖项名称: {win_prize_name}")
        print(f"奖品类型: {win_goods_type_desc}（{win_goods_type}类型）")
        print(f"活动名称: {act_name}")
        print(f"奖品等级: {win_prize_level}")
        print("-" * 50)
        # 如果奖品名称不为 "潘展乐祝福奖"，添加到 all_prizes 列表
        if win_prize_level in ["五等奖", "四等奖", "三等奖", "二等奖", "一等奖"] and win_goods_name != "潘展乐祝福奖":
            all_prizes.append({
                "username": username,
                "奖品名称": win_goods_name,
                "获奖时间": scan_time,
                "奖项名称": win_prize_name,
                "奖品类型": win_goods_type_desc,
                "活动名称": act_name,
                "奖品等级": win_prize_level,
            })

def main():
    print(f"账号数量: {len(account_tokens)}")
    all_prizes = []
    for a in account_tokens:
        # 分割 token，提取用户名
        if "#" in a:
            token, unique_identity,provice_name,username = a.split("#")

        print(f"开始执行账号: {username}\n账号所以地区为{provice_name}")
        mapdata =generate_mapdata.generate_mapdata(provice_name)
        all_prizes = []  # 存储所有需要推送的奖品信息

        # 更新 headers 中的 token
        headers = headers_template.copy()
        headers['apitoken'] = token

        # 获取任务列表
        tasks = get_tasks(headers)

        # 遍历任务并执行
        for task_data in tasks:
            if task_data["task_status"] == "有效" and task_data["complete_count"] < task_data["allow_complete_count"]:
                task(
                    task_name=task_data["task_name"],
                    task_id=task_data["task_id"],
                    allow_complete_count=task_data["allow_complete_count"],
                    complete_count=task_data["complete_count"],
                    headers=headers
                )
            else:
                print(f"任务: {task_data['task_name']} 无需执行或已完成")
                print("-" * 50)
        #执行游戏
        gametask(headers,mapdata)
        # 执行抽奖
        choujiang(headers,mapdata)
        #打印资产信息
        def property_request(username, headers, unique_identity,all_prizes,provice_name):
            headers['unique_identity'] = unique_identity
            property(username, headers,all_prizes,provice_name)
        property_request(username, headers,unique_identity,all_prizes,provice_name)
        if all_prizes:  # 如果有需要推送的奖品信息
            content = "\n\n".join([
                f"账号: {prize['username']}\n"
                f"中奖地区: {provice_name}\n"
                f"奖品名称: {prize['奖品名称']}\n"
                f"获奖时间: {prize['获奖时间']}\n"
                f"奖项名称: {prize['奖项名称']}\n"
                f"奖品类型: {prize['奖品类型']}\n"
                f"活动名称: {prize['活动名称']}\n"
                f"奖品等级: {prize['奖品等级']}"
                for prize in all_prizes
            ])

            send_push_notification(
                title="中奖信息汇总",
                content=f"以下是五等奖以上的的中奖信息:\n\n{content}"
            )
        else:
            print("无有效中奖记录，不进行推送。")

# 调用主程序
main()

import random
import time
import threading

# 模拟用户抢话费
def grab_recharge(user_id, lock, log_file):
    """
    模拟单个用户抢话费的行为。

    参数:
        user_id (int): 用户ID。
        lock (threading.Lock): 用于线程同步的锁。
        log_file (str): 日志文件名。
    """
    recharge_amounts = [0.5, 1.0, 5.0, 10.0]  # 允许的充值金额
    recharge_amount = random.choice(recharge_amounts)
    success_rate = 0.2 # 调整成功率
    if random.random() < success_rate:
        with lock:
            with open(log_file, "a", encoding="utf-8") as f:
                phone_number = generate_phone_number()  # 生成随机电话号码
                f.write(f"用户 : {phone_number} 成功抢到 {recharge_amount} 元话费！\n")
        print(f"用户 : {phone_number}  成功抢到 {recharge_amount} 元话费！")
    else:
        phone_number = generate_phone_number() #也要生成电话号码
        print(f"用户 : {phone_number}  未能抢到话费。")
    time.sleep(random.uniform(0.1, 0.5))  # 模拟用户操作间隔，避免过于集中

def simulate_recharge_event(num_users, log_file="recharge_log.txt"):
    """
    模拟多用户并发抢话费的场景。

    参数:
        num_users (int): 参与抢话费的用户数量。
        log_file (str): 用于记录日志的文件名。
    """
    threads = []
    lock = threading.Lock()  # 创建一个线程锁，保证日志文件写入的线程安全

    with open(log_file, "w", encoding="utf-8") as f:  # 指定 utf-8 编码
        f.write("抢话费活动日志:\n")

    for i in range(num_users):
        thread = threading.Thread(target=grab_recharge, args=(i + 1, lock, log_file))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    print("抢话费活动结束，详细结果请查看 {}".format(log_file))

# 生成随机11位电话号码
def generate_phone_number():
    """生成一个随机的11位手机号码"""
    prefix_list = ['130', '131', '132', '133', '134', '135', '136', '137', '138', '139',
                   '147', '148', '150', '151', '152', '153', '155', '156', '157', '158',
                   '159', '166', '170', '171', '172', '173', '175', '176', '177', '178',
                   '180', '181', '182', '183', '184', '185', '186', '187', '188', '189',
                   '198', '199']  # 手机号前缀列表
    prefix = random.choice(prefix_list)
    suffix = ''.join(random.choice("0123456789") for _ in range(8))
    return prefix + suffix

if __name__ == "__main__":
    num_users = 200  # 模拟用户数量，可以根据需要调整
    log_file = "recharge_log.txt"  # 日志文件名

    simulate_recharge_event(num_users, log_file)

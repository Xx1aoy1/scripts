"""
name: 好衣收旧衣服回收，起提1元
Author: MK集团本部
Date: 2024-09-24
export hyhs="uid"
cron: 0 5 * * *
"""
#import notify
import requests, json, os, sys, time, random,datetime
response = requests.get("https://mkjt.jdmk.xyz/mkjt.txt")
response.encoding = 'utf-8'
txt = response.text
print(txt)
#---------------------主代码区块---------------------
session = requests.session()

def userinfo(uid):
	url = 'https://haoyi.haojim.com/index/user/getinfo'
	header = {
		"Connection": "keep-alive",
		"User-Agent": "Mozilla/5.0 (Linux; Android 10; MI 8 Build/QKQ1.190828.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/126.0.6478.188 Mobile Safari/537.36 XWEB/1260117 MMWEBSDK/20240501 MMWEBID/3169 MicroMessenger/8.0.50.2701(0x2800325B) WeChat/arm64 Weixin NetType/WIFI Language/zh_CN ABI/arm64 MiniProgramEnv/android",
		"content-type": "application/json"
	}
	data = {"uid":uid}
	try:
		response = session.post(url=url, headers=header, json=data)
		info = json.loads(response.text)
		#print(info)
		if "success" in info["message"]:
			return info["data"]["realname"],info["data"]["balance"]
	except Exception as e:
		#print(e)
		pass

def qdinfo(uid):
	url = 'https://haoyi.haojim.com/index/user/qiandaoinfo'
	header = {
		"Connection": "keep-alive",
		"User-Agent": "Mozilla/5.0 (Linux; Android 10; MI 8 Build/QKQ1.190828.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/126.0.6478.188 Mobile Safari/537.36 XWEB/1260117 MMWEBSDK/20240501 MMWEBID/3169 MicroMessenger/8.0.50.2701(0x2800325B) WeChat/arm64 Weixin NetType/WIFI Language/zh_CN ABI/arm64 MiniProgramEnv/android",
		"content-type": "application/json"
	}
	data = {"uid":uid}
	try:
		response = session.post(url=url, headers=header, json=data)
		info = json.loads(response.text)
		#print(info)
		if "success" in info["message"]:
			pass
	except Exception as e:
		#print(e)
		pass

def tx(uid,d):
	url = 'https://haoyi.haojim.com/index/commission/cashwait'
	header = {
		"Connection": "keep-alive",
		"User-Agent": "Mozilla/5.0 (Linux; Android 10; MI 8 Build/QKQ1.190828.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/126.0.6478.188 Mobile Safari/537.36 XWEB/1260117 MMWEBSDK/20240501 MMWEBID/3169 MicroMessenger/8.0.50.2701(0x2800325B) WeChat/arm64 Weixin NetType/WIFI Language/zh_CN ABI/arm64 MiniProgramEnv/android",
		"content-type": "application/json"
	}
	data =  {
		"uid":uid,
		"type":"1",
		"commission_wait":d,
		"cash_type":2,
		"telphone":""
	}
	try:
		response = session.post(url=url, headers=header, json=data)
		tx = json.loads(response.text)
		#print(tx)
		if tx["errno"] == 0:
			return tx["message"]
		else:
			return tx["message"]
	except Exception as e:
		pass

def run(uid):
	try:
		for i in range(8):
			login = 'https://haoyi.haojim.com/index/user/qiandao'
			header = {
				"Connection": "keep-alive",
				"User-Agent": "Mozilla/5.0 (Linux; Android 10; MI 8 Build/QKQ1.190828.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/126.0.6478.188 Mobile Safari/537.36 XWEB/1260117 MMWEBSDK/20240501 MMWEBID/3169 MicroMessenger/8.0.50.2701(0x2800325B) WeChat/arm64 Weixin NetType/WIFI Language/zh_CN ABI/arm64 MiniProgramEnv/android",
				"content-type": "application/json"
			}
			data = {
				"uid":uid,
				"isqd":"0"
			}
			response = session.post(url=login, headers=header, json=data)
			login = json.loads(response.text)
			print(login)
			a , b = userinfo(uid)
			if "success" in login["message"]:
				print(f"📱：{a}，☁️签到{i+1}次")
			elif "签到失败" in login["message"]:
				print(f"📱：{a}，☁️签到完成，🌈余额：{b}元")
				if float(b) >= 1:
					txjg = tx(uid,b)
					print(f"🌈开始提现：{txjg}")
				break
			time.sleep(5)
	except Exception as e:
		#print(e)
		try:
			a , b = userinfo(uid)
			print(f"📱：{a}，☁️签到完成，🌈余额：{b}元")
			if float(b) >= 1:
				txjg = tx(uid,b)
				print(f"🌈开始提现：{txjg}")
		except:
			print("📱：账号已过期或异常")

def main():
	if os.environ.get("hyhs"):
		ck = os.environ.get("hyhs")
	else:
		ck = ""
		if ck == "":
			print("请设置变量")
			sys.exit()

	if datetime.datetime.strptime('05:01', '%H:%M').time() <= datetime.datetime.now().time() <= datetime.datetime.strptime('06:59', '%H:%M').time():
		time.sleep(random.randint(100, 500))
	ck_run = ck.split('\n')
	print(f"{' ' * 10}꧁༺ 好衣༒回收 ༻꧂\n")
	for i, ck_run_n in enumerate(ck_run):
		print(f'\n----------- 🍺账号【{i + 1}/{len(ck_run)}】执行🍺 -----------')
		try:
			uid = ck_run_n
			qdinfo(uid)
			run(uid)
			time.sleep(random.randint(3, 5))
		except Exception as e:
			print(e)
			#notify.send('title', 'message')

	print(f'\n----------- 🎊 执 行  结 束 🎊 -----------')


if __name__ == '__main__':
	main()

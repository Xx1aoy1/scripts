"""
name: 绿燕子旧衣服回收，起提1元
Author: MK集团本部
Date: 2024-09-24
export lyzhs="Authorization"
cron: 0 5 * * *
"""
#import notify
import requests, json, os, sys, time, random,datetime
print("🎉斗鸡眼黄诚跑路曝光群:https://t.me/KingHeader")
print("🎉斗鸡眼黄诚跑路维权群:https://t.me/+qtkNyVVnPtBkYjk1")
print("畜生全家信息在频道，详情请点击上方链接，他老婆的罗照也已经被曝光")
print("姓名:黄诚")
print("身份证号:33052219910226211X")
print("手机号1:13735178279")
print("手机号2:17336283606")
print("手机号3:19000586470")
print("地址1:湖州云丰小区云鸿西路转椅市场2115号")
print("地址2:湖州山水华庭北苑交通路山水华庭北苑3幢一单元501")
#---------------------主代码区块---------------------
session = requests.session()

def userinfo(ck):
	url = 'https://lyz.api.5tan.com/api/user/index?platform=1'
	header = {
		"Connection": "keep-alive",
		"User-Agent": "Mozilla/5.0 (Linux; Android 10; MI 8 Build/QKQ1.190828.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/126.0.6478.188 Mobile Safari/537.36 XWEB/1260117 MMWEBSDK/20240501 MMWEBID/3169 MicroMessenger/8.0.50.2701(0x2800325B) WeChat/arm64 Weixin NetType/WIFI Language/zh_CN ABI/arm64 MiniProgramEnv/android",
		"content-type": "application/json",
		"Authorization": ck,
	}
	data = {}
	try:
		response = session.get(url=url, headers=header, data=data)
		info = json.loads(response.text)
		#print(info)
		if "ok" in info["msg"]:
			return info["data"]["money"],info["data"]["nick_name"]
	except Exception as e:
		#print(e)
		pass

def run(ck):
	userinfo(ck)
	login = 'https://lyz.api.5tan.com/api/signin/addSignIn'
	header = {
		"Connection": "keep-alive",
		"User-Agent": "Mozilla/5.0 (Linux; Android 10; MI 8 Build/QKQ1.190828.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/126.0.6478.188 Mobile Safari/537.36 XWEB/1260117 MMWEBSDK/20240501 MMWEBID/3169 MicroMessenger/8.0.50.2701(0x2800325B) WeChat/arm64 Weixin NetType/WIFI Language/zh_CN ABI/arm64 MiniProgramEnv/android",
		"content-type": "application/json",
		"Authorization": ck,
	}
	data = {"platform":1}
	try:
		response = session.post(url=login, headers=header, json=data)
		login = json.loads(response.text)
		#print(login)
		a , b = userinfo(ck)
		if login["code"] == 200:
			print(f"📱：{b}\n☁️签到：成功\n🌈现金：{a}元")
		else:
			print(f"📱：{b}\n☁️签到：{login['msg']}\n🌈现金：{a}元")
		time.sleep(2)
	except Exception as e:
		print("📱：账号已过期或异常")

def main():
	if os.environ.get("lyzhs"):
		ck = os.environ.get("lyzhs")
	else:
		ck = ""
		if ck == "":
			print("请设置变量")
			sys.exit()

	if datetime.datetime.strptime('05:01','%H:%M').time() <= datetime.datetime.now().time() <= datetime.datetime.strptime('06:59', '%H:%M').time():
		time.sleep(random.randint(100, 500))
	ck_run = ck.split('\n')
	print(f"{' ' * 10}꧁༺ 绿燕༒回收 ༻꧂\n")
	for i, ck_run_n in enumerate(ck_run):
		print(f'\n----------- 🍺账号【{i + 1}/{len(ck_run)}】执行🍺 -----------')
		try:
			ck = ck_run_n
			run(ck)
			time.sleep(random.randint(1, 2))
		except Exception as e:
			print(e)
			#notify.send('title', 'message')

	print(f'\n----------- 🎊 执 行  结 束 🎊 -----------')


if __name__ == '__main__':
	main()
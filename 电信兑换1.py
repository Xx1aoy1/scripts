"""
cron: 0 59 9,13 * * *
new Env('电信金豆兑换话费');
"""
# 格式
# 手机号#密码#uid
# 15555555555#888888#
# 15555555555#888888#
# uid可为空
# 单抢兑线程数
submitMaxWorkers=1
# 单抢兑线提交任务间隔时间---模拟手动延迟
submitTime=8

appToken='' # 推送的appToken
phoneArr=[]
import os
dxyh=os.getenv('dx')
for item in dxyh.split('&'):
    dxs = item.split('#')
    uid = ""
    if len(dxs) == 3:
        uid = item.split('#')[2]
    phoneArr.append({
        'phone':item.split('#')[0],
        'password':item.split('#')[1],
        'uid':uid
    })
import subprocess
import re
import datetime
import time
from functools import partial
subprocess.Popen = partial(subprocess.Popen, encoding='utf-8')
import execjs
import json
from bs4 import BeautifulSoup
# from Crypto.PublicKey import RSA
# from Crypto.Cipher import PKCS1_v1_5
import rsa
from Crypto.Cipher import DES3
from Crypto.Util.Padding import pad, unpad
from Crypto.Util.strxor import strxor
from Crypto.Cipher import AES
import random
import base64
import httpx
import binascii
from concurrent.futures import ThreadPoolExecutor
import threading
httpx._config.DEFAULT_CIPHERS += ":ALL:@SECLEVEL=1"
userArr=[]
stopArr=[]
runUserCookie={}
runCookies={}
successPhone={}
jsCache = 'Cache.js'
userCache='./Cache.json'

if os.path.exists(userCache):
    with open(userCache, 'r', encoding='utf-8') as fileCache:
        print(f'▶️  开始运行 ')
        contents=fileCache.read()
        # print(contents)
        load_token = json.loads(contents)
else:
    print('▶️  开始运行')
    load_token={}
filename='Cache.js'
if os.path.exists(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        fileContent = file.read()
else:
    fileContent=''

js_code_ym = '''delete __filename
delete __dirname
ActiveXObject = undefined

window = global;


content="content_code"


navigator = {"platform": "Linux aarch64"}
navigator = {"userAgent": "CtClient;11.0.0;Android;13;22081212C;NTIyMTcw!#!MTUzNzY"}

location={
    "href": "https://",
    "origin": "",
    "protocol": "",
    "host": "",
    "hostname": "",
    "port": "",
    "pathname": "",
    "search": "",
    "hash": ""
}

i = {length: 0}
base = {length: 0}
div = {
    getElementsByTagName: function (res) {
        console.log('div中的getElementsByTagName：', res)
        if (res === 'i') {
            return i
        }
    return '<div></div>'

    }
}

script = {

}
meta = [
    {charset:"UTF-8"},
    {
        content: content,
        getAttribute: function (res) {
            console.log('meta中的getAttribute：', res)
            if (res === 'r') {
                return 'm'
            }
        },
        parentNode: {
            removeChild: function (res) {
                console.log('meta中的removeChild：', res)
                
              return content
            }
        },
        
    }
]
form = '<form></form>'


window.addEventListener= function (res) {
        console.log('window中的addEventListener:', res)
        
    }
    

document = {

   
    createElement: function (res) {
        console.log('document中的createElement：', res)
        
        
       if (res === 'div') {
            return div
        } else if (res === 'form') {
            return form
        }
        else{return res}
            
        


    },
    addEventListener: function (res) {
        console.log('document中的addEventListener:', res)
        
    },
    appendChild: function (res) {
        console.log('document中的appendChild：', res)
        return res
    },
    removeChild: function (res) {
        console.log('document中的removeChild：', res)
    },
    getElementsByTagName: function (res) {
        console.log('document中的getElementsByTagName：', res)
        if (res === 'script') {
            return script
        }
        if (res === 'meta') {
            return meta
        }
        if (res === 'base') {
            return base
        }
    },
    getElementById: function (res) {
        console.log('document中的getElementById：', res)
        if (res === 'root-hammerhead-shadow-ui') {
            return null
        }
    }

}

setInterval = function () {}
setTimeout = function () {}
window.top = window


'ts_code'



function main() {
    cookie = document.cookie.split(';')[0]
    return cookie
}'''



#加密参数
key = b'1234567`90koiuyhgtfrdews'
iv = 8 * b'\0'

public_key_b64 = '''-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDBkLT15ThVgz6/NOl6s8GNPofdWzWbCkWnkaAm7O2LjkM1H7dMvzkiqdxU02jamGRHLX/ZNMCXHnPcW/sDhiFCBN18qFvy8g6VYb9QtroI09e176s+ZCtiv7hbin2cCTj99iUpnEloZm19lwHyo69u5UMiPMpq0/XKBO8lYhN/gwIDAQAB
-----END PUBLIC KEY-----'''

public_key_data = '''-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC+ugG5A8cZ3FqUKDwM57GM4io6JGcStivT8UdGt67PEOihLZTw3P7371+N47PrmsCpnTRzbTgcupKtUv8ImZalYk65dU8rjC/ridwhw9ffW2LBwvkEnDkkKKRi2liWIItDftJVBiWOh17o6gfbPoNrWORcAdcbpk2L+udld5kZNwIDAQAB
-----END PUBLIC KEY-----'''
def newTime():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
def encrypt(text):    
    cipher = DES3.new(key, DES3.MODE_CBC, iv)
    ciphertext = cipher.encrypt(pad(text.encode(), DES3.block_size))
    return ciphertext.hex()

def decrypt(text):
    ciphertext = bytes.fromhex(text)
    cipher = DES3.new(key, DES3.MODE_CBC, iv)
    plaintext = unpad(cipher.decrypt(ciphertext), DES3.block_size)
    return plaintext.decode()
    
def encrypt_b64(plaintext):
    # 将字符串转换为bytes类型
    public_key_pem_bytes = public_key_b64.encode('ascii')

    # 使用load_pkcs1_openssl_pem方法加载公钥
    public_key = rsa.PublicKey.load_pkcs1_openssl_pem(public_key_pem_bytes)
    # public_key = RSA.import_key(public_key_b64)
    # cipher = PKCS1_v1_5.new(public_key)
    ciphertext = rsa.encrypt(plaintext.encode('utf-8'), public_key)
    # ciphertext = cipher.encrypt(plaintext.encode())
    return base64.b64encode(ciphertext).decode()


# public_key_der1 = base64.b64decode(public_key_data)  

# 加载公钥  

def rsa_encrypt_block(plaintext_block):
    # 将字符串转换为bytes类型
    public_key_pem_bytes = public_key_data.encode('ascii')

    # 使用load_pkcs1_openssl_pem方法加载公钥
    public_key = rsa.PublicKey.load_pkcs1_openssl_pem(public_key_pem_bytes)
    # cipher = PKCS1_v1_5.new(public_key)
    encrypted_block = rsa.encrypt(plaintext_block.encode('utf-8'), public_key)
    # encrypted_block = cipher.encrypt(plaintext_block.encode())
    return binascii.hexlify(encrypted_block).decode()

def encrypt_para(plaintext, block_size=32):
    # public_key = RSA.import_key(public_key_data)
    encrypted_text = ''
    # 分段加密
    for i in range(0, len(plaintext), block_size):
        block = plaintext[i:i + block_size]
        encrypted_block = rsa_encrypt_block(block)
        encrypted_text += encrypted_block
    return encrypted_text
def encode_phone(text):
    encoded_chars = []
    for char in text:
        encoded_chars.append(chr(ord(char) + 2))
    return ''.join(encoded_chars)

def check_time_in_range(start_time, end_time):
    current_time = datetime.datetime.now().time()
    if start_time <= current_time <= end_time:
        return True
    return False
def encodePhoneLog(phone):
    return f'{str(phone)[:3]+"****"+str(phone)[-4:]}'

def aes_ecb_encrypt(plaintext, key):
    key = key.encode('utf-8')
    if len(key) not in [16, 24, 32]:
        raise ValueError("密钥长度必须为16/24/32字节")
    padded_data = pad(plaintext.encode('utf-8'), AES.block_size)
    cipher = AES.new(key, AES.MODE_ECB)
    ciphertext = cipher.encrypt(padded_data)
    return base64.b64encode(ciphertext).decode('utf-8')
def sendmsg(content,uid):
    try:
        # 没有这个文件会抛出异常，不会执行else里面的内容
        data = {
        "appToken": appToken,
        "content": f"{content}",
        "summary": f"电信抢兑成功",
        "contentType": 1,
        "topicIds": [],
        "uids": [
            uid
        ],
        "url": "",
        "verifyPay": 'false'
        }
        response = httpx.post(
        'https://wxpusher.zjiecode.com/api/send/message', json=data)
        print(response.text)
    except Exception as e:
        print(f"发生了异常:{e}")
    

def initCookie(getUrl='https://wapact.189.cn:9001/gateway/standExchange/detailNew/exchange'):
    global js_code_ym,fileContent
    cookie=''
    response=httpx.post(getUrl)
    # print(response.headers)
    content=response.text.split(' content="')[2].split('" r=')[0]
    code1 = response.text.split('$_ts=window')[1].split('</script><script type="text/javascript"')[0]
    code1Content = '$_ts=window' + code1
     # 文件不存在，从网络下载
    Url = response.text.split('$_ts.lcd();</script><script type="text/javascript" charset="utf-8" src="')[1].split('" r=')[0]
    urls  = getUrl.split('/')
    rsurl = urls[0] + '//' + urls[2] + Url
    filename='Cache.js'
    # 检查文件是否存在
    if fileContent=='':
        if not os.path.exists(filename):
            print('⛔️  文件不存在，从网络下载')
            # 如果文件不存在，则从远程 URL 下载文件
            fileRes = httpx.get(rsurl)
            fileContent=fileRes.text
            # 检查请求是否成功
            if fileRes.status_code == 200:
                with open(filename, 'w', encoding='utf-8') as file:
                    file.write(fileRes.text)
            else:
                print(f"Failed to download {rsurl}. Status code: {fileRes.status_code}")

    # fileContent = fileCode.text
    # print(content)
    # print(code1Content)
    if(response.headers['Set-Cookie']):
        cookie=response.headers['Set-Cookie'].split(';')[0].split('=')[1]
    runJs=js_code_ym.replace('content_code', content).replace("'ts_code'",code1Content+fileContent)
    execjsRun=RefererCookie(runJs)
    return {
        'cookie':cookie,
        'execjsRun':execjsRun
    }
def RefererCookie(runJs):
    try:
        execjsRun= execjs.compile(runJs)
        # runlog=execjsRun.call('main')
        # return runlog.split('=')[1]
        return execjsRun
    except execjs._exceptions.CompileError as e:
        print(f"JavaScript 编译错误: {e}")
    except execjs._exceptions.RuntimeError as e:
        print(f"JavaScript 运行时错误: {e}")
    except Exception as e:
        print(f"其他错误: {e}")
def get_ticket(phone,userId,token):
    r = httpx.post('https://appgologin.189.cn:9031/map/clientXML',data='<Request><HeaderInfos><Code>getSingle</Code><Timestamp>'+datetime.datetime.now().strftime("%Y%m%d%H%M%S")+'</Timestamp><BroadAccount></BroadAccount><BroadToken></BroadToken><ClientType>#9.6.1#channel50#iPhone 14 Pro Max#</ClientType><ShopId>20002</ShopId><Source>110003</Source><SourcePassword>Sid98s</SourcePassword><Token>'+token+'</Token><UserLoginName>'+phone+'</UserLoginName></HeaderInfos><Content><Attach>test</Attach><FieldData><TargetId>'+encrypt(userId)+'</TargetId><Url>4a6862274835b451</Url></FieldData></Content></Request>',headers={'user-agent': 'CtClient;10.4.1;Android;13;22081212C;NTQzNzgx!#!MTgwNTg1'})
    #printn(phone, '获取ticket', re.findall('<Reason>(.*?)</Reason>',r.text)[0])
    tk = re.findall('<Ticket>(.*?)</Ticket>',r.text)
    if len(tk) == 0:        
        return False
    return decrypt(tk[0])
def userLoginNormal(phone,password):
    try:
        alphabet = 'abcdef0123456789'
        uuid = [''.join(random.sample(alphabet, 8)),''.join(random.sample(alphabet, 4)),'4'+''.join(random.sample(alphabet, 3)),''.join(random.sample(alphabet, 4)),''.join(random.sample(alphabet, 12))]
        timestamp=datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        loginAuthCipherAsymmertric = 'iPhone 14 15.4.' + uuid[0] + uuid[1] + phone + timestamp + password[:6] + '0$$$0.'
        
        reqdata={"headerInfos": {"code": "userLoginNormal", "timestamp": timestamp, "broadAccount": "", "broadToken": "", "clientType": "#9.6.1#channel50#iPhone 14 Pro Max#", "shopId": "20002", "source": "110003", "sourcePassword": "Sid98s", "token": "", "userLoginName": phone}, "content": {"attach": "test", "fieldData": {"loginType": "4", "accountType": "", "loginAuthCipherAsymmertric": encrypt_b64(loginAuthCipherAsymmertric), "deviceUid": uuid[0] + uuid[1] + uuid[2], "phoneNum": encode_phone(phone), "isChinatelecom": "0", "systemVersion": "15.4.0", "authentication": password}}}
        r = httpx.post('https://appgologin.189.cn:9031/login/client/userLoginNormal',json=reqdata).json()
        l = r['responseData']['data']['loginSuccessResult']
        
        if l:
            load_token[phone] = l
            with open(userCache, 'w', encoding='utf-8') as f:
                json.dump(load_token, f)
            ticket = get_ticket(phone,l['userId'],l['token']) 
            return ticket
        print(f'❗️❗️❗️❗️ {phone} 登录失败 {r["responseData"]["resultDesc"]}')
        return False
    except Exception as e:
        print(f"其他错误: {e}")
def unifiedUserLogin(ticket,cookies):
    data={
        "ticket": ticket,
        "backUrl": "https%3A%2F%2Fwapact.189.cn%3A9001",
        "platformCode": "P201010301",
        "loginType": 2
    }
    encrypted_data = aes_ecb_encrypt(json.dumps(data), 'telecom_wap_2018')
    userToken=httpx.post('https://wapact.189.cn:9001/unified/user/login',data=encrypted_data,cookies=cookies,headers={'Content-Type': 'application/json'})
    token="Bearer " +userToken.json()['biz']['token']
    return token
def getUserDetail(ticket,myExchanList,runcookie):
    cookies={
        'yiUIIlbdQT3fO':runcookie['cookie'],
        'yiUIIlbdQT3fP':runcookie['execjsRun'].call('main').split('=')[1]
    }
    token=unifiedUserLogin(ticket,cookies)
    headers={
        'Authorization':token
    }
    cookies={
        'yiUIIlbdQT3fO':runcookie['cookie'],
        'yiUIIlbdQT3fP':runcookie['execjsRun'].call('main').split('=')[1]
    }
    queryInfoRes=httpx.get('https://wapact.189.cn:9001/gateway/golden/api/queryInfo',headers=headers,cookies=cookies)
    amountTotal=queryInfoRes.json()['biz']['amountTotal']
    cookies={
        'yiUIIlbdQT3fO':runcookie['cookie'],
        'yiUIIlbdQT3fP':runcookie['execjsRun'].call('main').split('=')[1]
    }
    ExchangeGoodslistRes=httpx.get('https://wapact.189.cn:9001/gateway/golden/goldGoods/getGoodsList?userType=1&page=1&order=3&tabOrder=1',headers=headers,cookies=cookies)
    # print(ExchangeGoodslistRes.json()['biz']['ExchangeGoodslist'])
    runArr = []
    
    # 获取当前时间
    now = datetime.datetime.now()
    current_hour = now.hour
    ExchangeGoodslist=ExchangeGoodslistRes.json()['biz']['ExchangeGoodslist']
    try:
        for item in ExchangeGoodslist:
            is_redeemed = item['title'] in myExchanList
            if not is_redeemed:
                if current_hour < 13:
                    if '0.5元' in item['title'] or '5元' in item['title']:
                        match = re.search(r'\d+', item['amount']).group()
                        if match:
                            amount = int(match)
                        if amount <= amountTotal:
                            runArr.append({
                                'id': item['id'],
                                'title': item['title'],
                            })
                else:
                    if '1元' in item['title'] or '10元' in item['title']:
                        match = re.search(r'\d+', item['amount']).group()
                        if match:
                            amount = int(match)
                        if amount <= amountTotal:
                            runArr.append({
                                'id': item['id'],
                                'title': item['title'],
                            })
    except Exception as e:
        print(f"发生了异常:{e}")
    return {
        'amountTotal':amountTotal,
        'runArr':runArr,
        'token':token
    }
def getExchangetRecords(ticket,runcookie):
    cookies={
        'yiUIIlbdQT3fO':runcookie['cookie'],
        'yiUIIlbdQT3fP':runcookie['execjsRun'].call('main').split('=')[1]
    }
    loginRes=httpx.get(f'https://wappark.189.cn/jt-sign/ssoHomLogin?ticket={ticket}',cookies=cookies)
    userSign=loginRes.json()
    # return
    try:
        data={
            'accId':userSign['accId'],
            'page': 0,
            'size': 10
        }
        paraTxt=json.dumps(data, ensure_ascii=False)
        data={
            'para':encrypt_para(paraTxt)
        }
    except Exception as e:
        print(f'{userSign}')
        print(f"发生了异常:{e}")
    headers={
        'Content-Type': 'application/json;charset=utf-8',
        'sign': userSign['sign']
    }
    cookies={
        'yiUIIlbdQT3fO':runcookie['cookie'],
        'yiUIIlbdQT3fP':runcookie['execjsRun'].call('main').split('=')[1]
    }
    RecordsListRes=httpx.post('https://wappark.189.cn/jt-sign/paradise/getCoinMallExchangetRecords',json=data,headers=headers,cookies=cookies)
    # print(RecordsListRes.json()['data'])
    records=RecordsListRes.json()['data']
    current_month = datetime.datetime.now().month
    filtered_records = []
    for record in records:
        title = record.get('title', '')
        created_date = record.get('createdDate', '')
        # 解析createdDate中的月份
        try:
            created_month = datetime.datetime.strptime(created_date, '%Y-%m-%d %H:%M:%S.%f').month
        except ValueError:
            continue
        # 检查title是否包含'话费'以及createdDate是否为当前月份
        if '话费' in title and created_month == current_month:
            filtered_records.append(title)
    return filtered_records

def exchange(phone,initArr,runItem,uid):
    try:
        global successPhone,runUserCookie,stopArr,runCookies
        # if str(phone) not in runUserCookie:
        #     runUserCookie[str(phone)]=initCookie()
        # cookies={
        #     'yiUIIlbdQT3fO':runUserCookie[str(phone)]['cookie'],
        #     'yiUIIlbdQT3fP':runUserCookie[str(phone)]['execjsRun'].call('main').split('=')[1]
        # }
        cookies={
            'yiUIIlbdQT3fO':runCookies['cookie'],
            'yiUIIlbdQT3fP':runCookies['execjsRun'].call('main').split('=')[1]
        }
        headers={
            'Authorization':initArr['token'],
            "User-Agent": "Mozilla/5.0 (Linux; Android 13; 22081212C Build/TKQ1.220829.002) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.97 Mobile Safari/537.36",
            "Referer": "https://wapact.189.cn:9001/JinDouMall/JinDouMall_independentDetails.html",
        }
        data={
            'activityId':runItem['id']
        }
        exchangeRes=httpx.post('https://wapact.189.cn:9001/gateway/standExchange/detailNew/exchange',json=data,cookies=cookies,headers=headers)
        
        # exchangeRes.json()['biz']['resultCode'] == '410' 未开始
        if exchangeRes.status_code == 200:
            if exchangeRes.json()['biz']['resultCode'] == '0':
                print(f"🎉 🎉 🎉 {encodePhoneLog(phone)} 兑换成功 {runItem['title']}  {newTime()}")
                if uid:
                    successPhone.setdefault(uid, {}).setdefault(phone, f'🎉 🎉 🎉 {phone} 兑换成功 {runItem["title"]}  {newTime()}\n')
                stopArr.append(phone)
            elif exchangeRes.json()['biz']['resultCode'] == '412':
                print(f'⚠️ {encodePhoneLog(phone)} 兑换失败，兑换次数已达上限  {newTime()}')
                stopArr.append(phone)
            elif exchangeRes.json()['biz']['resultCode'] == '413':
                print(f'⚠️ {encodePhoneLog(phone)} 兑换失败，商品已兑完  {newTime()}')
                stopArr.append(phone)
                pass
                # exchange(phone,initArr,runCookies,runItem)
            elif exchangeRes.json()['biz']['resultCode'] == '410':
                print(f'⚠️ 兑换失败，兑换时间未到  {newTime()}')
                pass
                # print(f'⚠️ 兑换失败，兑换时间未到  {newTime()}')
            else:
                print(f'⚠️ {encodePhoneLog(phone)} 兑换失败，未知错误  {newTime()}',exchangeRes.json())
                # print(f'⚠️ ⚠️ {exchangeRes.json()["biz"]}  {newTime()}')
                # cookie1=initCookie()
                # print(f'❗️❗️❗️❗️ 未知错误  {exchangeRes.json()}')
                # runUserCookie[str(phone)]=cookie1
                pass
        elif exchangeRes.status_code == 412:
            stopArr.append(phone)
            # cookie1=initCookie()
            # print(f"❗️❗️❗️❗️ 瑞数过期,刷新成功  {newTime()}")
            # runUserCookie[str(phone)]=cookie1
            pass
    except Exception as e:
        pass
        # print(f"❗️❗️❗️❗️ 发生了报错:{e}")
        # exchange(phone,initArr,runItem)
    
def initUser(phone,password,uid,runcookie):
    global userArr
    ticket=False
    # print(load_token)
    # return
    if phone in load_token:
        ticket = get_ticket(phone,load_token[phone]['userId'],load_token[phone]['token'])
        if ticket :
            print(f'✅️ {encodePhoneLog(phone)} 缓存登录成功  {newTime()}')
    if ticket == False:
        ticket = userLoginNormal(phone,password)
        if ticket :
            print(f'✅️ {encodePhoneLog(phone)} 密码登录成功  {newTime()}')
    myExchanList=getExchangetRecords(ticket,runcookie)
    
    initArr=getUserDetail(ticket,myExchanList,runcookie)
    kdnr=",".join([item["title"] for item in initArr["runArr"]])
    ydnr=",".join(myExchanList)
    print(f'🧧 {encodePhoneLog(phone)} 当前金豆 {initArr["amountTotal"]}  {newTime()}\n🎁 {encodePhoneLog(phone)} 已兑内容 {ydnr}\n⭕️ {encodePhoneLog(phone)} 可兑内容 {kdnr}')
    # print(f'🎁 {encodePhoneLog(phone)} 已兑内容 {','.join(myExchanList)}')
    # print(f'⭕️ {encodePhoneLog(phone)} 可兑内容 {','.join([item['title'] for item in initArr['runArr']])}')
    userArr.append({
        'phone':phone,
        'uid':uid,
        'initArr':initArr
    })
    return {
        'phone':phone,
        'initArr':initArr
    }
    
    # runcookie=initCookie()
    # exchange(phone,initArr,runcookie,item)
    # try:
    #     for item in initArr['runArr']:
    #         executor.submit(exchange,phone,initArr,runcookie,item)
    # except Exception as e:
    #     print(f"发生了异常:{e}")    
    # print(ticket)
executor=None
def main():
    global userArr,stopArr,executor,phoneArr,successPhone,runCookies
    
    num=len(phoneArr)*2
    executor=ThreadPoolExecutor(max_workers=num)
    userArr=[]
    stopArr=[]
    runcookie=initCookie()
    for item in phoneArr:
        executor.submit(initUser,item['phone'],item['password'],item['uid'],runcookie)

    executor.shutdown(wait=True)
    print(f'✅️ ✅️ 登录成功账号数 {len(userArr)}')
    executor=ThreadPoolExecutor(max_workers=num)
    start_time1 = datetime.datetime.strptime('10:00:00', '%H:%M:%S').time()
    end_time1 = datetime.datetime.strptime('12:20:00', '%H:%M:%S').time()
    start_time2 = datetime.datetime.strptime('14:00:00', '%H:%M:%S').time()
    end_time2 = datetime.datetime.strptime('22:05:00', '%H:%M:%S').time()
    isRun = True
    while True:
        if (check_time_in_range(start_time1, end_time1) and isRun) or (check_time_in_range(start_time2, end_time2) and isRun):
            print(f"☑️ ☑️ ☑️  到点开始执行任务  {newTime()}")
            runCookies=initCookie()
            print(f'获取瑞数加密成功  {newTime()}')
            isRun=False
            for item in userArr:
                if len(item['initArr']['runArr']) > 0:
                    # yxqdnr=','.join([item["title"] for item in item["initArr"]["runArr"]])
                    print(f'⭕️ {encodePhoneLog(item["phone"])} 运行抢兑内容 {item["initArr"]["runArr"][0]["title"]}  {newTime()}')
                    executor.submit(submitExchange, item['phone'], item['initArr'],item["initArr"]["runArr"][0],item['uid'])
                    # for item2 in item['initArr']['runArr']:
                    #     try:
                    #         executor.submit(submitExchange, item['phone'], item['initArr'],item2)
                    #         # threading.Thread(submitExchange, args=(item['phone'], item['initArr'],item2)).start()
                    #     except Exception as e:
                    #         print(f"❗️❗️❗️❗️ 发生了异常:{e}")
            break
        # 暂停一段时间后再检查
        time.sleep(1)
    
    
    executor.shutdown()
    print(f'抢兑结束---开始推送中奖名单')
    mznum=0
    for uid in successPhone:
        content=''
        for phone in successPhone[uid]:
            mznum+=1
            content+=successPhone[uid][phone]
        sendmsg(f'中国电信抢兑成功名单：\n{content}',uid)
        time.sleep(1)
    print(f'抢兑成功次数：{mznum}')


def submitExchange(phone,initArr,runItem,uid):
    global stopArr
    with ThreadPoolExecutor(max_workers=submitMaxWorkers) as executor_two:
        try:
            while phone not in stopArr:
                # threading.Thread(target=exchange, args=(phone, initArr,runItem)).start()
                executor_two.submit(exchange, phone, initArr,runItem,uid)
                time.sleep(submitTime)
        except Exception as e:
            print(f"❗️❗️❗️❗️ 发生了异常:{e}")

main()

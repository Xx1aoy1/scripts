"""
人脸请用同目录下另外一个脚本
cron: 59 6 * * *
const $ = new Env("太平通兑换");
"""
import os
import base64
import hashlib
import ssl
import requests
import rsa
import hmac
import time
import datetime
import binascii
import json
import uuid
from Crypto.PublicKey import RSA
from Crypto.Util.number import bytes_to_long, long_to_bytes
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from requests.adapters import HTTPAdapter
from collections import OrderedDict

#抢券重发次数
times = 30

#变量名称:tptdh
#变量格式:手机号#x-ac-token-ticket#x-ac-device-id#x-ac-black-box
tptdh = ''

#变量名称:tptdhsj
#变量名称:开始兑换时间
tptdhsj = '6:59:59'

#变量名称:tptdhsp
#变量格式:兑换商品id
#10京东e卡
tptdhsp = "121"


'''
1e卡 66
2e卡 169
5e卡 120
10e卡 121
20e卡 122
50e卡 144

20盒马 84
10盒马 83
5盒马 82

50猫卡 145
20猫卡 129
10猫卡 128
5猫卡 127

100元话费券 110
'''




tptdh = os.environ.get('tptdh') or tptdh
tptdhsj = os.environ.get('tptdhsj') or tptdhsj
tptdhsp = os.environ.get('tptdhsp') or tptdhsp
phone, ticket, device_id, box = tptdh.split('&')[-1].split('#')



headers = {
    "x-ac-api-caller": "h5",
    "x-ac-time": str(int(time.time()*1000)),
    "x-ac-api-base": "2",
    "x-ac-app-version":"4.6.4",
    "x-ac-os-info":"Android",
    "x-ac-device-id":device_id,
    "x-ac-trace-no":f"{uuid.uuid4()}-1744479572058-{int(time.time()*1000)}",
    "x-ac-token-ticket": ticket,
    "x-ac-black-box":box,
    "x-ac-session-id": f"{int(time.time()*1000)}FUmqRwzf02MbC9rU6qbyxs",
    "x-ac-app-store-id": "10295",
    "User-Agent":"okhttp/4.3.1",
    "Content-Type": "application/json"
}


try:
    from notify import send
    print("青龙推送: 加载成功")
except:
    def send(title, content):
        print("未配置推送")
        return
        
        
class LegacyRenegotiationAdapter(HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        context = ssl.create_default_context()
        # 允许旧版重新协商（降低安全性）
        context.options |= 0x4  # OP_LEGACY_SERVER_CONNECT
        kwargs["ssl_context"] = context
        return super().init_poolmanager(*args, **kwargs)

# 使用自定义适配器
session = requests.Session()
session.mount("https://", LegacyRenegotiationAdapter())

class SecurityDTO:
    def __init__(self):
        self.sign = None
        self.securityKey = None
        self.body = None

TO_BE_SIGNED_HEADER_NAMES = [
    "x-ac-app-version",
    "x-ac-device-id",
    "x-ac-os-info",
    "x-ac-session-id",
    "x-ac-time",
    "x-ac-token-ticket",
    "x-ac-trace-no",
]
# 正确格式示例（公钥）
PUBLIC_KEY_STR = 'MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCR1BmnrfdI/wK3IloIPfAjmr/VzzEyp2GO8srJMoOpIcSXFweBPqLdIIwpbalog47pbcG3PnDuqWvx/Gr/JNsvQ28QkDW8gkp9Ks6Xg5L1Bb2ye65IhLx6tLoBJ85XzFPWLfUghJ95n0grSgWvFlkTMAkc5disnN1vmdQ0aWPfpwIDAQAB'

def rsa_no_padding_encrypt(public_key, plaintext: bytes) -> bytes:
    # 将明文转换为大整数
    m = bytes_to_long(plaintext)
    # 执行模幂运算（公钥指数e，模数n）
    public_key = RSA.import_key(f'-----BEGIN RSA PRIVATE KEY-----\n{PUBLIC_KEY_STR}\n-----END RSA PRIVATE KEY-----')  
    c = pow(m, public_key.e, public_key.n)    
    return long_to_bytes(c)[79:]
    
def add_sign(map_params, str_host, str_body):
    security_dto = SecurityDTO()
    try:
        init_aes_key = os.urandom(32)        
        generate_random_bytes = os.urandom(16)
        string_to_be_signed = get_string_to_be_signed(map_params, str_host, str_body)
        hmac_key = generate_random_bytes
        hmac_sha256 = hmac.new(hmac_key, string_to_be_signed.encode('utf-8'), hashlib.sha256)
        sign_hex = hmac_sha256.hexdigest().lower()

        body = None
        if str_body and 'Content-Type' in map_params and map_params['Content-Type'] == 'application/json':
            iv = generate_random_bytes
            cipher = AES.new(init_aes_key, AES.MODE_CBC, iv)
            padded_data = pad(str_body.encode('utf-8'), AES.block_size)
            body = cipher.encrypt(padded_data)
        
        # Combine AES key and IV for RSA encryption
        combined = init_aes_key + generate_random_bytes
        
        # RSA encryption with public key

        rsa_key = f"-----BEGIN PUBLIC KEY-----\n{PUBLIC_KEY_STR}\n-----END PUBLIC KEY-----"
        pubkey = rsa.PublicKey.load_pkcs1_openssl_pem(rsa_key.encode())
        encrypted_combined = rsa.encrypt(combined, pubkey)
    
        security_key_hex = encrypted_combined.hex().lower()
        
        security_dto.sign = sign_hex
        security_dto.securityKey = security_key_hex
        security_dto.body = body
        
    except Exception as e:
       print(f"Error in add_sign: {str(e)}")
    
    return security_dto

def get_string_to_be_signed(map_params, str_uri, str_body):
    headers = OrderedDict()
    for header in TO_BE_SIGNED_HEADER_NAMES:
        if header in map_params and map_params[header]:
            headers[header] = map_params[header]
    return "requestBody="+str_body+"&requestURI="+str_uri+ "&"+'&'.join([f"{k}={v}" for k, v in headers.items()])


def decrypt_response_body(encrypted_security_key_hex, encrypted_body):
    
    decrypted_key = rsa_no_padding_encrypt(PUBLIC_KEY_STR, binascii.unhexlify(encrypted_security_key_hex))
    aes_key = decrypted_key[:32]
    iv = decrypted_key[32:48]
    # AES decryption
    cipher = AES.new(aes_key, AES.MODE_CBC, iv)
    decrypted_body = cipher.decrypt(encrypted_body)
    
    decrypted_body = unpad(decrypted_body, AES.block_size)
    return json.loads(decrypted_body.decode())
        

def run_Time(sj):
    sj = sj.split(':')
    hour,miute,second = int(sj[0]), int(sj[1]), int(sj[2])
    date = datetime.datetime.now()
    date_zero = datetime.datetime.now().replace(year=date.year, month=date.month, day=date.day, hour=hour, minute=miute, second=second)
    date_zero_time = int(time.mktime(date_zero.timetuple()))
    return date_zero_time
    
def main():
    #getAcct = session.get('https://ecustomer.cntaiping.com/tpayms/app/tpay/account/getAcct', headers=headers).json()
    queryUserPointsDetail = session.post('https://ecustomer.cntaiping.com/campaignsms/integral/queryUserPointsDetail', json={"sourceOrganId":"932"}, headers=headers).json()
    if '登录' in str(queryUserPointsDetail):
        print(queryUserPointsDetail)
        return
    userId = queryUserPointsDetail.get('data').get('scoreAccountInfo').get('userId')
    availableScore = queryUserPointsDetail.get('data').get('scoreAccountInfo').get('availableScore')
    twoPage = session.get(f'https://ecustomer.cntaiping.com/campaignsms/coin/exchange/twoPage?id={tptdhsp}', headers=headers).json()
    couponTitle =  twoPage.get('data').get('couponTitle')
    requiredCoin =  twoPage.get('data').get('requiredCoin')
    print(f'手机号码: {phone}\n金币余额: {availableScore}\n兑换商品: {couponTitle}\n需要金币: {requiredCoin}')
    if requiredCoin > availableScore:
        print("金币余额不足")
        return
    wt = run_Time(tptdhsj)
    if wt -time.time() >0:
        print(f'等待{int(wt -time.time())}秒')
    while wt > time.time():
        pass
    rl = 0
    for _ in range(times):
        url = "https://ecustomer.cntaiping.com/commonms/coin/exchange/receive?language=zh-cn"
        dto = add_sign(headers, "/commonms/coin/exchange/receive", json.dumps({"id":tptdhsp,"appVersion":"4.6.4","type":"43","internatCode":"0086","accountName":userId}))
        headers["x-ac-sign"] = dto.sign
        headers["x-ac-security-key"] = dto.securityKey
        try:
            response = session.post(
                url,
                headers=headers,
                data=dto.body,
                timeout=10,
            )
            response.raise_for_status()
            #print(f"Status Code: {response.status_code}")
            k = response.headers.get('x-ac-security-key')
        
            r = decrypt_response_body(k, response.content)
            msg = r.get('msg') or '成功'
            print(f'第{_+1}次兑换: {msg}')
            if '人脸' in msg and rl ==0:
                rl += 1
                url = "https://ecustomer.cntaiping.com/userms/tpt-face/compare?language=zh-cn"
                try:
                    with open('tpt.json') as f:
                        data = f.read()
                except:
                    print("获取人脸数据失败")
                    return
                    
                dto = add_sign(headers, "/userms/tpt-face/compare", data)
                headers["x-ac-sign"] = dto.sign
                headers["x-ac-security-key"] = dto.securityKey
                try:
                    response = session.post(
                        url,
                        headers=headers,
                        data=dto.body,
                        timeout=10,
                    )
                    response.raise_for_status()
                    #print(f"Status Code: {response.status_code}")
                    k = response.headers.get('x-ac-security-key')
                
                    r = decrypt_response_body(k, response.content)
                    msg = r.get('desc') or r.get('msg') or r.get('data').get('msg') or '成功'
                    print(f"人脸识别: {msg}")
                except:
                    pass
                continue
            elif '成功' in msg:
                msg = f'{phone[-4:]}太平通兑换[{couponTitle}]{msg}'     
                print(msg)
                send(msg, msg)
                return
            if any(keyword in msg for keyword in {'成功', '火爆', '已兑', '上限', '人脸', '实名'}):
                return

                
                
        except requests.exceptions.RequestException as e:
            print(f"请求异常: {str(e)}")
        except ValueError as ve:
            print(f"数据解析错误: {str(ve)}")
        


# 示例用法
if __name__ == "__main__":
    # 测试add_sign
    main()

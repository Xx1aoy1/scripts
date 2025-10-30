const CryptoJS = require("crypto-js");
const crypto = require('crypto');
const axios = require('axios');
const fs = require('fs');
const JSEncrypt = require('node-jsencrypt');

let pubKey = `MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDBkLT15ThVgz6/NOl6s8GNPofdWzWbCkWnkaAm7O2LjkM1H7dMvzkiqdxU02jamGRHLX/ZNMCXHnPcW/sDhiFCBN18qFvy8g6VYb9QtroI09e176s+ZCtiv7hbin2cCTj99iUpnEloZm19lwHyo69u5UMiPMpq0/XKBO8lYhN/gwIDAQAB`
const decrypt = new JSEncrypt(); // 创建加密对象实例

const mySetTimeout = setTimeout.bind(globalThis);

var encrypt_req = function (key, iv, text) {
    var l = CryptoJS.enc.Utf8.parse(text);
    var e = CryptoJS.enc.Utf8.parse(key);
    CryptoJS.DES
    var a = CryptoJS.TripleDES.encrypt(l, e, {
        mode: CryptoJS.mode.CBC,
        padding: CryptoJS.pad.Pkcs7,
        iv: CryptoJS.enc.Utf8.parse(iv)
    })
    // return a.toString()   // 此方式返回base64  l8KqKSJHOBJr2W+T99S++XdV8MTy5Yvw7eXIi35j8KoEbuJqiu2JBumzz6QUbF+S
    return a.ciphertext.toString() // 返回hex格式的密文  97c2aa29224738126bd96f93f7d4bef97755f0c4f2e58bf0ede5c88b7e63f0aa046ee26a8aed8906e9b3cfa4146c5f92
}
var decrypt_req = function (key, iv, text) {
    var e = CryptoJS.enc.Utf8.parse(key);
    var WordArray = CryptoJS.enc.Hex.parse(text); // 如果text是base64形式，该行注释掉
    var text = CryptoJS.enc.Base64.stringify(WordArray); // 如果text是base64形式，该行注释掉
    var a = CryptoJS.TripleDES.decrypt(text, e, {
        mode: CryptoJS.mode.CBC,
        padding: CryptoJS.pad.Pkcs7,
        iv: CryptoJS.enc.Utf8.parse(iv)
    });
    return CryptoJS.enc.Utf8.stringify(a).toString()
}
var encrypt_aes = function (text, key = '34d7cb0bcdf07523') {
    if (typeof text != 'string') {
        text = JSON.stringify(text)
    }
    var keyContent = CryptoJS.enc.Utf8.parse(key);
    var textContent = CryptoJS.enc.Utf8.parse(text);
    return CryptoJS.AES.encrypt(textContent, keyContent, {
        mode: CryptoJS.mode.ECB,
        padding: CryptoJS.pad.Pkcs7
    }).ciphertext.toString()
}
var encrypt_aes_base64 = function (text, key = '34d7cb0bcdf07523') {
    if (typeof text != 'string') {
        text = JSON.stringify(text)
    }
    var keyContent = CryptoJS.enc.Utf8.parse(key);
    var textContent = CryptoJS.enc.Utf8.parse(text);
    return CryptoJS.AES.encrypt(textContent, keyContent, {
        mode: CryptoJS.mode.ECB,
        padding: CryptoJS.pad.Pkcs7
    }).toString()
}
var encrypt_rsa_hex = function (text) {
    // 读取公钥证书文本文件
    const publicKeyPem = "-----BEGIN PUBLIC KEY-----\n" +
        "MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC+ugG5A8cZ3FqUKDwM57GM4io6\n" +
        "JGcStivT8UdGt67PEOihLZTw3P7371+N47PrmsCpnTRzbTgcupKtUv8ImZalYk65\n" +
        "dU8rjC/ridwhw9ffW2LBwvkEnDkkKKRi2liWIItDftJVBiWOh17o6gfbPoNrWORc\n" +
        "Adcbpk2L+udld5kZNwIDAQAB\n" +
        "-----END PUBLIC KEY-----"

    // 创建一个公钥对象
    const publicKey = crypto.createPublicKey(publicKeyPem);


    if (typeof text != 'string') {
        text = JSON.stringify(text)
    }
    let str = text
    let pjzfc = ''
    for (let i = 0; i < Math.ceil(str.length / 32); i++) {
        if (i == 0) {
            pjzfc += crypto.publicEncrypt({
                key: publicKey,
                padding: crypto.constants.RSA_PKCS1_PADDING,
            }, Buffer.from(str.substring(0, 32))).toString('hex');

        } else if (i == Math.ceil(str.length / 32)) {
            pjzfc += crypto.publicEncrypt({
                key: publicKey,
                padding: crypto.constants.RSA_PKCS1_PADDING,
            }, Buffer.from(str.substring(32 * i, str.length))).toString('hex')
        } else {
            pjzfc += crypto.publicEncrypt({
                key: publicKey,
                padding: crypto.constants.RSA_PKCS1_PADDING,
            }, Buffer.from(str.substring(32 * i, 32 * (i + 1)))).toString('hex')
        }
    }
    return pjzfc
}

function TIMEstamp() {
    let date = new Date();
    var fullYear = date.getFullYear();
    var month = date.getMonth() + 1;
    var _date = date.getDate();
    var hours = date.getHours();
    var minutes = date.getMinutes();
    var seconds = date.getSeconds();
    if (month < 10) {
        month = '0' + month
    }
    if (_date < 10) {
        _date = '0' + _date
    }
    if (hours < 10) {
        hours = '0' + hours
    }
    if (minutes < 10) {
        minutes = '0' + minutes
    }
    if (seconds < 10) {
        seconds = '0' + seconds
    }
    let timestamp = fullYear + '' + month + '' + _date + '' + hours + '' + minutes + '' + seconds
    return timestamp
}

//("yyyy-MM-dd HH:mm:ss:S")
function envtime(t, e = null) {
    const s = e ? new Date(e) : new Date(); // 创建日期对象，使用传入的时间戳或默认为当前时间
    let a = {
        "M+": s.getMonth() + 1, // 月份从0开始，所以需要加1
        "d+": s.getDate(),      // 日期
        "H+": s.getHours(),     // 小时
        "m+": s.getMinutes(),   // 分钟
        "s+": s.getSeconds(),   // 秒
        "q+": Math.floor((s.getMonth() + 3) / 3), // 季度
        S: s.getMilliseconds(), // 毫秒
    };

    // 处理年份格式
    if (/(y+)/.test(t)) {
        t = t.replace(RegExp.$1, (s.getFullYear() + "").substr(4 - RegExp.$1.length));
    }

    // 处理其他时间格式
    for (let key in a) {
        if (new RegExp("(" + key + ")").test(t)) {
            t = t.replace(RegExp.$1, 1 == RegExp.$1.length ? a[key] : ("00" + a[key]).substr(("" + a[key]).length));
        }
    }

    return t;
}

// 脱敏手机号
function maskPhone(phone) {
    return phone.replace(/^(\d{3})(\d*)(\d{4})$/, "$1****$3");
}

// 延时  await wait(2000)
function wait(n) {
    return new Promise(function (resolve) {
        mySetTimeout(resolve, n);
    });
}
function TIMEstamp1() {
	let date = new Date();
	var fullYear = date.getFullYear();
	var month = date.getMonth() + 1;
	var _date = date.getDate();
	var hours = date.getHours();
	var minutes = date.getMinutes();
	var seconds = date.getSeconds();
	if (month < 10) {
		month = '0' + month
	}
	if (_date < 10) {
		_date = '0' + _date
	}
	if (hours < 10) {
		hours = '0' + hours
	}
	if (minutes < 10) {
		minutes = '0' + minutes
	}
	if (seconds < 10) {
		seconds = '0' + seconds
	}
	let timestamp = fullYear + '-' + month + '-' + _date + ' ' + hours + ':' + minutes + ":" + seconds
	return timestamp
}
async function waitt(ms) {
    const start = Date.now();
    while (Date.now() - start < ms) {
        await new Promise(resolve => process.nextTick(resolve));
    }
}

function randomString(length) {
    var str = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ';
    var result = '';
    for (var i = length; i > 0; --i)
        result += str[Math.floor(Math.random() * str.length)];
    return result;
}

async function sendMsg(content, msgtitle, appToken = "", uids = '') {
    const options = {
        url: 'https://wxpusher.zjiecode.com/api/send/message',
        method: 'post',
        headers: {
            'Content-Type': 'application/json',
        },
        data: {
            "appToken": appToken,
            "content": String(content),
            "summary": msgtitle,
            "contentType": 1,
            "topicIds": [],
            "uids": [uids],
            "verifyPayType": '2'
        }
    };
    try {
        await axios(options);
        console.log('Message sent successfully');
    } catch (error) {
        console.error('Failed to send message:', error);
    }
}
async function loginPhone(phone, password,Caches,login=false) {
    try {
        decrypt.setPrivateKey(pubKey)
        let timestamp = TIMEstamp()
        let rdmstr = randomString(16)
        // console.log(rdmstr, rdmstr.substring(0, 13));

        let encrypttext = decrypt.encrypt(`iPhone 14 15.4.${rdmstr.substring(0, 12)}${phone}${timestamp}${password}0$$$0.`)
        // console.log(encrypttext);
        let strphone = ''
        for (let a of phone) {
            if (a <= 7) {
                strphone += String(Number(a) + 2)
            } else {
                if (a == 8) {
                    strphone += ':'
                } else if (a == 9) {
                    strphone += ';'
                }
            }
        }
        let data = {
            "headerInfos": {
                "code": "userLoginNormal",
                "timestamp": timestamp,
                "broadAccount": "",
                "broadToken": "",
                "clientType": "#9.6.1#channel50#iPhone 14 Pro Max#",
                "shopId": "20002",
                "source": "110003",
                "sourcePassword": "Sid98s",
                "token": "",
                "userLoginName": phone
            },
            "content": {
                "attach": "test",
                "fieldData": {
                    "loginType": "4",
                    "accountType": "",
                    "loginAuthCipherAsymmertric": encrypttext,
                    "deviceUid": rdmstr,
                    "phoneNum": strphone,
                    "isChinatelecom": "0",
                    "systemVersion": "15.4.0",
                    "authentication": password
                }
            }
        }
        // console.log(data);
        if (!Caches||login) {
            let options = {
                url: 'https://appgologin.189.cn:9031/login/client/userLoginNormal',
                method: 'POST',
                data: data
            }
            let res = await axios(options)
            // console.log(res.data);
            // console.log(options);
            try {
                Caches = {
                    ...res.data.responseData.data.loginSuccessResult
                }
            
            } catch (error) {
                return false
            }
        }
        // console.log(res.data.responseData);
        // return
        let userInfo = {
            ...Caches
        }
        let userToken = Caches.token
        let userId = Caches.userId
        timestamp = TIMEstamp()
        data = `<Request>
                                <HeaderInfos>
                                    <Code>getSingle</Code>
                                    <Timestamp>${timestamp}</Timestamp>
                                    <BroadAccount></BroadAccount>
                                    <BroadToken></BroadToken>
                                    <ClientType>#9.6.1#channel50#iPhone 14 Pro Max#</ClientType>
                                    <ShopId>20002</ShopId>
                                    <Source>110003</Source>
                                    <SourcePassword>Sid98s</SourcePassword>
                                    <Token>${userToken}</Token>
                                    <UserLoginName>${phone}</UserLoginName>
                                </HeaderInfos>
                                <Content>
                                    <Attach>test</Attach>
                                    <FieldData>
                                        <TargetId>${encrypt_req('1234567`90koiuyhgtfrdewsaqaqsqde', '', userId)}</TargetId>
                                        <Url>4a6862274835b451</Url>
                                    </FieldData>
                                </Content>
                    </Request>`
        options = {
            url: `https://appgologin.189.cn:9031/map/clientXML`,
            method: 'post',
            data,
            'headers': {
                'Content-Type': 'application/xml;charset=utf-8'
            }
        }
        let titckRes = await axios(options)
        // console.log(titckRes.data);
        if (String(titckRes.data).includes('过期') || String(titckRes.data).includes('校验错误')) {
            return await loginPhone(phone, password,Caches,true)
        }
        let tickettext = titckRes.data.split('<Ticket>')[1].split('</Ticket>')[0]
        let uid = decrypt_req('1234567`90koiuyhgtfrdewsaqaqsqde', '', tickettext)
        // console.log(uid,'uid');
        userInfo.uid = uid
        userInfo.password = password
        userInfo.phoneNbr = phone
        return userInfo
    } catch (e) {
        return false
    }
}
// 电信登录
async function loginPhoneTwo(phone, password, Cache, ChacePath='./Cache.json',login=false) {
    try {
        decrypt.setPrivateKey(pubKey)
        let timestamp = TIMEstamp()
        let rdmstr = randomString(16)
        // console.log(rdmstr, rdmstr.substring(0, 13));

        let encrypttext = decrypt.encrypt(`iPhone 14 15.4.${rdmstr.substring(0, 12)}${phone}${timestamp}${password}0$$$0.`)
        // console.log(encrypttext);
        let strphone = ''
        for (let a of phone) {
            if (a <= 7) {
                strphone += String(Number(a) + 2)
            } else {
                if (a == 8) {
                    strphone += ':'
                } else if (a == 9) {
                    strphone += ';'
                }
            }
        }
        let data = {
            "headerInfos": {
                "code": "userLoginNormal",
                "timestamp": timestamp,
                "broadAccount": "",
                "broadToken": "",
                "clientType": "#9.6.1#channel50#iPhone 14 Pro Max#",
                "shopId": "20002",
                "source": "110003",
                "sourcePassword": "Sid98s",
                "token": "",
                "userLoginName": phone
            },
            "content": {
                "attach": "test",
                "fieldData": {
                    "loginType": "4",
                    "accountType": "",
                    "loginAuthCipherAsymmertric": encrypttext,
                    "deviceUid": rdmstr,
                    "phoneNum": strphone,
                    "isChinatelecom": "0",
                    "systemVersion": "15.4.0",
                    "authentication": password
                }
            }
        }
        // console.log(data);
        if (!Cache[phone]||login) {
            let options = {
                url: 'https://appgologin.189.cn:9031/login/client/userLoginNormal',
                method: 'POST',
                data: data
            }
            let res = await axios(options)
            Cache[phone] = {
                ...res.data.responseData.data.loginSuccessResult
            }
            console.log('写入缓存成功');
        } else {
            // console.log('读取缓存成功');
        }

        // console.log(res.data.responseData);
        // return
        let userInfo = {
            ...Cache[phone]
        }
        fs.writeFileSync(ChacePath, JSON.stringify(Cache, null, 4), 'utf8')
        let userToken = Cache[phone].token
        let userId = Cache[phone].userId
        timestamp = TIMEstamp()
        data = `<Request>
							<HeaderInfos>
								<Code>getSingle</Code>
								<Timestamp>${timestamp}</Timestamp>
								<BroadAccount></BroadAccount>
								<BroadToken></BroadToken>
								<ClientType>#9.6.1#channel50#iPhone 14 Pro Max#</ClientType>
								<ShopId>20002</ShopId>
								<Source>110003</Source>
								<SourcePassword>Sid98s</SourcePassword>
								<Token>${userToken}</Token>
								<UserLoginName>${phone}</UserLoginName>
							</HeaderInfos>
							<Content>
								<Attach>test</Attach>
								<FieldData>
									<TargetId>${encrypt_req('1234567`90koiuyhgtfrdewsaqaqsqde', '', userId)}</TargetId>
									<Url>4a6862274835b451</Url>
								</FieldData>
							</Content>
				</Request>`
        options = {
            url: `https://appgologin.189.cn:9031/map/clientXML`,
            method: 'post',
            data,
            'headers': {
                'Content-Type': 'application/xml;charset=utf-8'
            }
        }
        let titckRes = await axios(options)
        // console.log(titckRes.data);
        if (String(titckRes.data).includes('过期') || String(titckRes.data).includes('校验错误')) {
            return await loginPhone(phone, password, Cache, ChacePath,true)
        }
        let tickettext = titckRes.data.split('<Ticket>')[1].split('</Ticket>')[0]
        let uid = decrypt_req('1234567`90koiuyhgtfrdewsaqaqsqde', '', tickettext)
        // console.log(uid,'uid');
        userInfo.uid = uid
        userInfo.password = password
        // userInfo.phoneNbr = phone
        return userInfo
    } catch (e) {
        console.log(e)
        return false
    }
}
module.exports = {
    TIMEstamp,
    envtime,
    maskPhone,
    wait,
    waitt,
    randomString,
    encrypt_req,
    decrypt_req,
    encrypt_aes,
    encrypt_rsa_hex,
    sendMsg,
    TIMEstamp1,
    loginPhone,
    loginPhoneTwo,
    encrypt_aes_base64
}
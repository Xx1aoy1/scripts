const tool = require('./tools/tool.js')
const axios = require('axios')
const getCookie = require('./tools/index.js')
const CryptoJS = require('crypto-js');
const JSEncrypt = require('node-jsencrypt');
const fs = require('fs')
const schedule = require('node-schedule');

// 初始化用户数据
let userPhone = []
if (process?.env?.dx) {
    process?.env?.dx.split('\n').map(item => {
        if (item) {
            let phone = item.split('#')[0]
            let password = item.split('#')[1]
            userPhone.push({ phone, password })
        }
    })
} else {
    return console.log('未找到环境变量，请设置环境变量dx')
}

// 加密配置
let pubKey = `MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDBkLT15ThVgz6/NOl6s8GNPofdWzWbCkWnkaAm7O2LjkM1H7dMvzkiqdxU02jamGRHLX/ZNMCXHnPcW/sDhiFCBN18qFvy8g6VYb9QtroI09e176s+ZCtiv7hbin2cCTj99iUpnEloZm19lwHyo69u5UMiPMpq0/XKBO8lYhN/gwIDAQAB`
const decrypt = new JSEncrypt();
decrypt.setPrivateKey(pubKey)
let pubKey1 = `MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC+ugG5A8cZ3FqUKDwM57GM4io6JGcStivT8UdGt67PEOihLZTw3P7371+N47PrmsCpnTRzbTgcupKtUv8ImZalYk65dU8rjC/ridwhw9ffW2LBwvkEnDkkKKRi2liWIItDftJVBiWOh17o6gfbPoNrWORcAdcbpk2L+udld5kZNwIDAQAB`
const decrypt1 = new JSEncrypt();
decrypt1.setPrivateKey(pubKey1)

// 全局变量
let Cache = {}
let cookies = null
let runArr = []
let runNumber = 0
const MAX_CONCURRENT = 3 // 最大并发数
let currentConcurrent = 0 // 当前并发数

// 初始化缓存
try {
    Cache = JSON.parse(fs.readFileSync('./Cache.json', 'utf8'));
} catch (error) {
    fs.writeFileSync('./Cache.json', JSON.stringify({}), 'utf8');
    Cache = JSON.parse(fs.readFileSync('./Cache.json', 'utf8'));
}

// 登录函数
async function loginPhone(phone, password) {
    try {
        let timestamp = tool.TIMEstamp()
        let rdmstr = tool.randomString(16)
        let encrypttext = decrypt.encrypt(`iPhone 14 15.4.${rdmstr.substring(0, 12)}${phone}${timestamp}${password}0$$$0.`)
        
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

        if (!Cache[phone]) {
            let options = {
                url: 'https://appgologin.189.cn:9031/login/client/userLoginNormal',
                method: 'POST',
                data: data
            }
            let res = await axios(options)
            Cache[phone] = {
                ...res.data.responseData.data.loginSuccessResult
            }
        }

        let userInfo = {
            ...Cache[phone]
        }
        fs.writeFileSync('./Cache.json', JSON.stringify(Cache), 'utf8')
        let userToken = Cache[phone].token
        let userId = Cache[phone].userId
        
        timestamp = tool.TIMEstamp()
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
                    <TargetId>${tool.encrypt_req('1234567`90koiuyhgtfrdewsaqaqsqde', '', userId)}</TargetId>
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
        if (String(titckRes.data).includes('过期') || String(titckRes.data).includes('校验错误')) {
            // 重新登录逻辑
            timestamp = tool.TIMEstamp()
            rdmstr = tool.randomString(16)
            encrypttext = decrypt.encrypt(`iPhone 14 15.4.${rdmstr.substring(0, 12)}${phone}${timestamp}${password}0$$$0.`)
            
            strphone = ''
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
            
            data = {
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
            
            options = {
                url: 'https://appgologin.189.cn:9031/login/client/userLoginNormal',
                method: 'POST',
                data: data
            }
            
            res = await axios(options)
            Cache[phone] = {
                ...res.data.responseData.data.loginSuccessResult
            }
            fs.writeFileSync('./Cache.json', JSON.stringify(Cache), 'utf8')
            return await loginPhone(phone, password)
        }
        
        let tickettext = titckRes.data.split('<Ticket>')[1].split('</Ticket>')[0]
        let uid = tool.decrypt_req('1234567`90koiuyhgtfrdewsaqaqsqde', '', tickettext)
        userInfo.uid = uid
        userInfo.password = password
        userInfo.phoneNbr = phone
        return userInfo
    } catch (e) {
        console.error(`用户 ${phone} 登录失败:`, e.message)
        return false
    }
}

// SSO登录
async function ssoHomLogin(ticket) {
    let options = {
        url: 'https://wappark.189.cn/jt-sign/ssoHomLogin?ticket=' + ticket,
        method: 'GET',
        headers: {
            cookie: cookies.cookie + await getCookie.RefreshCookie(),
        }
    }
    let res = await axios(options)
    return res.data
}

// 获取等级权益
async function getLevelRightsList(userinfo, signData) {
    try {
        let data = {
            phone: userinfo.phoneNbr,
        };
        
        let options = {
            url: 'https://wappark.189.cn/jt-sign/paradise/getLevelRightsList',
            method: 'POST',
            headers: {
                'Content-Type': 'application/json;charset=utf-8',
                sign: signData.sign,
                cookie: cookies.cookie + await getCookie.RefreshCookie(),
            },
            data: {
                para: tool.encrypt_rsa_hex(data)
            }
        }
        
        let res = await axios(options)
        let currentLevel = 'V' + res.data.currentLevel;
        console.log(`用户 ${userinfo.phoneNbr} 当前等级: ${currentLevel}`);
        
        console.log(`===== ${currentLevel}等级权益列表 =====`);
        res.data[currentLevel].forEach(item => {
            console.log(`权益名称: ${item.righstName}, 权益ID: ${item.id}, 可兑换次数: ${item.receiveType}`);
        });
        console.log('==============================');

        // 处理话费类权益
        for (let item of res.data[currentLevel]) {
            if (String(item.righstName).includes('话费')) {
                let state = await getState(userinfo, signData, item, currentLevel)
                if (!state) {
                    runArr.push({
                        userinfo,
                        signData,
                        item,
                        level: currentLevel
                    });
                }
            }
        }
    } catch (err) {
        console.error('获取等级权益列表失败，正在重试...', err.message);
        await new Promise(resolve => setTimeout(resolve, 2000));
        return getLevelRightsList(userinfo, signData)
    }
}

// 检查权益状态
async function getState(userinfo, signData, receive, level) {
    if (runNumber >= 15) return true
    
    let data = {
        phone: userinfo.phoneNbr,
        rightsId: receive.id,
        receiveCount: receive.receiveType
    };
    
    let options = {
        url: 'https://wappark.189.cn/jt-sign/paradise/getConversionRights',
        method: 'POST',
        headers: {
            'Content-Type': 'application/json;charset=utf-8',
            sign: signData.sign,
            cookie: cookies.cookie + await getCookie.RefreshCookie(),
        },
        data: {
            para: tool.encrypt_rsa_hex(data)
        }
    }
    
    try {
        let datas = await axios(options)
        if (datas.data['rightsStatus'].includes('已兑换') || datas.data['rightsStatus'].includes('已领取')) {
            console.log(`[${level}] 用户 ${userinfo.phoneNbr} 的权益 "${receive.righstName}" 已兑换`);
            return true
        } else {
            console.log(`[${level}] 用户 ${userinfo.phoneNbr} 的权益 "${receive.righstName}" 准备兑换中... (尝试次数: ${runNumber + 1})`);
            runNumber++
            return false
        }
    } catch (err) {
        console.error(`检查权益状态失败:`, err.message);
        return false
    }
}

// 兑换权益
async function getConversionRights(userinfo, signData, receive, level, number = 1) {
    if (number >= 50) return
    
    try {
        let data = {
            phone: userinfo.phoneNbr,
            rightsId: receive.id,
        };
        
        let options = {
            url: 'https://wappark.189.cn/jt-sign/paradise/conversionRights',
            method: 'POST',
            headers: {
                'Content-Type': 'application/json;charset=utf-8',
                sign: signData.sign,
                cookie: cookies.cookie + await getCookie.RefreshCookie(),
            },
            data: {
                para: tool.encrypt_rsa_hex(data)
            }
        }
        
        let res = await axios(options)
        if (res.data.resoultCode == '0') {
            console.log(`[${level}] 用户 ${userinfo.phoneNbr} 成功兑换 "${receive.righstName}" 权益`);
        } else if (res.data.resoultCode == '1') {
            console.log(`[${level}] 用户 ${userinfo.phoneNbr} 兑换 "${receive.righstName}" 权益失败，正在重试 (${number})`);
            await new Promise(resolve => setTimeout(resolve, 1500));
            return getConversionRights(userinfo, signData, receive, level, number + 1)
        } else if (res.data.resoultMsg == '您当前金豆数不足~') {
            console.log(`[${level}] 用户 ${userinfo.phoneNbr} 金豆不足，无法兑换 "${receive.righstName}"`);
        } else if (res.data.resoultMsg == '权益已兑换~') {
            console.log(`[${level}] 用户 ${userinfo.phoneNbr} 的权益 "${receive.righstName}" 已兑换过`);
        } else {
            console.log(`[${level}] 用户 ${userinfo.phoneNbr} 兑换 "${receive.righstName}" 权益遇到未知错误: ${res.data.resoultMsg}`);
            await new Promise(resolve => setTimeout(resolve, 1500));
            return getConversionRights(userinfo, signData, receive, level, number + 1)
        }
    } catch (err) {
        console.error(`[${level}] 用户 ${userinfo.phoneNbr} 兑换 "${receive.righstName}" 权益时发生错误:`, err.message);
        await new Promise(resolve => setTimeout(resolve, 1500));
        return getConversionRights(userinfo, signData, receive, level, number + 1)
    }
}

// 主流程
async function main(phone, passwdord) {
    if (currentConcurrent >= MAX_CONCURRENT) {
        await new Promise(resolve => setTimeout(resolve, 1000));
        return main(phone, passwdord);
    }
    
    currentConcurrent++;
    try {
        let res = await loginPhone(phone, passwdord)
        if (!res) return
        
        let res1 = await ssoHomLogin(res.uid)
        await getLevelRightsList(res, res1)
    } catch (err) {
        console.error(`处理用户 ${phone} 时出错:`, err.message);
    } finally {
        currentConcurrent--;
    }
}

// 执行兑换任务
async function run() {
    while (runArr.length > 0 && currentConcurrent < MAX_CONCURRENT) {
        let task = runArr.shift();
        currentConcurrent++;
        try {
            await getConversionRights(task.userinfo, task.signData, task.item, task.level);
        } catch (err) {
            console.error('兑换任务执行失败:', err.message);
        } finally {
            currentConcurrent--;
        }
    }
    
    if (runArr.length > 0) {
        setTimeout(run, 1000);
    }
}

// 初始化并获取用户
async function getUser() {
    console.log('获取账号成功', userPhone.length);
    
    // 初始化cookie
    cookies = await getCookie.initCookie('https://wapact.189.cn:9001/gateway/standExchange/detailNew/exchange');
    
    // 并发控制处理用户
    for (let i = 0; i < userPhone.length; i++) {
        while (currentConcurrent >= MAX_CONCURRENT) {
            await new Promise(resolve => setTimeout(resolve, 1000));
        }
        
        let item = userPhone[i];
        main(item.phone, item.password);
        await new Promise(resolve => setTimeout(resolve, 2000));
    }
    
    // 检查并执行兑换任务
    setTimeout(run, 10000);
}

// 定时任务设置
function setupSchedules() {
    // 每天23:59:30执行兑换任务
    schedule.scheduleJob('30 59 23 * * *', async function() {
        console.log('定时任务触发: 开始执行兑换任务');
        await run();
    });
    
    // 每天0:10执行获取用户任务
    schedule.scheduleJob('0 10 0 * * *', function() {
        console.log('定时任务触发: 开始获取用户信息');
        getUser();
    });
    
    console.log('定时任务已设置: 每天23:59:30执行兑换, 每天0:10获取用户');
}

// 启动应用
(async () => {
    setupSchedules();
    await getUser();
})();

/**
 * 中国电信权益兑换脚本
 * 功能：登录电信账号，获取权益列表，定时兑换话费权益
 * 特点：
 * - 多账号并发运行
 * - 定时精确到毫秒级
 * - 自动重试机制
 * - 兑换结果通知
 */

const sendNotify = require('./sendNotify'); // 引入通知模块
let userPhone = [];

// 初始化用户账号信息
if (process?.env?.dx) {
    process?.env?.dx.split('\n').map(item => {
        if (item) {
            let phone = item.split('#')[0];
            let password = item.split('#')[1];
            userPhone.push({ phone, password });
        }
    });
} else {
    console.log('未找到环境变量，请设置环境变量dx');
    return;
}

const tool = require('./tools/tool.js');
const axios = require('axios');
const getCookie = require('./tools/index.js');
const CryptoJS = require('crypto-js');
const JSEncrypt = require('node-jsencrypt');
const fs = require('fs');

// 加密公钥配置
let pubKey = `MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDBkLT15ThVgz6/NOl6s8GNPofdWzWbCkWnkaAm7O2LjkM1H7dMvzkiqdxU02jamGRHLX/ZNMCXHnPcW/sDhiFCBN18qFvy8g6VYb9QtroI09e176s+ZCtiv7hbin2cCTj99iUpnEloZm19lwHyo69u5UMiPMpq0/XKBO8lYhN/gwIDAQAB`;
const decrypt = new JSEncrypt();
decrypt.setPrivateKey(pubKey);

let pubKey1 = `MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC+ugG5A8cZ3FqUKDwM57GM4io6JGcStivT8UdGt67PEOihLZTw3P7371+N47PrmsCpnTRzbTgcupKtUv8ImZalYk65dU8rjC/ridwhw9ffW2LBwvkEnDkkKKRi2liWIItDftJVBiWOh17o6gfbPoNrWORcAdcbpk2L+udld5kZNwIDAQAB`;
const decrypt1 = new JSEncrypt();
decrypt1.setPrivateKey(pubKey1);

let Cache = {}; // 用户缓存
let cookies = null; // cookie存储
let runArr = []; // 待兑换任务队列
let runNumber = 0; // 当前运行兑换次数
const MAX_RETRY = 5; // 最大重试次数
const MAX_CONCURRENT = 15; // 最大并发兑换数

/**
 * 登录电信账号
 * @param {string} phone - 手机号
 * @param {string} password - 密码
 * @returns {Promise<Object|boolean>} 用户信息或false
 */
async function loginPhone(phone, password) {
    try {
        let startTime = Date.now();
        let timestamp = tool.TIMEstamp();
        let rdmstr = tool.randomString(16);

        // 加密登录信息
        let encrypttext = decrypt.encrypt(`iPhone 14 15.4.${rdmstr.substring(0, 12)}${phone}${timestamp}${password}0$$$0.`);
        
        // 处理手机号格式
        let strphone = '';
        for (let a of phone) {
            if (a <= 7) {
                strphone += String(Number(a) + 2);
            } else {
                if (a == 8) {
                    strphone += ':';
                } else if (a == 9) {
                    strphone += ';';
                }
            }
        }

        // 构造登录请求数据
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
        };

        // 检查缓存中是否有登录信息
        if (!Cache[phone]) {
            let options = {
                url: 'https://appgologin.189.cn:9031/login/client/userLoginNormal',
                method: 'POST',
                data: data
            };
            let res = await axios(options);
            Cache[phone] = {
                ...res.data.responseData.data.loginSuccessResult
            };
            fs.writeFileSync('./Cache.json', JSON.stringify(Cache), 'utf8');
        }

        let userInfo = {
            ...Cache[phone]
        };
        let userToken = Cache[phone].token;
        let userId = Cache[phone].userId;

        // 获取ticket
        timestamp = tool.TIMEstamp();
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
        </Request>`;
        
        let options = {
            url: `https://appgologin.189.cn:9031/map/clientXML`,
            method: 'post',
            data,
            'headers': {
                'Content-Type': 'application/xml;charset=utf-8'
            }
        };
        
        let titckRes = await axios(options);
        
        // 检查token是否过期
        if (String(titckRes.data).includes('过期') || String(titckRes.data).includes('校验错误')) {
            // 重新登录
            timestamp = tool.TIMEstamp();
            rdmstr = tool.randomString(16);
            encrypttext = decrypt.encrypt(`iPhone 14 15.4.${rdmstr.substring(0, 12)}${phone}${timestamp}${password}0$$$0.`);
            
            strphone = '';
            for (let a of phone) {
                if (a <= 7) {
                    strphone += String(Number(a) + 2);
                } else {
                    if (a == 8) {
                        strphone += ':';
                    } else if (a == 9) {
                        strphone += ';';
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
            };
            
            options = {
                url: 'https://appgologin.189.cn:9031/login/client/userLoginNormal',
                method: 'POST',
                data: data
            };
            
            let res = await axios(options);
            Cache[phone] = {
                ...res.data.responseData.data.loginSuccessResult
            };
            fs.writeFileSync('./Cache.json', JSON.stringify(Cache), 'utf8');
            return await loginPhone(phone, password);
        }
        
        let tickettext = titckRes.data.split('<Ticket>')[1].split('</Ticket>')[0];
        let uid = tool.decrypt_req('1234567`90koiuyhgtfrdewsaqaqsqde', '', tickettext);
        
        userInfo.uid = uid;
        userInfo.password = password;
        userInfo.phoneNbr = phone;
        
        console.log(`登录成功 ${phone}，耗时 ${(Date.now() - startTime) / 1000}秒`);
        return userInfo;
    } catch (e) {
        console.error(`登录失败 ${phone}:`, e.message);
        return false;
    }
}

/**
 * SSO登录
 * @param {string} ticket - 登录凭证
 * @returns {Promise<Object>} 登录结果
 */
async function ssoHomLogin(ticket) {
    try {
        let options = {
            url: 'https://wappark.189.cn/jt-sign/ssoHomLogin?ticket=' + ticket,
            method: 'GET',
            headers: {
                cookie: cookies.cookie + await getCookie.RefreshCookie(),
            }
        };
        let res = await axios(options);
        return res.data;
    } catch (e) {
        console.error('SSO登录失败:', e.message);
        throw e;
    }
}

/**
 * 获取用户权益列表
 * @param {Object} userinfo - 用户信息
 * @param {Object} signData - 签名数据
 */
async function getLevelRightsList(userinfo, signData) {
    try {
        let startTime = Date.now();
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
        };
        
        let res = await axios(options);
        let level = 'V' + res.data.currentLevel;
        
        // 筛选话费权益
        let rights = res.data[level].filter(item => String(item.righstName).includes('话费'));
        
        if (rights.length > 0) {
            console.log(`获取权益列表成功 ${userinfo.phoneNbr} ${level}，耗时 ${(Date.now() - startTime) / 1000}秒`);
            
            // 检查权益状态并加入兑换队列
            for (let item of rights) {
                let state = await getState(userinfo, signData, item, level);
                if (!state) {
                    runArr.push({
                        userinfo,
                        signData,
                        item,
                        level,
                        retryCount: 0 // 初始化重试次数
                    });
                }
            }
        }
    } catch (err) {
        console.error(`获取权益列表失败 ${userinfo.phoneNbr}:`, err.message);
        // 重试获取权益列表
        setTimeout(() => getLevelRightsList(userinfo, signData), 2000);
    }
}

/**
 * 检查权益状态
 * @param {Object} userinfo - 用户信息
 * @param {Object} signData - 签名数据
 * @param {Object} receive - 权益信息
 * @param {string} level - 用户等级
 * @returns {Promise<boolean>} 是否已兑换
 */
async function getState(userinfo, signData, receive, level) {
    if (runNumber >= MAX_CONCURRENT) return true;
    
    try {
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
        };
        
        let res = await axios(options);
        
        if (res.data['rightsStatus'].includes('已兑换') || res.data['rightsStatus'].includes('已领取')) {
            console.log(`已兑换 ${userinfo.phoneNbr} ${level}`);
            return true;
        } else {
            console.log(`可兑换 ${userinfo.phoneNbr} ${level}`);
            runNumber++;
            return false;
        }
    } catch (e) {
        console.error(`检查权益状态失败 ${userinfo.phoneNbr}:`, e.message);
        return true; // 出错时视为已兑换，避免重复尝试
    }
}

/**
 * 兑换权益
 * @param {Object} userinfo - 用户信息
 * @param {Object} signData - 签名数据
 * @param {Object} receive - 权益信息
 * @param {number} number - 当前尝试次数
 * @param {number} startTime - 开始时间戳
 */
async function getConversionRights(userinfo, signData, receive, number = 1, startTime = Date.now()) {
    if (number > MAX_RETRY) {
        console.log(`兑换失败 ${userinfo.phoneNbr}，已达最大重试次数`);
        runNumber--;
        return;
    }
    
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
        };
        
        let res = await axios(options);
        
        if (res.data.resoultCode == '0') {
            let costTime = (Date.now() - startTime) / 1000;
            console.log(`兑换成功 ${userinfo.phoneNbr}，耗时 ${costTime}秒`);
            
            // 发送通知
            let notifyText = `电信权益兑换成功`;
            let notifyDesp = `账号: ${userinfo.phoneNbr}\n等级: ${receive.level}\n权益: ${receive.righstName}\n耗时: ${costTime}秒`;
            await sendNotify(notifyText, notifyDesp);
            
            runNumber--;
        } else if (res.data.resoultCode == '1') {
            console.log(`兑换中 ${userinfo.phoneNbr}，第 ${number} 次重试`);
            setTimeout(() => getConversionRights(userinfo, signData, receive, number + 1, startTime), 1500);
        } else if (res.data.resoultMsg == '您当前金豆数不足~') {
            console.log(`兑换失败 ${userinfo.phoneNbr}，金豆不足`);
            runNumber--;
        } else if (res.data.resoultMsg == '权益已兑换~') {
            console.log(`兑换失败 ${userinfo.phoneNbr}，权益已兑换`);
            runNumber--;
        } else {
            console.log(`兑换异常 ${userinfo.phoneNbr}: ${res.data.resoultMsg}，第 ${number} 次重试`);
            setTimeout(() => getConversionRights(userinfo, signData, receive, number + 1, startTime), 1500);
        }
    } catch (err) {
        console.error(`兑换出错 ${userinfo.phoneNbr}:`, err.message);
        setTimeout(() => getConversionRights(userinfo, signData, receive, number + 1, startTime), 2000);
    }
}

/**
 * 主流程函数
 * @param {string} phone - 手机号
 * @param {string} password - 密码
 */
async function main(phone, password) {
    try {
        let userInfo = await loginPhone(phone, password);
        if (!userInfo) return;
        
        let signData = await ssoHomLogin(userInfo.uid);
        await getLevelRightsList(userInfo, signData);
    } catch (e) {
        console.error(`主流程出错 ${phone}:`, e.message);
    }
}

/**
 * 初始化并启动所有账号
 */
async function getUser() {
    try {
        // 读取缓存
        Cache = JSON.parse(fs.readFileSync('./Cache.json', 'utf8'));
    } catch (error) {
        fs.writeFileSync('./Cache.json', JSON.stringify({}), 'utf8');
        Cache = JSON.parse(fs.readFileSync('./Cache.json', 'utf8'));
    }
    
    console.log('开始处理账号，总数:', userPhone.length);
    
    // 初始化cookie
    cookies = await getCookie.initCookie('https://wapact.189.cn:9001/gateway/standExchange/detailNew/exchange');
    
    // 并发登录所有账号
    let loginPromises = userPhone.map(item => main(item.phone, item.password));
    await Promise.all(loginPromises);
    
    console.log('所有账号登录完成，等待定时兑换');
}

/**
 * 执行兑换任务
 */
async function runExchange() {
    console.log('开始执行兑换任务，待兑换数量:', runArr.length);
    
    // 并发执行兑换，控制最大并发数
    let concurrentTasks = [];
    for (let i = 0; i < Math.min(MAX_CONCURRENT, runArr.length); i++) {
        let task = runArr[i];
        concurrentTasks.push(
            getConversionRights(task.userinfo, task.signData, task.item, 1, Date.now())
        );
    }
    
    await Promise.all(concurrentTasks);
    console.log('兑换任务执行完成');
}

/**
 * 获取当前时间
 * @returns {Object} 包含小时和分钟的对象
 */
function getCurrentTime() {
    const now = new Date();
    return {
        hour: now.getHours(),
        minute: now.getMinutes(),
        seconds: now.getSeconds(),
        milliseconds: now.getMilliseconds()
    };
}

/**
 * 判断是否是23点59分59秒500毫秒
 * @returns {boolean} 是否到达目标时间
 */
function isTargetTime() {
    const { hour, minute, seconds, milliseconds } = getCurrentTime();
    return hour === 23 && minute === 59 && seconds === 59 && milliseconds >= 500;
}

/**
 * 等待到指定时间执行兑换
 */
function waitForSpecificTime() {
    const now = new Date();
    const targetTime = new Date(
        now.getFullYear(),
        now.getMonth(),
        now.getDate(),
        23, // 小时
        59, // 分钟
        59, // 秒
        500 // 毫秒
    );
    
    // 如果现在已经过了目标时间，设置为明天的同一时间
    if (now >= targetTime) {
        targetTime.setDate(targetTime.getDate() + 1);
    }
    
    const timeDifference = targetTime - now;
    console.log(`等待 ${timeDifference} 毫秒后执行兑换`);
    
    setTimeout(async () => {
        console.log('到达目标时间，开始执行兑换');
        await runExchange();
        
        // 兑换完成后关闭定时器
        clearInterval(dayTimer);
    }, timeDifference);
}

// 启动程序
getUser();

// 设置每天检查时间的定时器
let dayTimer = setInterval(() => {
    if (isTargetTime()) {
        console.log('到达目标时间，准备执行兑换');
        runExchange();
    }
}, 1000);

// 等待到精确时间执行兑换
waitForSpecificTime();

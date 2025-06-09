/**
 * cron "8 8,14,22 * * *" yyck.js
 * 环境变量yyck="账号1#密码1#支付宝姓名1#支付宝账号1#设备id 多号换行便可
 本版本为MK集团版本去除了内置接口
 因为wxtoken的限制一个白ID可支持10个号,主号的DVID每三天需要打开一次APP激活因为没内置接口
 第二我们提供了半自动过验证网站本脚本会自动在脚本目录输出一个甬派.json文件导出此文件内容去网站导入便可半自动化过抽奖的验证
 每天运行脚本前先导入JSON文件去网站手动过抽奖验证然后再运行本脚本便可
 运行本脚本之前请先申请闲趣代理IP第137行就是写脚本代理IP的。
 MK集团甬音自助过验证官方站点http://dl.jdmk.xyz:1688
 */
const fs = require('fs');
const path = require('path');
const filePath = path.join(__dirname, '甬派.json');
const $ = new Env('꧁༺ 甬音༒抽奖 ༻꧂')
const { HttpsProxyAgent } = require('https-proxy-agent');// 如果是 HTTPS 代理
const axios = require('axios');
const yyck = ($.isNode() ? process.env.yyck : $.getdata("yyck")) || '';
window = {}
let deviceId = '';
let token = '';
let lotteryCookie = '';
let lotteryId = '';
let phone = '';
let password = '';
let realname = '';
let aliPay = '';
let userId = '';
let consumerId = '';
let name = '';
let model = '';
let notice = '';
let proxies = '';
let proxiesip = '';

!(async () => {
    await main();
})().catch((e) => {$.log(e)}).finally(() => {$.done({});});

async function main() {
    if (!yyck) {
        console.log("⭕环境变量获取失败")
        await sendMsg('⭕环境变量获取失败');
        return
    }
    let arr = yyck.split("\n");
    let countzh = 1;
    for (const item of arr) {
        console.log(`\n----------- 🍺账号【${countzh}/${arr.length}】执行🍺 -----------`)
        countzh = countzh+1;
        phone = item.split("#")[0]
        password = item.split("#")[1]
        realname = item.split("#")[2]
        aliPay = item.split("#")[3]
        deviceId = item.split("#")[4]
        let randomDevice = generateRandomDevice();
        if (!deviceId) {
            console.log("☁️随机生成deviceId")
            deviceId = randomDevice.deviceId;
        }
        model = randomDevice.model;
        console.log(`📱：${phone.substring(0, 3)}*****${phone.substring(8, 11)}`)
        let time = Date.now();
        let loginPwd = await loginPwdGet(`username=${phone}&password=${encodeURI(password)}&deviceId=${deviceId}&globalDatetime=${time}&sign=${md5(`globalDatetime${time}username${phone}test_123456679890123456`).toUpperCase()}`);
        if (loginPwd.code != 0) {
            console.log(`⭕${loginPwd.message}`);
            continue;
        }
        userId = loginPwd.data.userId;
        fs.readFile(filePath, 'utf8', (err, data) => {
            if (err) {
                // 文件不存在时创建新文件
                if (err.code === 'ENOENT') {
                    const newData = [userId];
                    fs.writeFile(filePath, JSON.stringify(newData, null, 2), (err) => {
                        if (err) throw err;
                        console.log(`${userId}：写入成功`)
                    });
                } else {
                    throw err;
                }
            } else {
                // 文件存在时处理
                try {
                    const jsonData = JSON.parse(data);
                    
                    if (!Array.isArray(jsonData)) {
                        throw new Error('JSON文件内容不是数组格式！');
                    }
                    // 关键去重逻辑：只有用户不存在时才追加
                    if (!jsonData.includes(userId)) {
                        jsonData.push(userId);
                        fs.writeFile(filePath, JSON.stringify(jsonData, null, 2), (err) => {
                            if (err) throw err;
                            console.log(`${userId}：写入成功`);
                        });
                    } else {
                        //console.log('用户已存在，无需重复添加');
                    }
                } catch (parseErr) {
                    console.error('SON解析失败:', parseErr);
                }
            }
        });
        let queryToken = loginPwd.data.token;
        name = loginPwd.data.nickname;
        let login = await loginGet(`userId=${userId}&loginName=${phone}&name=${encodeURI(name)}&phone=${phone}`);
        if (login.code != 200) {
            console.log(`⭕${login.message}`);
            continue;
        }
        token = login.data;
        //抽红包区块
        console.log("------- 甬 音 -------")
        let yongyintime = await yongyintimePost(`${Date.now()}`,3800000);
        if (yongyintime.message) {
            //console.log(`☁️时长提交：${yongyintime.message}`)
            let yongyingetime= await yongyintimeGet(`${Date.now()}`);
            console.log(`☁️刷新时长：${yongyingetime.message}`)
            }else {
                console.log(`⭕时长提交：失败`)
            }
        let yongyinhongbao = await yongyinhongbaoGet(`/yppage-share2/js/Yongyin_hongbao.js`);
        const regex = /id=(\d+)&/g;
        const matches = [];
        let match;
        while ((match = regex.exec(yongyinhongbao))!== null) {
            matches.push(match[1]);
            }
        for (const item of matches) {
            lotteryId = item;
            let lotteryLogin = await lotteryLoginGet(`userId=${userId}&dbredirect=https://92722.activity-12.m.duiba.com.cn/hdtool/index?id=${lotteryId}&dbnewopen`);
            lotteryCookie = ''
            lotteryCookie = await lotteryCookieGet(lotteryLogin.data);
            let key = await keyGet(`https://92722.activity-12.m.duiba.com.cn/hdtool/index?id=${lotteryId}&dbnewopen&from=login&spm=92722.1.1.1`)
            for (let count = 0; count < 5; count++) {
                proxiesip = (await axios.get("输入代理")).data;
                proxies = `http://${proxiesip}`
                console.log(proxiesip)
                lottery = await lotteryPost(`/hdtool/ajaxElement?_=${Date.now()}`,`hdType=dev&hdToolId=&preview=false&actId=${lotteryId}&adslotId=`)
                if (lottery == false) {
                    console.log(`☁️代理异常：重试`)
                    //await $.wait(2000)
                    continue
                }else{
                    break
                }
            }
            if (lottery == false) {
                console.log(`☁️代理异常：跳过当次抽奖`)
                continue
            }
            lotteryCount = lottery.element.freeLimit;
            if (lotteryCount == 0) {
                console.log(`☁️抽奖次数：${lotteryCount}次`)
                }
            for (let i = 0; i < lottery.element.freeLimit; i++) {
                let getTokenNew = await lotteryPost(`/hdtool/ctoken/getTokenNew`,`timestamp=${Date.now()}&activityId=${lotteryId}&activityType=hdtool&consumerId=${consumerId}`)
                eval(getTokenNew.token);
                let token = window[key];
                let lottery = await lotteryPost(`/hdtool/doJoin?dpm=92722.3.1.0&activityId=${lotteryId}&_=${Date.now()}`,`actId=${lotteryId}&oaId=${lotteryId}&activityType=hdtool&consumerId=${consumerId}&token=${token}`)
                if (lottery.success) {
                    if (!lottery.orderId) {
                        console.log(`⭕orderId获取失败：${lottery.message}`)
                        break
                    }
                    let orderId = lottery.orderId;
                    let result = 0;
                    while (result == 0) {
                        let getOrderStatus = await lotteryPost(`/hdtool/getOrderStatus?_=${Date.now()}`,`orderId=${orderId}&adslotId=`)
                        result = getOrderStatus.result;
                        if (result == 0) {
                            //console.log(`☁️抽奖结果：${getOrderStatus.message}`)
                        } else {
						    try {
                                const type = getOrderStatus.lottery.type;
                            } catch (error) {
                                console.error('捕捉到异常:', error.message);
                                break
                            }
                            if (getOrderStatus.lottery.type == 'thanks') {
                                console.log(`⭕抽奖结果：谢谢参与`)
                            }
                            if (getOrderStatus.lottery.type == 'alipay') {
                                console.log(`🌈抽奖结果：${getOrderStatus.lottery.title}`) //红包直接到支付宝
                                let url = getOrderStatus.lottery.link;
                                let urlStr = url.split('?')[1];
                                let result = {};
                                let paramsArr = urlStr.split('&')
                                for(let i = 0,len = paramsArr.length;i < len;i++){
                                    let arr = paramsArr[i].split('=')
                                    result[arr[0]] = arr[1];
                                }
                                let recordId = result.recordId;
                                if (realname && aliPay) {
                                    //console.log("☁️获取红包兑换key")
                                    key = await keyGet(`https://92722.activity-12.m.duiba.com.cn/activity/takePrizeNew?recordId=${recordId}&dbnewopen`)
                                    let getToken = await lotteryPost(`/ctoken/getToken.do`)
                                    eval(getToken.token);
                                    let token = window[key];
                                    let award = await lotteryPost(`/activity/doTakePrize`,`alipay=${aliPay}&realname=${encodeURI(realname)}&recordId=${recordId}&token=${token}`)
                                    console.log(`🌈开始领取：${award.message}`)
                                } else {
                                    console.log(`⭕支付宝姓名和账号未设置`)
                                }
                            }
                        }
                    }
                } else {
                    console.log(`⭕抽奖情况：${lottery.message}`)
                }
            }
        }
        console.log("----- 信 息 -----")
        let detail = await commonGet(`/yongpai-user/api/user/client?userId=${userId}&deviceId=${deviceId}&token=${queryToken}`)
        //console.log(`🍚当前积分：${detail.data.score}积分\n`)
        console.log(`🍚当前积分：${detail?.data?.score}积分\n`)
        notice += `用户：${phone} 积分：${detail.data.score}\n`
    }
    console.log('\n----------- 🎊 执 行  结 束 🎊 -----------')
    if (notice) {
        //await sendMsg(notice);
    }
}

async function loginPwdGet(url) {
    return new Promise(resolve => {
        const options = {
            url: `https://ypapp.cnnb.com.cn/yongpai-user/api/login2/local3?${url}`,
            headers : {
                'system': 'android',
                'version': '29',
                'model': "MI 8",
                'appversion': '11.2.0',
                'appbuild': '202501210',
                'deviceid': deviceId,
                'ticket': '',
                'accept-encoding': 'gzip',
                'user-agent': 'okhttp/4.9.1',
            }
        }
        $.get(options, async (err, resp, data) => {
            try {
                if (err) {
                    console.log(`${JSON.stringify(err)}`)
                    console.log(`${$.name} API请求失败，请检查网路重试`)
                } else {
                    //await $.wait(1000)
                    resolve(JSON.parse(data));
                }
            } catch (e) {
                $.logErr(e, resp)
            } finally {
                resolve();
            }
        })
    })
}

async function loginGet(url) {
    return new Promise(resolve => {
        const options = {
            url: `https://ypapp.cnnb.com.cn/web-nbcc/member/login?${url}`,
            headers : {
                'content-type': 'application/json',
                'module': 'web-member',
                'sign': md5(`/member/login{loginName:${phone},name:${name},phone:${phone},userId:${userId}`),
                'accept-encoding': 'gzip',
                'user-agent': 'okhttp/4.9.1',
            }
        }
        $.get(options, async (err, resp, data) => {
            try {
                if (err) {
                    console.log(`${JSON.stringify(err)}`)
                    console.log(`${$.name} API请求失败，请检查网路重试`)
                } else {
                    //await $.wait(1000)
                    resolve(JSON.parse(data));
                }
            } catch (e) {
                $.logErr(e, resp)
            } finally {
                resolve();
            }
        })
    })
}

async function commonGet(url) {
    return new Promise(resolve => {
        const options = {
            url: `https://ypapp.cnnb.com.cn${url}`,
            headers : {
                'system': 'android',
                'version': '29',
                'model': "MI 8",
                'appversion': '11.2.0',
                'appbuild': '202501210',
                'deviceid': deviceId,
                'ticket': token,
                'accept-encoding': 'gzip',
                'user-agent': 'okhttp/4.9.1',
            }
        }
        $.get(options, async (err, resp, data) => {
            try {
                if (err) {
                    console.log(`${JSON.stringify(err)}`)
                    console.log(`${$.name} API请求失败，请检查网路重试`)
                } else {
                    //await $.wait(1000)
                    resolve(JSON.parse(data));
                }
            } catch (e) {
                $.logErr(e, resp)
            } finally {
                resolve();
            }
        })
    })
}

async function dl() {
    try {
            let ip = (await axios.get("http://api.xiequ.cn/VAD/GetIp.aspx?act=get&uid=141694&vkey=DD7CB4081B16905588B3C9E74CF71DDF&num=1&time=30&plat=1&re=0&type=0&so=1&ow=1&spl=1&addr=浙江&db=1")).data;
            console.log(ip)

            let tmp = ip.split(":");
            let proxy = {
                protocol: 'http',
                host: tmp[0],
                port: tmp[1]
            }
            let res = (await axios.post(url, data, { headers, proxy })).data;
            this.sessionId = res.data.sessionId
        } catch (error) {
            console.log(url,error.message)
            return this.login(--i);
        }
}


async function yongyintimeGet(time) {
    return new Promise(resolve => {
        const options = {
            url: `https://ypapp.cnnb.com.cn/yongpai-user/api/duiba/hear/duration?userId=${userId}&time=${time}`,
            headers: {
                'accept': 'application/json,application/plain,*/*',
                'user-agent': 'Mozilla\/5\.0 \(Linux\; Android 10\; MI 8 Build\/QKQ1\.190828\.002\; wv\) AppleWebKit\/537\.36 \(KHTML\, like Gecko\) Version\/4\.0 Chrome\/83\.0\.4103\.101 Mobile Safari\/537\.36 agentweb\/4\.0\.2  UCBrowser\/11\.6\.4\.950 yongpai',
                'content-type': 'application/json; charset=utf-8',
                'x-requested-with': 'io.dcloud.H55BDF6BE',
                'sec-fetch-site': 'same-site',
                'sec-fetch-mode': 'cros',
                'sec-fetch-dest': 'empty',
                'accept-encoding': 'gzip, deflate',
                'accept-language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            }
        }
        $.get(options, async (err, resp, data) => {
            try {
                if (err) {
                    console.log(`${JSON.stringify(err)}`)
                    console.log(`${$.name} API请求失败，请检查网路重试`)
                } else {
                    //await $.wait(1000)
                    //resolve(JSON.stringify(data)); //转字符串格式
                    resolve(JSON.parse(data)); //转json格式
                }
            } catch (e) {
                $.logErr(e, resp)
            } finally {
                resolve();
            }
        })
    })
}

async function yongyintimePost(time,needtime) {
    return new Promise(resolve => {
        const options = {
            url: `https://ypapp.cnnb.com.cn/yongpai-user/api/duiba/hear`,
            headers : {
                'content-type': 'application/json; charset=utf-8',
                'accept-encoding': 'gzip',
                'user-agent': 'okhttp/4.9.1',
            },
            body: JSON.stringify({
                'userId':userId,
                'timestamp':time,
                'sign':md5(`duration${needtime}timestamp${time}userId${userId}hear1236..!#85862,==OHBICYVuyBikl-=!@#*()+_`),
                'duration': needtime,
            })
        }
        //console.log(options)
        $.post(options, async (err, resp, data) => {
            try {
                if (err) {
                    console.log(`${JSON.stringify(err)}`)
                    console.log(`${$.name} API请求失败，请检查网路重试`)
                } else {
                    //await $.wait(1000)
                    //resolve(JSON.stringify(data)); //转字符串格式
                    resolve(JSON.parse(data)); //转json格式
                }
            } catch (e) {
                $.logErr(e, resp)
            } finally {
                resolve();
            }
        })
    })
}

async function yongyinhongbaoGet(url) {
    return new Promise(resolve => {
        const options = {
            url: `https://ypstatic.cnnb.com.cn/${url}`,
            headers : {
                'Host': 'ypstatic.cnnb.com.cn',
                'user-agent': 'Mozilla/5.0 (Linux; Android 10; MI 8 Build/QKQ1.190828.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/83.0.4103.101 Mobile Safari/537.36 agentweb/4.0.2  UCBrowser/11.6.4.950 yongpai',
                'accept': '*/*',
                'x-requested-with': 'io.dcloud.H55BDF6BE',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-mode': 'no-cors',
                'sec-fetch-dest': 'script',
                'accept-encoding': 'gzip, deflate',
                'accept-language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            },
        }
        $.get(options, async (err, resp, data) => {
            try {
                if (err) {
                    console.log(`${JSON.stringify(err)}`)
                    console.log(`${$.name} API请求失败，请检查网路重试`)
                } else {
                    //await $.wait(1000)
                    resolve(data);
                }
            } catch (e) {
                $.logErr(e, resp)
            } finally {
                resolve();
            }
        })
    })
}

async function lotteryLoginGet(url) {
    return new Promise(resolve => {
        const options = {
            url: `https://ypapp.cnnb.com.cn/yongpai-user/api/duiba/autologin?${url}`,
            headers : {
                'accept-encoding': 'gzip',
                'user-agent': 'okhttp/4.9.1',
            }
        }
        $.get(options, async (err, resp, data) => {
            try {
                if (err) {
                    console.log(`${JSON.stringify(err)}`)
                    console.log(`${$.name} API请求失败，请检查网路重试`)
                } else {
                    //await $.wait(1000)
                    resolve(JSON.parse(data));
                }
            } catch (e) {
                $.logErr(e, resp)
            } finally {
                resolve();
            }
        })
    })
}


async function lotteryCookieGet(url) {
    return new Promise(resolve => {
        const options = {
            url: `${url}`,
            headers : {
                'upgrade-insecure-requests': '1',
                'user-agent': 'Mozilla/5.0 (Linux; Android 10; MI 8 Build/QKQ1.190828.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/83.0.4103.101 Mobile Safari/537.36 agentweb/4.0.2  UCBrowser/11.6.4.950 yongpai',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'x-requested-with': 'io.dcloud.H55BDF6BE',
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-encoding': 'gzip, deflate',
                'accept-language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            },
            followRedirect: false
        }
        $.get(options, async (err, resp, data) => {
            try {
                if (err) {
                    console.log(`${JSON.stringify(err)}`)
                    console.log(`${$.name} API请求失败，请检查网路重试`)
                } else {
                    //await $.wait(1000)
                    if ($.isNode()) {
                        let cookieArr = resp.headers['set-cookie'] || resp.headers['Set-Cookie'];
                        for (let i = 0; i < cookieArr.length; i++) {
                            lotteryCookie += cookieArr[i].split(';')[0] + ';'
                        }
                    } else {
                        lotteryCookie = resp.headers['set-cookie'] || resp.headers['Set-Cookie'];
                        lotteryCookie = formatCookies(lotteryCookie);
                    }
                    resolve(lotteryCookie);
                }
            } catch (e) {
                $.logErr(e, resp)
            } finally {
                resolve();
            }
        })
    })
}


async function lotteryPost(url, body) {
    try {
        const agent = new HttpsProxyAgent(proxies);
        const response = await axios.post(`https://92722.activity-12.m.duiba.com.cn${url}`, body, {
            httpsAgent: agent,
            headers: {
                'accept': 'application/json',
                'user-agent': 'Mozilla/5.0 (Linux; Android 10; MI 8 Build/QKQ1.190828.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/83.0.4103.101 Mobile Safari/537.36 agentweb/4.0.2  UCBrowser/11.6.4.950 yongpai',
                'x-requested-with': 'XMLHttpRequest',
                'content-type': 'application/x-www-form-urlencoded',
                'origin': 'https://92722.activity-12.m.duiba.com.cn',
                'cookie': lotteryCookie,
                'sec-fetch-site': 'same-origin',
                'sec-fetch-mode': 'cors',
                'sec-fetch-dest': 'empty',
                'referer': `https://92722.activity-12.m.duiba.com.cn/hdtool/index?id=${lotteryId}&dbnewopen&from=login&spm=92722.1.1.1`,
                'accept-encoding': 'gzip, deflate',
                'accept-language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            },
        });
        return response.data;
    } catch (error) {
        //console.error('API请求失败:', error);
        //throw error;
        return false;
    }
}

async function keyGet(url) {
    return new Promise(resolve => {
        const options = {
            url: url,
            headers: {
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'upgrade-insecure-requests': '1',
                'user-agent': 'Mozilla\/5\.0 \(Linux\; Android 10\; MI 8 Build\/QKQ1\.190828\.002\; wv\) AppleWebKit\/537\.36 \(KHTML\, like Gecko\) Version\/4\.0 Chrome\/83\.0\.4103\.101 Mobile Safari\/537\.36 agentweb\/4\.0\.2  UCBrowser\/11\.6\.4\.950 yongpai',
                'x-requested-with': 'io.dcloud.H55BDF6BE',
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-encoding': 'gzip, deflate',
                'accept-language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
                'cookie': lotteryCookie
            }
        }
        $.get(options, async (err, resp, data) => {
            try {
                if (err) {
                    console.log(`${JSON.stringify(err)}`)
                    console.log(`${$.name} API请求失败，请检查网路重试`)
                } else {
                    //await $.wait(1000)
                    let code = /<script type\b[^>]*>\s*var([\s\S]*?)<\/script>/.exec(data)[1];
                    eval(code)
                    let key = /var\s+key\s+=\s+'([^']+)';/.exec(getDuibaToken.toString())[1];
                    //console.log(key)
                    //console.log('获取consumerId')
                    const regex = /consumerId:'(\d+)'/;
                    const match = data.match(regex);
                    if (match) {
                        consumerId = match[1];
                    } else {
                        consumerId = '4136126583'
                    }
                    //console.log(consumerId)
                    resolve(key);
                }
            } catch (e) {
                $.logErr(e, resp)
            } finally {
                resolve();
            }
        })
    })
}

function formatCookies(cookieString) {
    const cookies = cookieString.split(', ');
    const formattedCookies = cookies.map(cookie => {
        const keyValue = cookie.split(';')[0];
        return keyValue.trim();
    });
    return formattedCookies.join(';');
}

function generateRandomDevice() {
    const deviceId = generateDeviceId();
    const models = [
        "M1903F2A",
        "M2001J2E",
        "M2001J2C",
        "M2001J1E",
        "M2001J1C",
        "M2002J9E",
        "M2011K2C",
        "M2102K1C",
        "M2101K9C",
        "2107119DC",
        "2201123C",
        "2112123AC",
        "2201122C",
        "2211133C",
        "2210132C",
        "2304FPN6DC",
        "23127PN0CC",
        "24031PN0DC",
        "23090RA98C",
        "2312DRA50C",
        "2312CRAD3C",
        "2312DRAABC",
        "22101316UCP",
        "22101316C"
    ];
    const model = getRandomElement(models);
    return {"deviceId": deviceId, "model": model}
}

function getRandomElement(arr) {
    return arr[Math.floor(Math.random() * arr.length)];
}

function generateDeviceId(length = 16) {
    const characters = 'abcdefghijklmnopqrstuvwxyz0123456789';
    let deviceId = '';
    for (let i = 0; i < length; i++) {
        deviceId += characters.charAt(Math.floor(Math.random() * characters.length));
    }
    return deviceId;
}

function isToday(dateString) {
    const inputDate = new Date(dateString);
    const today = new Date();

    return inputDate.getFullYear() === today.getFullYear() &&
        inputDate.getMonth() === today.getMonth() &&
        inputDate.getDate() === today.getDate();
}

/*
async function sendMsg(message) {
    if ($.isNode()) {
        let notify = ''
        try {
            notify = require('./sendNotify');
        } catch (e) {
            notify = require("../sendNotify");
        }
        await notify.sendNotify($.name, message);
    } else {
        $.msg($.name, '', message)
    }
}*/

function md5(r){return rstr2hex(rstr_md5(str2rstr_utf8(r)))}function b64_md5(r){return rstr2b64(rstr_md5(str2rstr_utf8(r)))}function any_md5(r,t){return rstr2any(rstr_md5(str2rstr_utf8(r)),t)}function hex_hmac_md5(r,t){return rstr2hex(rstr_hmac_md5(str2rstr_utf8(r),str2rstr_utf8(t)))}function b64_hmac_md5(r,t){return rstr2b64(rstr_hmac_md5(str2rstr_utf8(r),str2rstr_utf8(t)))}function any_hmac_md5(r,t,d){return rstr2any(rstr_hmac_md5(str2rstr_utf8(r),str2rstr_utf8(t)),d)}function md5_vm_test(){return"900150983cd24fb0d6963f7d28e17f72"==hex_md5("abc").toLowerCase()}function rstr_md5(r){return binl2rstr(binl_md5(rstr2binl(r),8*r.length))}function rstr_hmac_md5(r,t){var d=rstr2binl(r);d.length>16&&(d=binl_md5(d,8*r.length));for(var n=Array(16),_=Array(16),m=0;m<16;m++)n[m]=909522486^d[m],_[m]=1549556828^d[m];var f=binl_md5(n.concat(rstr2binl(t)),512+8*t.length);return binl2rstr(binl_md5(_.concat(f),640))}function rstr2hex(r){for(var t,d=hexcase?"0123456789ABCDEF":"0123456789abcdef",n="",_=0;_<r.length;_++)t=r.charCodeAt(_),n+=d.charAt(t>>>4&15)+d.charAt(15&t);return n}function rstr2b64(r){for(var t="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/",d="",n=r.length,_=0;_<n;_+=3)for(var m=r.charCodeAt(_)<<16|(_+1<n?r.charCodeAt(_+1)<<8:0)|(_+2<n?r.charCodeAt(_+2):0),f=0;f<4;f++)8*_+6*f>8*r.length?d+=b64pad:d+=t.charAt(m>>>6*(3-f)&63);return d}function rstr2any(r,t){var d,n,_,m,f,h=t.length,e=Array(Math.ceil(r.length/2));for(d=0;d<e.length;d++)e[d]=r.charCodeAt(2*d)<<8|r.charCodeAt(2*d+1);var a=Math.ceil(8*r.length/(Math.log(t.length)/Math.log(2))),i=Array(a);for(n=0;n<a;n++){for(f=Array(),m=0,d=0;d<e.length;d++)m=(m<<16)+e[d],_=Math.floor(m/h),m-=_*h,(f.length>0||_>0)&&(f[f.length]=_);i[n]=m,e=f}var o="";for(d=i.length-1;d>=0;d--)o+=t.charAt(i[d]);return o}function str2rstr_utf8(r){for(var t,d,n="",_=-1;++_<r.length;)t=r.charCodeAt(_),d=_+1<r.length?r.charCodeAt(_+1):0,55296<=t&&t<=56319&&56320<=d&&d<=57343&&(t=65536+((1023&t)<<10)+(1023&d),_++),t<=127?n+=String.fromCharCode(t):t<=2047?n+=String.fromCharCode(192|t>>>6&31,128|63&t):t<=65535?n+=String.fromCharCode(224|t>>>12&15,128|t>>>6&63,128|63&t):t<=2097151&&(n+=String.fromCharCode(240|t>>>18&7,128|t>>>12&63,128|t>>>6&63,128|63&t));return n}function str2rstr_utf16le(r){for(var t="",d=0;d<r.length;d++)t+=String.fromCharCode(255&r.charCodeAt(d),r.charCodeAt(d)>>>8&255);return t}function str2rstr_utf16be(r){for(var t="",d=0;d<r.length;d++)t+=String.fromCharCode(r.charCodeAt(d)>>>8&255,255&r.charCodeAt(d));return t}function rstr2binl(r){for(var t=Array(r.length>>2),d=0;d<t.length;d++)t[d]=0;for(d=0;d<8*r.length;d+=8)t[d>>5]|=(255&r.charCodeAt(d/8))<<d%32;return t}function binl2rstr(r){for(var t="",d=0;d<32*r.length;d+=8)t+=String.fromCharCode(r[d>>5]>>>d%32&255);return t}function binl_md5(r,t){r[t>>5]|=128<<t%32,r[14+(t+64>>>9<<4)]=t;for(var d=1732584193,n=-271733879,_=-1732584194,m=271733878,f=0;f<r.length;f+=16){var h=d,e=n,a=_,i=m;d=md5_ff(d,n,_,m,r[f+0],7,-680876936),m=md5_ff(m,d,n,_,r[f+1],12,-389564586),_=md5_ff(_,m,d,n,r[f+2],17,606105819),n=md5_ff(n,_,m,d,r[f+3],22,-1044525330),d=md5_ff(d,n,_,m,r[f+4],7,-176418897),m=md5_ff(m,d,n,_,r[f+5],12,1200080426),_=md5_ff(_,m,d,n,r[f+6],17,-1473231341),n=md5_ff(n,_,m,d,r[f+7],22,-45705983),d=md5_ff(d,n,_,m,r[f+8],7,1770035416),m=md5_ff(m,d,n,_,r[f+9],12,-1958414417),_=md5_ff(_,m,d,n,r[f+10],17,-42063),n=md5_ff(n,_,m,d,r[f+11],22,-1990404162),d=md5_ff(d,n,_,m,r[f+12],7,1804603682),m=md5_ff(m,d,n,_,r[f+13],12,-40341101),_=md5_ff(_,m,d,n,r[f+14],17,-1502002290),n=md5_ff(n,_,m,d,r[f+15],22,1236535329),d=md5_gg(d,n,_,m,r[f+1],5,-165796510),m=md5_gg(m,d,n,_,r[f+6],9,-1069501632),_=md5_gg(_,m,d,n,r[f+11],14,643717713),n=md5_gg(n,_,m,d,r[f+0],20,-373897302),d=md5_gg(d,n,_,m,r[f+5],5,-701558691),m=md5_gg(m,d,n,_,r[f+10],9,38016083),_=md5_gg(_,m,d,n,r[f+15],14,-660478335),n=md5_gg(n,_,m,d,r[f+4],20,-405537848),d=md5_gg(d,n,_,m,r[f+9],5,568446438),m=md5_gg(m,d,n,_,r[f+14],9,-1019803690),_=md5_gg(_,m,d,n,r[f+3],14,-187363961),n=md5_gg(n,_,m,d,r[f+8],20,1163531501),d=md5_gg(d,n,_,m,r[f+13],5,-1444681467),m=md5_gg(m,d,n,_,r[f+2],9,-51403784),_=md5_gg(_,m,d,n,r[f+7],14,1735328473),n=md5_gg(n,_,m,d,r[f+12],20,-1926607734),d=md5_hh(d,n,_,m,r[f+5],4,-378558),m=md5_hh(m,d,n,_,r[f+8],11,-2022574463),_=md5_hh(_,m,d,n,r[f+11],16,1839030562),n=md5_hh(n,_,m,d,r[f+14],23,-35309556),d=md5_hh(d,n,_,m,r[f+1],4,-1530992060),m=md5_hh(m,d,n,_,r[f+4],11,1272893353),_=md5_hh(_,m,d,n,r[f+7],16,-155497632),n=md5_hh(n,_,m,d,r[f+10],23,-1094730640),d=md5_hh(d,n,_,m,r[f+13],4,681279174),m=md5_hh(m,d,n,_,r[f+0],11,-358537222),_=md5_hh(_,m,d,n,r[f+3],16,-722521979),n=md5_hh(n,_,m,d,r[f+6],23,76029189),d=md5_hh(d,n,_,m,r[f+9],4,-640364487),m=md5_hh(m,d,n,_,r[f+12],11,-421815835),_=md5_hh(_,m,d,n,r[f+15],16,530742520),n=md5_hh(n,_,m,d,r[f+2],23,-995338651),d=md5_ii(d,n,_,m,r[f+0],6,-198630844),m=md5_ii(m,d,n,_,r[f+7],10,1126891415),_=md5_ii(_,m,d,n,r[f+14],15,-1416354905),n=md5_ii(n,_,m,d,r[f+5],21,-57434055),d=md5_ii(d,n,_,m,r[f+12],6,1700485571),m=md5_ii(m,d,n,_,r[f+3],10,-1894986606),_=md5_ii(_,m,d,n,r[f+10],15,-1051523),n=md5_ii(n,_,m,d,r[f+1],21,-2054922799),d=md5_ii(d,n,_,m,r[f+8],6,1873313359),m=md5_ii(m,d,n,_,r[f+15],10,-30611744),_=md5_ii(_,m,d,n,r[f+6],15,-1560198380),n=md5_ii(n,_,m,d,r[f+13],21,1309151649),d=md5_ii(d,n,_,m,r[f+4],6,-145523070),m=md5_ii(m,d,n,_,r[f+11],10,-1120210379),_=md5_ii(_,m,d,n,r[f+2],15,718787259),n=md5_ii(n,_,m,d,r[f+9],21,-343485551),d=safe_add(d,h),n=safe_add(n,e),_=safe_add(_,a),m=safe_add(m,i)}return Array(d,n,_,m)}function md5_cmn(r,t,d,n,_,m){return safe_add(bit_rol(safe_add(safe_add(t,r),safe_add(n,m)),_),d)}function md5_ff(r,t,d,n,_,m,f){return md5_cmn(t&d|~t&n,r,t,_,m,f)}function md5_gg(r,t,d,n,_,m,f){return md5_cmn(t&n|d&~n,r,t,_,m,f)}function md5_hh(r,t,d,n,_,m,f){return md5_cmn(t^d^n,r,t,_,m,f)}function md5_ii(r,t,d,n,_,m,f){return md5_cmn(d^(t|~n),r,t,_,m,f)}function safe_add(r,t){var d=(65535&r)+(65535&t),n=(r>>16)+(t>>16)+(d>>16);return n<<16|65535&d}function bit_rol(r,t){return r<<t|r>>>32-t}var hexcase=0,b64pad="";

// prettier-ignore
function Env(t,e){class s{constructor(t){this.env=t}send(t,e="GET"){t="string"==typeof t?{url:t}:t;let s=this.get;return"POST"===e&&(s=this.post),new Promise(((e,i)=>{s.call(this,t,((t,s,o)=>{t?i(t):e(s)}))}))}get(t){return this.send.call(this.env,t)}post(t){return this.send.call(this.env,t,"POST")}}return new class{constructor(t,e){this.logLevels={debug:0,info:1,warn:2,error:3},this.logLevelPrefixs={debug:"[DEBUG] ",info:"[INFO] ",warn:"[WARN] ",error:"[ERROR] "},this.logLevel="info",this.name=t,this.http=new s(this),this.data=null,this.dataFile="box.dat",this.logs=[],this.isMute=!1,this.isNeedRewrite=!1,this.logSeparator="\n",this.encoding="utf-8",this.startTime=(new Date).getTime(),Object.assign(this,e),this.log("",`${' '.repeat(10)}${this.name}\n`)}getEnv(){return"undefined"!=typeof $environment&&$environment["surge-version"]?"Surge":"undefined"!=typeof $environment&&$environment["stash-version"]?"Stash":"undefined"!=typeof module&&module.exports?"Node.js":"undefined"!=typeof $task?"Quantumult X":"undefined"!=typeof $loon?"Loon":"undefined"!=typeof $rocket?"Shadowrocket":void 0}isNode(){return"Node.js"===this.getEnv()}isQuanX(){return"Quantumult X"===this.getEnv()}isSurge(){return"Surge"===this.getEnv()}isLoon(){return"Loon"===this.getEnv()}isShadowrocket(){return"Shadowrocket"===this.getEnv()}isStash(){return"Stash"===this.getEnv()}toObj(t,e=null){try{return JSON.parse(t)}catch{return e}}toStr(t,e=null,...s){try{return JSON.stringify(t,...s)}catch{return e}}getjson(t,e){let s=e;if(this.getdata(t))try{s=JSON.parse(this.getdata(t))}catch{}return s}setjson(t,e){try{return this.setdata(JSON.stringify(t),e)}catch{return!1}}getScript(t){return new Promise((e=>{this.get({url:t},((t,s,i)=>e(i)))}))}runScript(t,e){return new Promise((s=>{let i=this.getdata("@chavy_boxjs_userCfgs.httpapi");i=i?i.replace(/\n/g,"").trim():i;let o=this.getdata("@chavy_boxjs_userCfgs.httpapi_timeout");o=o?1*o:20,o=e&&e.timeout?e.timeout:o;const[r,a]=i.split("@"),n={url:`http://${a}/v1/scripting/evaluate`,body:{script_text:t,mock_type:"cron",timeout:o},headers:{"X-Key":r,Accept:"*/*"},timeout:o};this.post(n,((t,e,i)=>s(i)))})).catch((t=>this.logErr(t)))}loaddata(){if(!this.isNode())return{};{this.fs=this.fs?this.fs:require("fs"),this.path=this.path?this.path:require("path");const t=this.path.resolve(this.dataFile),e=this.path.resolve(process.cwd(),this.dataFile),s=this.fs.existsSync(t),i=!s&&this.fs.existsSync(e);if(!s&&!i)return{};{const i=s?t:e;try{return JSON.parse(this.fs.readFileSync(i))}catch(t){return{}}}}}writedata(){if(this.isNode()){this.fs=this.fs?this.fs:require("fs"),this.path=this.path?this.path:require("path");const t=this.path.resolve(this.dataFile),e=this.path.resolve(process.cwd(),this.dataFile),s=this.fs.existsSync(t),i=!s&&this.fs.existsSync(e),o=JSON.stringify(this.data);s?this.fs.writeFileSync(t,o):i?this.fs.writeFileSync(e,o):this.fs.writeFileSync(t,o)}}lodash_get(t,e,s){const i=e.replace(/\[(\d+)\]/g,".$1").split(".");let o=t;for(const t of i)if(o=Object(o)[t],void 0===o)return s;return o}lodash_set(t,e,s){return Object(t)!==t||(Array.isArray(e)||(e=e.toString().match(/[^.[\]]+/g)||[]),e.slice(0,-1).reduce(((t,s,i)=>Object(t[s])===t[s]?t[s]:t[s]=Math.abs(e[i+1])>>0==+e[i+1]?[]:{}),t)[e[e.length-1]]=s),t}getdata(t){let e=this.getval(t);if(/^@/.test(t)){const[,s,i]=/^@(.*?)\.(.*?)$/.exec(t),o=s?this.getval(s):"";if(o)try{const t=JSON.parse(o);e=t?this.lodash_get(t,i,""):e}catch(t){e=""}}return e}setdata(t,e){let s=!1;if(/^@/.test(e)){const[,i,o]=/^@(.*?)\.(.*?)$/.exec(e),r=this.getval(i),a=i?"null"===r?null:r||"{}":"{}";try{const e=JSON.parse(a);this.lodash_set(e,o,t),s=this.setval(JSON.stringify(e),i)}catch(e){const r={};this.lodash_set(r,o,t),s=this.setval(JSON.stringify(r),i)}}else s=this.setval(t,e);return s}getval(t){switch(this.getEnv()){case"Surge":case"Loon":case"Stash":case"Shadowrocket":return $persistentStore.read(t);case"Quantumult X":return $prefs.valueForKey(t);case"Node.js":return this.data=this.loaddata(),this.data[t];default:return this.data&&this.data[t]||null}}setval(t,e){switch(this.getEnv()){case"Surge":case"Loon":case"Stash":case"Shadowrocket":return $persistentStore.write(t,e);case"Quantumult X":return $prefs.setValueForKey(t,e);case"Node.js":return this.data=this.loaddata(),this.data[e]=t,this.writedata(),!0;default:return this.data&&this.data[e]||null}}initGotEnv(t){this.got=this.got?this.got:require("got"),this.cktough=this.cktough?this.cktough:require("tough-cookie"),this.ckjar=this.ckjar?this.ckjar:new this.cktough.CookieJar,t&&(t.headers=t.headers?t.headers:{},t&&(t.headers=t.headers?t.headers:{},void 0===t.headers.cookie&&void 0===t.headers.Cookie&&void 0===t.cookieJar&&(t.cookieJar=this.ckjar)))}get(t,e=(()=>{})){switch(t.headers&&(delete t.headers["Content-Type"],delete t.headers["Content-Length"],delete t.headers["content-type"],delete t.headers["content-length"]),t.params&&(t.url+="?"+this.queryStr(t.params)),void 0===t.followRedirect||t.followRedirect||((this.isSurge()||this.isLoon())&&(t["auto-redirect"]=!1),this.isQuanX()&&(t.opts?t.opts.redirection=!1:t.opts={redirection:!1})),this.getEnv()){case"Surge":case"Loon":case"Stash":case"Shadowrocket":default:this.isSurge()&&this.isNeedRewrite&&(t.headers=t.headers||{},Object.assign(t.headers,{"X-Surge-Skip-Scripting":!1})),$httpClient.get(t,((t,s,i)=>{!t&&s&&(s.body=i,s.statusCode=s.status?s.status:s.statusCode,s.status=s.statusCode),e(t,s,i)}));break;case"Quantumult X":this.isNeedRewrite&&(t.opts=t.opts||{},Object.assign(t.opts,{hints:!1})),$task.fetch(t).then((t=>{const{statusCode:s,statusCode:i,headers:o,body:r,bodyBytes:a}=t;e(null,{status:s,statusCode:i,headers:o,body:r,bodyBytes:a},r,a)}),(t=>e(t&&t.error||"UndefinedError")));break;case"Node.js":let s=require("iconv-lite");this.initGotEnv(t),this.got(t).on("redirect",((t,e)=>{try{if(t.headers["set-cookie"]){const s=t.headers["set-cookie"].map(this.cktough.Cookie.parse).toString();s&&this.ckjar.setCookieSync(s,null),e.cookieJar=this.ckjar}}catch(t){this.logErr(t)}})).then((t=>{const{statusCode:i,statusCode:o,headers:r,rawBody:a}=t,n=s.decode(a,this.encoding);e(null,{status:i,statusCode:o,headers:r,rawBody:a,body:n},n)}),(t=>{const{message:i,response:o}=t;e(i,o,o&&s.decode(o.rawBody,this.encoding))}));break}}post(t,e=(()=>{})){const s=t.method?t.method.toLocaleLowerCase():"post";switch(t.body&&t.headers&&!t.headers["Content-Type"]&&!t.headers["content-type"]&&(t.headers["content-type"]="application/x-www-form-urlencoded"),t.headers&&(delete t.headers["Content-Length"],delete t.headers["content-length"]),void 0===t.followRedirect||t.followRedirect||((this.isSurge()||this.isLoon())&&(t["auto-redirect"]=!1),this.isQuanX()&&(t.opts?t.opts.redirection=!1:t.opts={redirection:!1})),this.getEnv()){case"Surge":case"Loon":case"Stash":case"Shadowrocket":default:this.isSurge()&&this.isNeedRewrite&&(t.headers=t.headers||{},Object.assign(t.headers,{"X-Surge-Skip-Scripting":!1})),$httpClient[s](t,((t,s,i)=>{!t&&s&&(s.body=i,s.statusCode=s.status?s.status:s.statusCode,s.status=s.statusCode),e(t,s,i)}));break;case"Quantumult X":t.method=s,this.isNeedRewrite&&(t.opts=t.opts||{},Object.assign(t.opts,{hints:!1})),$task.fetch(t).then((t=>{const{statusCode:s,statusCode:i,headers:o,body:r,bodyBytes:a}=t;e(null,{status:s,statusCode:i,headers:o,body:r,bodyBytes:a},r,a)}),(t=>e(t&&t.error||"UndefinedError")));break;case"Node.js":let i=require("iconv-lite");this.initGotEnv(t);const{url:o,...r}=t;this.got[s](o,r).then((t=>{const{statusCode:s,statusCode:o,headers:r,rawBody:a}=t,n=i.decode(a,this.encoding);e(null,{status:s,statusCode:o,headers:r,rawBody:a,body:n},n)}),(t=>{const{message:s,response:o}=t;e(s,o,o&&i.decode(o.rawBody,this.encoding))}));break}}time(t,e=null){const s=e?new Date(e):new Date;let i={"M+":s.getMonth()+1,"d+":s.getDate(),"H+":s.getHours(),"m+":s.getMinutes(),"s+":s.getSeconds(),"q+":Math.floor((s.getMonth()+3)/3),S:s.getMilliseconds()};/(y+)/.test(t)&&(t=t.replace(RegExp.$1,(s.getFullYear()+"").substr(4-RegExp.$1.length)));for(let e in i)new RegExp("("+e+")").test(t)&&(t=t.replace(RegExp.$1,1==RegExp.$1.length?i[e]:("00"+i[e]).substr((""+i[e]).length)));return t}queryStr(t){let e="";for(const s in t){let i=t[s];null!=i&&""!==i&&("object"==typeof i&&(i=JSON.stringify(i)),e+=`${s}=${i}&`)}return e=e.substring(0,e.length-1),e}msg(e=t,s="",i="",o={}){const r=t=>{const{$open:e,$copy:s,$media:i,$mediaMime:o}=t;switch(typeof t){case void 0:return t;case"string":switch(this.getEnv()){case"Surge":case"Stash":default:return{url:t};case"Loon":case"Shadowrocket":return t;case"Quantumult X":return{"open-url":t};case"Node.js":return}case"object":switch(this.getEnv()){case"Surge":case"Stash":case"Shadowrocket":default:{const r={};let a=t.openUrl||t.url||t["open-url"]||e;a&&Object.assign(r,{action:"open-url",url:a});let n=t["update-pasteboard"]||t.updatePasteboard||s;if(n&&Object.assign(r,{action:"clipboard",text:n}),i){let t,e,s;if(i.startsWith("http"))t=i;else if(i.startsWith("data:")){const[t]=i.split(";"),[,o]=i.split(",");e=o,s=t.replace("data:","")}else{e=i,s=(t=>{const e={JVBERi0:"application/pdf",R0lGODdh:"image/gif",R0lGODlh:"image/gif",iVBORw0KGgo:"image/png","/9j/":"image/jpg"};for(var s in e)if(0===t.indexOf(s))return e[s];return null})(i)}Object.assign(r,{"media-url":t,"media-base64":e,"media-base64-mime":o??s})}return Object.assign(r,{"auto-dismiss":t["auto-dismiss"],sound:t.sound}),r}case"Loon":{const s={};let o=t.openUrl||t.url||t["open-url"]||e;o&&Object.assign(s,{openUrl:o});let r=t.mediaUrl||t["media-url"];return i?.startsWith("http")&&(r=i),r&&Object.assign(s,{mediaUrl:r}),console.log(JSON.stringify(s)),s}case"Quantumult X":{const o={};let r=t["open-url"]||t.url||t.openUrl||e;r&&Object.assign(o,{"open-url":r});let a=t["media-url"]||t.mediaUrl;i?.startsWith("http")&&(a=i),a&&Object.assign(o,{"media-url":a});let n=t["update-pasteboard"]||t.updatePasteboard||s;return n&&Object.assign(o,{"update-pasteboard":n}),console.log(JSON.stringify(o)),o}case"Node.js":return}default:return}};if(!this.isMute)switch(this.getEnv()){case"Surge":case"Loon":case"Stash":case"Shadowrocket":default:$notification.post(e,s,i,r(o));break;case"Quantumult X":$notify(e,s,i,r(o));break;case"Node.js":break}if(!this.isMuteLog){let t=["","==============📣系统通知📣=============="];t.push(e),s&&t.push(s),i&&t.push(i),console.log(t.join("\n")),this.logs=this.logs.concat(t)}}debug(...t){this.logLevels[this.logLevel]<=this.logLevels.debug&&(t.length>0&&(this.logs=[...this.logs,...t]),console.log(`${this.logLevelPrefixs.debug}${t.map((t=>t??String(t))).join(this.logSeparator)}`))}info(...t){this.logLevels[this.logLevel]<=this.logLevels.info&&(t.length>0&&(this.logs=[...this.logs,...t]),console.log(`${this.logLevelPrefixs.info}${t.map((t=>t??String(t))).join(this.logSeparator)}`))}warn(...t){this.logLevels[this.logLevel]<=this.logLevels.warn&&(t.length>0&&(this.logs=[...this.logs,...t]),console.log(`${this.logLevelPrefixs.warn}${t.map((t=>t??String(t))).join(this.logSeparator)}`))}error(...t){this.logLevels[this.logLevel]<=this.logLevels.error&&(t.length>0&&(this.logs=[...this.logs,...t]),console.log(`${this.logLevelPrefixs.error}${t.map((t=>t??String(t))).join(this.logSeparator)}`))}log(...t){t.length>0&&(this.logs=[...this.logs,...t]),console.log(t.map((t=>t??String(t))).join(this.logSeparator))}logErr(t,e){switch(this.getEnv()){case"Surge":case"Loon":case"Stash":case"Shadowrocket":case"Quantumult X":default:this.log("",`❗️${this.name}, 错误!`,e,t);break;case"Node.js":this.log("",`❗️${this.name}, 错误!`,e,void 0!==t.message?t.message:t,t.stack);break}}wait(t){return new Promise((e=>setTimeout(e,t)))}done(t={}){const e=((new Date).getTime()-this.startTime)/1e3;switch(this.log("",``),this.log(),this.getEnv()){case"Surge":case"Loon":case"Stash":case"Shadowrocket":case"Quantumult X":default:$done(t);break;case"Node.js":process.exit(1)}}}(t,e)}
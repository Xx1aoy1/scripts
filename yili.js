**
 * cron "5 0,18 * * *" YiLi.js
 * export YiLi='[{"mobile": "1", "openId": "1", "unionId": "1", "nickName": "1", "avatarUrl": "1", "yiliToken":"1"},{"mobile": "2", "openId": "2", "unionId": "2", "nickName": "2", "avatarUrl": "2", "yiliToken":"2"}]'//yiliToken是域名msmarket.msx.digitalyili.com的access-token
 * export YiLi_Open='true'//翻牌
 */
const $ = new Env('伊利-国庆')


let YiLiblsz = 0;  // 控制 YiLi 格式    默认是0 原始格式    等于1 使用#拼接多账号回车


if (YiLiblsz === 0) {
    // 如果 YiLiblsz 为 0，
    YiLi = ($.isNode() ? JSON.parse(process.env.YiLi) : $.getjson("YiLi")) || [];
} else {
    // 如果 YiLiblsz 为 1，
    YiLi = ($.isNode() ? process.env.YiLi.split('\n').map(item => {
        let parts = item.split('#');
        return {
            mobile: parts[0],
            openId: parts[1],
            unionId: parts[2],
            nickName: parts[3],
            avatarUrl: parts[4],
            yiliToken: parts[5]
        };
    }) : $.getjson("YiLi")) || [];
}






const YiLi_Open = ($.isNode() ? process.env.YiLi_Open : $.getdata("YiLi_Open")) === 'true' || false;
let Utils = undefined;
let mobile = ''
let token = ''
let avatarUrl = ''
let nickName = ''
let yiliToken = ''
let openId = ''
let unionId = ''
let type = '2'
let type1 = '2'
// 以 # 分隔的多个口令，空白将被跳过  每天上限好像10次  稀有 QQ星 舒化  畅意100% 
//let YiLi_Code = '';

let YiLi_Code = '晏晓林邀您来伊利拿礼#陆桂英邀您来伊利拿礼';



//'翟芳邀您来伊利拿礼#韩海莉邀您来伊利拿礼#郝银爱邀您来伊利拿礼#王素红邀您来伊利拿礼#黄思梦邀您来伊利拿礼#朱梦婷邀您来伊利拿礼#曹彩花邀您来伊利拿礼#何维邀您来伊利拿礼#杨慧庆邀您来伊利拿礼';  // 09.26  9
//#廖艳邀您来伊利拿礼#文慧邀您来伊利拿礼#冉七邀您来伊利拿礼#韩桧君邀您来伊利拿礼#吕文秀邀您来伊利拿礼#青晓琼邀您来伊利拿礼#唐佳丽邀您来伊利拿礼#国庆去哪里出行有伊利#放假倒计时4天#伊利伴国庆欢乐加倍'; 实验室的艺术家们  // 09.27  6+3+1


//闫杰邀您来伊利拿礼#邹春莲邀您来伊利拿礼#麻天天邀您来伊利拿礼#郎兰英邀您来伊利拿礼#国庆佳节伊利共享#  放假倒计时3天 假期倒计时 多提更划算 5+1+1+1
//童春燕邀您来伊利拿礼#何丽娟邀您来伊利拿礼#杨苗邀您来伊利拿礼#王容邀您来伊利拿礼#宋莉邀您来伊利拿礼#文梅邀您来伊利拿礼#杨科凤邀您来伊利拿礼#宋明菊邀您来伊利拿礼#曾秀君邀您来伊利拿礼#熊心灵邀您来伊利拿礼 9.29 10
//倒计时一天#10#放假倒计时2天#欢度国庆伊利情浓 假期快乐#假期如约而至#一切就绪坐等放假#国庆伊利礼相随# 9.30 +4+4
//红旗飘飘伊利醇香 在路上#彭丽娜邀您来伊利拿礼#刘丽凤邀您来伊利拿礼#邱威邀您来伊利拿礼#国庆#国庆快乐#齐宏波邀您来伊利拿礼#  8

let notice = ''
!(async () => {
    if (typeof $request != "undefined") {
        await getYiLiCookie();
    } else {
        await main();
    }
})().catch((e) => {$.log(e)}).finally(() => {$.done({});});

async function main() {
    console.log('作者：@xzxxn777\n频道：https://t.me/xzxxn777\n群组：https://t.me/xzxxn7777\n自用机场推荐：https://xn--diqv0fut7b.com\n')
    Utils = await loadUtils();
    
    // 要排除的 fragmentId 列表   如果稀有13 14  15 16   (不翻卡)
    //  13,安慕希 14,金典 15,优酸乳 16,伊利纯牛奶 17,伊刻活泉  18,臻浓
    //  19,QQ星  20,舒化 21,谷粒多 22,植选 23,畅意100%  24,万能卡
    const excludedFragmentIds = [13, 14, 15, 16];
    
    // 要排除的奖励内容
   
    // 要排除的奖励内容列表
    const excludedRewards = ["满99-30元优惠券", "15元优惠券"];
    

    // 存储出现过的错误口令
    let invalidCodes = [];

    for (const item of YiLi) {
        mobile = item.mobile;
        unionId = item.unionId;
        nickName = item.nickName;
        avatarUrl = item.avatarUrl;
        openId = item.openId;
        yiliToken = item.yiliToken;
        console.log(`用户：${mobile}开始任务`)
        let login = await commonPost('/v2/wechat/applet/set-user-info', {
            "headImg": avatarUrl,
            "phoneNum": mobile,
            "nickName": nickName,
            "openId": openId,
            "unionId": unionId,
            "ciphertext": Utils.md5(unionId + 'ui@op9889;as98gh12c3b1&!jiasdasdjlkyf98r4y3ujfnakhjrf098')
        })
        if (login.code != 200) {
            console.log(login.message)
            await sendMsg(`用户：${mobile}\nyiliToken已过期，请重新获取`);
            continue
        }
        console.log(`登录成功`)
        token = login.data.token;
        type = login.data.num1;
        type1 = login.data.num2;
        let ticketInfo = await commonGet(`/fragment/ticket/ticket-info?openId=${openId}`)
        if (!ticketInfo.data.sign) {
            let sign = await commonGet(`/fragment/ticket/sign?openId=${openId}`)
            console.log(`签到：${sign.message}`)
        }
        if (!ticketInfo.data.seePage) {
            let seePage = await commonGet(`/fragment/ticket/see-page?openId=${openId}`)
            console.log(`浏览：${seePage.message}`)
        }

        // 将口令字符串拆分成独立的口令
        
        const YiLi_Codes = YiLi_Code.split('#').filter(code => code.trim());
        const validCodeCount = YiLi_Codes.length;

        if (validCodeCount === 0) {
            console.log('本次运行没有有效口令，跳过口令兑换');
        } else {
            console.log(`本次运行共有${validCodeCount}个有效口令`);
        }

        for (let code of YiLi_Codes) {
            // 检查是否之前出现过错误口令
            if (invalidCodes.includes(code)) {
                console.log(`跳过错误口令：${code}`);
                continue;
            }

            let authorize = await yiLiGet(`/developer/oauth2/buyer/authorize?app_key=zdcade261b48eb4c5e`);
            if (authorize.data) {
                let inputCode = await commonGet(`/fragment/ticket/input-code?code=${encodeURIComponent(code)}&authorizationCode=${authorize.data}&openId=${openId}`);

                // 记录使用的口令和兑换结果
                console.log(`使用口令：${code} 口令兑换：${inputCode.message}`);

                // 如果口令有误，将其加入 invalidCodes 列表，跳过后续账号使用
                if (inputCode.message.includes('口令有误')) {
                    console.log(`口令有误，将其标记为无效`);
                    invalidCodes.push(code);
                    continue;  // 继续处理下一个口令，但不影响当前账号
                }

                if (inputCode.message.includes('今日输入口令次数已达上限')) {
                    console.log('今日输入口令次数已达上限，停止后续口令处理');
                    break;
                }
            } else {
                console.log(authorize?.error?.msg);
                await sendMsg(`用户：${mobile}\nyiliToken已过期，请重新获取`);
                break;
            }
        }

        let ticketGet = await commonGet(`/fragment/ticket/get?openId=${openId}`);
        console.log(`拥有抽卡次数：${ticketGet.data}次`);
        for (let i = 0; i < ticketGet.data; i++) {
            let lottery = await commonGet(`/fragmentActivity/lottery?activityId=2&openId=${openId}`);
            console.log(`抽卡获得：${lottery.data.fragmentName}`);
        }

        let cardInfo = await commonGet(`/fragmentActivity/fragment?activityId=2&openId=${openId}`);
        for (let card of cardInfo.data) {
            console.log(`卡片：${card.fragmentName} 数量：${card.num}`);

            // 只在卡片数量大于1且fragmentId不在排除列表中时翻卡，且保留至少1张卡片
            if (card.num > 1 && YiLi_Open) {
                if (excludedFragmentIds.includes(card.fragmentId)) {
                    console.log(`卡片ID：${card.fragmentId}（${card.fragmentName}）已排除，不进行翻卡操作`);
                } else {
                    // 翻卡次数 = 卡片数量 - 1
                    for (let i = 0; i < card.num - 1; i++) {
                        let openPrize = await commonGet(`/fragmentActivity/open-prize?fragmentId=${card.fragmentId}&activityId=2&openId=${openId}`);

                        // 排除指定的奖励内容
                        if (!excludedRewards.includes(openPrize.data.prizeName)) {
                            console.log(`翻卡获得：${openPrize.data.prizeName}`);
                            notice += `用户${mobile} 翻卡获得：${openPrize.data.prizeName}\n`;
                        } else {
                            console.log(`翻卡获得：${openPrize.data.prizeName}，已排除`);
                        }
                    }
                }
            }
        }
    }

    if (notice) {
        await sendMsg(notice);
    }
}





async function getYiLiCookie() {
    const yiliToken = $request.headers["access-token"];
    if (!yiliToken) {
        return
    }
    const body = $.toObj($response.body);
    if (!body || !body.data) {
        return
    }
    const newData = {"mobile": body.data.mobile, "openId": body.data.openId, "unionId": body.data.unionId, "nickName": body.data.nickName, "avatarUrl": body.data.avatarUrl, "yiliToken":yiliToken};
    const index = YiLi.findIndex(e => e.mobile == newData.mobile);
    if (index !== -1) {
        if (YiLi[index].yiliToken == newData.yiliToken) {
            return
        } else {
            YiLi[index] = newData;
            console.log(newData.yiliToken)
            $.msg($.name, `🎉用户${newData.mobile}更新yiliToken成功!`, ``);
        }
    } else {
        YiLi.push(newData)
        console.log(newData.yiliToken)
        $.msg($.name, `🎉新增用户${newData.mobile}成功!`, ``);
    }
    $.setjson(YiLi, "YiLi");
}

async function yiLiGet(url) {
    return new Promise(resolve => {
        const options = {
            url: `https://msmarket.msx.digitalyili.com${url}`,
            headers : {
                'register-source': '',
                'forward-appid': 'wx06af0ef532292cd3',
                'source-type': '',
                'content-type': 'application/json',
                'atv-page': '',
                'scene': '1089',
                'xweb_xhr': '1',
                'access-token': yiliToken,
                'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 MicroMessenger/6.8.0(0x16080000) NetType/WIFI MiniProgramEnv/Mac MacWechat/WMPF MacWechat/3.8.7(0x13080712) XWEB/1191',
                'tenant-id': '1559474730809618433',
                'accept': '*/*',
                'Sec-Fetch-Site': 'cross-site',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Dest': 'empty',
                'Referer': `https://servicewechat.com/wx06af0ef532292cd3/533/page-frame.html`,
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'zh-CN,zh;q=0.9',
            }
        }
        $.get(options, async (err, resp, data) => {
            try {
                if (err) {
                    console.log(`${JSON.stringify(err)}`)
                    console.log(`${$.name} API请求失败，请检查网路重试`)
                } else {
                    await $.wait(2000)
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

async function commonPost(url, body) {
    let params = getParams();
    return new Promise(resolve => {
        const options = {
            url: `https://wx-camp-180-shuangjie-api.mscampapi.digitalyili.com${url}`,
            headers : {
                'content-type': 'application/json',
                'xweb_xhr': '1',
                'timestamp': params.timestamp,
                'signature': params.signature,
                'uniquecode': params.uniquecode,
                'access_token': token,
                'token': token,
                'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 MicroMessenger/6.8.0(0x16080000) NetType/WIFI MiniProgramEnv/Mac MacWechat/WMPF MacWechat/3.8.7(0x13080712) XWEB/1191',
                'app-version': '1.1.1',
                'accept': '*/*',
                'Sec-Fetch-Site': 'cross-site',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Dest': 'empty',
                'Referer': `https://servicewechat.com/wx06af0ef532292cd3/533/page-frame.html`,
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'zh-CN,zh;q=0.9',
            },
            body: JSON.stringify(body)
        }
        $.post(options, async (err, resp, data) => {
            try {
                if (err) {
                    console.log(`${JSON.stringify(err)}`)
                    console.log(`${$.name} API请求失败，请检查网路重试`)
                } else {
                    await $.wait(2000)
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
    let params = getParams();
    return new Promise(resolve => {
        const options = {
            url: `https://wx-camp-180-shuangjie-api.mscampapi.digitalyili.com${url}`,
            headers : {
                'content-type': 'application/json',
                'xweb_xhr': '1',
                'timestamp': params.timestamp,
                'signature': params.signature,
                'uniquecode': params.uniquecode,
                'access_token': token,
                'token': token,
                'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 MicroMessenger/6.8.0(0x16080000) NetType/WIFI MiniProgramEnv/Mac MacWechat/WMPF MacWechat/3.8.7(0x13080712) XWEB/1191',
                'app-version': '1.1.1',
                'accept': '*/*',
                'Sec-Fetch-Site': 'cross-site',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Dest': 'empty',
                'Referer': `https://servicewechat.com/wx06af0ef532292cd3/533/page-frame.html`,
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'zh-CN,zh;q=0.9',
            }
        }
        $.get(options, async (err, resp, data) => {
            try {
                if (err) {
                    console.log(`${JSON.stringify(err)}`)
                    console.log(`${$.name} API请求失败，请检查网路重试`)
                } else {
                    await $.wait(2000)
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

function getParams() {
    let timestamp = Date.now();
    let uniquecode = timestamp + "&" + String(Math.floor(1e5 + 9e5 * Math.random()));
    var F = "timeStamp:"+ timestamp + "&uniqueCode:" + uniquecode + {
        1: "963QQ45465465xcvdasfasdfzxEcadfafzafoi897as8dfw8g4za78qqfd878000df8/er78a",
        2: "363QQ45465465xcvdas89!safzafwa36paweoi897as8dfw8g4za78qqfd878000df8/er89b",
        3: "763Qi45895465xcv89as89!sa2616wa36paweoi897as8dfw8g4za78qqfd878000df8/eqr23b",
        4: "7531Qi45891546115xcv89as819!sa26161wa36pa81g4z1a78qqfd87810001df18/eqr213b",
        5: "3f53f1Qia4f5f91546fa115axcvfff89asf819!saff26161fwa36fpa81g4z1fa7/eqr21f3b",
        6: "egf513gf1Qifag4f5f9f154g6fa115afxgcvffgf89gasgf8g19!saffg2g6161gfg6fpa@g1g",
        7: "2e@gf513g2f1Qif@ag4!f5f92f215!4g6fa115afxgcvffgf89gasgf82g19!2gfwa3g62fpa2",
        8: "6e@!gf514g2fb1Qif@!bag41f89gasbgf8b2g19!2gfwa3gb62fbpa@g1g32b9999!",
        9: "6a@!gf514g2fb1Qif@!bag41f89gasbgf8b2g19!2gfwa3gb62fbpa@g1g32b9869!++3",
        10: "2e@gf513g2f1Qif@ag4!sdfzxEcadfafzafoi897as8dfw8g4za78qqfd8780df8==/er78a"
    }[type1], e = Utils.md5(F).toUpperCase();
    let signature = 1 == type ? aesEncrypt(e) : 2 == type ? Utils.md5(e).toUpperCase() : 3 == type ? Utils.md5(aesEncrypt(F)).toUpperCase() : 4 == type ? aesEncrypt(aesEncrypt(F)) : e;
    return {"timestamp": timestamp, "uniquecode": uniquecode, "signature": signature}
}

function aesEncrypt(e) {
    let cryptojs = Utils.createCryptoJS();
    var t = cryptojs.enc.Utf8.parse('asdvbnqwer!=564av8952116lkouytb+')
        , a = cryptojs.enc.Utf8.parse('Y9uR16ByteIvH8q9')
        , i = cryptojs.enc.Utf8.parse(e)
        , r = cryptojs.AES.encrypt(i, t, {
        iv: a,
        mode: cryptojs.mode.CBC,
        padding: cryptojs.pad.Pkcs7
    });
    return cryptojs.enc.Base64.stringify(r.ciphertext)
}

async function loadUtils() {
    let code = $.getdata('Utils_Code') || '';
    if (code && Object.keys(code).length) {
        console.log(`✅ ${$.name}: 缓存中存在Utils代码, 跳过下载`)
        eval(code)
        return creatUtils();
    }
    console.log(`🚀 ${$.name}: 开始下载Utils代码`)
    return new Promise(async (resolve) => {
        $.getScript(
            'https://mirror.ghproxy.com/https://raw.githubusercontent.com/xzxxn777/Surge/main/Utils/Utils.js'
        ).then((fn) => {
            $.setdata(fn, "Utils_Code")
            eval(fn)
            console.log(`✅ Utils加载成功, 请继续`)
            resolve(creatUtils())
        })
    })
}

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
}

// prettier-ignore
function Env(t,e){class s{constructor(t){this.env=t}send(t,e="GET"){t="string"==typeof t?{url:t}:t;let s=this.get;return"POST"===e&&(s=this.post),new Promise(((e,i)=>{s.call(this,t,((t,s,o)=>{t?i(t):e(s)}))}))}get(t){return this.send.call(this.env,t)}post(t){return this.send.call(this.env,t,"POST")}}return new class{constructor(t,e){this.logLevels={debug:0,info:1,warn:2,error:3},this.logLevelPrefixs={debug:"[DEBUG] ",info:"[INFO] ",warn:"[WARN] ",error:"[ERROR] "},this.logLevel="info",this.name=t,this.http=new s(this),this.data=null,this.dataFile="box.dat",this.logs=[],this.isMute=!1,this.isNeedRewrite=!1,this.logSeparator="\n",this.encoding="utf-8",this.startTime=(new Date).getTime(),Object.assign(this,e),this.log("",`🔔${this.name}, 开始!`)}getEnv(){return"undefined"!=typeof $environment&&$environment["surge-version"]?"Surge":"undefined"!=typeof $environment&&$environment["stash-version"]?"Stash":"undefined"!=typeof module&&module.exports?"Node.js":"undefined"!=typeof $task?"Quantumult X":"undefined"!=typeof $loon?"Loon":"undefined"!=typeof $rocket?"Shadowrocket":void 0}isNode(){return"Node.js"===this.getEnv()}isQuanX(){return"Quantumult X"===this.getEnv()}isSurge(){return"Surge"===this.getEnv()}isLoon(){return"Loon"===this.getEnv()}isShadowrocket(){return"Shadowrocket"===this.getEnv()}isStash(){return"Stash"===this.getEnv()}toObj(t,e=null){try{return JSON.parse(t)}catch{return e}}toStr(t,e=null,...s){try{return JSON.stringify(t,...s)}catch{return e}}getjson(t,e){let s=e;if(this.getdata(t))try{s=JSON.parse(this.getdata(t))}catch{}return s}setjson(t,e){try{return this.setdata(JSON.stringify(t),e)}catch{return!1}}getScript(t){return new Promise((e=>{this.get({url:t},((t,s,i)=>e(i)))}))}runScript(t,e){return new Promise((s=>{let i=this.getdata("@chavy_boxjs_userCfgs.httpapi");i=i?i.replace(/\n/g,"").trim():i;let o=this.getdata("@chavy_boxjs_userCfgs.httpapi_timeout");o=o?1*o:20,o=e&&e.timeout?e.timeout:o;const[r,a]=i.split("@"),n={url:`http://${a}/v1/scripting/evaluate`,body:{script_text:t,mock_type:"cron",timeout:o},headers:{"X-Key":r,Accept:"*/*"},timeout:o};this.post(n,((t,e,i)=>s(i)))})).catch((t=>this.logErr(t)))}loaddata(){if(!this.isNode())return{};{this.fs=this.fs?this.fs:require("fs"),this.path=this.path?this.path:require("path");const t=this.path.resolve(this.dataFile),e=this.path.resolve(process.cwd(),this.dataFile),s=this.fs.existsSync(t),i=!s&&this.fs.existsSync(e);if(!s&&!i)return{};{const i=s?t:e;try{return JSON.parse(this.fs.readFileSync(i))}catch(t){return{}}}}}writedata(){if(this.isNode()){this.fs=this.fs?this.fs:require("fs"),this.path=this.path?this.path:require("path");const t=this.path.resolve(this.dataFile),e=this.path.resolve(process.cwd(),this.dataFile),s=this.fs.existsSync(t),i=!s&&this.fs.existsSync(e),o=JSON.stringify(this.data);s?this.fs.writeFileSync(t,o):i?this.fs.writeFileSync(e,o):this.fs.writeFileSync(t,o)}}lodash_get(t,e,s){const i=e.replace(/\[(\d+)\]/g,".$1").split(".");let o=t;for(const t of i)if(o=Object(o)[t],void 0===o)return s;return o}lodash_set(t,e,s){return Object(t)!==t||(Array.isArray(e)||(e=e.toString().match(/[^.[\]]+/g)||[]),e.slice(0,-1).reduce(((t,s,i)=>Object(t[s])===t[s]?t[s]:t[s]=Math.abs(e[i+1])>>0==+e[i+1]?[]:{}),t)[e[e.length-1]]=s),t}getdata(t){let e=this.getval(t);if(/^@/.test(t)){const[,s,i]=/^@(.*?)\.(.*?)$/.exec(t),o=s?this.getval(s):"";if(o)try{const t=JSON.parse(o);e=t?this.lodash_get(t,i,""):e}catch(t){e=""}}return e}setdata(t,e){let s=!1;if(/^@/.test(e)){const[,i,o]=/^@(.*?)\.(.*?)$/.exec(e),r=this.getval(i),a=i?"null"===r?null:r||"{}":"{}";try{const e=JSON.parse(a);this.lodash_set(e,o,t),s=this.setval(JSON.stringify(e),i)}catch(e){const r={};this.lodash_set(r,o,t),s=this.setval(JSON.stringify(r),i)}}else s=this.setval(t,e);return s}getval(t){switch(this.getEnv()){case"Surge":case"Loon":case"Stash":case"Shadowrocket":return $persistentStore.read(t);case"Quantumult X":return $prefs.valueForKey(t);case"Node.js":return this.data=this.loaddata(),this.data[t];default:return this.data&&this.data[t]||null}}setval(t,e){switch(this.getEnv()){case"Surge":case"Loon":case"Stash":case"Shadowrocket":return $persistentStore.write(t,e);case"Quantumult X":return $prefs.setValueForKey(t,e);case"Node.js":return this.data=this.loaddata(),this.data[e]=t,this.writedata(),!0;default:return this.data&&this.data[e]||null}}initGotEnv(t){this.got=this.got?this.got:require("got"),this.cktough=this.cktough?this.cktough:require("tough-cookie"),this.ckjar=this.ckjar?this.ckjar:new this.cktough.CookieJar,t&&(t.headers=t.headers?t.headers:{},t&&(t.headers=t.headers?t.headers:{},void 0===t.headers.cookie&&void 0===t.headers.Cookie&&void 0===t.cookieJar&&(t.cookieJar=this.ckjar)))}get(t,e=(()=>{})){switch(t.headers&&(delete t.headers["Content-Type"],delete t.headers["Content-Length"],delete t.headers["content-type"],delete t.headers["content-length"]),t.params&&(t.url+="?"+this.queryStr(t.params)),void 0===t.followRedirect||t.followRedirect||((this.isSurge()||this.isLoon())&&(t["auto-redirect"]=!1),this.isQuanX()&&(t.opts?t.opts.redirection=!1:t.opts={redirection:!1})),this.getEnv()){case"Surge":case"Loon":case"Stash":case"Shadowrocket":default:this.isSurge()&&this.isNeedRewrite&&(t.headers=t.headers||{},Object.assign(t.headers,{"X-Surge-Skip-Scripting":!1})),$httpClient.get(t,((t,s,i)=>{!t&&s&&(s.body=i,s.statusCode=s.status?s.status:s.statusCode,s.status=s.statusCode),e(t,s,i)}));break;case"Quantumult X":this.isNeedRewrite&&(t.opts=t.opts||{},Object.assign(t.opts,{hints:!1})),$task.fetch(t).then((t=>{const{statusCode:s,statusCode:i,headers:o,body:r,bodyBytes:a}=t;e(null,{status:s,statusCode:i,headers:o,body:r,bodyBytes:a},r,a)}),(t=>e(t&&t.error||"UndefinedError")));break;case"Node.js":let s=require("iconv-lite");this.initGotEnv(t),this.got(t).on("redirect",((t,e)=>{try{if(t.headers["set-cookie"]){const s=t.headers["set-cookie"].map(this.cktough.Cookie.parse).toString();s&&this.ckjar.setCookieSync(s,null),e.cookieJar=this.ckjar}}catch(t){this.logErr(t)}})).then((t=>{const{statusCode:i,statusCode:o,headers:r,rawBody:a}=t,n=s.decode(a,this.encoding);e(null,{status:i,statusCode:o,headers:r,rawBody:a,body:n},n)}),(t=>{const{message:i,response:o}=t;e(i,o,o&&s.decode(o.rawBody,this.encoding))}));break}}post(t,e=(()=>{})){const s=t.method?t.method.toLocaleLowerCase():"post";switch(t.body&&t.headers&&!t.headers["Content-Type"]&&!t.headers["content-type"]&&(t.headers["content-type"]="application/x-www-form-urlencoded"),t.headers&&(delete t.headers["Content-Length"],delete t.headers["content-length"]),void 0===t.followRedirect||t.followRedirect||((this.isSurge()||this.isLoon())&&(t["auto-redirect"]=!1),this.isQuanX()&&(t.opts?t.opts.redirection=!1:t.opts={redirection:!1})),this.getEnv()){case"Surge":case"Loon":case"Stash":case"Shadowrocket":default:this.isSurge()&&this.isNeedRewrite&&(t.headers=t.headers||{},Object.assign(t.headers,{"X-Surge-Skip-Scripting":!1})),$httpClient[s](t,((t,s,i)=>{!t&&s&&(s.body=i,s.statusCode=s.status?s.status:s.statusCode,s.status=s.statusCode),e(t,s,i)}));break;case"Quantumult X":t.method=s,this.isNeedRewrite&&(t.opts=t.opts||{},Object.assign(t.opts,{hints:!1})),$task.fetch(t).then((t=>{const{statusCode:s,statusCode:i,headers:o,body:r,bodyBytes:a}=t;e(null,{status:s,statusCode:i,headers:o,body:r,bodyBytes:a},r,a)}),(t=>e(t&&t.error||"UndefinedError")));break;case"Node.js":let i=require("iconv-lite");this.initGotEnv(t);const{url:o,...r}=t;this.got[s](o,r).then((t=>{const{statusCode:s,statusCode:o,headers:r,rawBody:a}=t,n=i.decode(a,this.encoding);e(null,{status:s,statusCode:o,headers:r,rawBody:a,body:n},n)}),(t=>{const{message:s,response:o}=t;e(s,o,o&&i.decode(o.rawBody,this.encoding))}));break}}time(t,e=null){const s=e?new Date(e):new Date;let i={"M+":s.getMonth()+1,"d+":s.getDate(),"H+":s.getHours(),"m+":s.getMinutes(),"s+":s.getSeconds(),"q+":Math.floor((s.getMonth()+3)/3),S:s.getMilliseconds()};/(y+)/.test(t)&&(t=t.replace(RegExp.$1,(s.getFullYear()+"").substr(4-RegExp.$1.length)));for(let e in i)new RegExp("("+e+")").test(t)&&(t=t.replace(RegExp.$1,1==RegExp.$1.length?i[e]:("00"+i[e]).substr((""+i[e]).length)));return t}queryStr(t){let e="";for(const s in t){let i=t[s];null!=i&&""!==i&&("object"==typeof i&&(i=JSON.stringify(i)),e+=`${s}=${i}&`)}return e=e.substring(0,e.length-1),e}msg(e=t,s="",i="",o={}){const r=t=>{const{$open:e,$copy:s,$media:i,$mediaMime:o}=t;switch(typeof t){case void 0:return t;case"string":switch(this.getEnv()){case"Surge":case"Stash":default:return{url:t};case"Loon":case"Shadowrocket":return t;case"Quantumult X":return{"open-url":t};case"Node.js":return}case"object":switch(this.getEnv()){case"Surge":case"Stash":case"Shadowrocket":default:{const r={};let a=t.openUrl||t.url||t["open-url"]||e;a&&Object.assign(r,{action:"open-url",url:a});let n=t["update-pasteboard"]||t.updatePasteboard||s;if(n&&Object.assign(r,{action:"clipboard",text:n}),i){let t,e,s;if(i.startsWith("http"))t=i;else if(i.startsWith("data:")){const[t]=i.split(";"),[,o]=i.split(",");e=o,s=t.replace("data:","")}else{e=i,s=(t=>{const e={JVBERi0:"application/pdf",R0lGODdh:"image/gif",R0lGODlh:"image/gif",iVBORw0KGgo:"image/png","/9j/":"image/jpg"};for(var s in e)if(0===t.indexOf(s))return e[s];return null})(i)}Object.assign(r,{"media-url":t,"media-base64":e,"media-base64-mime":o??s})}return Object.assign(r,{"auto-dismiss":t["auto-dismiss"],sound:t.sound}),r}case"Loon":{const s={};let o=t.openUrl||t.url||t["open-url"]||e;o&&Object.assign(s,{openUrl:o});let r=t.mediaUrl||t["media-url"];return i?.startsWith("http")&&(r=i),r&&Object.assign(s,{mediaUrl:r}),console.log(JSON.stringify(s)),s}case"Quantumult X":{const o={};let r=t["open-url"]||t.url||t.openUrl||e;r&&Object.assign(o,{"open-url":r});let a=t["media-url"]||t.mediaUrl;i?.startsWith("http")&&(a=i),a&&Object.assign(o,{"media-url":a});let n=t["update-pasteboard"]||t.updatePasteboard||s;return n&&Object.assign(o,{"update-pasteboard":n}),console.log(JSON.stringify(o)),o}case"Node.js":return}default:return}};if(!this.isMute)switch(this.getEnv()){case"Surge":case"Loon":case"Stash":case"Shadowrocket":default:$notification.post(e,s,i,r(o));break;case"Quantumult X":$notify(e,s,i,r(o));break;case"Node.js":break}if(!this.isMuteLog){let t=["","==============📣系统通知📣=============="];t.push(e),s&&t.push(s),i&&t.push(i),console.log(t.join("\n")),this.logs=this.logs.concat(t)}}debug(...t){this.logLevels[this.logLevel]<=this.logLevels.debug&&(t.length>0&&(this.logs=[...this.logs,...t]),console.log(`${this.logLevelPrefixs.debug}${t.map((t=>t??String(t))).join(this.logSeparator)}`))}info(...t){this.logLevels[this.logLevel]<=this.logLevels.info&&(t.length>0&&(this.logs=[...this.logs,...t]),console.log(`${this.logLevelPrefixs.info}${t.map((t=>t??String(t))).join(this.logSeparator)}`))}warn(...t){this.logLevels[this.logLevel]<=this.logLevels.warn&&(t.length>0&&(this.logs=[...this.logs,...t]),console.log(`${this.logLevelPrefixs.warn}${t.map((t=>t??String(t))).join(this.logSeparator)}`))}error(...t){this.logLevels[this.logLevel]<=this.logLevels.error&&(t.length>0&&(this.logs=[...this.logs,...t]),console.log(`${this.logLevelPrefixs.error}${t.map((t=>t??String(t))).join(this.logSeparator)}`))}log(...t){t.length>0&&(this.logs=[...this.logs,...t]),console.log(t.map((t=>t??String(t))).join(this.logSeparator))}logErr(t,e){switch(this.getEnv()){case"Surge":case"Loon":case"Stash":case"Shadowrocket":case"Quantumult X":default:this.log("",`❗️${this.name}, 错误!`,e,t);break;case"Node.js":this.log("",`❗️${this.name}, 错误!`,e,void 0!==t.message?t.message:t,t.stack);break}}wait(t){return new Promise((e=>setTimeout(e,t)))}done(t={}){const e=((new Date).getTime()-this.startTime)/1e3;switch(this.log("",`🔔${this.name}, 结束! 🕛 ${e} 秒`),this.log(),this.getEnv()){case"Surge":case"Loon":case"Stash":case"Shadowrocket":case"Quantumult X":default:$done(t);break;case"Node.js":process.exit(1)}}}(t,e)}






async function getYiLiCookie() {
    const yiliToken = $request.headers["access-token"];
    if (!yiliToken) {
        return
    }
    const body = $.toObj($response.body);
    if (!body || !body.data) {
        return
    }
    const newData = {"mobile": body.data.mobile, "openId": body.data.openId, "unionId": body.data.unionId, "nickName": body.data.nickName, "avatarUrl": body.data.avatarUrl, "yiliToken":yiliToken};
    const index = YiLi.findIndex(e => e.mobile == newData.mobile);
    if (index !== -1) {
        if (YiLi[index].yiliToken == newData.yiliToken) {
            return
        } else {
            YiLi[index] = newData;
            console.log(newData.yiliToken)
            $.msg($.name, `🎉用户${newData.mobile}更新yiliToken成功!`, ``);
        }
    } else {
        YiLi.push(newData)
        console.log(newData.yiliToken)
        $.msg($.name, `🎉新增用户${newData.mobile}成功!`, ``);
    }
    $.setjson(YiLi, "YiLi");
}

async function yiLiGet(url) {
    return new Promise(resolve => {
        const options = {
            url: `https://msmarket.msx.digitalyili.com${url}`,
            headers : {
                'register-source': '',
                'forward-appid': 'wx06af0ef532292cd3',
                'source-type': '',
                'content-type': 'application/json',
                'atv-page': '',
                'scene': '1089',
                'xweb_xhr': '1',
                'access-token': yiliToken,
                'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 MicroMessenger/6.8.0(0x16080000) NetType/WIFI MiniProgramEnv/Mac MacWechat/WMPF MacWechat/3.8.7(0x13080712) XWEB/1191',
                'tenant-id': '1559474730809618433',
                'accept': '*/*',
                'Sec-Fetch-Site': 'cross-site',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Dest': 'empty',
                'Referer': `https://servicewechat.com/wx06af0ef532292cd3/533/page-frame.html`,
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'zh-CN,zh;q=0.9',
            }
        }
        $.get(options, async (err, resp, data) => {
            try {
                if (err) {
                    console.log(`${JSON.stringify(err)}`)
                    console.log(`${$.name} API请求失败，请检查网路重试`)
                } else {
                    await $.wait(2000)
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

async function commonPost(url, body) {
    let params = getParams();
    return new Promise(resolve => {
        const options = {
            url: `https://wx-camp-180-shuangjie-api.mscampapi.digitalyili.com${url}`,
            headers : {
                'content-type': 'application/json',
                'xweb_xhr': '1',
                'timestamp': params.timestamp,
                'signature': params.signature,
                'uniquecode': params.uniquecode,
                'access_token': token,
                'token': token,
                'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 MicroMessenger/6.8.0(0x16080000) NetType/WIFI MiniProgramEnv/Mac MacWechat/WMPF MacWechat/3.8.7(0x13080712) XWEB/1191',
                'app-version': '1.1.1',
                'accept': '*/*',
                'Sec-Fetch-Site': 'cross-site',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Dest': 'empty',
                'Referer': `https://servicewechat.com/wx06af0ef532292cd3/533/page-frame.html`,
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'zh-CN,zh;q=0.9',
            },
            body: JSON.stringify(body)
        }
        $.post(options, async (err, resp, data) => {
            try {
                if (err) {
                    console.log(`${JSON.stringify(err)}`)
                    console.log(`${$.name} API请求失败，请检查网路重试`)
                } else {
                    await $.wait(2000)
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
    let params = getParams();
    return new Promise(resolve => {
        const options = {
            url: `https://wx-camp-180-shuangjie-api.mscampapi.digitalyili.com${url}`,
            headers : {
                'content-type': 'application/json',
                'xweb_xhr': '1',
                'timestamp': params.timestamp,
                'signature': params.signature,
                'uniquecode': params.uniquecode,
                'access_token': token,
                'token': token,
                'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 MicroMessenger/6.8.0(0x16080000) NetType/WIFI MiniProgramEnv/Mac MacWechat/WMPF MacWechat/3.8.7(0x13080712) XWEB/1191',
                'app-version': '1.1.1',
                'accept': '*/*',
                'Sec-Fetch-Site': 'cross-site',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Dest': 'empty',
                'Referer': `https://servicewechat.com/wx06af0ef532292cd3/533/page-frame.html`,
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'zh-CN,zh;q=0.9',
            }
        }
        $.get(options, async (err, resp, data) => {
            try {
                if (err) {
                    console.log(`${JSON.stringify(err)}`)
                    console.log(`${$.name} API请求失败，请检查网路重试`)
                } else {
                    await $.wait(2000)
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

function getParams() {
    let timestamp = Date.now();
    let uniquecode = timestamp + "&" + String(Math.floor(1e5 + 9e5 * Math.random()));
    var F = "timeStamp:"+ timestamp + "&uniqueCode:" + uniquecode + {
        1: "963QQ45465465xcvdasfasdfzxEcadfafzafoi897as8dfw8g4za78qqfd878000df8/er78a",
        2: "363QQ45465465xcvdas89!safzafwa36paweoi897as8dfw8g4za78qqfd878000df8/er89b",
        3: "763Qi45895465xcv89as89!sa2616wa36paweoi897as8dfw8g4za78qqfd878000df8/eqr23b",
        4: "7531Qi45891546115xcv89as819!sa26161wa36pa81g4z1a78qqfd87810001df18/eqr213b",
        5: "3f53f1Qia4f5f91546fa115axcvfff89asf819!saff26161fwa36fpa81g4z1fa7/eqr21f3b",
        6: "egf513gf1Qifag4f5f9f154g6fa115afxgcvffgf89gasgf8g19!saffg2g6161gfg6fpa@g1g",
        7: "2e@gf513g2f1Qif@ag4!f5f92f215!4g6fa115afxgcvffgf89gasgf82g19!2gfwa3g62fpa2",
        8: "6e@!gf514g2fb1Qif@!bag41f89gasbgf8b2g19!2gfwa3gb62fbpa@g1g32b9999!",
        9: "6a@!gf514g2fb1Qif@!bag41f89gasbgf8b2g19!2gfwa3gb62fbpa@g1g32b9869!++3",
        10: "2e@gf513g2f1Qif@ag4!sdfzxEcadfafzafoi897as8dfw8g4za78qqfd8780df8==/er78a"
    }[type1], e = Utils.md5(F).toUpperCase();
    let signature = 1 == type ? aesEncrypt(e) : 2 == type ? Utils.md5(e).toUpperCase() : 3 == type ? Utils.md5(aesEncrypt(F)).toUpperCase() : 4 == type ? aesEncrypt(aesEncrypt(F)) : e;
    return {"timestamp": timestamp, "uniquecode": uniquecode, "signature": signature}
}

function aesEncrypt(e) {
    let cryptojs = Utils.createCryptoJS();
    var t = cryptojs.enc.Utf8.parse('asdvbnqwer!=564av8952116lkouytb+')
        , a = cryptojs.enc.Utf8.parse('Y9uR16ByteIvH8q9')
        , i = cryptojs.enc.Utf8.parse(e)
        , r = cryptojs.AES.encrypt(i, t, {
        iv: a,
        mode: cryptojs.mode.CBC,
        padding: cryptojs.pad.Pkcs7
    });
    return cryptojs.enc.Base64.stringify(r.ciphertext)
}

async function loadUtils() {
    let code = $.getdata('Utils_Code') || '';
    if (code && Object.keys(code).length) {
        console.log(`✅ ${$.name}: 缓存中存在Utils代码, 跳过下载`)
        eval(code)
        return creatUtils();
    }
    console.log(`🚀 ${$.name}: 开始下载Utils代码`)
    return new Promise(async (resolve) => {
        $.getScript(
            'https://mirror.ghproxy.com/https://raw.githubusercontent.com/xzxxn777/Surge/main/Utils/Utils.js'
        ).then((fn) => {
            $.setdata(fn, "Utils_Code")
            eval(fn)
            console.log(`✅ Utils加载成功, 请继续`)
            resolve(creatUtils())
        })
    })
}

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
}

// prettier-ignore
function Env(t,e){class s{constructor(t){this.env=t}send(t,e="GET"){t="string"==typeof t?{url:t}:t;let s=this.get;return"POST"===e&&(s=this.post),new Promise(((e,i)=>{s.call(this,t,((t,s,o)=>{t?i(t):e(s)}))}))}get(t){return this.send.call(this.env,t)}post(t){return this.send.call(this.env,t,"POST")}}return new class{constructor(t,e){this.logLevels={debug:0,info:1,warn:2,error:3},this.logLevelPrefixs={debug:"[DEBUG] ",info:"[INFO] ",warn:"[WARN] ",error:"[ERROR] "},this.logLevel="info",this.name=t,this.http=new s(this),this.data=null,this.dataFile="box.dat",this.logs=[],this.isMute=!1,this.isNeedRewrite=!1,this.logSeparator="\n",this.encoding="utf-8",this.startTime=(new Date).getTime(),Object.assign(this,e),this.log("",`🔔${this.name}, 开始!`)}getEnv(){return"undefined"!=typeof $environment&&$environment["surge-version"]?"Surge":"undefined"!=typeof $environment&&$environment["stash-version"]?"Stash":"undefined"!=typeof module&&module.exports?"Node.js":"undefined"!=typeof $task?"Quantumult X":"undefined"!=typeof $loon?"Loon":"undefined"!=typeof $rocket?"Shadowrocket":void 0}isNode(){return"Node.js"===this.getEnv()}isQuanX(){return"Quantumult X"===this.getEnv()}isSurge(){return"Surge"===this.getEnv()}isLoon(){return"Loon"===this.getEnv()}isShadowrocket(){return"Shadowrocket"===this.getEnv()}isStash(){return"Stash"===this.getEnv()}toObj(t,e=null){try{return JSON.parse(t)}catch{return e}}toStr(t,e=null,...s){try{return JSON.stringify(t,...s)}catch{return e}}getjson(t,e){let s=e;if(this.getdata(t))try{s=JSON.parse(this.getdata(t))}catch{}return s}setjson(t,e){try{return this.setdata(JSON.stringify(t),e)}catch{return!1}}getScript(t){return new Promise((e=>{this.get({url:t},((t,s,i)=>e(i)))}))}runScript(t,e){return new Promise((s=>{let i=this.getdata("@chavy_boxjs_userCfgs.httpapi");i=i?i.replace(/\n/g,"").trim():i;let o=this.getdata("@chavy_boxjs_userCfgs.httpapi_timeout");o=o?1*o:20,o=e&&e.timeout?e.timeout:o;const[r,a]=i.split("@"),n={url:`http://${a}/v1/scripting/evaluate`,body:{script_text:t,mock_type:"cron",timeout:o},headers:{"X-Key":r,Accept:"*/*"},timeout:o};this.post(n,((t,e,i)=>s(i)))})).catch((t=>this.logErr(t)))}loaddata(){if(!this.isNode())return{};{this.fs=this.fs?this.fs:require("fs"),this.path=this.path?this.path:require("path");const t=this.path.resolve(this.dataFile),e=this.path.resolve(process.cwd(),this.dataFile),s=this.fs.existsSync(t),i=!s&&this.fs.existsSync(e);if(!s&&!i)return{};{const i=s?t:e;try{return JSON.parse(this.fs.readFileSync(i))}catch(t){return{}}}}}writedata(){if(this.isNode()){this.fs=this.fs?this.fs:require("fs"),this.path=this.path?this.path:require("path");const t=this.path.resolve(this.dataFile),e=this.path.resolve(process.cwd(),this.dataFile),s=this.fs.existsSync(t),i=!s&&this.fs.existsSync(e),o=JSON.stringify(this.data);s?this.fs.writeFileSync(t,o):i?this.fs.writeFileSync(e,o):this.fs.writeFileSync(t,o)}}lodash_get(t,e,s){const i=e.replace(/\[(\d+)\]/g,".$1").split(".");let o=t;for(const t of i)if(o=Object(o)[t],void 0===o)return s;return o}lodash_set(t,e,s){return Object(t)!==t||(Array.isArray(e)||(e=e.toString().match(/[^.[\]]+/g)||[]),e.slice(0,-1).reduce(((t,s,i)=>Object(t[s])===t[s]?t[s]:t[s]=Math.abs(e[i+1])>>0==+e[i+1]?[]:{}),t)[e[e.length-1]]=s),t}getdata(t){let e=this.getval(t);if(/^@/.test(t)){const[,s,i]=/^@(.*?)\.(.*?)$/.exec(t),o=s?this.getval(s):"";if(o)try{const t=JSON.parse(o);e=t?this.lodash_get(t,i,""):e}catch(t){e=""}}return e}setdata(t,e){let s=!1;if(/^@/.test(e)){const[,i,o]=/^@(.*?)\.(.*?)$/.exec(e),r=this.getval(i),a=i?"null"===r?null:r||"{}":"{}";try{const e=JSON.parse(a);this.lodash_set(e,o,t),s=this.setval(JSON.stringify(e),i)}catch(e){const r={};this.lodash_set(r,o,t),s=this.setval(JSON.stringify(r),i)}}else s=this.setval(t,e);return s}getval(t){switch(this.getEnv()){case"Surge":case"Loon":case"Stash":case"Shadowrocket":return $persistentStore.read(t);case"Quantumult X":return $prefs.valueForKey(t);case"Node.js":return this.data=this.loaddata(),this.data[t];default:return this.data&&this.data[t]||null}}setval(t,e){switch(this.getEnv()){case"Surge":case"Loon":case"Stash":case"Shadowrocket":return $persistentStore.write(t,e);case"Quantumult X":return $prefs.setValueForKey(t,e);case"Node.js":return this.data=this.loaddata(),this.data[e]=t,this.writedata(),!0;default:return this.data&&this.data[e]||null}}initGotEnv(t){this.got=this.got?this.got:require("got"),this.cktough=this.cktough?this.cktough:require("tough-cookie"),this.ckjar=this.ckjar?this.ckjar:new this.cktough.CookieJar,t&&(t.headers=t.headers?t.headers:{},t&&(t.headers=t.headers?t.headers:{},void 0===t.headers.cookie&&void 0===t.headers.Cookie&&void 0===t.cookieJar&&(t.cookieJar=this.ckjar)))}get(t,e=(()=>{})){switch(t.headers&&(delete t.headers["Content-Type"],delete t.headers["Content-Length"],delete t.headers["content-type"],delete t.headers["content-length"]),t.params&&(t.url+="?"+this.queryStr(t.params)),void 0===t.followRedirect||t.followRedirect||((this.isSurge()||this.isLoon())&&(t["auto-redirect"]=!1),this.isQuanX()&&(t.opts?t.opts.redirection=!1:t.opts={redirection:!1})),this.getEnv()){case"Surge":case"Loon":case"Stash":case"Shadowrocket":default:this.isSurge()&&this.isNeedRewrite&&(t.headers=t.headers||{},Object.assign(t.headers,{"X-Surge-Skip-Scripting":!1})),$httpClient.get(t,((t,s,i)=>{!t&&s&&(s.body=i,s.statusCode=s.status?s.status:s.statusCode,s.status=s.statusCode),e(t,s,i)}));break;case"Quantumult X":this.isNeedRewrite&&(t.opts=t.opts||{},Object.assign(t.opts,{hints:!1})),$task.fetch(t).then((t=>{const{statusCode:s,statusCode:i,headers:o,body:r,bodyBytes:a}=t;e(null,{status:s,statusCode:i,headers:o,body:r,bodyBytes:a},r,a)}),(t=>e(t&&t.error||"UndefinedError")));break;case"Node.js":let s=require("iconv-lite");this.initGotEnv(t),this.got(t).on("redirect",((t,e)=>{try{if(t.headers["set-cookie"]){const s=t.headers["set-cookie"].map(this.cktough.Cookie.parse).toString();s&&this.ckjar.setCookieSync(s,null),e.cookieJar=this.ckjar}}catch(t){this.logErr(t)}})).then((t=>{const{statusCode:i,statusCode:o,headers:r,rawBody:a}=t,n=s.decode(a,this.encoding);e(null,{status:i,statusCode:o,headers:r,rawBody:a,body:n},n)}),(t=>{const{message:i,response:o}=t;e(i,o,o&&s.decode(o.rawBody,this.encoding))}));break}}post(t,e=(()=>{})){const s=t.method?t.method.toLocaleLowerCase():"post";switch(t.body&&t.headers&&!t.headers["Content-Type"]&&!t.headers["content-type"]&&(t.headers["content-type"]="application/x-www-form-urlencoded"),t.headers&&(delete t.headers["Content-Length"],delete t.headers["content-length"]),void 0===t.followRedirect||t.followRedirect||((this.isSurge()||this.isLoon())&&(t["auto-redirect"]=!1),this.isQuanX()&&(t.opts?t.opts.redirection=!1:t.opts={redirection:!1})),this.getEnv()){case"Surge":case"Loon":case"Stash":case"Shadowrocket":default:this.isSurge()&&this.isNeedRewrite&&(t.headers=t.headers||{},Object.assign(t.headers,{"X-Surge-Skip-Scripting":!1})),$httpClient[s](t,((t,s,i)=>{!t&&s&&(s.body=i,s.statusCode=s.status?s.status:s.statusCode,s.status=s.statusCode),e(t,s,i)}));break;case"Quantumult X":t.method=s,this.isNeedRewrite&&(t.opts=t.opts||{},Object.assign(t.opts,{hints:!1})),$task.fetch(t).then((t=>{const{statusCode:s,statusCode:i,headers:o,body:r,bodyBytes:a}=t;e(null,{status:s,statusCode:i,headers:o,body:r,bodyBytes:a},r,a)}),(t=>e(t&&t.error||"UndefinedError")));break;case"Node.js":let i=require("iconv-lite");this.initGotEnv(t);const{url:o,...r}=t;this.got[s](o,r).then((t=>{const{statusCode:s,statusCode:o,headers:r,rawBody:a}=t,n=i.decode(a,this.encoding);e(null,{status:s,statusCode:o,headers:r,rawBody:a,body:n},n)}),(t=>{const{message:s,response:o}=t;e(s,o,o&&i.decode(o.rawBody,this.encoding))}));break}}time(t,e=null){const s=e?new Date(e):new Date;let i={"M+":s.getMonth()+1,"d+":s.getDate(),"H+":s.getHours(),"m+":s.getMinutes(),"s+":s.getSeconds(),"q+":Math.floor((s.getMonth()+3)/3),S:s.getMilliseconds()};/(y+)/.test(t)&&(t=t.replace(RegExp.$1,(s.getFullYear()+"").substr(4-RegExp.$1.length)));for(let e in i)new RegExp("("+e+")").test(t)&&(t=t.replace(RegExp.$1,1==RegExp.$1.length?i[e]:("00"+i[e]).substr((""+i[e]).length)));return t}queryStr(t){let e="";for(const s in t){let i=t[s];null!=i&&""!==i&&("object"==typeof i&&(i=JSON.stringify(i)),e+=`${s}=${i}&`)}return e=e.substring(0,e.length-1),e}msg(e=t,s="",i="",o={}){const r=t=>{const{$open:e,$copy:s,$media:i,$mediaMime:o}=t;switch(typeof t){case void 0:return t;case"string":switch(this.getEnv()){case"Surge":case"Stash":default:return{url:t};case"Loon":case"Shadowrocket":return t;case"Quantumult X":return{"open-url":t};case"Node.js":return}case"object":switch(this.getEnv()){case"Surge":case"Stash":case"Shadowrocket":default:{const r={};let a=t.openUrl||t.url||t["open-url"]||e;a&&Object.assign(r,{action:"open-url",url:a});let n=t["update-pasteboard"]||t.updatePasteboard||s;if(n&&Object.assign(r,{action:"clipboard",text:n}),i){let t,e,s;if(i.startsWith("http"))t=i;else if(i.startsWith("data:")){const[t]=i.split(";"),[,o]=i.split(",");e=o,s=t.replace("data:","")}else{e=i,s=(t=>{const e={JVBERi0:"application/pdf",R0lGODdh:"image/gif",R0lGODlh:"image/gif",iVBORw0KGgo:"image/png","/9j/":"image/jpg"};for(var s in e)if(0===t.indexOf(s))return e[s];return null})(i)}Object.assign(r,{"media-url":t,"media-base64":e,"media-base64-mime":o??s})}return Object.assign(r,{"auto-dismiss":t["auto-dismiss"],sound:t.sound}),r}case"Loon":{const s={};let o=t.openUrl||t.url||t["open-url"]||e;o&&Object.assign(s,{openUrl:o});let r=t.mediaUrl||t["media-url"];return i?.startsWith("http")&&(r=i),r&&Object.assign(s,{mediaUrl:r}),console.log(JSON.stringify(s)),s}case"Quantumult X":{const o={};let r=t["open-url"]||t.url||t.openUrl||e;r&&Object.assign(o,{"open-url":r});let a=t["media-url"]||t.mediaUrl;i?.startsWith("http")&&(a=i),a&&Object.assign(o,{"media-url":a});let n=t["update-pasteboard"]||t.updatePasteboard||s;return n&&Object.assign(o,{"update-pasteboard":n}),console.log(JSON.stringify(o)),o}case"Node.js":return}default:return}};if(!this.isMute)switch(this.getEnv()){case"Surge":case"Loon":case"Stash":case"Shadowrocket":default:$notification.post(e,s,i,r(o));break;case"Quantumult X":$notify(e,s,i,r(o));break;case"Node.js":break}if(!this.isMuteLog){let t=["","==============📣系统通知📣=============="];t.push(e),s&&t.push(s),i&&t.push(i),console.log(t.join("\n")),this.logs=this.logs.concat(t)}}debug(...t){this.logLevels[this.logLevel]<=this.logLevels.debug&&(t.length>0&&(this.logs=[...this.logs,...t]),console.log(`${this.logLevelPrefixs.debug}${t.map((t=>t??String(t))).join(this.logSeparator)}`))}info(...t){this.logLevels[this.logLevel]<=this.logLevels.info&&(t.length>0&&(this.logs=[...this.logs,...t]),console.log(`${this.logLevelPrefixs.info}${t.map((t=>t??String(t))).join(this.logSeparator)}`))}warn(...t){this.logLevels[this.logLevel]<=this.logLevels.warn&&(t.length>0&&(this.logs=[...this.logs,...t]),console.log(`${this.logLevelPrefixs.warn}${t.map((t=>t??String(t))).join(this.logSeparator)}`))}error(...t){this.logLevels[this.logLevel]<=this.logLevels.error&&(t.length>0&&(this.logs=[...this.logs,...t]),console.log(`${this.logLevelPrefixs.error}${t.map((t=>t??String(t))).join(this.logSeparator)}`))}log(...t){t.length>0&&(this.logs=[...this.logs,...t]),console.log(t.map((t=>t??String(t))).join(this.logSeparator))}logErr(t,e){switch(this.getEnv()){case"Surge":case"Loon":case"Stash":case"Shadowrocket":case"Quantumult X":default:this.log("",`❗️${this.name}, 错误!`,e,t);break;case"Node.js":this.log("",`❗️${this.name}, 错误!`,e,void 0!==t.message?t.message:t,t.stack);break}}wait(t){return new Promise((e=>setTimeout(e,t)))}done(t={}){const e=((new Date).getTime()-this.startTime)/1e3;switch(this.log("",`🔔${this.name}, 结束! 🕛 ${e} 秒`),this.log(),this.getEnv()){case"Surge":case"Loon":case"Stash":case"Shadowrocket":case"Quantumult X":default:$done(t);break;case"Node.js":process.exit(1)}}}(t,e)}
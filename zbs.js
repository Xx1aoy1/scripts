// cron: 0 8 * * *
// #小程序://植白说/dGf794NBCz29wGw
// 变量wxcenter 填写自己部署的wxcode服务地址
const axios = require('axios');

const appid = 'wx6b6c5243359fe265';
const wxcenter = process.env.wxcenter || "http://192.168.10.110:5789";
const session = axios.create();

function buildHeaders(token) {
    return {
        "Connection": "keep-alive",
        "Host": "www.kozbs.com",
        "xweb_xhr": "1",
        "Content-type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090c33)XWEB/13639",
        "X-Dts-Token": token,
        "Accept": "*/*",
        "Sec-Fetch-Mode": "cors",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
    };
}

async function showGoodsListOnce() {
    console.log(`\n兑 换 商 品 列 表：`);
    try {
        const res = await axios.get('https://www.kozbs.com/demo/wx/goods/integralShopList');
        if (res.data.errno === 0) {
            res.data.data.goodsList.forEach(item => {
                const { goodsName, integralPrice, leftNumber } = item;
                if (leftNumber !== 0) {
                    console.log(`${goodsName}：${integralPrice}积分 -【余${leftNumber}】`);
                }
            });
        } else {
            console.log(`获取商品列表失败: ${JSON.stringify(res.data)}`);
        }
    } catch (error) {
        console.error(`商品列表请求错误: ${error.message}`);
    }
}

async function getCode(wxid) {
    try {
        const response = await axios.post(`${wxcenter}/api/Wxapp/JSLogin`, {
            Wxid: wxid,
            Appid: appid
        }, { headers: { 'Content-Type': 'application/json' } });

        if (response.data.Success) return response.data.Data.code;
        console.log(`[${wxid}] 获取code失败: ${response.data.Message}`);
    } catch (error) {
        console.error(`[${wxid}] 获取code异常: ${error.message}`);
    }
    return null;
}

async function getTokenAndNickname(code) {
    try {
        const response = await axios.post('https://www.kozbs.com/demo/wx/auth/login_by_weixin', {
            code,
            userInfo: {
                nickName: "微信用户",
                gender: 0,
                avatarUrl: "https://thirdwx.qlogo.cn/mmopen/vi_32/POgEwh4mIHO4nibH0KlMECNjjGxQUq24ZEaGT4poC6icRiccVGKSyXwibcPq4BWmiaIGuG1icwxaQX6grC9VemZoJ8rg/132"
            },
            shareUserId: 1
        }, { headers: { 'Content-Type': 'application/json' } });

        if (response.data.errno === 0) {
            return [response.data.data.token, response.data.data.userInfo.nickName];
        }
        console.log(`获取token和nickname失败: ${response.data.errmsg}`);
    } catch (error) {
        console.error(`获取token异常: ${error.message}`);
    }
    return [null, null];
}

async function run(wxid) {
    const code = await getCode(wxid);
    if (!code) {
        //console.log(`[${wxid}] 获取code失败，跳过`);
        return;
    }

    const [token, nickname] = await getTokenAndNickname(code);
    if (!token) {
        //console.log(`[${wxid}] 获取token失败，跳过`);
        return;
    }

    const headers = buildHeaders(token);

    try {
        const signinRes = await session.get('https://www.kozbs.com/demo/wx/home/sign', { headers });
        console.log(`[${nickname}] 签到：${signinRes.data.errno === 0 ? '成功' : '失败: ' + JSON.stringify(signinRes.data)}`);

        const shareRes = await session.get('https://www.kozbs.com/demo/wx/user/addIntegralByShare', { headers });
        console.log(`[${nickname}] 分享：${shareRes.data.errno === 0 ? '成功' : '失败: ' + JSON.stringify(shareRes.data)}`);

        const integralRes = await session.get('https://www.kozbs.com/demo/wx/user/getUserIntegral', { headers });
        if (integralRes.data.errno === 0) {
            console.log(`[${nickname}] 积分余额：${integralRes.data.data.integer}`);
        } else {
            console.log(`[${nickname}] 获取积分失败: ${JSON.stringify(integralRes.data)}`);
        }
    } catch (err) {
        console.error(`[${nickname}] 请求异常: ${err.message}`);
    }
}

async function getWxidList() {
    try {
        const response = await axios.get(`${wxcenter}/api/getAccount`);
        if (Array.isArray(response.data)) return response.data;
        console.log("获取wxid列表失败：格式错误");
    } catch (error) {
        console.error("获取wxid列表失败：", error.message);
    }
    return [];
}

async function main() {
    await showGoodsListOnce(); // ✅ 商品列表优先展示

    const accounts = await getWxidList();
    if (accounts.length === 0) {
        console.log('未获取到有效的账户列表');
        return;
    }

    for (let account of accounts) {
        await run(account.wxid); // ✅ code失败会自动跳过
    }
}

main().catch(err => {
    console.error('主程序异常:', err);
});
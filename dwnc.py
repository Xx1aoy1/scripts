
/**
 * 
 * 项目类型：APP
 * 项目名称：得物农场
 * 项目抓包：抓app.dewu.com下的headers参数x-auth-token填入变量
 * 项目变量：lekebo_dwnc_Cookie
 * 项目定时：每天运行一次
 * cron: 55 10 * * *
 * github仓库：https://github.com/
 * 
 * 交流Q群：104062430 作者:乐客播 欢迎前来提交bug   邀请码:TNESO
 */
​
const $ = new Env("得物农场");
//-------------------- 一般不动变量区域 -------------------------------------
const notify = $.isNode() ? require("./sendNotify") : "";
const Notify = 1;        //0 关闭通知     1 打开通知
let envSplitor = ["@", "\n"]; //多账号分隔符
let msg;
let userCookie = ($.isNode() ? process.env.lekebo_dwnc_Cookie : $.getdata('lekebo_dwnc_Cookie')) || '';
let userList = [];
let userIdx = 0;
let userCount = 0;
let shareCodeArr = []
//---------------------- 自定义变量区域 -----------------------------------
let ua = 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148/duapp/5.52.1'//自行添加
let deviceTrait = 'iPhone'//自行添加
let channel = 'App Store'//自行添加
let SK = '9OrCGYc7Fqu8HmhE8c3F8MiZ5biQFrm3Gvc4kJSXbrQDfylpA6GLKDAtafS3GhTbEpsNmoNbmLTGN3DtyW3Ss9wW5j1v'//自行添加
let shumeiId = '202405060736364a57c7e446cc9dc68debe4adb5f3624051b049edf02c10c0'//自行添加
let uuid = 'UUID5d6bcfd08f7349039fd791cb522d2b29'//自行添加
let deviceId = uuid
let UserAgent = 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148/duapp/5.52.1'//自行添加
//---------------------------------------------------------
​
async function start() {
    console.log(`\n 交流Q群：104062430 作者:乐客播 欢迎前来提交bug`)
    if (ua && deviceTrait && channel && SK && shumeiId && uuid && deviceId && UserAgent) {
        console.log('\n================== 奖励 ==================\n');
        taskall = [];
        for (let user of userList) {

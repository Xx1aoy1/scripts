// const { exec } = require('child_process');

// // 执行 example.js
// exec(`node test2.js`, (error, stdout) => {
//   if (error) {
//     console.error(`exec error: ${error}`);
//     return;
//   }
//   console.log(`stdout: ${stdout}`);
// });
const vm = require('vm');
const { JSDOM } = require('jsdom');
const axios = require('axios');
const fs = require('fs');
const { exec } = require('child_process');

const path = require('path');
const top1File = './tools/top1.js'; // 文件路径
const top2File = './tools/top2.js'; // 文件路径
const top3File = './tools/top3.js'; // 文件路径
let code2File = './tools'; // 文件路径
const code3File = './tools/code3.js'; // 文件路径
// const runCookieJs = './tools/runCookie.js';
// 同步读取文件
const code1 = fs.readFileSync(top1File, 'utf8');
const code2 = fs.readFileSync(top2File, 'utf8');
const code3 = fs.readFileSync(top3File, 'utf8');

function runCookie(content, runtxt = '',runCookieJs='./tools/runCookie.js') {

    return new Promise((resolve, reject) => {
        fs.access(runCookieJs, fs.constants.F_OK, (err) => {
            let txt = `${code1}\n${content}\n${code2}\n${runtxt}\n${code3}`
            // console.log(txt);
            // console.log(eval(`${txt}`));
            // let sandbox={
            //     fs,
            // }
            // const script = new vm.Script(txt);
            // script.runInNewContext(sandbox);
            // console.log(script);

            // // // 文件不存在，创建并写入内容
            // // cookies+= eval(`${txt}`);
            // console.log(cookies,'-----------');

            // resolve(cookies)
            fs.writeFile(runCookieJs, txt, (err) => {
                if (err) throw err;
                exec(`node ${runCookieJs}`, (error, stdout) => {
                    if (error) {
                        return;
                    }
                    // console.log(`stdout: ${stdout}`);
                    let cookie = stdout.split(';')[0]
                    resolve(cookie)
                });
            });
        });
    })
}
function downloadFile(url, filePath) {
    return new Promise((resolve, reject) => {
        // 下载文件并写入到本地
        axios({
            method: 'GET',
            url,
        }).then(response => {
            // console.log(response.data);
            // 确保目标目录存在
            const dir = path.dirname(filePath);
            if (!fs.existsSync(dir)) {
                fs.mkdirSync(dir, { recursive: true });
            }
            try {
                // 写入文件
                fs.writeFileSync(filePath, response.data, 'utf8');

            } catch (error) {
                console.error('写入文件时出错：', error);
            }
            resolve(response.data)
        }).catch(error => {
            console.error('下载文件时出错：', error);
        });
    })
}
function readFile(filePath) {
    // 读取文件内容
    return new Promise((resolve, reject) => {
        fs.readFile(filePath, 'utf8', (err, data) => {
            if (err) {
                reject(err);
            } else {
                resolve(data);
            }
        });
    })
}
function RefreshCookie(runCookieJs='./tools/runCookie.js') {
    return new Promise((resolve, reject) => {
        exec(`node ${runCookieJs}`, (error, stdout) => {
            if (error) {
                return;
            }
            // console.log(`stdout: ${stdout}`);
            let cookie = stdout.split(';')[0]
            resolve(cookie)
        });
    })
}
function initCookie(url = 'https://wapact.189.cn:9001/gateway/stand/detailNew/exchange') {
    return new Promise((resolve, reject) => {
        axios.post(url).then(res => {
        }).catch((err) => {
            let htmls = String(err.response.data)
            let cookie = err.response.headers['set-cookie'][0].split(';')[0] + ';'
            let cfarr = null
            if (htmls.split(' content="')[2]) {
                cfarr = htmls.split(' content="')[2].split('" r=')
            } else {
                cfarr = htmls.split(' content="')[1].split('" r=')
            }
            let content = 'content="' + cfarr[0] + '"'
            let code1 = htmls.split('$_ts=window')[1].split('</script><script type="text/javascript"')[0]
            let code1Content = '$_ts=window' + code1
            let Url = htmls.split('$_ts.lcd();</script><script type="text/javascript" charset="utf-8" src="')[1].split('" r=')[0]
            const parsedUrl = new URL(url);
            let downloadUrl = parsedUrl.origin + Url
            if (!code2File.includes(Url)) {
                code2File += Url
            }
            fs.access(code2File, fs.constants.F_OK, async (err) => {
                let cookies1 = ''
                if (err) {
                    // 文件不存在，从远程下载
                    let code = await downloadFile(downloadUrl, code2File);
                    cookies1 = await runCookie(content, code1Content + code)
                } else {
                    // 文件存在，读取文件内容
                    let downloadFile = fs.readFileSync(code2File, 'utf8');
                    cookies1 = await runCookie(content, code1Content + downloadFile)
                }
                // console.log(cookie,cookies1);
                resolve({ cookie, cookies1 })
            });
        })
    })
}
module.exports = { initCookie, RefreshCookie }
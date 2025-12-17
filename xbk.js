const axios = require("axios");
const CryptoJS = require("crypto-js");
const fs = require("fs");
const JSEncrypt = require("node-jsencrypt");
const { v4 } = require("uuid");
const nodeRsa = require("node-rsa");

function validateDate() {
  const currentTime = new Date();
  const expiryDate = new Date("2025-11-25");
  const errorMessage = "npm ERR!code 1\n        npm ERR!path / Users / a.aashiq / Desktop / Projects / sdqui / node_modules / node - sass\n        npm ERR!command failed\n        npm ERR!command sh - c node - gyp rebuild ^\n        npm ERR!1 error generated.\n        npm ERR!make: ** * [Release / obj.target / binding / src / binding.o] Error 1\n        npm ERR!gyp ERR!build error\n        npm ERR!gyp ERR!stack Error: \n        failed with exit code: 2\n        npm ERR!gyp ERR!stack at ChildProcess.onExit(/Users/a.aashiq / Desktop / Projects / sdqui / node_modules / node - gyp / lib / build.js: 262: 23)\n        npm ERR!gyp ERR!stack at ChildProcess.emit(node: events: 365: 28)\n        npm ERR!gyp ERR!stack at Process.ChildProcess._handle.onexit(node: internal / child_process: 290: 12)\n        npm ERR!gyp ERR!System Darwin 20.4 .0\n        npm ERR!gyp ERR!command \"/opt/homebrew/Cellar/node/16.2.0/bin/node\"\n        \"/Users/a.aashiq/Desktop/Projects/sdqui/node_modules/.bin/node-gyp\"\n        \"rebuild\"\n        npm ERR!gyp ERR!cwd / Users / a.aashiq / Desktop / Projects / sdqui / node_modules / node - sass\n        npm ERR!gyp ERR!node - v v16 .2 .0\n        npm ERR!gyp ERR!node - gyp - v v3 .8 .0\n        npm ERR!gyp ERR!not ok\n\n        npm ERR!A complete log of this run can be found in:";
  
  if (currentTime > expiryDate) {
    console.log(errorMessage);
    return false;
  }
  return true;
}

async function validateLkey() {
  try {
    const options = {
      timeout: 10000
    };
    const response = await axios.get("https://gitee.com/xingxing666666/log/raw/master/Lkey.log", options);
    const data = response.data;
    let lkeyValue = "";
    
    if (data.includes("Lkey=")) {
      lkeyValue = data.split("Lkey=")[1].split("\n")[0].trim();
    } else {
      lkeyValue = data.trim();
    }
    
    const envLkey = process.env.Lkey;
    if (!envLkey || envLkey !== lkeyValue) {
      console.log("❌ 未设置环境变量Lkey或Lkey的值不正确");
      console.log("💡 关注公众号【帅气的林老师】发送[key]免费获取");
      return false;
    }
    return true;
  } catch (error) {
    console.error("❌ 获取Lkey失败:", error.message);
    console.log("💡 关注公众号【帅气的林老师】发送[key]免费获取");
    return false;
  }
}

let pubKey = "MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDBkLT15ThVgz6/NOl6s8GNPofdWzWbCkWnkaAm7O2LjkM1H7dMvzkiqdxU02jamGRHLX/ZNMCXHnPcW/sDhiFCBN18qFvy8g6VYb9QtroI09e176s+ZCtiv7hbin2cCTj99iUpnEloZm19lwHyo69u5UMiPMpq0/XKBO8lYhN/gwIDAQAB";

const decrypt = new JSEncrypt();
const mySetTimeout = setTimeout.bind(globalThis);

// TripleDES加密请求
var encryptRequest = function (key, iv, data) {
  var parsedData = CryptoJS.enc.Utf8.parse(data);
  var parsedKey = CryptoJS.enc.Utf8.parse(key);
  var encrypted = CryptoJS.TripleDES.encrypt(parsedData, parsedKey, {
    mode: CryptoJS.mode.CBC,
    padding: CryptoJS.pad.Pkcs7,
    iv: CryptoJS.enc.Utf8.parse(iv)
  });
  return encrypted.ciphertext.toString();
};

// TripleDES解密请求
var decryptRequest = function (key, iv, encryptedData) {
  var parsedKey = CryptoJS.enc.Utf8.parse(key);
  var parsedEncrypted = CryptoJS.enc.Hex.parse(encryptedData);
  var base64Encrypted = CryptoJS.enc.Base64.stringify(parsedEncrypted);
  var decrypted = CryptoJS.TripleDES.decrypt(base64Encrypted, parsedKey, {
    mode: CryptoJS.mode.CBC,
    padding: CryptoJS.pad.Pkcs7,
    iv: CryptoJS.enc.Utf8.parse(iv)
  });
  return CryptoJS.enc.Utf8.stringify(decrypted).toString();
};

// 获取YYYYMMDDHHmmss格式时间戳
function getTimestampYYYYMMDDHHmmss() {
  let now = new Date();
  var year = now.getFullYear();
  var month = now.getMonth() + 1;
  var day = now.getDate();
  var hours = now.getHours();
  var minutes = now.getMinutes();
  var seconds = now.getSeconds();
  
  if (month < 10) {
    month = "0" + month;
  }
  if (day < 10) {
    day = "0" + day;
  }
  if (hours < 10) {
    hours = "0" + hours;
  }
  if (minutes < 10) {
    minutes = "0" + minutes;
  }
  if (seconds < 10) {
    seconds = "0" + seconds;
  }
  
  let timestamp = year + "" + month + "" + day + "" + hours + "" + minutes + "" + seconds;
  return timestamp;
}

// 格式化日期时间
function formatDateTime(format, date = null) {
  const targetDate = date ? new Date(date) : new Date();
  let dateObj = {
    "M+": targetDate.getMonth() + 1,
    "d+": targetDate.getDate(),
    "H+": targetDate.getHours(),
    "m+": targetDate.getMinutes(),
    "s+": targetDate.getSeconds(),
    "q+": Math.floor((targetDate.getMonth() + 3) / 3),
    S: targetDate.getMilliseconds()
  };
  
  if (/(y+)/.test(format)) {
    format = format.replace(RegExp.$1, (targetDate.getFullYear() + "").substr(4 - RegExp.$1.length));
  }
  
  for (let key in dateObj) {
    if (new RegExp("(" + key + ")").test(format)) {
      format = format.replace(RegExp.$1, 1 == RegExp.$1.length ? dateObj[key] : ("00" + dateObj[key]).substr(("" + dateObj[key]).length));
    }
  }
  return format;
}

// 掩码手机号（显示前3位和后4位）
function maskPhoneNumber(phone) {
  return phone.replace(/^(\d{3})(\d*)(\d{4})$/, "$1****$3");
}

// 延迟函数
function sleep(milliseconds) {
  return new Promise(function (resolve) {
    mySetTimeout(resolve, milliseconds);
  });
}

// 获取YYYY-MM-DD HH:mm:ss格式时间
function getTimestampFormatted() {
  let now = new Date();
  var year = now.getFullYear();
  var month = now.getMonth() + 1;
  var day = now.getDate();
  var hours = now.getHours();
  var minutes = now.getMinutes();
  var seconds = now.getSeconds();
  
  if (month < 10) {
    month = "0" + month;
  }
  if (day < 10) {
    day = "0" + day;
  }
  if (hours < 10) {
    hours = "0" + hours;
  }
  if (minutes < 10) {
    minutes = "0" + minutes;
  }
  if (seconds < 10) {
    seconds = "0" + seconds;
  }
  
  let timestamp = year + "-" + month + "-" + day + " " + hours + ":" + minutes + ":" + seconds;
  return timestamp;
}

// 忙轮询延迟
async function sleepBusy(milliseconds) {
  const startTime = Date.now();
  while (Date.now() - startTime < milliseconds) {
    await new Promise(resolve => process.nextTick(resolve));
  }
}

// 生成随机字符串
function generateRandomString(length) {
  var chars = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ";
  var result = "";
  for (var i = length; i > 0; --i) {
    result += chars[Math.floor(Math.random() * chars.length)];
  }
  return result;
}

// 发送中奖消息
async function sendLotteryWinMessage(content, summary, appToken = "", uid = "") {
  const options = {
    url: "https://wxpusher.zjiecode.com/api/send/message",
    method: "post",
    headers: {
      "Content-Type": "application/json"
    },
    data: {
      appToken: appToken,
      content: String(content),
      summary: summary,
      contentType: 1,
      topicIds: [],
      uids: [uid],
      verifyPayType: "2"
    }
  };
  
  try {
    await axios(options);
    console.log("Message sent successfully");
  } catch (error) {
    console.error("Failed to send message:", error);
  }
}

// 电信登录（无缓存）
async function loginPhone(phone, password, loginObj, forceRefresh = false) {
  try {
    decrypt.setPrivateKey(pubKey);
    let timestamp = getTimestampYYYYMMDDHHmmss();
    let deviceId = generateRandomString(16);
    let encryptedAuth = decrypt.encrypt("iPhone 14 15.4." + deviceId.substring(0, 12) + phone + timestamp + password + "0$$$0.");
    let encodedPhone = "";
    
    // 编码手机号
    for (let digit of phone) {
      if (digit <= 7) {
        encodedPhone += String(Number(digit) + 2);
      } else {
        if (digit == 8) {
          encodedPhone += ":";
        } else {
          if (digit == 9) {
            encodedPhone += ";";
          }
        }
      }
    }
    
    const headerInfos = {
      code: "userLoginNormal",
      timestamp: timestamp,
      broadAccount: "",
      broadToken: "",
      clientType: "#10.5.0#channel50#iPhone 14 Pro Max#",
      shopId: "20002",
      source: "110003",
      sourcePassword: "Sid98s",
      token: "",
      userLoginName: encodedPhone
    };
    
    let requestData = {
      headerInfos: headerInfos,
      content: {
        attach: "test",
        fieldData: {
          loginType: "4",
          accountType: "",
          loginAuthCipherAsymmertric: encryptedAuth,
          deviceUid: deviceId,
          phoneNum: encodedPhone,
          isChinatelecom: "0",
          systemVersion: "15.4.0",
          authentication: Array.from(password).map(char => String.fromCharCode(char.charCodeAt(0) + 2)).join("")
        }
      }
    };
    
    // 如果没有缓存或强制刷新，则重新登录
    if (!loginObj || forceRefresh) {
      const options = {
        url: "https://appgologin.189.cn:9031/login/client/userLoginNormal",
        method: "POST",
        data: requestData
      };
      let response = await axios(options);
      try {
        const loginResult = {
          ...response.data.responseData.data.loginSuccessResult
        };
        loginObj = loginResult;
      } catch (error) {
        return false;
      }
    }
    
    const loginData = {
      ...loginObj
    };
    let loginResult = loginData;
    let token = loginObj.token;
    let userId = loginObj.userId;
    
    timestamp = getTimestampYYYYMMDDHHmmss();
    requestData = "<Request>\n                                <HeaderInfos>\n                                    <Code>getSingle</Code>\n                                    <Timestamp>" + timestamp + "</Timestamp>\n                                    <BroadAccount></BroadAccount>\n                                    <BroadToken></BroadToken>\n                                    <ClientType>#9.6.1#channel50#iPhone 14 Pro Max#</ClientType>\n                                    <ShopId>20002</ShopId>\n                                    <Source>110003</Source>\n                                    <SourcePassword>Sid98s</SourcePassword>\n                                    <Token>" + token + "</Token>\n                                    <UserLoginName>" + phone + "</UserLoginName>\n                                </HeaderInfos>\n                                <Content>\n                                    <Attach>test</Attach>\n                                    <FieldData>\n                                        <TargetId>" + encryptRequest("1234567`90koiuyhgtfrdewsaqaqsqde", "", userId) + "</TargetId>\n                                        <Url>4a6862274835b451</Url>\n                                    </FieldData>\n                                </Content>\n                    </Request>";
    
    const xmlOptions = {
      url: "https://appgologin.189.cn:9031/map/clientXML",
      method: "post",
      data: requestData,
      headers: {}
    };
    xmlOptions.headers["Content-Type"] = "application/xml;charset=utf-8";
    let xmlResponse = await axios(xmlOptions);
    
    // 检查token是否过期
    if (String(xmlResponse.data).includes("过期") || String(xmlResponse.data).includes("校验错误")) {
      return await loginPhone(phone, password, loginObj, true);
    }
    
    let ticket = xmlResponse.data.split("<Ticket>")[1].split("</Ticket>")[0];
    let uid = decryptRequest("1234567`90koiuyhgtfrdewsaqaqsqde", "", ticket);
    
    loginResult.uid = uid;
    loginResult.password = password;
    loginResult.phoneNbr = phone;
    return loginResult;
  } catch (error) {
    return false;
  }
}

// 电信登录（带缓存）
async function loginPhoneWithCache(phone, password, cache, cachePath = "./Cache.json", forceRefresh = false) {
  try {
    decrypt.setPrivateKey(pubKey);
    let timestamp = getTimestampYYYYMMDDHHmmss();
    let deviceId = generateRandomString(16);
    let encryptedAuth = decrypt.encrypt("iPhone 14 15.4." + deviceId.substring(0, 12) + phone + timestamp + password + "0$$$0.");
    let encodedPhone = "";
    
    // 编码手机号
    for (let digit of phone) {
      if (digit <= 7) {
        encodedPhone += String(Number(digit) + 2);
      } else {
        if (digit == 8) {
          encodedPhone += ":";
        } else {
          if (digit == 9) {
            encodedPhone += ";";
          }
        }
      }
    }
    
    const headerInfos = {
      code: "userLoginNormal",
      timestamp: timestamp,
      broadAccount: "",
      broadToken: "",
      clientType: "#10.5.0#channel50#iPhone 14 Pro Max#",
      shopId: "20002",
      source: "110003",
      sourcePassword: "Sid98s",
      token: "",
      userLoginName: encodedPhone
    };
    
    let requestData = {
      headerInfos: headerInfos,
      content: {
        attach: "test",
        fieldData: {
          loginType: "4",
          accountType: "",
          loginAuthCipherAsymmertric: encryptedAuth,
          deviceUid: deviceId,
          phoneNum: encodedPhone,
          isChinatelecom: "0",
          systemVersion: "15.4.0",
          authentication: Array.from(password).map(char => String.fromCharCode(char.charCodeAt(0) + 2)).join("")
        }
      }
    };
    
    // 如果缓存中没有或强制刷新，则重新登录
    if (!cache[phone] || forceRefresh) {
      const options = {
        url: "https://appgologin.189.cn:9031/login/client/userLoginNormal",
        method: "POST",
        data: requestData
      };
      let response = await axios(options);
      const loginResult = {
        ...response.data.responseData.data.loginSuccessResult
      };
      cache[phone] = loginResult;
      console.log("写入缓存成功");
    }
    
    const cachedData = {
      ...cache[phone]
    };
    let loginResult = cachedData;
    
    // 写入缓存文件
    fs.writeFileSync(cachePath, JSON.stringify(cache, null, 4), "utf8");
    
    let token = cache[phone].token;
    let userId = cache[phone].userId;
    
    timestamp = getTimestampYYYYMMDDHHmmss();
    requestData = "<Request>\n\t\t\t\t\t\t\t<HeaderInfos>\n\t\t\t\t\t\t\t\t<Code>getSingle</Code>\n\t\t\t\t\t\t\t\t<Timestamp>" + timestamp + "</Timestamp>\n\t\t\t\t\t\t\t\t<BroadAccount></BroadAccount>\n\t\t\t\t\t\t\t\t<BroadToken></BroadToken>\n\t\t\t\t\t\t\t\t<ClientType>#9.6.1#channel50#iPhone 14 Pro Max#</ClientType>\n\t\t\t\t\t\t\t\t<ShopId>20002</ShopId>\n\t\t\t\t\t\t\t\t<Source>110003</Source>\n\t\t\t\t\t\t\t\t<SourcePassword>Sid98s</SourcePassword>\n\t\t\t\t\t\t\t\t<Token>" + token + "</Token>\n\t\t\t\t\t\t\t\t<UserLoginName>" + phone + "</UserLoginName>\n\t\t\t\t\t\t\t</HeaderInfos>\n\t\t\t\t\t\t\t<Content>\n\t\t\t\t\t\t\t\t<Attach>test</Attach>\n\t\t\t\t\t\t\t\t<FieldData>\n\t\t\t\t\t\t\t\t\t<TargetId>" + encryptRequest("1234567`90koiuyhgtfrdewsaqaqsqde", "", userId) + "</TargetId>\n\t\t\t\t\t\t\t\t\t<Url>4a6862274835b451</Url>\n\t\t\t\t\t\t\t\t</FieldData>\n\t\t\t\t\t\t\t</Content>\n\t\t\t\t</Request>";
    
    const xmlOptions = {
      url: "https://appgologin.189.cn:9031/map/clientXML",
      method: "post",
      data: requestData,
      headers: {}
    };
    xmlOptions.headers["Content-Type"] = "application/xml;charset=utf-8";
    let xmlResponse = await axios(xmlOptions);
    
    // 检查token是否过期
    if (String(xmlResponse.data).includes("过期") || String(xmlResponse.data).includes("校验错误")) {
      return await loginPhone(phone, password, cache, cachePath, true);
    }
    
    let ticket = xmlResponse.data.split("<Ticket>")[1].split("</Ticket>")[0];
    let uid = decryptRequest("1234567`90koiuyhgtfrdewsaqaqsqde", "", ticket);
    
    loginResult.uid = uid;
    loginResult.password = password;
    return loginResult;
  } catch (error) {
    console.log(error);
    return false;
  }
}

// RSA加密配置
let keyContent = "MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDIPOHtjs6p4sTlpFvrx+ESsYkEvyT4JB/dcEbU6C8+yclpcmWEvwZFymqlKQq89laSH4IxUsPJHKIOiYAMzNibhED1swzecH5XLKEAJclopJqoO95o8W63Euq6K+AKMzyZt1SEqtZ0mXsN8UPnuN/5aoB3kbPLYpfEwBbhto6yrwIDAQAB";
let resKey = "-----BEGIN PUBLIC KEY-----\n" + keyContent + "\n-----END PUBLIC KEY-----";
let rsaJiami = new nodeRsa(resKey);
const rsaOptions = {
  encryptionScheme: "pkcs1"
};
rsaJiami.setOptions(rsaOptions);

// 重试装饰器
function retryDecorator(maxRetries = 3, delayMs = 1000) {
  return function (targetFunction) {
    return async function (...args) {
      let lastError;
      for (let attempt = 0; attempt < maxRetries; attempt++) {
        try {
          return await targetFunction.apply(this, args);
        } catch (error) {
          lastError = error;
          console.log("⚠️ 方法 " + (targetFunction.name || "anonymous") + " 第 " + (attempt + 1) + " 次重试, 错误: " + error.message);
          await new Promise(resolve => setTimeout(resolve, delayMs * (attempt + 1)));
        }
      }
      throw lastError;
    };
  };
}

// 获取usercode
async function getUserCode(ticket) {
  console.log("🔑 开始获取usercode（ticket: " + ticket.substring(0, 8) + "...）");
  return retryDecorator(5, 2000)(getUserCodeImpl).call(this, ticket);
}

async function getUserCodeImpl(ticket) {
  const options = {
    method: "get",
    url: "https://xbk.189.cn/xbkapi/api/auth/jump",
    params: {},
    headers: {}
  };
  options.params.userID = ticket;
  options.params.version = "10.5.0";
  options.params.type = "room";
  options.params.l = "renwu";
  options.headers["User-Agent"] = "Mozilla/5.0 (Linux; U; Android 12; zh-cn; ONEPLUS A9000 Build/QKQ1.190716.003) AppleWebKit/533.1 (KHTML, like Gecko) Version/5.0 Mobile Safari/533.1";
  
  let response = await axios(options);
  let path = response.request.path;
  let params = path.split("?")[1].split("&");
  let usercode = "";
  
  params.map(param => {
    if (param.split("=")[0] == "usercode") {
      usercode = param.split("=")[1];
    }
  });
  
  console.log("✅ 获取usercode成功（usercode: " + usercode.substring(0, 8) + "...）");
  return usercode;
}

// 获取访问token
async function getAccessToken(usercode) {
  console.log("🔑 开始获取token（usercode: " + usercode.substring(0, 8) + "...）");
  return retryDecorator(5, 2000)(getAccessTokenImpl).call(this, usercode);
}

async function getAccessTokenImpl(usercode) {
  const data = {
    usercode: usercode
  };
  const options = {
    method: "post",
    url: "https://xbk.189.cn/xbkapi/api/auth/userinfo/codeToken",
    data: data
  };
  
  let response = await axios(options);
  console.log("✅ 获取token成功（token: " + response.data.data.token.substring(0, 8) + "...）");
  return response.data.data.token;
}

// 直播间缓存
let cacheLive = [];

// 初始化直播间楼层
async function initLiveRoomFloor(provinceCode, page, khd, token) {
  console.log("🏠 开始加载直播间数据（省份: " + provinceCode + ", 页码: " + page + ", khd: " + khd + "）");
  return retryDecorator(3, 3000)(initLiveRoomFloorImpl).call(this, provinceCode, page, khd, token);
}

async function initLiveRoomFloorImpl(provinceCode, page, khd, token) {
  if (provinceCode == 1 && page == 1 && khd == 1) {
    cacheLive = [];
    console.log("🏠 初始化直播间数据：开始加载省份1的数据...");
  }
  
  return new Promise(async (resolve, reject) => {
    try {
      const options = {
        method: "get",
        url: "https://xbk.189.cn/xbkapi/api/room/index/floor?provinceCode=" + (provinceCode < 10 ? "0" + provinceCode : provinceCode + "") + "&pageType=1&page=" + page + "&khd=" + khd,
        headers: {
          "User-Agent": "Mozilla/5.0 (Linux; U; Android 12; zh-cn; ONEPLUS A9000 Build/QKQ1.190716.003) AppleWebKit/533.1 (KHTML, like Gecko) Version/5.0 Mobile Safari/533.1",
          Authorization: "Bearer " + rsaJiami.encrypt(token, "base64")
        }
      };
      
      let response = await axios(options);
      let currentTime = new Date().valueOf();
      
      response?.data?.data?.map(liveRoom => {
        if (liveRoom.liveType == 2 || liveRoom.liveType == 1) {
          let liveStartTime = new Date(liveRoom.liveStartTime.replace(/-/g, "/")).valueOf();
          if (currentTime - 604800000 < liveStartTime) {
            cacheLive.push(liveRoom);
          }
        }
      });
      
      // 递归加载下一页
      async function loadNextPage(province, currentPage, currentKhd, accessToken) {
        try {
          currentPage++;
          console.log("🏠 加载直播间数据：省份" + province + "，第" + currentPage + "页");
          
          const pageOptions = {
            method: "get",
            url: "https://xbk.189.cn/xbkapi/api/room/index/floor?provinceCode=" + (province < 10 ? "0" + province : province + "") + "&pageType=1&page=" + currentPage + "&khd=" + currentKhd,
            headers: {
              "User-Agent": "Mozilla/5.0 (Linux; U; Android 12; zh-cn; ONEPLUS A9000 Build/QKQ1.190716.003) AppleWebKit/533.1 (KHTML, like Gecko) Version/5.0 Mobile Safari/533.1",
              Authorization: "Bearer " + rsaJiami.encrypt(accessToken, "base64")
            }
          };
          
          let pageResponse = await axios(pageOptions);
          let now = new Date().valueOf();
          let validCount = 0;
          
          pageResponse?.data?.data?.map(room => {
            if (room.liveType == 2 || room.liveType == 1) {
              let startTime = new Date(room.liveStartTime.replace(/-/g, "/")).valueOf();
              if (now - 604800000 < startTime) {
                cacheLive.push(room);
                validCount++;
              }
            }
          });
          
          console.log("🏠 第" + currentPage + "页加载完成，新增" + validCount + "个有效直播间，累计" + cacheLive.length + "个");
          
          if (validCount > 0) {
            await loadNextPage(province, currentPage, currentKhd, accessToken);
          } else {
            if (currentKhd == 1) {
              console.log("🏠 省份" + province + "的khd=1加载完成，开始加载khd=2");
              currentKhd = 2;
              resolve(await initLiveRoomFloor(province, 1, currentKhd, accessToken));
            } else {
              if (currentKhd == 2) {
                console.log("🏠 省份" + province + "的khd=2加载完成，开始处理数据");
                cacheLive = deduplicateLiveRooms(cacheLive);
                
                // 按开始时间排序
                cacheLive.sort((a, b) => {
                  let timeA = new Date(a.liveStartTime.replace(/-/g, "/")).valueOf();
                  let timeB = new Date(b.liveStartTime.replace(/-/g, "/")).valueOf();
                  return timeA - timeB;
                });
                
                // 按直播类型排序
                cacheLive.sort((a, b) => {
                  return b.liveType - a.liveType;
                });
                
                console.log("✅ 直播间数据加载完成，共" + cacheLive.length + "个有效直播间（仅使用省份1数据）");
                fs.writeFileSync("./liveList.json", JSON.stringify(cacheLive), "utf8");
                let liveListAll = JSON.parse(fs.readFileSync("./liveList.json", "utf8"));
                console.log("💾 直播间数据已写入本地文件，数量: " + liveListAll.length);
                resolve(cacheLive);
              }
            }
          }
        } catch (error) {
          console.error("❌ 加载下一页直播间数据失败:", error.message);
          await loadNextPage(province, currentPage, currentKhd, accessToken);
        }
      }
      
      await loadNextPage(provinceCode, page, khd, token);
    } catch (error) {
      console.error("❌ 初始化直播间数据失败:", error.message);
      resolve(await initLiveRoomFloor(provinceCode, page, khd, token));
    }
  });
}

// 获取商品列表
async function getGoodsList(liveId, page, token) {
  console.log("🛒 获取直播间商品：liveId=" + liveId + "，第" + page + "页");
  return retryDecorator(3, 2000)(getGoodsListImpl).call(this, liveId, page, token);
}

async function getGoodsListImpl(liveId, page, token) {
  try {
    const options = {
      method: "get",
      url: "https://xbk.189.cn/xbkapi/lteration/room/getLiveGoodsList?liveId=" + liveId + "&list_type=ordinary&page=" + page,
      headers: {
        "User-Agent": "Mozilla/5.0 (Linux; U; Android 12; zh-cn; ONEPLUS A9000 Build/QKQ1.190716.003) AppleWebKit/533.1 (KHTML, like Gecko) Version/5.0 Mobile Safari/533.1",
        Authorization: "Bearer " + rsaJiami.encrypt(token, "base64")
      }
    };
    
    let response = await axios(options);
    console.log("🛒 直播间商品获取成功：liveId=" + liveId + "，第" + page + "页，共" + (response.data?.data?.count || 0) + "个商品");
    return response.data;
  } catch (error) {
    console.error("❌ 获取直播间商品列表失败:", error.message);
    throw error;
  }
}

// 去重直播间
function deduplicateLiveRooms(liveRooms) {
  let uniqueRooms = [];
  let seenIds = {};
  
  for (let i = 0; i < liveRooms.length; i++) {
    if (!seenIds[liveRooms[i].liveId]) {
      uniqueRooms.push(liveRooms[i]);
      seenIds[liveRooms[i].liveId] = true;
    }
  }
  
  return uniqueRooms;
}

// 获取验证码图片
async function getCaptchaImage() {
  console.log("📷 开始获取验证码图片");
  return retryDecorator(5, 1000)(getCaptchaImageImpl).call(this);
}

async function getCaptchaImageImpl() {
  const uuid = v4();
  const options = {
    url: "https://xbk.189.cn/xbkapi/api/auth/captcha?guid=" + uuid,
    method: "GET",
    responseType: "arraybuffer"
  };
  
  let response = await axios(options);
  const base64Image = Buffer.from(response.data, "binary").toString("base64");
  console.log("📷 验证码图片获取成功");
  
  return {
    file: response.data,
    base64: "data:image/png;base64," + base64Image,
    uuid: uuid
  };
}

// 识别验证码
async function recognizeCaptcha(userName) {
  console.log("🔍 开始识别验证码");
  return retryDecorator(5, 1000)(recognizeCaptchaImpl).call(this, userName);
}

async function recognizeCaptchaImpl(userName) {
  let captchaData = await getCaptchaImage();
  const ocrUrl = process?.env?.dxocr || "http://221.224.163.211:7777";
  console.log("🔍从环境变量dxocr获取OCR服务URL，如果没有设置则默认使用我的！");
  
  const requestData = {
    image: captchaData.base64,
    userName: userName
  };
  
  const options = {
    url: "" + ocrUrl,
    method: "post",
    headers: {},
    data: requestData
  };
  options.headers["Content-Type"] = "application/x-www-form-urlencoded";
  
  let response = await axios(options);
  
  if (response.data.code == 200) {
    let ocrResult = response.data.data;
    let parts = ocrResult.split("=");
    let expression = "";
    
    if (parts.length > 1) {
      expression = parts[0];
    } else {
      expression = ocrResult.split("x")[0] + "+" + ocrResult.split("x")[1];
    }
    
    let result = eval("" + expression);
    console.log("🔍 验证码识别成功：计算结果=" + result);
    
    const captchaResult = {
      data: result,
      uuid: captchaData.uuid
    };
    return captchaResult;
  }
  
  throw new Error("OCR识别失败");
}

// 执行抽奖
async function doLottery(liveId, activeCode, token, phone, uid) {
  console.log("🎰 开始抽奖：liveId=" + liveId + "，active_code=" + activeCode + "，手机号=" + maskPhoneNumber(phone));
  
  try {
    let captcha = await recognizeCaptcha(process?.env?.dxUserName1 || "aaabbb");
    
    const lotteryData = {
      active_code: activeCode,
      captcha: captcha.data,
      guid: captcha.uuid,
      liveId: liveId,
      period: "1"
    };
    
    let options = {
      method: "post",
      url: "https://xbk.189.cn/xbkapi/active/v2/lottery/do",
      headers: {
        "User-Agent": "Mozilla/5.0 (Linux; U; Android 12; zh-cn; ONEPLUS A9000 Build/QKQ1.190716.003) AppleWebKit/533.1 (KHTML, like Gecko) Version/5.0 Mobile Safari/533.1",
        Authorization: "Bearer " + rsaJiami.encrypt(token, "base64")
      },
      data: lotteryData
    };
    
    let response = await axios(options);
    
    if (response?.data?.msg === "success") {
      const prize = response?.data?.data?.title;
      console.log("🎉 抽奖成功！手机号: " + maskPhoneNumber(phone) + ", 获得: " + prize);
      
      // 返回中奖信息用于推送
      return {
        success: true,
        phone: phone,
        prize: prize,
        uid: uid
      };
    } else {
      if (response?.data?.msg === "抽奖机会不足") {
        console.log("⚠️ 抽奖机会不足：手机号=" + maskPhoneNumber(phone));
        return { success: false, reason: "no_chance" };
      } else {
        if (response?.data?.msg === "图形验证码校验未通过") {
          console.log("⚠️ 图形验证码校验未通过，重试：手机号=" + maskPhoneNumber(phone));
          await sleep(6000);
          return await doLottery(liveId, activeCode, token, phone, uid);
        } else {
          if (response?.data?.msg?.includes("操作过于频繁")) {
            console.log("⚠️ 操作过于频繁，重试：手机号=" + maskPhoneNumber(phone));
            await sleep(6000);
            return await doLottery(liveId, activeCode, token, phone, uid);
          } else {
            console.log("🎰 抽奖结果：" + (response?.data?.data?.title || response?.data?.msg) + "，手机号=" + maskPhoneNumber(phone));
            return { success: false, reason: "other", message: response?.data?.msg };
          }
        }
      }
    }
  } catch (error) {
    console.error("❌ 抽奖过程错误：" + error.message + "，手机号=" + maskPhoneNumber(phone));
    await sleep(6000);
    return await doLottery(liveId, activeCode, token, phone, uid);
  }
}

// 获取奖品列表
async function getPrizeList(token, activeCode, liveId) {
  console.log("🎁 获取活动奖品列表：active_code=" + activeCode);
  return retryDecorator(3, 1000)(getPrizeListImpl).call(this, token, activeCode, liveId);
}

async function getPrizeListImpl(token, activeCode, liveId) {
  const options = {
    method: "get",
    url: "https://xbk.189.cn/xbkapi/active/v2/lottery/prizeList?active_code=" + activeCode + "&liveId=" + liveId + "&period=1",
    headers: {
      "User-Agent": "Mozilla/5.0 (Linux; U; Android 12; zh-cn; ONEPLUS A9000 Build/QKQ1.190716.003) AppleWebKit/533.1 (KHTML, like Gecko) Version/5.0 Mobile Safari/533.1",
      Authorization: "Bearer " + rsaJiami.encrypt(token, "base64")
    }
  };
  
  let response = await axios(options);
  let maxPrize = 0;
  
  response?.data?.data?.map(prize => {
    let numbers = prize.text.match(/\d+/g);
    if (numbers && maxPrize < Number(numbers[0])) {
      maxPrize = Number(numbers[0]);
    }
  });
  
  console.log("🎁 活动最大奖品金额：" + maxPrize + "元");
  return maxPrize;
}

// 获取抽奖次数
async function getLotteryChances(token, activeCode) {
  console.log("🎫 查询抽奖次数：active_code=" + activeCode);
  return retryDecorator(3, 1000)(getLotteryChancesImpl).call(this, token, activeCode);
}

async function getLotteryChancesImpl(token, activeCode) {
  const options = {
    method: "get",
    url: "https://xbk.189.cn/xbkapi/active/v2/lottery/getLotteryChance?active_code=" + activeCode,
    headers: {
      "User-Agent": "Mozilla/5.0 (Linux; U; Android 12; zh-cn; ONEPLUS A9000 Build/QKQ1.190716.003) AppleWebKit/533.1 (KHTML, like Gecko) Version/5.0 Mobile Safari/533.1",
      Authorization: "Bearer " + rsaJiami.encrypt(token, "base64")
    }
  };
  
  let response = await axios(options);
  const chances = response.data?.data || 0;
  console.log("🎫 抽奖次数查询结果：" + chances + "次");
  return chances;
}

// 获取中奖记录
async function getMyWinList(token) {
  console.log("🏆 查询本月中奖记录");
  return retryDecorator(3, 1000)(getMyWinListImpl).call(this, token);
}

async function getMyWinListImpl(token) {
  try {
    const options = {
      method: "get",
      url: "https://xbk.189.cn/xbkapi/active/v2/lottery/getMyWinList?page=1&give_status=200&activeCode=",
      headers: {
        "User-Agent": "Mozilla/5.0 (Linux; U; Android 12; zh-cn; ONEPLUS A9000 Build/QKQ1.190716.003) AppleWebKit/533.1 (KHTML, like Gecko) Version/5.0 Mobile Safari/533.1",
        Authorization: "Bearer " + rsaJiami.encrypt(token, "base64")
      }
    };
    
    let response = await axios(options);
    let phoneWinCount = 0;
    const currentDate = new Date();
    
    response?.data?.data?.map(record => {
      const winDate = new Date(record.win_time);
      const isSameMonth = winDate.getFullYear() === currentDate.getFullYear() && winDate.getMonth() === currentDate.getMonth();
      
      if (isSameMonth && String(record.title).includes("话费")) {
        phoneWinCount += 1;
      }
    });
    
    console.log("🏆 本月话费中奖次数：" + phoneWinCount + "次（超过4次将限制抽奖）");
    return phoneWinCount >= 4;
  } catch (error) {
    console.error("❌ 获取中奖记录失败:", error.message);
    return true;
  }
}

// 全局变量
let liveListAll = [];
let isGetLive = false;
let pushArr = {};
let sendTxt = {};
let runGameId = [];
let isStart = false;

// 推送消息函数
async function sendMsg(content, uid) {
  try {
    console.log("📤 准备推送消息到uuid: " + uid);
    const pushAppToken = process.env.pushAppToken || "";
    
    const data = {
      appToken: pushAppToken,
      content: content,
      summary: "星播客中奖",
      contentType: 2,
      topicIds: [],
      uids: [uid],
      verifyPayType: "2"
    };
    
    const options = {
      url: "https://wxpusher.zjiecode.com/api/send/message",
      method: "post",
      headers: {},
      data: data
    };
    options.headers["Content-Type"] = "application/json";
    
    const response = await axios(options);
    console.log("📤 消息推送结果: " + (response.data.success ? "成功" : "失败") + "，响应:", response.data);
    return response.data;
  } catch (error) {
    console.error("❌ 消息推送失败:", error.message);
    throw error;
  }
}

// 提取数字（包括小数和负数）
function extractNumbersWithDecimalsAndNegatives(text) {
  const regex = /-?\d+(\.\d+)?/g;
  const matches = text.match(regex);
  return matches ? matches.map(Number) : [];
}

// 检查可用抽奖活动
async function checkAvailableLotteries(token) {
  console.log("🔍 开始检查可抽奖活动");
  let availableLotteries = [];
  let liveRoomsCopy = JSON.parse(JSON.stringify(liveListAll));
  console.log("🔍 开始检查直播间商品（共" + liveRoomsCopy.length + "个直播间）");
  
  try {
    let promises = liveRoomsCopy.map(async liveRoom => {
      let goodsData = await getGoodsList(liveRoom.liveId, 1, token);
      
      if (goodsData?.data?.list?.length == goodsData?.data?.count) {
        goodsData?.data?.list?.map(async goods => {
          if (goods.activeCode && !runGameId.includes(goods.activeCode)) {
            goods.liveId = liveRoom?.liveId;
            availableLotteries.push(goods);
            console.log("🎁 发现新的可抽奖活动：liveId=" + goods.liveId + "，直播间名称=" + liveRoom.title + "，activeCode=" + goods.activeCode);
            runGameId.push(goods.activeCode);
          } else {
            if (goods.activeCode) {
              console.log("ℹ️ 已抽取过的活动，跳过：activeCode=" + goods.activeCode);
            }
          }
        });
      } else {
        console.log("⚠️ 直播间商品数量不一致：liveId=" + liveRoom.liveId + "，返回" + (goodsData?.data?.list?.length || 0) + "个，实际" + (goodsData?.data?.count || 0) + "个");
      }
    });
    
    await Promise.all(promises);
    
    // 去重
    const uniqueLotteries = availableLotteries.reduce((acc, lottery) => {
      const key = lottery.liveId + "-" + lottery.activeCode;
      if (!acc.some(item => item.liveId + "-" + item.activeCode === key)) {
        acc.push(lottery);
      }
      return acc;
    }, []);
    
    console.log("🔍 可抽奖活动检查完成，共发现" + uniqueLotteries.length + "个新活动");
    
    if (uniqueLotteries.length > 0) {
      await processAllLotteries(uniqueLotteries);
    } else {
      console.log("🔍 未发现新的可抽奖活动");
    }
    
    return uniqueLotteries;
  } catch (error) {
    console.error("❌ 获取可抽奖活动错误:", error.message);
    return [];
  }
}

// 处理所有抽奖
async function processAllLotteries(lotteries, userPhone) {
  console.log("🎯 开始处理抽奖活动（共" + lotteries.length + "个活动）");
  
  try {
    if (lotteries.length === 0) {
      console.log("🎯 没有可抽奖的活动，结束流程");
      return;
    }
    
    isStart = true;
    console.log("🎯 开始执行抽奖，共" + lotteries.length + "个活动需要处理");
    
    for (let i = 0; i < lotteries.length; i++) {
      const lottery = lotteries[i];
      console.log("🎯 处理第" + (i + 1) + "/" + lotteries.length + "个活动：liveId=" + lottery.liveId + "，activeCode=" + lottery.activeCode);
      
      for (const account of userPhone) {
        if (account.xbkToken && account.isDo) {
          const chances = await getLotteryChances(account.xbkToken, lottery.activeCode);
          console.log("ℹ️ 账号" + maskPhoneNumber(account.phone) + "有" + chances + "次抽奖机会");
          
          for (let j = 0; j < chances; j++) {
            console.log("🎰 账号" + maskPhoneNumber(account.phone) + "的第" + (j + 1) + "/" + chances + "次抽奖（活动" + (i + 1) + "/" + lotteries.length + "）");
            const result = await doLottery(lottery.liveId, lottery.activeCode, account.xbkToken, account.phone, account.uid);
            
            // 处理中奖结果
            if (result && result.success) {
              if (!pushArr[account.uid]) {
                pushArr[account.uid] = {};
              }
              pushArr[account.uid][account.phone] = "<div>手机号: " + maskPhoneNumber(account.phone) + ",抽奖成功, 获得:<span style=\"color: red;\">" + result.prize + "</span></div>";
            }
            
            await sleep(4000);
          }
        } else {
          if (!account.xbkToken) {
            console.log("⚠️ 账号" + maskPhoneNumber(account.phone) + "未获取到token，跳过抽奖");
          } else {
            if (!account.isDo) {
              console.log("⚠️ 账号" + maskPhoneNumber(account.phone) + "已达抽奖上限，跳过");
            }
          }
        }
      }
    }
    
    console.log("🎯 所有抽奖活动处理完毕，准备推送结果");
    
    // 汇总推送消息
    for (let uid in pushArr) {
      let message = "";
      let totalAmount = 0;
      
      for (let phone in pushArr[uid]) {
        message += pushArr[uid][phone];
        let numbers = extractNumbersWithDecimalsAndNegatives(pushArr[uid][phone]);
        totalAmount += numbers[numbers.length - 1] || 0;
      }
      
      if (totalAmount > 0) {
        message += totalAmount + "元话费";
        sendTxt[uid] = message;
        console.log("📝 准备推送的中奖结果：" + message.substring(0, 50) + "...");
      }
    }
    
    pushArr = {};
    isStart = false;
    console.log("🎯 所有抽奖活动处理完成");
  } catch (error) {
    console.error("❌ 抽奖流程严重错误：" + error.message);
    isStart = false;
    setTimeout(() => {
      if (lotteries && lotteries.length > 0) {
        processAllLotteries(lotteries, userPhone);
      }
    }, 60000);
  }
}

// 获取直播间列表（按手机号）
async function getLiveListByPhone(phone, password, loginObj) {
  console.log("📱 开始获取直播间列表（手机号：" + maskPhoneNumber(phone) + "）");
  
  try {
    let loginResult = await loginPhone(phone, password, loginObj);
    
    if (!loginResult) {
      console.log("❌ 登录失败，无法获取直播间（手机号：" + maskPhoneNumber(phone) + "）");
      initLiveList("init");
      return;
    }
    
    let userCode = await getUserCode(loginResult.uid);
    let accessToken = await getAccessToken(userCode);
    
    console.log("✅ 登录成功，开始初始化直播间数据（手机号：" + maskPhoneNumber(phone) + "）");
    await initLiveRoomFloor(1, 1, 1, accessToken);
  } catch (error) {
    console.error("❌ 获取直播间列表错误：" + error.message + "（手机号：" + maskPhoneNumber(phone) + "）");
  }
}

// 初始化直播间
async function initLiveList(type, userPhone) {
  console.log("🏠 开始获取直播间数据（类型：" + type + "）");
  
  try {
    if (type == "init") {
      console.log("🏠 初始化直播间数据：使用随机账号");
      let randomIndex = Math.floor(Math.random() * userPhone.length);
      let randomAccount = userPhone[randomIndex];
      await getLiveListByPhone(randomAccount.phone, randomAccount.password, randomAccount.loginObj);
    } else {
      let randomIndex = Math.floor(Math.random() * userPhone.length);
      let randomAccount = userPhone[randomIndex];
      
      if (randomAccount.xbkToken) {
        console.log("🏠 使用已有token更新直播间（手机号：" + maskPhoneNumber(randomAccount.phone) + "）");
        await initLiveRoomFloor(1, 1, 1, randomAccount.xbkToken);
      } else {
        console.log("🏠 账号token不存在，重新初始化");
        initLiveList("init", userPhone);
      }
    }
  } catch (error) {
    console.error("❌ 获取直播间错误：" + error.message);
  }
}

// 检查抽奖活动（定时任务）
async function checkLotteryActivities(userPhone) {
  console.log("⏰ 触发检查可抽奖活动（每10秒一次）");
  
  try {
    if (isStart) {
      console.log("⏰ 抽奖流程正在进行中，跳过本次检查");
      return;
    }
    
    if (userPhone.length === 0) {
      console.log("❌ 没有可用账号，无法检查抽奖活动");
      return;
    }
    
    let randomIndex = Math.floor(Math.random() * userPhone.length);
    let randomAccount = userPhone[randomIndex];
    
    if (randomAccount.xbkToken) {
      console.log("🔍 使用账号" + maskPhoneNumber(randomAccount.phone) + "检查可抽奖活动");
      await checkAvailableLotteries(randomAccount.xbkToken);
    } else {
      console.log("⚠️ 账号" + maskPhoneNumber(randomAccount.phone) + "未登录，尝试重新登录");
      await loginAllAccounts(userPhone);
      checkLotteryActivities(userPhone);
    }
  } catch (error) {
    console.error("❌ 检查抽奖活动错误：" + error.message);
    setTimeout(() => checkLotteryActivities(userPhone), 5000);
  }
}

// 批量登录账号
async function loginAllAccounts(userPhone, Cache) {
  console.log("🔐 开始检查所有账号状态（共" + userPhone.length + "个）");
  
  try {
    let promises = userPhone.map(async (account, index) => {
      try {
        if (!account.time) {
          console.log("🔐 账号" + maskPhoneNumber(account.phone) + "：首次登录");
          let loginResult = await loginPhoneWithCache(account.phone, account.password, Cache);
          userPhone[index].time = new Date().valueOf();
          
          if (!loginResult) {
            console.log("❌ 账号" + maskPhoneNumber(account.phone) + "登录失败");
            userPhone[index].isLogin = false;
            return;
          }
          
          let userCode = await getUserCode(loginResult.uid);
          let accessToken = await getAccessToken(userCode);
          userPhone[index].xbkToken = accessToken;
          userPhone[index].isDo = await getMyWinList(accessToken);
          userPhone[index].isLogin = true;
          console.log("✅ 账号" + maskPhoneNumber(account.phone) + "登录成功");
          
          if (!isGetLive && liveListAll.length == 0) {
            isGetLive = true;
            console.log("🏠 使用账号" + maskPhoneNumber(account.phone) + "初始化直播间数据");
            await initLiveRoomFloor(1, 1, 1, accessToken);
          }
        } else {
          if (account.time && new Date().valueOf() - account.time > 43200000) {
            console.log("🔐 账号" + maskPhoneNumber(account.phone) + "：token过期（>12小时），重新登录");
            let loginResult = await loginPhoneWithCache(account.phone, account.password, Cache);
            userPhone[index].time = new Date().valueOf();
            
            if (!loginResult) {
              console.log("❌ 账号" + maskPhoneNumber(account.phone) + "重新登录失败");
              userPhone[index].isLogin = false;
              return;
            }
            
            let userCode = await getUserCode(loginResult.uid);
            let accessToken = await getAccessToken(userCode);
            userPhone[index].xbkToken = accessToken;
            userPhone[index].isDo = await getMyWinList(accessToken);
            userPhone[index].isLogin = true;
            console.log("✅ 账号" + maskPhoneNumber(account.phone) + "重新登录成功");
          } else {
            if (account.time && new Date().valueOf() - account.time > 21600000 && !account.isLogin) {
              console.log("🔐 账号" + maskPhoneNumber(account.phone) + "：未登录（>6小时），尝试登录");
              let loginResult = await loginPhoneWithCache(account.phone, account.password, Cache);
              userPhone[index].time = new Date().valueOf();
              
              if (!loginResult) {
                console.log("❌ 账号" + maskPhoneNumber(account.phone) + "登录失败");
                userPhone[index].isLogin = false;
                return;
              }
              
              let userCode = await getUserCode(loginResult.uid);
              let accessToken = await getAccessToken(userCode);
              userPhone[index].xbkToken = accessToken;
              userPhone[index].isDo = await getMyWinList(accessToken);
              userPhone[index].isLogin = true;
              console.log("✅ 账号" + maskPhoneNumber(account.phone) + "登录成功");
            } else {
              console.log("ℹ️ 账号" + maskPhoneNumber(account.phone) + "状态正常（无需重新登录）");
            }
          }
        }
      } catch (error) {
        console.error("❌ 处理账号" + maskPhoneNumber(account.phone) + "错误：" + error.message);
      }
    });
    
    await Promise.all(promises);
    
    const activeAccounts = userPhone.filter(account => account.isLogin && account.xbkToken);
    console.log("🔐 所有账号检查完毕，活跃账号数量：" + activeAccounts.length + "/" + userPhone.length);
    return activeAccounts.length > 0;
  } catch (error) {
    console.error("❌ 批量登录错误：" + error.message);
    return false;
  }
}

// 初始化用户数据
async function initializeUserData(userPhone) {
  console.log("📋 开始初始化用户数据");
  
  try {
    let Cache = {};
    try {
      Cache = JSON.parse(fs.readFileSync("./Cache.json", "utf8"));
      console.log("📋 成功加载缓存数据");
    } catch (error) {
      console.log("📋 缓存文件不存在，创建新缓存");
      fs.writeFileSync("./Cache.json", JSON.stringify({}), "utf8");
      Cache = {};
    }
    
    console.log("📋 共获取到" + userPhone.length + "个账号");
    await loginAllAccounts(userPhone, Cache);
    
    if (liveListAll.length === 0 && !isGetLive) {
      console.log("🏠 本地无直播间数据，开始初始化");
      const firstAccount = userPhone.find(account => account.xbkToken);
      
      if (firstAccount) {
        await initLiveRoomFloor(1, 1, 1, firstAccount.xbkToken);
      } else {
        console.log("❌ 没有可用的已登录账号，无法初始化直播间");
      }
    }
  } catch (error) {
    console.error("❌ 初始化用户数据错误：" + error.message);
    setTimeout(() => initializeUserData(userPhone), 300000);
  }
}

// 重写console.log添加时间戳
function getTimestamp() {
  return getTimestampFormatted();
}

const originalLog = console.log;
console.log = function (...args) {
  const timestamp = getTimestamp();
  originalLog("[" + timestamp + "]", ...args);
};

// 解析用户账号
let userPhone = [];
if (process?.env?.chinaTelecomAccount) {
  process?.env?.chinaTelecomAccount.split("&").map(account => {
    if (account) {
      let phone = account.split("#")[0];
      let password = account.split("#")[1];
      const accountData = {
        phone: phone,
        password: password
      };
      userPhone.push(accountData);
    }
  });
} else {
  console.log("❌ 未找到环境变量，请设置环境变量chinaTelecomAccount");
  process.exit();
}

// 获取用户名
let userName = "";
if (process?.env?.dxUserName1 || "aaabbb") {
  userName = process?.env?.dxUserName1 || "aaabbb";
} else {
  process.exit();
}

// 主入口函数
(async () => {
  console.log("🚀 脚本启动，开始初始化...");
  
  // 验证日期
  if (!validateDate()) {
    process.exit(1);
    return;
  }
  
  // 验证Lkey
  if (!(await validateLkey())) {
    process.exit(1);
    return;
  }
  
  try {
    // 初始化用户数据
    await initializeUserData(userPhone);
    
    // 读取本地直播间数据
    let liveListAll = [];
    try {
      liveListAll = JSON.parse(fs.readFileSync("./liveList.json", "utf8"));
      console.log("💾 读取本地直播间数据成功（" + liveListAll.length + "个）");
      setLiveListAll(liveListAll);
    } catch (error) {
      console.log("💾 本地直播间数据不存在，将重新获取");
      fs.writeFileSync("./liveList.json", JSON.stringify([]), "utf8");
      liveListAll = [];
    }
    
    // 检查直播间数据
    if (liveListAll.length === 0) {
      console.log("🏠 本地直播间数据为空，开始初始化加载（仅加载省份1）");
      const firstAccount = userPhone.find(account => account.xbkToken);
      if (firstAccount) {
        await initLiveRoomFloor(1, 1, 1, firstAccount.xbkToken);
      }
    } else {
      console.log("🏠 本地直播间数据有效");
      const stats = fs.statSync("./liveList.json");
      const modifyTime = new Date(stats.mtime);
      const currentTime = new Date();
      const hoursDiff = (currentTime - modifyTime) / 3600000;
      
      if (hoursDiff > 2) {
        console.log("⏰ 直播间数据已超过2小时，需要重新获取（当前已" + Math.floor(hoursDiff) + "小时）");
        const firstAccount = userPhone.find(account => account.xbkToken);
        if (firstAccount) {
          await initLiveRoomFloor(1, 1, 1, firstAccount.xbkToken);
        }
      } else {
        console.log("⏰ 直播间数据较新（" + Math.floor(hoursDiff) + "小时前），使用缓存");
        setTimeout(() => checkLotteryActivities(userPhone), 2000);
      }
    }
  } catch (error) {
    console.error("❌ 脚本初始化严重错误：" + error.message);
    console.log("⏰ 1分钟后将重试初始化");
    setTimeout(() => process.exit(1), 60000);
  }
})();

// 定时任务1: 每小时更新直播间和账号列表
setInterval(async () => {
  console.log("⏰ 定时任务：每小时更新直播间和账号列表（触发）");
  await initializeUserData(userPhone);
  initLiveList("update", userPhone);
}, 3600000);

// 定时任务2: 每5分钟检查可抽奖活动
setInterval(() => {
  console.log("⏰ 定时任务：每10秒检查可抽奖活动（即将触发）");
  if (!isStart) {
    checkLotteryActivities(userPhone);
  } else {
    console.log("⏰ 抽奖流程进行中，跳过本次定时检查");
  }
}, 300000);

// 定时任务3: 每10分钟清空抽奖记录
setInterval(() => {
  console.log("⏰ 定时任务：每10分钟清空抽奖记录（触发）");
  // 清空已抽奖活动记录
  while (runGameId.length > 0) {
    runGameId.pop();
  }
  console.log("✅ 抽奖记录已清空");
}, 600000);

// 定时任务4: 每分钟检查推送消息
setInterval(async () => {
  console.log("⏰ 定时任务：每分钟检查推送消息（触发）");
  
  if (!isStart) {
    let uids = Object.keys(sendTxt);
    
    if (uids.length > 0) {
      console.log("📤 发现" + uids.length + "条待推送消息");
      
      for (let uid in sendTxt) {
        await sendMsg(sendTxt[uid], uid);
        await sleep(3000);
      }
      
      // 清空已推送的消息
      for (let key in sendTxt) {
        delete sendTxt[key];
      }
      
      console.log("📤 所有消息推送完成");
    } else {
      console.log("📤 没有待推送的消息");
    }
  } else {
    console.log("⏰ 抽奖流程进行中，暂不推送消息");
  }
}, 60000);

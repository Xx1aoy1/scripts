/*
环境变量值 chinaTelecomAccount = 账号#密码
*/
const _0x49dfef = _0x5370a4("电信营业厅"),
  _0x8e0885 = require("got"),
  _0x203c4a = require("path"),
  {
    exec: _0x3898d1
  } = require("child_process"),
  {
    CookieJar: _0x4f58d7
  } = require("tough-cookie"),
  _0x5336b3 = require("fs"),
  _0x5e650c = require("crypto-js"),
  _0x22f09c = "chinaTelecom",
  _0x1876a7 = /[\n\&\@]/,
  _0x4aec53 = [_0x22f09c + "Account"],
  _0x128624 = 30000,
  _0x5a04a9 = 3;
const _0x1736e2 = _0x22f09c + "Rpc",
  _0x16d3ea = process.env[_0x1736e2],
  _0xf4231c = 6.02,
  _0x14f289 = "chinaTelecom",
  _0x100b57 = "https://leafxcy.coding.net/api/user/leafxcy/project/validcode/shared-depot/validCode/git/blob/master/code.json",
  _0x344953 = "JinDouMall";
let _0x1d3d6d = {};
const _0x5370da = "./chinaTelecom_cache.json",
  _0x3ed712 = "Mozilla/5.0 (Linux; U; Android 12; zh-cn; ONEPLUS A9000 Build/QKQ1.190716.003) AppleWebKit/533.1 (KHTML, like Gecko) Version/5.0 Mobile Safari/533.1",
  _0x75a069 = "34d7cb0bcdf07523",
  _0x2304b1 = "1234567`90koiuyhgtfrdewsaqaqsqde",
  _0x1110eb = "\0\0\0\0\0\0\0\0",
  _0x3c561e = "MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDBkLT15ThVgz6/NOl6s8GNPofdWzWbCkWnkaAm7O2LjkM1H7dMvzkiqdxU02jamGRHLX/ZNMCXHnPcW/sDhiFCBN18qFvy8g6VYb9QtroI09e176s+ZCtiv7hbin2cCTj99iUpnEloZm19lwHyo69u5UMiPMpq0/XKBO8lYhN/gwIDAQAB",
  _0x1e9565 = "-----BEGIN PUBLIC KEY-----\n" + _0x3c561e + "\n-----END PUBLIC KEY-----",
  _0x516f15 = "MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC+ugG5A8cZ3FqUKDwM57GM4io6JGcStivT8UdGt67PEOihLZTw3P7371+N47PrmsCpnTRzbTgcupKtUv8ImZalYk65dU8rjC/ridwhw9ffW2LBwvkEnDkkKKRi2liWIItDftJVBiWOh17o6gfbPoNrWORcAdcbpk2L+udld5kZNwIDAQAB",
  _0x4995b7 = "-----BEGIN PUBLIC KEY-----\n" + _0x516f15 + "\n-----END PUBLIC KEY-----",
  _0x51cf70 = "MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDIPOHtjs6p4sTlpFvrx+ESsYkEvyT4JB/dcEbU6C8+yclpcmWEvwZFymqlKQq89laSH4IxUsPJHKIOiYAMzNibhED1swzecH5XLKEAJclopJqoO95o8W63Euq6K+AKMzyZt1SEqtZ0mXsN8UPnuN/5aoB3kbPLYpfEwBbhto6yrwIDAQAB",
  _0x2e5ddf = "-----BEGIN PUBLIC KEY-----\n" + _0x51cf70 + "\n-----END PUBLIC KEY-----",
  _0xc38e90 = require("node-rsa");
let _0x13a631 = new _0xc38e90(_0x1e9565);
const _0x4386dc = {
  encryptionScheme: "pkcs1"
};
_0x13a631.setOptions(_0x4386dc);
let _0x47bb4b = new _0xc38e90(_0x4995b7);
const _0xe2cacf = {
  encryptionScheme: "pkcs1"
};
_0x47bb4b.setOptions(_0xe2cacf);
let _0x5b4189 = new _0xc38e90(_0x2e5ddf);
const _0x3ab892 = {
  encryptionScheme: "pkcs1"
};
_0x5b4189.setOptions(_0x3ab892);
const _0x131d2d = [202201, 202202, 202203],
  _0x3c685e = 5;
function _0x1519a6(_0xa8ae5c, _0x459aac, _0x58d61f, _0xa81bc3, _0x5af061, _0x3eaf32) {
  return _0x5e650c[_0xa8ae5c].encrypt(_0x5e650c.enc.Utf8.parse(_0xa81bc3), _0x5e650c.enc.Utf8.parse(_0x5af061), {
    mode: _0x5e650c.mode[_0x459aac],
    padding: _0x5e650c.pad[_0x58d61f],
    iv: _0x5e650c.enc.Utf8.parse(_0x3eaf32)
  }).ciphertext.toString(_0x5e650c.enc.Hex);
}
function _0x436a1e(_0x5007ed, _0x18814d, _0x38ebb6, _0x4281ff, _0x1bafc9, _0x3aac70) {
  return _0x5e650c[_0x5007ed].decrypt({
    ciphertext: _0x5e650c.enc.Hex.parse(_0x4281ff)
  }, _0x5e650c.enc.Utf8.parse(_0x1bafc9), {
    mode: _0x5e650c.mode[_0x18814d],
    padding: _0x5e650c.pad[_0x38ebb6],
    iv: _0x5e650c.enc.Utf8.parse(_0x3aac70)
  }).toString(_0x5e650c.enc.Utf8);
}
function _0x4e4355() {
  try {
    _0x5336b3.writeFileSync(_0x5370da, JSON.stringify(_0x1d3d6d, null, 4), "utf-8");
  } catch (_0x1c3791) {
    console.log("保存缓存出错");
  }
}
function _0xa0ff1b() {
  try {
    _0x1d3d6d = JSON.parse(_0x5336b3.readFileSync(_0x5370da, "utf-8"));
  } catch (_0x125821) {
    console.log("读取缓存出错, 新建一个token缓存");
    _0x4e4355();
  }
}
let _0x300c8e = 0,
  _0xdb6efe = 0;
function _0x11cae0() {
  _0xdb6efe = 1;
  process.on("SIGTERM", () => {
    _0xdb6efe = 2;
    process.exit(0);
  });
  const _0x377b8a = _0x203c4a.basename(process.argv[1]),
    _0x39bc5b = ["bash", "timeout", "grep"];
  let _0x4fe84e = ["ps afx"];
  _0x4fe84e.push("grep " + _0x377b8a);
  _0x4fe84e = _0x4fe84e.concat(_0x39bc5b.map(_0x425dac => "grep -v \"" + _0x425dac + " \""));
  _0x4fe84e.push("wc -l");
  const _0x401932 = _0x4fe84e.join("|"),
    _0x134226 = () => {
      _0x3898d1(_0x401932, (_0x26b41f, _0x817890, _0x4eca1a) => {
        if (_0x26b41f || _0x4eca1a) {
          return;
        }
        _0x300c8e = parseInt(_0x817890.trim(), 10);
      });
      if (_0xdb6efe == 1) {
        setTimeout(_0x134226, 2000);
      }
    };
  _0x134226();
}
class _0x9d1851 {
  constructor() {
    this.index = _0x49dfef.userIdx++;
    this.name = "";
    this.valid = false;
    const _0x46f57a = {
      limit: 0
    };
    const _0x42e66e = {
      Connection: "keep-alive"
    };
    const _0x1612bd = {
      retry: _0x46f57a,
      timeout: _0x128624,
      followRedirect: false,
      ignoreInvalidCookies: true,
      headers: _0x42e66e
    };
    this.got = _0x8e0885.extend(_0x1612bd);
    if (_0xdb6efe == 0) {
      _0x11cae0();
    }
  }
  log(_0x42a357, _0x32d0cc = {}) {
    var _0x58117c = "",
      _0x9ca0e2 = _0x49dfef.userCount.toString().length;
    if (this.index) {
      _0x58117c += "账号[" + _0x49dfef.padStr(this.index, _0x9ca0e2) + "]";
    }
    if (this.name) {
      _0x58117c += "[" + this.name + "]";
    }
    _0x49dfef.log(_0x58117c + _0x42a357, _0x32d0cc);
  }
  set_cookie(_0x309397, _0x3ab012, _0x4a8547, _0x1320cb, _0x482400 = {}) {
    this.cookieJar.setCookieSync(_0x309397 + "=" + _0x3ab012 + "; Domain=" + _0x4a8547 + ";", "" + _0x1320cb);
  }
  async request(_0x29ad8a) {
    const _0x58b4a1 = ["ECONNRESET", "EADDRINUSE", "ENOTFOUND", "EAI_AGAIN"],
      _0x497c09 = ["TimeoutError"],
      _0x54807f = ["EPROTO"],
      _0x30eee7 = [];
    var _0x208a74 = null,
      _0x3a35d0 = 0,
      _0x1684d3 = _0x29ad8a.fn || _0x29ad8a.url;
    let _0x25d788 = _0x49dfef.get(_0x29ad8a, "valid_code", _0x30eee7);
    _0x29ad8a.method = _0x29ad8a?.["method"]?.["toUpperCase"]() || "GET";
    let _0x19ce7b, _0x5c8c40;
    while (_0x3a35d0 < _0x5a04a9) {
      try {
        _0x3a35d0++;
        _0x19ce7b = "";
        _0x5c8c40 = "";
        let _0x1fa216 = null,
          _0x123eec = _0x29ad8a?.["timeout"] || this.got?.["defaults"]?.["options"]?.["timeout"]?.["request"] || _0x128624,
          _0x34e77b = false,
          _0x5397b0 = Math.max(this.index - 2, 0),
          _0x5d25e7 = Math.min(Math.max(this.index - 3, 1), 3),
          _0x52755a = Math.min(Math.max(this.index - 4, 1), 4),
          _0x15d328 = _0x5397b0 * _0x5d25e7 * _0x52755a * 400,
          _0x2c4c80 = _0x5397b0 * _0x5d25e7 * _0x52755a * 1800,
          _0x4cfee0 = _0x15d328 + Math.floor(Math.random() * _0x2c4c80),
          _0x15dce7 = _0x300c8e * (_0x300c8e - 1) * 2000,
          _0x5ca50a = (_0x300c8e - 1) * (_0x300c8e - 1) * 2000,
          _0x333735 = _0x15dce7 + Math.floor(Math.random() * _0x5ca50a),
          _0x573d35 = Math.max(_0x49dfef.userCount - 2, 0),
          _0x25871d = Math.max(_0x49dfef.userCount - 3, 0),
          _0x34f531 = _0x573d35 * 200,
          _0x1bd293 = _0x25871d * 400,
          _0x4845e7 = _0x34f531 + Math.floor(Math.random() * _0x1bd293),
          _0x5dc50f = _0x4cfee0 + _0x333735 + _0x4845e7;
        await _0x49dfef.wait(_0x5dc50f);
        await new Promise(async _0x45b1d3 => {
          setTimeout(() => {
            _0x34e77b = true;
            _0x45b1d3();
          }, _0x123eec);
          await this.got(_0x29ad8a).then(_0x284c2a => {
            _0x208a74 = _0x284c2a;
          }, _0x55b6b8 => {
            _0x1fa216 = _0x55b6b8;
            _0x208a74 = _0x55b6b8.response;
            _0x19ce7b = _0x1fa216?.["code"] || "";
            _0x5c8c40 = _0x1fa216?.["name"] || "";
          });
          _0x45b1d3();
        });
        if (_0x34e77b) {
          this.log("[" + _0x1684d3 + "]请求超时(" + _0x123eec / 1000 + "秒)，重试第" + _0x3a35d0 + "次");
        } else {
          if (_0x54807f.includes(_0x19ce7b)) {
            this.log("[" + _0x1684d3 + "]请求错误[" + _0x19ce7b + "][" + _0x5c8c40 + "]");
            if (_0x1fa216?.["message"]) {
              console.log(_0x1fa216.message);
            }
            break;
          } else {
            if (_0x497c09.includes(_0x5c8c40)) {
              this.log("[" + _0x1684d3 + "]请求错误[" + _0x19ce7b + "][" + _0x5c8c40 + "]，重试第" + _0x3a35d0 + "次");
            } else {
              if (_0x58b4a1.includes(_0x19ce7b)) {
                this.log("[" + _0x1684d3 + "]请求错误[" + _0x19ce7b + "][" + _0x5c8c40 + "]，重试第" + _0x3a35d0 + "次");
              } else {
                let _0x42b498 = _0x208a74?.["statusCode"] || "",
                  _0x2ef704 = _0x42b498 / 100 | 0;
                if (_0x42b498) {
                  _0x2ef704 > 3 && !_0x25d788.includes(_0x42b498) && (_0x42b498 ? this.log("请求[" + _0x1684d3 + "]返回[" + _0x42b498 + "]") : this.log("请求[" + _0x1684d3 + "]错误[" + _0x19ce7b + "][" + _0x5c8c40 + "]"));
                  if (_0x2ef704 <= 4) {
                    break;
                  }
                } else {
                  this.log("请求[" + _0x1684d3 + "]错误[" + _0x19ce7b + "][" + _0x5c8c40 + "]");
                }
              }
            }
          }
        }
      } catch (_0xa3ad4) {
        _0xa3ad4.name == "TimeoutError" ? this.log("[" + _0x1684d3 + "]请求超时，重试第" + _0x3a35d0 + "次") : this.log("[" + _0x1684d3 + "]请求错误(" + _0xa3ad4.message + ")，重试第" + _0x3a35d0 + "次");
      }
    }
    const _0x14f89a = {
      statusCode: _0x19ce7b || -1,
      headers: null,
      result: null
    };
    if (_0x208a74 == null) {
      return Promise.resolve(_0x14f89a);
    }
    let {
      statusCode: _0x4f50c8,
      headers: _0x4fdc35,
      body: _0x4bfa21
    } = _0x208a74;
    if (_0x4bfa21) {
      try {
        _0x4bfa21 = JSON.parse(_0x4bfa21);
      } catch {}
    }
    const _0x5d1199 = {
      statusCode: _0x4f50c8,
      headers: _0x4fdc35,
      result: _0x4bfa21
    };
    return Promise.resolve(_0x5d1199);
  }
}
let _0x280825 = _0x9d1851;
try {
  let _0x236d58 = require("./LocalBasic");
  _0x280825 = _0x236d58;
} catch {}
let _0x3b1630 = new _0x280825(_0x49dfef);
class _0x3f433d extends _0x280825 {
  constructor(_0x5669ce) {
    super(_0x49dfef);
    let _0x28f602 = _0x5669ce.split("#");
    this.name = _0x28f602[0];
    this.passwd = _0x28f602?.[1] || "";
    this.uuid = [_0x49dfef.randomPattern("xxxxxxxx"), _0x49dfef.randomPattern("xxxx"), _0x49dfef.randomPattern("4xxx"), _0x49dfef.randomPattern("xxxx"), _0x49dfef.randomPattern("xxxxxxxxxxxx")];
    this.cookieJar = new _0x4f58d7();
    this.can_feed = true;
    this.jml_tokenFlag = "";
    this.mall_token = "";
    const _0x1effd8 = {
      Connection: "keep-alive",
      "User-Agent": _0x3ed712
    };
    this.got = this.got.extend({
      cookieJar: this.cookieJar,
      headers: _0x1effd8
    });
  }
  load_token() {
    let _0x2f4a66 = false;
    _0x1d3d6d[this.name] && (this.userId = _0x1d3d6d[this.name].userId, this.token = _0x1d3d6d[this.name].token, this.log("读取到缓存token"), _0x2f4a66 = true);
    return _0x2f4a66;
  }
  encode_phone() {
    let _0xd2389f = this.name.split("");
    for (let _0x51660a in _0xd2389f) {
      _0xd2389f[_0x51660a] = String.fromCharCode(_0xd2389f[_0x51660a].charCodeAt(0) + 2);
    }
    return _0xd2389f.join("");
  }
  encode_aes(_0x53e9bb) {
    return _0x1519a6("AES", "ECB", "Pkcs7", _0x53e9bb, _0x75a069, 0);
  }
  get_mall_headers() {
    return {
      "Content-Type": "application/json;charset=utf-8",
      Accept: "application/json, text/javascript, */*; q=0.01",
      Authorization: this.mall_token ? "Bearer " + this.mall_token : "",
      "X-Requested-With": "XMLHttpRequest"
    };
  }
  async login(_0x2971d3 = {}) {
    let _0x22cd07 = false;
    try {
      let _0x3ae9d0 = _0x49dfef.time("yyyyMMddhhmmss"),
        _0x16bc9b = "iPhone 14 15.4." + this.uuid.slice(0, 2).join("") + this.name + _0x3ae9d0 + this.passwd + "0$$$0.",
        _0x807c6e = {
          fn: "login",
          method: "post",
          url: "https://appgologin.189.cn:9031/login/client/userLoginNormal",
          json: {
            headerInfos: {
              code: "userLoginNormal",
              timestamp: _0x3ae9d0,
              broadAccount: "",
              broadToken: "",
              clientType: "#9.6.1#channel50#iPhone 14 Pro Max#",
              shopId: "20002",
              source: "110003",
              sourcePassword: "Sid98s",
              token: "",
              userLoginName: this.name
            },
            content: {
              attach: "test",
              fieldData: {
                loginType: "4",
                accountType: "",
                loginAuthCipherAsymmertric: _0x13a631.encrypt(_0x16bc9b, "base64"),
                deviceUid: this.uuid.slice(0, 3).join(""),
                phoneNum: this.encode_phone(),
                isChinatelecom: "0",
                systemVersion: "15.4.0",
                authentication: this.passwd
              }
            }
          }
        },
        {
          result: _0x3cbd6a,
          statusCode: _0x4338ff
        } = await this.request(_0x807c6e),
        _0x107431 = _0x49dfef.get(_0x3cbd6a?.["responseData"], "resultCode", -1);
      if (_0x107431 == "0000") {
        let {
          userId = "",
          token = ""
        } = _0x3cbd6a?.["responseData"]?.["data"]?.["loginSuccessResult"] || {};
        this.userId = userId;
        this.token = token;
        this.log("使用服务密码登录成功");
        _0x1d3d6d[this.name] = {
          token: token,
          userId: userId,
          t: Date.now()
        };
        _0x4e4355();
        _0x22cd07 = true;
      } else {
        let _0xf8ba30 = _0x3cbd6a?.["msg"] || _0x3cbd6a?.["responseData"]?.["resultDesc"] || _0x3cbd6a?.["headerInfos"]?.["reason"] || "";
        this.log("服务密码登录失败[" + _0x107431 + "]: " + _0xf8ba30);
      }
    } catch (_0x576f6c) {
      console.log(_0x576f6c);
    } finally {
      return _0x22cd07;
    }
  }
  async get_ticket(_0x3e5067 = {}) {
    let _0x252ee2 = "";
    try {
      let _0x21dd20 = "\n            <Request>\n                <HeaderInfos>\n                    <Code>getSingle</Code>\n                    <Timestamp>" + _0x49dfef.time("yyyyMMddhhmmss") + "</Timestamp>\n                    <BroadAccount></BroadAccount>\n                    <BroadToken></BroadToken>\n                    <ClientType>#9.6.1#channel50#iPhone 14 Pro Max#</ClientType>\n                    <ShopId>20002</ShopId>\n                    <Source>110003</Source>\n                    <SourcePassword>Sid98s</SourcePassword>\n                    <Token>" + this.token + "</Token>\n                    <UserLoginName>" + this.name + "</UserLoginName>\n                </HeaderInfos>\n                <Content>\n                    <Attach>test</Attach>\n                    <FieldData>\n                        <TargetId>" + _0x1519a6("TripleDES", "CBC", "Pkcs7", this.userId, _0x2304b1, _0x1110eb) + "</TargetId>\n                        <Url>4a6862274835b451</Url>\n                    </FieldData>\n                </Content>\n            </Request>";
      const _0xb709e1 = {
        fn: "get_ticket",
        method: "post",
        url: "https://appgologin.189.cn:9031/map/clientXML",
        body: _0x21dd20
      };
      let {
        result: _0x9f4220,
        statusCode: _0x1e891f
      } = await this.request(_0xb709e1);
      if (_0x9f4220) {
        let _0x18f397 = _0x9f4220.match(/\<Ticket\>(\w+)\<\/Ticket\>/);
        if (_0x18f397) {
          let _0x2c4653 = _0x18f397[1];
          _0x252ee2 = _0x436a1e("TripleDES", "CBC", "Pkcs7", _0x2c4653, _0x2304b1, _0x1110eb);
          this.ticket = _0x252ee2;
        }
      }
      !_0x252ee2 && (!_0x3e5067.retry && (await this.login()) ? (_0x3e5067.retry = true, _0x252ee2 = await this.get_ticket(_0x3e5067)) : (this.log("没有获取到ticket[" + _0x1e891f + "]: "), _0x9f4220 && this.log(": " + JSON.stringify(_0x9f4220))));
    } catch (_0x1c9e54) {
      console.log(_0x1c9e54);
    } finally {
      return _0x252ee2;
    }
  }
  async get_sign(_0x9b96be = {}) {
    let _0x10c0cb = false;
    try {
      const _0x59fe75 = {
        ticket: this.ticket
      };
      const _0x139dfe = {
        fn: "login",
        method: "get",
        url: "https://wapside.189.cn:9001/jt-sign/ssoHomLogin",
        searchParams: _0x59fe75
      };
      let {
          result: _0x36bbb6,
          statusCode: _0x3a8945
        } = await this.request(_0x139dfe),
        _0xe3542d = _0x49dfef.get(_0x36bbb6, "resoultCode", _0x3a8945);
      _0xe3542d == 0 ? (_0x10c0cb = _0x36bbb6?.["sign"], this.sign = _0x10c0cb, this.got = this.got.extend({
        headers: {
          sign: this.sign
        }
      })) : this.log("获取sign失败[" + _0xe3542d + "]: " + _0x36bbb6);
    } catch (_0x44161f) {
      console.log(_0x44161f);
    } finally {
      return _0x10c0cb;
    }
  }
  encrypt_para(_0x217db5) {
    let _0x1c768f = typeof _0x217db5 == "string" ? _0x217db5 : JSON.stringify(_0x217db5);
    return _0x47bb4b.encrypt(_0x1c768f, "hex");
  }
    encrypt_para(_0x217db5) {
    let _0x1c768f = typeof _0x217db5 == "string" ? _0x217db5 : JSON.stringify(_0x217db5);
    return _0x47bb4b.encrypt(_0x1c768f, "hex");
  }
  async userCoinInfo(_0x3a27b0 = false, _0x2a9f2e = {}) {
    try {
      const _0x314c14 = {
        phone: this.name
      };
      let _0x55424b = {
          fn: "userCoinInfo",
          method: "post",
          url: "https://wapside.189.cn:9001/jt-sign/api/home/userCoinInfo",
          json: {
            para: this.encrypt_para(_0x314c14)
          }
        },
        {
          result: _0x18ad00,
          statusCode: _0x3e695c
        } = await this.request(_0x55424b),
        _0x474131 = _0x49dfef.get(_0x18ad00, "resoultCode", _0x3e695c);
      if (_0x474131 == 0) {
        this.coin = _0x18ad00?.["totalCoin"] || 0;
        if (_0x3a27b0) {
          const _0x3a5985 = {
            notify: true
          };
          this.log("金豆余额: " + this.coin, _0x3a5985);
          if (_0x18ad00.amountEx) {
            let _0x5b7bde = _0x49dfef.time("yyyy-MM-dd", _0x18ad00.expireDate);
            const _0x359049 = {
              notify: true
            };
            _0x49dfef.log("-- [" + _0x5b7bde + "]将过期" + _0x18ad00.amountEx + "金豆", _0x359049);
          }
        }
      } else {
        let _0x4e7123 = _0x18ad00?.["msg"] || _0x18ad00?.["resoultMsg"] || _0x18ad00?.["error"] || "";
        this.log("查询账户金豆余额错误[" + _0x474131 + "]: " + _0x4e7123);
      }
    } catch (_0x4d1b75) {
      console.log(_0x4d1b75);
    }
  }
    async getLevelRightsList(_0x3ea0a7 = {}) {
    try {
      const _0x166dba = {
        phone: this.name
      };
      let _0x5a0971 = {
          fn: "getLevelRightsList",
          method: "post",
          url: "https://wapside.189.cn:9001/jt-sign/paradise/getLevelRightsList",
          json: {
            para: this.encrypt_para(_0x166dba)
          }
        },
        {
          result: _0x4cf13d,
          statusCode: _0x5e92a4
        } = await this.request(_0x5a0971);
      if (_0x4cf13d?.["currentLevel"]) {
        let _0x3b50bb = _0x4cf13d?.["currentLevel"] || 6,
          _0x1f1006 = false,
          _0x53ddf4 = "V" + _0x3b50bb;
        for (let _0x1ab325 of _0x4cf13d[_0x53ddf4] || []) {
          let _0x59ef49 = _0x1ab325?.["righstName"] || "";
          if (this.coin < _0x1ab325.costCoin) {
            continue;
          }
          (_0x59ef49?.["match"](/\d+元话费/) || _0x59ef49?.["match"](/专享\d+金豆/)) && (await this.getConversionRights(_0x1ab325, _0x1f1006)) && (_0x1f1006 = true);
        }
      } else {
        let _0x4ff776 = _0x4cf13d?.["msg"] || _0x4cf13d?.["resoultMsg"] || _0x4cf13d?.["error"] || "";
        this.log("查询宠物兑换权益失败: " + _0x4ff776);
      }
    } catch (_0xcfd2ba) {
      console.log(_0xcfd2ba);
    }
  }
  async getConversionRights(_0xca19ef, _0x28066a, _0x21f772 = {}) {
    let _0x21db60 = false;
    try {
      let _0x5d6f72 = _0xca19ef?.["righstName"] || "";
      const _0x714d7a = {
        phone: this.name,
        rightsId: _0xca19ef.id,
        receiveCount: _0xca19ef.receiveType
      };
      let _0x5ed3b5 = {
          fn: "getConversionRights",
          method: "post",
          url: "https://wapside.189.cn:9001/jt-sign/paradise/getConversionRights",
          json: {
            para: this.encrypt_para(_0x714d7a)
          }
        },
        {
          result: _0x409ea1,
          statusCode: _0x3fb426
        } = await this.request(_0x5ed3b5),
        _0x17b3d0 = _0x49dfef.get(_0x409ea1, "code", _0x49dfef.get(_0x409ea1, "resoultCode", _0x3fb426));
      if (_0x17b3d0 == 200) {
        if (!(_0x409ea1?.["rightsStatus"]?.["includes"]("已兑换") || _0x409ea1?.["rightsStatus"]?.["includes"]("已领取"))) {
          _0x21db60 = true;
          if (_0x28066a) {
            await _0x49dfef.wait(3000);
          }
          await this.conversionRights(_0xca19ef);
        }
      } else {
        let _0x267dcb = _0x409ea1?.["msg"] || _0x409ea1?.["resoultMsg"] || _0x409ea1?.["error"] || "";
        this.log("查询权益[" + _0x5d6f72 + "]失败[" + _0x17b3d0 + "]: " + _0x267dcb);
      }
    } catch (_0x1c9805) {
      console.log(_0x1c9805);
    } finally {
      return _0x21db60;
    }
  }
  async conversionRights(_0x1258fb, _0x5ee37a = {}) {
    try {
      let _0x285002 = _0x1258fb?.["righstName"] || "";
      const _0x3ba559 = {
        phone: this.name,
        rightsId: _0x1258fb.id
      };
      let _0x259df8 = {
          fn: "conversionRights",
          method: "post",
          url: "https://wapside.189.cn:9001/jt-sign/paradise/conversionRights",
          json: {
            para: this.encrypt_para(_0x3ba559)
          }
        },
        {
          result: _0x24b720,
          statusCode: _0x2867ce
        } = await this.request(_0x259df8),
        _0x1caee2 = _0x49dfef.get(_0x24b720, "resoultCode", _0x2867ce);
      if (_0x1caee2 == 0) {
        this.log("兑换权益[" + _0x285002 + "]成功");
      } else {
        let _0x58c8d6 = _0x24b720?.["msg"] || _0x24b720?.["resoultMsg"] || _0x24b720?.["error"] || "";
        this.log("兑换权益[" + _0x285002 + "]失败[" + _0x1caee2 + "]: " + _0x58c8d6);
      }
    } catch (_0x2f6eb8) {
      console.log(_0x2f6eb8);
    }
  }
    async userTask() {
    const _0x4d55e5 = {
      notify: true
    };
    _0x49dfef.log("\n======= 账号[" + this.index + "][" + this.name + "] =======", _0x4d55e5);
    if (!this.load_token() && !(await this.login())) {
      return;
    }
    if (!(await this.get_ticket())) {
      return;
    }
    if (!(await this.get_sign())) {
      return;
    }
    await this.userCoinInfo();
    await this.getLevelRightsList();
    //await this.month_jml_preCost();
    //await this.userStatusInfo();
    //await this.continueSignRecords();
    //await this.homepage("hg_qd_zrwzjd");
    //await this.getParadiseInfo();
    if (_0x16d3ea) {
      await this.userLotteryTask();
    }
    await this.userCoinInfo(true);
  }
  async userLotteryTask() {
    if (!(await this.auth_login())) {
      return;
    }
    await this.queryInfo();
  }
}
!(async () => {
  _0x49dfef.read_env(_0x3f433d);
  for (let _0x28b102 of _0x49dfef.userList) {
    await _0x28b102.userTask();
  }
})().catch(_0x3fccb3 => _0x49dfef.log(_0x3fccb3)).finally(() => _0x49dfef.exitNow());

function _0x5370a4(_0x24412c) {
  return new class {
    constructor(_0x198bc4) {
      this.name = _0x198bc4;
      this.startTime = Date.now();
      const _0x555858 = {
        time: true
      };
      this.log("[" + this.name + "]开始运行\n", _0x555858);
      this.notifyStr = [];
      this.notifyFlag = true;
      this.userIdx = 0;
      this.userList = [];
      this.userCount = 0;
      this.default_timestamp_len = 13;
      this.default_wait_interval = 1000;
      this.default_wait_limit = 3600000;
      this.default_wait_ahead = 0;
    }
    log(_0x25f67c, _0x45847d = {}) {
      const _0x82b0fc = {
        console: true
      };
      Object.assign(_0x82b0fc, _0x45847d);
      if (_0x82b0fc.time) {
        let _0x58f096 = _0x82b0fc.fmt || "hh:mm:ss";
        _0x25f67c = "[" + this.time(_0x58f096) + "]" + _0x25f67c;
      }
      if (_0x82b0fc.notify) {
        this.notifyStr.push(_0x25f67c);
      }
      if (_0x82b0fc.console) {
        console.log(_0x25f67c);
      }
    }
    get(_0x2ecf4d, _0x5800fb, _0x1ff76e = "") {
      let _0x5a663b = _0x1ff76e;
      _0x2ecf4d?.["hasOwnProperty"](_0x5800fb) && (_0x5a663b = _0x2ecf4d[_0x5800fb]);
      return _0x5a663b;
    }
    pop(_0x2ae8ec, _0xbb54f6, _0x9c8563 = "") {
      let _0x213044 = _0x9c8563;
      _0x2ae8ec?.["hasOwnProperty"](_0xbb54f6) && (_0x213044 = _0x2ae8ec[_0xbb54f6], delete _0x2ae8ec[_0xbb54f6]);
      return _0x213044;
    }
    copy(_0x1fbe5b) {
      return Object.assign({}, _0x1fbe5b);
    }
    read_env(_0x412e83) {
      let _0x1267c5 = _0x4aec53.map(_0x166c56 => process.env[_0x166c56]);
      for (let _0x2b0da2 of _0x1267c5.filter(_0x22b120 => !!_0x22b120)) {
        for (let _0x4465a3 of _0x2b0da2.split(_0x1876a7).filter(_0x3c7dca => !!_0x3c7dca)) {
          if (this.userList.includes(_0x4465a3)) {
            continue;
          }
          this.userList.push(new _0x412e83(_0x4465a3));
        }
      }
      this.userCount = this.userList.length;
      if (!this.userCount) {
        const _0x3d5d5 = {
          notify: true
        };
        this.log("未找到变量，请检查变量" + _0x4aec53.map(_0x56423f => "[" + _0x56423f + "]").join("或"), _0x3d5d5);
        return false;
      }
      this.log("共找到" + this.userCount + "个账号");
      return true;
    }
    time(_0x43e381, _0x1822e0 = null) {
      let _0x1de2f7 = _0x1822e0 ? new Date(_0x1822e0) : new Date(),
        _0x180e96 = {
          "M+": _0x1de2f7.getMonth() + 1,
          "d+": _0x1de2f7.getDate(),
          "h+": _0x1de2f7.getHours(),
          "m+": _0x1de2f7.getMinutes(),
          "s+": _0x1de2f7.getSeconds(),
          "q+": Math.floor((_0x1de2f7.getMonth() + 3) / 3),
          S: this.padStr(_0x1de2f7.getMilliseconds(), 3)
        };
      /(y+)/.test(_0x43e381) && (_0x43e381 = _0x43e381.replace(RegExp.$1, (_0x1de2f7.getFullYear() + "").substr(4 - RegExp.$1.length)));
      for (let _0x2cfbd9 in _0x180e96) new RegExp("(" + _0x2cfbd9 + ")").test(_0x43e381) && (_0x43e381 = _0x43e381.replace(RegExp.$1, 1 == RegExp.$1.length ? _0x180e96[_0x2cfbd9] : ("00" + _0x180e96[_0x2cfbd9]).substr(("" + _0x180e96[_0x2cfbd9]).length)));
      return _0x43e381;
    }
    async showmsg() {
      if (!this.notifyFlag) {
        return;
      }
      if (!this.notifyStr.length) {
        return;
      }
      var _0x2264e = require("./sendNotify");
      this.log("\n============== 推送 ==============");
      await _0x2264e.sendNotify(this.name, this.notifyStr.join("\n"));
    }
    padStr(_0x397014, _0x4fcca2, _0x1abd3c = {}) {
      let _0x10354b = _0x1abd3c.padding || "0",
        _0x39ed4e = _0x1abd3c.mode || "l",
        _0x3b33af = String(_0x397014),
        _0x26e87b = _0x4fcca2 > _0x3b33af.length ? _0x4fcca2 - _0x3b33af.length : 0,
        _0x3bb60f = "";
      for (let _0x30ac41 = 0; _0x30ac41 < _0x26e87b; _0x30ac41++) {
        _0x3bb60f += _0x10354b;
      }
      _0x39ed4e == "r" ? _0x3b33af = _0x3b33af + _0x3bb60f : _0x3b33af = _0x3bb60f + _0x3b33af;
      return _0x3b33af;
    }
    json2str(_0x123637, _0x402c90, _0x46e6c5 = false) {
      let _0x75d972 = [];
      for (let _0x2a0f42 of Object.keys(_0x123637).sort()) {
        let _0x2bc1ca = _0x123637[_0x2a0f42];
        if (_0x2bc1ca && _0x46e6c5) {
          _0x2bc1ca = encodeURIComponent(_0x2bc1ca);
        }
        _0x75d972.push(_0x2a0f42 + "=" + _0x2bc1ca);
      }
      return _0x75d972.join(_0x402c90);
    }
    str2json(_0x32e5fc, _0x43a064 = false) {
      let _0x4cd4ad = {};
      for (let _0x520529 of _0x32e5fc.split("&")) {
        if (!_0x520529) {
          continue;
        }
        let _0x1dc4e6 = _0x520529.indexOf("=");
        if (_0x1dc4e6 == -1) {
          continue;
        }
        let _0x4998d0 = _0x520529.substr(0, _0x1dc4e6),
          _0x3ac012 = _0x520529.substr(_0x1dc4e6 + 1);
        if (_0x43a064) {
          _0x3ac012 = decodeURIComponent(_0x3ac012);
        }
        _0x4cd4ad[_0x4998d0] = _0x3ac012;
      }
      return _0x4cd4ad;
    }
    randomPattern(_0x369f7e, _0x4006d8 = "abcdef0123456789") {
      let _0x3140cf = "";
      for (let _0x8e9314 of _0x369f7e) {
        if (_0x8e9314 == "x") {
          _0x3140cf += _0x4006d8.charAt(Math.floor(Math.random() * _0x4006d8.length));
        } else {
          _0x8e9314 == "X" ? _0x3140cf += _0x4006d8.charAt(Math.floor(Math.random() * _0x4006d8.length)).toUpperCase() : _0x3140cf += _0x8e9314;
        }
      }
      return _0x3140cf;
    }
    randomUuid() {
      return this.randomPattern("xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx");
    }
    randomString(_0x33254d, _0x5f4306 = "abcdef0123456789") {
      let _0x440af6 = "";
      for (let _0x475f61 = 0; _0x475f61 < _0x33254d; _0x475f61++) {
        _0x440af6 += _0x5f4306.charAt(Math.floor(Math.random() * _0x5f4306.length));
      }
      return _0x440af6;
    }
    randomList(_0x4242c3) {
      let _0x35c76e = Math.floor(Math.random() * _0x4242c3.length);
      return _0x4242c3[_0x35c76e];
    }
    wait(_0x1dc9b5) {
      return new Promise(_0x54d822 => setTimeout(_0x54d822, _0x1dc9b5));
    }
    async exitNow() {
      await this.showmsg();
      let _0x4210ea = Date.now(),
        _0x52abd1 = (_0x4210ea - this.startTime) / 1000;
      this.log("");
      const _0x4bb8d6 = {
        time: true
      };
      this.log("[" + this.name + "]运行结束，共运行了" + _0x52abd1 + "秒", _0x4bb8d6);
      process.exit(0);
    }
    normalize_time(_0x2e4fd9, _0x6f3e21 = {}) {
      let _0x2a3018 = _0x6f3e21.len || this.default_timestamp_len;
      _0x2e4fd9 = _0x2e4fd9.toString();
      let _0x54eeae = _0x2e4fd9.length;
      while (_0x54eeae < _0x2a3018) {
        _0x2e4fd9 += "0";
      }
      _0x54eeae > _0x2a3018 && (_0x2e4fd9 = _0x2e4fd9.slice(0, 13));
      return parseInt(_0x2e4fd9);
    }
    async wait_until(_0x3145a4, _0x3938d8 = {}) {
      let _0x155654 = _0x3938d8.logger || this,
        _0x808a8f = _0x3938d8.interval || this.default_wait_interval,
        _0x1929a1 = _0x3938d8.limit || this.default_wait_limit,
        _0x4fa992 = _0x3938d8.ahead || this.default_wait_ahead;
      if (typeof _0x3145a4 == "string" && _0x3145a4.includes(":")) {
        if (_0x3145a4.includes("-")) {
          _0x3145a4 = new Date(_0x3145a4).getTime();
        } else {
          let _0xbcf425 = this.time("yyyy-MM-dd ");
          _0x3145a4 = new Date(_0xbcf425 + _0x3145a4).getTime();
        }
      }
      let _0x44ad11 = this.normalize_time(_0x3145a4) - _0x4fa992,
        _0x213d55 = this.time("hh:mm:ss.S", _0x44ad11),
        _0x64f4d7 = Date.now();
      _0x64f4d7 > _0x44ad11 && (_0x44ad11 += 86400000);
      let _0x539462 = _0x44ad11 - _0x64f4d7;
      if (_0x539462 > _0x1929a1) {
        const _0x533822 = {
          time: true
        };
        _0x155654.log("离目标时间[" + _0x213d55 + "]大于" + _0x1929a1 / 1000 + "秒,不等待", _0x533822);
      } else {
        const _0x436e20 = {
          time: true
        };
        _0x155654.log("离目标时间[" + _0x213d55 + "]还有" + _0x539462 / 1000 + "秒,开始等待", _0x436e20);
        while (_0x539462 > 0) {
          let _0x5a2288 = Math.min(_0x539462, _0x808a8f);
          await this.wait(_0x5a2288);
          _0x64f4d7 = Date.now();
          _0x539462 = _0x44ad11 - _0x64f4d7;
        }
        const _0x179ceb = {
          time: true
        };
        _0x155654.log("已完成等待", _0x179ceb);
      }
    }
    async wait_gap_interval(_0x5caf3a, _0x373b08) {
      let _0x5561b7 = Date.now() - _0x5caf3a;
      _0x5561b7 < _0x373b08 && (await this.wait(_0x373b08 - _0x5561b7));
    }
  }(_0x24412c);
}

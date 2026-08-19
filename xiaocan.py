import hashlib
import json
import os
import random
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


#   大模型答题配置，兼容 DeepSeek / 千问 DashScope OpenAI-compatible 接口
LLM_API_KEY = os.getenv("XC_FOOTBALL_LLM_API_KEY", "")
# DeepSeek: https://api.deepseek.com/v1/chat/completions
# 千问:    https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions
LLM_API_URL = os.getenv("XC_FOOTBALL_LLM_API_URL", "https://api.deepseek.com/v1/chat/completions")
LLM_MODEL = os.getenv("XC_FOOTBALL_LLM_MODEL", "deepseek-chat")
LLM_TIMEOUT = int(os.getenv("XC_FOOTBALL_LLM_TIMEOUT", "30"))
LLM_MAX_RETRIES = 3
QBANK_URL = os.getenv("XC_FOOTBALL_QBANK_URL", "http://106.53.12.120:23456").rstrip("/")
QBANK_TOKEN = os.getenv("XC_FOOTBALL_QBANK_TOKEN", "")
QBANK_TIMEOUT = int(os.getenv("XC_FOOTBALL_QBANK_TIMEOUT", "20"))

RPC_URL = "https://gwh.xiaocantech.com/rpc"
COOKIE_ENV = "xcplus"
SERVER_NAME = "MarketingActivityApi"
CHANNEL = 1
HTTP_TIMEOUT = 15
REQUEST_INTERVAL = 2
DEFAULT_THREADS = int(os.getenv("XC_FOOTBALL_THREADS", "3"))
DRAW_STEPS = (3, 9)
EXPIRE_DATE = date(2026, 7, 21)
EXPIRE_MESSAGE = "活动已过期，更多活动请加入饱了么脚本交流群：476250706"

HOME_PAGE_METHOD = "NationalFootballService.HomePageConf"
COMPLETE_TASK_METHOD = "NationalFootballService.CompleteTask"
DRAW_METHOD = "NationalFootballService.FootballGameLottery"
GET_MATCHES_METHOD = "NationalFootballService.GetFootballGameMatches"
EXTRACT_QUESTIONS_METHOD = "NationalFootballService.FootballGameExtractingQuestions"
SUBMIT_ANSWER_METHOD = "NationalFootballService.FootballGameSubmitUserAnswer"

ALREADY_DONE_TEXTS = ("已完成", "已经完成", "限一次", "今日已", "已领取")

DISCLAIMER = (
    "免责声明：本脚本仅供学习和接口调试使用，请遵守平台规则和相关法律法规；\n"
    "所发布的内容仅供学习，禁止用于其他用途，您必须在下载后的24小时内从计算机或手机中完全删除以上内容。严禁产生利益链！\n"
    "一旦使用或复制了任何相关脚本或Script项目的规则，则视为您已接受此免责声明。如您不同意，请马上删除所以相关文件\n"
    "因使用本脚本产生的风险由使用者自行承担。 饱了么脚本交流群：476250706"
)

ANSI_COLORS = {
    "R": "\033[31m",
    "G": "\033[32m",
    "Y": "\033[33m",
    "B": "\033[34m",
    "C": "\033[36m",
    "M": "\033[35m",
    "W": "\033[90m",
    "D": "\033[2m",
    "BOLD": "\033[1m",
    "RST": "\033[0m",
}
ACCOUNT_COLOR_CODES = ["B", "M", "C", "G", "R", "Y"]
PRINT_LOCK = threading.Lock()


def thread_safe_print(*args, **kwargs):
    with PRINT_LOCK:
        print(*args, **kwargs)


def colored(text, *codes):
    prefix = "".join(ANSI_COLORS.get(code, "") for code in codes)
    return f"{prefix}{text}{ANSI_COLORS['RST']}" if prefix else text


def md5_hex(text):
    return hashlib.md5(text.encode()).hexdigest()


def build_retry_adapter():
    retry = Retry(
        total=2,
        connect=2,
        read=2,
        backoff_factor=0.5,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset({"POST"}),
    )
    return HTTPAdapter(max_retries=retry)


def is_finished_task(task):
    status = task.get("status")
    if status is True or status == 1 or status == "1":
        return True
    status_text = "".join(
        str(task.get(key, ""))
        for key in ("status_text", "task_status_text", "button_text", "state_text")
    )
    return "已完成" in status_text or status_text.strip() == "完成"


def is_already_done_message(message):
    return any(text in str(message) for text in ALREADY_DONE_TEXTS)


def pick_int(data, keys):
    if not isinstance(data, dict):
        return None
    for key in keys:
        value = data.get(key)
        if isinstance(value, bool):
            continue
        if isinstance(value, int):
            return value
        if isinstance(value, str) and value.isdigit():
            return int(value)
    return None


def question_text(question):
    return str(question.get("content") or "").strip()


def option_indexes(question):
    options = question.get("options") or []
    indexes = []
    for option in options:
        value = pick_int(option, ("index",))
        if value is not None:
            indexes.append(value)
    return indexes


def normalize_answer(question, answer):
    indexes = option_indexes(question)
    if not indexes:
        return None
    if isinstance(answer, int) and answer in indexes:
        return answer
    if isinstance(answer, str):
        value = answer.strip().upper()
        if value.isdigit() and int(value) in indexes:
            return int(value)
        if len(value) == 1 and "A" <= value <= "Z":
            index = ord(value) - ord("A") + 1
            if index in indexes:
                return index
    return None


def option_content(question, index):
    for option in question.get("options", []) or []:
        if pick_int(option, ("index",)) == index:
            return str(option.get("content") or "")
    return ""


def format_options(question):
    parts = []
    for option in question.get("options", []) or []:
        index = option.get("index")
        content = option.get("content")
        parts.append(f"{index}.{content}")
    return "  ".join(parts)


def extract_json_object(text):
    text = str(text or "").strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:].strip()
    try:
        return json.loads(text)
    except ValueError:
        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end > start:
            return json.loads(text[start: end + 1])
        raise


def build_quiz_prompt(questions):
    compact = []
    for question in questions:
        compact.append(
            {
                "id": question.get("id"),
                "question": question_text(question),
                "options": [
                    {
                        "index": option.get("index"),
                        "content": option.get("content"),
                    }
                    for option in question.get("options", [])
                ],
            }
        )
    return (
        "你是答题助手。请根据常识选择每道单选题的正确选项，只返回 JSON，"
        "格式必须为 {\"answers\":{\"题目id\":选项index}}，不要解释。\n"
        + json.dumps(compact, ensure_ascii=False)
    )


def question_payload(question):
    return {
        "id": question.get("id"),
        "content": question_text(question),
        "options": [
            {
                "index": option.get("index"),
                "content": option.get("content"),
            }
            for option in question.get("options", [])
        ],
    }


def ask_qbank_for_answers(questions):
    if not QBANK_URL:
        return {}
    headers = {"Content-Type": "application/json"}
    if QBANK_TOKEN:
        headers["X-QBank-Token"] = QBANK_TOKEN
    response = requests.post(
        f"{QBANK_URL}/api/quiz/resolve",
        headers=headers,
        data=json.dumps(
            {"questions": [question_payload(question) for question in questions]},
            ensure_ascii=False,
        ).encode("utf-8"),
        timeout=QBANK_TIMEOUT,
    )
    response.raise_for_status()
    data = response.json()
    answers = data.get("answers", {})
    return answers if isinstance(answers, dict) else {}


def push_answer_to_qbank(question, answer_index):
    """将正确答案推送到云题库，返回 True 表示推送成功"""
    if not QBANK_URL:
        return False
    question_id = str(question.get("id", ""))
    if not question_id:
        return False
    if not isinstance(answer_index, int) or answer_index <= 0:
        thread_safe_print(f"  [题库推送] 跳过无效答案 question_id={question_id!r} answer_index={answer_index!r}")
        return False
    headers = {"Content-Type": "application/json"}
    if QBANK_TOKEN:
        headers["X-QBank-Token"] = QBANK_TOKEN
    try:
        resp = requests.post(
            f"{QBANK_URL}/api/quiz/upsert",
            headers=headers,
            data=json.dumps(
                {
                    "question_id": question_id,
                    "question_text": question_text(question),
                    "options_json": json.dumps(
                        question.get("options") or [], ensure_ascii=False
                    ),
                    "answer_index": answer_index,
                    "answer_content": option_content(question, answer_index),
                    "source": "submit",
                },
                ensure_ascii=False,
            ).encode("utf-8"),
            timeout=QBANK_TIMEOUT,
        )
        if resp.status_code >= 400:
            thread_safe_print(f"  [题库推送] [{question_id}] HTTP {resp.status_code}: {resp.text[:200]}")
            return False
        thread_safe_print(f"  [题库推送] [{question_id}] 成功 answer_index={answer_index}")
        return True
    except requests.RequestException as exc:
        thread_safe_print(f"  [题库推送] [{question_id}] 请求失败: {exc}")
        return False


def ask_llm_for_answers(questions):
    if not LLM_API_KEY:
        return {}
    payload = {
        "model": LLM_MODEL,
        "temperature": 0,
        "messages": [
            {
                "role": "system",
                "content": "你只输出合法 JSON，不输出解释、Markdown 或多余文本。",
            },
            {"role": "user", "content": build_quiz_prompt(questions)},
        ],
    }
    response = None
    for attempt in range(1, LLM_MAX_RETRIES + 1):
        try:
            response = requests.post(
                LLM_API_URL,
                headers={
                    "Authorization": f"Bearer {LLM_API_KEY}",
                    "Content-Type": "application/json",
                },
                data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
                timeout=LLM_TIMEOUT,
            )
            if response.status_code in (429, 500, 502, 503, 504) and attempt < LLM_MAX_RETRIES:
                time.sleep(attempt * 2)
                continue
            response.raise_for_status()
            break
        except (requests.Timeout, requests.ConnectionError):
            if attempt >= LLM_MAX_RETRIES:
                raise
            time.sleep(attempt * 2)
    if response is None:
        raise requests.RequestException("大模型请求未返回响应")
    data = response.json()
    content = data["choices"][0]["message"]["content"]
    parsed = extract_json_object(content)
    raw_answers = parsed.get("answers", parsed)
    return raw_answers if isinstance(raw_answers, dict) else {}


def resolve_quiz_answers(questions):
    answers = {}
    qbank_answers = {}
    try:
        qbank_answers = ask_qbank_for_answers(questions)
    except requests.RequestException:
        qbank_answers = {}

    missing_questions = []
    for question in questions:
        raw_question_id = question.get("id")
        question_id = str(raw_question_id)
        candidates = [qbank_answers.get(question_id)]
        if isinstance(raw_question_id, int):
            candidates.append(qbank_answers.get(raw_question_id))
        answer = None
        for candidate in candidates:
            answer = normalize_answer(question, candidate)
            if answer is not None:
                break
        if answer is not None:
            answers[question_id] = answer
        else:
            missing_questions.append(question)

    if not missing_questions:
        return answers

    llm_answers = ask_llm_for_answers(missing_questions)
    for question in missing_questions:
        raw_question_id = question.get("id")
        question_id = str(raw_question_id)
        candidates = [llm_answers.get(question_id)]
        if isinstance(raw_question_id, int):
            candidates.append(llm_answers.get(raw_question_id))
        answer = None
        for candidate in candidates:
            answer = normalize_answer(question, candidate)
            if answer is not None:
                break
        if answer is not None:
            answers[question_id] = answer
    return answers


class FootballBot:
    def __init__(self, cookie, account_label="", color_code="C"):
        user_id, silk_id, token = self.parse_cookie(cookie)
        self.user_id = user_id
        self.silk_id = silk_id
        self.token = token
        self.label = account_label
        self.color_code = color_code
        self.session = requests.Session()
        self.session.mount("https://", build_retry_adapter())
        self.headers = self.build_base_headers()
        self.success = True

    @staticmethod
    def parse_cookie(cookie):
        parts = cookie.strip().split("#")
        if len(parts) != 3:
            raise ValueError("cookie 格式应为: x-vayne#x-teemo#x-sivir")
        if not parts[0].isdigit() or not parts[1].isdigit() or not parts[2]:
            raise ValueError("cookie 内容无效")
        return parts

    def _log(self, *args):
        prefix = colored(f"[{self.label}]", self.color_code, "BOLD")
        thread_safe_print(prefix, *args)

    def _kv(self, key, value, ok=True):
        color = "G" if ok else "R"
        self._log(f"  {colored(key, self.color_code)}  {colored(str(value), color)}")

    def _section(self, title):
        self._log(colored(f"┌─ {title} ─────────────────────────────────────┐", self.color_code))

    def silk_id_as_int(self):
        return int(self.silk_id)

    def build_base_headers(self):
        return {
            "Host": "gwh.xiaocantech.com",
            "x-version": "3.17.1.0",
            "x-vayne": self.user_id,
            "x-platform": "iOS",
            "x-annie": "XC",
            "x-city": os.getenv("XC_FOOTBALL_CITY", "430102"),
            "x-nami": "",
            "x-teemo": self.silk_id,
            "x-garen": "",
            "x-sivir": self.token,
            "x-ashe": "",
            "servername": SERVER_NAME,
            "methodname": HOME_PAGE_METHOD,
            "content-type": "application/json",
            "accept": "application/json, text/plain, */*",
            "origin": "https://gw.hzaiguojiang.com",
            "referer": "https://gw.hzaiguojiang.com/",
            "accept-language": "zh-CN,zh-Hans;q=0.9",
            "user-agent": (
                "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) "
                "AppleWebKit/605.1.15 (KHTML, like Gecko) xcapp;3.17.1;iOS"
            ),
        }

    def refresh_auth_headers(self, method_name):
        request_id = uuid.uuid4().hex
        random_tail_length = max(0, 16 - len(self.silk_id) - 4)
        x_nami = request_id[:4] + self.silk_id + request_id[4: 4 + random_tail_length]
        x_garen = str(int(time.time() * 1000))
        service_method = f"{SERVER_NAME}.{method_name}".lower()
        x_ashe = md5_hex(md5_hex(service_method) + x_garen + x_nami)
        self.headers.update(
            {
                "methodname": method_name,
                "x-nami": x_nami,
                "x-garen": x_garen,
                "x-ashe": x_ashe,
            }
        )

    def base_payload(self, **extra):
        payload = {"silk_id": self.silk_id_as_int(), "channel": CHANNEL}
        payload.update(extra)
        return payload

    def rpc(self, method_name, data):
        self.refresh_auth_headers(method_name)
        payload = json.dumps(data, separators=(",", ":"), ensure_ascii=False)
        response = self.session.post(
            RPC_URL,
            headers=self.headers,
            data=payload.encode("utf-8"),
            timeout=HTTP_TIMEOUT,
        )
        response.raise_for_status()
        try:
            result = response.json()
        except ValueError as exc:
            raise ValueError(f"接口返回不是合法 JSON: {method_name}") from exc
        if not isinstance(result, dict):
            raise ValueError(f"接口返回格式异常: {method_name}")
        return result

    def fetch_home_page(self):
        response = self.rpc(HOME_PAGE_METHOD, self.base_payload())
        status = response.get("status", {})
        if status.get("code") != 0:
            self._kv("活动", f"获取失败 [{status.get('msg', response)}]", ok=False)
            return {}
        return response

    def extract_tasks(self, home_page):
        tasks = self.quiz_conf(home_page).get("task_list") or []
        return tasks if isinstance(tasks, list) else []

    @staticmethod
    def quiz_conf(home_page):
        return home_page.get("quiz_conf") or {}

    @staticmethod
    def lottery_conf(home_page):
        return home_page.get("lottery_conf") or {}

    def activity_id(self, home_page):
        return pick_int(self.lottery_conf(home_page), ("activity_id",)) or 242

    def quiz_left(self, home_page):
        return pick_int(self.quiz_conf(home_page), ("quiz_left",)) or 0

    def quiz_activity_id(self, home_page):
        return pick_int(self.quiz_conf(home_page), ("activity_id",)) or 232

    def completed_task_count(self, home_page):
        return sum(1 for task in self.extract_tasks(home_page) if is_finished_task(task))

    def drawn_count(self, home_page):
        return pick_int(self.lottery_conf(home_page), ("reward_day_count",)) or 0

    def complete_tasks(self):
        self._section("任务")
        home_page = self.fetch_home_page()
        tasks = self.extract_tasks(home_page)
        if not tasks:
            self._kv("任务", "未获取到任务列表", ok=False)
            self.success = False
            return

        self._kv("任务", f"发现 {len(tasks)} 个，可用次数 {self.quiz_left(home_page)}")
        for task in tasks:
            task_type = pick_int(task, ("task_type", "type"))
            task_name = str(task.get("task_name") or task.get("name") or "")
            if task_type is None:
                continue
            if is_finished_task(task):
                self._kv(f"任务[{task_type}]", f"{task_name}：已完成，跳过")
                continue

            ok = self.complete_task(task_type, task_name)
            if not ok:
                self.success = False
            time.sleep(REQUEST_INTERVAL)

    def complete_task(self, task_type, task_name):
        response = self.rpc(
            COMPLETE_TASK_METHOD,
            self.base_payload(action=2, task_type=int(task_type)),
        )
        status = response.get("status", {})
        if status.get("code") == 0:
            self._kv(f"任务[{task_type}]", f"{task_name}：完成")
            return True
        message = status.get("msg", response)
        if is_already_done_message(message):
            self._kv(f"任务[{task_type}]", f"{task_name}：已完成，跳过")
            return True
        self._kv(f"任务[{task_type}]", f"{task_name}：失败 [{message}]", ok=False)
        return False

    def answer_quiz_rounds(self):
        self._section("答题")
        if not QBANK_URL and not LLM_API_KEY:
            self._kv("答题", "未配置云题库地址或大模型 API Key，跳过答题", ok=False)
            return

        home_page = self.fetch_home_page()
        quiz_left = self.quiz_left(home_page)
        activity_id = self.quiz_activity_id(home_page)
        if quiz_left <= 0:
            self._kv("答题", "无可用答题次数")
            return

        self._kv("答题", f"剩余挑战 {quiz_left} 次")
        for _ in range(quiz_left):
            if not self.answer_quiz_once(activity_id):
                self.success = False
                return
            time.sleep(REQUEST_INTERVAL)

    def fetch_quiz_match(self, activity_id):
        response = self.rpc(
            GET_MATCHES_METHOD,
            {"silk_id": self.silk_id_as_int(), "activity_id": int(activity_id)},
        )
        status = response.get("status", {})
        if status.get("code") != 0:
            self._kv("答题", f"获取场次失败 [{status.get('msg', response)}]", ok=False)
            return None
        return pick_int(response, ("matches",)) or 1

    def fetch_questions(self, activity_id, match):
        response = self.rpc(
            EXTRACT_QUESTIONS_METHOD,
            self.base_payload(activity_id=int(activity_id), matches=int(match)),
        )
        status = response.get("status", {})
        if status.get("code") != 0:
            self._kv("答题", f"抽题失败 [{status.get('msg', response)}]", ok=False)
            return []
        questions = response.get("questions") or []
        return questions if isinstance(questions, list) else []

    def answer_quiz_once(self, activity_id):
        match = self.fetch_quiz_match(activity_id)
        if match is None:
            return False

        questions = self.fetch_questions(activity_id, match)
        if not questions:
            self._kv("答题", "未获取到题目", ok=False)
            return False

        try:
            answers = resolve_quiz_answers(questions)
        except requests.RequestException as exc:
            self._kv("答题", f"大模型请求失败 [{exc}]", ok=False)
            return False
        except (KeyError, ValueError, TypeError) as exc:
            self._kv("答题", f"大模型返回解析失败 [{exc}]", ok=False)
            return False

        question_ids = []
        user_answers = []
        missing_titles = []
        for question in questions:
            question_id = question.get("id")
            answer = answers.get(str(question_id))
            if answer is None:
                missing_titles.append(question_text(question))
                continue
            question_ids.append(int(question_id))
            user_answers.append(str(answer))

        if len(question_ids) != len(questions):
            self._kv("答题", f"缺少 {len(missing_titles)} 题答案，跳过提交", ok=False)
            for title in missing_titles[:3]:
                self._kv("缺答案", title, ok=False)
            return False

        question_by_id = {int(question.get("id")): question for question in questions}
        for index, question in enumerate(questions, start=1):
            question_id = int(question.get("id"))
            answer = int(answers[str(question_id)])
            self._kv(
                f"题目{index}",
                f"[{question_id}] {question_text(question)} | {format_options(question)}",
            )
            self._kv(
                f"选择{index}",
                f"{answer}.{option_content(question, answer)}",
            )

        duration = random.randint(45000, 75000)
        response = self.rpc(
            SUBMIT_ANSWER_METHOD,
            {
                "match": int(match),
                "silk_id": self.silk_id_as_int(),
                "activity_id": int(activity_id),
                "duration": duration,
                "question_list": question_ids,
                "user_answer_list": user_answers,
                "return_answers": True,
            },
        )
        status = response.get("status", {})
        if status.get("code") != 0:
            self._kv("答题", f"提交失败 [{status.get('msg', response)}]", ok=False)
            return False

        score = response.get("score", 0)
        correct_num = response.get("correct_num", 0)
        total = len(questions)
        self._kv("答题", f"得分 {score}，正确 {correct_num}/{total}")

        # 把提交时的最终答案（正确或错误）推送回云题库
        for question_id_str, answer_str in zip(question_ids, user_answers):
            qid = str(question_id_str)
            answer = int(answer_str)
            question = question_by_id.get(question_id_str, {})
            push_answer_to_qbank(question, answer)

        wrong_answers = response.get("answer_list") or []
        for wrong in wrong_answers[:3]:
            question_id = pick_int(wrong, ("question_id",))
            question = question_by_id.get(question_id, {})
            correct_answer = normalize_answer(question, wrong.get("correct_answer"))
            self._kv(
                "错题",
                (
                    f"[{question_id}] {question_text(question)} | "
                    f"正确 {correct_answer}.{option_content(question, correct_answer)}"
                ),
                ok=False,
            )
            # 服务器返回正确答案时，纠正云题库中的记录
            if correct_answer is not None:
                push_answer_to_qbank(question, correct_answer)

        return True

    def draw_node_rewards(self):
        self._section("抽奖")
        home_page = self.fetch_home_page()
        done_count = self.completed_task_count(home_page)
        drawn_count = self.drawn_count(home_page)
        self._kv("抽奖", f"已完成任务 {done_count} 个，已抽奖 {drawn_count} 次")

        drawn_any = False
        for index, threshold in enumerate(DRAW_STEPS, start=1):
            if drawn_count >= index:
                continue
            if done_count < threshold:
                self._kv(f"节点[{threshold}]", "未达成")
                continue

            reward_name = self.draw_once(self.activity_id(home_page))
            if not reward_name:
                self.success = False
                return
            drawn_count += 1
            drawn_any = True
            self._kv(f"节点[{threshold}]", f"抽奖成功 [{reward_name}]")
            time.sleep(REQUEST_INTERVAL)

        if not drawn_any:
            self._kv("抽奖", "暂无可用抽奖机会")

    def draw_once(self, activity_id):
        response = self.rpc(
            DRAW_METHOD,
            self.base_payload(activity_id=int(activity_id)),
        )
        status = response.get("status", {})
        if status.get("code") != 0:
            message = status.get("msg", response)
            if is_already_done_message(message):
                self._kv("抽奖", "已抽奖")
            else:
                self._kv("抽奖", f"失败 [{message}]", ok=False)
            return ""
        return response.get("reward_name") or response.get("name") or "未知奖励"

    def run(self):
        self.complete_tasks()
        self.answer_quiz_rounds()
        self.draw_node_rewards()


def _run_one_account(cookie, index, total):
    color = ACCOUNT_COLOR_CODES[(index - 1) % len(ACCOUNT_COLOR_CODES)]
    label = f"账号{index}/{total}"
    try:
        bot = FootballBot(cookie, account_label=label, color_code=color)
        bot.run()
        return (index, bot.success, None)
    except (ValueError, requests.RequestException) as exc:
        bot = FootballBot.__new__(FootballBot)
        bot.label = label
        bot.color_code = color
        bot._kv("异常", str(exc), ok=False)
        return (index, False, str(exc))


def main():
    if date.today() == EXPIRE_DATE:
        thread_safe_print(EXPIRE_MESSAGE)
        return

    thread_safe_print(colored(DISCLAIMER, "D"))
    thread_safe_print()

    cookie_text = os.getenv(COOKIE_ENV, "").strip()
    if not cookie_text:
        thread_safe_print(colored(f"请设置环境变量：{COOKIE_ENV}", "R"))
        return

    cookies = [cookie for cookie in cookie_text.split("@") if cookie.strip()]
    total = len(cookies)
    threads = max(1, min(DEFAULT_THREADS, total))

    thread_safe_print(colored("=" * 50, "C"))
    thread_safe_print(colored("  小蚕全民足球赛 - 多账号并发执行", "C", "BOLD"))
    thread_safe_print(colored(f"  线程数: {threads}  |  账号数: {total}", "C"))
    thread_safe_print(colored("=" * 50, "C"))
    thread_safe_print()

    start_time = time.time()
    results = []
    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = [
            executor.submit(_run_one_account, cookie, i + 1, total)
            for i, cookie in enumerate(cookies)
        ]
        for future in as_completed(futures):
            results.append(future.result())

    elapsed = time.time() - start_time
    results.sort(key=lambda x: x[0])
    ok_count = sum(1 for _, success, _ in results if success)
    fail_count = total - ok_count

    thread_safe_print()
    thread_safe_print(colored("=" * 50, "C"))
    thread_safe_print(colored("  执行完成", "C", "BOLD"))
    thread_safe_print(
        colored("  成功: ", "C")
        + colored(str(ok_count), "G", "BOLD")
        + colored("  |  失败: ", "C")
        + colored(str(fail_count), "R" if fail_count else "C", "BOLD")
        + colored(f"  |  总耗时: {elapsed:.1f}秒", "C")
    )
    for idx, _, error in results:
        if error:
            thread_safe_print(colored(f"  账号{idx} 执行异常: {error}", "R"))
    thread_safe_print(colored("=" * 50, "C"))


if __name__ == "__main__":
    main()

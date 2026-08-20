# -*- coding: utf-8 -*-
"""
通用工具函数：随机测试数据生成、JSON 解析、业务响应校验等。

注意：本模块不包含任何环境相关信息（IP、账号、密码等），
所有环境信息统一从 config.settings 读取。
"""
import random
import string
import time


def unique_suffix(length=4):
    """生成唯一后缀：时间戳末 8 位 + 随机数字，用于避免测试数据冲突。"""
    ts = str(int(time.time() * 1000))[-8:]
    rand = "".join(random.choices(string.digits, k=length))
    return ts + rand


def random_username(prefix="test_user_"):
    """生成随机用户名（字母+数字），避免与已有数据冲突。"""
    return prefix + unique_suffix()


def random_mobile():
    """生成 11 位随机手机号（以 13-19 开头）。"""
    head = random.choice(["13", "14", "15", "16", "17", "18", "19"])
    tail = "".join(random.choices(string.digits, k=9))
    return head + tail


def random_password(length=8):
    """生成指定长度的随机密码（字母+数字）。"""
    chars = string.ascii_letters + string.digits
    return "".join(random.choices(chars, k=length))


def safe_json(resp):
    """将响应解析为 JSON；解析失败时抛出带响应内容的清晰异常。"""
    try:
        return resp.json()
    except ValueError:
        raise ValueError(
            "响应不是合法 JSON: HTTP {}, 内容: {}".format(
                resp.status_code, resp.text[:200]
            )
        )


def assert_business_success(json_data, desc=""):
    """校验业务响应 code == 200，失败时抛出带 code/msg 的断言信息。"""
    if json_data.get("code") != 200:
        raise AssertionError(
            "{}失败: code={}, msg={}".format(
                desc, json_data.get("code"), json_data.get("msg")
            )
        )


def format_response(resp):
    """格式化响应摘要，便于日志输出（不打印 token 等敏感信息）。"""
    return "HTTP {}, body: {}".format(resp.status_code, resp.text[:500])

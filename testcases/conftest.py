# -*- coding: utf-8 -*-
"""
Pytest 夹具（fixture）定义。

提供：
- api_client：会话级 API 客户端（首次请求自动登录、自动携带 token）；
- admin_token：已登录的管理员 token；
- db：会话级数据库连接（用于登录日志等只读校验）；
- random_user：随机生成的测试用户数据（userId/username/password/mobile）。

注意：夹具中不包含任何真实环境信息，所有配置从 config.settings 读取。
"""
import os
import time

import pytest

from common.api_client import APIClient
from common.db_utils import DBUtils
from common.utils import random_mobile, random_password, random_username
from config.settings import BASE_URL

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture(scope="session", autouse=True)
def allure_environment():
    """在 Allure 报告中记录测试环境信息（仅记录非敏感信息）。"""
    result_dir = os.path.join(_PROJECT_ROOT, "reports", "allure-results")
    os.makedirs(result_dir, exist_ok=True)
    env_file = os.path.join(result_dir, "environment.properties")
    with open(env_file, "w", encoding="utf-8") as f:
        f.write("BASE_URL={}\n".format(BASE_URL))
        f.write("Framework=pytest\n")
        f.write("Language=Python\n")
    yield


@pytest.fixture(scope="session")
def api_client():
    """会话级 API 客户端：首次请求时自动登录，结束时关闭会话。"""
    client = APIClient()
    yield client
    client.close()


@pytest.fixture(scope="session")
def admin_token(api_client):
    """返回已登录的管理员 token（首次调用时自动触发登录）。"""
    if not api_client.token:
        api_client.login()
    return api_client.token


@pytest.fixture(scope="session")
def db():
    """会话级数据库连接，用于登录日志等只读校验。"""
    with DBUtils() as database:
        yield database


@pytest.fixture()
def random_user():
    """生成一条唯一的测试用户数据，字段与 /test/user/* 接口的 UserEntity 一致。"""
    return {
        "userId": int(time.time() * 1000) % 100000000,
        "username": random_username(),
        "password": random_password(),
        "mobile": random_mobile(),
    }

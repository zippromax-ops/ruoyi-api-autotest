# -*- coding: utf-8 -*-
"""
API 客户端封装。

职责：
- 自动登录并保存 token，自动携带 Authorization 请求头；
- 请求返回 401 时自动重新登录并重试一次（处理 token 过期）；
- 统一处理网络异常、超时和非 JSON 响应，抛出带可读信息的 ApiError。

测试用例只需调用 get/post/put/delete，无需关心 token 细节。
"""
import requests

from common.logger import get_logger
from config.settings import BASE_URL, LOGIN_URL, ADMIN_USER, ADMIN_PWD, TIMEOUT

logger = get_logger("api_client")


class ApiError(Exception):
    """接口请求或业务异常，message 为可读的错误描述。"""


class APIClient:
    """基于 requests.Session 的接口客户端，自动处理登录鉴权。"""

    def __init__(self, base_url=None, timeout=None):
        self.base_url = (base_url or BASE_URL).rstrip("/")
        self.timeout = timeout or TIMEOUT
        self.token = None
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

    # ---------- 登录与 token 管理 ----------
    def login(self, username=None, password=None):
        """使用管理员账号登录，成功后保存 token 并写入请求头。"""
        # 注意：仅当未传参(None)时使用默认账号；空字符串属于有效测试数据，
        # 不能用 `or` 代替，否则空账号/空密码会被默认值覆盖。
        username = ADMIN_USER if username is None else username
        password = ADMIN_PWD if password is None else password
        try:
            resp = self.session.post(
                LOGIN_URL,
                json={"username": username, "password": password},
                timeout=self.timeout,
            )
        except requests.RequestException as exc:
            raise ApiError("登录请求失败: {}".format(exc))

        data = self._parse_json(resp, "登录")
        if data.get("code") != 200 or not data.get("token"):
            logger.warning(
                "登录失败: user={}, code={}, msg={}".format(
                    username, data.get("code"), data.get("msg")
                )
            )
            raise ApiError(
                "登录失败: code={}, msg={}".format(data.get("code"), data.get("msg"))
            )
        self.token = data["token"]
        self.session.headers["Authorization"] = "Bearer " + self.token
        logger.info("登录成功: user={}".format(username))
        return self.token

    def _ensure_login(self):
        """确保已登录（懒登录：首次请求前自动登录）。"""
        if not self.token:
            self.login()

    # ---------- 核心请求方法 ----------
    def _request(self, method, url, retry=True, **kwargs):
        """发送请求；401 时自动重新登录并重试一次。"""
        self._ensure_login()
        kwargs.setdefault("timeout", self.timeout)
        try:
            resp = self.session.request(method, self.base_url + url, **kwargs)
        except requests.RequestException as exc:
            logger.error("请求异常: {} {} - {}".format(method, url, exc))
            raise ApiError("请求失败 {} {}: {}".format(method, url, exc))

        logger.info("{} {} -> HTTP {}".format(method, url, resp.status_code))
        if resp.status_code == 401 and retry:
            # token 失效：重新登录后重试一次
            self.login()
            return self._request(method, url, retry=False, **kwargs)
        return resp

    @staticmethod
    def _parse_json(resp, desc):
        """解析响应 JSON，失败时抛出清晰异常。"""
        try:
            return resp.json()
        except ValueError:
            raise ApiError(
                "{}响应不是合法 JSON, HTTP {}, 内容: {}".format(
                    desc, resp.status_code, resp.text[:200]
                )
            )

    # ---------- 对外封装 ----------
    def get(self, url, params=None, **kwargs):
        return self._request("GET", url, params=params, **kwargs)

    def post(self, url, json=None, data=None, **kwargs):
        return self._request("POST", url, json=json, data=data, **kwargs)

    def put(self, url, json=None, data=None, **kwargs):
        return self._request("PUT", url, json=json, data=data, **kwargs)

    def delete(self, url, **kwargs):
        return self._request("DELETE", url, **kwargs)

    def close(self):
        """关闭会话，释放连接。"""
        self.session.close()

# -*- coding: utf-8 -*-
"""
登录接口测试用例。

说明（依据实测环境）：
- 后端已关闭验证码（captchaEnabled: false），登录只需 username/password；
- 登录成功返回顶层 token：{"code":200, "msg":"操作成功", "token":"..."}；
- 各类登录失败统一返回：{"code":500, "msg":"用户不存在/密码错误"}；
- 正常/失败登录后，通过 sys_logininfor 日志做数据库校验（方案 A）。
"""
import pytest
import allure

from common.api_client import ApiError
from config.settings import ADMIN_PWD, ADMIN_USER


@allure.feature("登录模块")
class TestLogin:

    @allure.story("正常登录")
    def test_login_success(self, api_client, db):
        """校验管理员使用正确账号密码登录成功，并返回顶层非空 token。"""
        with allure.step("调用登录接口"):
            token = api_client.login(ADMIN_USER, ADMIN_PWD)

        with allure.step("校验 token 非空"):
            assert token, "登录成功但 token 为空"
            assert isinstance(token, str) and len(token) > 0

        with allure.step("数据库校验登录成功日志"):
            assert db.has_login_success(ADMIN_USER), "sys_logininfor 未查到登录成功记录"

    @allure.story("登录失败")
    @pytest.mark.parametrize(
        "username,password",
        [
            ("admin", "admin126"),     # 已注册账号 + 错误密码
            ("admin", ""),             # 已注册账号 + 密码为空
            ("", "admin123"),          # 账号为空
            ("admin123", "admin123"),  # 未注册账号 + 正确格式密码
        ],
        ids=["wrong_password", "empty_password", "empty_username", "unregistered_username"],
    )
    def test_login_failed(self, api_client, db, username, password):
        """校验错误账号/密码登录失败，返回 code=500 且提示用户不存在/密码错误。"""
        with allure.step("调用登录接口并断言抛出 ApiError"):
            with pytest.raises(ApiError) as exc_info:
                api_client.login(username, password)
            message = str(exc_info.value)
            assert "登录失败" in message
            assert "code=500" in message
            assert "用户不存在/密码错误" in message

        with allure.step("数据库校验登录失败日志"):
            assert db.has_login_failure(username), "sys_logininfor 未查到登录失败记录"

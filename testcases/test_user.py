# -*- coding: utf-8 -*-
"""
用户管理模块测试用例（方案 A：/dev-api/test/user/* 接口）。

说明（依据实测与源码确认）：
- 该接口数据保存在后端内存 Map 中（重启即清空），无法做数据库校验；
- save 接口要求 userId 不能为空（否则返回“用户ID不能为空”）；
- 重复 userId 保存会直接覆盖旧数据（已知缺陷，见重复用户名用例注释）；
- 查询/修改/删除不存在的用户返回 code=500 且提示“用户不存在”；
- 用例使用随机唯一数据，并在 finally 中清理测试数据。
"""
import allure

from common.utils import assert_business_success, random_mobile, safe_json


@allure.feature("用户管理模块")
class TestUserAPI:

    @allure.story("查询用户列表")
    def test_user_list_success(self, api_client):
        """校验查询用户列表成功，返回用户数组且包含种子用户 admin/ry。"""
        resp = api_client.get("/test/user/list")
        data = safe_json(resp)
        assert_business_success(data, "查询用户列表")

        users = data["data"]
        assert isinstance(users, list), "data 应为用户数组"
        usernames = [u.get("username") for u in users]
        assert "admin" in usernames, "列表未包含 admin"
        assert "ry" in usernames, "列表未包含 ry"

    @allure.story("查询用户详情")
    def test_user_detail_success(self, api_client):
        """校验按 userId 查询已存在用户（id=1 admin）成功，字段完整。"""
        resp = api_client.get("/test/user/1")
        data = safe_json(resp)
        assert_business_success(data, "查询用户详情")

        user = data["data"]
        assert user["userId"] == 1
        assert user["username"] == "admin"
        assert user["password"]
        assert user["mobile"]

    @allure.story("查询用户详情")
    def test_user_detail_not_found(self, api_client):
        """校验查询不存在的用户返回 code=500 且提示用户不存在。"""
        resp = api_client.get("/test/user/99999999")
        data = safe_json(resp)
        assert data["code"] == 500
        assert "用户不存在" in data["msg"]

    @allure.story("新增用户")
    def test_add_user_success(self, api_client, random_user):
        """校验新增用户成功，并可通过详情接口查询到新用户（结束后清理）。"""
        user = random_user
        try:
            resp = api_client.post("/test/user/save", params=user)
            assert_business_success(safe_json(resp), "新增用户")

            detail = safe_json(api_client.get("/test/user/{}".format(user["userId"])))
            assert_business_success(detail, "查询新增用户")
            assert detail["data"]["username"] == user["username"]
            assert detail["data"]["mobile"] == user["mobile"]
        finally:
            api_client.delete("/test/user/{}".format(user["userId"]))

    @allure.story("新增用户")
    def test_add_user_missing_userid(self, api_client, random_user):
        """校验新增用户缺少 userId 时返回 code=500 且提示用户ID不能为空。"""
        user = random_user
        user.pop("userId")
        resp = api_client.post("/test/user/save", params=user)
        data = safe_json(resp)
        assert data["code"] == 500
        assert "用户ID不能为空" in data["msg"]

    @allure.story("新增用户")
    def test_add_user_duplicate_username(self, api_client, random_user):
        """校验重复用户名场景：按当前真实行为断言（返回 200 且覆盖旧数据）。"""
        # 已知缺陷（见 Excel TC_USER_api_004 实际结果）：重复保存同一 userId
        # 时，预期应拒绝（如 code=403 提示用户已存在），但当前实现直接覆盖旧数据。
        # 按用户要求以实际行为断言，套件保持绿色；后端修复后需改为 code != 200。
        user = random_user
        try:
            resp1 = api_client.post("/test/user/save", params=user)
            assert_business_success(safe_json(resp1), "第一次新增")

            overwrite = dict(user)
            overwrite["mobile"] = random_mobile()
            overwrite["password"] = "overwrite_pwd_123"
            resp2 = api_client.post("/test/user/save", params=overwrite)
            assert_business_success(safe_json(resp2), "重复保存")

            detail = safe_json(api_client.get("/test/user/{}".format(user["userId"])))
            assert detail["data"]["mobile"] == overwrite["mobile"]
            assert detail["data"]["password"] == overwrite["password"]
        finally:
            api_client.delete("/test/user/{}".format(user["userId"]))

    @allure.story("修改用户")
    def test_update_user_success(self, api_client, random_user):
        """校验修改已存在用户成功，修改后详情返回新数据（结束后清理）。"""
        user = random_user
        try:
            api_client.post("/test/user/save", params=user)

            updated = dict(user)
            updated["mobile"] = random_mobile()
            updated["password"] = "updated_pwd_123"
            resp = api_client.put("/test/user/update", json=updated)
            assert_business_success(safe_json(resp), "修改用户")

            detail = safe_json(api_client.get("/test/user/{}".format(user["userId"])))
            assert detail["data"]["mobile"] == updated["mobile"]
            assert detail["data"]["password"] == updated["password"]
        finally:
            api_client.delete("/test/user/{}".format(user["userId"]))

    @allure.story("修改用户")
    def test_update_user_not_found(self, api_client, random_user):
        """校验修改不存在的用户返回 code=500 且提示用户不存在。"""
        user = random_user
        user["userId"] = 99999999
        resp = api_client.put("/test/user/update", json=user)
        data = safe_json(resp)
        assert data["code"] == 500
        assert "用户不存在" in data["msg"]

    @allure.story("删除用户")
    def test_delete_user_success(self, api_client, random_user):
        """校验删除已存在用户成功，删除后详情返回用户不存在（结束后兜底清理）。"""
        user = random_user
        api_client.post("/test/user/save", params=user)
        try:
            resp = api_client.delete("/test/user/{}".format(user["userId"]))
            assert_business_success(safe_json(resp), "删除用户")

            detail = safe_json(api_client.get("/test/user/{}".format(user["userId"])))
            assert detail["code"] == 500, "删除后仍能查到该用户"
        finally:
            api_client.delete("/test/user/{}".format(user["userId"]))

    @allure.story("删除用户")
    def test_delete_user_not_found(self, api_client):
        """校验删除不存在的用户返回 code=500 且提示用户不存在。"""
        resp = api_client.delete("/test/user/99999999")
        data = safe_json(resp)
        assert data["code"] == 500
        assert "用户不存在" in data["msg"]

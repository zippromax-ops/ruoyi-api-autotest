# 用户管理测试
import pytest
import allure
from faker import Faker
from business.user_api import UserAPI
from common.db_utils import DBUtils

fake = Faker()  # 用于生成随机用户名/手机号


@allure.feature("用户管理模块")
class TestUser:

    @allure.story("查询用户列表")
    def test_get_user_list(self):
        api = UserAPI()
        resp = api.get_user_list()

        with allure.step("校验状态码和业务 Code"):
            assert resp.status_code == 200
            assert resp.json()["code"] == 200

        with allure.step("校验返回数据格式"):
            data = resp.json()["data"]
            assert "rows" in data
            assert "total" in data
            assert isinstance(data["rows"], list)
            print(f"查询成功，共 {data['total']} 条记录")

    @allure.story("新增用户")
    @pytest.mark.parametrize("username_prefix", ["test_user_01", "test_user_02"])
    def test_add_user_success(self, username_prefix):
        # 1. 准备数据（使用 faker 生成唯一值，避免冲突）
        username = f"{username_prefix}_{fake.random_number(digits=4)}"
        phone = fake.phone_number()[:11]

        api = UserAPI()
        db = DBUtils()

        with allure.step("执行新增接口"):
            resp = api.add_user(username, f"测试_{username}", phone)
            assert resp.json()["code"] == 200

        with allure.step("校验数据库是否新增成功（硬核验证）"):
            assert db.check_user_exists(username) is True, "数据库未查到该用户，新增失败！"

        with allure.step("清理数据（删除测试用户）"):
            # 注意：这里由于新增时不知道 user_id，先查出来再删（可封装更优雅）
            db.execute_sql(f"DELETE FROM sys_user WHERE user_name = '{username}'")
            db.conn.commit()
            assert db.check_user_exists(username) is False

        db.close()
        print(f"✅ 用户 {username} 测试通过")

    @allure.story("新增用户-异常场景")
    def test_add_user_username_exists(self):
        api = UserAPI()

        with allure.step("尝试添加已存在的用户名 'admin'"):
            resp = api.add_user("admin", "违规新增", "13800001111")

        with allure.step("校验返回错误信息"):
            assert resp.json()["code"] != 200
            assert "用户名" in resp.json()["msg"] or "已存在" in resp.json()["msg"]
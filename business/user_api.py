# 用户管理增删改查
from common.api_client import APIClient

class UserAPI:
    def __init__(self):
        self.client = APIClient()
        self.client.login()  # 实例化时自动登录

    def get_user_list(self, page_num=1, page_size=10):
        params = {"pageNum": page_num, "pageSize": page_size}
        return self.client.get("/system/user/list", params=params)

    def add_user(self, username, nickname, phone, password="123456"):
        payload = {
            "userName": username,
            "nickName": nickname,
            "password": password,
            "phonenumber": phone,
            "status": "0",
            "deptId": 100,
            "roleIds": [2]
        }
        return self.client.post("/system/user", json=payload)

    def delete_user(self, user_id):
        return self.client.delete(f"/system/user/{user_id}")
# 数据库操作（MySQL 校验）
import pymysql
from config.settings import DB_CONFIG

class DBUtils:
    def __init__(self):
        self.conn = pymysql.connect(**DB_CONFIG)

    def get_cursor(self):
        return self.conn.cursor()

    def execute_sql(self, sql):
        cursor = self.get_cursor()
        cursor.execute(sql)
        result = cursor.fetchall()
        cursor.close()
        return result

    def check_user_exists(self, username):
        """校验数据库是否存在某用户"""
        sql = f"SELECT * FROM sys_user WHERE user_name = '{username}'"
        result = self.execute_sql(sql)
        return len(result) > 0

    def close(self):
        self.conn.close()
# -*- coding: utf-8 -*-
"""
数据库工具模块（用于测试数据校验）。

连接信息统一从 config.settings.DB_CONFIG 读取，真实值保存在本地 .env 中，
仓库内不包含任何真实环境信息。

说明：被测的 /test/user/* 接口数据保存在后端内存中（重启即清空），
无法从数据库校验，因此本模块主要用于：
- 登录日志（sys_logininfor）校验：登录成功/失败是否按预期记录；
- sys_user 兜底检查：确认业务库中基础数据存在。
"""
import pymysql

from config.settings import DB_CONFIG


class DBUtils:
    """基于 PyMySQL 的数据库操作封装，提供只读校验方法。"""

    def __init__(self):
        self.conn = pymysql.connect(**DB_CONFIG)

    def query(self, sql, params=None):
        """执行查询并返回所有结果行（使用参数绑定，避免 SQL 注入）。"""
        cursor = self.conn.cursor()
        try:
            cursor.execute(sql, params)
            return cursor.fetchall()
        finally:
            cursor.close()

    # ---------- 登录日志（sys_logininfor） ----------
    def get_latest_login_logs(self, limit=5):
        """查询最近的登录日志，按日志 ID 倒序。"""
        sql = (
            "SELECT info_id, user_name, status, msg, login_time "
            "FROM sys_logininfor ORDER BY info_id DESC LIMIT %s"
        )
        return self.query(sql, (limit,))

    def has_login_success(self, username, limit=10):
        """校验最近 limit 条登录日志中是否存在该用户的登录成功记录(status='0')。"""
        rows = self.query(
            "SELECT info_id FROM sys_logininfor "
            "WHERE user_name = %s AND status = '0' "
            "ORDER BY info_id DESC LIMIT %s",
            (username, limit),
        )
        return bool(rows)

    def has_login_failure(self, username, limit=10):
        """校验最近 limit 条登录日志中是否存在该用户的登录失败记录(status='1')。"""
        rows = self.query(
            "SELECT info_id FROM sys_logininfor "
            "WHERE user_name = %s AND status = '1' "
            "ORDER BY info_id DESC LIMIT %s",
            (username, limit),
        )
        return bool(rows)

    # ---------- 系统用户（sys_user）兜底检查 ----------
    def get_user_by_name(self, username):
        """按用户名查询 sys_user，返回 (user_id, user_name) 列表。"""
        return self.query(
            "SELECT user_id, user_name FROM sys_user WHERE user_name = %s",
            (username,),
        )

    def check_user_exists(self, username):
        """判断 sys_user 中是否存在指定用户。"""
        return bool(self.get_user_by_name(username))

    # ---------- 生命周期 ----------
    def close(self):
        """关闭数据库连接。"""
        self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

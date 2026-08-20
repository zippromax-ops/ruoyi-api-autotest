# -*- coding: utf-8 -*-
"""
项目配置模块。

安全约定：
- 仓库中不保存任何真实环境信息（IP、账号、密码、数据库名等）；
- 真实值统一放在项目根目录的 .env 文件中（已被 .gitignore 忽略，不会提交）；
- 可参考 .env.example 复制生成 .env；
- 系统环境变量优先级高于 .env 中的值。

支持的环境变量：
    RUOYI_BASE_URL        接口基础地址，如 http://<服务器IP>/dev-api
    RUOYI_ADMIN_USER      管理员账号
    RUOYI_ADMIN_PWD       管理员密码
    RUOYI_TIMEOUT         请求超时秒数（默认 15）
    RUOYI_DB_HOST         数据库地址
    RUOYI_DB_PORT         数据库端口（默认 3306）
    RUOYI_DB_USER         数据库账号
    RUOYI_DB_PASSWORD     数据库密码
    RUOYI_DB_NAME         数据库名
    RUOYI_DB_CHARSET      数据库字符集（默认 utf8mb4）
    RUOYI_DB_CONNECT_TIMEOUT  数据库连接超时秒数（默认 5）
"""
import os

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _load_dotenv(path=None):
    """读取项目根目录 .env 文件，不覆盖系统已有的环境变量。"""
    path = path or os.path.join(_PROJECT_ROOT, ".env")
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value


# 优先读取 .env（如有）
_load_dotenv()

# ---------- 接口配置 ----------
# 登录接口地址（验证码已关闭，无需 code/uuid 字段）
BASE_URL = os.getenv("RUOYI_BASE_URL", "").rstrip("/")

# ---------- 管理员账号（用于登录获取 token） ----------
ADMIN_USER = os.getenv("RUOYI_ADMIN_USER", "")
ADMIN_PWD = os.getenv("RUOYI_ADMIN_PWD", "")

# ---------- 请求配置 ----------
TIMEOUT = int(os.getenv("RUOYI_TIMEOUT", "15"))

# ---------- 数据库配置（用于登录日志等校验） ----------
DB_CONFIG = {
    "host": os.getenv("RUOYI_DB_HOST", ""),
    "port": int(os.getenv("RUOYI_DB_PORT", "3306")),
    "user": os.getenv("RUOYI_DB_USER", ""),
    "password": os.getenv("RUOYI_DB_PASSWORD", ""),
    "database": os.getenv("RUOYI_DB_NAME", ""),
    "charset": os.getenv("RUOYI_DB_CHARSET", "utf8mb4"),
    "connect_timeout": int(os.getenv("RUOYI_DB_CONNECT_TIMEOUT", "5")),
}


def _validate():
    """校验必需的环境变量，缺失时给出清晰提示。"""
    required = {
        "RUOYI_BASE_URL": "接口基础地址",
        "RUOYI_ADMIN_USER": "管理员账号",
        "RUOYI_ADMIN_PWD": "管理员密码",
        "RUOYI_DB_HOST": "数据库地址",
        "RUOYI_DB_USER": "数据库账号",
        "RUOYI_DB_PASSWORD": "数据库密码",
        "RUOYI_DB_NAME": "数据库名",
    }
    missing = [name for name, _ in required.items() if not os.getenv(name)]
    if missing:
        raise RuntimeError(
            "缺少必要的环境变量: {}\n"
            "请在项目根目录创建 .env 文件（参考 .env.example），"
            "或设置系统环境变量。".format(", ".join(missing))
        )


_validate()

LOGIN_URL = BASE_URL + "/login"

# RuoYi-Vue 接口自动化测试

基于 **Python + Pytest + Requests + Allure** 的若依（RuoYi-Vue v3.8.8）后台管理系统接口自动化测试项目，覆盖登录模块与用户管理模块共 **15 条用例**。

## 功能特性

- **配置安全**：环境信息（服务地址、账号、数据库）统一从本地 `.env` 读取，仓库中不包含任何真实环境信息，并提供 `.env.example` 模板；
- **API 封装**：`APIClient` 自动登录、自动携带 token、token 过期（401）自动重新登录并重试，统一处理超时与网络异常；
- **数据驱动**：登录失败场景使用 `@pytest.mark.parametrize` 参数化，便于扩展；
- **数据库校验**：登录成功/失败后校验 `sys_logininfor` 日志落库情况；
- **Allure 报告**：自动生成测试报告数据，可一键生成 HTML 报告；
- **一键运行**：`python run.py` 运行全部用例。

## 技术栈

| 组件 | 说明 |
| ---- | ---- |
| Python | 3.6+（本机 3.13 验证） |
| requests | HTTP 请求库 |
| pytest | 测试框架 |
| allure-pytest | 测试报告 |
| PyMySQL | 数据库校验 |

## 项目结构

```text
RuoYi-VUE/
├── config/            # 配置模块（环境变量读取与校验）
├── common/            # 核心封装
│   ├── api_client.py  #   API 客户端（自动登录 / token 刷新）
│   ├── db_utils.py    #   数据库工具（登录日志校验）
│   ├── logger.py      #   日志（控制台 + 文件）
│   └── utils.py       #   随机测试数据 / JSON 工具
├── testcases/         # 测试用例
│   ├── conftest.py    #   Pytest 夹具（api_client / db / random_user）
│   ├── test_login.py  #   登录模块（5 条）
│   └── test_user.py   #   用户管理模块（10 条）
├── reports/           # Allure 报告输出（gitignored）
├── logs/              # 运行日志（gitignored）
├── run.py             # 测试运行入口
├── pytest.ini         # Pytest 配置
├── requirements.txt   # 项目依赖
└── .env.example       # 环境变量模板
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

> 依赖版本按 Python 3.13 锁定；若需在 Python 3.6（如 CentOS 7 默认版本）环境运行，请改用兼容 Python 3.6 的旧版本包。

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并填入真实环境信息：

```bash
cp .env.example .env        # Linux / macOS
copy .env.example .env      # Windows
```

| 变量 | 说明 |
| ---- | ---- |
| `RUOYI_BASE_URL` | 接口基础地址，如 `http://<服务器IP>/dev-api` |
| `RUOYI_ADMIN_USER` / `RUOYI_ADMIN_PWD` | 管理员账号密码（用于获取 token） |
| `RUOYI_DB_HOST` / `RUOYI_DB_PORT` | 数据库地址 / 端口 |
| `RUOYI_DB_USER` / `RUOYI_DB_PASSWORD` | 数据库账号 / 密码 |
| `RUOYI_DB_NAME` | 数据库名（业务库） |

### 3. 运行测试

```bash
python run.py                                # 运行全部用例
python run.py testcases/test_login.py        # 运行指定用例文件
python run.py -k "user"                      # 按关键字筛选用例
```

或直接使用 pytest：

```bash
pytest
```

### 4. 查看报告

运行结束后，测试报告数据位于 `reports/allure-results`；若本机已安装 allure 命令行工具，`run.py` 会自动生成 HTML 报告到 `reports/allure-html`：

```bash
allure open reports/allure-html
```

## 被测接口

| 接口 | 方法 | 说明 |
| ---- | ---- | ---- |
| `/login` | POST | 登录，返回顶层 token（验证码已关闭） |
| `/test/user/list` | GET | 用户列表 |
| `/test/user/{userId}` | GET | 用户详情（不存在返回 code=500） |
| `/test/user/save` | POST | 新增 / 保存用户（userId 不能为空） |
| `/test/user/update` | PUT | 修改用户（不存在返回 code=500） |
| `/test/user/{userId}` | DELETE | 删除用户（不存在返回 code=500） |

说明：用户管理接口的数据保存在后端内存中（重启即清空），无法做数据库级校验，因此数据库校验仅用于登录日志。

## 用例说明

- **登录模块（5 条）**：正常登录（返回顶层 token + 登录日志校验）；错误密码、空密码、空账号、未注册账号 4 个失败场景（断言 code=500 与提示文案 + 登录日志校验）；
- **用户管理模块（10 条）**：用户列表、详情、详情不存在、新增成功、缺少 userId、重复保存（按当前实际行为断言，见下方“已知缺陷”）、修改成功、修改不存在、删除成功、删除不存在；涉及写操作的用例会自动清理测试数据。

## 已知缺陷记录

- **重复保存同一 userId**：预期应拒绝并提示“用户已存在”（如 code=403），当前实现返回 code=200 并覆盖旧数据（对应手工测试记录 `TC_USER_api_004`）。用例按当前实际行为断言以保持套件稳定，后端修复后需同步调整断言。

## 安全说明

- 真实环境信息仅保存在本地 `.env`（已被 `.gitignore` 忽略），请勿提交到仓库；
- 日志与测试报告不记录 token、密码等敏感信息；
- 发布到公开仓库前，请确认提交历史中不包含 `.env` 或真实凭据。

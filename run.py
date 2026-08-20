# -*- coding: utf-8 -*-
"""
测试运行入口。

用法：
    python run.py                          # 运行全部测试
    python run.py testcases/test_login.py  # 运行指定用例文件
    python run.py -k "login"               # 按关键字筛选用例

说明：
- 测试报告数据输出到 reports/allure-results（目录已被 .gitignore 忽略）；
- 若本机已安装 allure 命令行工具，运行结束后自动生成 HTML 报告到
  reports/allure-html。
"""
import os
import subprocess
import sys

import pytest

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
ALLURE_RESULTS_DIR = os.path.join(PROJECT_ROOT, "reports", "allure-results")
ALLURE_HTML_DIR = os.path.join(PROJECT_ROOT, "reports", "allure-html")


def _allure_available():
    """判断本机是否安装了 allure 命令行工具。"""
    try:
        result = subprocess.run(
            ["allure", "--version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=10,
        )
        return result.returncode == 0
    except Exception:
        return False


def generate_allure_report():
    """基于测试结果数据生成 Allure HTML 报告。"""
    subprocess.run(
        [
            "allure", "generate", ALLURE_RESULTS_DIR,
            "-o", ALLURE_HTML_DIR, "--clean",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=120,
        check=False,
    )
    index_file = os.path.join(ALLURE_HTML_DIR, "index.html")
    if os.path.exists(index_file):
        print("Allure HTML 报告已生成: {}".format(index_file))
    else:
        print("Allure HTML 报告生成失败，请确认 allure 命令行工具已安装。")


def main():
    """解析命令行参数并运行 pytest，结束后尝试生成 Allure 报告。"""
    args = sys.argv[1:] or ["testcases"]
    exit_code = pytest.main(args)
    if _allure_available():
        generate_allure_report()
    return exit_code


if __name__ == "__main__":
    sys.exit(main())

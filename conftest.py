# Pytest 夹具（前置后置）
import pytest
import allure

@pytest.fixture(scope="session", autouse=True)
def global_setup():
    """全局前置：报告展示"""
    allure.dynamic.title("RuoYi-Vue 自动化测试报告")
    yield
    print("\n测试执行完毕")
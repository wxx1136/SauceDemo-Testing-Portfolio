import pytest
import time

def run_full_coverage_tests():
    """运行完整的35项测试用例"""
    print("SauceDemo完整自动化测试 - 35项测试用例")
    print("=" * 70)

    test_modules = {
        "用户登录模块": 8,
        "商品管理模块": 8,
        "购物车模块": 8,
        "结算模块": 8,
        "用户界面模块": 3
    }

    print("测试用例分布:")
    total_cases = 0
    for module, count in test_modules.items():
        print(f"   {module}: {count}个测试用例")
        total_cases += count

    print(f"   总计: {total_cases}个测试用例")
    print("=" * 70)

    # 运行测试
    start_time = time.time()

    result = pytest.main([
        "test_full_coverage.py",
        "-v",
        "-s",
        "--html=reports/full_coverage_report.html",
        "--self-contained-html",
        "--tb=short"
    ])

    elapsed_time = time.time() - start_time

    print("=" * 70)
    print(f"总执行时间: {elapsed_time:.2f}秒")
    print(f"测试用例数量: {total_cases}个")

    if result == 0:
        print("所有测试通过！")
        print("详细报告: reports/full_coverage_report.html")
    else:
        print("有测试失败")

    return result

if __name__ == "__main__":
    run_full_coverage_tests()
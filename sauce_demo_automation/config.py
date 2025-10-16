import os
class Config:
    BASE_URL = "https://www.saucedemo.com/"
    TIMEOUT = 10
    # 测试账号
    STANDARD_USER = "standard_user"
    LOCKED_USER = "locked_out_user"
    PROBLEM_USER = "problem_user"
    PASSWORD = "secret_sauce"
    # 用户信息
    FIRST_NAME = "Test"
    LAST_NAME = "User"
    POSTAL_CODE = "12345"
    # 截图路径
    SCREENSHOT_DIR = os.path.join(os.path.dirname(__file__), "screenshots")
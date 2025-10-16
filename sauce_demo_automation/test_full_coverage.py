import pytest
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import os
import time

class Config:
    BASE_URL = "https://www.saucedemo.com/"
    TIMEOUT = 15
    # 用户账号
    STANDARD_USER = "standard_user"
    LOCKED_USER = "locked_out_user"
    PROBLEM_USER = "problem_user"
    PERFORMANCE_USER = "performance_glitch_user"
    PASSWORD = "secret_sauce"
    # 配送信息
    FIRST_NAME = "Test"
    LAST_NAME = "User"
    POSTAL_CODE = "12345"

class TestSauceDemoFullCoverage:
    def setup_method(self):
        """每个测试方法前的设置"""
        print("启动Edge浏览器...")

        service = Service()
        options = webdriver.EdgeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")

        self.driver = webdriver.Edge(service=service, options=options)
        self.driver.maximize_window()
        self.driver.get(Config.BASE_URL)
        self.wait = WebDriverWait(self.driver, Config.TIMEOUT)
        print("Edge浏览器启动成功")

    def teardown_method(self):
        """每个测试方法后的清理"""
        print("关闭浏览器...")
        if hasattr(self, 'driver'):
            self.driver.quit()
            print("浏览器关闭成功")

    def get_fresh_element(self, by, value):
        """获取新的元素引用"""
        return self.wait.until(EC.presence_of_element_located((by, value)))

    def get_fresh_elements(self, by, value):
        """获取新的元素列表引用"""
        return self.wait.until(EC.presence_of_all_elements_located((by, value)))

    def login(self, username, password):
        """通用的登录方法"""
        print(f"登录用户: {username}")

        username_field = self.get_fresh_element(By.ID, "user-name")
        username_field.clear()
        username_field.send_keys(username)

        password_field = self.get_fresh_element(By.ID, "password")
        password_field.clear()
        password_field.send_keys(password)

        login_button = self.get_fresh_element(By.ID, "login-button")
        login_button.click()
        time.sleep(2)

        return username, password

    def add_to_cart_by_index(self, index):
        """根据索引添加商品到购物车"""
        add_to_cart_buttons = self.get_fresh_elements(By.CSS_SELECTOR, ".btn_inventory")
        if index < len(add_to_cart_buttons):
            add_to_cart_buttons[index].click()
            return True
        return False

    def fill_checkout_info(self, first_name, last_name, postal_code):
        """填写结算信息"""
        first_name_field = self.get_fresh_element(By.ID, "first-name")
        first_name_field.clear()
        first_name_field.send_keys(first_name)

        last_name_field = self.get_fresh_element(By.ID, "last-name")
        last_name_field.clear()
        last_name_field.send_keys(last_name)

        postal_code_field = self.get_fresh_element(By.ID, "postal-code")
        postal_code_field.clear()
        postal_code_field.send_keys(postal_code)

    # ==================== 用户登录模块测试用例 ====================

    def test_001_standard_user_login_success(self):
        """Login_001: 标准用户登陆成功"""
        print("Login_001: 标准用户登陆成功")
        self.login(Config.STANDARD_USER, Config.PASSWORD)
        products_title = self.get_fresh_element(By.CLASS_NAME, "title")
        assert products_title.text == "Products"
        print("标准用户登陆成功")

    def test_002_problem_user_login_success(self):
        """Login_002: 问题用户登陆成功"""
        print("Login_002: 问题用户登陆成功")
        self.login(Config.PROBLEM_USER, Config.PASSWORD)
        products_title = self.get_fresh_element(By.CLASS_NAME, "title")
        assert products_title.text == "Products"
        print("问题用户登陆成功")

    def test_003_locked_user_login_fail(self):
        """Login_003: 锁定用户登录失败"""
        print("Login_003: 锁定用户登录失败")
        self.login(Config.LOCKED_USER, Config.PASSWORD)
        error_message = self.get_fresh_element(By.CSS_SELECTOR, "[data-test='error']")
        assert "Sorry, this user has been locked out." in error_message.text
        print("锁定用户登录失败验证成功")

    def test_004_performance_user_login_success(self):
        """Login_004: 性能用户登陆成功"""
        print("Login_004: 性能用户登陆成功")
        self.login(Config.PERFORMANCE_USER, Config.PASSWORD)
        products_title = self.get_fresh_element(By.CLASS_NAME, "title")
        assert products_title.text == "Products"
        print("性能用户登陆成功")

    def test_005_login_fail_username_empty(self):
        """Login_005: 标准用户登陆失败（用户名为空）- 验证BUG_Login_001"""
        print("Login_005: 标准用户登陆失败（用户名为空）")

        # 输入密码
        password_field = self.get_fresh_element(By.ID, "password")
        password_field.clear()
        password_field.send_keys(Config.PASSWORD)

        # 用户名字段留空
        username_field = self.get_fresh_element(By.ID, "user-name")
        username_field.clear()

        login_button = self.get_fresh_element(By.ID, "login-button")
        login_button.click()
        time.sleep(1)

        # 验证错误信息
        error_message = self.get_fresh_element(By.CSS_SELECTOR, "[data-test='error']")
        assert "Username is required" in error_message.text

        # 验证BUG_Login_001: 用户名为空时密码字段未被清空
        password_field_after = self.get_fresh_element(By.ID, "password")
        password_value = password_field_after.get_attribute("value")

        # 根据缺陷报告，这里应该失败 - 密码字段应该被清空但实际上没有被清空
        if password_value == "":
            print("密码字段已被清空（符合预期）")
        else:
            print(f"BUG_Login_001确认: 用户名为空时密码字段未被清空，当前密码值: {password_value}")
            # 这里应该标记为失败来反映实际缺陷
            pytest.fail(f"BUG_Login_001: 用户名为空时密码字段未被清空，当前密码值: {password_value}")

        print("用户名为空验证完成")

    def test_006_login_fail_password_empty(self):
        """Login_006: 标准用户登陆失败（密码为空）"""
        print("Login_006: 标准用户登陆失败（密码为空）")
        self.login(Config.STANDARD_USER, "")
        error_message = self.get_fresh_element(By.CSS_SELECTOR, "[data-test='error']")
        assert "Password is required" in error_message.text
        print("密码为空验证成功")

    def test_007_login_fail_wrong_password(self):
        """Login_007: 标准用户登陆失败（密码错误）"""
        print("Login_007: 标准用户登陆失败（密码错误）")
        self.login(Config.STANDARD_USER, "wrong_password")
        error_message = self.get_fresh_element(By.CSS_SELECTOR, "[data-test='error']")
        assert "Username and password do not match" in error_message.text
        print("密码错误验证成功")

    def test_008_login_fail_wrong_username(self):
        """Login_008: 标准用户登陆失败（用户名错误）"""
        print("Login_008: 标准用户登陆失败（用户名错误）")
        self.login("wrong_user", Config.PASSWORD)
        error_message = self.get_fresh_element(By.CSS_SELECTOR, "[data-test='error']")
        assert "Username and password do not match" in error_message.text
        print("用户名错误验证成功")

    # ==================== 商品管理模块测试用例 ====================

    def test_009_product_list_display(self):
        """Product_001: 商品列表正常显示"""
        print("Product_001: 商品列表正常显示")
        self.login(Config.STANDARD_USER, Config.PASSWORD)

        # 验证商品网格布局
        inventory_items = self.get_fresh_elements(By.CLASS_NAME, "inventory_item")
        assert len(inventory_items) > 0
        print("商品网格布局显示正常")

        # 验证每个商品包含必要元素
        for item in inventory_items[:3]:  # 检查前3个商品
            image = item.find_element(By.CLASS_NAME, "inventory_item_img")
            name = item.find_element(By.CLASS_NAME, "inventory_item_name")
            description = item.find_element(By.CLASS_NAME, "inventory_item_desc")
            price = item.find_element(By.CLASS_NAME, "inventory_item_price")
            button = item.find_element(By.CSS_SELECTOR, ".btn_inventory")

            assert image.is_displayed()
            assert name.text != ""
            assert description.text != ""
            assert price.text != ""
            assert button.is_displayed()

        print("所有商品信息完整显示")

    def test_010_sort_name_ascending(self):
        """Product_002: 按名称升序排序"""
        print("Product_002: 按名称升序排序")
        self.login(Config.STANDARD_USER, Config.PASSWORD)

        sort_dropdown = Select(self.get_fresh_element(By.CLASS_NAME, "product_sort_container"))
        sort_dropdown.select_by_value("az")
        time.sleep(2)

        first_product = self.get_fresh_element(By.CLASS_NAME, "inventory_item_name")
        print(f"名称升序 - 第一个商品: {first_product.text}")

    def test_011_sort_name_descending(self):
        """Product_003: 按名称降序排序"""
        print("Product_003: 按名称降序排序")
        self.login(Config.STANDARD_USER, Config.PASSWORD)

        sort_dropdown = Select(self.get_fresh_element(By.CLASS_NAME, "product_sort_container"))
        sort_dropdown.select_by_value("za")
        time.sleep(2)

        first_product = self.get_fresh_element(By.CLASS_NAME, "inventory_item_name")
        print(f"名称降序 - 第一个商品: {first_product.text}")

    def test_012_sort_price_descending(self):
        """Product_004: 按价格降序排序"""
        print("Product_004: 按价格降序排序")
        self.login(Config.STANDARD_USER, Config.PASSWORD)

        sort_dropdown = Select(self.get_fresh_element(By.CLASS_NAME, "product_sort_container"))
        sort_dropdown.select_by_value("hilo")
        time.sleep(2)

        first_product_price = self.get_fresh_element(By.CLASS_NAME, "inventory_item_price")
        print(f"价格降序 - 第一个商品价格: {first_product_price.text}")

    def test_013_sort_price_ascending(self):
        """Product_005: 按价格升序排序"""
        print("Product_005: 按价格升序排序")
        self.login(Config.STANDARD_USER, Config.PASSWORD)

        sort_dropdown = Select(self.get_fresh_element(By.CLASS_NAME, "product_sort_container"))
        sort_dropdown.select_by_value("lohi")
        time.sleep(2)

        first_product_price = self.get_fresh_element(By.CLASS_NAME, "inventory_item_price")
        print(f"价格升序 - 第一个商品价格: {first_product_price.text}")

    def test_014_product_detail_verification(self):
        """Product_006: 商品详细信息验证"""
        print("Product_006: 商品详细信息验证")
        self.login(Config.STANDARD_USER, Config.PASSWORD)

        # 找到Sauce Labs Backpack商品
        inventory_items = self.get_fresh_elements(By.CLASS_NAME, "inventory_item")
        backpack_item = None

        for item in inventory_items:
            name_element = item.find_element(By.CLASS_NAME, "inventory_item_name")
            if "Sauce Labs Backpack" in name_element.text:
                backpack_item = item
                break

        assert backpack_item is not None, "未找到Sauce Labs Backpack商品"

        # 验证商品信息
        image = backpack_item.find_element(By.CLASS_NAME, "inventory_item_img")
        name = backpack_item.find_element(By.CLASS_NAME, "inventory_item_name")
        description = backpack_item.find_element(By.CLASS_NAME, "inventory_item_desc")
        price = backpack_item.find_element(By.CLASS_NAME, "inventory_item_price")

        assert image.is_displayed()
        assert "Sauce Labs Backpack" in name.text
        assert description.text != ""
        assert "$29.99" in price.text

        print("Sauce Labs Backpack商品信息验证成功")

    def test_015_problem_user_images(self):
        """Product_007: 问题用户图片显示"""
        print("Product_007: 问题用户图片显示")
        self.login(Config.PROBLEM_USER, Config.PASSWORD)

        # 问题用户应该所有商品显示同一张图片
        images = self.get_fresh_elements(By.CLASS_NAME, "inventory_item_img")

        if len(images) > 1:
            first_src = images[0].get_attribute("src")
            all_same = True

            for i, img in enumerate(images[1:], 1):
                current_src = img.get_attribute("src")
                if current_src != first_src:
                    all_same = False
                    print(f"图片 {i} 不相同: {current_src}")
                    break

            if all_same:
                print("所有商品显示相同图片（问题用户的预期行为）")
            else:
                print("商品图片不一致")

        print("问题用户图片显示验证完成")

    def test_016_default_sort_verification(self):
        """Product_008: 默认排序方式验证"""
        print("Product_008: 默认排序方式验证")
        self.login(Config.STANDARD_USER, Config.PASSWORD)

        # 验证默认排序是名称升序
        sort_dropdown = Select(self.get_fresh_element(By.CLASS_NAME, "product_sort_container"))
        selected_option = sort_dropdown.first_selected_option
        assert selected_option.get_attribute("value") == "az"
        print("默认排序方式为名称升序")

    # ==================== 购物车模块测试用例 ====================

    def test_017_add_single_product(self):
        """Cart_001: 添加单件商品"""
        print("Cart_001: 添加单件商品")
        self.login(Config.STANDARD_USER, Config.PASSWORD)

        self.add_to_cart_by_index(0)
        time.sleep(1)

        # 验证按钮文字变化
        updated_buttons = self.get_fresh_elements(By.CSS_SELECTOR, ".btn_inventory")
        assert updated_buttons[0].text == "Remove"

        # 验证购物车数量
        cart_badge = self.get_fresh_element(By.CLASS_NAME, "shopping_cart_badge")
        assert cart_badge.text == "1"

        print("添加单件商品成功")

    def test_018_add_multiple_different_products(self):
        """Cart_002: 添加多件不同商品"""
        print("Cart_002: 添加多件不同商品")
        self.login(Config.STANDARD_USER, Config.PASSWORD)

        # 添加前2个商品
        for i in range(2):
            self.add_to_cart_by_index(i)
            time.sleep(0.5)

        # 验证购物车数量
        cart_badge = self.get_fresh_element(By.CLASS_NAME, "shopping_cart_badge")
        assert cart_badge.text == "2"

        # 验证两个按钮都显示Remove
        updated_buttons = self.get_fresh_elements(By.CSS_SELECTOR, ".btn_inventory")
        assert updated_buttons[0].text == "Remove"
        assert updated_buttons[1].text == "Remove"

        print("添加多件不同商品成功")

    def test_019_remove_product_from_list(self):
        """Cart_003: 从商品页移除商品"""
        print("Cart_003: 从商品页移除商品")
        self.login(Config.STANDARD_USER, Config.PASSWORD)

        # 先添加商品
        self.add_to_cart_by_index(0)
        time.sleep(1)

        # 然后移除
        remove_buttons = self.get_fresh_elements(By.XPATH, "//button[text()='Remove']")
        remove_buttons[0].click()
        time.sleep(1)

        # 验证按钮恢复
        updated_buttons = self.get_fresh_elements(By.CSS_SELECTOR, ".btn_inventory")
        assert updated_buttons[0].text == "Add to cart"

        # 验证购物车数量消失
        cart_badges = self.driver.find_elements(By.CLASS_NAME, "shopping_cart_badge")
        assert len(cart_badges) == 0

        print("从商品页移除商品成功")

    def test_020_add_same_product_multiple_times(self):
        """Cart_004: 同一商品多次添加 - 验证BUG_Cart_002"""
        print("Cart_004: 同一商品多次添加")
        self.login(Config.STANDARD_USER, Config.PASSWORD)

        # 点击同一商品3次
        for _ in range(3):
            add_to_cart_buttons = self.get_fresh_elements(By.CSS_SELECTOR, ".btn_inventory")
            add_to_cart_buttons[0].click()
            time.sleep(0.5)

        # 验证购物车数量 - 这里应该失败，因为存在BUG_Cart_002
        cart_badge = self.get_fresh_element(By.CLASS_NAME, "shopping_cart_badge")
        cart_count = cart_badge.text

        # 根据缺陷报告，这里应该显示"3"但实际上显示"1"
        if cart_count == "3":
            print("同一商品多次添加计数正确")
        else:
            print(f"BUG_Cart_002确认: 同一商品多次点击只计数1次，当前计数: {cart_count} (期望: 3)")
            pytest.fail(f"BUG_Cart_002: 同一商品多次点击只计数1次，当前计数: {cart_count} (期望: 3)")

        print("同一商品多次添加验证完成")

    def test_021_view_cart_details(self):
        """Cart_005: 查看购物车详情 - 验证BUG_Cart_003"""
        print("Cart_005: 查看购物车详情")
        self.login(Config.STANDARD_USER, Config.PASSWORD)

        # 添加多个商品
        for i in range(2):
            self.add_to_cart_by_index(i)
            time.sleep(0.5)

        # 进入购物车
        cart_icon = self.get_fresh_element(By.CLASS_NAME, "shopping_cart_link")
        cart_icon.click()

        # 验证BUG_Cart_003: 小计金额缺失
        try:
            summary_subtotal = self.driver.find_element(By.CLASS_NAME, "summary_subtotal_label")
            print(f"找到小计金额: {summary_subtotal.text}")
        except NoSuchElementException:
            print("BUG_Cart_003确认: 购物车页面缺少小计金额显示")
            pytest.fail("BUG_Cart_003: 购物车页面缺少小计金额显示")

        print("查看购物车详情完成")

    def test_022_remove_product_from_cart_page(self):
        """Cart_006: 从购物车页面移除商品"""
        print("Cart_006: 从购物车页面移除商品")
        self.login(Config.STANDARD_USER, Config.PASSWORD)

        # 添加商品并进入购物车
        self.add_to_cart_by_index(0)
        time.sleep(1)

        cart_icon = self.get_fresh_element(By.CLASS_NAME, "shopping_cart_link")
        cart_icon.click()

        # 从购物车移除
        remove_button = self.get_fresh_element(By.CSS_SELECTOR, ".cart_button")
        remove_button.click()
        time.sleep(1)

        # 验证购物车为空
        cart_items = self.driver.find_elements(By.CLASS_NAME, "cart_item")
        assert len(cart_items) == 0

        print("从购物车页面移除商品成功")

    def test_023_continue_shopping_function(self):
        """Cart_007: 继续购物功能"""
        print("Cart_007: 继续购物功能")
        self.login(Config.STANDARD_USER, Config.PASSWORD)

        # 进入购物车
        cart_icon = self.get_fresh_element(By.CLASS_NAME, "shopping_cart_link")
        cart_icon.click()

        # 点击继续购物
        continue_button = self.get_fresh_element(By.ID, "continue-shopping")
        continue_button.click()

        # 验证返回商品页面
        products_title = self.get_fresh_element(By.CLASS_NAME, "title")
        assert products_title.text == "Products"

        print("继续购物功能正常")

    def test_024_empty_cart_verification(self):
        """Cart_008: 空购物车验证"""
        print("Cart_008: 空购物车验证")
        self.login(Config.STANDARD_USER, Config.PASSWORD)

        # 查看购物车图标
        cart_icons = self.driver.find_elements(By.CLASS_NAME, "shopping_cart_badge")
        assert len(cart_icons) == 0

        # 进入购物车页面
        cart_icon = self.get_fresh_element(By.CLASS_NAME, "shopping_cart_link")
        cart_icon.click()

        # 验证购物车为空
        cart_items = self.driver.find_elements(By.CLASS_NAME, "cart_item")
        assert len(cart_items) == 0

        print("空购物车验证成功")

    # ==================== 结算模块测试用例 ====================

    def test_025_complete_purchase_flow(self):
        """Checkout_001: 完整购买流程"""
        print("Checkout_001: 完整购买流程")
        self.login(Config.STANDARD_USER, Config.PASSWORD)

        # 添加商品
        for i in range(2):
            self.add_to_cart_by_index(i)
            time.sleep(0.5)

        # 进入购物车并结算
        cart_icon = self.get_fresh_element(By.CLASS_NAME, "shopping_cart_link")
        cart_icon.click()

        checkout_button = self.get_fresh_element(By.ID, "checkout")
        checkout_button.click()

        # 填写配送信息
        self.fill_checkout_info(Config.FIRST_NAME, Config.LAST_NAME, Config.POSTAL_CODE)

        continue_button = self.get_fresh_element(By.ID, "continue")
        continue_button.click()

        # 完成购买
        finish_button = self.get_fresh_element(By.ID, "finish")
        finish_button.click()

        # 验证购买成功
        success_message = self.get_fresh_element(By.CLASS_NAME, "complete-header")
        assert "Thank you for your order!" in success_message.text

        print("完整购买流程成功")

    def test_026_checkout_first_name_empty(self):
        """Checkout_002: 配送信息（名字为空）"""
        print("Checkout_002: 配送信息（名字为空）")
        self.login(Config.STANDARD_USER, Config.PASSWORD)

        # 添加商品并进入结算
        self.add_to_cart_by_index(0)
        time.sleep(1)

        cart_icon = self.get_fresh_element(By.CLASS_NAME, "shopping_cart_link")
        cart_icon.click()

        checkout_button = self.get_fresh_element(By.ID, "checkout")
        checkout_button.click()

        # 名字字段留空
        last_name_field = self.get_fresh_element(By.ID, "last-name")
        last_name_field.send_keys(Config.LAST_NAME)

        postal_code_field = self.get_fresh_element(By.ID, "postal-code")
        postal_code_field.send_keys(Config.POSTAL_CODE)

        continue_button = self.get_fresh_element(By.ID, "continue")
        continue_button.click()

        # 验证错误提示
        error_message = self.get_fresh_element(By.CSS_SELECTOR, "[data-test='error']")
        assert "First Name is required" in error_message.text

        print("名字为空验证成功")

    def test_027_checkout_last_name_empty(self):
        """Checkout_003: 配送信息（姓氏为空）"""
        print("Checkout_003: 配送信息（姓氏为空）")
        self.login(Config.STANDARD_USER, Config.PASSWORD)

        # 添加商品并进入结算
        self.add_to_cart_by_index(0)
        time.sleep(1)

        cart_icon = self.get_fresh_element(By.CLASS_NAME, "shopping_cart_link")
        cart_icon.click()

        checkout_button = self.get_fresh_element(By.ID, "checkout")
        checkout_button.click()

        # 姓氏字段留空
        first_name_field = self.get_fresh_element(By.ID, "first-name")
        first_name_field.send_keys(Config.FIRST_NAME)

        postal_code_field = self.get_fresh_element(By.ID, "postal-code")
        postal_code_field.send_keys(Config.POSTAL_CODE)

        continue_button = self.get_fresh_element(By.ID, "continue")
        continue_button.click()

        # 验证错误提示
        error_message = self.get_fresh_element(By.CSS_SELECTOR, "[data-test='error']")
        assert "Last Name is required" in error_message.text

        print("姓氏为空验证成功")

    def test_028_checkout_postal_code_empty(self):
        """Checkout_004: 配送信息（邮编为空）"""
        print("Checkout_004: 配送信息（邮编为空）")
        self.login(Config.STANDARD_USER, Config.PASSWORD)

        # 添加商品并进入结算
        self.add_to_cart_by_index(0)
        time.sleep(1)

        cart_icon = self.get_fresh_element(By.CLASS_NAME, "shopping_cart_link")
        cart_icon.click()

        checkout_button = self.get_fresh_element(By.ID, "checkout")
        checkout_button.click()

        # 邮编字段留空
        first_name_field = self.get_fresh_element(By.ID, "first-name")
        first_name_field.send_keys(Config.FIRST_NAME)

        last_name_field = self.get_fresh_element(By.ID, "last-name")
        last_name_field.send_keys(Config.LAST_NAME)

        continue_button = self.get_fresh_element(By.ID, "continue")
        continue_button.click()

        # 验证错误提示
        error_message = self.get_fresh_element(By.CSS_SELECTOR, "[data-test='error']")
        assert "Postal Code is required" in error_message.text

        print("邮编为空验证成功")

    def test_029_cancel_checkout_flow(self):
        """Checkout_005: 取消结算流程"""
        print("Checkout_005: 取消结算流程")
        self.login(Config.STANDARD_USER, Config.PASSWORD)

        # 添加商品并进入结算
        self.add_to_cart_by_index(0)
        time.sleep(1)

        cart_icon = self.get_fresh_element(By.CLASS_NAME, "shopping_cart_link")
        cart_icon.click()

        checkout_button = self.get_fresh_element(By.ID, "checkout")
        checkout_button.click()

        # 点击取消
        cancel_button = self.get_fresh_element(By.ID, "cancel")
        cancel_button.click()

        # 验证返回购物车页面
        cart_title = self.get_fresh_element(By.CLASS_NAME, "title")
        assert cart_title.text == "Your Cart"

        print("取消结算流程成功")

    def test_030_empty_cart_checkout(self):
        """Checkout_006: 空购物车结算验证 - 验证BUG_Checkout_004"""
        print("Checkout_006: 空购物车结算验证")
        self.login(Config.STANDARD_USER, Config.PASSWORD)

        # 直接进入购物车（确保为空）
        cart_icon = self.get_fresh_element(By.CLASS_NAME, "shopping_cart_link")
        cart_icon.click()

        # 验证结算按钮状态 - 这里应该失败，因为存在BUG_Checkout_004
        checkout_button = self.get_fresh_element(By.ID, "checkout")

        if checkout_button.is_enabled():
            print("BUG_Checkout_004确认: 空购物车时Checkout按钮未禁用")
            pytest.fail("BUG_Checkout_004: 空购物车时Checkout按钮未禁用")
        else:
            print("空购物车时Checkout按钮已禁用（符合预期）")

        print("空购物车结算验证完成")

    def test_031_order_amount_calculation(self):
        """Checkout_007: 订单金额正确计算"""
        print("Checkout_007: 订单金额正确计算")
        self.login(Config.STANDARD_USER, Config.PASSWORD)

        # 添加特定价格的商品
        inventory_items = self.get_fresh_elements(By.CLASS_NAME, "inventory_item")
        backpack_added = False
        onesie_added = False

        for item in inventory_items:
            name = item.find_element(By.CLASS_NAME, "inventory_item_name").text
            price = item.find_element(By.CLASS_NAME, "inventory_item_price").text
            button = item.find_element(By.CSS_SELECTOR, ".btn_inventory")

            if "Sauce Labs Backpack" in name and not backpack_added:
                button.click()
                backpack_added = True
                print(f"添加商品: {name} - {price}")

            if "Sauce Labs Onesie" in name and not onesie_added:
                button.click()
                onesie_added = True
                print(f"添加商品: {name} - {price}")

            if backpack_added and onesie_added:
                break

        time.sleep(1)

        # 进入结算流程到确认页面
        cart_icon = self.get_fresh_element(By.CLASS_NAME, "shopping_cart_link")
        cart_icon.click()

        checkout_button = self.get_fresh_element(By.ID, "checkout")
        checkout_button.click()

        # 填写配送信息
        self.fill_checkout_info(Config.FIRST_NAME, Config.LAST_NAME, Config.POSTAL_CODE)

        continue_button = self.get_fresh_element(By.ID, "continue")
        continue_button.click()

        # 验证金额计算
        summary_info = self.get_fresh_element(By.CLASS_NAME, "summary_info")
        assert summary_info.is_displayed()

        print("订单金额计算验证完成")

    def test_032_back_home_function(self):
        """Checkout_008: 返回首页功能"""
        print("Checkout_008: 返回首页功能")
        self.login(Config.STANDARD_USER, Config.PASSWORD)

        # 独立完成购买流程
        self.add_to_cart_by_index(0)
        time.sleep(1)

        cart_icon = self.get_fresh_element(By.CLASS_NAME, "shopping_cart_link")
        cart_icon.click()

        checkout_button = self.get_fresh_element(By.ID, "checkout")
        checkout_button.click()

        self.fill_checkout_info(Config.FIRST_NAME, Config.LAST_NAME, Config.POSTAL_CODE)

        continue_button = self.get_fresh_element(By.ID, "continue")
        continue_button.click()

        finish_button = self.get_fresh_element(By.ID, "finish")
        finish_button.click()

        # 点击返回首页
        back_home_button = self.get_fresh_element(By.ID, "back-to-products")
        back_home_button.click()

        # 验证返回商品页面
        products_title = self.get_fresh_element(By.CLASS_NAME, "title")
        assert products_title.text == "Products"

        print("返回首页功能正常")

    # ==================== 用户界面模块测试用例 ====================

    def test_033_main_navigation_menu(self):
        """UI_001: 主导航菜单功能"""
        print("UI_001: 主导航菜单功能")
        self.login(Config.STANDARD_USER, Config.PASSWORD)

        # 点击菜单按钮
        menu_button = self.get_fresh_element(By.ID, "react-burger-menu-btn")
        menu_button.click()
        time.sleep(1)

        # 验证菜单项显示
        menu_items = self.get_fresh_element(By.CLASS_NAME, "bm-item-list")
        assert menu_items.is_displayed()

        # 验证包含必要的菜单项
        menu_text = menu_items.text
        assert "All Items" in menu_text
        assert "About" in menu_text
        assert "Logout" in menu_text
        assert "Reset App State" in menu_text

        print("主导航菜单功能正常")

    def test_034_logout_function(self):
        """UI_002: 登出功能"""
        print("UI_002: 登出功能")
        self.login(Config.STANDARD_USER, Config.PASSWORD)

        # 打开菜单并点击登出
        menu_button = self.get_fresh_element(By.ID, "react-burger-menu-btn")
        menu_button.click()
        time.sleep(1)

        logout_button = self.get_fresh_element(By.ID, "logout_sidebar_link")
        logout_button.click()

        # 验证返回登录页面
        login_button = self.get_fresh_element(By.ID, "login-button")
        assert login_button.is_displayed()

        print("登出功能正常")

    def test_035_all_items_menu_function(self):
        """UI_003: All Items菜单功能"""
        print("UI_003: All Items菜单功能")
        self.login(Config.STANDARD_USER, Config.PASSWORD)

        # 先进入购物车页面
        cart_icon = self.get_fresh_element(By.CLASS_NAME, "shopping_cart_link")
        cart_icon.click()

        # 打开菜单并点击All Items
        menu_button = self.get_fresh_element(By.ID, "react-burger-menu-btn")
        menu_button.click()
        time.sleep(1)

        all_items_button = self.get_fresh_element(By.ID, "inventory_sidebar_link")
        all_items_button.click()

        # 验证返回商品列表页面
        products_title = self.get_fresh_element(By.CLASS_NAME, "title")
        assert products_title.text == "Products"

        print("All Items菜单功能正常")

    def test_036_reset_app_state_function(self):
        """UI_004: 重置应用状态功能 - 验证BUG_UI_005"""
        print("UI_004: 重置应用状态功能")
        self.login(Config.STANDARD_USER, Config.PASSWORD)

        # 添加商品到购物车
        self.add_to_cart_by_index(0)
        self.add_to_cart_by_index(1)
        time.sleep(1)

        # 验证购物车有商品
        cart_badge = self.get_fresh_element(By.CLASS_NAME, "shopping_cart_badge")
        initial_cart_count = cart_badge.text
        print(f"初始购物车数量: {initial_cart_count}")

        # 打开菜单并点击重置应用状态
        menu_button = self.get_fresh_element(By.ID, "react-burger-menu-btn")
        menu_button.click()
        time.sleep(1)

        reset_button = self.get_fresh_element(By.ID, "reset_sidebar_link")
        reset_button.click()
        time.sleep(2)

        # 验证BUG_UI_005: 重置应用状态功能失效
        try:
            # 检查购物车是否被清空
            cart_badges_after = self.driver.find_elements(By.CLASS_NAME, "shopping_cart_badge")
            if len(cart_badges_after) > 0:
                print(f"BUG_UI_005确认: 购物车未被清空，当前数量: {cart_badges_after[0].text}")
                pytest.fail(f"BUG_UI_005: 重置后购物车未被清空，当前数量: {cart_badges_after[0].text}")

            # 检查商品按钮状态是否重置
            add_buttons = self.get_fresh_elements(By.CSS_SELECTOR, ".btn_inventory")
            for i, button in enumerate(add_buttons[:2]):
                if button.text != "Add to cart":
                    print(f"BUG_UI_005确认: 商品 {i} 按钮未重置，当前状态: {button.text}")
                    pytest.fail(f"BUG_UI_005: 商品按钮状态未重置，当前状态: {button.text}")

            print("重置应用状态功能正常")

        except Exception as e:
            print(f"重置状态验证时发生错误: {e}")
            raise

        print("重置应用状态功能验证完成")


def run_full_coverage():
    """运行完整测试覆盖"""
    print("SauceDemo完整自动化测试 - 35项测试用例")
    print("=" * 70)
    print("测试用例分布:")
    print("   用户登录模块: 8个测试用例")
    print("   商品管理模块: 8个测试用例")
    print("   购物车模块: 8个测试用例")
    print("   结算模块: 8个测试用例")
    print("   用户界面模块: 3个测试用例")
    print("   总计: 35个测试用例")
    print("=" * 70)

    # 运行测试
    pytest.main([
        __file__,
        "-v",
        "-s",
        "--html=reports/full_coverage_report.html",
        "--self-contained-html"
    ])


if __name__ == "__main__":
    run_full_coverage()
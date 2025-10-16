from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from config import Config

class BasePage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, Config.TIMEOUT)

    def find_element(self, by, value):
        return self.wait.until(EC.presence_of_element_located((by, value)))

    def click_element(self, by, value):
        self.wait.until(EC.element_to_be_clickable((by, value))).click()

    def input_text(self, by, value, text):
        element = self.find_element(by, value)
        element.clear()
        element.send_keys(text)


class LoginPage(BasePage):
    # 定位器
    USERNAME_FIELD = (By.ID, "user-name")
    PASSWORD_FIELD = (By.ID, "password")
    LOGIN_BUTTON = (By.ID, "login-button")
    ERROR_MESSAGE = (By.CSS_SELECTOR, "[data-test='error']")

    def login(self, username, password):
        self.input_text(*self.USERNAME_FIELD, username)
        self.input_text(*self.PASSWORD_FIELD, password)
        self.click_element(*self.LOGIN_BUTTON)

    def get_error_message(self):
        return self.find_element(*self.ERROR_MESSAGE).text


class ProductsPage(BasePage):
    # 定位器
    PRODUCTS_TITLE = (By.CLASS_NAME, "title")
    ADD_TO_CART_BUTTON = (By.CSS_SELECTOR, ".btn_inventory")
    CART_ICON = (By.CLASS_NAME, "shopping_cart_link")
    SORT_DROPDOWN = (By.CLASS_NAME, "product_sort_container")

    def add_first_product_to_cart(self):
        self.click_element(*self.ADD_TO_CART_BUTTON)

    def go_to_cart(self):
        self.click_element(*self.CART_ICON)


class CartPage(BasePage):
    # 定位器
    CART_ITEMS = (By.CLASS_NAME, "cart_item")
    CHECKOUT_BUTTON = (By.ID, "checkout")
    CONTINUE_SHOPPING_BUTTON = (By.ID, "continue-shopping")

    def proceed_to_checkout(self):
        self.click_element(*self.CHECKOUT_BUTTON)


class CheckoutPage(BasePage):
    # 定位器
    FIRST_NAME_FIELD = (By.ID, "first-name")
    LAST_NAME_FIELD = (By.ID, "last-name")
    POSTAL_CODE_FIELD = (By.ID, "postal-code")
    CONTINUE_BUTTON = (By.ID, "continue")
    FINISH_BUTTON = (By.ID, "finish")

    def fill_shipping_info(self, first_name, last_name, postal_code):
        self.input_text(*self.FIRST_NAME_FIELD, first_name)
        self.input_text(*self.LAST_NAME_FIELD, last_name)
        self.input_text(*self.POSTAL_CODE_FIELD, postal_code)
        self.click_element(*self.CONTINUE_BUTTON)

    def complete_purchase(self):
        self.click_element(*self.FINISH_BUTTON)


class CompletePage(BasePage):
    # 定位器
    SUCCESS_MESSAGE = (By.CLASS_NAME, "complete-header")
    BACK_HOME_BUTTON = (By.ID, "back-to-products")

    def get_success_message(self):
        return self.find_element(*self.SUCCESS_MESSAGE).text
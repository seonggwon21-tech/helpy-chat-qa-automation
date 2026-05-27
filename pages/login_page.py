"""
AI Helpy Chat 로그인 페이지(POM) — 검증 전략 및 SSO 로그인 흐름 정의
"""

import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.common.exceptions import TimeoutException

from .base_page import BasePage


class LoginPage(BasePage):
    """AI Helpy Chat 로그인 화면 조작 및 검증 클래스"""

    LOGIN_ID_INPUT = (By.CSS_SELECTOR, "input[type='email']")
    PASSWORD_INPUT = (By.CSS_SELECTOR, "input[type='password']")
    LOGIN_BUTTON = (By.CSS_SELECTOR, "button[type='submit']")

    def __init__(self, driver: WebDriver, base_url: str):
        super().__init__(driver)
        self.base_url = base_url

    @allure.step("로그인 페이지 열기")
    def open(self):
        self.driver.get(self.base_url)

    @allure.step("계정 정보 입력 및 로그인 시도")
    def login(self, login_id: str, password: str):
        self.enter_text(self.LOGIN_ID_INPUT, login_id)
        self.enter_text(self.PASSWORD_INPUT, password)
        self.click(self.LOGIN_BUTTON)

    @allure.step("로그인 성공 여부(URL 기반) 확인")
    def is_login_successful(self) -> bool:
        try:
            self.wait_for_url_contains("ai-helpy-chat")
            self.wait_for_visible((By.CSS_SELECTOR, "button > svg[data-testid='PersonIcon']"))
            return True
        except TimeoutException:
            return False

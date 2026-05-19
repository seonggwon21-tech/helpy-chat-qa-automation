"""
최초 로그인 시 나타나는 약관 동의 및 온보딩 화면을 처리하는 클래스.
"""

import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC

from .base_page import BasePage


class SignupPage(BasePage):
    """약관 동의 및 계정 생성 프로세스 처리 클래스"""

    AGREE_ALL_CHECKBOX = (By.CSS_SELECTOR, "input[type='checkbox']")
    CREATE_ACCOUNT_BUTTON = (By.CSS_SELECTOR, "button[form='signup-form']")

    def __init__(self, driver: WebDriver):
        super().__init__(driver)

    @allure.step("약관 동의 및 계정 생성 완료")
    def agree_and_submit(self):
        """약관 동의 체크(JS 클릭) 및 제출 버튼 클릭"""
        agree_checkbox = self.wait.until(EC.presence_of_element_located(self.AGREE_ALL_CHECKBOX))
        self.driver.execute_script("arguments[0].click();", agree_checkbox)
        self.click(self.CREATE_ACCOUNT_BUTTON)

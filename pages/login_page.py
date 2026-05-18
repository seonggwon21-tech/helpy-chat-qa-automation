"""
로그인 페이지의 UI 요소와 액션을 정의한 Page Object Model 클래스.
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from .base_page import BasePage

class LoginPage(BasePage):
    """헬피챗 로그인 화면 조작 및 검증 클래스"""

    # 로그인 폼 관련 Locators
    LOGIN_ID_INPUT = (By.CSS_SELECTOR, "input[name='loginId']")
    PASSWORD_INPUT = (By.CSS_SELECTOR, "input[name='password']")
    LOGIN_BUTTON = (By.XPATH, "//button[contains(text(), 'Login')]")

    def __init__(self, driver, base_url):
        super().__init__(driver)
        self.base_url = base_url

    def open(self):
        """로그인 페이지 주소로 브라우저 이동 (비로그인 상태면 로그인 화면으로 리다이렉트 됨을 가정)"""
        self.driver.get(self.base_url)

    def login(self, login_id, password):
        """ID와 비밀번호를 입력하고 로그인 시도"""
        self.enter_text(self.LOGIN_ID_INPUT, login_id)
        self.enter_text(self.PASSWORD_INPUT, password)
        self.click(self.LOGIN_BUTTON)

    def is_login_successful(self):
        """로그인 성공 후 URL에 메인 경로가 포함되었는지 확인"""
        try:
            self.wait.until(EC.url_contains("ai-helpy-chat"))
            return True
        except TimeoutException:
            return False

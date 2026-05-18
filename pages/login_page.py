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
        super().__init__(driver) # 부모 클래스의 driver, wait 초기화 활용
        self.base_url = base_url

    def open(self):
        """로그인 페이지 주소로 브라우저 이동 (비로그인 상태면 로그인 화면으로 리다이렉트 됨을 가정)"""
        self.driver.get(self.base_url)

    def login(self, login_id, password):
        """ID와 비밀번호를 입력하고 로그인 시도"""
        self.enter_text(self.LOGIN_ID_INPUT, login_id) # ID 입력
        self.enter_text(self.PASSWORD_INPUT, password) # 비밀번호 입력
        self.click(self.LOGIN_BUTTON)                  # 로그인 버튼 클릭

    def is_login_successful(self):
        """로그인 성공 후 URL에 메인 경로가 포함되었는지 확인"""
        try:
            # 1단계: URL 주소 기반 확인 (가장 추천하는 방식)
            # 로그인 성공 후 도달하는 메인 URL 경로가 나타날 때까지 대기
            self.wait.until(EC.url_contains("ai-helpy-chat"))
            
            # 2단계: (선택사항) 실제 서비스 화면이 그려졌는지 추가 확인
            # 예를 들어 채팅 입력창(textarea)이 나타났는지 확인
            # self.wait.until(EC.visibility_of_element_located((By.TAG_NAME, "textarea")))
            
            return True
        except TimeoutException:
            return False
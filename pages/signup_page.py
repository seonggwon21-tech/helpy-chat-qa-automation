"""
최초 로그인 시 나타나는 약관 동의 및 온보딩 화면을 처리하는 클래스.
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from .base_page import BasePage

class SignupPage(BasePage):
    """약관 동의 및 계정 생성 프로세스 처리 클래스"""

    # MUI 체크박스 및 버튼 Locators
    AGREE_ALL_CHECKBOX = (By.CSS_SELECTOR, "input[type='checkbox']") 
    CREATE_ACCOUNT_BUTTON = (By.CSS_SELECTOR, "button[form='signup-form']")

    def __init__(self, driver):
        super().__init__(driver) # 부모 클래스의 driver, wait 초기화 활용

    def agree_and_submit(self):
        """약관 동의 체크(JS 클릭) 및 제출 버튼 클릭"""
        # 1. Agree All 체크박스 (일반 클릭이 안 될 경우를 대비해 JavaScript Click 사용)
        agree_checkbox = self.wait.until(EC.presence_of_element_located(self.AGREE_ALL_CHECKBOX))
        self.driver.execute_script("arguments[0].click();", agree_checkbox)
        
        # 2. 부모 클래스의 click 메서드를 활용하여 간결하게 작성
        self.click(self.CREATE_ACCOUNT_BUTTON)
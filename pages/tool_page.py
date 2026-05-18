"""
LNB 메뉴에서 도구 탭 진입 등 공통 도구 기능을 정의한 Page Object Model 클래스.
"""

from selenium.webdriver.common.by import By
from .base_page import BasePage

class ToolPage(BasePage):
    """도구 탭 진입 및 도구 공통 기능을 처리하는 클래스"""

    # 도구 관련 Locators 분리
    TOOL_MENU_BUTTON = (By.XPATH, "//span[normalize-space(text())='도구']")

    def __init__(self, driver):
        # 부모 클래스(BasePage)의 driver와 wait(10초) 초기화 활용
        super().__init__(driver)

    def setup_tool_tab(self):
        """도구 탭까지 진입하는 공통 단계"""
        # 부모 클래스의 click 메서드를 활용하여 대기 및 클릭을 한 번에 처리
        self.click(self.TOOL_MENU_BUTTON)
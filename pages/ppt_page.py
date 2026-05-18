"""
ToolPage를 상속받아 도구 메뉴의 하위 기능인
'PPT 생성' 페이지 이동을 담당하는 클래스.
"""

from selenium.webdriver.common.by import By
from pages.tool_page import ToolPage


class PptPage(ToolPage):
    """PPT 생성 페이지 이동 및 제어 클래스 (ToolPage 확장)"""

    # PPT 생성 버튼 Locator
    PPT_GENERATE_MENU = (
        By.XPATH,
        "//*[normalize-space(text())='PPT 생성']"
    )

    def __init__(self, driver):
        # 부모 클래스(ToolPage → BasePage)의 driver/wait 상속
        super().__init__(driver)

    def navigate_to_ppt_page(self):
        """
        도구 탭 진입 후,
        PPT 생성 버튼 클릭하여 페이지 이동
        """

        # ToolPage의 공통 도구 탭 진입 기능 사용
        self.setup_tool_tab()

        # BasePage의 click 메서드 활용
        self.click(self.PPT_GENERATE_MENU)

    def verify_ppt_page_url(self):
        """
        PPT 생성 페이지 URL 검증
        """

        self.wait.until(
            lambda d: "/ai-helpy-chat/tools/" in d.current_url
        )

        current_url = self.driver.current_url

        assert "/ai-helpy-chat/tools/" in current_url, \
            f"PPT 생성 페이지 이동 실패: {current_url}"
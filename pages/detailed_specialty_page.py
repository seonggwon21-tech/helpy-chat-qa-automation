"""
ToolPage를 상속받아 도구 메뉴의 하위 기능인 '세부 특기사항' 페이지 제어를 담당하는 클래스.
"""

from selenium.webdriver.common.by import By
from pages.tool_page import ToolPage  

class DetailedSpecialtyPage(ToolPage): 
    """세부 특기사항 페이지 조작 및 이동 클래스 (ToolPage 확장)"""

    DETAILED_SPECIALTY_MENU = (By.XPATH, "//a[.//p[normalize-space(text())='세부 특기사항']]")

    def __init__(self, driver):
        # 부모인 ToolPage(그리고 최상위 BasePage)의 driver와 10초 대기 설정을 그대로 물려받음
        super().__init__(driver)

    def navigate_to_detailed_specialty(self):
        """
        도구 메뉴 내부 진입 후, 화면에 보이는 '세부 특기사항' 카드를 클릭하여 최종 이동합니다.
        """
        
        # 상속받은 BasePage의 click 기능을 활용해 명시적 대기 후 클릭 처리
        self.click(self.DETAILED_SPECIALTY_MENU)
        
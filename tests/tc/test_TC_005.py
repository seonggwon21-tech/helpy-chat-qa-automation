"""
[TC-005] "+" 버튼 클릭 시 메뉴 노출 검증
- 사전 조건: test 계정으로 로그인된 상태, 새 대화 화면 진입 완료
- 테스트 절차:
    1. 입력창 좌측 "+" 버튼 클릭
    2. 파일 업로드 / 이미지 생성 / PPT 생성 / 웹 검색 메뉴 노출 확인
- 기대 결과:
    파일 업로드 / 이미지 생성 / PPT 생성 / 웹 검색 메뉴가 노출됨
"""

import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from pages.chat_page import ChatPage

logger = logging.getLogger(__name__)


class TestPlusButtonMenu:
    """입력창 "+" 버튼 클릭 시 메뉴 노출 검증 테스트 스위트"""

    PLUS_BUTTON = (By.CSS_SELECTOR, "button:has([data-testid='plusIcon'])")
    MENU_FILE_UPLOAD = (By.CSS_SELECTOR, "li[role='menuitem']:has([data-testid='paperclipIcon'])")
    MENU_IMAGE_CREATE = (By.CSS_SELECTOR, "li[role='menuitem']:has([data-testid='imageIcon'])")
    MENU_PPT_CREATE = (By.CSS_SELECTOR, "li[role='menuitem']:has([data-testid='presentation-screenIcon'])")
    MENU_WEB_SEARCH = (By.CSS_SELECTOR, "li[role='menuitem']:has([data-testid='magnifying-glassIcon'])")

    def test_plus_button_shows_menu(self, logged_in_driver):
        """
        [TC-005] 입력창 좌측 "+" 버튼 클릭 시
        파일 업로드 / 이미지 생성 / PPT 생성 / 웹 검색 메뉴가 노출되어야 한다.
        """
        chat_page = ChatPage(logged_in_driver)

        plus_button = chat_page.wait.until(
            EC.element_to_be_clickable(self.PLUS_BUTTON)
        )
        plus_button.click()
        logger.info('"+" 버튼 클릭 완료')

        menu_items = [
            ("파일 업로드", self.MENU_FILE_UPLOAD),
            ("이미지 생성", self.MENU_IMAGE_CREATE),
            ("PPT 생성",   self.MENU_PPT_CREATE),
            ("웹 검색",    self.MENU_WEB_SEARCH),
        ]

        for label, locator in menu_items:
            element = chat_page.wait.until(
                EC.visibility_of_element_located(locator)
            )
            assert element.is_displayed(), f'"{label}" 메뉴 항목이 노출되지 않았습니다.'
            logger.info(f'"{label}" 메뉴 항목 노출 확인 완료')

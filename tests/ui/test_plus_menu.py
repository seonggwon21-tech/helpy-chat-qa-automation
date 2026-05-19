"""
[TS-024] + 버튼 메뉴 노출 검증
포함 TC: TC_012 (자동화)
비고: TC_013~TC_016 (파일 업로드·이미지 생성·PPT 생성·웹 검색)은 수동 테스트로 진행
"""

import logging
import pytest
import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from pages.chat_page import ChatPage

logger = logging.getLogger(__name__)
pytestmark = pytest.mark.ui

PLUS_BUTTON = (By.CSS_SELECTOR, "button:has([data-testid='plusIcon'])")
MENU_FILE_UPLOAD = (By.CSS_SELECTOR, "li[role='menuitem']:has([data-testid='paperclipIcon'])")
MENU_IMAGE_CREATE = (By.CSS_SELECTOR, "li[role='menuitem']:has([data-testid='imageIcon'])")
MENU_PPT_CREATE = (By.CSS_SELECTOR, "li[role='menuitem']:has([data-testid='presentation-screenIcon'])")
MENU_WEB_SEARCH = (By.CSS_SELECTOR, "li[role='menuitem']:has([data-testid='magnifying-glassIcon'])")


@allure.epic("AI Helpy Chat")
@allure.feature("+ 버튼 메뉴")
@allure.story("TS-024 · + 버튼 메뉴 및 부가 기능 검증")
class TestPlusButtonMenu:

    @allure.title("+ 버튼 클릭 시 4종 메뉴(파일 업로드·이미지 생성·PPT 생성·웹 검색) 노출 확인")
    def test_plus_button_shows_all_menus(self, authenticated_driver):
        chat_page = ChatPage(authenticated_driver)
        chat_page.click(chat_page.NEW_CHAT_BUTTON)

        with allure.step("[TC_012] + 버튼 클릭"):
            chat_page.wait.until(EC.element_to_be_clickable(PLUS_BUTTON)).click()
            logger.info("+ 버튼 클릭 완료")

        with allure.step("[TC_012] 4종 메뉴 전체 노출 확인"):
            menus = [
                ("파일 업로드", MENU_FILE_UPLOAD),
                ("이미지 생성", MENU_IMAGE_CREATE),
                ("PPT 생성",   MENU_PPT_CREATE),
                ("웹 검색",    MENU_WEB_SEARCH),
            ]
            for label, locator in menus:
                element = chat_page.wait.until(EC.visibility_of_element_located(locator))
                assert element.is_displayed(), f'"{label}" 메뉴가 노출되지 않았습니다.'
                logger.info(f'"{label}" 메뉴 노출 확인 완료')

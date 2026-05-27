"""+ 버튼 메뉴 컴포넌트 — 파일 업로드·이미지·PPT·웹 검색 메뉴를 담당."""

from pathlib import PurePosixPath

import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from pages.base_page import BasePage


class PlusMenuComponent(BasePage):
    """채팅 입력창 좌측 + 버튼과 하위 메뉴(파일 업로드·이미지·PPT·웹 검색)를 관리하는 컴포넌트."""

    PLUS_BUTTON = (By.CSS_SELECTOR, "button:has([data-testid='plusIcon'])")
    MENU_FILE_UPLOAD = (By.CSS_SELECTOR, "li[role='menuitem']:has([data-testid='paperclipIcon'])")
    MENU_IMAGE_CREATE = (By.CSS_SELECTOR, "li[role='menuitem']:has([data-testid='imageIcon'])")
    MENU_PPT_CREATE = (By.CSS_SELECTOR, "li[role='menuitem']:has([data-testid='presentation-screenIcon'])")
    MENU_WEB_SEARCH = (By.CSS_SELECTOR, "li[role='menuitem']:has([data-testid='magnifying-glassIcon'])")
    FILE_INPUT = (By.CSS_SELECTOR, "input[type='file']")
    IMAGE_IN_RESPONSE = (By.CSS_SELECTOR, "div.elice-aichat__markdown img")
    PPT_RESULT = (By.XPATH, "//button[contains(., '생성 결과 받기') or contains(., '생성 결과 다운받기')]")
    PPT_DOWNLOAD_BTN = (By.XPATH, "//button[contains(., '생성 결과 받기') or contains(., '생성 결과 다운받기')]")

    def __init__(self, driver: WebDriver):
        super().__init__(driver)

    @allure.step("+ 버튼 메뉴 열기")
    def open_menu(self):
        """+ 버튼을 클릭해 부가 기능 메뉴를 엽니다."""
        self.click(self.PLUS_BUTTON)

    @staticmethod
    def get_file_chip_locator(filename: str) -> tuple[str, str]:
        """업로드된 파일명으로 첨부 칩 로케이터를 동적으로 생성합니다.

        Args:
            filename: 파일 전체 이름 또는 확장자 없는 이름 (예: "test_upload.txt")

        Returns:
            XPath 기반 로케이터 튜플 (By.XPATH, xpath_string)
        """
        stem = PurePosixPath(filename).stem
        return (
            By.XPATH,
            f"//*[contains(text(),'{stem}') or contains(@title,'{stem}')"
            f" or contains(@aria-label,'{stem}') or contains(@data-name,'{stem}')]",
        )

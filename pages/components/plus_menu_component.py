"""+ 버튼 메뉴 컴포넌트 — 파일 업로드·이미지·PPT·웹 검색 메뉴를 담당."""

from pathlib import Path, PurePosixPath

import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC

from pages.base_page import BasePage


class PlusMenuComponent(BasePage):
    """채팅 입력창 좌측 + 버튼과 하위 메뉴(파일 업로드·이미지·PPT·웹 검색)를 관리하는 컴포넌트."""

    PLUS_BUTTON = (By.CSS_SELECTOR, "button:has([data-testid='plusIcon'])")
    PLUS_MENU_POPOVER = (By.CSS_SELECTOR, "ul[role='menu']")
    MENU_FILE_UPLOAD = (By.CSS_SELECTOR, "li[role='menuitem']:has([data-testid='paperclipIcon'])")
    MENU_IMAGE_CREATE = (By.CSS_SELECTOR, "li[role='menuitem']:has([data-testid='imageIcon'])")
    MENU_PPT_CREATE = (By.CSS_SELECTOR, "li[role='menuitem']:has([data-testid='presentation-screenIcon'])")
    MENU_WEB_SEARCH = (By.CSS_SELECTOR, "li[role='menuitem']:has([data-testid='magnifying-glassIcon'])")
    FILE_INPUT = (By.CSS_SELECTOR, "input[type='file']")
    IMAGE_IN_RESPONSE = (By.CSS_SELECTOR, "div.elice-aichat__markdown img")
    # 이미지 생성 응답(assistant 메시지) 위에 hover 시 노출되는 다운로드 버튼
    RESPONSE_DOWNLOAD_BTN = (
        By.CSS_SELECTOR,
        "div[data-variant='assistant'] button:has(svg[data-testid='downloadIcon'])",
    )
    # PPT 생성 모드 선택 시 입력창에 노출되는 모드 칩
    PPT_MODE_CHIP = (By.XPATH, "//*[normalize-space(text())='PPT 생성']")
    PPT_RESULT = (By.XPATH, "//button[contains(., '생성 결과 받기') or contains(., '생성 결과 다운받기')]")
    PPT_DOWNLOAD_BTN = (By.XPATH, "//button[contains(., '생성 결과 받기') or contains(., '생성 결과 다운받기')]")

    def __init__(self, driver: WebDriver):
        super().__init__(driver)

    @allure.step("+ 버튼 메뉴 열기")
    def open_menu(self):
        """+ 버튼을 클릭해 부가 기능 메뉴를 엽니다."""
        self.click(self.PLUS_BUTTON)

    @allure.step("+ 메뉴 항목 선택: {menu_locator}")
    def select_plus_menu_item(self, menu_locator: tuple[str, str]):
        """+ 메뉴를 열고 항목을 클릭한 뒤 팝오버가 닫힐 때까지 대기합니다.

        Firefox 타이밍 이슈 대응: 팝오버 잔재가 다음 동작을 방해하지 않도록
        PLUS_MENU_POPOVER가 DOM에서 사라진 것을 확인한 뒤 반환합니다.
        """
        self.open_menu()
        self.click(menu_locator)
        self.wait_until_invisible(self.PLUS_MENU_POPOVER)

    @allure.step("파일 업로드 (send_keys 풀패스): {file_path}")
    def upload_file(self, file_path):
        """OS 파일 다이얼로그 없이 숨겨진 file input에 절대 경로를 직접 전달합니다."""
        self.select_plus_menu_item(self.MENU_FILE_UPLOAD)
        file_input = self.wait.until(EC.presence_of_element_located(self.FILE_INPUT))
        self.driver.execute_script(
            "arguments[0].removeAttribute('hidden');"
            "arguments[0].style.display='block';"
            "arguments[0].style.visibility='visible';",
            file_input,
        )
        file_input.send_keys(str(Path(file_path).resolve()))

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

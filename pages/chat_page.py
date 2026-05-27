"""
AI Helpy Chat 메인 화면의 UI 요소와 액션을 정의한 Page Object Model 클래스.

TODO(Component Object Pattern): ChatPage가 채팅 입력·플러스 메뉴·LNB 관리를 모두 담당하고 있어
SRP(단일 책임 원칙)가 옅습니다. 추후 다음과 같이 분리할 예정입니다.
  - ChatInputComponent  : 채팅 입력·전송·응답 대기
  - PlusMenuComponent   : + 버튼 메뉴(파일 업로드·이미지·PPT·웹 검색)
  - LnbComponent        : LNB 대화 목록 관리(생성·삭제·이름 변경)
현재는 테스트 파일 수가 적어 단일 클래스로 유지하며, 케이스가 늘어나면 분리합니다.
"""

import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from .base_page import BasePage


class ChatPage(BasePage):
    """AI Helpy Chat 메시지 전송, 플러스 메뉴, LNB 관리 통합 Page Object 클래스"""

    # ── 채팅 입력 영역 ──────────────────────────────────────────────────────
    CHAT_INPUT = (By.CSS_SELECTOR, "textarea[name='input']")
    SEND_BUTTON = (By.CSS_SELECTOR, "button:has(svg[data-testid='arrow-upIcon'])")
    NEW_CHAT_BUTTON = (By.XPATH, "//a[contains(@href, 'ai-helpy-chat') and .//span[text()='새 대화']]")
    LNB_CHAT_ITEMS = (By.CSS_SELECTOR, "a[href*='/ai-helpy-chat/chats/']")
    AI_MESSAGE_CONTENT = (By.CSS_SELECTOR, "div.elice-aichat__markdown[data-status='complete']")
    CHAT_MESSAGE_ELEMENTS = (By.CSS_SELECTOR, "div.elice-aichat__markdown")

    # ── + 버튼 메뉴 (TODO: PlusMenuComponent로 추출 예정) ────────────────────
    PLUS_BUTTON       = (By.CSS_SELECTOR, "button:has([data-testid='plusIcon'])")
    MENU_FILE_UPLOAD  = (By.CSS_SELECTOR, "li[role='menuitem']:has([data-testid='paperclipIcon'])")
    MENU_IMAGE_CREATE = (By.CSS_SELECTOR, "li[role='menuitem']:has([data-testid='imageIcon'])")
    MENU_PPT_CREATE   = (By.CSS_SELECTOR, "li[role='menuitem']:has([data-testid='presentation-screenIcon'])")
    MENU_WEB_SEARCH   = (By.CSS_SELECTOR, "li[role='menuitem']:has([data-testid='magnifying-glassIcon'])")
    FILE_INPUT        = (By.CSS_SELECTOR, "input[type='file']")
    IMAGE_IN_RESPONSE = (By.CSS_SELECTOR, "div.elice-aichat__markdown img")
    PPT_RESULT        = (By.XPATH, "//button[contains(., '생성 결과 받기') or contains(., '생성 결과 다운받기')]")
    PPT_DOWNLOAD_BTN  = (By.XPATH, "//button[contains(., '생성 결과 받기') or contains(., '생성 결과 다운받기')]")

    # ── LNB 대화 목록 관리 (TODO: LnbComponent로 추출 예정) ─────────────────
    LNB_MORE_BUTTON       = (By.XPATH, "//button[.//*[@data-testid='ellipsis-verticalIcon']]")
    LNB_DELETE_BUTTON     = (By.XPATH, "//li[@role='menuitem'][.//*[@data-testid='trashIcon']]")
    CONFIRM_DELETE_BUTTON = (By.CSS_SELECTOR, "div.MuiDialogActions-root button.MuiButton-colorError")

    def __init__(self, driver: WebDriver):
        super().__init__(driver)

    @staticmethod
    def get_file_chip_locator(filename: str) -> tuple[str, str]:
        """업로드된 파일명으로 첨부 칩 로케이터를 동적으로 생성합니다.

        Args:
            filename: 파일 전체 이름 또는 확장자 없는 이름 (예: "test_upload.txt" 또는 "test_upload")

        Returns:
            XPath 기반 로케이터 튜플 (By.XPATH, xpath_string)
        """
        # 확장자 포함 여부와 무관하게 매칭하도록 stem(확장자 제외 이름)을 사용
        from pathlib import PurePosixPath
        stem = PurePosixPath(filename).stem
        return (
            By.XPATH,
            f"//*[contains(text(),'{stem}') or contains(@title,'{stem}')"
            f" or contains(@aria-label,'{stem}') or contains(@data-name,'{stem}')]",
        )

    @allure.step("AI에게 메시지 전송: '{message}'")
    def send_message(self, message: str):
        """텍스트 영역에 메시지를 입력하고 전송 버튼을 클릭합니다."""
        self.enter_text(self.CHAT_INPUT, message)
        self.click(self.SEND_BUTTON)

    @allure.step("AI 생성 완료 응답 대기 및 텍스트 추출")
    def wait_for_ai_response(self, timeout: int = 60) -> str:
        """AI의 응답이 화면에 완전히 노출될 때까지 대기하고 해당 텍스트를 반환합니다."""
        ai_wait = WebDriverWait(self.driver, timeout)
        return ai_wait.until(EC.visibility_of_element_located(self.AI_MESSAGE_CONTENT)).text

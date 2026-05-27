"""LNB(Left Navigation Bar) 컴포넌트 — 대화 목록 생성·삭제·조회를 담당."""

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from pages.base_page import BasePage

# JS로 LNB href를 원자적으로 수집하는 쿼리 (StaleElementReferenceException 방지)
_JS_LNB_HREFS = (
    "return Array.from(document.querySelectorAll("
    "\"a[href*='/ai-helpy-chat/chats/']\")).map(e => e.href)"
)


class LnbComponent(BasePage):
    """좌측 대화 목록(LNB)의 항목 조회·삭제를 관리하는 컴포넌트."""

    LNB_CHAT_ITEMS = (By.CSS_SELECTOR, "a[href*='/ai-helpy-chat/chats/']")
    LNB_MORE_BUTTON = (By.XPATH, "//button[.//*[@data-testid='ellipsis-verticalIcon']]")
    LNB_DELETE_BUTTON = (By.XPATH, "//li[@role='menuitem'][.//*[@data-testid='trashIcon']]")
    CONFIRM_DELETE_BUTTON = (By.CSS_SELECTOR, "div.MuiDialogActions-root button.MuiButton-colorError")

    def __init__(self, driver: WebDriver):
        super().__init__(driver)

    def get_chat_hrefs(self) -> set[str]:
        """현재 LNB에 노출된 대화 항목의 href를 JS로 원자적으로 수집합니다.

        DOM 갱신 중 요소 참조가 무효화되는 StaleElementReferenceException을
        방지하기 위해 Selenium 요소 대신 JavaScript를 사용합니다.

        Returns:
            LNB 대화 항목 href의 집합
        """
        return set(self.driver.execute_script(_JS_LNB_HREFS))

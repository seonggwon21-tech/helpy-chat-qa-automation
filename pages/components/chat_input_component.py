"""채팅 입력 영역 컴포넌트 — 메시지 입력·전송·AI 응답 대기를 담당."""

import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from pages.base_page import BasePage


class ChatInputComponent(BasePage):
    """채팅 입력창, 전송 버튼, AI 응답 영역을 관리하는 컴포넌트."""

    CHAT_INPUT = (By.CSS_SELECTOR, "textarea[name='input']")
    SEND_BUTTON = (By.CSS_SELECTOR, "button:has(svg[data-testid='arrow-upIcon'])")
    NEW_CHAT_BUTTON = (By.XPATH, "//a[contains(@href, 'ai-helpy-chat') and .//span[text()='새 대화']]")
    AI_MESSAGE_CONTENT = (By.CSS_SELECTOR, "div.elice-aichat__markdown[data-status='complete']")
    CHAT_MESSAGE_ELEMENTS = (By.CSS_SELECTOR, "div.elice-aichat__markdown")

    def __init__(self, driver: WebDriver):
        super().__init__(driver)

    @allure.step("새 대화 화면으로 이동")
    def start_new_chat(self):
        """LNB 상단 '새 대화' 버튼을 클릭해 빈 입력 화면으로 전환합니다."""
        self.click(self.NEW_CHAT_BUTTON)

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

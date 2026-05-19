"""
포피싱 메인 채팅 화면의 UI 요소와 액션을 정의한 Page Object Model 클래스.
"""

import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from .base_page import BasePage


class ChatPage(BasePage):
    """포피싱 메시지 전송 및 응답 확인 클래스"""

    CHAT_INPUT = (By.CSS_SELECTOR, "textarea[name='input']")
    SEND_BUTTON = (By.CSS_SELECTOR, "button:has(svg[data-testid='arrow-upIcon'])")
    NEW_CHAT_BUTTON = (By.XPATH, "//a[contains(@href, 'ai-helpy-chat') and .//span[text()='새 대화']]")
    LNB_CHAT_ITEMS = (By.CSS_SELECTOR, "a[href*='/ai-helpy-chat/chats/']")
    AI_MESSAGE_CONTENT = (By.CSS_SELECTOR, "div.elice-aichat__markdown[data-status='complete']")
    CHAT_MESSAGE_ELEMENTS = (By.CSS_SELECTOR, "div.elice-aichat__markdown")

    def __init__(self, driver: WebDriver):
        super().__init__(driver)

    @allure.step("AI에게 메시지 전송: '{message}'")
    def send_message(self, message: str):
        """텍스트 영역에 메시지를 입력하고 전송 버튼을 클릭합니다."""
        self.enter_text(self.CHAT_INPUT, message)
        self.click(self.SEND_BUTTON)

    @allure.step("AI 생성 완료 응답 대기 및 텍스트 추출")
    def wait_for_ai_response(self) -> str:
        """AI의 응답이 화면에 완전히 노출될 때까지 대기하고 해당 텍스트를 반환합니다."""
        return self.get_text(self.AI_MESSAGE_CONTENT)

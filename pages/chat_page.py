"""
AI Helpy Chat 메인 화면의 Page Object — Component Object Pattern 적용.

ChatPage는 세 개의 전담 컴포넌트를 조합하는 파사드(Facade) 역할을 합니다.

  chat_page.chat_input  → ChatInputComponent  : 채팅 입력·전송·AI 응답 대기
  chat_page.plus_menu   → PlusMenuComponent   : + 버튼 메뉴(파일·이미지·PPT·웹 검색)
  chat_page.lnb         → LnbComponent        : LNB 대화 목록 관리(조회·삭제)
"""

import allure
from selenium.webdriver.remote.webdriver import WebDriver

from pages.base_page import BasePage
from pages.components import ChatInputComponent, LnbComponent, PlusMenuComponent


class ChatPage(BasePage):
    """AI Helpy Chat 화면의 파사드 Page Object.

    직접 로케이터를 보유하지 않고, 역할별 컴포넌트에 위임합니다.
    컴포넌트 인스턴스는 공개 속성으로 노출되어 테스트에서 직접 접근할 수 있습니다.
    """

    def __init__(self, driver: WebDriver):
        super().__init__(driver)
        self.chat_input = ChatInputComponent(driver)
        self.plus_menu = PlusMenuComponent(driver)
        self.lnb = LnbComponent(driver)

    # ── 편의 위임 메서드 ──────────────────────────────────────────────────────
    # conftest.py·테스트 공통 시나리오처럼 ChatPage 수준에서 호출하는 경우를 위해
    # 각 컴포넌트의 핵심 액션을 래핑합니다.

    @allure.step("AI에게 메시지 전송: '{message}'")
    def send_message(self, message: str):
        """chat_input 컴포넌트에 위임 — 메시지 입력 후 전송."""
        self.chat_input.send_message(message)

    @allure.step("AI 생성 완료 응답 대기 및 텍스트 추출")
    def wait_for_ai_response(self, timeout: int = 60) -> str:
        """chat_input 컴포넌트에 위임 — AI 응답 완료까지 대기 후 텍스트 반환."""
        return self.chat_input.wait_for_ai_response(timeout)

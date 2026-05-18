"""
[TC-006] Shift+Enter 입력 시 줄바꿈 적용 및 전송 미동작 검증
- 사전 조건: test 계정으로 로그인된 상태
- 테스트 절차:
    1. 텍스트 입력
    2. Shift+Enter 입력
    3. 전송 여부 확인
- 기대 결과:
    줄바꿈만 적용되고 메시지가 전송되지 않음
    (전송 버튼 미동작 + 입력창 내 줄바꿈 확인)
"""

import logging
import pytest
from selenium.webdriver.common.keys import Keys
from pages.chat_page import ChatPage

logger = logging.getLogger(__name__)
pytestmark = pytest.mark.ui


class TestShiftEnterNewline:
    """Shift+Enter 줄바꿈 적용 및 전송 미동작 검증 테스트 스위트"""

    def test_shift_enter_applies_newline_without_sending(self, logged_in_driver):
        """
        [TC-006] 텍스트 입력 후 Shift+Enter를 누르면
        줄바꿈만 적용되고 메시지가 전송되지 않아야 한다.
        """
        chat_page = ChatPage(logged_in_driver)

        test_message = "줄바꿈 테스트"
        input_element = chat_page.enter_text(chat_page.CHAT_INPUT, test_message)
        logger.info(f"텍스트 입력 완료: {test_message}")

        input_element.send_keys(Keys.SHIFT, Keys.ENTER)
        logger.info("Shift+Enter 입력 완료")

        # [검증 1] 입력창에 줄바꿈(\n)이 포함되어 있는지 확인 (전송 미동작)
        input_value = input_element.get_attribute("value")
        assert "\n" in input_value, (
            f"줄바꿈이 적용되지 않았습니다. 현재 value: '{input_value}'"
        )
        logger.info(f"줄바꿈 적용 확인 완료 (value: '{input_value}')")

        # [검증 2] AI 응답 요소가 생성되지 않았는지 확인 (메시지 전송 미동작)
        ai_messages = logged_in_driver.find_elements(*chat_page.CHAT_MESSAGE_ELEMENTS)
        assert len(ai_messages) == 0, (
            f"Shift+Enter 입력 후 메시지가 전송되었습니다. AI 응답 요소 수: {len(ai_messages)}"
        )
        logger.info("메시지 전송 미동작 확인 완료 (AI 응답 요소 없음)")

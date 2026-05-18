"""
[TC-004] 전송 버튼 비활성화 검증
- 사전 조건: test 계정으로 로그인된 상태, 새 대화 화면 진입 완료 후 입력창 빈 상태
- 테스트 절차:
    1. 새 대화 화면 진입
    2. 입력창 빈 상태 확인
    3. 전송 버튼 활성화 여부 확인
- 기대 결과:
    전송 버튼이 비활성화 상태로 표시됨 (disabled 속성 확인 가능)
"""

import logging
from selenium.webdriver.support import expected_conditions as EC
from pages.chat_page import ChatPage

logger = logging.getLogger(__name__)


class TestSendButtonDisabled:
    """입력창 빈 상태에서 전송 버튼 비활성화 검증 테스트 스위트"""

    def test_send_button_disabled_when_input_empty(self, logged_in_driver):
        """
        [TC-004] 새 대화 화면에서 입력창이 비어 있을 때
        전송 버튼이 비활성화(disabled) 상태여야 한다.
        """
        chat_page = ChatPage(logged_in_driver)

        chat_page.click(chat_page.NEW_CHAT_BUTTON)
        logger.info("새 대화 화면 진입 완료")

        # [검증 1] 입력창 빈 상태 확인
        input_element = chat_page.wait.until(
            EC.visibility_of_element_located(chat_page.CHAT_INPUT)
        )
        input_value = input_element.get_attribute("value")
        assert input_value == "", (
            f"입력창이 비어 있지 않습니다. 현재 value: '{input_value}'"
        )
        logger.info("입력창 빈 상태 확인 완료")

        # [검증 2] 전송 버튼 비활성화(disabled) 확인
        send_button = chat_page.wait.until(
            EC.presence_of_element_located(chat_page.SEND_BUTTON)
        )
        is_disabled = send_button.get_attribute("disabled")
        assert is_disabled is not None, (
            "전송 버튼이 활성화 상태입니다. 입력창이 비어 있을 때 disabled 속성이 존재해야 합니다."
        )
        logger.info(f"전송 버튼 비활성화 확인 완료 (disabled='{is_disabled}')")

"""
[TC-001] 새 대화 버튼 클릭 시 화면 전환 및 상태 초기화 검증
- 사전 조건: test 계정으로 로그인된 상태
- 테스트 절차:
    1. '새 대화' 버튼 클릭
    2. 화면 변경 확인
    3. 입력창 value 확인
    4. 대화 영역 메시지 요소 확인
- 기대 결과:
    1. 빈 대화 화면으로 이동
    2. 입력창 초기화 (value = "")
    3. 이전 대화 미표시
"""

import logging
import pytest
from selenium.webdriver.support import expected_conditions as EC
from pages.chat_page import ChatPage

logger = logging.getLogger(__name__)
pytestmark = pytest.mark.ui


class TestNewChatButton:
    """새 대화 버튼 기능 검증 테스트 스위트"""

    def test_new_chat_clears_conversation(self, logged_in_driver):
        """
        [TC-001] 로그인 상태에서 '새 대화' 버튼을 클릭하면
        입력창이 초기화되고 이전 대화가 표시되지 않아야 한다.
        """
        chat_page = ChatPage(logged_in_driver)

        test_message = "안녕하세요, 테스트 메시지입니다."
        chat_page.send_message(test_message)
        chat_page.wait_for_ai_response()
        logger.info(f"사전 메시지 전송 완료: {test_message}")

        current_url = logged_in_driver.current_url
        chat_page.click(chat_page.NEW_CHAT_BUTTON)
        logger.info("'새 대화' 버튼 클릭 완료")

        chat_page.wait.until(EC.url_changes(current_url))
        logger.info("새 대화 페이지로 전환 완료")

        # [검증 1] 입력창 value 초기화 확인
        input_element = chat_page.wait.until(
            EC.visibility_of_element_located(chat_page.CHAT_INPUT)
        )
        input_value = input_element.get_attribute("value")
        assert input_value == "", (
            f"입력창이 초기화되지 않았습니다. 현재 value: '{input_value}'"
        )
        logger.info("입력창 초기화 확인 완료 (value = '')")

        # [검증 2] 대화 영역 메시지 요소 미표시 확인
        message_elements = logged_in_driver.find_elements(*chat_page.CHAT_MESSAGE_ELEMENTS)
        assert len(message_elements) == 0, (
            f"새 대화 화면에 이전 메시지가 {len(message_elements)}개 남아있습니다."
        )
        logger.info("이전 대화 미표시 확인 완료 (메시지 요소 없음)")

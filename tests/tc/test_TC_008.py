"""
[TC-008] 메시지 전송 버튼 클릭 시 입력창 초기화 및 AI 응답 출력 검증
- 사전 조건: test 계정으로 로그인된 상태, 입력창에 텍스트 입력된 상태
- 테스트 절차:
    1. 텍스트 입력
    2. 전송 버튼 클릭
    3. 입력창 초기화 확인
    4. AI 응답 요소 확인
- 기대 결과:
    메시지 전송 후 입력창이 초기화되고 AI 응답이 출력됨
"""

import logging
from selenium.webdriver.support import expected_conditions as EC
from pages.chat_page import ChatPage

logger = logging.getLogger(__name__)


class TestMessageSend:
    """메시지 전송 기능 검증 테스트 스위트"""

    def test_send_message_clears_input_and_shows_response(self, logged_in_driver):
        """
        [TC-008] 텍스트 입력 후 전송 버튼을 클릭하면
        입력창이 초기화되고 AI 응답이 출력되어야 한다.
        """
        chat_page = ChatPage(logged_in_driver)

        # 1. 텍스트 입력
        test_message = "소프트웨어 QA에 대해 10글자 이내로 짧게 설명해줘."
        chat_page.enter_text(chat_page.CHAT_INPUT, test_message)
        logger.info(f"텍스트 입력 완료: {test_message}")

        # 2. 전송 버튼 클릭
        chat_page.click(chat_page.SEND_BUTTON)
        logger.info("전송 버튼 클릭 완료")

        # 3. [검증 1] 입력창 초기화 확인
        input_element = chat_page.wait.until(EC.presence_of_element_located(chat_page.CHAT_INPUT))
        input_value = input_element.get_attribute("value")
        assert input_value == "", (
            f"입력창이 초기화되지 않았습니다. 현재 value: '{input_value}'"
        )
        logger.info("입력창 초기화 확인 완료 (value = '')")

        # 4. [검증 2] AI 응답 요소 출력 확인
        response_text = chat_page.wait_for_ai_response()
        assert response_text, "AI 응답이 출력되지 않았습니다."
        logger.info(f"AI 응답 출력 확인 완료: {response_text}")

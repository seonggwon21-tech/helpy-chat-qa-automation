"""
[TC-003] 기존 대화 클릭 시 내용 유지 검증
- 사전 조건: test 계정으로 로그인된 상태, 기존 대화 1개 이상 존재
- 테스트 절차:
    1. 메시지 전송으로 대화 생성
    2. '새 대화' 버튼 클릭
    3. LNB 목록 확인
    4. 기존 대화 클릭 후 내용 확인
- 기대 결과:
    기존 대화가 LNB 목록에 보존되고 클릭 시 내용이 유지됨
"""

import logging
import pytest
from selenium.webdriver.support import expected_conditions as EC
from pages.chat_page import ChatPage

logger = logging.getLogger(__name__)
pytestmark = pytest.mark.ui


class TestLnbChatHistory:
    """LNB 대화 목록 및 내용 유지 검증 테스트 스위트"""

    def test_previous_chat_preserved_in_lnb(self, logged_in_driver):
        """
        [TC-003] 메시지 전송 후 새 대화로 전환했을 때
        기존 대화가 LNB 목록에 남아있고 클릭 시 내용이 유지되어야 한다.
        """
        chat_page = ChatPage(logged_in_driver)

        test_message = "안녕하세요, 대화 보존 테스트입니다."
        chat_page.send_message(test_message)
        response_text = chat_page.wait_for_ai_response()
        logger.info(f"대화 생성 완료 - 전송: {test_message} / 응답: {response_text}")

        chat_page.click(chat_page.NEW_CHAT_BUTTON)
        logger.info("'새 대화' 버튼 클릭 완료")

        # [검증 1] LNB 목록에 기존 대화 항목 존재 확인
        chat_page.wait.until(EC.presence_of_element_located(chat_page.LNB_CHAT_ITEMS))
        lnb_items = logged_in_driver.find_elements(*chat_page.LNB_CHAT_ITEMS)
        assert len(lnb_items) > 0, "LNB 목록에 기존 대화가 존재하지 않습니다."
        logger.info(f"LNB 목록 확인 완료 - 대화 항목 {len(lnb_items)}개 존재")

        chat_page.wait.until(EC.element_to_be_clickable(chat_page.LNB_CHAT_ITEMS)).click()
        logger.info("LNB 첫 번째 대화 클릭 완료")

        # [검증 2] 클릭 후 AI 응답 내용 유지 확인
        chat_page.wait_for_ai_response()
        message_elements = logged_in_driver.find_elements(*chat_page.CHAT_MESSAGE_ELEMENTS)
        assert len(message_elements) > 0, "기존 대화 클릭 후 이전 내용이 표시되지 않습니다."
        logger.info("대화 내용 유지 확인 완료")

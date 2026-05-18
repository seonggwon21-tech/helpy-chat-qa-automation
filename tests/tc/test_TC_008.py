"""
[TC-008] 새로고침 후 대화 유지 검증
- 사전 조건: test 계정으로 로그인된 상태, 대화 1개 이상 존재
- 테스트 절차:
    1. 메시지 전송 후 페이지 새로고침
    2. LNB 목록 확인
- 기대 결과:
    새로고침 후 기존 대화 목록이 유지됨
"""

import logging
from selenium.webdriver.support import expected_conditions as EC
from pages.chat_page import ChatPage

logger = logging.getLogger(__name__)


class TestChatPreservedAfterRefresh:
    """새로고침 후 대화 유지 검증 테스트 스위트"""

    def test_chat_preserved_after_refresh(self, logged_in_driver):
        """
        [TC-008] 메시지 전송 후 페이지를 새로고침해도
        LNB 목록에 기존 대화가 유지되어야 한다.
        """
        chat_page = ChatPage(logged_in_driver)

        test_message = "새로고침 후 대화 유지 테스트"
        chat_page.send_message(test_message)
        chat_page.wait_for_ai_response()
        logger.info(f"메시지 전송 완료: {test_message}")

        before_hrefs = {
            el.get_attribute("href")
            for el in logged_in_driver.find_elements(*chat_page.LNB_CHAT_ITEMS)
        }
        logger.info(f"새로고침 전 LNB 항목 수: {len(before_hrefs)}")

        logged_in_driver.refresh()
        logger.info("페이지 새로고침 완료")

        # [검증] 새로고침 후 LNB 목록에 기존 대화 항목 유지 확인
        chat_page.wait.until(EC.presence_of_element_located(chat_page.LNB_CHAT_ITEMS))
        after_hrefs = {
            el.get_attribute("href")
            for el in logged_in_driver.find_elements(*chat_page.LNB_CHAT_ITEMS)
        }
        logger.info(f"새로고침 후 LNB 항목 수: {len(after_hrefs)}")

        assert before_hrefs == after_hrefs, (
            f"새로고침 후 대화 목록이 변경되었습니다.\n"
            f"이전: {before_hrefs}\n이후: {after_hrefs}"
        )
        logger.info("새로고침 후 대화 목록 유지 확인 완료")

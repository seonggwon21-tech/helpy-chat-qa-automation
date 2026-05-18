"""
[TC-019] 대화 생성 후 LNB 목록 항목 추가 검증
- 사전 조건: test 계정으로 로그인된 상태
- 테스트 절차:
    1. 메시지 전송 전 LNB 항목 수 기록
    2. 메시지 전송
    3. LNB 항목 수 재확인
- 기대 결과:
    LNB에 새 대화 항목이 추가됨 (전송 전후 LNB 항목 수 비교 검증)
"""

import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from pages.chat_page import ChatPage

logger = logging.getLogger(__name__)


class TestLnbItemAdded:
    """메시지 전송 후 LNB 목록 항목 추가 검증 테스트 스위트"""

    LNB_CHAT_ITEMS = (By.CSS_SELECTOR, "a[href*='/ai-helpy-chat/chats/']")

    def test_new_chat_item_added_to_lnb_after_send(self, logged_in_driver):
        """
        [TC-019] 메시지 전송 후
        LNB 목록에 새 대화 항목이 추가되어야 한다.
        """
        chat_page = ChatPage(logged_in_driver)

        # 1. 전송 전 LNB href 목록 기록
        before_hrefs = {
            el.get_attribute("href")
            for el in logged_in_driver.find_elements(*self.LNB_CHAT_ITEMS)
        }
        logger.info(f"전송 전 LNB 항목 수: {len(before_hrefs)}")

        # 2. 메시지 전송
        test_message = "LNB 목록 추가 테스트"
        chat_page.send_message(test_message)
        logger.info(f"메시지 전송 완료: {test_message}")

        # 3. [검증] 전송 전에 없던 새 href가 LNB에 등장할 때까지 대기
        long_wait = WebDriverWait(logged_in_driver, 60)
        long_wait.until(
            lambda d: any(
                el.get_attribute("href") not in before_hrefs
                for el in d.find_elements(*self.LNB_CHAT_ITEMS)
            )
        )
        after_hrefs = {
            el.get_attribute("href")
            for el in logged_in_driver.find_elements(*self.LNB_CHAT_ITEMS)
        }
        new_hrefs = after_hrefs - before_hrefs
        logger.info(f"새로 추가된 LNB 항목: {new_hrefs}")

        assert len(new_hrefs) == 1, (
            f"LNB에 새 대화 항목이 정확히 1개 추가되지 않았습니다. "
            f"추가된 항목: {new_hrefs}"
        )
        logger.info("LNB 신규 항목 추가 확인 완료")

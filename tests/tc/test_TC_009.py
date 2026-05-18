"""
[TC-009] LNB 대화 삭제 검증
- 사전 조건: test 계정으로 로그인된 상태, 대화 1개 이상 존재
- 테스트 절차:
    1. LNB 항목 삭제 버튼 클릭
    2. 목록 확인
- 기대 결과:
    삭제된 대화가 LNB에서 사라짐
"""

import logging
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from pages.chat_page import ChatPage

logger = logging.getLogger(__name__)
pytestmark = pytest.mark.ui


class TestLnbChatDelete:
    """LNB 대화 삭제 검증 테스트 스위트"""

    LNB_MORE_BUTTON = (By.XPATH, "//button[.//*[@data-testid='ellipsis-verticalIcon']]")
    LNB_DELETE_BUTTON = (By.XPATH, "//li[@role='menuitem'][.//*[@data-testid='trashIcon']]")
    CONFIRM_DELETE_BUTTON = (By.CSS_SELECTOR, "div.MuiDialogActions-root button.MuiButton-colorError")

    def test_chat_deleted_from_lnb(self, logged_in_driver):
        """
        [TC-009] LNB 항목의 삭제 버튼을 클릭하면
        해당 대화가 LNB 목록에서 사라져야 한다.
        """
        chat_page = ChatPage(logged_in_driver)

        # 메시지 전송 전 초기 LNB 항목 수 기록
        initial_hrefs = {
            el.get_attribute("href")
            for el in logged_in_driver.find_elements(*chat_page.LNB_CHAT_ITEMS)
        }
        initial_count = len(initial_hrefs)
        logger.info(f"초기 LNB 항목 수: {initial_count}")

        # 메시지 전송 → 새 대화 생성
        test_message = "삭제 테스트용 메시지"
        chat_page.send_message(test_message)
        chat_page.wait_for_ai_response()
        logger.info(f"메시지 전송 완료: {test_message}")

        # 새 대화가 LNB에 등장할 때까지 대기
        long_wait = WebDriverWait(logged_in_driver, 60)
        long_wait.until(
            lambda d: any(
                el.get_attribute("href") not in initial_hrefs
                for el in d.find_elements(*chat_page.LNB_CHAT_ITEMS)
            )
        )
        current_items = logged_in_driver.find_elements(*chat_page.LNB_CHAT_ITEMS)
        logger.info(f"새 대화 등장 후 LNB 항목 수: {len(current_items)}")

        # 1번 클릭: 새로 생성된 첫 번째 항목 클릭
        current_items[0].click()
        logger.info("LNB 첫 번째 항목 클릭 완료")

        # 2번 클릭: barsIcon 클릭 → 드롭다운 메뉴 열기
        more_button = chat_page.wait.until(
            EC.element_to_be_clickable(self.LNB_MORE_BUTTON)
        )
        more_button.click()
        logger.info("⋮ 버튼 클릭 완료")

        # 삭제 메뉴 항목 클릭
        delete_button = chat_page.wait.until(
            EC.visibility_of_element_located(self.LNB_DELETE_BUTTON)
        )
        delete_button.click()
        logger.info("삭제 버튼 클릭 완료")

        # 삭제 확인 다이얼로그 → 빨간 '삭제' 버튼 클릭
        confirm_button = chat_page.wait.until(
            EC.element_to_be_clickable(self.CONFIRM_DELETE_BUTTON)
        )
        confirm_button.click()
        logger.info("삭제 확인 완료")

        # [검증] 삭제 후 LNB 항목 수가 초기값으로 복구됐는지 확인
        chat_page.wait.until(
            lambda d: len(d.find_elements(*chat_page.LNB_CHAT_ITEMS)) <= initial_count
        )
        after_count = len(logged_in_driver.find_elements(*chat_page.LNB_CHAT_ITEMS))
        logger.info(f"삭제 후 LNB 항목 수: {after_count}")

        assert after_count == initial_count, (
            f"LNB 항목이 삭제되지 않았습니다. 삭제 전: {initial_count + 1}개, 삭제 후: {after_count}개"
        )
        logger.info("LNB 대화 삭제 확인 완료")

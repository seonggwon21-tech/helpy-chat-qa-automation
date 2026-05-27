"""
[TS-002] 새 대화 전환 및 기존 대화 보존 검증
포함 TC: TC_002, TC_003
"""

import logging
import pytest
import allure
from selenium.webdriver.support import expected_conditions as EC

logger = logging.getLogger(__name__)
pytestmark = pytest.mark.ui


@allure.epic("AI Helpy Chat")
@allure.feature("새 대화")
@allure.story("TS-002 · 새 대화 전환 및 기존 대화 보존 검증")
class TestNewChatAndHistory:

    @allure.title("새 대화 버튼 클릭 후 화면 초기화 및 기존 대화 LNB 보존·복원 확인")
    def test_new_chat_and_history_preserved(self, seeded_chat):
        # seeded_chat fixture가 사전 대화 생성을 담당 → 테스트 본문은 TC 검증에 집중
        chat_page = seeded_chat
        authenticated_driver = seeded_chat.driver

        current_url = authenticated_driver.current_url

        with allure.step("[TC_002] 새 대화 버튼 클릭 후 빈 화면으로 전환 확인"):
            chat_page.click(chat_page.NEW_CHAT_BUTTON)
            chat_page.wait.until(EC.url_changes(current_url))
            logger.info("새 대화 화면 전환 완료")

            input_value = chat_page.wait_for_visible(chat_page.CHAT_INPUT).get_attribute("value")
            assert input_value == "", f"입력창이 초기화되지 않았습니다. value: '{input_value}'"

            message_elements = authenticated_driver.find_elements(*chat_page.CHAT_MESSAGE_ELEMENTS)
            assert len(message_elements) == 0, \
                f"새 대화 화면에 이전 메시지가 {len(message_elements)}개 남아있습니다."
            logger.info("입력창 초기화 및 이전 메시지 미표시 확인 완료")

        with allure.step("[TC_003] LNB에서 기존 대화 클릭 후 내용 복원 확인"):
            chat_page.wait.until(EC.presence_of_element_located(chat_page.LNB_CHAT_ITEMS))
            lnb_items = authenticated_driver.find_elements(*chat_page.LNB_CHAT_ITEMS)
            assert len(lnb_items) > 0, "LNB 목록에 기존 대화가 존재하지 않습니다."
            logger.info(f"LNB 기존 대화 {len(lnb_items)}개 확인")

            chat_page.click(chat_page.LNB_CHAT_ITEMS)
            chat_page.wait_for_ai_response()
            message_elements = authenticated_driver.find_elements(*chat_page.CHAT_MESSAGE_ELEMENTS)
            assert len(message_elements) > 0, "기존 대화 클릭 후 내용이 표시되지 않습니다."
            logger.info("기존 대화 내용 복원 확인 완료")

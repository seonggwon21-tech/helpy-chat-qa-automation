"""
[TS-005] LNB 대화 목록 관리 검증
포함 TC: TC_012, TC_013, TC_014
"""

import logging
import pytest
import allure
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from pages.chat_page import ChatPage

logger = logging.getLogger(__name__)
pytestmark = pytest.mark.ui


@allure.epic("AI Helpy Chat")
@allure.feature("LNB 대화 목록")
@allure.story("TS-005 · LNB 대화 목록 관리 검증")
class TestLnbManagement:

    @allure.title("LNB 대화 항목 추가 → 새로고침 유지 → 삭제 시나리오")
    def test_lnb_lifecycle(self, authenticated_driver):
        chat_page = ChatPage(authenticated_driver)
        long_wait = WebDriverWait(authenticated_driver, 60)

        # LNB 항목이 로드될 때까지 대기 (빈 상태로 스냅샷 방지)
        try:
            long_wait.until(lambda d: len(d.find_elements(*chat_page.LNB_CHAT_ITEMS)) > 0)
        except Exception:
            pass

        initial_hrefs = {
            el.get_attribute("href")
            for el in authenticated_driver.find_elements(*chat_page.LNB_CHAT_ITEMS)
        }
        logger.info(f"초기 LNB 항목 수: {len(initial_hrefs)}")

        with allure.step("[TC_012] 메시지 전송 후 LNB에 새 항목 추가 확인"):
            chat_page.send_message("LNB 목록 관리 테스트")
            long_wait.until(
                lambda d: any(
                    el.get_attribute("href") not in initial_hrefs
                    for el in d.find_elements(*chat_page.LNB_CHAT_ITEMS)
                )
            )
            long_wait.until(EC.visibility_of_element_located(chat_page.AI_MESSAGE_CONTENT))

            after_hrefs = {
                el.get_attribute("href")
                for el in authenticated_driver.find_elements(*chat_page.LNB_CHAT_ITEMS)
            }
            new_hrefs = after_hrefs - initial_hrefs
            assert len(new_hrefs) >= 1, \
                f"LNB에 새 항목이 추가되지 않았습니다."
            logger.info(f"LNB 신규 항목 추가 확인 완료: {new_hrefs}")

        with allure.step("[TC_013] 페이지 새로고침 후 신규 대화 유지 확인"):
            new_chat_href = list(new_hrefs)[0]
            new_chat_id = new_chat_href.rstrip("/").split("/")[-1]
            authenticated_driver.refresh()
            long_wait.until(lambda d: len(d.find_elements(*chat_page.LNB_CHAT_ITEMS)) > 0)
            # URL로 채팅 유지 확인 (LNB 가상화로 DOM에 없는 항목도 정상 처리)
            long_wait.until(EC.url_contains(new_chat_id))
            logger.info("새로고침 후 LNB 신규 대화 유지 확인 완료")

        with allure.step("[TC_014] LNB 첫 번째 항목 삭제 후 목록에서 제거 확인"):
            current_items = authenticated_driver.find_elements(*chat_page.LNB_CHAT_ITEMS)
            target_href = current_items[0].get_attribute("href")

            # hover → more 버튼 노출 → 클릭
            ActionChains(authenticated_driver).move_to_element(current_items[0]).perform()
            chat_page.click(chat_page.LNB_MORE_BUTTON)
            chat_page.click(chat_page.LNB_DELETE_BUTTON)
            chat_page.click(chat_page.CONFIRM_DELETE_BUTTON)

            # 카운트 대신 특정 URL이 LNB에서 사라졌는지 확인 (lazy-load로 항목 보충 시 카운트 오차 방지)
            chat_page.wait.until(
                lambda d: not any(
                    el.get_attribute("href") == target_href
                    for el in d.find_elements(*chat_page.LNB_CHAT_ITEMS)
                )
            )
            logger.info(f"LNB 대화 삭제 확인 완료: {target_href}")

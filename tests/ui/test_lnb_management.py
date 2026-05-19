"""
[TS-025] LNB 대화 목록 관리 검증
포함 TC: TC_019, TC_020, TC_021
"""

import logging
import pytest
import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from pages.chat_page import ChatPage

logger = logging.getLogger(__name__)
pytestmark = pytest.mark.ui

LNB_MORE_BUTTON = (By.XPATH, "//button[.//*[@data-testid='ellipsis-verticalIcon']]")
LNB_DELETE_BUTTON = (By.XPATH, "//li[@role='menuitem'][.//*[@data-testid='trashIcon']]")
CONFIRM_DELETE_BUTTON = (By.CSS_SELECTOR, "div.MuiDialogActions-root button.MuiButton-colorError")


@allure.epic("AI Helpy Chat")
@allure.feature("LNB 대화 목록")
@allure.story("TS-025 · LNB 대화 목록 관리 검증")
class TestLnbManagement:

    @allure.title("LNB 대화 항목 추가 → 새로고침 유지 → 삭제 시나리오")
    def test_lnb_lifecycle(self, authenticated_driver):
        chat_page = ChatPage(authenticated_driver)
        long_wait = WebDriverWait(authenticated_driver, 60)

        initial_hrefs = {
            el.get_attribute("href")
            for el in authenticated_driver.find_elements(*chat_page.LNB_CHAT_ITEMS)
        }
        logger.info(f"초기 LNB 항목 수: {len(initial_hrefs)}")

        with allure.step("[TC_019] 메시지 전송 후 LNB에 새 항목 추가 확인"):
            chat_page.send_message("LNB 목록 관리 테스트")
            long_wait.until(
                lambda d: any(
                    el.get_attribute("href") not in initial_hrefs
                    for el in d.find_elements(*chat_page.LNB_CHAT_ITEMS)
                )
            )
            chat_page.wait_for_ai_response()

            after_hrefs = {
                el.get_attribute("href")
                for el in authenticated_driver.find_elements(*chat_page.LNB_CHAT_ITEMS)
            }
            new_hrefs = after_hrefs - initial_hrefs
            assert len(new_hrefs) == 1, \
                f"LNB에 새 항목이 정확히 1개 추가되지 않았습니다. 추가된 항목: {new_hrefs}"
            logger.info(f"LNB 신규 항목 추가 확인 완료: {new_hrefs}")

        with allure.step("[TC_020] 페이지 새로고침 후 LNB 목록 유지 확인"):
            before_refresh_hrefs = {
                el.get_attribute("href")
                for el in authenticated_driver.find_elements(*chat_page.LNB_CHAT_ITEMS)
            }
            authenticated_driver.refresh()
            chat_page.wait.until(EC.presence_of_element_located(chat_page.LNB_CHAT_ITEMS))

            after_refresh_hrefs = {
                el.get_attribute("href")
                for el in authenticated_driver.find_elements(*chat_page.LNB_CHAT_ITEMS)
            }
            assert before_refresh_hrefs == after_refresh_hrefs, (
                f"새로고침 후 LNB 목록이 변경되었습니다.\n"
                f"이전: {before_refresh_hrefs}\n이후: {after_refresh_hrefs}"
            )
            logger.info("새로고침 후 LNB 목록 유지 확인 완료")

        with allure.step("[TC_021] LNB 첫 번째 항목 삭제 후 목록에서 제거 확인"):
            current_items = authenticated_driver.find_elements(*chat_page.LNB_CHAT_ITEMS)
            current_count = len(current_items)
            current_items[0].click()

            chat_page.wait.until(EC.element_to_be_clickable(LNB_MORE_BUTTON)).click()
            chat_page.wait.until(EC.visibility_of_element_located(LNB_DELETE_BUTTON)).click()
            chat_page.wait.until(EC.element_to_be_clickable(CONFIRM_DELETE_BUTTON)).click()

            chat_page.wait.until(
                lambda d: len(d.find_elements(*chat_page.LNB_CHAT_ITEMS)) < current_count
            )
            after_count = len(authenticated_driver.find_elements(*chat_page.LNB_CHAT_ITEMS))
            assert after_count == current_count - 1, (
                f"LNB 항목이 삭제되지 않았습니다. 삭제 전: {current_count}개, 삭제 후: {after_count}개"
            )
            logger.info("LNB 대화 삭제 확인 완료")

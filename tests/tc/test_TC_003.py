# test_new_chat.py

import pytest
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

logger = logging.getLogger(__name__)


class TestNewChat:
    """
    새 대화 버튼 관련 테스트
    """

    @pytest.mark.ui
    def test_new_chat_page_after_click_new_chat_button(self, logged_in_driver):
        """
        시나리오:
          1) 로그인 완료 상태 (logged_in_driver fixture에서 수행)
          2) LNB '새 대화' 버튼 클릭

        기대 결과:
          - 빈 대화 페이지가 노출됨
        """

        driver = logged_in_driver
        wait = WebDriverWait(driver, 10)

        # === (1) LNB '새 대화' 버튼 클릭 ===
        new_chat_button_locator = (
            By.XPATH,
            "//span[contains(@class, 'MuiListItemText-primary') and contains(text(), '새 대화')]"
        )

        try:
            new_chat_button = wait.until(
                EC.element_to_be_clickable(new_chat_button_locator)
            )
            new_chat_button.click()
            logger.info("LNB '새 대화' 버튼 클릭")
        except TimeoutException:
            pytest.fail(
                "'새 대화' 버튼이 클릭 가능한 상태가 되지 않습니다. "
                "(LNB에서 버튼을 찾지 못한 것 같아요.)"
            )

        # === (2) 빈 대화 페이지 노출 확인 ===
        empty_chat_locator = (
            By.XPATH,
            "//p[contains(text(), '검색이나 앱 등 다양한 도구를')]"
        )

        try:
            empty_chat_page = wait.until(
                EC.visibility_of_element_located(empty_chat_locator)
            )
        except TimeoutException:
            pytest.fail(
                "빈 대화 페이지가 노출되지 않습니다. "
                "('새 대화' 클릭 후 페이지가 초기화되지 않은 것 같아요.)"
            )

        assert empty_chat_page.is_displayed(), (
            "빈 대화 페이지 요소가 화면에 노출되어야 합니다."
        )

        logger.info(
            "테스트 통과: '새 대화' 버튼 클릭 시 "
            "빈 대화 페이지가 정상적으로 노출됩니다."
        )
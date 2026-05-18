# test_search_modal_close.py

import pytest
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

logger = logging.getLogger(__name__)


class TestSearchModalClose:
    """
    검색 모달 - X버튼 클릭 시 닫힘 처리 테스트
    """

    @pytest.mark.ui
    def test_search_modal_close_on_x_button_click(self, logged_in_driver):
        """
        시나리오:
          1) 로그인 완료 상태 (logged_in_driver fixture에서 수행)
          2) LNB 메뉴의 검색 버튼 클릭 (모달 열기)
          3) 검색 모달 창의 X버튼 클릭 (모달 닫기)

        기대 결과:
          - 검색 모달 창이 닫혀 화면에서 노출되지 않음
        """

        driver = logged_in_driver
        wait = WebDriverWait(driver, 10)

        # === (1) LNB 메뉴의 검색 버튼 클릭 (모달 열기) ===
        lnb_search_button_locator = (
            By.XPATH,
            "//div[@role='button' and .//*[@data-testid='magnifying-glassIcon']]"
        )

        try:
            lnb_search_button = wait.until(
                EC.element_to_be_clickable(lnb_search_button_locator)
            )
        except TimeoutException:
            pytest.fail(
                "LNB 메뉴의 검색 버튼이 보이지 않습니다. "
                "(LNB가 펼쳐진 상태인지 확인하세요.)"
            )

        lnb_search_button.click()

        # === (2) 검색 모달이 열렸는지 먼저 확인 ===
        # 모달이 열린 상태의 기준: '플로에스 홀더 : 검색' 을 기준으로 함
        modal_open_indicator_locator = (
            By.XPATH,
            "//input[@placeholder='검색']"
        )

        try:
            wait.until(
                EC.visibility_of_element_located(modal_open_indicator_locator)
            )
        except TimeoutException:
            pytest.fail(
                "검색 모달이 열리지 않았습니다. "
                "(X버튼 클릭 전 모달이 정상적으로 열려야 합니다.)"
            )

        # === (3) 검색 모달 창의 X버튼 클릭 ===
        close_button_locator = (
            By.XPATH,
            "//button[.//*[@data-testid='xmark-largeIcon']]"
)

        try:
            close_button = wait.until(
                EC.element_to_be_clickable(close_button_locator)
            )
        except TimeoutException:
            pytest.fail(
                "검색 모달의 X버튼이 보이지 않습니다."
            )

        close_button.click()

        # === (4) 기대 결과 확인: 검색 모달이 닫혔는지 검증 ===
        # '검색 결과가 없습니다.' 문구가 더 이상 보이지 않으면 모달이 닫힌 것으로 판단
        try:
            wait.until(
                EC.invisibility_of_element_located(modal_open_indicator_locator)
            )
        except TimeoutException:
            pytest.fail(
                "X버튼 클릭 후에도 검색 모달이 닫히지 않았습니다."
            )

        logger.info("테스트 통과: X버튼 클릭 후 검색 모달 창이 정상적으로 닫혔습니다.")
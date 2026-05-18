# test_lnb_search.py

import pytest
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

logger = logging.getLogger(__name__)


class TestLnbSearch:
    """
    LNB 메뉴 - 검색 기능 테스트
    """

    @pytest.mark.ui
    def test_search_modal_is_displayed_after_click(self, logged_in_driver):
        """
        시나리오:
          1) 로그인 완료 상태 (logged_in_driver fixture에서 수행)
          2) LNB 메뉴의 검색 버튼 클릭

        기대 결과:
          - 검색 모달 창이 노출됨
        """

        driver = logged_in_driver
        wait = WebDriverWait(driver, 5)

        # === (1) LNB 메뉴의 검색 버튼 클릭 ===
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

        # === (2) 기대 결과 확인: 검색 모달 창이 노출되는지 검증 ===
        search_modal_locator = (
            By.XPATH,
            "# TODO: 검색 모달 창의 대표 요소 XPath를 입력하세요"
            # 예시 패턴 1) 모달 컨테이너: "//div[@role='dialog']"
            # 예시 패턴 2) 검색 입력창: "//input[@placeholder='검색어를 입력하세요']"
        )

        try:
            search_modal = wait.until(
                EC.visibility_of_element_located(search_modal_locator)
            )
        except TimeoutException:
            pytest.fail(
                "검색 모달 창이 노출되지 않습니다. "
                "(검색 버튼 클릭 후 모달이 열리지 않은 것 같아요.)"
            )

        assert search_modal.is_displayed(), (
            "검색 모달 창이 화면에 노출되어야 합니다."
        )

        logger.info("테스트 통과: LNB 검색 버튼 클릭 후 검색 모달 창이 정상적으로 노출됩니다.")
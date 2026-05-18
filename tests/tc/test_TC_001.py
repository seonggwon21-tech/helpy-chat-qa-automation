# test_lnb_menu.py

import pytest
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

logger = logging.getLogger(__name__)


class TestLnbMenu:
    """
    LNB(좌측 메뉴) 관련 테스트
    """

    @pytest.mark.ui
    def test_lnb_open_after_click_menu(self, logged_in_driver):
        """
        시나리오:
          1) 로그인 완료 상태 (logged_in_driver fixture에서 수행)
          2) 좌측 상단 햄버거 메뉴 버튼 클릭

        기대 결과:
          - 왼쪽 LNB에 '새 대화' 메뉴가 보이면
            LNB가 펼쳐진 것으로 판단
        """

        driver = logged_in_driver
        wait = WebDriverWait(driver, 10)

        # === (1) 햄버거 메뉴 버튼 선택자 ===
        menu_button_locator = (
            By.CSS_SELECTOR,
            "button.MuiIconButton-root.css-1p4tfme"
        )

        # 햄버거 버튼 클릭
        menu_button = wait.until(
            EC.element_to_be_clickable(menu_button_locator)
        )
        menu_button.click()
        logger.info("햄버거 메뉴 버튼 클릭")

        # === (2) LNB 열림 여부 확인 ===
        lnb_first_item_locator = (
            By.XPATH,
            "//span[contains(@class, 'MuiListItemText-primary') and contains(text(), '새 대화')]"
        )

        try:
            lnb_first_item = wait.until(
                EC.visibility_of_element_located(lnb_first_item_locator)
            )
        except TimeoutException:
            pytest.fail(
                "'새 대화' 메뉴가 보이지 않습니다. "
                "(LNB가 열리지 않은 것 같아요.)"
            )

        # 텍스트 검증
        assert "새 대화" in lnb_first_item.text, (
            "LNB 항목 텍스트가 기대와 다릅니다."
        )

        logger.info(
            "테스트 통과: 메뉴 버튼 클릭 시 "
            "LNB(왼쪽 메뉴)가 펼쳐져 "
            "'새 대화' 항목이 노출됩니다."
        )
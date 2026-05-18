import pytest
import logging

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from pages.ppt_page import PptPage

logger = logging.getLogger(__name__)


class TestTC081:

    @pytest.mark.ui
    def test_input_ppt_topic(self, logged_in_driver):
        """
        TC_081 테스트 :
        PPT 생성 페이지에서
        심층 조사 모드 토글 비활성화 검증
        """

        driver = logged_in_driver
        wait = WebDriverWait(driver, 10)

        # PPT Page 객체 생성
        ppt_page = PptPage(driver)

        # PPT 생성 페이지 이동
        ppt_page.navigate_to_ppt_page()

        # 심층 조사 모드 토글 확인
        logger.info("심층 조사 모드 토글 확인")

        # 토글 상태 확인용 input
        toggle_input = wait.until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "//input[@name='simple_mode']"
                )
            )
        )

        # 실제 클릭용 span
        toggle_button = wait.until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//input[@name='simple_mode']/ancestor::span[contains(@class,'MuiSwitch-root')]"
                )
            )
        )

        # 초기 토글 상태 확인
        initial_state = toggle_input.is_selected()

        logger.info(f"초기 토글 상태: {initial_state}")

        # 토글 클릭
        logger.info("심층 조사 모드 토글 클릭")

        toggle_button.click()

        # 클릭 후 상태 확인
        changed_state = toggle_input.is_selected()

        logger.info(f"변경 후 토글 상태: {changed_state}")

        # 활성화 -> 비활성화 검증
        assert initial_state is True, \
            "초기 토글 상태가 활성화 상태가 아닙니다."

        assert changed_state is False, \
            "토글 비활성화 실패"

        logger.info("심층 조사 모드 토글 비활성화 확인 완료")
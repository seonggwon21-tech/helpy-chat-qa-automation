import pytest
import logging

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC  # ✅ 수정된 부분

from pages.ppt_page import PptPage

logger = logging.getLogger(__name__)


class TestTC052:

    @pytest.mark.ui
    def test_lnb_open_after_click_menu(self, logged_in_driver):
        """
        TC_052 테스트 :
        PPT 생성 페이지에서 도구 목록 클릭 후
        도구 목록 페이지로 이동하는지 검증
        """

        driver = logged_in_driver
        wait = WebDriverWait(driver, 10)

        # PPT Page 객체 생성
        ppt_page = PptPage(driver)

        # PPT 생성 페이지 진입
        ppt_page.navigate_to_ppt_page()

        # PPT 생성 페이지 URL 검증   
        # 하위에 현재 URL 출력
        ppt_page.verify_ppt_page_url()

        # 현재 PPT 생성 페이지 URL 로그 출력
        current_ppt_url = driver.current_url
        logger.info(f"PPT 생성 페이지 현재 URL: {current_ppt_url}")

        # 도구 목록 링크 클릭
        logger.info("도구 목록 클릭")

        tools_link = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//a[normalize-space(text())='도구 목록']")
            )
        )

        tools_link.click()

        # 도구 목록 페이지 URL 검증
        logger.info("도구 목록 페이지 URL 검증 시작")

        wait.until(
            lambda d:
            d.current_url ==
            "https://qaproject.elice.io/ai-helpy-chat/tools"
        )

        current_url = driver.current_url

        logger.info(f"현재 URL: {current_url}")

        assert current_url == \
            "https://qaproject.elice.io/ai-helpy-chat/tools", \
            "URL 이동 실패: " + current_url

        logger.info("도구 목록 페이지 이동 완료")
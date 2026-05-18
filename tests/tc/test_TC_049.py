import pytest
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logger = logging.getLogger(__name__)


class TestTC049:

    @pytest.mark.ui
    def test_lnb_open_after_click_menu(self, logged_in_driver):
        """
        TC_049 테스트 : 좌측 LNB 메뉴 도구 클릭 후 도구 페이지 진입
        """

        driver = logged_in_driver
        wait = WebDriverWait(driver, 10)

        # 1. 도구 버튼 클릭 전 현재 URL 확인
        logger.info(f"도구 버튼 클릭 전 현재 URL: {driver.current_url}")

        # 2. '도구' 텍스트를 가진 <span> 요소가 클릭 가능할 때까지 대기 후 클릭
        logger.info("도구 버튼 클릭")
        tool_span = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//span[normalize-space(text())='도구']")
            )
        )
        tool_span.click()
        logger.info("도구 버튼 클릭 완료")

        # 3. 도구 버튼 클릭 후 URL 변경 검증
        logger.info("도구 페이지 URL 검증 시작")
        expected_tools_url = "https://qaproject.elice.io/ai-helpy-chat/tools"
        wait.until(EC.url_to_be(expected_tools_url))

        current_url = driver.current_url
        logger.info(f"현재 URL: {current_url}")
        assert current_url == expected_tools_url, f"URL이 기대와 다릅니다: {current_url}"
        logger.info("도구 페이지 URL 검증 완료")


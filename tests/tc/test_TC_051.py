import pytest
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urlparse
from pages.tool_page import ToolPage  # ToolPage 임포트

logger = logging.getLogger(__name__)


class TestTC051:

    @pytest.mark.ui
    def test_lnb_open_after_click_menu(self, logged_in_driver):
        """
        TC_051 테스트 : 좌측 LNB 메뉴 도구 클릭 후 도구 페이지 진입
        """

        driver = logged_in_driver
        wait = WebDriverWait(driver, 10)

        # ToolPage 인스턴스 생성 후 도구 탭 진입 (클릭 대기 + 클릭을 한 번에 처리)
        tool_page = ToolPage(driver)
        tool_page.setup_tool_tab()

        # '도구 목록' 텍스트를 가진 <h2> 요소가 노출될 때까지 대기
        tools_title = wait.until(
            EC.visibility_of_element_located(
                (By.XPATH, "//h2[normalize-space(text())='도구 목록']")
            )
        )

        # 도구 목록 타이틀이 실제로 화면에 표시되는지 검증
        assert tools_title.is_displayed(), "도구 목록 제목이 화면에 표시되지 않습니다."
        assert tools_title.text.strip() == "도구 목록", f"예상 텍스트와 다름: {tools_title.text}"

        # PPT 생성 버튼 클릭
        logger.info("Test PPT 생성 버튼 클릭")
        ppt_button = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//*[normalize-space(text())='PPT 생성']")
            )
        )
        ppt_button.click()

        # PPT 생성 페이지 URL 검증
        logger.info("Test PPT 생성 페이지 URL 검증 시작")

        wait.until(lambda d: "/ai-helpy-chat/tools/" in d.current_url)

        current_url = driver.current_url
        logger.info(f"현재 URL: {current_url}")

        parsed = urlparse(current_url)
        path = parsed.path  # 예: /ai-helpy-chat/tools/b11ea...

        expected_prefix = "/ai-helpy-chat/tools/"  # 주소가 이걸로 시작하는지
        assert path.startswith(expected_prefix), f"URL 경로가 기대와 다릅니다: {path}"

        suffix = path[len(expected_prefix):]  # tools/ 뒤에 무언가 있는지
        assert suffix != "", "tools/ 뒤에 페이지 ID가 없습니다."

        logger.info("PPT 생성 페이지 진입 완료")
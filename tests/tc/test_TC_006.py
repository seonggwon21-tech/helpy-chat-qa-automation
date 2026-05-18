# test_model_settings.py

import pytest
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

logger = logging.getLogger(__name__)


class TestModelSettings:
    """
    채팅 화면 - 모델 설정 페이지 진입 테스트
    """

    @pytest.mark.ui
    def test_model_settings_page_is_displayed(self, logged_in_driver):
        """
        시나리오:
          1) 로그인 완료 상태 (logged_in_driver fixture에서 수행)
          2) 현재 설정된 모델 버튼 클릭 (모델 목록 열기)
          3) 모델 설정 버튼 클릭

        전제 조건:
          - 설정에 모델이 1개 이상 등록되어 있어야 함

        기대 결과:
          - 모델 설정 페이지가 노출됨
        """

        driver = logged_in_driver
        wait = WebDriverWait(driver, 10)

        # === (1) 현재 설정된 모델 버튼 클릭 (모델 목록 열기) ===
        # 이전 케이스(test_model_change.py)와 동일한 로케이터 사용
        current_model_button_locator = (
            By.XPATH,
            "//button[.//p[contains(@class, 'MuiTypography-noWrap')]]"
        )

        try:
            current_model_button = wait.until(
                EC.element_to_be_clickable(current_model_button_locator)
            )
        except TimeoutException:
            pytest.fail(
                "현재 선택된 모델 버튼이 보이지 않습니다. "
                "(설정에 모델이 1개 이상 등록되어 있는지 확인하세요.)"
            )

        current_model_button.click()

        # === (2) 모델 설정 버튼 클릭 ===
        model_settings_button_locator = (
            By.XPATH,
            "//a[@href='/ai-helpy-chat/admin/models' and @role='menuitem']"
            # 예시 패턴: "//*[contains(text(), '모델 설정')]"
            # 또는: "//button[contains(@class, '클래스명')]"
        )

        try:
            model_settings_button = wait.until(
                EC.element_to_be_clickable(model_settings_button_locator)
            )
        except TimeoutException:
            pytest.fail(
                "모델 설정 버튼이 보이지 않습니다. "
                "(모델 목록이 정상적으로 열렸는지 확인하세요.)"
            )

        model_settings_button.click()

        # === (3) 기대 결과 확인: 모델 설정 페이지가 노출되는지 검증 ===
        model_settings_page_locator = (
            By.XPATH,
            "# TODO: 모델 설정 페이지의 대표 요소(제목 또는 컨테이너) XPath를 입력하세요"
            # 예시 패턴: "//*[contains(text(), '모델 설정')]"
        )
        try:
            wait.until(EC.url_contains("/ai-helpy-chat/admin/models"))
        except TimeoutException:
            pytest.fail(
                "모델 설정 페이지로 이동되지 않았습니다. "
                "(URL이 '/ai-helpy-chat/admin/models'로 변경되지 않았어요.)"
            )

        logger.info("테스트 통과: 모델 설정 버튼 클릭 후 모델 설정 페이지가 정상적으로 노출됩니다.")
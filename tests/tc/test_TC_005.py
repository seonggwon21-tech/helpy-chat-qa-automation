# test_model_change.py

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import logging
logger = logging.getLogger(__name__)

class TestModelChange:
    """
    채팅 화면 - 모델 변경 관련 테스트
    """

    @pytest.mark.ui
    def test_model_change_shows_empty_chat(self, logged_in_driver):
        """
        시나리오:
          1) 로그인 완료 상태 (logged_in_driver fixture에서 수행)
          2) 설정된 모델 버튼 클릭 (모델 선택 목록 열기)
          3) 기본 모델 외 다른 모델 클릭

        전제 조건:
          - 설정에 모델이 2개 이상 등록되어 있어야 함

        기대 결과:
          - 선택한 모델로 변경되고 빈 대화 페이지가 노출됨
        """

        driver = logged_in_driver
        wait = WebDriverWait(driver, 10)

        # === (1) 현재 설정된 모델 버튼 클릭 (모델 목록 열기) ===
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

        # === (2) 모델 목록에서 기본 모델 외 다른 모델 클릭 ===
        other_model_locator = (
            By.XPATH,
            "//li[@role='menuitem' and .//span[text()='Helpy Edu']]"
            # 예시 패턴 1) 목록의 두 번째 항목: "//ul[@class='모델목록 클래스명']/li[2]"
            # 예시 패턴 2) 특정 모델명으로 찾기: "//*[contains(text(), '모델명')]"
        )

        try:
            other_model_item = wait.until(
                EC.element_to_be_clickable(other_model_locator)
            )
        except TimeoutException:
            pytest.fail(
                "모델 목록이 열리지 않았거나, 변경 가능한 다른 모델 항목이 보이지 않습니다."
            )

        other_model_item.click()

        # === (3) 기대 결과 확인: 빈 대화 페이지가 노출되는지 검증 ===

        # 검증 1) 채팅 입력창이 빈 상태로 노출되는지 확인
        chat_input_locator = (
            By.CSS_SELECTOR,
            "textarea[name='input']"  # chat_page.py의 CHAT_INPUT 로케이터 참고
        )

        try:
            chat_input = wait.until(
                EC.visibility_of_element_located(chat_input_locator)
            )
        except TimeoutException:
            pytest.fail(
                "모델 변경 후 채팅 입력창이 노출되지 않습니다. "
                "(빈 대화 페이지로 전환되지 않은 것 같아요.)"
            )

        assert chat_input.get_attribute("value") == "", (
            "채팅 입력창이 비어 있어야 합니다. (이전 대화 내용이 남아 있습니다.)"
        )

        # 검증 2) 이전 AI 메시지가 없는지 확인
        ai_message_locator = (
            By.CSS_SELECTOR,
            "div.elice-aichat__markdown[data-status='complete']"  # chat_page.py의 AI_MESSAGE_CONTENT 참고
        )

        ai_messages = driver.find_elements(*ai_message_locator)
        assert len(ai_messages) == 0, (
            "모델 변경 후 빈 대화 페이지여야 하는데, 이전 메시지가 남아 있습니다."
        )

        logger.info("테스트 통과: 모델 변경 후 빈 대화 페이지가 정상적으로 노출됩니다.")
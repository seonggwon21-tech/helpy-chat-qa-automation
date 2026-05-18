# test_search_empty.py

import pytest
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from pages.login_page import LoginPage
from pages.signup_page import SignupPage

logger = logging.getLogger(__name__)

# =========================================================
# 이 테스트 전용 계정 정보
# logged_in_driver fixture(기본 계정) 대신
# 아래 계정으로 직접 로그인을 진행합니다.
# =========================================================
QA_USER = {
    "id": "qa@test.com",
    "pw": "qwert12345!"
}


class TestSearchEmpty:
    """
    검색 기능 - 검색 결과 없음 안내 문구 노출 테스트
    """

    @pytest.mark.ui
    def test_search_empty_message_is_displayed(self, driver, base_url):
        """
        시나리오:
          1) QA 전용 계정(qa@test.com)으로 직접 로그인
          2) 검색을 진행하지 않은 상태에서 LNB 메뉴의 검색 버튼 클릭

        사전 조건:
          - 검색을 진행하지 않은 상태 (검색 기록 없는 계정)

        기대 결과:
          - 검색 모달 창에 '검색 결과가 없습니다.' 안내 문구 노출됨
        """

        wait = WebDriverWait(driver, 10)

        # === (1) QA 전용 계정으로 직접 로그인 ===
        login_page = LoginPage(driver, base_url)
        signup_page = SignupPage(driver)

        login_page.open()
        login_page.login(QA_USER["id"], QA_USER["pw"])

        # 최초 로그인 시 약관 동의 화면이 뜰 수 있으므로 예외 처리
        try:
            signup_page.agree_and_submit()
        except TimeoutException:
            pass  # 이미 약관 동의 완료된 계정은 스킵

        # 로그인 성공 여부 확인
        assert login_page.is_login_successful() is True, (
            "로그인에 실패했습니다. QA 계정 정보(id/pw)를 확인하세요."
        )

        # === (2) LNB 메뉴의 검색 버튼 클릭 ===
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

        # === (3) 기대 결과 확인: '검색 결과가 없습니다.' 안내 문구 노출 검증 ===
        # <p class="MuiTypography-root ...">검색 결과가 없습니다.</p> 를 타겟
        no_result_message_locator = (
            By.XPATH,
            "//p[text()='검색 결과가 없습니다.']"
        )

        try:
            no_result_message = wait.until(
                EC.visibility_of_element_located(no_result_message_locator)
            )
        except TimeoutException:
            pytest.fail(
                "'검색 결과가 없습니다.' 안내 문구가 노출되지 않습니다. "
                "(검색 기록이 존재하는 계정이거나, 모달이 정상적으로 열리지 않은 것 같아요.)"
            )

        assert no_result_message.is_displayed(), (
            "'검색 결과가 없습니다.' 문구가 화면에 노출되어야 합니다."
        )
        assert no_result_message.text == "검색 결과가 없습니다.", (
            f"안내 문구 텍스트가 다릅니다. 실제 텍스트: '{no_result_message.text}'"
        )

        logger.info("테스트 통과: 검색 기록이 없는 상태에서 검색 클릭 시 '검색 결과가 없습니다.' 안내 문구가 정상적으로 노출됩니다.")
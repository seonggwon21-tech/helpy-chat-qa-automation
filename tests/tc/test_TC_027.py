# test_search_modal_close.py

import pytest
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

logger = logging.getLogger(__name__)


class TestSearchModalreopen:
    """
    검색 모달 에 글자 입력후 값 초기화 여부 테스트 - 이슈 발생 (근데 assert를 수정해서 pass 상태로 바꿔야 할지, 이슈 인지 판단이 필요)
    """

    @pytest.mark.ui
    def test_search_modal_close_on_x_button_click(self, logged_in_driver):
        """
        시나리오:
          1) 로그인 완료 상태 (logged_in_driver fixture에서 수행)
          2) LNB 메뉴의 검색 버튼 클릭 (모달 열기)
          3) 모달 열림 확인
          4) 검색 입력창에 텍스트 입력
          5) X버튼 클릭 (모달 닫기)
          6) 모달 닫힘 확인
          7) LNB 검색 버튼 재클릭 (모달 재오픈)
          8) 입력창 초기화 여부 확인

        기대 결과:
          - X버튼 클릭 후 검색 모달이 닫힘
          - 모달 재오픈 시 이전 입력 텍스트가 남아있지 않음
        """

        driver = logged_in_driver
        wait = WebDriverWait(driver, 10)

        # 공통 로케이터 (재사용)
        lnb_search_button_locator = (
            By.XPATH,
            "//div[@role='button' and .//*[@data-testid='magnifying-glassIcon']]"
        )
        modal_open_indicator_locator = (
            By.XPATH,
            "//p[text()='검색 결과가 없습니다.']"
        )
        search_input_locator = (
            By.CSS_SELECTOR,
            "input[placeholder='검색']"
        )
        close_button_locator = (
            By.XPATH,
            "//button[.//*[@data-testid='xmark-largeIcon']]"
        )

        # 검색 입력 텍스트를 변수로 관리
        SEARCH_TEXT = "테스트글자입니다."

        # === (1) LNB 메뉴의 검색 버튼 클릭 (모달 열기) ===
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

        # === (2) 검색 모달 열림 확인 ===
        try:
            wait.until(
                EC.visibility_of_element_located(search_input_locator)  # input[placeholder='검색']
            )
        except TimeoutException:
            pytest.fail(
                "검색 모달이 열리지 않았습니다. "
                "(검색 입력창이 보이지 않습니다.)"
            )

        # === (3) 검색 입력창에 텍스트 입력 ===
        try:
            search_input = wait.until(
                EC.visibility_of_element_located(search_input_locator)
            )
        except TimeoutException:
            pytest.fail(
                "검색 입력창이 보이지 않습니다."
            )

        search_input.clear()
        search_input.send_keys(SEARCH_TEXT)
        logger.info(f"검색 입력창에 텍스트 입력 완료: '{SEARCH_TEXT}'")

        # === (4) X버튼 클릭 (모달 닫기) ===
        try:
            close_button = wait.until(
                EC.element_to_be_clickable(close_button_locator)
            )
        except TimeoutException:
            pytest.fail(
                "검색 모달의 X버튼이 보이지 않습니다."
            )

        close_button.click()

        # === (5) 기대 결과 확인 1: 모달 닫힘 검증 ===
        try:
            wait.until(
                EC.invisibility_of_element_located(modal_open_indicator_locator)
            )
        except TimeoutException:
            pytest.fail(
                "X버튼 클릭 후에도 검색 모달이 닫히지 않았습니다."
            )

        logger.info("모달 닫힘 확인 완료")

        # === (6) LNB 검색 버튼 재클릭 (모달 재오픈) ===
        try:
            lnb_search_button = wait.until(
                EC.element_to_be_clickable(lnb_search_button_locator)
            )
        except TimeoutException:
            pytest.fail(
                "모달 닫힘 후 LNB 검색 버튼이 보이지 않습니다."
            )

        lnb_search_button.click()

        # === (7) 기대 결과 확인 2: 재오픈 후 입력창 초기화 여부 검증 ===
        # X버튼으로 닫은 후 재오픈 시 이전에 입력한 텍스트가 남아있지 않아야 함
        try:
            search_input_reopened = wait.until(
                EC.visibility_of_element_located(search_input_locator)
            )
        except TimeoutException:
            pytest.fail(
                "검색 모달 재오픈 후 입력창이 보이지 않습니다."
            )

        actual_text = search_input_reopened.get_attribute("value")
        assert actual_text != SEARCH_TEXT, (
            f"모달 재오픈 후 입력창에 이전 텍스트 '{SEARCH_TEXT}'가 남아있습니다. "
            f"입력창이 초기화되어야 합니다."
        )

        logger.info(
            f"테스트 통과: X버튼 클릭 후 모달이 닫히고, "
            f"재오픈 시 입력창이 초기화되었습니다. (현재 값: '{actual_text}')"
        )
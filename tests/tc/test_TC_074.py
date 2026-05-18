import pytest
import logging

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from pages.ppt_page import PptPage

logger = logging.getLogger(__name__)


class TestTC65:

    @pytest.mark.ui
    def test_input_ppt_instruction(self, logged_in_driver):
        """
        TC_065 테스트 :
        PPT 생성 페이지에서 슬라이드 수 입력 필드에
        문자 입력이 불가능한지 검증
        """

        driver = logged_in_driver
        wait = WebDriverWait(driver, 10)

        # PPT Page 객체 생성
        ppt_page = PptPage(driver)

        # PPT 생성 페이지 이동
        ppt_page.navigate_to_ppt_page()

        # 슬라이드 수 입력 필드 찾기

        topic_input = wait.until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//input[@name='slides_count']")))
                

        # 슬라이드 수 입력 필드 클릭
        topic_input.click()

        # 기존 값 전체 삭제

        topic_input.send_keys(Keys.CONTROL + "a")
        topic_input.send_keys(Keys.DELETE)

        # 문자 입력 시도
        logger.info("문자 입력 시도. 입력 값 : 가")

        topic_input.send_keys("가")

        # 입력값 확인
        entered_value = topic_input.get_attribute("value")

        logger.info(f"현재 입력값: {entered_value}")

        # 문자 입력 불가능 검증
        assert entered_value == "", \
            f"문자 입력 제한 실패: {entered_value}"

        logger.info("문자 입력 제한 확인 완료")
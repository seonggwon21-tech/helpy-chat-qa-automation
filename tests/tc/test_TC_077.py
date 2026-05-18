import pytest
import logging

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from pages.ppt_page import PptPage

logger = logging.getLogger(__name__)


class TestTC077:

    @pytest.mark.ui
    def test_input_ppt_instruction(self, logged_in_driver):
        """
        TC_077 테스트 :
        PPT 생성 페이지에서 섹션수 입력 필드 클릭 후
        숫자 0 입력 시 입력 불가 상태 검증
        """

        driver = logged_in_driver
        wait = WebDriverWait(driver, 10)

        # PPT Page 객체 생성
        ppt_page = PptPage(driver)

        # PPT 생성 페이지 이동
        ppt_page.navigate_to_ppt_page()

        # 섹션 수 입력 필드 찾기
        logger.info("섹션 수 입력 필드 확인")

        topic_input = wait.until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//input[@name='section_count']")))

        # 섹션 수 입력 필드 클릭
        logger.info("섹션 수 필드 클릭")
        topic_input.click()

        # 기존 값 전체 삭제
        logger.info("기존 값 제거")

        topic_input.send_keys(Keys.CONTROL + "a")
        topic_input.send_keys(Keys.DELETE)

        # 섹션 수 입력
        logger.info("섹션 수 0 입력")

        topic_input.send_keys("0")

        # 입력값 검증
          # 입력값 확인
        entered_value = topic_input.get_attribute("value")

        logger.info(f"현재 입력값: {entered_value}")

        # 문자 입력 불가능 검증
        assert entered_value == "", \
            f"문자 입력 제한 실패: {entered_value}"

        logger.info("0 입력 제한 확인 완료")
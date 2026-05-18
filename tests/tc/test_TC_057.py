import pytest
import logging

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from pages.ppt_page import PptPage

logger = logging.getLogger(__name__)


class TestTC057:

    @pytest.mark.ui
    def test_input_ppt_topic(self, logged_in_driver):
        """
        TC_057 테스트 :
        PPT 생성 페이지에서 주제 입력 필드 클릭 후
        글자수 501자 입력 시 에러 메시지 출력 검증.
        """

        driver = logged_in_driver
        wait = WebDriverWait(driver, 10)

        # PPT Page 객체 생성
        ppt_page = PptPage(driver)

        # PPT 생성 페이지 이동
        ppt_page.navigate_to_ppt_page()

        # 주제 입력 필드 찾기
        topic_input = wait.until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//input[@placeholder='PPT 주제를 입력해주세요.']")))

        assert topic_input, "주제 입력 필드 찾기 실패"

        # 주제 입력 필드 클릭
        topic_input.click()

        # 기존 값 전체 삭제

        topic_input.send_keys(Keys.CONTROL + "a")
        topic_input.send_keys(Keys.DELETE)

        # 새 주제 입력
        logger.info("글자 수 501자 입력")

        topic_input.send_keys("가"*501)

        logger.info("에러 메시지 확인")

        error_message = wait.until(
            EC.visibility_of_element_located(
                (
                    By.XPATH,
                    "//p[contains(text(),'1자 이상 500자 이하로 입력해주세요.')]"
                )
            )
        )

        # 에러 메시지 표시 여부 검증
        assert error_message.is_displayed(), \
            "글자 수 제한 에러 메시지가 표시되지 않습니다."

        # 에러 메시지 텍스트 검증
        assert error_message.text.strip() == \
            "1자 이상 500자 이하로 입력해주세요.", \
            f"에러 메시지 불일치: {error_message.text}"

        logger.info("글자 수 제한 에러 메시지 확인 완료")
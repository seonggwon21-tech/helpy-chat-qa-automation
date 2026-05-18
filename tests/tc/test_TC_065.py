import pytest
import logging

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from pages.ppt_page import PptPage

logger = logging.getLogger(__name__)


class TestTC065:

    @pytest.mark.ui
    def test_input_ppt_instruction(self, logged_in_driver):
        """
        TC_064 테스트 :
        PPT 생성 페이지에서 슬라이드 수 입력 필드 클릭 후
        숫자 (50초과) 입력 시 에러 메시지 출력 검증
        """

        driver = logged_in_driver
        wait = WebDriverWait(driver, 10)

        # PPT Page 객체 생성
        ppt_page = PptPage(driver)

        # PPT 생성 페이지 이동
        ppt_page.navigate_to_ppt_page()

        # 지시사항 입력 필드 찾기
        logger.info("슬라이드 수 입력 필드 확인")

        topic_input = wait.until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//input[@name='slides_count']")))

        # 지시사항 입력 필드 클릭
        logger.info("슬라이드 수 필드 클릭")
        topic_input.click()

        # 기존 값 전체 삭제
        logger.info("기존 값 제거")

        topic_input.send_keys(Keys.CONTROL + "a")
        topic_input.send_keys(Keys.DELETE)

        # 새 지시사항 입력
        logger.info("슬라이드 수 51 입력")

        topic_input.send_keys("51")

        logger.info("에러 메시지 확인")

        error_message = wait.until(
            EC.visibility_of_element_located(
                (
                    By.XPATH,
                    "//p[contains(text(),'3 이상 50 이하로 입력해주세요.')]"
                )
            )
        )

        # 에러 메시지 표시 여부 검증
        assert error_message.is_displayed(), \
            "글자 수 제한 에러 메시지가 표시되지 않습니다."

        # 에러 메시지 텍스트 검증
        assert error_message.text.strip() == \
            "3 이상 50 이하로 입력해주세요.", \
            f"에러 메시지 불일치: {error_message.text}"

        logger.info("슬라이드 수 제한 에러 메시지 확인 완료")
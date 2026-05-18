import pytest
import logging

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from pages.ppt_page import PptPage

logger = logging.getLogger(__name__)


class TestTC061:

    @pytest.mark.ui
    def test_input_ppt_instruction(self, logged_in_driver):
        """
        TC_061 테스트 :
        PPT 생성 페이지 지시사항 입력 필드에 
        2001자 입력 시 에러 메시지 출력 검증
        """

        driver = logged_in_driver
        wait = WebDriverWait(driver, 10)

        # PPT Page 객체 생성
        ppt_page = PptPage(driver)

        # PPT 생성 페이지 이동
        ppt_page.navigate_to_ppt_page()

        # 지시사항 입력 필드 찾기
        logger.info("지시사항 입력 필드 확인")

        topic_input = wait.until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//textarea[@placeholder='AI가 PPT 생성 시 반영할 사항이나 고려할 점을 알려주세요.']"
                )
            )
        )

        # 지시사항 입력 필드 클릭
        topic_input.click()

        # 기존 값 전체 삭제

        topic_input.send_keys(Keys.CONTROL + "a")
        topic_input.send_keys(Keys.DELETE)

        # 새 지시사항 입력
        logger.info("2001자 입력")

        topic_input.send_keys("가"*2001)

        logger.info("에러 메시지 확인")

        error_message = wait.until(
            EC.visibility_of_element_located(
                (
                    By.XPATH,
                    "//p[contains(text(),'2000자 이하로 입력해주세요.')]"
                )
            )
        )

        # 에러 메시지 표시 여부 검증
        assert error_message.is_displayed(), \
            "글자 수 제한 에러 메시지가 표시되지 않습니다."

        # 에러 메시지 텍스트 검증
        assert error_message.text.strip() == \
            "2000자 이하로 입력해주세요.", \
            f"에러 메시지 불일치: {error_message.text}"

        logger.info("글자 수 제한 에러 메시지 확인 완료")
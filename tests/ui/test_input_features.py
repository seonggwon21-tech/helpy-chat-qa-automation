"""
[TS-003] 메시지 입력 기능 검증
포함 TC: TC_004, TC_005, TC_006
"""

import logging
import time

import allure
import pytest
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC

from pages.chat_page import ChatPage

logger = logging.getLogger(__name__)
pytestmark = pytest.mark.ui


@allure.epic("AI Helpy Chat")
@allure.feature("메시지 입력")
@allure.story("TS-003 · 메시지 입력 기능 검증")
class TestInputFeatures:

    @allure.title("전송 버튼 비활성화 / Shift+Enter 줄바꿈 / Enter 전송 시나리오")
    def test_input_features_scenario(self, authenticated_driver):
        chat_page = ChatPage(authenticated_driver)
        inp = chat_page.chat_input
        long_wait = chat_page.wait_up_to(60)

        inp.start_new_chat()
        logger.info("새 대화 화면 진입")

        with allure.step("[TC_004] 빈 입력창에서 전송 버튼 비활성화 확인"):
            send_button = inp.wait.until(
                EC.presence_of_element_located(inp.SEND_BUTTON)
            )
            assert send_button.get_attribute("disabled") is not None, \
                "전송 버튼이 활성화 상태입니다. disabled 속성이 존재해야 합니다."
            logger.info("전송 버튼 비활성화 확인 완료")

        with allure.step("[TC_005] Shift+Enter 입력 시 줄바꿈만 적용, 전송 미동작 확인"):
            input_element = inp.enter_text(inp.CHAT_INPUT, "줄바꿈 테스트")
            input_element.send_keys(Keys.SHIFT, Keys.ENTER)

            input_value = input_element.get_attribute("value")
            assert "\n" in input_value, f"줄바꿈이 적용되지 않았습니다. value: '{input_value}'"

            # AI 응답은 비동기이므로 잠시 대기 후 응답 노드가 없음을 확인
            time.sleep(2)
            ai_messages = authenticated_driver.find_elements(*inp.CHAT_MESSAGE_ELEMENTS)
            assert len(ai_messages) == 0, \
                f"Shift+Enter 입력 후 메시지가 전송되었습니다. AI 응답 요소 수: {len(ai_messages)}"
            logger.info("Shift+Enter 줄바꿈 적용 및 전송 미동작 확인 완료")

        with allure.step("[TC_006] Enter 키 전송 후 AI 응답 출력 확인"):
            input_element = inp.enter_text(
                inp.CHAT_INPUT, "소프트웨어 QA에 대해 10글자 이내로 짧게 설명해줘."
            )
            input_element.send_keys(Keys.ENTER)
            logger.info("Enter 키 전송 완료")

            long_wait.until(EC.visibility_of_element_located(inp.AI_MESSAGE_CONTENT))
            response_text = inp.get_text(inp.AI_MESSAGE_CONTENT)
            assert response_text, "AI 응답이 출력되지 않았습니다."
            assert len(response_text.strip()) > 0, "AI 응답 텍스트가 비어있습니다."
            logger.info(f"AI 응답 출력 확인 완료: {response_text}")

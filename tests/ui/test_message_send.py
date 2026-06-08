"""
[TS-001] 메시지 전송 E2E 플로우 검증 (전송 버튼 클릭)
포함 TC: TC_001
"""

import logging

import allure
import pytest

logger = logging.getLogger(__name__)
pytestmark = pytest.mark.ui


@allure.epic("AI Helpy Chat")
@allure.feature("메시지 전송")
@allure.story("TS-001 · 메시지 전송 E2E 플로우 검증 (전송 버튼 클릭)")
class TestMessageSendFlow:

    @allure.title("전송 버튼 클릭 시 입력창 초기화 및 AI 응답 출력 확인")
    def test_send_via_button_shows_ai_response(self, fresh_chat):
        chat_page = fresh_chat

        message = "소프트웨어 QA에 대해 10글자 이내로 짧게 설명해줘."

        with allure.step("[TC_001] 텍스트 입력 후 전송 버튼 클릭"):
            chat_page.chat_input.send_message(message)
            logger.info(f"메시지 전송 완료: {message}")

        with allure.step("[TC_001] 전송 후 입력창 초기화 확인"):
            input_value = chat_page.chat_input.wait_for_visible(
                chat_page.chat_input.CHAT_INPUT
            ).get_attribute("value")
            assert input_value == "", f"입력창이 초기화되지 않았습니다. value: '{input_value}'"
            logger.info("입력창 초기화 확인 완료")

        with allure.step("[TC_001] AI 응답 출력 완료 확인"):
            response_text = chat_page.wait_for_ai_response()
            assert response_text, "AI 응답이 출력되지 않았습니다."
            logger.info(f"AI 응답 출력 확인 완료: {response_text}")

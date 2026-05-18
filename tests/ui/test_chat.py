"""
헬피챗 채팅 전송 및 AI 응답 기능에 대한 UI 시나리오 테스트 스크립트.
"""

import pytest
import logging
from pages.chat_page import ChatPage

logger = logging.getLogger(__name__)

class TestChat:
    """채팅 기능 검증 테스트 스위트"""

    def test_send_chat_and_receive_response(self, logged_in_driver):
        """
        [TC-CHAT-001] 정상적으로 로그인한 사용자는 헬피챗에서 메시지를 전송하고 AI의 응답을 받을 수 있어야 한다.
        """
        # 1. Page Object 초기화 (로그인 픽스처 주입)
        chat_page = ChatPage(logged_in_driver)
        
        # 2. 테스트 액션(Test Action): 메시지 전송
        test_message = "소프트웨어 QA에 대해 10글자 이내로 짧게 설명해줘."
        chat_page.send_message(test_message)
        
        # 3. 검증(Assertion): AI 응답 대기 및 확인
        response_text = chat_page.wait_for_ai_response()
        
        # [참고] Jira 연동 테스트 시 아래 주석을 풀고 강제 에러 발생시키기!
        # assert response_text == "일부러 틀리는 텍스트", "Jira 테스트용 강제 에러"
        
        # 응답이 정상적으로 돌아왔는지 확인 (빈 문자열이 아님을 검증)
        assert response_text is not None, "AI 응답 요소를 찾을 수 없습니다."
        assert len(response_text.strip()) > 0, "AI 응답 텍스트가 비어있습니다."
        
        logger.info(f"전송한 메시지: {test_message}")
        logger.info(f"AI 응답 내용: {response_text}")

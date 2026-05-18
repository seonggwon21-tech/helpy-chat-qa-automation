"""
[TC-011] 채팅방 목록 조회 API 검증
- 사전 조건: 유효한 인증 토큰 보유
- 테스트 절차:
    1. 인증 토큰으로 GET /chatrooms 요청
    2. 응답 상태 코드 및 응답 바디 구조 확인
- 기대 결과:
    상태 코드 200, 채팅방 목록 데이터 반환
"""

import logging
import pytest

logger = logging.getLogger(__name__)
pytestmark = pytest.mark.api


class TestChatroomListAPI:
    """채팅방 목록 조회 API 검증 테스트 스위트"""

    def test_chatroom_list_returns_200(self, api_session, api_base_url):
        """
        [TC-011] 인증된 사용자가 채팅방 목록을 조회하면
        상태 코드 200과 목록 데이터가 반환되어야 한다.
        """
        url = f"{api_base_url}/chatrooms"
        response = api_session.get(url)
        logger.info(f"채팅방 목록 API 응답 코드: {response.status_code}")

        assert response.status_code == 200, (
            f"채팅방 목록 조회 실패. 상태 코드: {response.status_code}, 응답: {response.text}"
        )
        body = response.json()
        assert isinstance(body, (list, dict)), (
            f"예상치 못한 응답 형식. 응답 바디: {body}"
        )
        logger.info(f"채팅방 목록 조회 확인 완료. 응답 타입: {type(body).__name__}")

"""
[TC-010] 로그인 API 인증 토큰 발급 검증
- 사전 조건: 유효한 계정 정보 존재
- 테스트 절차:
    1. POST /otp 엔드포인트에 자격증명 전송
    2. 응답 상태 코드 및 응답 바디 확인
- 기대 결과:
    상태 코드 200, access_token 포함된 JSON 응답 반환
"""

import logging
import requests

logger = logging.getLogger(__name__)

AUTH_API_URL = "https://auth.example.com"


class TestLoginAPI:
    """로그인 API 인증 토큰 발급 검증 테스트 스위트"""

    def test_login_returns_access_token(self, test_user):
        """
        [TC-010] 유효한 자격증명으로 POST /otp 요청 시
        상태 코드 200과 access_token이 반환되어야 한다.
        """
        url = f"{AUTH_API_URL}/login/otp"
        payload = {"username": test_user["id"], "password": test_user["pw"]}
        response = requests.post(url, json=payload)
        logger.info(f"로그인 API 응답 코드: {response.status_code}")

        assert response.status_code == 200, (
            f"로그인 실패. 상태 코드: {response.status_code}, 응답: {response.text}"
        )
        body = response.json()
        assert "access_token" in body, (
            f"응답에 access_token 없음. 응답 바디: {body}"
        )
        assert body["access_token"], "access_token 값이 비어 있습니다."
        logger.info("access_token 발급 확인 완료")

"""
[TS-006] 커뮤니티 API 검증
포함 TC: TC_015 (에이전트 목록 조회), TC_016 (에이전트 수 조회),
         TC_017 (에이전트 상세 조회), TC_018 (미인증 접근 거부),
         TC_019 (유효하지 않은 토큰 거부), TC_020 (잘못된 인증 스킴 거부)
"""

import logging

import allure
import pytest
import requests

logger = logging.getLogger(__name__)
pytestmark = pytest.mark.api

# 명백히 유효하지 않은 토큰 — 만료·서명 불일치를 시뮬레이션
_INVALID_TOKEN = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
    ".eyJzdWIiOiIwMDAwMDAwMCIsImV4cCI6MX0"
    ".INVALID_SIGNATURE_FOR_TEST"
)


@allure.epic("AI Helpy Chat API")
@allure.feature("에이전트 API")
@allure.story("TS-006 · 에이전트 목록·수·상세 조회 시나리오")
class TestAgentAPI:

    @allure.title("에이전트 목록 조회 → 수 확인 → 상세 조회 시나리오")
    def test_agent_read_flow(self, api_session, api_base_url):
        """에이전트 목록(TC_015) → 수 조회(TC_016) → 상세 조회(TC_017) 전체 플로우"""

        with allure.step("[TC_015] GET /agent → 200 및 리스트 구조 확인"):
            response = api_session.get(f"{api_base_url}/agent", params={"skip": 0, "count": 10})
            logger.info(f"GET /agent 응답 코드: {response.status_code}")
            assert response.status_code == 200, \
                f"에이전트 목록 조회 실패. 상태 코드: {response.status_code}, 응답: {response.text}"
            agents = response.json()
            assert isinstance(agents, list), \
                f"응답 형식이 list가 아닙니다. 실제 타입: {type(agents).__name__}"
            assert len(agents) > 0, "에이전트 목록이 비어 있습니다."
            logger.info(f"에이전트 목록 조회 완료. 총 {len(agents)}개")

        with allure.step("[TC_016] GET /agent/count → 200 및 count 정수 반환 확인"):
            response = api_session.get(f"{api_base_url}/agent/count")
            logger.info(f"GET /agent/count 응답 코드: {response.status_code}")
            assert response.status_code == 200, \
                f"에이전트 수 조회 실패. 상태 코드: {response.status_code}, 응답: {response.text}"
            body = response.json()
            count = body.get("count") if isinstance(body, dict) else body
            assert isinstance(count, int) and count >= 0, \
                f"count 값이 유효하지 않습니다. 응답: {body}"
            logger.info(f"에이전트 수 조회 완료. count: {count}")

        with allure.step("[TC_017] GET /agent/{agent_id} → 200 및 상세 데이터 구조 확인"):
            agent_id = agents[0].get("id") or agents[0].get("agent_id")
            assert agent_id, "TC_015 응답에서 agent_id를 가져올 수 없습니다."

            response = api_session.get(f"{api_base_url}/agent/{agent_id}")
            logger.info(f"GET /agent/{agent_id} 응답 코드: {response.status_code}")
            assert response.status_code == 200, \
                f"에이전트 상세 조회 실패. 상태 코드: {response.status_code}, 응답: {response.text}"
            detail = response.json()
            assert isinstance(detail, dict), \
                f"응답 형식이 dict가 아닙니다. 실제 타입: {type(detail).__name__}"
            returned_id = detail.get("id") or detail.get("agent_id")
            assert returned_id == agent_id, \
                f"응답의 agent_id 불일치. 기대: {agent_id}, 실제: {returned_id}"
            logger.info(f"에이전트 상세 조회 완료. name: {detail.get('name')}")


@allure.epic("AI Helpy Chat API")
@allure.feature("인증")
@allure.story("TS-006 · 에이전트 API & 인증 검증 — 미인증/만료 토큰 음성 케이스")
class TestChatroomAuth:

    @allure.title("인증 헤더 없이 요청 시 401 또는 403 반환 확인")
    def test_unauthorized_returns_401_or_403(self, api_base_url):
        """[TC_018] 인증 헤더 자체를 생략한 경우 서버가 접근을 거부하는지 확인."""
        with allure.step("[TC_018] 인증 없이 GET /chatroom 요청"):
            response = requests.get(
                f"{api_base_url}/chatroom",
                headers={"x-elice-org-name-short": "qaproject"},
            )
            logger.info(f"GET /chatroom (인증 없음) 응답 코드: {response.status_code}")
            assert response.status_code in (401, 403), (
                f"미인증 요청에 예상치 못한 응답. "
                f"상태 코드: {response.status_code}, 응답: {response.text}"
            )
            logger.info(f"미인증 요청 거부 확인 완료 (상태 코드: {response.status_code})")

    @allure.title("유효하지 않은 토큰으로 요청 시 401 또는 403 반환 확인")
    def test_invalid_token_returns_401_or_403(self, api_base_url):
        """[TC_019] 서명이 올바르지 않은 JWT 토큰(만료·변조 시뮬레이션)으로 요청 시
        서버가 토큰을 검증하고 접근을 거부하는지 확인."""
        with allure.step("[TC_019] 유효하지 않은 Bearer 토큰으로 GET /chatroom 요청"):
            response = requests.get(
                f"{api_base_url}/chatroom",
                headers={
                    "Authorization": f"Bearer {_INVALID_TOKEN}",
                    "x-elice-org-name-short": "qaproject",
                },
            )
            logger.info(f"GET /chatroom (유효하지 않은 토큰) 응답 코드: {response.status_code}")
            assert response.status_code in (401, 403), (
                f"유효하지 않은 토큰 요청에 예상치 못한 응답. "
                f"상태 코드: {response.status_code}, 응답: {response.text}"
            )
            logger.info(f"유효하지 않은 토큰 거부 확인 완료 (상태 코드: {response.status_code})")

    @allure.title("잘못된 인증 스킴으로 요청 시 401 또는 403 반환 확인")
    def test_wrong_auth_scheme_returns_401_or_403(self, api_base_url):
        """[TC_020] Bearer 대신 잘못된 스킴(Basic)을 사용하거나 토큰 형식이
        완전히 다른 경우 서버가 인증 스킴을 검증하고 거부하는지 확인."""
        with allure.step("[TC_020] 잘못된 인증 스킴(Basic)으로 GET /agent 요청"):
            response = requests.get(
                f"{api_base_url}/agent",
                headers={
                    "Authorization": "Basic dGVzdDp0ZXN0",  # base64("test:test")
                    "x-elice-org-name-short": "qaproject",
                },
            )
            logger.info(f"GET /agent (잘못된 인증 스킴) 응답 코드: {response.status_code}")
            assert response.status_code in (401, 403), (
                f"잘못된 인증 스킴 요청에 예상치 못한 응답. "
                f"상태 코드: {response.status_code}, 응답: {response.text}"
            )
            logger.info(f"잘못된 인증 스킴 거부 확인 완료 (상태 코드: {response.status_code})")

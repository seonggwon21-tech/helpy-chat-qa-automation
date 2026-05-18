"""
세부 특기사항 진입 UI 테스트 케이스.
"""

import pytest
import time
import logging
from pages.detailed_specialty_page import DetailedSpecialtyPage

logger = logging.getLogger(__name__)

class TestDetailedSpecialtyNavigation:
    """도구 탭을 상속받은 세부 특기사항 페이지로의 진입을 검증하는 테스트 케이스"""

    def test_navigate_to_detailed_specialty_successful(self, logged_in_driver):
        """
        테스트 케이스: 로그인 완료 후 [도구 탭 진입] ➡️ [세부 특기사항 클릭] 연속 검증
        """
        logger.info("🚀 [TC_142] 세부 특기사항 진입 테스트 검증을 시작합니다.")
        
        # 1. 셋업
        specialty_page = DetailedSpecialtyPage(logged_in_driver)

        # 2. 실행: 1단계 - 부모(ToolPage)의 도구 탭 진입 기능 호출
        logger.info("🖱️ 1단계: LNB 메뉴에서 [도구] 탭 클릭을 시작합니다.")
        specialty_page.setup_tool_tab()
        
        # 3. 실행: 2단계 - 자신의 세부 특기사항 카드 클릭 기능 호출
        logger.info("🖱️ 2단계: 도구 목록 화면에서 [세부 특기사항] 카드 클릭을 시작합니다.")
        specialty_page.navigate_to_detailed_specialty()

        # 4. 검증(Assert): URL에 'tools' 경로가 포함되어 페이지가 정상 전환되었는지 확인
        current_url = logged_in_driver.current_url
        logger.info(f"🔎 현재 브라우저 URL 최종 검증 중... 주소: {current_url}")
        
        assert "tools" in current_url, f"세부 특기사항 페이지 진입 실패! 현재 URL: {current_url}"
        
        logger.info("🎉 [성공] ToolPage 상속 구조를 통해 세부 특기사항 페이지로 완벽하게 이동되었습니다!")
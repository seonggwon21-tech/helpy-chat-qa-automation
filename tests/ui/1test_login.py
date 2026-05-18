"""
로그인 기능에 대한 UI 시나리오 테스트 스크립트.
"""

import pytest
import logging
from selenium.common.exceptions import TimeoutException
from pages.login_page import LoginPage
from pages.signup_page import SignupPage

logger = logging.getLogger(__name__)

class TestLogin:
    """로그인 프로세스 검증 테스트 스위트"""

    def test_login_and_onboarding_success(self, driver, base_url, test_user):
        """
        [TC-LOGIN-001] 로그인 및 온보딩 통합 성공 테스트
        
        1. 로그인 정보 입력 및 Login 클릭
        2. 최초 로그인인 경우 약관 동의 절차 수행 (예외 처리 포함)
        3. 최종적으로 메인 서비스 URL 진입 여부 검증
        """
        # 1. Page Object(객체) 초기화
        login_page = LoginPage(driver, base_url)
        signup_page = SignupPage(driver)
        
        # 2. 헬피챗 접속
        login_page.open()
        
        # 3. 로그인 정보 입력 및 실행 (공통 픽스처에서 주입받은 계정 사용)
        login_page.login(test_user["id"], test_user["pw"])
        
        # 4. 온보딩(약관 동의) 화면 처리 
        try:
            signup_page.agree_and_submit()
            logger.info("최초 로그인: 온보딩 약관 동의를 완료했습니다.")
        except TimeoutException:
            logger.info("기존 계정: 약관 동의 화면을 건너뛰고 메인으로 진입합니다.")
        
        # 5. 최종 결과 검증
        is_success = login_page.is_login_successful()
        assert is_success is True, "로그인 완료 후 메인 페이지(/ai-helpy-chat) 진입에 실패했습니다."

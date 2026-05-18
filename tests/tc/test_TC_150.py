"""
세부 특기사항 페이지 내 단원(숫자) 입력 폼 기능 검증 UI 시나리오 테스트.
"""

import pytest
import time
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pages.detailed_specialty_page import DetailedSpecialtyPage

logger = logging.getLogger(__name__)


class TestDetailedSpecialtyUnitInput:
    """[TC-150] 세부 특기사항 단원 입력창 기능 검증 테스트 스위트"""

    def test_unit_input_field_numeric_successful(self, logged_in_driver):
        """
        테스트 케이스: [TC-150] 다른 필드 입력 없이 '단원' 입력창에 숫자를 직접 입력했을 때 값이 정상 반영되는지 확인
        """
        logger.info("🚀 [TC-150] 세부 특기사항 단원 숫자 입력 테스트를 시작합니다.")

        # 1. 셋업: 기존에 만들어 둔 세부 특기사항 페이지 객체 활용
        specialty_page = DetailedSpecialtyPage(logged_in_driver)

        # 2. 이동 기능 재사용: [도구 탭 진입] -> [세부 특기사항 카드 클릭]
        specialty_page.setup_tool_tab()
        specialty_page.navigate_to_detailed_specialty()
        logger.info("✅ 세부 특기사항 페이지 진입 완료 (사전 조건 없음)")

        # 🎯 [스크린샷 HTML 기반 완벽 저격 로케이터]
        # HTML 소스코드에 명시된 name="unit" 속성을 활용하여 가장 확실하게 요소를 타겟팅합니다.
        UNIT_INPUT = (By.CSS_SELECTOR, "input[name='unit']")

        # 3. 단원 입력창이 화면에 렌더링되고 클릭 가능할 때까지 명시적 대기
        wait = WebDriverWait(logged_in_driver, 10)
        unit_field = wait.until(EC.element_to_be_clickable(UNIT_INPUT))

        # 4. '단원' 입력창 조작 및 숫자 입력
        # 표준 input 구조이므로 셀레니움 기본 clear와 send_keys가 완벽하게 작동합니다.
        target_number = "5"
        unit_field.click()
        unit_field.clear()
        unit_field.send_keys(target_number)
        logger.info(f"⌨️ 단원 입력창에 숫자 [{target_number}] 데이터 주입을 완료했습니다.")

        # 값이 들어간 상태를 유지하고 눈으로 확인하기 위한 임시 대기
        time.sleep(3)

        # 5. 검증(Assert): 입력창의 실제 'value' 속성을 긁어와 정상 반영되었는지 체크
        actual_value = unit_field.get_attribute("value")
        logger.info(f"🔎 단원 입력창 최종 결과 검증 중... 실제 value: '{actual_value}'")

        assert actual_value == target_number, (
            f"단원 입력 오류! 기대값: '{target_number}', 실제 입력된 값: '{actual_value}'"
        )
        
        logger.info("🎉 [성공] 단원 입력창에 숫자가 밀림이나 차단 없이 완벽하게 반영되었습니다!")
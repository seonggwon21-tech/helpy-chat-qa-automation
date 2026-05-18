"""
세부 특기사항 페이지 내 입력 폼 기능 검증 UI 시나리오 테스트.
"""

import pytest
import time
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pages.detailed_specialty_page import DetailedSpecialtyPage

logger = logging.getLogger(__name__)


class TestDetailedSpecialtyInput:
    """세부 특기사항 폼 입력 기능 검증 테스트 케이스"""

    def test_subject_input_field_successful(self, logged_in_driver):
        """
        테스트 케이스: 학교급(초등학교) 및 학년(1학년) 선택 후 과목창에 '중국어'가 정상 입력되는지 검증
        """
        logger.info("🚀 [TC] 세부 특기사항 과목 직접 입력 테스트를 시작합니다.")

        # 1. 페이지 객체 초기화 및 진입
        specialty_page = DetailedSpecialtyPage(logged_in_driver)
        specialty_page.setup_tool_tab()
        specialty_page.navigate_to_detailed_specialty()
        logger.info("✅ 세부 특기사항 페이지 진입 완료")

        wait = WebDriverWait(logged_in_driver, 10)

        # 🎯 [1단계] 학교급 드롭다운 박스 클릭 
        SCHOOL_LEVEL_COMBO = (By.XPATH, "//div[@role='combobox' and contains(., '학교급')] | //div[@role='combobox' and contains(@id, '_r_3t_')]")
        school_field = wait.until(EC.element_to_be_clickable(SCHOOL_LEVEL_COMBO))
        school_field.click()
        logger.info("🖱️ 학교급 드롭다운 박스 클릭 완료")
        time.sleep(0.5)
        
        # 드롭다운 레이어에서 '초등학교' 옵션 선택
        ELEMENT_SCHOOL = (By.XPATH, "//*[contains(@class, 'MuiAutocomplete-option') and normalize-space(text())='초등학교'] | //li[normalize-space(text())='초등학교'] | //*[normalize-space(text())='초등학교']")
        wait.until(EC.element_to_be_clickable(ELEMENT_SCHOOL)).click()
        logger.info("✅ 학교급: [초등학교] 선택 완료")
        time.sleep(0.5)

        # 🎯 [2단계] 학년 드롭다운 박스 클릭
        GRADE_COMBO = (By.XPATH, "//div[@role='combobox' and contains(@id, '_r_3v_')] | //label[contains(., '학년')]/..//div[@role='combobox']")
        grade_field = wait.until(EC.element_to_be_clickable(GRADE_COMBO))
        grade_field.click()
        logger.info("🖱️ 학년 드롭다운 박스 클릭 완료")
        time.sleep(0.5)
        
        # 드롭다운 레이어에서 '1학년' 옵션 선택
        ELEMENT_FIRST_GRADE = (By.XPATH, "//*[contains(@class, 'MuiAutocomplete-option') and normalize-space(text())='1학년'] | //li[normalize-space(text())='1학년'] | //*[normalize-space(text())='1학년']")
        wait.until(EC.element_to_be_clickable(ELEMENT_FIRST_GRADE)).click()
        logger.info("✅ 학년: [1학년] 선택 완료")
        time.sleep(0.5)

        # 🎯 [3단계] 상위 조건이 모두 충족되어 활성화된 과목 입력창 타겟팅
        SUBJECT_INPUT = (By.XPATH, "//input[@placeholder='과목을 선택해주세요. (직접 입력 가능)']")
        subject_field = wait.until(EC.presence_of_element_located(SUBJECT_INPUT))

        # 4. ActionChains를 사용하여 포커스를 잡고 키보드 이벤트를 직접 주입
        target_text = "중국어"
        
        actions = ActionChains(logged_in_driver)
        actions.move_to_element(subject_field)
        actions.click()
        
        for char in target_text:
            actions.send_keys(char)
            
        actions.perform()
        logger.info(f"⌨️ 과목 입력창에 [{target_text}] 직접 타이핑 완료")

        # 결과 확인을 위한 대기
        time.sleep(3)

        # 5. 검증(Assert): 입력창의 실제 'value' 속성을 읽어와 정상 반영되었는지 체크
        actual_value = subject_field.get_attribute("value")
        logger.info(f"🔎 입력창 최종 가동 결과 검증 중... 실제 value: '{actual_value}'")

        assert actual_value == target_text, (
            f"과목 입력 오류! 기대값: '{target_text}', 실제 입력된 값: '{actual_value}'"
        )
        
        logger.info("🎉 [성공] 제약 조건 해제 후 과목 창에 중국어가 완벽하게 반영되었습니다!")
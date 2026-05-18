"""
세부 특기사항 페이지 내 필수 폼 완성 후 '다음으로' 버튼 활성화 및 이동 검증 시나리오 테스트.
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


class TestDetailedSpecialtySubmit:
    """[TC-151] 세부 특기사항 전체 입력 후 다음 화면 이동 검증 테스트 스위트"""

    def test_submit_button_activation_and_navigation(self, logged_in_driver):
        """
        테스트 케이스: [TC-151] 학교급(초등학교), 학년(1학년), 과목(국어), 단원(1) 입력 시
        '다음으로' 버튼이 활성화되고, 이를 클릭하면 다음 단계로 정상 이동하는지 검증
        """
        logger.info("🚀 [TC-151] 세부 특기사항 필수 정보 입력 후 다음으로 이동 테스트를 시작합니다.")

        # 1. 페이지 객체 초기화 및 진입
        specialty_page = DetailedSpecialtyPage(logged_in_driver)
        specialty_page.setup_tool_tab()
        specialty_page.navigate_to_detailed_specialty()
        logger.info("✅ 세부 특기사항 페이지 진입 완료")

        wait = WebDriverWait(logged_in_driver, 10)

        # 🎯 [1단계] 학교급 드롭다운 박스 클릭 -> '초등학교' 옵션 선택
        SCHOOL_LEVEL_COMBO = (By.XPATH, "//div[@role='combobox' and contains(., '학교급')] | //div[@role='combobox' and contains(@id, '_r_3t_')]")
        wait.until(EC.element_to_be_clickable(SCHOOL_LEVEL_COMBO)).click()
        time.sleep(0.5)
        
        ELEMENT_SCHOOL = (By.XPATH, "//*[contains(@class, 'MuiAutocomplete-option') and normalize-space(text())='초등학교'] | //li[normalize-space(text())='초등학교']")
        wait.until(EC.element_to_be_clickable(ELEMENT_SCHOOL)).click()
        logger.info("✅ 학교급: [초등학교] 선택 완료")
        time.sleep(0.5)

        # 🎯 [2단계] 학년 드롭다운 박스 클릭 -> '1학년' 옵션 선택
        GRADE_COMBO = (By.XPATH, "//div[@role='combobox' and contains(@id, '_r_3v_')] | //label[contains(., '학년')]/..//div[@role='combobox']")
        wait.until(EC.element_to_be_clickable(GRADE_COMBO)).click()
        time.sleep(0.5)
        
        ELEMENT_FIRST_GRADE = (By.XPATH, "//*[contains(@class, 'MuiAutocomplete-option') and normalize-space(text())='1학년'] | //li[normalize-space(text())='1학년']")
        wait.until(EC.element_to_be_clickable(ELEMENT_FIRST_GRADE)).click()
        logger.info("✅ 학년: [1학년] 선택 완료")
        time.sleep(0.5)

        # 🎯 [3단계] 과목 드롭다운 박스 클릭 -> '국어' 옵션 선택
        SUBJECT_COMBO = (By.XPATH, "//input[@placeholder='과목을 선택해주세요. (직접 입력 가능)']/..")
        wait.until(EC.element_to_be_clickable(SUBJECT_COMBO)).click()
        time.sleep(0.5)

        ELEMENT_KOREAN = (By.XPATH, "//*[contains(@class, 'MuiAutocomplete-option') and normalize-space(text())='국어'] | //li[normalize-space(text())='국어']")
        wait.until(EC.element_to_be_clickable(ELEMENT_KOREAN)).click()
        logger.info("✅ 과목: [국어] 선택 완료")
        time.sleep(0.5)

        # 🎯 [4단계] 단원 입력창에 숫자 '5' 입력
        UNIT_INPUT = (By.CSS_SELECTOR, "input[name='unit']")
        unit_field = wait.until(EC.element_to_be_clickable(UNIT_INPUT))
        unit_field.click()
        unit_field.clear()
        unit_field.send_keys("5")
        logger.info("⌨️ 단원 입력창에 숫자 [5] 주입 완료")
        time.sleep(1)

        # 🎯 [5단계] 텍스트 기반 XPATH로 '다음으로' 버튼 찾기
        NEXT_BUTTON = (By.XPATH, "//button[normalize-space(text())='다음으로'] | //span[normalize-space(text())='다음으로']/..")
        next_button_element = wait.until(EC.presence_of_element_located(NEXT_BUTTON))

        # 6. 검증 1: 버튼이 화면에 활성화(상호작용 가능) 상태인지 체크
        # 'disabled' 속성이 붙어있지 않은지 assert로 확인합니다.
        is_enabled = next_button_element.is_enabled()
        logger.info(f"🔎 '다음으로' 버튼 활성화 상태 확인 중... 결과: {is_enabled}")
        
        assert is_enabled is True, "모든 값을 채웠으나 '다음으로' 버튼이 아직 비활성화 상태입니다."
        logger.info("✅ '다음으로' 버튼 활성화 확인 완료!")

        # 7. '다음으로' 버튼 클릭 및 이동 대기
        next_button_element.click()
        logger.info("🖱️ '다음으로' 버튼을 클릭했습니다.")
        time.sleep(3)  # 다음 화면으로 스무스하게 넘어가는 시간 대기

        # 8. 검증 2: 다음 탭인 '학생 정보 입력 및 생성' 화면이 켜졌는지 텍스트로 최종 검증
        # 상단 탭에 진한 글씨로 변경되었을 '학생 정보 입력 및 생성' 영역을 탐색합니다.
        NEXT_STEP_INDICATOR = (By.XPATH, "//*[normalize-space(text())='학생 정보 입력 및 생성']")
        assert wait.until(EC.visibility_of_element_located(NEXT_STEP_INDICATOR)), (
            "버튼을 눌렀으나 다음 단계 화면(학생 정보 입력 및 생성)으로 이동하지 못했습니다."
        )
        
        logger.info("🎉 [성공] 필수 폼 완성 후 다음 화면으로 완벽하게 페이징 이동했습니다!")
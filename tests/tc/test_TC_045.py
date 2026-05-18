"""
에이전트 탑색 탭 AI 에이전트 검색 테스트 케이스.
"""

import pytest
import time
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logger = logging.getLogger(__name__)

def test_navigate_to_agent_search(logged_in_driver, base_url):
    """
    [TC-045] AI 에이전트 검색 창 테스트 케이스
    """
    driver = logged_in_driver
    wait = WebDriverWait(driver, 10)
    
    # logger.info("🚀 [TC_032] 에이전트 탐색 진입 테스트 검증을 시작합니다.")
    
    try:
        hamburger_xpath = "//button[.//svg[@data-testid='barsIcon']]"
        hamburger_btn = wait.until(EC.element_to_be_clickable((By.XPATH, hamburger_xpath)))
        hamburger_btn.click()
    except Exception:
        # 화면이 커서 햄버거 버튼이 없거나 이미 열려있어서 에러가 나면 패스
        pass

    # 2. '에이전트 탐색' 버튼 클릭
    logger.info("🖱️ 1단계: LNB 메뉴에서 [에이전트 탐색] 탭 클릭을 시작합니다.")
    
    agent_search_xpath = "//*[text()='에이전트 탐색']"
    agent_search_btn = wait.until(EC.element_to_be_clickable((By.XPATH, agent_search_xpath)))
    agent_search_btn.click()

    # 3. 결과 검증 (Assertion)
    # 이동한 페이지의 URL에 '/agents' 경로가 포함되어 있는지 확인
    expected_url_part = "/agents"
    wait.until(EC.url_contains(expected_url_part))

    current_url = logged_in_driver.current_url
    # logger.info(f"🔎 현재 브라우저 URL 최종 검증 중... 주소: {current_url}")

    assert expected_url_part in driver.current_url, f"에이전트 탐색 페이지 이동 실패. 현재 URL: {driver.current_url}"
    
    # 플러스 검증: 페이지 상단에 '에이전트 탐색'이라는 타이틀 문구가 실제로 보이는지 확인
    page_title_xpath = "//*[text()='에이전트 탐색']"
    assert wait.until(EC.visibility_of_element_located((By.XPATH, page_title_xpath))).is_displayed()

    """[TC_045] AI 에이전트 검색창 검증"""

    logger.info("🚀 [TC_045] AI 에이전트 검색창 검증을 시작합니다.")
    logger.info("🖱️ 1단계: 화면에서 [AI 에이전트 검색] 창 클릭을 시작합니다.")

    # [로케이터 전략] 가장 변하지 않는 속성인 placeholder 값으로 input 창을 찾습니다.
    search_input_xpath = "//input[@placeholder='AI 에이전트 검색']"
    search_input = wait.until(EC.visibility_of_element_located((By.XPATH, search_input_xpath)))
    
    # 만약 기존에 입력된 값이 있을지 모르니 깔끔하게 비워주고 시작합니다.
    search_input.clear()
    
    # 테스트할 검색어 정의 
    test_search_keyword = "testtesttest"
    logger.info(f"⌨️ 검색창에 [{test_search_keyword}]를 입력합니다.")
    search_input.send_keys(test_search_keyword)
    
    
    # 화면 갱신을 위해 살짝 대기합니다.
    time.sleep(1)

    # ---------------------------------------------------------
    # 7. 검색 결과 필터링 검증
    # ---------------------------------------------------------
    logger.info("🔎 입력한 검색어대로 필터링이 정상적으로 되었는지 목록을 검증합니다.")
    
      
    search_title_xpath = "//*[text()='검색 결과가 없습니다.']"
    assert wait.until(EC.visibility_of_element_located((By.XPATH, search_title_xpath))).is_displayed()
        
    logger.info(f"🎉 [{test_search_keyword}] 검색 및 목록 필터링 검증 완료!")
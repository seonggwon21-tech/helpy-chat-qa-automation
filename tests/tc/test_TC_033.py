"""
에이전트 검색 +만들기 테스트 케이스.
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
    [TC-033] 사이드바 메뉴를 통한 에이전트 탐색 페이지 이동 검증
    """
    driver = logged_in_driver
    wait = WebDriverWait(driver, 10)
    
    logger.info("🚀 [TC_032] 에이전트 탐색 진입 테스트 검증을 시작합니다.")
    
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
    logger.info(f"🔎 현재 브라우저 URL 최종 검증 중... 주소: {current_url}")

    assert expected_url_part in driver.current_url, f"에이전트 탐색 페이지 이동 실패. 현재 URL: {driver.current_url}"
    
    # 플러스 검증: 페이지 상단에 '에이전트 탐색'이라는 타이틀 문구가 실제로 보이는지 확인
    page_title_xpath = "//*[text()='에이전트 탐색']"
    assert wait.until(EC.visibility_of_element_located((By.XPATH, page_title_xpath))).is_displayed()


    # 4. '+ 만들기' 버튼 클릭 및 이동 검증 (추가된 시나리오)
    logger.info("🖱️ 2단계: 우측 상단 [+ 만들기] 버튼 클릭을 시작합니다.")

    
    # 텍스트 앞뒤 공백을 방어하기 위해 normalize-space()를 사용한 정확한 매칭
    create_agent_xpath = "//*[contains(text(), '만들기')]"
    # create_agent_xpath = "//*[@data-icon='plus']/ancestor::button"
    # create_agent_xpath = "//*[@data-testid='plusIcon']/ancestor::button"

    create_agent_btn = wait.until(EC.element_to_be_clickable((By.XPATH, create_agent_xpath)))
    create_agent_btn.click()

    # 5. 새 에이전트 만들기 화면 진입 최종 검증
    # 이동할 페이지의 URL 규칙을 검증합니다. (보통 /create 나 /new-agent 등이 붙습니다.)
    # 실제 진입 후 주소창을 확인하시고 아래 '/create' 부분을 사이트 주소에 맞게 수정해 주세요!
    wait.until(EC.url_contains("/agents/"))
    wait.until(EC.url_contains("/builder"))
    

    current_url = logged_in_driver.current_url
    logger.info(f"🔎 현재 에이전트 생성 화면 URL 검증 중... 주소: {current_url}")
    assert "/agents/" in current_url and "/builder" in current_url, f"새 에이전트 만들기 페이지 이동 실패. 현재 URL: {current_url}"

    # 화면 타이틀 검증: "새 에이전트 만들기" 혹은 "에이전트 생성" 문구가 보이는지 확인
    # 이 부분도 실제 이동한 화면의 헤더 타이틀 텍스트에 맞게 문구를 살짝 다듬어주시면 됩니다.
    create_page_title_xpath = "//*[text()='새 에이전트 만들기']"
    assert wait.until(EC.visibility_of_element_located((By.XPATH, create_page_title_xpath))).is_displayed()

    logger.info("🎉 [TC_033] 에이전트 탐색 +만들기 생성 화면 진입까지 올 패스!")
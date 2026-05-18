"""
프로젝트 전역에서 사용되는 Pytest Fixture 설정 파일.
WebDriver 초기화, 공통 환경 변수 관리, Jira 후처리 담당.
"""

import pytest
import requests
import json
import re
import os
import logging
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from requests.auth import HTTPBasicAuth
from pages.login_page import LoginPage
from pages.signup_page import SignupPage

# .env 파일을 읽어서 OS 환경 변수로 메모리에 로드합니다. (로컬에서만 사용)
load_dotenv()

# 로거 설정
logger = logging.getLogger(__name__)

####### [참고] WebDriver 매니저 관련 설명
# webdriver_manager 사용 여부는 프로젝트 상황에 따라 다릅니다.
# Selenium 4.6+ 부터는 Selenium Manager가 내장되어서 chromedriver를 자동 관리하지만, 명시적으로 webdriver_manager를 사용할 수도 있습니다.
# 과거에 ChromeDriver를 직접 설치/버전관리해야 했을 때 많이 사용했습니다.
# 실무에서도 최근에는 보통 제거하는 추세입다만 아직 아래 경우에는 webdriver_manager를 쓰기도 합니다.
#  - 회사 내부망이라 Selenium Manager 다운로드 차단
#  - 특정 ChromeDriver 버전 고정 필요
#  - CI/CD 환경에서 드라이버 버전 통제 필요
#  - 오래된 Selenium 버전 유지 프로젝트
# from webdriver_manager.chrome import ChromeDriverManager # pip install webdriver-manager 필요
####### 그래서 요즘은 대부분 아래처럼만 씁니다.
from selenium import webdriver

# =========================================================
# [1] 테스트 기본 정보 및 보안 설정
# =========================================================
BASE_UI_URL = "https://qaproject.elice.io"
BASE_API_URL = "https://dev-v2-community-api.dev.elicer.io"

TEST_USER = {
    "id": os.getenv("TEST_USER_ID"), # 환경 변수에 설정 - HelpyChat 아이디
    "pw": os.getenv("TEST_USER_PW")  # 환경 변수에 설정 - HelpyChat 비밀번호
}

JIRA_URL = os.getenv("JIRA_BASE_URL")            # 환경변수에 설정 - Jira 주소
JIRA_EMAIL = os.getenv("JIRA_EMAIL")             # 환경변수에 설정 - Jira 이메일
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")     # 환경변수에 설정 - Jira API 토큰
JIRA_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY") # 환경변수에 설정 - 티켓을 생성할 프로젝트 키


# =========================================================
# [2] UI 자동화 관련 Fixture: WebDriver
# =========================================================
@pytest.fixture(scope="function")
def driver():
    """
    각 테스트 함수마다 Selenium WebDriver를 초기화하고 브라우저 세션을 시작함.
    테스트 종료 후 브라우저를 닫음(Teardown).
    """
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    # options.add_argument("--headless")  # CI/CD 환경용 - Jenkins 등 서버 (GUI 없이) 실행 시 활성화

    ####### [참고] WebDriver 매니저 관련 설명
    # WebDriver 매니저를 통해 드라이버 자동 설치 및 실행
    # from selenium.webdriver.chrome.service import Service
    # driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    # driver.implicitly_wait(10)
    ####### 그래서 요즘은 대부분 아래처럼만 씁니다.
    driver = webdriver.Chrome(options=options)

    yield driver
    driver.quit()

# =========================================================
# [3] API 자동화 관련 Fixture: 인증 토큰 및 세션
# =========================================================
@pytest.fixture(scope="session")
def auth_token():
    """테스트 세션 시작 시 단 한 번 로그인하여 API 인증용 Bearer 토큰 획득."""
    login_url = f"{BASE_API_URL}/login"  # 실제 API 명세의 로그인 엔드포인트 확인 필요 (가정)
    payload = {
        "username": TEST_USER["id"],
        "password": TEST_USER["pw"]
    }
    # 실제 환경에서는 명세서에 따라 data(form-data) 또는 json 형식을 선택.
    response = requests.post(login_url, data=payload)
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        # 로그인 실패 시 테스트 중단을 위해 예외 발생
        # (만약 로그인 API가 아직 미구현이라면 수동으로 토큰을 입력하도록 유도 가능)
        pytest.fail(f"로그인 실패! 상태 코드: {response.status_code}")

@pytest.fixture(scope="function")
def api_session(auth_token):
    """인증 헤더가 포함된 requests.Session 객체를 제공함."""
    session = requests.Session()
    session.headers.update({
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json",
        "x-elice-org-name-short": "elice"  # 명세서에 포함된 필수 헤더 예시
    })
    yield session
    session.close()

# =========================================================
# [4] 공통 환경 설정 Fixture
# =========================================================
@pytest.fixture
def base_url():
    return BASE_UI_URL

@pytest.fixture
def api_base_url():
    return BASE_API_URL

@pytest.fixture
def test_user():
    return TEST_USER

# =========================================================
# [5] 사전 조건(Pre-condition) 특화 Fixture
# =========================================================
@pytest.fixture(scope="function")
def logged_in_driver(driver, base_url, test_user):
    """UI 로그인이 완료된 상태의 WebDriver를 제공."""
    login_page = LoginPage(driver, base_url)
    signup_page = SignupPage(driver)
    
    # 1. 헬피챗 접속 및 로그인
    login_page.open()
    login_page.login(test_user["id"], test_user["pw"])
    
    # 2. 온보딩 예외 처리
    try:
        signup_page.agree_and_submit()
    except TimeoutException:
        pass
        
    # 3. 로그인 성공 검증 (실패 시 여기서 테스트 중단)
    assert login_page.is_login_successful() is True, "Fixture 사전 조건 설정 실패: 로그인 불가"
    return driver # 로그인이 완료된 브라우저 객체를 반환

# =========================================================
# [6] 사전 조건(Pre-condition) 특화 Fixture
# API 쿠키 인젝션 기반 빠른 로그인
# =========================================================
# @pytest.fixture(scope="function")
# def logged_in_driver(driver, base_url, auth_token):
#     """
#     [사전 조건: API 쿠키 인젝션 기반 빠른 로그인]
#     UI 로딩을 기다리지 않고, API로 발급받은 세션 토큰을 브라우저 쿠키에 직접 주입하여
#     0.1초 만에 로그인된 상태로 만듬.
#     """
#     # 1. 쿠키를 세팅하려면 먼저 해당 도메인에 한 번 접속해야 함.
#     # 로그인 화면으로 리다이렉트 되더라도 일단 접속.
#     driver.get(base_url)
    
#     # 2. 브라우저 쿠키에 API로 받아온 토큰(auth_token)을 직접 주입함.
#     # Key 이름 'eliceSessionKey'를 사용.
#     driver.add_cookie({
#         "name": "eliceSessionKey",
#         "value": auth_token,
#         "domain": ".elice.io" # 쿠키 탭에 명시된 도메인
#     })
    
#     # 3. 쿠키 주입 후, 우리가 진짜로 테스트할 메인 채팅 화면으로 이동.
#     # 브라우저는 방금 넣은 쿠키를 서버로 보내므로, 서버는 "아, 로그인된 유저구나!" 하고 통과시킴.
#     driver.get(f"{base_url}/ai-helpy-chat")
    
#     # 4. (선택) 최초 로그인 계정일 경우 온보딩(약관 동의) 화면이 뜰 수 있으므로 기존 예외 처리는 유지.
#     from selenium.common.exceptions import TimeoutException
#     from pages.signup_page import SignupPage
    
#     signup_page = SignupPage(driver)
#     try:
#         signup_page.agree_and_submit()
#     except TimeoutException:
#         pass # 이미 약관 동의를 한 기존 계정은 스킵
        
#     return driver


# =========================================================
# [7] Jira API 연동 헬퍼 함수
# =========================================================
def create_jira_bug_ticket(summary, description):
    """Jira REST API를 호출하여 버그 이슈를 자동 생성하고 이슈 키를 반환."""
    url = f"{JIRA_URL}/rest/api/2/issue"
    auth = HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN)
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    
    # Jira 티켓 생성 규격(Payload)
    payload = json.dumps({
        "fields": {
            "project": {"key": JIRA_PROJECT_KEY},
            "summary": summary,
            "description": description,
            "issuetype": {"name": "Bug"}, # Jira에 'Bug' 또는 '버그' 이슈 타입이 존재해야 함
            "labels": ["Automation", "UI-Test"]
        }
    })

    try:
        response = requests.post(url, data=payload, headers=headers, auth=auth)
        if response.status_code == 201:
            issue_key = response.json().get("key")
            logger.info(f"🚨 [JIRA 연동 성공] 티켓 자동 생성 완료: {JIRA_URL}/browse/{issue_key}")
            return issue_key # 스크린샷 첨부를 위해 생성된 티켓 번호를 반환
        else:
            logger.error(f"❌ [JIRA 연동 실패] 응답 코드: {response.status_code}, 상세: {response.text}")
            return None
    except Exception as e:
        logger.error(f"❌ [JIRA 통신 에러] API 호출 중 문제가 발생했습니다: {e}")
        return None

def attach_image_to_jira(issue_key, image_bytes):
    """생성된 Jira 이슈에 스크린샷 이미지를 직접 첨부합니다."""
    url = f"{JIRA_URL}/rest/api/2/issue/{issue_key}/attachments"
    auth = HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN)
    # Jira 첨부파일 API의 핵심: 이 헤더가 없으면 무조건 404 에러가 납니다!
    headers = {"X-Atlassian-Token": "no-check"}
    # 메모리에 있는 스크린샷 데이터(image_bytes)를 파일 형태로 포장해서 전송
    files = {"file": ("error_screenshot.png", image_bytes, "image/png")}
    
    try:
        response = requests.post(url, headers=headers, auth=auth, files=files)
        if response.status_code == 200:
            logger.info(f"📎 [JIRA 첨부 성공] 스크린샷 이미지가 티켓에 정상 업로드되었습니다.")
        else:
            logger.error(f"❌ [JIRA 첨부 실패] 상태 코드: {response.status_code}, 상세: {response.text}")
    except Exception as e:
        logger.error(f"❌ [JIRA 첨부 에러] {e}")

# =========================================================
# [8] Pytest Hook: 테스트 실패 감지 및 후처리 (Jira)
# =========================================================
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """테스트 실패 시 Jira에 스크린샷과 로그를 전송."""
    outcome = yield
    rep = outcome.get_result()
    
    # 테스트 실행(call) 중 실패(failed)한 경우에만 동작
    if rep.when == "call" and rep.failed:
        # 1. WebDriver 객체 가져오기
        driver = item.funcargs.get("driver") or item.funcargs.get("logged_in_driver")
        
        if driver:
            # 2. 스크린샷을 찍어서 변수(바이트 데이터)에 저장
            screenshot_bytes = driver.get_screenshot_as_png()
            
            # 3. 에러 메시지 추출 및 외계어(ANSI 색상 코드) 제거
            test_name = item.name
            raw_error = str(call.excinfo.value) if call.excinfo else "알 수 없는 에러"
            # 터미널 색상 코드를 깔끔하게 지워주는 정규표현식
            clean_error_message = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', raw_error)
            
            # 4. Jira 티켓 제목 및 내용 구성
            summary = f"[자동화 버그] {test_name} 테스트 실패"
            description = (
                f"UI 자동화 테스트 실행 중 결함이 발견되었습니다.\n\n"
                f"* 🌐 실행 환경:* Chrome / Base URL: {item.funcargs.get('base_url', BASE_UI_URL)}\n"
                f"* 📝 테스트 케이스:* {test_name}\n\n"
                f"*🚨 발생한 에러 메시지:*\n"
                f"{{code:python}}\n{clean_error_message}\n{{code}}\n\n"
                f"자세한 화면 캡처는 본 티켓의 *첨부파일*을 확인해 주세요."
            )
            
            # 5. Jira 티켓 먼저 생성
            issue_key = create_jira_bug_ticket(summary, description)
            
            # 6. 티켓 생성이 성공했다면, 방금 찍어둔 스크린샷을 그 티켓에 바로 업로드
            if issue_key:
                attach_image_to_jira(issue_key, screenshot_bytes)

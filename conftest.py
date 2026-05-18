"""
프로젝트 전역에서 사용되는 Pytest Fixture 설정 파일.
WebDriver 초기화, 공통 환경 변수 관리 담당.
"""

import pytest
import requests
import os
import logging
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from pages.login_page import LoginPage
from pages.signup_page import SignupPage

# .env 파일을 읽어서 OS 환경 변수로 메모리에 로드합니다. (로컬에서만 사용)
load_dotenv()

logger = logging.getLogger(__name__)


# =========================================================
# [1] 테스트 기본 정보 및 보안 설정
# =========================================================
BASE_UI_URL = "https://qaproject.elice.io"
BASE_API_URL = "https://api.example.com"
AUTH_API_URL = "https://auth.example.com"

TEST_USER = {
    "id": os.getenv("TEST_USER_ID"), # 환경 변수에 설정 - HelpyChat 아이디
    "pw": os.getenv("TEST_USER_PW")  # 환경 변수에 설정 - HelpyChat 비밀번호
}


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
    if os.getenv("JENKINS_HOME"):
        options.add_argument("--headless")

    driver = webdriver.Chrome(options=options)

    yield driver
    driver.quit()

# =========================================================
# [3] API 자동화 관련 Fixture: 인증 토큰 및 세션
# =========================================================
@pytest.fixture(scope="session")
def auth_token():
    """테스트 세션 시작 시 단 한 번 로그인하여 API 인증용 Bearer 토큰 획득."""
    login_url = f"{AUTH_API_URL}/login/otp"
    payload = {
        "username": TEST_USER["id"],
        "password": TEST_USER["pw"]
    }
    response = requests.post(login_url, json=payload)
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        pytest.fail(f"로그인 실패! 상태 코드: {response.status_code}")

@pytest.fixture(scope="function")
def api_session(auth_token):
    """인증 헤더가 포함된 requests.Session 객체를 제공함."""
    session = requests.Session()
    session.headers.update({
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json",
        "x-elice-org-name-short": "qaproject"
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

    login_page.open()
    login_page.login(test_user["id"], test_user["pw"])

    try:
        signup_page.agree_and_submit()
    except TimeoutException:
        pass

    assert login_page.is_login_successful() is True, "Fixture 사전 조건 설정 실패: 로그인 불가"
    return driver


# =========================================================
# [6] 테스트 실패 시 자동 스크린샷
# =========================================================
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and report.failed:
        driver = item.funcargs.get("logged_in_driver") or item.funcargs.get("driver")
        if driver:
            os.makedirs("reports/screenshots", exist_ok=True)
            safe_name = item.nodeid.replace("/", "_").replace("::", "_").replace("\\", "_")
            screenshot_path = f"reports/screenshots/{safe_name}.png"
            driver.save_screenshot(screenshot_path)
            logger.info(f"실패 스크린샷 저장: {screenshot_path}")

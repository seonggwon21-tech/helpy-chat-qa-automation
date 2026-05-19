"""
프로젝트 전역에서 사용되는 Pytest Fixture 설정 파일.
WebDriver 초기화, 공통 환경 변수 관리 담당.
"""

import json
import os
import time
import pytest
import requests
from pathlib import Path
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException

from pages.login_page import LoginPage
from pages.signup_page import SignupPage
from config.config import BASE_UI_URL, BASE_API_URL, TEST_USER, DEFAULT_API_TIMEOUT
from utils.logger import get_custom_logger

load_dotenv()

logger = get_custom_logger(__name__)

AUTH_API_URL = "https://auth.example.com"

_COOKIE_CACHE_PATH = Path(".pytest_cache/elice_session.json")
_COOKIE_TTL = 30 * 60  # 30분(초 단위)


def _load_cached_cookies() -> list | None:
    if not _COOKIE_CACHE_PATH.exists():
        return None
    with open(_COOKIE_CACHE_PATH) as f:
        data = json.load(f)
    if time.time() - data["timestamp"] > _COOKIE_TTL:
        return None
    return data["cookies"]


def _save_cookies(cookies: list) -> None:
    _COOKIE_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(_COOKIE_CACHE_PATH, "w") as f:
        json.dump({"timestamp": time.time(), "cookies": cookies}, f)


# =========================================================
# [2] UI 자동화 관련 Fixture: WebDriver
# =========================================================
@pytest.fixture(scope="function")
def driver():
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    if os.getenv("JENKINS_HOME"):
        options.add_argument("--headless")

    d = webdriver.Chrome(options=options)
    yield d
    try:
        d.quit()
    except Exception:
        pass


# =========================================================
# [3] API 자동화 관련 Fixture: 인증 토큰 및 세션
# =========================================================
@pytest.fixture(scope="session")
def auth_token():
    """API 인증용 Bearer 토큰을 .env에서 직접 로드. Bearer 접두사는 자동 제거."""
    token = os.getenv("AUTH_TOKEN")
    if not token:
        pytest.fail("AUTH_TOKEN이 .env에 설정되지 않았습니다.")
    return token.removeprefix("Bearer ").strip()


@pytest.fixture(scope="function")
def api_session(auth_token):
    """인증 헤더가 포함된 requests.Session 객체를 제공함."""
    session = requests.Session()
    session.headers.update({
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json",
        "x-elice-org-name-short": "qaproject",
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
def authenticated_driver(driver, base_url, test_user):
    """UI 로그인이 완료된 상태의 WebDriver를 제공. 쿠키 캐싱으로 재로그인 최소화."""
    login_page = LoginPage(driver, base_url)

    chat_url = f"{base_url}/ai-helpy-chat"

    cached_cookies = _load_cached_cookies()
    if cached_cookies:
        driver.get(base_url)
        for cookie in cached_cookies:
            try:
                driver.add_cookie(cookie)
            except Exception:
                pass
        driver.get(chat_url)
        logger.info("캐시된 쿠키로 로그인 세션 복원 완료")
    else:
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        signup_page = SignupPage(driver)
        login_page.open()
        login_page.login(test_user["id"], test_user["pw"])
        try:
            signup_page.agree_and_submit()
        except TimeoutException:
            pass
        # SSO 리다이렉트 완료(qaproject.elice.io 복귀) 후 쿠키 저장
        try:
            WebDriverWait(driver, 30).until(EC.url_contains("qaproject.elice.io"))
        except TimeoutException:
            pass
        _save_cookies(driver.get_cookies())
        logger.info(f"UI 로그인 완료 및 쿠키 캐시 저장 (현재 URL: {driver.current_url})")
        driver.get(chat_url)

    if not login_page.is_login_successful():
        os.makedirs("reports/screenshots", exist_ok=True)
        driver.save_screenshot("reports/screenshots/fixture_login_failed.png")
        logger.error(f"로그인 실패 시점 URL: {driver.current_url}")
        if _COOKIE_CACHE_PATH.exists():
            _COOKIE_CACHE_PATH.unlink()
            logger.info("만료된 쿠키 캐시 삭제 완료")
        pytest.fail("Fixture 사전 조건 설정 실패: 로그인 불가")
    return driver


# =========================================================
# [6] 테스트 실패 시 자동 스크린샷
# =========================================================
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when in ("call", "setup") and report.failed:
        driver = item.funcargs.get("authenticated_driver") or item.funcargs.get("driver")
        if driver:
            os.makedirs("reports/screenshots", exist_ok=True)
            safe_name = item.nodeid.replace("/", "_").replace("::", "_").replace("\\", "_")
            screenshot_path = f"reports/screenshots/{safe_name}.png"
            driver.save_screenshot(screenshot_path)
            logger.info(f"실패 스크린샷 저장: {screenshot_path}")

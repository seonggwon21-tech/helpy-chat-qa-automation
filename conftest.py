"""
프로젝트 전역에서 사용되는 Pytest Fixture 설정 파일.
WebDriver 초기화, 공통 환경 변수 관리 담당.
"""

import json
import os
import platform
import sys
import time
import pytest
import allure
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

AUTH_API_URL = os.getenv("AUTH_API_URL", "")


def pytest_sessionstart(session):
    props = [
        f"Python={sys.version.split()[0]}",
        f"OS={platform.system()} {platform.release()}",
        f"Browser=Chrome",
        f"Target.URL={BASE_UI_URL}",
        f"Environment=Local",
    ]
    Path("allure-results").mkdir(exist_ok=True)
    Path("allure-results/environment.properties").write_text("\n".join(props), encoding="utf-8")

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
    if os.getenv("JENKINS_HOME") or os.getenv("CI"):
        options.add_argument("--headless")

    download_dir = os.getenv("DOWNLOAD_DIR", str(Path.home() / "Downloads"))
    options.add_experimental_option("prefs", {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
    })

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
    """로그인 API로 Bearer 토큰 자동 발급. AUTH_TOKEN 환경변수가 있으면 그것을 우선 사용."""
    token = os.getenv("AUTH_TOKEN")
    if token:
        return token.removeprefix("Bearer ").strip()

    login_id = os.getenv("TEST_USER_ID")
    password = os.getenv("TEST_USER_PW")
    if not login_id or not password:
        pytest.fail("AUTH_TOKEN 또는 TEST_USER_ID/TEST_USER_PW가 .env에 설정되지 않았습니다.")

    response = requests.post(
        "https://api-account.elice.io/login/otp",
        json={"login_id": login_id, "password": password},
        headers={"Content-Type": "application/json"},
        timeout=30,
    )
    if response.status_code != 200:
        pytest.fail(f"로그인 API 실패. 상태 코드: {response.status_code}, 응답: {response.text}")

    token = response.json().get("access_token")
    if not token:
        pytest.fail(f"로그인 응답에 access_token이 없습니다. 응답: {response.text}")
    return token


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
        # CDP로 도메인 제약 없이 쿠키 직접 주입 (SSO 리다이렉트 문제 우회)
        driver.execute_cdp_cmd("Network.enable", {})
        for cookie in cached_cookies:
            cdp_cookie = {
                "name": cookie["name"],
                "value": cookie["value"],
                "domain": cookie.get("domain", "qaproject.elice.io"),
                "path": cookie.get("path", "/"),
                "secure": cookie.get("secure", False),
                "httpOnly": cookie.get("httpOnly", False),
            }
            if "expiry" in cookie:
                cdp_cookie["expires"] = cookie["expiry"]
            try:
                driver.execute_cdp_cmd("Network.setCookie", cdp_cookie)
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
            with open(screenshot_path, "rb") as f:
                allure.attach(f.read(), name="실패 스크린샷", attachment_type=allure.attachment_type.PNG)
            logger.info(f"실패 스크린샷 저장: {screenshot_path}")

"""
프로젝트 전역에서 사용되는 Pytest Fixture 설정 파일.
WebDriver 초기화, 공통 환경 변수 관리 담당.
"""

import json
import os
import platform
import subprocess
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
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from pages.login_page import LoginPage
from pages.signup_page import SignupPage
from config.config import BASE_UI_URL, BASE_API_URL, TEST_USER, DEFAULT_API_TIMEOUT, DEFAULT_WAIT_TIME
from utils.logger import get_custom_logger

load_dotenv()

logger = get_custom_logger(__name__)


def pytest_sessionstart(session):
    # CI 환경 여부 판단
    is_ci = bool(os.getenv("JENKINS_HOME") or os.getenv("CI"))

    # Git 커밋 해시 (CI 파이프라인에서 회귀 추적용)
    try:
        git_commit = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], stderr=subprocess.DEVNULL
        ).decode().strip()
    except Exception:
        git_commit = "N/A"

    props = [
        f"Python={sys.version.split()[0]}",
        f"OS={platform.system()} {platform.release()}",
        f"Browser=Chrome",
        f"Target.URL={BASE_UI_URL}",
        f"Environment={'CI' if is_ci else 'Local'}",
        f"Build.Number={os.getenv('BUILD_NUMBER', 'local')}",
        f"Git.Commit={git_commit}",
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
    """GitHub Secrets의 AUTH_TOKEN 환경변수에서 Bearer 토큰을 로드한다.

    CI: GitHub Secrets에 AUTH_TOKEN 등록 후 워크플로우 env로 전달.
    로컬: .env 파일에 AUTH_TOKEN=<token> 형식으로 등록.
    토큰 갱신: 브라우저 Network 탭에서 Authorization 헤더 값을 복사해 Secret 업데이트.
    """
    token = os.getenv("AUTH_TOKEN")
    if not token:
        pytest.fail(
            "AUTH_TOKEN 환경변수가 설정되지 않았습니다.\n"
            "CI: GitHub Secrets에 AUTH_TOKEN을 등록하고 워크플로우 env에 추가하세요.\n"
            "로컬: .env 파일에 AUTH_TOKEN=<token>을 추가하세요."
        )
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
    using_cache = False

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
        using_cache = True
        logger.info("캐시된 쿠키로 로그인 세션 복원 완료")
    else:
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

    # 캐시 복원 경로: 채팅 URL 진입 여부만 확인 (LoginPage 로케이터 의존성 제거)
    # 신규 로그인 경로: PersonIcon 포함 전체 검증으로 로그인 완료를 확실히 판단
    if using_cache:
        try:
            WebDriverWait(driver, DEFAULT_WAIT_TIME).until(EC.url_contains("ai-helpy-chat"))
            login_ok = True
        except TimeoutException:
            login_ok = False
    else:
        login_ok = login_page.is_login_successful()

    if not login_ok:
        os.makedirs("reports/screenshots", exist_ok=True)
        driver.save_screenshot("reports/screenshots/fixture_login_failed.png")
        logger.error(f"로그인 실패 시점 URL: {driver.current_url}")
        if _COOKIE_CACHE_PATH.exists():
            _COOKIE_CACHE_PATH.unlink()
            logger.info("만료된 쿠키 캐시 삭제 완료")
        pytest.fail("Fixture 사전 조건 설정 실패: 로그인 불가")
    return driver


# =========================================================
# [5-2] 사전 대화가 생성된 상태의 ChatPage 제공 Fixture
# =========================================================
@pytest.fixture(scope="function")
def seeded_chat(authenticated_driver):
    """사전 대화 1개가 생성된 ChatPage 인스턴스를 반환합니다.

    '기존 대화가 있는 상태'를 전제로 하는 테스트 케이스에서 재사용 가능합니다.
    사전 준비 로직을 테스트 본문에서 분리해 TC 핵심 시나리오에 집중하도록 돕습니다.

    Usage:
        def test_something(self, seeded_chat):
            chat_page = seeded_chat
            driver = seeded_chat.driver
    """
    from pages.chat_page import ChatPage
    chat_page = ChatPage(authenticated_driver)
    chat_page.send_message("안녕하세요, 대화 보존 테스트입니다.")
    chat_page.wait_for_ai_response()
    logger.info("seeded_chat: 사전 대화 생성 완료")
    return chat_page


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

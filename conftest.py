"""
프로젝트 전역에서 사용되는 Pytest Fixture 설정 파일.
WebDriver 초기화, 공통 환경 변수 관리 담당.
"""

import json
import logging
import os
import platform
import subprocess
import sys
import time
from pathlib import Path

import allure
import pytest
import requests
from dotenv import load_dotenv
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config.config import BASE_API_URL, BASE_UI_URL, DEFAULT_WAIT_TIME, TEST_USER
from pages.login_page import LoginPage
from pages.signup_page import SignupPage

load_dotenv()

# 콘솔 로그는 pytest log_cli(log_cli=true)가 일원화한다.
# 모듈별 StreamHandler를 직접 부착하면 log_cli와 중복 출력되므로,
# 테스트·페이지 객체와 동일하게 표준 logging 로거를 사용한다.
logger = logging.getLogger(__name__)


# =========================================================
# [0] CLI 옵션 및 파라미터화 훅
# =========================================================
def pytest_addoption(parser):
    parser.addoption(
        "--browser", action="store", default="chrome",
        choices=["chrome", "edge", "firefox", "all"],
        help="실행할 브라우저 (chrome | edge | firefox | all)",
    )


def pytest_generate_tests(metafunc):
    if "browser" in metafunc.fixturenames:
        opt = metafunc.config.getoption("--browser")
        browsers = ["chrome", "edge", "firefox"] if opt == "all" else [opt]
        metafunc.parametrize("browser", browsers)


def pytest_sessionstart(session):
    is_ci = bool(os.getenv("JENKINS_HOME") or os.getenv("CI"))

    try:
        git_commit = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], stderr=subprocess.DEVNULL
        ).decode().strip()
    except Exception:
        git_commit = "N/A"

    try:
        browser_opt = session.config.getoption("--browser")
        browser_label = "Chrome / Edge / Firefox" if browser_opt == "all" else browser_opt.capitalize()
    except ValueError:
        browser_label = "Chrome"

    props = [
        f"Python={sys.version.split()[0]}",
        f"OS={platform.system()} {platform.release()}",
        f"Browser={browser_label}",
        f"Target.URL={BASE_UI_URL}",
        f"Environment={'CI' if is_ci else 'Local'}",
        f"Build.Number={os.getenv('BUILD_NUMBER', 'local')}",
        f"Git.Commit={git_commit}",
    ]
    Path("allure-results").mkdir(exist_ok=True)
    Path("allure-results/environment.properties").write_text("\n".join(props), encoding="utf-8")


_COOKIE_CACHE_DIR = Path(__file__).parent / ".pytest_cache"
_COOKIE_TTL = 30 * 60  # 30분(초 단위)


def _cookie_cache_path(browser: str) -> Path:
    """브라우저별 쿠키 캐시 파일 경로를 반환합니다.

    --browser all 실행 시 Chrome 캐시가 Firefox 세션에 재사용되는
    인증 실패를 방지하기 위해 브라우저명으로 파일을 분리합니다.
    Path(__file__).parent 기반 절대 경로로 실행 위치에 무관합니다.
    """
    return _COOKIE_CACHE_DIR / f"elice_session_{browser}.json"


def _load_cached_cookies(browser: str) -> list | None:
    path = _cookie_cache_path(browser)
    if not path.exists():
        return None
    with open(path) as f:
        data = json.load(f)
    if time.time() - data["timestamp"] > _COOKIE_TTL:
        return None
    return data["cookies"]


def _save_cookies(cookies: list, browser: str) -> None:
    path = _cookie_cache_path(browser)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump({"timestamp": time.time(), "cookies": cookies}, f)


# =========================================================
# [1] 브라우저 / 다운로드 디렉터리 Fixture
# =========================================================
@pytest.fixture
def browser(request):
    """pytest_generate_tests가 주입한 브라우저명 문자열을 반환합니다.

    pytest_generate_tests 파라미터화 없이 직접 요청되는 경우(단독 fixture 테스트 등)에도
    AttributeError 없이 기본값 "chrome"을 반환하도록 getattr 가드를 사용합니다.
    """
    return getattr(request, "param", "chrome")


@pytest.fixture(scope="function")
def temp_download_dir(tmp_path, browser):
    """브라우저 인스턴스 전용 임시 다운로드 디렉터리.

    Firefox는 options.set_preference로 주입, Chromium 계열은 prefs dict로 주입합니다.
    driver fixture가 이 경로를 브라우저 설정에 사용하므로 driver보다 먼저 평가됩니다.
    """
    d = tmp_path / "downloads"
    d.mkdir()
    return d


# =========================================================
# [2] UI 자동화 관련 Fixture: WebDriver
# =========================================================
@pytest.fixture(scope="function")
def driver(browser, temp_download_dir):
    is_headless = bool(os.getenv("JENKINS_HOME") or os.getenv("CI"))
    download_str = str(temp_download_dir)

    chromium_prefs = {
        "download.default_directory": download_str,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
    }

    if browser == "chrome":
        options = ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        if is_headless:
            options.add_argument("--headless")
        options.add_experimental_option("prefs", chromium_prefs)
        d = webdriver.Chrome(options=options)

    elif browser == "edge":
        options = EdgeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        if is_headless:
            options.add_argument("--headless")
        options.add_experimental_option("prefs", chromium_prefs)
        d = webdriver.Edge(options=options)

    elif browser == "firefox":
        options = FirefoxOptions()
        options.add_argument("--width=1920")
        options.add_argument("--height=1080")
        if is_headless:
            options.add_argument("--headless")
        options.set_preference("browser.download.dir", download_str)
        options.set_preference("browser.download.folderList", 2)
        options.set_preference("browser.download.useDownloadDir", True)
        options.set_preference(
            "browser.helperApps.neverAsk.saveToDisk",
            "application/octet-stream,application/zip,text/plain",
        )
        options.set_preference("browser.download.manager.showWhenStarting", False)
        d = webdriver.Firefox(options=options)

    else:
        raise ValueError(f"지원하지 않는 브라우저입니다: {browser}")

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
def authenticated_driver(driver, base_url, test_user, browser):
    """UI 로그인이 완료된 상태의 WebDriver를 제공. 쿠키 캐싱으로 재로그인 최소화."""
    login_page = LoginPage(driver, base_url)
    chat_url = f"{base_url}/ai-helpy-chat"
    using_cache = False

    cached_cookies = _load_cached_cookies(browser)
    if cached_cookies:
        if browser == "firefox":
            # Firefox CDP 미지원 → 도메인 이동 후 Selenium add_cookie로 주입
            driver.get(base_url)
            for cookie in cached_cookies:
                try:
                    driver.add_cookie({
                        "name": cookie["name"],
                        "value": cookie["value"],
                        "domain": cookie.get("domain", "qaproject.elice.io").lstrip("."),
                        "path": cookie.get("path", "/"),
                        "secure": cookie.get("secure", False),
                        "httpOnly": cookie.get("httpOnly", False),
                    })
                except Exception:
                    pass
        else:
            # Chrome / Edge: CDP로 도메인 제약 없이 쿠키 직접 주입 (SSO 리다이렉트 문제 우회)
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
        logger.info(f"캐시된 쿠키로 로그인 세션 복원 완료 (browser={browser})")
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
        _save_cookies(driver.get_cookies(), browser)
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
        cache_path = _cookie_cache_path(browser)
        if cache_path.exists():
            cache_path.unlink()
            logger.info("만료된 쿠키 캐시 삭제 완료")
        pytest.fail("Fixture 사전 조건 설정 실패: 로그인 불가")
    return driver


# =========================================================
# [5-1] 새 대화가 시작된 ChatPage 제공 Fixture
# =========================================================
@pytest.fixture(scope="function")
def fresh_chat(authenticated_driver):
    """새 대화가 시작된 ChatPage 인스턴스를 반환합니다.

    대부분의 UI 테스트가 '빈 새 대화 화면'을 출발점으로 하므로,
    ChatPage 생성 + start_new_chat() 셋업을 fixture로 분리해
    테스트 본문이 TC 검증에만 집중하도록 합니다.

    드라이버가 필요하면 chat_page.driver 로 접근합니다.

    Usage:
        def test_something(self, fresh_chat):
            chat_page = fresh_chat
            inp = chat_page.chat_input
    """
    from pages.chat_page import ChatPage
    chat_page = ChatPage(authenticated_driver)
    chat_page.chat_input.start_new_chat()
    logger.info("fresh_chat: 새 대화 시작 완료")
    return chat_page


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

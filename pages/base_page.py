"""
모든 Page Object가 상속받는 최상위 부모 클래스.
공통 동작(클릭, 입력, 텍스트 추출 등)과 명시적 대기를 캡슐화합니다.
"""

import logging
import time

import allure
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    StaleElementReferenceException,
)
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config.config import DEFAULT_WAIT_TIME

logger = logging.getLogger(__name__)


class BasePage:
    """모든 페이지 객체의 부모 클래스"""

    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.wait = WebDriverWait(driver, DEFAULT_WAIT_TIME)

    @allure.step("클릭: {locator}")
    def click(self, locator: tuple[str, str]):
        """요소가 클릭 가능해질 때까지 대기 후 안정적으로 클릭합니다.
        React/MUI 환경의 intercept·stale element 문제를 방어합니다."""
        element = self.wait.until(EC.visibility_of_element_located(locator))
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)
        self.wait.until(EC.element_to_be_clickable(locator))
        # MUI 애니메이션(모달 열림·오버레이 전환 등)이 완전히 끝난 뒤 클릭하기 위한
        # 최소 안정화 대기. SPA 특유의 짧은 리렌더 사이클에서 intercept 오류를 줄인다.
        time.sleep(0.3)

        try:
            element.click()
        except (ElementClickInterceptedException, StaleElementReferenceException):
            logger.warning(f"일반 클릭 실패, JS click으로 재시도합니다. locator={locator}")
            element = self.wait.until(EC.presence_of_element_located(locator))
            self.driver.execute_script("arguments[0].click();", element)

    @allure.step("텍스트 입력: {locator} -> '{text}'")
    def enter_text(self, locator: tuple[str, str], text: str):
        """요소가 화면에 보일 때까지 대기 후 스크롤·초기화·입력합니다."""
        element = self.wait.until(EC.visibility_of_element_located(locator))
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)
        element.clear()
        element.send_keys(text)
        return element

    @allure.step("텍스트 추출: {locator}")
    def get_text(self, locator: tuple[str, str]) -> str:
        return self.wait_for_visible(locator).text

    @allure.step("요소 노출 대기: {locator}")
    def wait_for_visible(self, locator: tuple[str, str]):
        return self.wait.until(EC.visibility_of_element_located(locator))

    @allure.step("URL 변경 대기: '{text}' 포함 여부")
    def wait_for_url_contains(self, text: str):
        self.wait.until(EC.url_contains(text))

    @allure.step("요소 사라짐 대기: {locator} (최대 {timeout}초)")
    def wait_until_invisible(self, locator: tuple[str, str], timeout: int = DEFAULT_WAIT_TIME):
        WebDriverWait(self.driver, timeout).until(EC.invisibility_of_element_located(locator))

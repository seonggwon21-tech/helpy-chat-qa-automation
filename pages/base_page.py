"""
모든 Page Object가 상속받는 최상위 부모 클래스.
공통 동작(클릭, 입력, 텍스트 추출 등)과 명시적 대기를 캡슐화합니다.
"""

import allure
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from config.config import DEFAULT_WAIT_TIME


class BasePage:
    """모든 페이지 객체의 부모 클래스"""

    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.wait = WebDriverWait(driver, DEFAULT_WAIT_TIME)

    @allure.step("클릭: {locator}")
    def click(self, locator: tuple):
        """요소가 클릭 가능해질 때까지 대기 후 클릭합니다."""
        self.wait.until(EC.element_to_be_clickable(locator)).click()

    @allure.step("텍스트 입력: {locator} -> '{text}'")
    def enter_text(self, locator: tuple, text: str):
        """요소가 화면에 보일 때까지 대기 후 텍스트를 입력합니다."""
        element = self.wait_for_visible(locator)
        element.clear()
        element.send_keys(text)
        return element

    @allure.step("텍스트 추출: {locator}")
    def get_text(self, locator: tuple) -> str:
        """요소가 화면에 보일 때까지 대기 후 텍스트를 반환합니다."""
        return self.wait_for_visible(locator).text

    @allure.step("요소 노출 대기: {locator}")
    def wait_for_visible(self, locator: tuple):
        """요소가 화면에 렌더링되어 시각적으로 보일 때까지 대기하고 해당 요소를 반환합니다."""
        return self.wait.until(EC.visibility_of_element_located(locator))

    @allure.step("URL 변경 대기: '{text}' 포함 여부")
    def wait_for_url_contains(self, text: str):
        """현재 브라우저의 URL에 특정 텍스트가 포함될 때까지 대기합니다."""
        self.wait.until(EC.url_contains(text))

    @allure.step("요소 사라짐 대기: {locator} (최대 {timeout}초)")
    def wait_until_invisible(self, locator: tuple, timeout: int = DEFAULT_WAIT_TIME):
        """요소가 화면에서 완전히 사라질 때까지 지정된 시간만큼 대기합니다."""
        custom_wait = WebDriverWait(self.driver, timeout)
        custom_wait.until(EC.invisibility_of_element_located(locator))

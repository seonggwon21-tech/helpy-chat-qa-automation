"""
모든 Page Object가 상속받는 최상위 부모 클래스.
공통 동작(클릭, 입력 등)과 명시적 대기를 래핑합니다.
"""

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class BasePage:
    """모든 페이지 객체의 부모 클래스"""
    def __init__(self, driver):
        self.driver = driver
        # 명시적 대기(Explicit Wait) 10초 공통 설정
        self.wait = WebDriverWait(driver, 10)

    def click(self, locator):
        """요소가 클릭 가능해질 때까지 대기 후 클릭합니다."""
        self.wait.until(EC.element_to_be_clickable(locator)).click()

    def enter_text(self, locator, text):
        """요소가 화면에 보일 때까지 대기 후 텍스트를 입력합니다."""
        element = self.wait.until(EC.visibility_of_element_located(locator))
        element.clear()
        element.send_keys(text)
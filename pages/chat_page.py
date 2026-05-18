"""
헬피챗 메인 채팅 화면의 UI 요소와 액션을 정의한 Page Object Model 클래스.
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from .base_page import BasePage

class ChatPage(BasePage):
    """헬피챗 메시지 전송 및 응답 확인 클래스"""

    # 채팅 관련 Locators
    CHAT_INPUT = (By.CSS_SELECTOR, "textarea[name='input']") # 메시지 입력창
   # SVG 태그 특성을 고려한 XPATH 로케이터 적용
    SEND_BUTTON = (By.XPATH, "//button[.//*[local-name()='svg' and @data-testid='arrow-upIcon']]") # 전송 버튼
    NEW_CHAT_BUTTON = (By.XPATH, "//a[contains(@href, 'ai-helpy-chat') and .//span[text()='새 대화']]") # 새 대화 버튼

    # AI 응답 관련 Locators
    AI_MESSAGE_CONTENT = (By.CSS_SELECTOR, "div.elice-aichat__markdown[data-status='complete']") # AI의 답변 텍스트 박스
    CHAT_MESSAGE_ELEMENTS = (By.CSS_SELECTOR, "div.elice-aichat__markdown") # 대화 영역 메시지 요소

    def __init__(self, driver):
        super().__init__(driver)

    def send_message(self, message):
        """텍스트 영역에 메시지를 입력하고 전송 버튼을 클릭합니다."""
        self.enter_text(self.CHAT_INPUT, message)
        self.click(self.SEND_BUTTON)

    def wait_for_ai_response(self):
        """
        AI의 응답이 화면에 완전히 노출될 때까지 대기하고, 해당 텍스트를 반환합니다.
        스트리밍 생성이 완료된(data-status='complete') 메시지를 타겟팅합니다.
        """
        # 생성 완료(data-status='complete')된 메시지가 화면에 노출될 때까지 대기
        response_element = self.wait.until(EC.visibility_of_element_located(self.AI_MESSAGE_CONTENT))
        
        # 텍스트 반환
        return response_element.text
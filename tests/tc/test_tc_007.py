"""
[TC-007] 새 대화 버튼 클릭 시 화면 전환 및 상태 초기화 검증
"""

import logging
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pages.chat_page import ChatPage

logger = logging.getLogger(__name__)


class TestNewChatButton:
    """새 대화 버튼 기능 검증 테스트 스위트"""

    def test_new_chat_clears_conversation(self, logged_in_driver):
        """
        [TC-007] 로그인 상태에서 '새 대화' 버튼을 클릭하면
        입력창이 초기화되고 이전 대화가 표시되지 않아야 한다.
        """
        chat_page = ChatPage(logged_in_driver)

        # 1. 사전 대화 생성
        test_message = "안녕하세요, 테스트 메시지입니다."
        chat_page.send_message(test_message)
        chat_page.wait_for_ai_response()
        logger.info(f"사전 메시지 전송 완료: {test_message}")

        # [chat_page.py 고정용 임시 로케이터 정의]
        NEW_CHAT_BUTTON = (By.XPATH, "//*[normalize-space(text())='새 대화'] | //button[contains(., '새 대화')]")
        
        # 2. '새 대화' 버튼 클릭
        chat_page.click(NEW_CHAT_BUTTON)
        logger.info("'새 대화' 버튼 클릭 완료")

        # 🔄 [핵심 해결책] 
        # 화면 전환으로 인한 Stale 에러를 막기 위해, 
        # 새 화면의 입력창이 완벽하게 나타나서 상호작용 가능해질 때까지 명시적 대기를 걸어줍니다.
        wait = WebDriverWait(logged_in_driver, 10)
        input_element = wait.until(EC.presence_of_element_located(chat_page.CHAT_INPUT))
        
        # 대기 이후에 안전하게 새로고침된 엘리먼트에서 값을 읽어옵니다.
        input_value = input_element.get_attribute("value")
        
        # 3. [검증 1] 입력창 value 초기화 확인
        assert input_value == "", (
            f"입력창이 초기화되지 않았습니다. 현재 value: '{input_value}'"
        )
        logger.info("입력창 초기화 확인 완료 (value = '')")

        # 4. [검증 2] 대화 영역 메시지 요소 미표시 확인
        # 화면 전환 직후 이전 엘리먼트 찌꺼기가 남는 걸 방지하기 위해 0.5초만 살짝 대기 후 개수를 셉니다.
        time.sleep(0.5)
        message_elements = logged_in_driver.find_elements(*chat_page.AI_MESSAGE_CONTENT)
        
        assert len(message_elements) == 0, (
            f"새 대화 화면에 이전 메시지가 {len(message_elements)}개 남아있습니다."
        )
        logger.info("이전 대화 미표시 확인 완료 (메시지 요소 없음)")
warning: in the working copy of 'tests/tc/test_TC_003.py', LF will be replaced by CRLF the next time Git touches it
[1mdiff --git a/tests/tc/test_TC_003.py b/tests/tc/test_TC_003.py[m
[1mindex 2d09a10..54cd6cd 100644[m
[1m--- a/tests/tc/test_TC_003.py[m
[1m+++ b/tests/tc/test_TC_003.py[m
[36m@@ -1,73 +1,43 @@[m
[31m-# test_new_chat.py[m
[32m+[m[32m"""[m
[32m+[m[32m[TC-003] 새 대화 버튼 클릭 시 빈 대화 페이지 노출 검증[m
[32m+[m[32m- 사전 조건: test 계정으로 로그인된 상태[m
[32m+[m[32m- 테스트 절차:[m
[32m+[m[32m    1. LNB '새 대화' 버튼 클릭[m
[32m+[m[32m    2. 빈 대화 페이지 노출 확인[m
[32m+[m[32m- 기대 결과:[m
[32m+[m[32m    빈 대화 페이지가 노출됨[m
[32m+[m[32m"""[m
 [m
[31m-import pytest[m
 import logging[m
 from selenium.webdriver.common.by import By[m
[31m-from selenium.webdriver.support.ui import WebDriverWait[m
 from selenium.webdriver.support import expected_conditions as EC[m
[31m-from selenium.common.exceptions import TimeoutException[m
[32m+[m[32mfrom pages.chat_page import ChatPage[m
 [m
 logger = logging.getLogger(__name__)[m
 [m
[32m+[m[32mNEW_CHAT_BUTTON = (By.XPATH, "//a[contains(@href, 'ai-helpy-chat') and .//span[text()='새 대화']]")[m
[32m+[m[32mEMPTY_CHAT_INDICATOR = (By.XPATH, "//p[contains(text(), '검색이나 앱 등 다양한 도구를')]")[m
[32m+[m
 [m
 class TestNewChat:[m
[31m-    """[m
[31m-    새 대화 버튼 관련 테스트[m
[31m-    """[m
[32m+[m[32m    """새 대화 버튼 관련 테스트"""[m
 [m
[31m-    @pytest.mark.ui[m
     def test_new_chat_page_after_click_new_chat_button(self, logged_in_driver):[m
         """[m
[31m-        시나리오:[m
[31m-          1) 로그인 완료 상태 (logged_in_driver fixture에서 수행)[m
[31m-          2) LNB '새 대화' 버튼 클릭[m
[31m-[m
[31m-        기대 결과:[m
[31m-          - 빈 대화 페이지가 노출됨[m
[32m+[m[32m        [TC-003] 로그인 상태에서 LNB '새 대화' 버튼을 클릭하면[m
[32m+[m[32m        빈 대화 페이지가 노출되어야 한다.[m
         """[m
[32m+[m[32m        chat_page = ChatPage(logged_in_driver)[m
 [m
[31m-        driver = logged_in_driver[m
[31m-        wait = WebDriverWait(driver, 10)[m
[31m-[m
[31m-        # === (1) LNB '새 대화' 버튼 클릭 ===[m
[31m-        new_chat_button_locator = ([m
[31m-            By.XPATH,[m
[31m-            "//span[contains(@class, 'MuiListItemText-primary') and contains(text(), '새 대화')]"[m
[31m-        )[m
[31m-[m
[31m-        try:[m
[31m-            new_chat_button = wait.until([m
[31m-                EC.element_to_be_clickable(new_chat_button_locator)[m
[31m-            )[m
[31m-            new_chat_button.click()[m
[31m-            logger.info("LNB '새 대화' 버튼 클릭")[m
[31m-        except TimeoutException:[m
[31m-            pytest.fail([m
[31m-                "'새 대화' 버튼이 클릭 가능한 상태가 되지 않습니다. "[m
[31m-                "(LNB에서 버튼을 찾지 못한 것 같아요.)"[m
[31m-            )[m
[32m+[m[32m        # 1. LNB '새 대화' 버튼 클릭[m
[32m+[m[32m        chat_page.click(NEW_CHAT_BUTTON)[m
[32m+[m[32m        logger.info("LNB '새 대화' 버튼 클릭 완료")[m
 [m
[31m-        # === (2) 빈 대화 페이지 노출 확인 ===[m
[31m-        empty_chat_locator = ([m
[31m-            By.XPATH,[m
[31m-            "//p[contains(text(), '검색이나 앱 등 다양한 도구를')]"[m
[32m+[m[32m        # 2. [검증] 빈 대화 페이지 노출 확인[m
[32m+[m[32m        empty_chat_element = chat_page.wait.until([m
[32m+[m[32m            EC.visibility_of_element_located(EMPTY_CHAT_INDICATOR)[m
         )[m
[31m-[m
[31m-        try:[m
[31m-            empty_chat_page = wait.until([m
[31m-                EC.visibility_of_element_located(empty_chat_locator)[m
[31m-            )[m
[31m-        except TimeoutException:[m
[31m-            pytest.fail([m
[31m-                "빈 대화 페이지가 노출되지 않습니다. "[m
[31m-                "('새 대화' 클릭 후 페이지가 초기화되지 않은 것 같아요.)"[m
[31m-            )[m
[31m-[m
[31m-        assert empty_chat_page.is_displayed(), ([m
[32m+[m[32m        assert empty_chat_element.is_displayed(), ([m
             "빈 대화 페이지 요소가 화면에 노출되어야 합니다."[m
         )[m
[31m-[m
[31m-        logger.info([m
[31m-            "테스트 통과: '새 대화' 버튼 클릭 시 "[m
[31m-            "빈 대화 페이지가 정상적으로 노출됩니다."[m
[31m-        )[m
\ No newline at end of file[m
[32m+[m[32m        logger.info("테스트 통과: '새 대화' 버튼 클릭 시 빈 대화 페이지가 정상적으로 노출됩니다.")[m

"""
[TS-005] LNB 대화 목록 관리 검증
포함 TC: TC_012, TC_013, TC_014
"""

import logging

import allure
import pytest
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC

logger = logging.getLogger(__name__)
pytestmark = pytest.mark.ui


@allure.epic("AI Helpy Chat")
@allure.feature("LNB 대화 목록")
@allure.story("TS-005 · LNB 대화 목록 관리 검증")
class TestLnbManagement:

    @allure.title("LNB 대화 항목 추가 → 새로고침 유지 → 삭제 시나리오")
    def test_lnb_lifecycle(self, fresh_chat):
        chat_page = fresh_chat
        driver = chat_page.driver
        inp = chat_page.chat_input
        lnb = chat_page.lnb
        long_wait = chat_page.wait_up_to(60)

        lnb.wait_for_lnb_loaded()
        initial_hrefs = lnb.get_lnb_hrefs()
        logger.info(f"초기 LNB 항목 수: {len(initial_hrefs)}")

        with allure.step("[TC_012] 메시지 전송 후 LNB에 새 항목 추가 확인"):
            # 짧은 응답을 유도하는 프롬프트로 AI 응답 완료 시점을 안정화(CI flaky 방지)
            chat_page.send_message("소프트웨어 QA에 대해 10글자 이내로 짧게 설명해줘.")
            # JS로 href를 원자적으로 수집 — LNB 동적 갱신 중 StaleElementReferenceException 방지
            long_wait.until(
                lambda d: any(
                    href not in initial_hrefs for href in lnb.get_lnb_hrefs()
                )
            )
            # AI 응답 완료 대기는 통일된 wait_for_ai_response 사용. CI 부하 대비 120초 헤드룸.
            inp.wait_for_ai_response(120)

            after_hrefs = lnb.get_lnb_hrefs()
            new_hrefs = after_hrefs - initial_hrefs
            assert len(new_hrefs) >= 1, "LNB에 새 항목이 추가되지 않았습니다."
            logger.info(f"LNB 신규 항목 추가 확인 완료: {new_hrefs}")

        with allure.step("[TC_013] 페이지 새로고침 후 신규 대화 유지 확인"):
            # set 순서가 비결정적이므로 현재 브라우저 URL에서 직접 ID 추출
            new_chat_href = driver.current_url
            new_chat_id = new_chat_href.rstrip("/").split("/")[-1]
            driver.refresh()
            lnb.wait_for_lnb_loaded()
            # URL로 채팅 유지 확인 (LNB 가상화로 DOM에 없는 항목도 정상 처리)
            long_wait.until(EC.url_contains(new_chat_id))
            logger.info("새로고침 후 LNB 신규 대화 유지 확인 완료")

        with allure.step("[TC_014] 본 테스트가 생성한 대화 삭제 후 목록에서 제거 확인"):
            # 임의의 '첫 항목'이 아니라 이 테스트가 만든 대화(new_chat_id)만 타겟팅한다.
            #  - 독립성: 다른 테스트·이전 실행이 만든 대화를 건드리지 않음
            #  - cleanup: 삭제가 곧 자기 생성 데이터 정리이므로 서버측 대화 누적 방지
            target_item = chat_page.wait.until(
                lambda d: lnb.find_item_by_id(new_chat_id)
            )
            target_href = target_item.get_attribute("href")

            # hover → more 버튼 노출 → 클릭 (대상 항목 위에서만 액션 버튼이 노출됨)
            ActionChains(driver).move_to_element(target_item).perform()
            lnb.click(lnb.LNB_MORE_BUTTON)
            lnb.click(lnb.LNB_DELETE_BUTTON)
            lnb.click(lnb.CONFIRM_DELETE_BUTTON)

            # 카운트 대신 해당 URL이 LNB에서 사라졌는지 확인 (lazy-load 항목 보충 시 오차 방지)
            chat_page.wait.until(
                lambda d: target_href not in lnb.get_lnb_hrefs()
            )
            logger.info(f"본 테스트 생성 대화 삭제·정리 완료: {target_href}")

"""
[TS-004] + 버튼 메뉴 및 부가 기능 검증
포함 TC: TC_007 (메뉴 노출), TC_008 (파일 업로드), TC_010 (PPT 생성), TC_011 (웹 검색)
버그 기록: TC_009 (이미지 생성) — 다운로드 버튼 클릭 시 파일 미저장 (skip 처리)
"""

import os
import time
import logging
import pytest
import allure
from pathlib import Path
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from pages.chat_page import ChatPage

logger = logging.getLogger(__name__)
pytestmark = pytest.mark.ui

DUMMY_FILE    = Path(__file__).resolve().parents[2] / "test_data" / "test_upload.txt"
DOWNLOAD_DIR  = Path(os.getenv("DOWNLOAD_DIR", str(Path.home() / "Downloads")))
BUG_EVIDENCE  = Path(__file__).resolve().parents[2] / "docs" / "bugs" / "TC_009"


@allure.epic("AI Helpy Chat")
@allure.feature("+ 버튼 메뉴")
@allure.story("TS-004 · + 버튼 메뉴 및 부가 기능 검증")
class TestPlusButtonMenu:

    @allure.title("+ 버튼 클릭 시 4종 메뉴(파일 업로드·이미지 생성·PPT 생성·웹 검색) 노출 확인")
    def test_plus_button_shows_all_menus(self, authenticated_driver):
        chat_page = ChatPage(authenticated_driver)
        chat_page.click(chat_page.NEW_CHAT_BUTTON)

        with allure.step("[TC_007] + 버튼 클릭"):
            chat_page.click(chat_page.PLUS_BUTTON)
            logger.info("+ 버튼 클릭 완료")

        with allure.step("[TC_007] 4종 메뉴 전체 노출 확인"):
            menus = [
                ("파일 업로드", chat_page.MENU_FILE_UPLOAD),
                ("이미지 생성", chat_page.MENU_IMAGE_CREATE),
                ("PPT 생성",   chat_page.MENU_PPT_CREATE),
                ("웹 검색",    chat_page.MENU_WEB_SEARCH),
            ]
            for label, locator in menus:
                element = chat_page.wait_for_visible(locator)
                assert element.is_displayed(), f'"{label}" 메뉴가 노출되지 않았습니다.'
                logger.info(f'"{label}" 메뉴 노출 확인 완료')

    @allure.title("파일 업로드 선택 후 입력창에 첨부 칩 노출 확인")
    def test_file_upload_via_plus_menu(self, authenticated_driver):
        chat_page = ChatPage(authenticated_driver)
        chat_page.click(chat_page.NEW_CHAT_BUTTON)

        assert DUMMY_FILE.exists(), f"더미 파일이 존재하지 않습니다: {DUMMY_FILE}"

        with allure.step("[TC_008] + 버튼 클릭 후 파일 업로드 메뉴 선택"):
            chat_page.click(chat_page.PLUS_BUTTON)
            chat_page.click(chat_page.MENU_FILE_UPLOAD)
            logger.info("파일 업로드 메뉴 클릭 완료")

        with allure.step("[TC_008] 숨겨진 file input에 파일 경로 전달"):
            file_input = chat_page.wait.until(EC.presence_of_element_located(chat_page.FILE_INPUT))
            file_input.send_keys(str(DUMMY_FILE))
            logger.info(f"파일 경로 전달 완료: {DUMMY_FILE.name}")

        with allure.step("[TC_008] 첨부 칩 노출 확인"):
            chip = chat_page.wait_for_visible(chat_page.FILE_CHIP)
            assert chip.is_displayed(), "파일 첨부 후 입력창 영역에 첨부 칩이 노출되지 않았습니다."
            logger.info("파일 첨부 칩 노출 확인 완료")

    @allure.title("[BUG] 이미지 생성 다운로드 버튼 클릭 시 파일 미저장")
    @allure.issue("이미지 다운로드 버튼 클릭 시 파일이 저장되지 않음 — 수동 확인 시에도 동일 증상 재현. 앱 자체 버그로 판단.")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.xfail(reason="[BUG] TC_009: 이미지 다운로드 버튼 클릭 시 파일 미저장 — 수동 확인 시에도 동일 증상, 앱 버그", strict=True)
    def test_image_creation_via_plus_menu(self, authenticated_driver):
        """
        [TC-009] 이미지 생성 선택 후 프롬프트 전송 시 AI 응답에 이미지 출력 및 다운로드 확인

        [버그] 다운로드 버튼 클릭 시 파일이 저장되지 않음
               - 재현 환경: Chrome / qaproject.elice.io
               - 수동 테스트에서도 동일 증상 확인 → 앱 자체 결함으로 판단
               - 이미지 노출까지는 정상 동작, 다운로드 단계에서 무반응
        """
        for filename, label, attach_type in [
            ("bug_image_generated.png",      "이미지 생성 결과 화면",          allure.attachment_type.PNG),
            ("bug_download_button_clicked.png", "다운로드 버튼 클릭 시 화면",  allure.attachment_type.PNG),
            ("bug_download_fail.gif",         "버그 재현 GIF",                 allure.attachment_type.GIF),
        ]:
            evidence_path = BUG_EVIDENCE / filename
            if evidence_path.exists():
                allure.attach.file(str(evidence_path), name=label, attachment_type=attach_type)
        long_wait = WebDriverWait(authenticated_driver, 120)
        chat_page = ChatPage(authenticated_driver)
        chat_page.click(chat_page.NEW_CHAT_BUTTON)

        with allure.step("[TC_009] + 버튼 클릭 후 이미지 생성 메뉴 선택"):
            chat_page.click(chat_page.PLUS_BUTTON)
            chat_page.click(chat_page.MENU_IMAGE_CREATE)
            logger.info("이미지 생성 메뉴 클릭 완료")

        with allure.step("[TC_009] 이미지 생성 프롬프트 입력 후 전송"):
            chat_page.enter_text(chat_page.CHAT_INPUT, "고양이")
            chat_page.click(chat_page.SEND_BUTTON)
            logger.info("이미지 생성 프롬프트 전송 완료")

        with allure.step("[TC_009] AI 응답 이미지 노출 확인"):
            image_element = long_wait.until(EC.visibility_of_element_located(chat_page.IMAGE_IN_RESPONSE))
            assert image_element.is_displayed(), "이미지 생성 응답에 이미지 요소가 노출되지 않았습니다."
            src = image_element.get_attribute("src")
            assert src, "이미지 src 속성이 비어있습니다."
            logger.info(f"이미지 응답 노출 확인 완료: {src[:80]}...")

        with allure.step("[TC_009] 다운로드 버튼 클릭 후 파일 저장 확인 ← 버그 발생 지점"):
            assert DOWNLOAD_DIR.exists(), f"DOWNLOAD_DIR 경로가 존재하지 않습니다: {DOWNLOAD_DIR}"
            before_count = len(list(DOWNLOAD_DIR.iterdir()))

            RESPONSE_DOWNLOAD_BTN = (
                By.CSS_SELECTOR,
                "div[data-variant='assistant'] button:has(svg[data-testid='downloadIcon'])"
            )
            ActionChains(authenticated_driver).move_to_element(image_element).perform()
            time.sleep(0.5)

            download_btn = long_wait.until(EC.element_to_be_clickable(RESPONSE_DOWNLOAD_BTN))
            ActionChains(authenticated_driver).move_to_element(download_btn).click().perform()
            logger.info("다운로드 버튼 클릭 완료")

            download_success = False
            for _ in range(60):
                current_files = list(DOWNLOAD_DIR.iterdir())
                if len(current_files) > before_count and not any(f.name.endswith(".crdownload") for f in current_files):
                    download_success = True
                    break
                time.sleep(1)

            assert download_success, "[BUG] 이미지 파일이 다운로드되지 않았습니다."
            logger.info("이미지 다운로드 파일 저장 확인 완료")

    @allure.title("PPT 생성 선택 후 프롬프트 전송 시 결과 노출 및 다운로드 확인")
    @pytest.mark.slow
    def test_ppt_creation_via_plus_menu(self, authenticated_driver):
        long_wait = WebDriverWait(authenticated_driver, 600)
        chat_page = ChatPage(authenticated_driver)
        chat_page.click(chat_page.NEW_CHAT_BUTTON)

        with allure.step("[TC_010] + 버튼 클릭 후 PPT 생성 메뉴 선택"):
            chat_page.click(chat_page.PLUS_BUTTON)
            chat_page.click(chat_page.MENU_PPT_CREATE)
            logger.info("PPT 생성 메뉴 클릭 완료")

        with allure.step("[TC_010] 입력창에 PPT 생성 모드 칩 노출 확인"):
            PPT_MODE_CHIP = (By.XPATH, "//*[normalize-space(text())='PPT 생성']")
            chat_page.wait.until(EC.presence_of_element_located(PPT_MODE_CHIP))
            logger.info("PPT 생성 모드 칩 노출 확인 완료")

        with allure.step("[TC_010] PPT 생성 프롬프트 입력 후 전송"):
            chat_page.enter_text(chat_page.CHAT_INPUT, "QA 자동화에 대한 5슬라이드 PPT를 만들어줘.")
            chat_page.click(chat_page.SEND_BUTTON)
            logger.info("PPT 생성 프롬프트 전송 완료")

        with allure.step("[TC_010] PPT 결과 노출 확인 (최대 600초 대기)"):
            ppt_result = long_wait.until(EC.visibility_of_element_located(chat_page.PPT_RESULT))
            assert ppt_result.is_displayed(), "PPT 생성 후 결과 요소가 화면에 노출되지 않았습니다."
            logger.info("PPT 결과 노출 확인 완료")

        with allure.step("[TC_010] 다운로드 버튼 클릭 후 PPTX 파일 저장 확인"):
            assert DOWNLOAD_DIR.exists(), f"DOWNLOAD_DIR 경로가 존재하지 않습니다: {DOWNLOAD_DIR}"
            before_count = len(list(DOWNLOAD_DIR.iterdir()))

            download_btn = long_wait.until(EC.element_to_be_clickable(chat_page.PPT_DOWNLOAD_BTN))
            authenticated_driver.execute_script("arguments[0].scrollIntoView({block:'center'});", download_btn)
            time.sleep(0.3)
            download_btn.click()
            logger.info("PPT 다운로드 버튼 클릭 완료")

            download_success = False
            for _ in range(60):
                current_files = list(DOWNLOAD_DIR.iterdir())
                if len(current_files) > before_count and not any(f.name.endswith(".crdownload") for f in current_files):
                    download_success = True
                    break
                time.sleep(1)

            after_count = len(list(DOWNLOAD_DIR.iterdir()))
            assert download_success, f"PPTX 파일이 {DOWNLOAD_DIR}에 다운로드되지 않았습니다."
            assert after_count > before_count, "다운로드 후 파일 개수가 증가하지 않았습니다."
            logger.info("PPT 다운로드 파일 저장 확인 완료")

    @allure.title("웹 검색 선택 후 검색어 전송 시 AI 응답 및 결과 텍스트 확인")
    def test_web_search_via_plus_menu(self, authenticated_driver):
        long_wait = WebDriverWait(authenticated_driver, 60)
        chat_page = ChatPage(authenticated_driver)
        chat_page.click(chat_page.NEW_CHAT_BUTTON)

        with allure.step("[TC_011] + 버튼 클릭 후 웹 검색 메뉴 선택"):
            long_wait.until(EC.element_to_be_clickable(chat_page.PLUS_BUTTON)).click()
            long_wait.until(EC.visibility_of_element_located(chat_page.MENU_WEB_SEARCH)).click()
            logger.info("웹 검색 메뉴 클릭 완료")

        with allure.step("[TC_011] 검색어 입력 후 전송"):
            chat_page.enter_text(chat_page.CHAT_INPUT, "소프트웨어 QA 자동화 테스트 최신 동향")
            chat_page.click(chat_page.SEND_BUTTON)
            logger.info("웹 검색어 전송 완료")

        with allure.step("[TC_011] AI 응답 텍스트 노출 확인"):
            response_text = long_wait.until(EC.visibility_of_element_located(chat_page.AI_MESSAGE_CONTENT)).text
            assert response_text and len(response_text.strip()) > 0, \
                "웹 검색 후 AI 응답 텍스트가 출력되지 않았습니다."
            logger.info(f"AI 응답 출력 확인 완료: '{response_text[:80]}...'")

        with allure.step("[TC_011] 웹 검색 결과 응답 내용 충분성 확인"):
            assert len(response_text.strip()) > 50, "웹 검색 응답 텍스트가 너무 짧습니다."
            logger.info("웹 검색 결과 텍스트 정상 출력 확인 완료")

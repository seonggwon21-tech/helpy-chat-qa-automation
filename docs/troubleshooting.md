# Troubleshooting

> 작성일: 2026-05-20  
> 브랜치: `feature/test-refactor`

---

## 1. API 인증 실패 — `/login/otp` 422 오류

**현상**  
`conftest.py`에서 ID/PW로 직접 로그인 API를 호출하면 `422 Unprocessable Entity` 반환.

**원인**  
API 스펙 변경으로 `/login/otp` 엔드포인트에 `otp` 필드가 필수가 됨.

**해결**  
동적 로그인 API 호출 방식을 제거하고, `.env`에 `AUTH_TOKEN`을 직접 등록하여 픽스처에서 로드하는 방식으로 전환.  
`Bearer ` 접두사가 중복으로 붙는 문제는 `token.removeprefix("Bearer ").strip()`으로 처리.

```python
# conftest.py
token = os.getenv("AUTH_TOKEN")
return token.removeprefix("Bearer ").strip()
```

---

## 2. API 테스트 — POST /chatroom 409·422 오류

**현상**  
`POST /chatroom` 호출 시 `409 Conflict` 또는 `422 Unprocessable Entity` 반환.

**원인**  
- 422: 요청 body에 `name`, `agent_id`, `model_id` 필수 필드 누락  
- 409: 세션 컨텍스트 불일치 (토큰과 org 정보가 맞지 않음)

**해결**  
CRUD 기반 테스트를 폐기하고, 인증만 있으면 되는 GET 계열 API로 테스트 재설계.  
`GET /agent` (목록) → `GET /agent/count` (수) → `GET /agent/{id}` (상세) 시나리오로 대체.

---

## 3. UI 로그인 셀렉터 불일치

**현상**  
`authenticated_driver` 픽스처에서 로그인 시도 후 `is_login_successful()` → `False` 반환.

**원인**  
`qaproject.elice.io`에 접속하면 Elice SSO(`accounts.elice.io`)로 리다이렉트되는데,  
로그인 폼 셀렉터가 `input[name='loginId']`로 되어 있었으나 실제 필드 타입은 `type="email"`.

**확인 방법**  
로그인 실패 시 스크린샷을 자동 저장하도록 픽스처를 수정하여 브라우저 상태를 확인.

```
로그인 실패 시점 URL: https://accounts.elice.io/accounts/signin/me?...
```

**해결**  
타입 기반 셀렉터로 변경 (name 속성과 무관하게 동작).

```python
LOGIN_ID_INPUT = (By.CSS_SELECTOR, "input[type='email']")
PASSWORD_INPUT = (By.CSS_SELECTOR, "input[type='password']")
```

---

## 4. is_login_successful — PersonIcon 대소문자 불일치

**현상**  
로그인 후 URL은 `ai-helpy-chat`을 포함하지만 `is_login_successful()` → `False`.

**원인**  
`data-testid` 값이 `personIcon`(소문자)이 아니라 `PersonIcon`(대문자)이었음.  
CSS 속성값은 대소문자를 구분하므로 셀렉터가 매칭되지 않음.

**해결**

```python
# 수정 전
(By.CSS_SELECTOR, "svg[data-testid='personIcon']")

# 수정 후
(By.CSS_SELECTOR, "button > svg[data-testid='PersonIcon']")
```

---

## 5. 쿠키 캐싱 — SSO 도메인 불일치로 복원 실패

**현상**  
신규 로그인으로 쿠키를 저장했음에도 다음 테스트에서 캐시된 쿠키 복원 실패.  
실패 시점 URL이 매번 `accounts.elice.io`로 리다이렉트됨.

**원인**  
쿠키 복원 흐름:  
1. `driver.get(base_url)` → SSO가 `accounts.elice.io`로 즉시 리다이렉트  
2. `add_cookie()` 호출 시 현재 도메인(`accounts.elice.io`)과 저장된 쿠키 도메인(`qaproject.elice.io`) 불일치  
3. Selenium이 예외를 발생시키지 않고 쿠키 추가를 무시 (try/except로 묻힘)  
4. 쿠키 없이 chat_url 접근 → 다시 로그인 페이지로 리다이렉트

**해결**  
CDP(Chrome DevTools Protocol) `Network.setCookie` 명령으로 도메인 제약 없이 쿠키를 직접 주입.

```python
driver.execute_cdp_cmd("Network.enable", {})
for cookie in cached_cookies:
    driver.execute_cdp_cmd("Network.setCookie", {
        "name": cookie["name"],
        "value": cookie["value"],
        "domain": cookie.get("domain", "qaproject.elice.io"),
        "path": cookie.get("path", "/"),
        "secure": cookie.get("secure", False),
        "httpOnly": cookie.get("httpOnly", False),
    })
driver.get(chat_url)
```

---

## 6. 쿠키 저장 타이밍 — SSO 리다이렉트 완료 전 저장

**현상**  
신규 로그인 후 저장된 쿠키가 유효하지 않은 세션 상태를 담고 있음.

**원인**  
`login_page.login()` 클릭 직후 쿠키를 저장했는데, 당시 브라우저가 아직 `accounts.elice.io`에 머물러 있었음.  
`qaproject.elice.io`로 돌아오는 SSO 콜백이 완료되기 전에 저장된 것.

**해결**  
`qaproject.elice.io`가 URL에 포함될 때까지 명시적으로 대기한 뒤 쿠키 저장.

```python
WebDriverWait(driver, 30).until(EC.url_contains("qaproject.elice.io"))
_save_cookies(driver.get_cookies())
```

---

## 7. Fixture setup 실패 시 스크린샷 미저장

**현상**  
`authenticated_driver` 픽스처가 실패해도 `reports/screenshots/`에 스크린샷이 생기지 않음.

**원인**  
`pytest_runtest_makereport` 훅에서 `report.when == "call"`만 체크 → setup 단계 실패는 무시됨.  
또한 픽스처 실패 시 `item.funcargs.get("driver")`가 `None`을 반환함.

**해결**  
- 훅 조건을 `"call", "setup"` 모두 포함하도록 수정
- 픽스처 내부에서 직접 스크린샷 저장 + 실패 시점 URL 로깅 추가

```python
if not login_page.is_login_successful():
    driver.save_screenshot("reports/screenshots/fixture_login_failed.png")
    logger.error(f"로그인 실패 시점 URL: {driver.current_url}")
    if _COOKIE_CACHE_PATH.exists():
        _COOKIE_CACHE_PATH.unlink()  # 만료 캐시 자동 삭제
    pytest.fail("Fixture 사전 조건 설정 실패: 로그인 불가")
```

---

## 8. enter_text 반환값 누락 — NoneType AttributeError

**현상**  
`test_input_features.py`에서 `AttributeError: 'NoneType' object has no attribute 'send_keys'`.

**원인**  
`BasePage.enter_text()` 리팩터링 과정에서 `return element`가 누락됨.  
테스트에서 반환된 element에 `send_keys(Keys.SHIFT, Keys.ENTER)`를 호출하려 하여 에러 발생.

**해결**

```python
def enter_text(self, locator: tuple, text: str):
    element = self.wait_for_visible(locator)
    element.clear()
    element.send_keys(text)
    return element  # 누락되었던 반환값 복원
```

---

## 9. LNB 삭제 검증 — 카운트 기반 실패

**현상**  
대화 삭제 후 LNB 항목 수가 줄지 않아 `TimeoutException` 발생.

**원인**  
LNB가 lazy-load 방식으로 아래 항목을 자동 보충하여 삭제해도 총 카운트가 동일하게 유지됨.

**해결**  
카운트 비교 → 삭제 대상 URL이 LNB에서 사라졌는지 확인하는 방식으로 변경.

```python
target_href = current_items[0].get_attribute("href")
chat_page.wait.until(
    lambda d: not any(
        el.get_attribute("href") == target_href
        for el in d.find_elements(*chat_page.LNB_CHAT_ITEMS)
    )
)
```

---

## 10. AI 응답 대기 타임아웃

**현상**  
`test_lnb_management`에서 AI 응답 대기 중 `TimeoutException`.

**원인**  
`wait_for_ai_response()`의 기본 대기가 10초인데, 해당 테스트의 메시지에 대한 AI 응답이 10초를 초과함.

**해결**  
테스트 내 `long_wait`(60초)을 직접 사용하도록 변경.

```python
long_wait.until(EC.visibility_of_element_located(chat_page.AI_MESSAGE_CONTENT))
```

---

## 11. LNB 초기 스냅샷 — 페이지 로드 전 캡처로 항목 0개

**현상**  
`test_lnb_management`에서 `초기 LNB 항목 수: 0` 로그 출력 후, 메시지 전송 뒤 신규 항목이 1개가 아닌 15개로 잡혀 AssertionError 발생.

**원인**  
`authenticated_driver` 픽스처가 페이지 이동 후 즉시 반환되는데, LNB 항목이 비동기로 로드되어 아직 렌더링되지 않은 상태에서 `initial_hrefs`를 캡처함.  
이후 메시지 전송 시 LNB가 뒤늦게 전체 로드되어 기존 항목 15개가 모두 "신규"로 인식됨.

**해결**  
초기 스냅샷 전에 LNB 항목이 1개 이상 로드될 때까지 명시적으로 대기.

```python
try:
    long_wait.until(lambda d: len(d.find_elements(*chat_page.LNB_CHAT_ITEMS)) > 0)
except Exception:
    pass  # LNB가 진짜 비어있는 경우 허용
```

---

## 12. StaleElementReferenceException — 새로고침 후 DOM 교체 중 요소 참조

**현상**  
TC_013(새로고침 후 LNB 목록 유지 확인)에서 `driver.refresh()` 이후 LNB 항목의 `get_attribute("href")` 호출 시 `StaleElementReferenceException` 발생.

**원인**  
`presence_of_element_located`로 첫 번째 요소 등장을 확인한 직후 `find_elements`로 전체 요소를 수집했으나,  
페이지가 아직 렌더링 중이어서 수집된 요소들이 DOM에서 교체되어 stale 상태가 됨.

**해결**  
요소 참조 대신 JavaScript로 href를 한 번에 수집하여 DOM 교체 타이밍 문제 우회.  
또한 `long_wait`으로 새로고침 전 항목 수만큼 로드될 때까지 대기 후 수집.

```python
after_refresh_hrefs = set(authenticated_driver.execute_script(
    "return Array.from(document.querySelectorAll('a[href*=\"/ai-helpy-chat/chats/\"]')).map(e => e.href)"
))
```

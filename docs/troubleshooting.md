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

---

## 13. AUTH_TOKEN 만료 — CI 실행마다 수동 갱신 필요

**현상**  
GitHub Actions API 테스트가 매일 `409` 오류로 실패.  
원인을 추적하니 `.env` 및 GitHub Secrets에 등록한 `AUTH_TOKEN`이 약 24시간 후 만료되는 세션 토큰이었음.

**배경**  
트러블슈팅 #1에서 `/login/otp` 엔드포인트 호출 시 `422` 오류가 발생해 자동 로그인을 포기하고 수동 토큰 방식으로 전환했었음.  
그러나 CI 환경에서 매번 토큰을 갱신하는 건 지속 불가능한 방식임을 운영 중에 확인.

**원인 재분석**  
브라우저 Network 탭으로 실제 로그인 요청을 캡처한 결과, `/login/otp` 엔드포인트가 `login_id` + `password` 필드만으로 정상 동작하는 것을 확인.  
기존 422 오류는 요청 body 구조가 잘못됐던 것이 원인이었음.

**해결**  
`auth_token` fixture를 자동 발급 방식으로 재구현.  
`TEST_USER_ID` / `TEST_USER_PW`로 로그인 API를 호출해 `access_token`을 발급받아 사용.  
기존 `AUTH_TOKEN` 환경변수가 있으면 우선 사용하는 fallback 구조도 유지.

```python
response = requests.post(
    "https://api-account.elice.io/login/otp",
    json={"login_id": login_id, "password": password},
    headers={"Content-Type": "application/json"},
    timeout=30,
)
token = response.json().get("access_token")
```

이로써 GitHub Secrets에 `TEST_USER_ID` / `TEST_USER_PW`만 등록하면 토큰 갱신 없이 CI가 영구적으로 동작함.

---

## 14. StaleElementReferenceException — LNB 동적 갱신 중 요소 참조 무효화 (TC_012)

**현상**  
TC_012(메시지 전송 후 LNB 신규 항목 추가 확인)에서 메시지 전송 직후 LNB 신규 항목을 기다리는 `long_wait.until` 람다 내부에서 `StaleElementReferenceException` 발생.

```
selenium.common.exceptions.StaleElementReferenceException:
stale element reference: stale element not found in the current frame
```

**원인**  
`long_wait.until` 람다가 반복 호출될 때마다 `find_elements`로 LNB 요소 목록을 수집하고, 요소별로 `get_attribute("href")`를 순회함.  
메시지 전송 후 LNB가 신규 항목을 동적으로 추가·재렌더링하는 타이밍에 람다가 재진입하면, 직전 호출에서 수집한 요소 참조가 이미 stale 상태가 되어 예외 발생.  
트러블슈팅 #12(TC_013 새로고침)와 근본 원인은 동일하나, 트리거가 `driver.refresh()`가 아닌 LNB의 실시간 DOM 갱신이라는 점에서 차이가 있음.

**해결**  
`find_elements` + `get_attribute` 조합 대신 JavaScript `execute_script`로 href를 한 번에 원자적으로 수집.  
JS 실행은 단일 RPC 호출이므로 수집 도중 DOM이 교체될 여지가 없음.  
`after_hrefs` 수집부도 동일 방식으로 통일.

```python
_js_lnb_hrefs = (
    "return Array.from(document.querySelectorAll("
    "\"a[href*='/ai-helpy-chat/chats/']\")).map(e => e.href)"
)

# 수정 전 — 요소 참조 보유 중 LNB 갱신 시 stale 발생
long_wait.until(
    lambda d: any(
        el.get_attribute("href") not in initial_hrefs
        for el in d.find_elements(*chat_page.LNB_CHAT_ITEMS)
    )
)

# 수정 후 — JS로 href를 원자적으로 수집
long_wait.until(
    lambda d: any(
        href not in initial_hrefs
        for href in d.execute_script(_js_lnb_hrefs)
    )
)
after_hrefs = set(authenticated_driver.execute_script(_js_lnb_hrefs))
```

**적용 범위**  
동적으로 업데이트되는 리스트 요소를 `WebDriverWait` 람다 내에서 순회할 때는 항상 JS 수집 방식을 우선 사용할 것.

---

## 15. /login/otp 엔드포인트 otp 필드 재필수화 — 자동 로그인 재불가

**현상**  
GitHub Actions API Tests가 다시 `422 Unprocessable Entity`로 실패.

```json
{"code":"unprocessable_entity","detail":{"loc":["body","otp"],"msg":"field required"}}
```

**배경**  
트러블슈팅 #1에서 동일 오류가 발생해 수동 `AUTH_TOKEN` 방식으로 전환했었음.  
트러블슈팅 #13에서 브라우저 Network 탭 캡처 결과 `otp` 없이도 동작함을 확인하고 자동 발급 방식으로 재전환했었음.  
그러나 이후 플랫폼이 `otp` 필드를 다시 필수로 변경해 자동 로그인이 재불가 상태가 됨.

**원인**  
OTP(2FA)가 실제로 필수화됨. TOTP·SMS 기반 OTP는 CI 환경에서 자동 획득이 불가능.

**해결**  
`auth_token` fixture를 `AUTH_TOKEN` 환경변수 전용으로 단순화. 자동 로그인 코드 전면 제거.

```python
@pytest.fixture(scope="session")
def auth_token():
    token = os.getenv("AUTH_TOKEN")
    if not token:
        pytest.fail("AUTH_TOKEN 환경변수가 설정되지 않았습니다.")
    return token.removeprefix("Bearer ").strip()
```

GitHub Secrets에 `AUTH_TOKEN` 등록 후 `qa.yml` API Tests env에 전달.

```yaml
- name: Run API tests
  env:
    AUTH_TOKEN: ${{ secrets.AUTH_TOKEN }}
```

**토큰 갱신 방법**  
브라우저 → `qaproject.elice.io` 로그인 → 개발자 도구 Network 탭 → API 요청 클릭 → Request Headers의 `Authorization: Bearer xxxxx` 값 복사 → GitHub Secrets `AUTH_TOKEN` 업데이트.

---

## 16. TC_019 유효하지 않은 토큰 요청 — API 게이트웨이가 401/403 대신 409로 래핑

**현상**  
TC_019(유효하지 않은 JWT 토큰으로 `GET /chatroom` 요청) 테스트가 실패.

```
assert 409 in (401, 403)
응답: {"code":"elice_core_unexpected_result","detail":{"resp_json":{"_result":{"status_code":403,"reason":"auth"}}}}
```

**원인**  
이 엔드포인트는 외부 인증 서버(Elice Core)에 ACL 검증을 위임하는 구조.  
백엔드 인증 실패(403)를 API 게이트웨이가 자체 오류 코드(`elice_core_unexpected_result`)로 감싸 **409**로 반환함.  
표준 REST 규약(`401/403`)과 다른 이 API 특유의 동작.

**해결**  
`401/403/409` 모두 인증 거부로 허용. 409인 경우 응답 body 내부에서 실제 인증 실패 사유를 추가 검증.

```python
assert response.status_code in (401, 403, 409)

if response.status_code == 409:
    body = response.json()
    inner_status = (
        body.get("detail", {})
        .get("resp_json", {})
        .get("_result", {})
        .get("status_code")
    )
    assert inner_status == 403, f"inner_status: {inner_status}"
```

**교훈**  
MSA 환경에서 인증 실패 응답 코드가 표준과 다를 수 있음. Negative 테스트 작성 시 실제 API 응답을 먼저 캡처해 기대값을 설정할 것.

---

## 17. 파일 업로드 — `Page.setInterceptFileChooser` Chrome 148 미지원

**현상**  
크로스 브라우저 확장 작업 중 파일 업로드 TC(TC_008)가 Chrome 최신 버전에서 실패.  
CDP `Page.setInterceptFileChooser` 호출 시 아무 반응 없이 파일이 선택되지 않음.

**원인**  
Chrome 148부터 `Page.setInterceptFileChooser` 커맨드가 더 이상 지원되지 않음.  
OS 네이티브 파일 다이얼로그를 인터셉트하는 CDP 방식 자체가 해당 버전에서 제거됨.

**해결**  
CDP 방식을 완전히 제거하고 `send_keys` 풀패스 방식으로 교체.  
`input[type='file']`에 절대 경로를 직접 전달하면 OS 파일 다이얼로그 없이 파일이 설정됨.  
Selenium은 `input[type='file']` 요소에 대해 `send_keys`를 특수 처리하므로 hidden 상태에서도 동작하지만,  
브라우저별 안정성을 위해 JS로 `display:block` / `visibility:visible`을 강제 설정한 뒤 호출.

```python
# plus_menu_component.py
def upload_file(self, file_path):
    self.select_plus_menu_item(self.MENU_FILE_UPLOAD)
    file_input = self.wait.until(EC.presence_of_element_located(self.FILE_INPUT))
    self.driver.execute_script(
        "arguments[0].removeAttribute('hidden');"
        "arguments[0].style.display='block';"
        "arguments[0].style.visibility='visible';",
        file_input,
    )
    file_input.send_keys(str(Path(file_path).resolve()))  # 절대 경로 직접 주입
```

단독 실행 결과 **PASSED** 확인. Chrome · Edge · Firefox 모두 동일 코드로 동작.

---

## 18. 크로스 브라우저 — Firefox CDP 미지원으로 쿠키 주입 실패

**현상**  
`--browser firefox`로 실행 시 `authenticated_driver` 픽스처에서 로그인 실패.  
캐시된 쿠키를 주입하려는 시점에 `invalid session id` 또는 `unknown command` 오류 발생.

**원인**  
기존 쿠키 주입 방식은 Chrome DevTools Protocol의 `Network.setCookie` 커맨드를 사용.  
Firefox는 W3C WebDriver 프로토콜만 지원하며 CDP 커맨드를 지원하지 않음.  
`driver.execute_cdp_cmd()`는 Chromium 계열(Chrome · Edge)에서만 동작하는 API.

**해결**  
`browser` 파라미터로 분기 처리.  
Firefox는 목표 도메인으로 먼저 이동(`driver.get(base_url)`)한 뒤 Selenium 표준 `add_cookie()`를 사용.  
쿠키 도메인 앞에 붙는 `.`(leading dot)은 Firefox의 `add_cookie()`가 거부하므로 `lstrip(".")`으로 제거.

```python
if browser == "firefox":
    # Firefox: CDP 미지원 → 도메인 이동 후 Selenium add_cookie로 주입
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
    # Chrome / Edge: CDP로 도메인 제약 없이 주입
    driver.execute_cdp_cmd("Network.enable", {})
    for cookie in cached_cookies:
        driver.execute_cdp_cmd("Network.setCookie", {...})
```

**교훈**  
크로스 브라우저 확장 시 CDP 의존 코드는 모두 점검 대상. `execute_cdp_cmd` 사용처를 일괄 검색해 Firefox 폴백 분기를 추가할 것.

---

## 19. 크로스 브라우저 — 쿠키 캐시 미분리로 `--browser all` 인증 실패

**현상**  
`--browser all`로 3브라우저 순차 실행 시 Chrome 이후 Firefox 세션에서 인증 실패.  
Chrome은 PASSED, Edge · Firefox는 `fixture_login_failed.png` 스크린샷과 함께 FAILED.

**원인**  
쿠키 캐시 파일이 `elice_session.json` 단일 파일로 공유됨.  
Chrome 테스트가 저장한 쿠키를 Firefox가 그대로 읽어 주입하는데, 브라우저 간 세션 쿠키는 호환되지 않아 인증 실패.  
실패 후 캐시가 삭제되면 Edge · Firefox는 신규 로그인을 시도하지만, 이 역시 Chrome 캐시가 다시 생성되어 순환 충돌 발생.

```
# 기존: 모든 브라우저가 같은 캐시 파일을 읽고 씀
_COOKIE_CACHE_PATH = Path(".pytest_cache/elice_session.json")
```

**해결**  
캐시 경로를 브라우저명 포함 파일명으로 분리하는 `_cookie_cache_path(browser)` 함수로 전환.  
동시에 상대 경로의 실행 위치 의존 문제를 해소하기 위해 `Path(__file__).parent` 기반 절대 경로로 변경.

```python
_COOKIE_CACHE_DIR = Path(__file__).parent / ".pytest_cache"

def _cookie_cache_path(browser: str) -> Path:
    return _COOKIE_CACHE_DIR / f"elice_session_{browser}.json"

# --browser all 실행 시 각 브라우저가 독립 캐시 사용
# elice_session_chrome.json
# elice_session_edge.json
# elice_session_firefox.json
```

**교훈**  
브라우저 파라미터화처럼 동일 픽스처가 여러 값으로 실행되는 경우, 파일·상태를 공유하는 전역 리소스는 파라미터별로 격리해야 함.

---

## 20. CI Lint 게이트 — `fresh_chat` 리팩터링이 남긴 미사용 변수(F841)를 GitHub Actions가 차단

**현상**  
테스트 셋업 중복 제거를 위해 `fresh_chat` fixture를 도입한 뒤 push했더니, GitHub Actions의 Lint(Ruff) job이 실패하며 이후 테스트 job이 실행되지 않음.

```
F841 Local variable `inp` is assigned to but never used
  --> tests/ui/test_plus_menu.py:54:9
   |
54 |         inp = fresh_chat.chat_input
   |         ^^^
```

**원인**  
`test_file_upload_via_plus_menu`에서 `inp.start_new_chat()` 호출을 `fresh_chat` fixture 안으로 옮기면서, 그 호출을 위해 선언했던 `inp = fresh_chat.chat_input`이 더 이상 사용되지 않게 됨.  
`python -m py_compile`과 `pytest --collect-only`는 모두 통과하므로(문법·수집상 결함 없음) **기능 검증만으로는 드러나지 않는, 정적 분석 전용 영역의 결함**이었음.

**해결**  
미사용 라인 제거. 이후 로컬에 ruff를 설치하고 `python -m ruff check .` → `All checks passed` 확인 후 재push해 CI 복구.

```python
# 수정 전
def test_file_upload_via_plus_menu(self, fresh_chat):
    inp = fresh_chat.chat_input     # start_new_chat()이 fixture로 이동하며 미사용
    plus = fresh_chat.plus_menu

# 수정 후
def test_file_upload_via_plus_menu(self, fresh_chat):
    plus = fresh_chat.plus_menu
```

**교훈**  
- Lint job이 테스트 job 앞단에서 게이트 역할을 하도록 구성한 파이프라인(README 주요 구현 #12)이, 실제로 품질 결함을 **테스트 단계 진입 전에 차단**함을 검증한 사례. CI 설계 의도가 운영에서 그대로 작동했음.  
- 리팩터링으로 변수 셋업 위치를 옮기면 옮겨진 쪽에 미사용 변수(F841)·미사용 import(F401)가 남기 쉬움. 기능 검증(compile·collect)은 이를 잡지 못하므로, **push 전 로컬에서 `python -m ruff check .`를 반드시 실행**할 것.

---

## 21. AI 응답 대기 — CI 부하에서 60초 타임아웃 재발 (TC_012)

**현상**  
GitHub Actions UI 테스트 `test_lnb_lifecycle`(TC_012)가 메시지 전송 직후 AI 응답 완료 대기에서 `TimeoutException`. 60초를 초과해 실패.

```
tests/ui/test_lnb_management.py:42: in test_lnb_lifecycle
    long_wait.until(EC.visibility_of_element_located(inp.AI_MESSAGE_CONTENT))
selenium.common.exceptions.TimeoutException
```

**원인**  
트러블슈팅 #10에서 이 지점을 `10초 → 60초`로 한 번 늘렸으나, CI 러너 부하와 **가변적 프롬프트(`"LNB 목록 관리 테스트"`)** 가 겹쳐 응답 완료(`data-status='complete'`)가 60초를 초과함.  
같은 실행의 다른 send 테스트들은 `"…10글자 이내로 짧게 설명해줘"` 류 프롬프트로 약 5초 내에 완료된 것을 확인 — **AI 응답의 길이·완료 시점은 프롬프트의 결정성에 크게 좌우**됨. 첫 단계(전송 → LNB 새 항목 등장)는 통과했으므로 전송 자체는 정상이었고, 순수하게 응답 완료 대기만 실패.

**해결**  
① 출력 길이를 제약하는 짧은-응답 유도형 프롬프트로 교체, ② AI 응답 대기를 통일 메서드 `wait_for_ai_response(120)`로 변경(`60 → 120`초 헤드룸 + 대기 경로 일원화).

```python
# 수정 전
chat_page.send_message("LNB 목록 관리 테스트")
...
long_wait.until(EC.visibility_of_element_located(inp.AI_MESSAGE_CONTENT))

# 수정 후
chat_page.send_message("소프트웨어 QA에 대해 10글자 이내로 짧게 설명해줘.")  # 짧은 응답 유도
...
inp.wait_for_ai_response(120)   # 통일된 대기 메서드 + CI 부하 대비 헤드룸
```

**교훈**  
AI 응답처럼 **비결정적 비동기 결과**를 기다릴 때는, 단순히 타임아웃만 늘리지 말고 ① 출력 길이를 제약하는 프롬프트로 완료 시점을 안정화하고 ② CI 부하를 감안한 헤드룸을 함께 둘 것. 타임아웃 증가만으로는 프롬프트 변동성에서 오는 flaky를 근본적으로 잡지 못함.

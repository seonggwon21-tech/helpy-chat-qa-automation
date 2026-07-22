# 주요 구현 내용

> 설계 결정과 트러블슈팅 13건을 정리했습니다. 관심 항목을 먼저 훑어보세요.
> README로 돌아가기 → [../README.md](../README.md)

| # | 구현 항목 | 한 줄 요약 |
|---|---|---|
| 1 | Component Object Pattern | ChatPage를 ChatInput·PlusMenu·Lnb 3컴포넌트로 분리 → UI 변경 시 수정 범위 최소화 |
| 2 | 크로스 브라우저 | `--browser` 옵션 하나로 Chrome·Edge·Firefox 단독/동시 실행 자동 파라미터화 |
| 3 | 파일 업로드 | `send_keys` 풀패스 주입으로 OS 파일 다이얼로그 우회 |
| 4 | Firefox 타이밍 | 팝오버 닫힘 대기로 브라우저 간 렌더링 속도 차이 flaky 해결 |
| 5 | 다운로드 감지 | Chrome `.crdownload` / Firefox `.part` 임시 확장자 병행 감지 |
| 6 | LNB 안정화·삭제 독립성 | 가상화 목록 안정화 + 자기 생성 대화만 삭제(독립성·cleanup 겸용) |
| 7 | SSO 인증 우회 | CDP 쿠키 주입 + 30분 TTL 캐싱 → 매 테스트 로그인 5~8초 제거 |
| 8 | 방어적 클릭 | visibility → scrollIntoView → clickable → JS fallback 4단계로 React/MUI flaky 흡수 |
| 9 | xfail 버그 추적 | 알려진 버그를 skip이 아닌 `xfail(strict=True)`로 파이프라인에 유지 |
| 10 | 자동 스크린샷 | 실패 단계 감지 후 디스크·Allure 동시 저장 |
| 11 | fixture 설계 | scope 분리(session/function) + fresh_chat·seeded_chat로 셋업 캡슐화·DRY |
| 12 | Ruff 정적 분석 | import 정렬·미사용 변수 등 CI Lint job 자동화 |
| 13 | API negative | 게이트웨이 409 래핑 분해로 인증 음성(negative) 케이스 검증 |

### 1. Component Object Pattern — ChatPage 역할별 분리

**UI 변경 시 수정 범위를 해당 컴포넌트 1개로 한정하기 위해 ChatPage를 세 컴포넌트로 분리했습니다.** POM만으로 구성했을 때 `ChatPage`는 채팅 입력·전송, + 버튼 메뉴, LNB가 모두 한 파일에 쌓여 400줄에 근접했고, TC_008 작성 중 "이 메서드는 PlusMenu의 기능인가, ChatPage의 기능인가"를 구분하기 어려워졌습니다.

화면의 UI 영역별로 전담 컴포넌트 클래스를 만들었습니다.

| 컴포넌트 | 담당 화면 영역 | 주요 역할 |
|---|---|---|
| `ChatInputComponent` | 채팅 입력창 | 메시지 입력·전송, AI 응답 대기 |
| `PlusMenuComponent` | + 버튼 팝업 | 파일·이미지·PPT 업로드, 웹 검색 |
| `LnbComponent` | 왼쪽 대화 목록 | 목록 로딩 대기, 대화 URL 수집·삭제 |

`ChatPage`는 이 세 컴포넌트를 속성으로 들고 있는 **조율자** 역할만 합니다. 로케이터를 직접 갖거나 클릭하지 않고, 테스트에서 `chat_page.chat_input.send_message()` 형태로 접근합니다.

```
ChatPage (조율자)
├── self.chat_input  →  ChatInputComponent   메시지 전송 · AI 응답 대기
├── self.plus_menu   →  PlusMenuComponent    파일 · 이미지 · PPT · 웹검색
└── self.lnb         →  LnbComponent         대화 목록 조회 · 삭제
```

다운로드 완료 감지(`wait_for_download`)는 특정 UI 영역과 무관한 유틸리티라 `utils/download.py`로 따로 뺐습니다.

**왜 이 구조가 좋은가.** UI가 바뀌었을 때 수정 범위가 명확해집니다. + 버튼 위치가 바뀌면 `PlusMenuComponent`만 열면 됩니다. 분리 전에는 어디를 고쳐야 하는지 `ChatPage` 전체를 읽어야 했습니다.

이 원칙을 끝까지 지키기 위해, 테스트 본문에 임시로 흩어져 있던 로케이터(이미지 응답 다운로드 버튼·PPT 모드 칩)도 모두 해당 컴포넌트의 클래스 속성으로 끌어올렸습니다. 그 결과 **모든 로케이터는 예외 없이 Page/Component 객체에만 존재**하고, 테스트는 동작과 검증에만 집중합니다.

### 2. 크로스 브라우저 지원 — pytest_addoption + pytest_generate_tests

**`--browser` 옵션 하나로 Chrome · Edge · Firefox를 단독 또는 전체 실행할 수 있고, 테스트 코드 변경 없이 파라미터화가 자동 전파됩니다.** `pytest_addoption`으로 옵션을 등록하고, `pytest_generate_tests`로 `--browser all` 지정 시 모든 테스트를 3브라우저로 자동 파라미터화합니다.

```python
# conftest.py
def pytest_addoption(parser):
    parser.addoption("--browser", choices=["chrome", "edge", "firefox", "all"], default="chrome")

def pytest_generate_tests(metafunc):
    if "browser" in metafunc.fixturenames:
        opt = metafunc.config.getoption("--browser")
        browsers = ["chrome", "edge", "firefox"] if opt == "all" else [opt]
        metafunc.parametrize("browser", browsers)
```

**Firefox CDP 미지원 대응.** Firefox는 `execute_cdp_cmd`를 지원하지 않습니다. `authenticated_driver` fixture에서 `browser == "firefox"` 분기를 두어 도메인 이동 후 Selenium 표준 `add_cookie`로 폴백합니다. 다운로드 설정도 Chromium 계열의 `prefs` dict 대신 `options.set_preference`로 주입합니다.

**`temp_download_dir` fixture.** 브라우저 인스턴스마다 pytest의 `tmp_path`를 기반으로 격리된 다운로드 디렉터리를 생성해 `driver` fixture에 주입합니다. 테스트 간 다운로드 파일 충돌이 없고, Firefox · Chrome 모두 동일한 경로를 가리킵니다.

```python
# 실행 예시
pytest --browser chrome          # Chrome 단독
pytest --browser firefox         # Firefox 단독
pytest --browser all -m "ui"     # 3브라우저 × UI 전체
```

**fixture 의존성 체인.** `browser` 픽스처는 트랜지티브 의존성을 통해 모든 UI 테스트에 자동 전파됩니다.

```
browser  (pytest_generate_tests가 값 주입)
  └── temp_download_dir  (tmp_path 기반 브라우저별 격리 디렉터리)
        └── driver  (Chrome | Edge | Firefox 인스턴스 생성)
              └── authenticated_driver  (SSO 쿠키 캐싱 → 로그인 검증)
                    ├── fresh_chat   (새 대화 시작된 ChatPage → 대다수 UI TC의 출발점)
                    ├── seeded_chat  (사전 대화 생성된 ChatPage → '기존 대화 존재' 전제 TC)
                    └── 개별 테스트 (test_*)
```

테스트 함수가 `browser`를 직접 인자로 받지 않아도 `driver`를 통해 픽스처 체인에 편입되므로, `pytest_generate_tests`의 파라미터화가 모든 UI 테스트에 투명하게 전파됩니다.

### 3. send_keys 풀패스 파일 업로드 — OS 파일 다이얼로그 우회

**OS 파일 다이얼로그를 우회해 Chrome · Edge · Firefox 및 headless 환경에서 동일하게 동작합니다.** Chrome 148에서 기존 `Page.setInterceptFileChooser` CDP 방식의 지원이 중단되어, `PlusMenuComponent.upload_file()`은 숨겨진 `input[type='file']`을 JS로 강제 노출하고 절대 경로를 `send_keys`로 직접 주입하는 방식으로 전환했습니다.

```python
def upload_file(self, file_path):
    self.select_plus_menu_item(self.MENU_FILE_UPLOAD)   # 팝오버 닫힘까지 대기
    file_input = self.wait.until(
        EC.presence_of_element_located(self.FILE_INPUT)
    )
    self.driver.execute_script(
        "arguments[0].removeAttribute('hidden');"
        "arguments[0].style.display='block';"
        "arguments[0].style.visibility='visible';",
        file_input,
    )
    file_input.send_keys(str(Path(file_path).resolve()))   # 절대 경로 직접 주입
```

**왜 이 방식인가.** OS 파일 다이얼로그는 네이티브 모달로 브라우저 DOM을 블로킹합니다. `send_keys`를 `input[type='file']`에 직접 호출하면 다이얼로그 없이 파일 경로가 설정되므로, Chrome · Edge · Firefox 모두 동일한 코드로 동작하고 headless 환경에서도 안정적입니다. 단독 실행 결과 **PASSED** 확인.

### 4. select_plus_menu_item — 팝오버 닫힘 대기로 Firefox 타이밍 이슈 해결

**팝오버 소멸을 명시적으로 대기해 Firefox의 `ElementClickInterceptedException`을 원천 차단했습니다.** `+` 메뉴 항목 선택 패턴(open_menu → click → 다음 동작)을 `select_plus_menu_item()`으로 추출하고, 클릭 직후 `PLUS_MENU_POPOVER`(`ul[role='menu']`)가 DOM에서 사라질 때까지 대기하는 로직을 추가했습니다.

```python
def select_plus_menu_item(self, menu_locator: tuple[str, str]):
    self.open_menu()
    self.click(menu_locator)
    self.wait_until_invisible(self.PLUS_MENU_POPOVER)   # Firefox 팝오버 잔재 방지
```

**왜 이 방식인가.** Firefox는 Chromium 대비 MUI 팝오버 애니메이션 처리가 느려, 팝오버가 DOM에 남아 있는 상태에서 다음 동작이 실행되면 `ElementClickInterceptedException`이 발생합니다. 팝오버 소멸을 명시적으로 기다리는 게 `time.sleep`보다 결정론적이고 안정적입니다.

### 5. wait_for_download — Chrome · Firefox 임시 확장자 병행 감지

**`.crdownload`(Chrome/Edge)와 `.part`(Firefox) 두 임시 확장자를 모두 감지해 브라우저별 다운로드 완료를 단일 로직으로 처리합니다.** 초기 구현은 `ChatPage` 정적 메서드였으나, Page 레이어와 무관한 유틸리티가 Page 클래스에 위치하는 SRP 위반을 해소하기 위해 `utils/download.py`로 분리했습니다. 테스트는 `from utils.download import wait_for_download`로 직접 임포트합니다.

```python
# utils/download.py
def wait_for_download(download_dir: Path, before_count: int, timeout: int = 60) -> bool:
    for _ in range(timeout):
        current = list(download_dir.iterdir())
        if len(current) > before_count and not any(
            f.name.endswith((".crdownload", ".part")) for f in current
        ):
            return True
        time.sleep(1)
    return False
```

### 6. LNB 안정화 — wait_for_lnb_loaded + get_lnb_hrefs 재시도

**가상화 LNB의 항목 수가 3회 연속 동일해질 때까지 폴링해 안정화를 보장하고, 타임아웃 시 `TimeoutError`로 침묵 실패를 차단합니다.** LNB는 가상화(virtualization)로 렌더링되어 로드 중 DOM 항목 수가 변동합니다. `get_lnb_hrefs()`(구 `get_chat_hrefs()`)는 JS로 href를 원자적으로 수집합니다. 초기 구현의 `StaleElementReferenceException` 재시도 로직은 `execute_script()`가 DOM 요소 참조를 반환하지 않아 실제 발생하지 않는 dead code임을 확인하고 제거했습니다.

```python
def wait_for_lnb_loaded(self, timeout: int = 10) -> None:
    stable_rounds, prev_count = 0, -1
    deadline = time.time() + timeout
    while time.time() < deadline:
        current = len(self.driver.find_elements(*self.LNB_CHAT_ITEMS))
        stable_rounds = stable_rounds + 1 if current == prev_count else 0
        if stable_rounds >= 3:
            return
        prev_count = current
        time.sleep(0.3)
    raise TimeoutError(f"LNB 항목 수가 {timeout}초 내에 안정화되지 않았습니다.")
```

**왜 이 방식인가.** 단순 `until(lambda d: len(...) > 0)` 조건은 첫 항목이 렌더링되자마자 통과합니다. 가상화 LNB는 스크롤·리렌더 중에도 항목 수가 변하므로 3회 안정화 확인이 필요합니다. `TimeoutError` raise는 LNB가 끝까지 안정화되지 않을 때 원인 불명의 assertion 실패 대신 명확한 타임아웃 메시지를 남깁니다.

**삭제 TC의 독립성 — 자기 생성 대화만 타겟팅(cleanup 겸용).** 같은 테스트 계정에는 다른 TC·이전 실행이 만든 대화가 서버측에 누적됩니다. 초기 TC_014는 LNB '첫 번째 항목'을 삭제했는데, 이는 자기가 만들지 않은 데이터를 건드려 병렬·부분 실행 시 깨질 수 있는 교차 결합이었습니다. `LnbComponent.find_item_by_id()`를 추가해 **이 테스트가 직접 생성한 대화(`new_chat_id`)만 찾아 삭제**하도록 한정했습니다. 자기 데이터만 다루므로 독립성이 보장되고, 삭제가 곧 생성 데이터 정리가 되어 대화 누적도 방지합니다.

```python
# 임의의 첫 항목이 아니라, 이 테스트가 만든 대화만 삭제
target_item = chat_page.wait.until(lambda d: lnb.find_item_by_id(new_chat_id))
target_href = target_item.get_attribute("href")
ActionChains(driver).move_to_element(target_item).perform()
lnb.click(lnb.LNB_MORE_BUTTON); lnb.click(lnb.LNB_DELETE_BUTTON); lnb.click(lnb.CONFIRM_DELETE_BUTTON)
chat_page.wait.until(lambda d: target_href not in lnb.get_lnb_hrefs())   # 자기 대화 소멸 확인
```

### 7. SSO 인증 우회 — CDP 쿠키 주입 + 30분 TTL 캐싱

**SSO 리다이렉트 5~8초를 제거하고, 캐시 만료·검증 실패 시 자동 재로그인하는 self-healing 구조입니다.** 로그인 성공 시점의 쿠키를 30분 TTL 파일 캐시(`.pytest_cache/elice_session.json`)에 저장하고, 이후 테스트는 `account.elice.io → qaproject.elice.io` SSO 리다이렉트 없이 캐시를 재사용합니다. 캐시가 만료되거나 로그인 검증에 실패하면 즉시 무효화하고 정상 로그인 경로로 폴백합니다.

**왜 CDP인가 / Firefox 폴백.** Selenium의 표준 `driver.add_cookie()`는 해당 도메인을 먼저 방문해야만 동작합니다. Chromium 계열에서는 `Network.setCookie` CDP 커맨드로 도메인 진입 전에 쿠키를 주입해 이 문제를 해결합니다. Firefox는 CDP를 지원하지 않으므로 도메인 이동(`driver.get(base_url)`) 후 `add_cookie()`로 주입하는 폴백 경로를 분기 처리했습니다.

```python
if browser == "firefox":
    driver.get(base_url)
    for cookie in cached_cookies:
        driver.add_cookie({**cookie, "domain": cookie["domain"].lstrip(".")})
else:
    driver.execute_cdp_cmd("Network.enable", {})
    for cookie in cached_cookies:
        driver.execute_cdp_cmd("Network.setCookie", {...})
```

### 8. 방어적 클릭 패턴 — React/MUI flaky test 흡수

**React/MUI SPA의 모달·리렌더 사이클에서 발생하는 인터셉트·스테일 예외만 폴백 경로로 처리해 flaky test를 줄이면서 실제 결함이 sleep 뒤에 가려지지 않도록 했습니다.** `BasePage.click()`은 `visibility → scrollIntoView → element_to_be_clickable → click()` 4단계를 거치며, `ElementClickInterceptedException` 또는 `StaleElementReferenceException` 발생 시 요소를 재조회한 뒤 JavaScript click으로 폴백합니다.

"그냥 sleep을 늘린다" 대신 **구체적인 예외 타입만 폴백 경로로 처리**하는 방식으로, 실제 결함이 sleep 뒤에 숨겨지지 않도록 했습니다.

`BasePage`는 `wait_up_to(timeout)` 메서드도 제공합니다. 기존에는 AI 응답·PPT 생성처럼 긴 대기가 필요한 TC마다 `long_wait = WebDriverWait(authenticated_driver, n)`을 인라인으로 선언했으나, 이를 `chat_page.wait_up_to(n)`으로 교체해 드라이버 참조 중복을 제거하고 WebDriver 접근을 `BasePage` 한 곳으로 집약합니다.

```python
# BasePage
def wait_up_to(self, timeout: int) -> WebDriverWait:
    return WebDriverWait(self.driver, timeout)

# 테스트에서
long_wait = chat_page.wait_up_to(600)   # PPT 생성 최대 대기
```

**AI 응답 대기는 단일 메서드로 통일.** 일부 TC는 응답 완료를 `long_wait.until(EC.visibility_of_element_located(AI_MESSAGE_CONTENT)).text`처럼 직접 풀어 썼고, 다른 TC는 `ChatInputComponent.wait_for_ai_response()`를 호출하는 등 같은 동작을 세 가지 방식으로 기다리고 있었습니다. 이미 존재하던 `wait_for_ai_response()` 한 경로로 모두 수렴시켜, "AI 응답을 어떻게 기다리는가"가 코드베이스 전체에서 한 가지로 일관되도록 정리했습니다.

### 9. 알려진 버그의 xfail + Allure issue 추적

**버그 수정 시 테스트가 XPASS로 빌드를 실패시켜 수정을 자동으로 감지합니다.** TC_009(다운로드 응답 미저장)를 skip·주석 처리 대신 `@pytest.mark.xfail(reason=..., strict=True)`로 파이프라인에 유지했습니다. `@allure.issue()`로 이슈 링크를 연결하고, `docs/bugs/TC_009/`의 재현 스크린샷·GIF를 Allure에 자동 첨부합니다.

`strict=True`는 버그가 수정되어 **예상 외로 통과(XPASS)할 경우 빌드를 실패**시킵니다. 회귀가 아닌 "수정"도 자동 감지되어 케이스를 정식 통과로 승격시키는 트리거가 됩니다.

### 10. 실패 시 자동 스크린샷

**`call`·`setup` 어느 단계에서 실패하든 스크린샷을 디스크와 Allure 양쪽에 동시 기록해 빌드 종료 후에도 증거를 보존합니다.** `pytest_runtest_makereport` hook을 `hookwrapper`로 감싸 실패 단계를 감지하고 드라이버를 추출합니다.

```python
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when in ("call", "setup") and report.failed:
        driver = item.funcargs.get("authenticated_driver") or item.funcargs.get("driver")
        if driver:
            safe_name = item.nodeid.replace("/", "_").replace("::", "_").replace("\\", "_")
            driver.save_screenshot(f"reports/screenshots/{safe_name}.png")
            allure.attach(...)
```

### 11. fixture scope의 의식적 분리

자원별 비용과 격리 요구를 따로 판단해 `session`/`function`을 혼용했습니다.

- `auth_token` → **`scope="session"`**: API 트랙 전체에서 1회 로드
- `api_session` → **`scope="function"`**: 테스트별 헤더·연결 격리 후 close
- `driver` / `authenticated_driver` / `temp_download_dir` → **`scope="function"`**: 브라우저·다운로드 경로 테스트 간 완전 격리

**사전 조건 fixture 2종 — 셋업 로직의 캡슐화로 DRY 확보.** 대다수 UI TC는 매 함수 첫머리에서 `ChatPage(authenticated_driver)` 생성 → 컴포넌트 추출 → `start_new_chat()`라는 동일한 4~5줄을 반복하고 있었습니다. 이 출발점 상태를 두 개의 fixture로 분리해, 테스트 본문이 TC 핵심 시나리오에만 집중하도록 했습니다.

- **`fresh_chat`** — "빈 새 대화 화면"을 전제로 하는 대다수 TC용. `ChatPage` 생성 + `start_new_chat()`까지 끝낸 인스턴스를 반환합니다. 도입 후 UI 테스트 8곳의 셋업 보일러플레이트가 인자 한 줄로 축소됐습니다.
- **`seeded_chat`** — TS-002처럼 "기존 대화가 이미 있는 상태"를 전제로 하는 TC용. 메시지를 하나 전송하고 AI 응답까지 완료된 `ChatPage`를 반환합니다.

두 fixture 모두 `ChatPage`를 반환하므로 `chat_page.driver`로 드라이버에도 접근할 수 있어, 테스트가 `authenticated_driver`를 직접 인자로 받을 필요가 없습니다.

```python
@pytest.fixture(scope="function")
def fresh_chat(authenticated_driver):
    chat_page = ChatPage(authenticated_driver)
    chat_page.chat_input.start_new_chat()   # 새 대화 출발점까지 셋업
    return chat_page

@pytest.fixture(scope="function")
def seeded_chat(authenticated_driver):
    chat_page = ChatPage(authenticated_driver)
    chat_page.send_message("안녕하세요, 대화 보존 테스트입니다.")
    chat_page.wait_for_ai_response()        # 기존 대화가 존재하는 상태
    return chat_page

# 테스트에서는 사전 준비 없이 바로 TC 검증
def test_send_via_button_shows_ai_response(self, fresh_chat):
    chat_page = fresh_chat                  # 셋업 끝, 바로 검증 시작
    ...
```

### 12. Ruff 정적 분석 — CI 코드 품질 자동화

**Lint job이 통과해야만 API · UI 테스트 job이 실행되어 코드 품질 문제를 조기 차단합니다.** GitHub Actions에 `Lint (Ruff)` job을 추가해 push마다 import 정렬(isort), 미사용 변수(`F401`), f-string 오용(`F541`), 공백 규칙(`E`/`W`) 등을 자동으로 검사합니다.

```toml
# ruff.toml
select = ["E", "F", "W", "I"]   # pycodestyle + pyflakes + isort
```

```yaml
# .github/workflows/lint.yml — 매 push에서 실행되는 게이트
lint:
  steps:
    - run: pip install ruff
    - run: ruff check .          # 위반 발생 시 job 실패
```

**왜 Ruff인가.** flake8 + black + isort를 별도로 설치·설정하면 CI 실행 시간이 늘고 설정 파일도 세 개가 됩니다. Rust로 작성된 Ruff는 동일 규칙을 단일 바이너리로 처리해 **기존 대비 10~100× 빠른 속도**를 내면서 설정을 `ruff.toml` 하나로 통합합니다. 7초 안에 끝나는 검사라 매 push 게이트로 두어도 부담이 없습니다.

**워크플로우 분리.** 정적 검사(`lint.yml`)는 매 push, 대상 서비스에 실제 접속하는 E2E(`e2e.yml`)는 수동 트리거로 나눴습니다. E2E는 서비스 가용성·테스트 계정 자격증명이라는 외부 요인에 의존해 코드 변경과 무관하게 실패할 수 있고, 그 실패가 push 게이트를 오염시키면 정작 코드 품질 신호를 못 읽게 되기 때문입니다.

### 13. API 음성(negative) 케이스 — 게이트웨이 409 래핑 분해

**백엔드의 403이 게이트웨이에 의해 409로 래핑되는 구조를 분해해 인증 거부 여부를 응답 body에서 직접 검증합니다.** 인증 헤더 완전 생략(TC_018), 서명 불일치 JWT(TC_019), 잘못된 인증 스킴 Basic(TC_020) 세 가지 음성 시나리오를 포함하며, TC_019에서 단순 상태 코드 비교로는 인증 거부 여부를 판단할 수 없는 구조를 발견했습니다.

```python
# TC_019 — 유효하지 않은 JWT 검증
assert response.status_code in (401, 403, 409)

if response.status_code == 409:          # 게이트웨이 래핑 경로
    inner_status = (
        response.json()
        .get("detail", {})
        .get("resp_json", {})
        .get("_result", {})
        .get("status_code")
    )
    assert inner_status == 403           # 실제 인증 실패임을 body로 확인
```

**왜 이렇게 했나.** 게이트웨이 래핑은 테스트 환경마다 달라질 수 있어 허용 상태 코드를 `in (401, 403, 409)`으로 열어두고, 409인 경우에만 body를 검증하는 조건부 분기를 택했습니다. 단순히 통과율을 높이려고 `assert True`로 넘기는 대신, **시스템 내부 구조를 이해한 상태에서 인증 거부가 실제로 발생했음을 검증**하는 것이 목적입니다.

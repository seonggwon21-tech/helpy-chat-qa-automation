# 코드 리뷰 보고서

## 요약 평가

전체 구조는 Component Object Pattern + Facade, CDP 쿠키 캐싱, 크로스 브라우저 파라미터화, xfail 버그 추적까지 신입 포트폴리오 수준을 명확히 초과한다. 설계 결정마다 "왜 이렇게 했는가"가 코드에 드러나며, QA 엔지니어링 가치관이 일관적이다. 다만 몇 가지 구조적 결함(쿠키 캐시 브라우저 비격리, `browser` fixture 방어 코드 누락, dead code)이 완성도를 낮추고 있어 수정 후 제출을 권장한다.

---

## 강점 (포트폴리오 어필 포인트)

### 1. Component Object Pattern — Facade + SRP 완성도
- **파일**: `pages/chat_page.py:18`, `pages/components/__init__.py`
- **내용**: `ChatPage`는 로케이터를 직접 보유하지 않고 `ChatInputComponent`, `PlusMenuComponent`, `LnbComponent` 세 전담 컴포넌트를 조합하는 Facade 역할만 한다. `__init__.py`에서 `__all__` 명시로 컴포넌트 패키지 인터페이스를 명확히 정의했다.
- **포트폴리오 가치**: "Page Object 만들 줄 안다"와 "Component 단위로 책임을 분리할 수 있다"는 레벨 차이가 크다. SRP를 의식한 설계 결정은 중급 이상 QA 엔지니어링 역량을 증명한다.

### 2. CDP 쿠키 주입 + Self-Healing 캐시
- **파일**: `conftest.py:149-226`
- **내용**: SSO 리다이렉트 비용을 제거하기 위해 `Network.setCookie` CDP 커맨드로 도메인 진입 전 쿠키를 주입하고, 30분 TTL 파일 캐시를 운용한다. 캐시 복원 실패 시 캐시 파일을 삭제하고 정상 로그인 경로로 폴백하는 self-healing 구조가 완성되어 있다. Firefox CDP 미지원 문제는 `browser == "firefox"` 분기로 `add_cookie` 폴백을 구현했다.
- **포트폴리오 가치**: Selenium WebDriver API를 넘어 CDP 계층까지 내려간 경험은 실무 자동화 엔지니어 수준의 역량을 직접 보여준다. "SSO 환경에서 테스트 속도 최적화"라는 실무 문제를 푼 결과물이다.

### 3. pytest 훅 시스템 활용 — 두 단계 실패 커버
- **파일**: `conftest.py:255-269`
- **내용**: `pytest_runtest_makereport`를 `hookwrapper`로 감싸 `call`(테스트 본문)뿐 아니라 `setup`(fixture 준비) 단계 실패에도 스크린샷을 남긴다. `item.funcargs`에서 드라이버를 추출하고 `nodeid`의 특수문자를 치환해 OS 무관 파일명을 생성하는 세부 구현까지 견고하다.
- **포트폴리오 가치**: `setup` 단계 커버는 많은 엔지니어가 놓치는 포인트다. "왜 fixture에서 실패했는지 CI에서 알 수 없다"는 실무 문제를 경험하지 않으면 나오기 어려운 설계다.

### 4. xfail(strict=True) 버그 추적 철학
- **파일**: `tests/ui/test_plus_menu.py:85-88`
- **내용**: TC_009 이미지 다운로드 버그를 `skip`이나 주석이 아닌 `xfail(strict=True)`로 처리했다. `strict=True`는 버그가 수정되어 테스트가 XPASS되면 빌드를 실패시킨다. `@allure.issue`로 이슈를 연결하고 `docs/bugs/TC_009/`에 재현 GIF·스크린샷을 보존해 Allure 첨부로 자동 노출한다.
- **포트폴리오 가치**: "자동화 통과율 100%보다 현재 시스템 상태를 정확히 반영하는 리포트가 신뢰할 수 있다"는 QA 철학을 코드로 증명한다. 신입·주니어와 가장 뚜렷하게 구별되는 지점이다.

### 5. 방어적 클릭 패턴 — React/MUI SPA 대응
- **파일**: `pages/base_page.py:31-46`
- **내용**: `visibility → scrollIntoView → element_to_be_clickable → click()` 4단계 후, `ElementClickInterceptedException` 또는 `StaleElementReferenceException` 발생 시 요소를 재조회해 JS click으로 폴백한다. `time.sleep(0.3)`은 MUI 애니메이션 완료를 위한 최소 안정화 대기이며 코드 주석으로 이유가 설명되어 있다.
- **포트폴리오 가치**: "flaky test를 sleep으로 덮는다" vs "특정 예외에만 폴백 경로를 둔다"는 자동화 성숙도의 차이다. SPA 환경에서 실제로 고생해본 사람만 이런 패턴을 만든다.

### 6. API 음성(negative) 케이스 — 게이트웨이 409 래핑 분해
- **파일**: `tests/api/test_community_api.py:101-129`
- **내용**: 백엔드 403 응답이 API 게이트웨이에서 409로 래핑되는 구조를 파악하고, 409인 경우 `body.detail.resp_json._result.status_code == 403`으로 내부를 검증한다. 단순 상태 코드 비교를 넘어 시스템 내부 아키텍처를 이해한 상태에서 인증 거부 여부를 판단한다.
- **포트폴리오 가치**: "API 테스트 = 200 확인"이 아니라 인증 계층, 게이트웨이 동작, 음성 케이스까지 커버하는 역량을 보여준다. 블랙박스 테스트와 화이트박스 테스트의 경계를 이해하는 엔지니어임을 증명한다.

### 7. LNB href 기반 검증 — 가상화 환경 대응
- **파일**: `pages/components/lnb_component.py:8-12`, `tests/ui/test_lnb_management.py:70-74`
- **내용**: 가상화(virtualization)로 렌더링되는 LNB에서 DOM 항목 수 대신 `href` 집합 차이로 새 대화 추가·삭제를 판별한다. JS로 원자적으로 수집해 `StaleElementReferenceException`을 구조적으로 회피하며, 삭제 확인도 `target_href not in lnb.get_lnb_hrefs()` 조건으로 정확도를 높였다.
- **포트폴리오 가치**: 가상화 리스트에서 DOM 기반 count 비교의 한계를 인식하고 href 기반 diff로 전환한 결정은 실무 SPA 자동화 경험이 없으면 나오기 어렵다.

### 8. seeded_chat fixture — 사전 조건 캡슐화
- **파일**: `conftest.py:232-249`
- **내용**: "기존 대화가 있는 상태"를 전제로 하는 TC를 위한 `seeded_chat` fixture가 메시지 전송부터 AI 응답 완료까지 사전 준비를 담당한다. 테스트 본문은 TC 핵심 검증에만 집중하고 `seeded_chat.driver`로 드라이버에 접근할 수 있다.
- **포트폴리오 가치**: fixture 합성(composition) 패턴을 이해하고 사전 조건 준비 로직을 테스트 본문에서 분리하는 능력은 테스트 유지보수성과 직결된다.

---

## 개선 권고

### High — 수정 강력 권고

| 파일 | 문제 | 개선안 |
|------|------|--------|
| `conftest.py:58` | `_COOKIE_CACHE_PATH = Path(".pytest_cache/...")` 상대 경로. pytest 실행 위치가 프로젝트 루트가 아닐 경우 캐시를 찾지 못하거나 잘못된 위치에 생성됨 | `Path(__file__).parent / ".pytest_cache/elice_session.json"` 절대화 |
| `conftest.py:58` | 쿠키 캐시가 브라우저 종류를 구분하지 않음. `--browser all`로 Chrome → Firefox 순으로 실행 시 Chrome이 저장한 쿠키를 Firefox가 재사용해 인증 실패 가능 | 캐시 경로를 `elice_session_{browser}.json`으로 브라우저별 분리 |
| `conftest.py:83` | `browser` fixture에 `request.param` 가드 없음. `pytest_generate_tests`가 파라미터를 주입하지 않은 상태에서 fixture가 호출되면 `AttributeError` 발생 | `return getattr(request, "param", "chrome")` |
| `tests/ui/test_plus_menu.py:223-225` | TC_011 웹 검색에서 `long_wait.until(...).click()` 인라인 패턴 사용. `select_plus_menu_item()`으로 도입한 팝오버 대기가 이 TC에만 누락 | `plus.select_plus_menu_item(plus.MENU_WEB_SEARCH)` 교체 |

### Medium — 개선 권고

| 파일 | 문제 | 개선안 |
|------|------|--------|
| `pages/components/lnb_component.py:35-43` | `get_lnb_hrefs()` 내 `StaleElementReferenceException` 재시도 로직이 dead code. `execute_script()`는 DOM 요소를 반환하지 않으므로 이 예외가 발생하지 않음 | retry 블록 제거 또는 `Exception`으로 교체해 실제 오류 방어용으로 전환 |
| `pages/components/lnb_component.py:17-32` | `wait_for_lnb_loaded()` 타임아웃 시 예외 없이 `None` 반환. LNB가 끝까지 안정화되지 않아도 침묵하므로 이후 테스트 실패 원인 추적이 어려움 | `TimeoutError("LNB 안정화 타임아웃")` raise 추가 |
| `pages/chat_page.py:49-62` | `wait_for_download()`가 `ChatPage`의 `@staticmethod`로 정의되어 있으나 `ChatPage` 상태를 전혀 사용하지 않음. 의미상 유틸리티 함수에 해당 | `utils/download.py`로 분리하거나 conftest `temp_download_dir` fixture에 완료 감지 로직 통합 |
| `pages/signup_page.py:16` | `AGREE_ALL_CHECKBOX = (By.CSS_SELECTOR, "input[type='checkbox']")` 는 페이지에 체크박스가 여러 개인 경우 첫 번째만 선택. 약관 동의 화면 변경 시 잘못된 요소 클릭 위험 | 더 구체적인 선택자(예: `[name='agreeAll']` 또는 `:first-of-type`) 사용 |
| `conftest.py`, `tests/ui/*.py` | `long_wait = WebDriverWait(authenticated_driver, 120)` 패턴이 개별 테스트 메서드 내부에서 반복 선언됨. `BasePage`에 이미 `self.wait`가 있고 timeout만 다름 | `BasePage.wait_with_timeout(timeout)` 또는 `WebDriverWait` 팩토리 메서드 제공 |

### Low — 참고용

| 파일 | 문제 | 개선안 |
|------|------|--------|
| `utils/logger.py:5-9` | `pytest.ini`의 `log_cli=true`와 `get_custom_logger`의 `StreamHandler`가 동시에 동작하면 CI에서 로그가 이중 출력됨. docstring에 경고가 있으나 코드 레벨 방어는 없음 | `log_cli=true` 사용 시 `get_custom_logger`에서 `StreamHandler` 추가 조건부 처리 |
| `pages/base_page.py:39` | `time.sleep(0.3)` 고정값. 느린 CI 환경에서 부족할 수 있음 | `ANIMATION_WAIT` 환경변수로 외부화 |
| `tests/ui/test_plus_menu.py` | `from selenium.webdriver.common.action_chains import ActionChains` 임포트가 xfail 테스트(TC_009)에서만 사용됨. 테스트를 실행하지 않더라도 임포트는 항상 발생 | 문제는 아니나 리뷰어 시각에서 "이 임포트가 왜 있지?" 의문을 줄 수 있음 |

---

## 포트폴리오 질문 답변

### 1. 가장 기술적으로 인상적인 구현 3가지

1. **CDP `Network.setCookie` + self-healing 캐시** — Selenium API 레이어를 넘어 CDP 프로토콜 직접 호출. 실무에서 SSO 인증 비용 문제를 실제로 경험하고 해결한 증거.
2. **`pytest_runtest_makereport` hookwrapper로 setup 단계 커버** — setup 실패도 스크린샷으로 잡는다. 기본 예제에서 절대 나오지 않는 패턴이며 CI 원격 실패 디버깅 경험이 축적된 결과.
3. **LNB href 기반 diff 검증** — 가상화 리스트에서 DOM count 비교의 한계를 JS 원자 수집 + 집합 연산으로 해결. 프레임워크 이해 없이는 나오지 않는 설계.

### 2. 신입·주니어와 구별되는 설계 결정

- `xfail(strict=True)` 버그 추적: 신입은 skip으로 덮거나 삭제한다. XPASS 빌드 실패 개념을 이해하고 적용한 것은 QA 철학 수준의 차이.
- 방어적 클릭 패턴: sleep 증가가 아닌 예외 종류 기반 폴백 분기. SPA flaky test와 싸워본 사람만 도달하는 패턴.
- fixture scope 의식적 혼용: `session` vs `function` 비용·격리 트레이드오프를 명확히 구분. 많은 주니어가 모든 fixture를 `function`으로 설정하거나 의미 없이 `session`을 사용한다.

### 3. README에 반드시 넣어야 할 기술적 포인트

1. **CDP 쿠키 주입** — SSO 환경 + Selenium 한계 → CDP 직접 호출이라는 문제-원인-해결 흐름이 서사로 강하다.
2. **xfail(strict=True) 버그 추적 전략** — "통과율 100%가 아니라 시스템 상태를 정확히 반영한다"는 QA 철학 명문화.
3. **API 409 게이트웨이 래핑 분해** — 시스템 내부 구조를 이해한 테스트 설계임을 증명하는 유일한 포인트.

### 4. 이 코드베이스에서 드러나는 QA 엔지니어링 가치관

- **테스트 시간 = 비용**: SSO 캐싱, fixture scope 분리, `--browser` 슬라이스 실행 전략이 모두 "불필요한 반복을 제거"하는 방향이다.
- **실패는 디버깅 가능해야 한다**: hookwrapper 스크린샷, Allure 4계층, setup 단계 커버 — 실패했을 때 "왜 실패했는지 알 수 없다"는 상황을 구조적으로 차단한다.
- **자동화 ≠ 통과율 100%**: xfail로 버그를 추적하고 XPASS 빌드 실패로 수정을 감지한다. 신뢰할 수 없는 통과율보다 정확한 시스템 상태 반영을 우선한다.
- **내가 짠 코드를 의심한다**: 방어적 클릭, 예외 폴백, LNB 안정화 폴링 — 모든 공통 액션에 "이게 실패할 수 있는 시나리오"를 먼저 고려했다.

---

## 수정 우선순위 체크리스트

- [ ] **[High]** 쿠키 캐시 경로 절대화 (`Path(__file__).parent`)
- [ ] **[High]** 쿠키 캐시 브라우저별 분리 (`elice_session_{browser}.json`)
- [ ] **[High]** `browser` fixture `getattr` 가드 추가
- [ ] **[High]** TC_011 웹 검색 → `select_plus_menu_item()` 교체
- [ ] **[Medium]** `get_lnb_hrefs()` dead code retry 제거
- [ ] **[Medium]** `wait_for_lnb_loaded()` 타임아웃 시 예외 raise
- [ ] **[Medium]** `wait_for_download()` utils로 이동 검토

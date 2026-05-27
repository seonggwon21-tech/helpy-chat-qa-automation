# HelpyChat QA Automation

**AI Helpy Chat** 서비스(qaproject.elice.io)를 대상으로 한 UI 자동화 테스트 포트폴리오 프로젝트입니다.

![Python](https://img.shields.io/badge/Python-3.14-blue?logo=python&logoColor=white)
![pytest](https://img.shields.io/badge/pytest-8.x-0A9EDC?logo=pytest&logoColor=white)
![Selenium](https://img.shields.io/badge/Selenium-4.x-43B02A?logo=selenium&logoColor=white)
![Allure](https://img.shields.io/badge/Allure-Report-FF6B6B?logo=qameta&logoColor=white)
![Jenkins](https://img.shields.io/badge/Jenkins-CI-D24939?logo=jenkins&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-CI-2088FF?logo=githubactions&logoColor=white)

> 이 프로젝트는 Claude AI의 도움을 받아 만들었습니다.
>
> 테스트 케이스 수보다, 왜 이렇게 짜야 하는지를 이해하면서 만들고 싶었습니다.
>
> Jenkins 플러그인 서버가 중국 미러로 막혔을 때 VPN으로 우회했고, Python 경로 문제도 직접 파고들었습니다. AI가 브라우저에 테스트 단계를 오버레이로 표시하는 기능을 제안했을 때는, 자동화 목적에 불필요한 JS 실행이 매 스텝마다 추가되는 거라 판단해서 걷어냈습니다.
>
> 재현되는 버그는 skip으로 넘기지 않고 xfail로 처리했습니다. 테스트가 실행되고 실패해야, 버그가 실제로 존재한다는 걸 결과로 남길 수 있다고 생각했기 때문입니다.

---

## 데모

| pytest 실행 (시작) | pytest 실행 (완료) |
|---|---|
| ![pytest start](docs/images/pytest_start.gif) | ![pytest end](docs/images/pytest_end.gif) |

### Jenkins CI — 빌드 성공

![Jenkins Build Success](docs/images/jenkins-success.png)

### Allure 리포트

![Allure Report](docs/images/allure-report.png)

### 테스트 대상 서비스

![AI Helpy Chat](docs/images/test_message_send.png)

---

## 프로젝트 개요

엘리스(Elice)의 AI 어시스턴트 서비스인 **AI Helpy Chat**(`qaproject.elice.io/ai-helpy-chat`)을 대상으로 한 엔드 투 엔드 QA 자동화 포트폴리오입니다. 메시지 송수신, 입력 인터랙션, 새 대화 관리, 플러스 메뉴(파일 첨부/다운로드), LNB(좌측 네비게이션) 동작 등 핵심 사용자 시나리오를 UI 자동화로 검증하고, 동시에 에이전트 CRUD API를 별도 트랙으로 검증해 **UI · API 듀얼 트랙 회귀 안전망**을 구성했습니다.

단순 자동화 스크립트가 아니라 **POM 계층화, fixture scope 트레이드오프 분리, CDP 기반 쿠키 캐싱을 통한 SSO 비용 절감, 실패 자동 진단(스크린샷 + Allure 첨부), CI headless 통합, 알려진 버그의 xfail 추적**까지 갖춘 실무형 프레임워크를 목표로 설계했습니다.

---

## 기술 스택

| 분류 | 사용 기술 | 선택 이유 |
|---|---|---|
| 언어 | Python 3.14 | 표준 라이브러리만으로 fixture 캐시·CDP 통신 구현 |
| UI 자동화 | Selenium 4 + CDP | `execute_cdp_cmd("Network.setCookie")`로 도메인 진입 전에도 쿠키 주입 → SSO 리다이렉트 우회 |
| API 자동화 | requests | `Session` 객체로 헤더·연결 풀 재사용, OTP 로그인 API에서 토큰 자동 발급 |
| 테스트 프레임워크 | pytest 8.x | fixture scope(`session`/`function`) 분리, marker 기반 슬라이스(`ui`/`api`/`slow`), `makereport` hook 확장 |
| 리포팅 | Allure Report | epic/feature/story/step 4계층 + 환경 정보·실패 스크린샷 자동 첨부로 비기술 이해관계자도 읽는 리포트 |
| 설계 패턴 | Page Object Model | UI 동작과 테스트 로직을 분리해 로케이터 변경 시 단일 지점만 수정 |
| CI/CD | Jenkins + GitHub Actions | Jenkins: UI·API 분리 실행 + Allure publish / GHA: push/PR 시 API 테스트 자동화 |
| 환경 관리 | python-dotenv | `.env`로 자격증명·URL을 코드와 분리, `.gitignore` 처리 |
| 로깅 | Python logging | 공통 로거로 테스트 흐름을 stdout에 기록, `LOG_FILE` 환경변수로 파일 로그 추가 가능 |

---

## 프로젝트 구조

```
helpy-chat-qa-automation/
├── config/
│   └── config.py              # URL, 대기 시간 등 전역 상수 (BASE_UI_URL 환경변수 오버라이드 가능)
├── pages/                     # Page Object Model
│   ├── base_page.py           # 방어적 클릭/입력 + @allure.step 자동 데코레이션
│   ├── login_page.py          # SSO 로그인 흐름
│   ├── signup_page.py         # 약관 동의 후처리
│   └── chat_page.py           # 채팅 입력 · 플러스 메뉴 · LNB 액션
├── tests/
│   ├── ui/
│   │   ├── test_message_send.py      # TS-001
│   │   ├── test_new_chat.py          # TS-002
│   │   ├── test_input_features.py    # TS-003
│   │   ├── test_plus_menu.py         # TS-004
│   │   └── test_lnb_management.py   # TS-005
│   └── api/
│       └── test_community_api.py    # TS-006
├── test_data/
│   └── test_upload.txt        # 파일 업로드 TC용 더미 파일
├── utils/
│   └── logger.py              # 공통 로거 (LOG_FILE 환경변수로 파일 핸들러 활성화)
├── docs/
│   ├── bugs/
│   │   └── TC_009/            # 버그 재현 GIF 및 스크린샷
│   ├── images/                # README 데모 이미지
│   ├── test_cases.csv         # TC/TS 전체 목록
│   ├── bug-report.md          # 발견 결함 5건
│   └── troubleshooting.md     # 트러블슈팅 기록 (13건)
├── reports/                   # 실패 시 자동 저장되는 스크린샷
├── allure-results/            # Allure raw 데이터 (environment.properties 포함)
├── .github/
│   └── workflows/
│       └── qa.yml             # GitHub Actions (main/develop push/PR → API 테스트 자동 실행)
├── conftest.py                # Fixture 정의 (WebDriver, 인증, 쿠키 캐싱, 실패 훅)
├── Jenkinsfile
├── pytest.ini
├── .env.example               # 환경 변수 템플릿
└── .env                       # 자격증명 (gitignore 처리, 직접 생성 필요)
```

---

## 테스트 구성

UI 5개 시나리오 14개 TC + API 1개 시나리오 4개 TC, **총 18개 TC**.

| TS ID | 테스트 스위트 | TC | 설명 |
|---|---|---|---|
| TS-001 | 메시지 전송 E2E | TC_001 | 사용자 메시지 입력 → 전송 → AI 응답 노드 확인까지 단일 E2E 검증 |
| TS-002 | 새 대화 전환 | TC_002~003 | 새 대화 클릭 후 화면 초기화 확인, LNB에서 기존 대화 복원 확인 |
| TS-003 | 입력창 동작 | TC_004~006 | 빈 입력 차단, Shift+Enter 줄바꿈(미전송), Enter 전송 후 AI 응답 출력 |
| TS-004 | + 버튼 메뉴 | TC_007~011 | 파일 업로드 칩 노출, 이미지·PPT 생성, 웹 검색 (**TC_009는 `xfail(strict=True)`로 버그 추적**) |
| TS-005 | LNB 대화 목록 관리 | TC_012~014 | 가상화 환경에서 새로고침 보존·삭제·이름 변경을 href 기준으로 검증 |
| TS-006 | 에이전트 API & 인증 | TC_015~018 | 에이전트 CRUD + 미인증/만료 토큰 음성(negative) 케이스 |

> 전체 TC 목록: [docs/test_cases.csv](docs/test_cases.csv)  
> `pytest -m "ui and not slow"`로 PR 단위 빠른 피드백 루프를 지원합니다.

---

## 주요 구현 내용

### SSO 인증 우회 — CDP 쿠키 주입 + 30분 TTL 캐싱

**무엇을 했나.** 매 테스트마다 발생하는 `account.elice.io → qaproject.elice.io` SSO 리다이렉트 비용(약 5~8초)을 제거하기 위해, 로그인 성공 시점의 쿠키를 30분 TTL 파일 캐시(`.pytest_cache/elice_session.json`)에 저장하고 이후 테스트에서는 캐시를 재사용합니다. 캐시가 만료되거나 로그인 검증에 실패하면 캐시를 즉시 무효화하고 정상 로그인 경로로 폴백하는 **self-healing** 구조입니다.

**왜 CDP인가.** Selenium의 표준 `driver.add_cookie()`는 해당 도메인을 먼저 방문해야만 동작합니다. 캐시된 쿠키를 주입하려면 다시 SSO 페이지를 거쳐야 하는 모순이 생깁니다. Chrome DevTools Protocol의 `Network.setCookie`를 직접 호출하면 **도메인 진입 전에도 쿠키를 주입**할 수 있어 이 문제를 해결합니다.

```python
# conftest.py
driver.execute_cdp_cmd("Network.enable", {})
for cookie in cached_cookies:
    driver.execute_cdp_cmd("Network.setCookie", {
        "name": cookie["name"], "value": cookie["value"],
        "domain": cookie.get("domain", "qaproject.elice.io"),
        "path": cookie.get("path", "/"),
        "secure": cookie.get("secure", False),
        "httpOnly": cookie.get("httpOnly", False),
    })
driver.get(chat_url)
```

### 방어적 클릭 패턴 — React/MUI flaky test 흡수

**무엇을 했나.** `BasePage.click()`은 `visibility → scrollIntoView → element_to_be_clickable → click()` 4단계를 거칩니다. `ElementClickInterceptedException` 또는 `StaleElementReferenceException` 발생 시 요소를 재조회한 뒤 JavaScript click으로 폴백합니다.

**왜 이 방식인가.** 테스트 대상이 React + MUI로 구성된 SPA라 모달/툴팁/리렌더 사이클로 인해 일반 click이 가로채이거나 요소가 다시 부착되는 상황이 빈번합니다. "그냥 sleep을 늘린다" 대신 **인터셉트/스테일이라는 구체적인 예외만 폴백 경로로 처리**해, flaky test를 줄이면서 실제 결함이 sleep 뒤에 가려지지 않도록 했습니다. 모든 공통 동작에는 `@allure.step`이 부착돼 Allure 리포트가 자연어 시나리오처럼 읽힙니다.

### 알려진 버그의 xfail + Allure issue 추적

**무엇을 했나.** TC_009(다운로드 응답이 디스크에 저장되지 않는 결함)를 발견한 후, 테스트를 끄거나 주석 처리하지 않고 `@pytest.mark.xfail(reason=..., strict=True)`로 표시했습니다. `@allure.issue()`로 이슈 링크를 연결하고, `docs/bugs/TC_009/`에 재현 스크린샷·GIF를 보관해 Allure 첨부로 자동 연결합니다.

**왜 이 방식인가.** `strict=True`는 버그가 수정되어 테스트가 **예상 외로 통과(XPASS)할 경우 빌드를 실패**시킵니다. 회귀가 아닌 "수정"도 자동 감지되어 케이스를 정식 통과로 승격시키는 트리거가 됩니다. "자동화 통과율 100%"가 아니라 **현재 시스템 상태를 정확히 반영하는 리포트**가 더 신뢰할 수 있다는 판단입니다.

### 실패 시 자동 스크린샷

**무엇을 했나.** `pytest_runtest_makereport` hook을 `hookwrapper`로 감싸 `call`/`setup` 단계 어디에서 실패하든 드라이버를 추출해 스크린샷을 저장합니다. 이미지를 디스크(`reports/screenshots/`)와 Allure attach **양쪽에 동시 기록**해, Jenkins 빌드가 끝난 후에도 증거가 보존됩니다.

**왜 이 방식인가.** 원격 CI에서 실패하면 로컬에서 재현하기 전까지 원인을 모르는 상황이 흔합니다. `authenticated_driver` 우선 → `driver` 폴백 순으로 드라이버를 찾고, `item.nodeid`를 슬래시/콜론/백슬래시까지 안전 문자열로 치환해 OS 무관한 파일명을 생성합니다.

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

### fixture scope의 의식적 분리

- `auth_token` → **`scope="session"`**: API 트랙 전체에서 1회 발급. `AUTH_TOKEN` 환경변수 우선, 없으면 OTP 로그인 API 폴백
- `api_session` → **`scope="function"`**: 테스트별 헤더·연결 격리 후 close
- `driver` / `authenticated_driver` → **`scope="function"`**: UI 테스트 간 상태 누수 방지

자원별 비용과 격리 요구를 따로 판단해, `session`/`function`을 혼용하는 결정을 내렸습니다.

---

## 로컬 실행 방법

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. 환경 변수 설정

`.env.example`을 복사해 `.env`를 생성하고 실제 값을 입력합니다.

```bash
cp .env.example .env
```

```env
# UI 테스트 및 API 인증 공통 계정 (로그인 API로 토큰 자동 발급)
TEST_USER_ID=your_email@example.com
TEST_USER_PW=your_password

# (선택) 이미 발급받은 토큰이 있다면 우선 사용
AUTH_TOKEN=your_bearer_token

# API 엔드포인트
BASE_API_URL=https://your-api-domain.com

# (선택) 파일 다운로드 경로 (미설정 시 ~/Downloads 사용)
DOWNLOAD_DIR=/path/to/download/directory
```

### 3. 테스트 실행

```bash
# UI 테스트 실행 (slow 제외 — PR 빠른 피드백용)
pytest -m "ui and not slow" --tb=short -v

# API 테스트 실행
pytest -m api --tb=short -v

# 특정 파일 실행
pytest tests/ui/test_message_send.py -v
```

### 4. Allure 리포트 확인

```bash
allure serve allure-results
```

### 5. CI 실행

**Jenkins** — `Jenkinsfile` 기반 Declarative Pipeline으로 UI · API 테스트를 순차 실행하고 Allure Report를 자동 생성합니다. `AUTH_TOKEN`은 Jenkins Credentials (Secret text)에 등록해 주입하며, 코드에는 노출되지 않습니다.

**GitHub Actions** — `.github/workflows/qa.yml`은 `main` · `develop` 브랜치 push/PR 시 API 테스트를 ubuntu-latest에서 자동 실행합니다.

---

## 테스트 결과

| 구분 | TC 수 | 결과 |
|---|---|---|
| UI (TS-001 ~ TS-005) | 14 | **13 passed · 1 xfail** (TC_009: 다운로드 미저장 버그) |
| API (TS-006) | 4 | **4 passed** |
| **총계** | **18** | **17 passed · 1 xfail · 0 failed** |

### Allure 리포트 구성

- **환경 정보**: Python 버전, OS, Browser, Target URL, Git Commit, Build Number (`pytest_sessionstart`에서 `environment.properties` 자동 생성)
- **4계층 트리**: `epic("AI Helpy Chat") → feature("메시지 전송") → story("TS-001 · …") → step("[TC_001] …")`
- **실패 첨부**: 모든 실패 케이스에 자동 스크린샷
- **xfail 첨부**: TC_009의 재현 스크린샷 + GIF(`docs/bugs/TC_009/`)와 `@allure.issue` 링크

### 발견 결함

| ID | 시나리오 | 현상 | 추적 방식 |
|----|---|---|---|
| TC_009 | TS-004 플러스 메뉴 | 다운로드 응답이 디스크에 저장되지 않음 | `xfail(strict=True)` + `@allure.issue` + 재현 증거(스크린샷·GIF) |

---

## 문서

- [버그 리포트](docs/bug-report.md) — 테스트 중 발견된 결함 5건 정리 (BUG-005: 이미지 다운로드 미동작, xfail 처리)
- [트러블슈팅 기록](docs/troubleshooting.md) — 자동화 구축 중 발생한 이슈 13건 정리
- [테스트 케이스 목록](docs/test_cases.csv) — TC/TS 전체 목록 (노션 DB 연동용)

---

## 향후 개선 로드맵

- `ChatPage`를 `ChatInputComponent` / `PlusMenuComponent` / `LnbComponent`로 분리하는 **Component Object Pattern** 도입
- 인증 음성(negative) 케이스 확장 — 만료 토큰, 스코프 부족, 권한 미보유

---

> 본 프로젝트는 **테스트 시간 = 비용**, **실패는 디버깅 가능해야 한다**, **자동화 ≠ 통과율 100%**, **운영 환경을 의식한다**는 네 가지 원칙으로 설계되었습니다.

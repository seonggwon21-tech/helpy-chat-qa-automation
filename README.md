# HelpyChat QA Automation

> AI 채팅 서비스(qaproject.elice.io)의 채팅 UI·API를 **Selenium + pytest**로 자동화한 QA 포트폴리오
> — 총 **20 TC** · 크로스 브라우저 3종 · Jenkins + GitHub Actions 이중 CI

![Python](https://img.shields.io/badge/Python-3.14-blue?logo=python&logoColor=white)
![pytest](https://img.shields.io/badge/pytest-8.x-0A9EDC?logo=pytest&logoColor=white)
![Selenium](https://img.shields.io/badge/Selenium-4.x-43B02A?logo=selenium&logoColor=white)
![Allure](https://img.shields.io/badge/Allure-Report-FF6B6B?logo=qameta&logoColor=white)
![CI](https://img.shields.io/badge/CI-Jenkins%20%2B%20GitHub%20Actions-D24939?logo=jenkins&logoColor=white)
[![CI](https://github.com/seonggwon21-tech/helpy-chat-qa-automation/actions/workflows/qa.yml/badge.svg)](https://github.com/seonggwon21-tech/helpy-chat-qa-automation/actions/workflows/qa.yml)

---

## 핵심 성과

| 테스트 | 결과 | 버그 | CI | 브라우저 |
|:---:|:---:|:---:|:---:|:---:|
| **20 TC** (UI 14·API 6) | **18 passed · 1 skip · 1 xfail · 0 fail** | **5건 추적** | **2종** | **3종** |

**핵심 기능**

- **SSO 로그인 5~8초 제거** — CDP 쿠키 주입(`Network.setCookie`) + 30분 TTL 캐싱으로 매 테스트 반복되던 인증 대기를 제거. 캐시 만료 시 자동 재로그인하는 self-healing 구조 *(TC당 5~8초 → 누적 수 분 단축)*
- **flaky test 원천 차단** — `visibility → scrollIntoView → clickable → JS fallback` 4단계 방어적 클릭. sleep 남발 대신 인터셉트·스테일 예외 타입만 선별 폴백해 실제 결함을 가리지 않음
- **버그 수정 자동 감지** — 알려진 버그를 skip이 아닌 `xfail(strict=True)`로 파이프라인에 유지 → 수정되면 XPASS로 빌드가 실패해 회귀/수정을 자동 포착
- **크로스 브라우저 1-옵션 전파** — `--browser all` 하나로 Chrome·Edge·Firefox에 전체 테스트 자동 파라미터화 (Firefox CDP 미지원은 표준 API 폴백)
- **UI 변경에 강한 구조** — POM + Component Object Pattern으로 화면이 바뀌어도 수정 범위를 컴포넌트 1개로 한정

> 설계 의도·코드 레벨 상세는 **[주요 구현 13선 →](docs/implementation.md)**

---

## 테스트 설계 기준

테스트 케이스는 임의로 늘리지 않고, **요구사항을 분해 → 기법 적용 → 우선순위**의 일관된 기준으로 도출했습니다. 어떤 설계 방식을 어디에 적용했는지는 다음과 같습니다.

| 설계 방식 | 적용 위치 (실제 TC) |
|---|---|
| **요구사항·기능 분해** | 서비스를 6개 기능 영역(메시지 전송·새 대화·입력·+메뉴·LNB·API)으로 나눠 영역별로 누락 없이 도출 |
| **동등분할 / 경계값** | 빈 입력창 전송 비활성화(TC_004), 웹검색 응답 충분성 `len > 50`(TC_011) |
| **정상 / 예외(네거티브)** | 정상 전송→응답(TC_001) ↔ 인증 헤더 없이 401/403(TC_018), Shift+Enter 미전송(TC_005) |
| **상태 전이·지속성** | 새로고침 후 LNB 유지(TC_013), 삭제 반영(TC_014), 기존 대화 복원(TC_003) |
| **계층 분리** | UI 사용자 시나리오 14 / API 계약 검증 6 |
| **리스크 우선순위** | 핵심 채팅 플로우(송수신·새 대화) 우선, 부가 기능(이미지·PPT·웹검색) 후순위 |

각 TC는 **단일 검증 목적 + 측정 가능한 기대/실제 결과**로 작성했습니다(예: `입력창 value == ""`).

> 설계 기준과 **20개 TC 전체 목록**(기능 영역별·검증 항목·결과)은 **[테스트 케이스 설계 & 목록 →](docs/test-cases.md)**

---

## 데모

**테스트 코드 & 실행**

![Test Run Demo](docs/images/demo_test_run.gif)

**실행 결과 — Jenkins CI (빌드 성공 · 실패 0)**

![Jenkins Build Success](docs/images/jenkins-success.png)

---

## 기술 스택

| 분류 | 사용 기술 |
|---|---|
| 언어 · 프레임워크 | Python 3.14 · pytest 8 (fixture scope, marker, 브라우저 파라미터화) |
| UI 자동화 | Selenium 4 + CDP · **POM + Component Object Pattern** |
| 크로스 브라우저 | Chrome · Edge · Firefox (`--browser` 옵션) |
| API 자동화 | requests (`Session` 재사용, negative 케이스) |
| 리포팅 | Allure (epic/feature/story/step 4계층 + 실패 스크린샷) |
| 품질 · CI/CD | Ruff(Lint 게이트) · Jenkins · GitHub Actions (Lint → API → UI) |
| 환경 · 로깅 | python-dotenv · Python logging |

> 각 기술의 선택 이유와 아키텍처는 **[아키텍처 & 테스트 구성 →](docs/architecture.md)**

---

## 실행 방법

```bash
# 1. 의존성 설치
pip install -r requirements.txt

# 2. 환경 변수 설정 (.env.example 복사 후 실제 값 입력)
cp .env.example .env
#   TEST_USER_ID / TEST_USER_PW / BASE_UI_URL / AUTH_TOKEN / BASE_API_URL

# 3. 테스트 실행
pytest -m "ui and not slow" -v        # UI (PR 빠른 피드백)
pytest --browser all -m ui            # Chrome·Edge·Firefox 동시
pytest -m api -v                      # API

# 4. Allure 리포트
allure serve allure-results
```

> CI: `main`·`develop` push 시 GitHub Actions가 **Lint → API → UI** 3-job 자동 실행, Jenkins는 UI·API 분리 실행 + Allure publish.

---

## 상세 문서

| 문서 | 내용 |
|---|---|
| [아키텍처 & 테스트 구성](docs/architecture.md) | 프로젝트 구조, TS/TC 체계, 실행 결과·크로스 브라우저 매트릭스, Allure 구성 |
| [주요 구현 13선](docs/implementation.md) | Component Object Pattern, CDP 인증 우회, 방어적 클릭, xfail 추적 등 설계·코드 상세 |
| [버그 리포트 (5건)](docs/bug-report.md) | 테스트 중 발견한 결함 정리 |
| [트러블슈팅 (21건)](docs/troubleshooting.md) | 자동화 구축 중 해결한 이슈 기록 |
| [테스트 케이스 설계 & 목록](docs/test-cases.md) | TC 설계 기준 6축 + 20개 TC 전체 목록(기능 영역별·검증 항목·결과) |
| [테스트 케이스 원본 데이터](docs/test_cases.csv) | TC/TS 전체 목록 (CSV) |

---

## 프로젝트 배경 & 회고

> 본 레포는 5인 팀 GitLab 프로젝트에서 제가 담당한 영역(**채팅 UI 자동화 · 프레임워크 설계 전반**)을 개인 포트폴리오로 정리한 것입니다. 대상은 엘리스 AI 채팅 서비스(qaproject.elice.io)이며, 메시지 전송·파일 업로드·대화 목록 관리 등 핵심 흐름과 API 인증 negative 케이스를 검증합니다.

**Claude AI를 적극 활용해** 설계·구현 전 과정을 진행했습니다. 다만 테스트 케이스 수를 늘리기보다, *왜 이렇게 짜야 하는지*를 이해하면서 만드는 데 더 많은 시간을 썼습니다 — Component Object Pattern 도입도, fixture scope를 `session`/`function`으로 나눈 것도, 재현 가능한 버그를 skip이 아닌 xfail로 남긴 것도 같은 이유에서였습니다.

가장 기억에 남는 건 크로스 브라우저였습니다. Firefox를 추가하자 Chrome에서 통과하던 테스트들이 조용히 깨졌습니다 — 팝오버 렌더링 타이밍이 미묘하게 느렸고(고정 sleep → 조건부 대기), 다운로드는 `.part` 임시 확장자를 따로 처리해야 했으며, Chrome에서 쓰던 CDP 명령은 Firefox에서 아예 동작하지 않아 `FirefoxProfile preferences`로 방향을 바꿔야 했습니다. 브라우저 하나를 더했을 뿐인데 같은 코드가 다르게 동작하는 걸 직접 마주하니, '크로스 브라우저 호환성'이라는 말이 비로소 와닿았습니다.

<details>
<summary>테스트를 만들며 세운 원칙</summary>

- **테스트 시간 = 비용** — 반복되는 로그인 대기 같은 낭비는 캐싱으로 제거
- **실패는 디버깅 가능해야 한다** — Allure + logging + 자동 스크린샷으로 "왜 실패했는지"를 결과로 남김
- **자동화 ≠ 통과율 100%** — 버그는 xfail로 드러내고, negative 케이스로 거부 동작까지 검증
- **운영 환경을 의식한다** — headless·CI 환경에서도 동일하게 동작하도록 설계

</details>

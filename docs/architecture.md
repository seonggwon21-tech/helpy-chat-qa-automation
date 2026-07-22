# 아키텍처 & 테스트 구성

> 프로젝트 구조, 테스트 케이스 체계, 실행 결과 상세를 정리했습니다.
> README로 돌아가기 → [../README.md](../README.md) · 주요 구현 상세 → [implementation.md](implementation.md)

## 프로젝트 구조

```
helpy-chat-qa-automation/
├── config/
│   └── config.py              # URL, 대기 시간 등 전역 상수 (BASE_UI_URL 환경변수 오버라이드 가능)
├── pages/                     # Page Object Model + Component Object Pattern
│   ├── base_page.py           # 방어적 클릭/입력 + @allure.step 자동 데코레이션
│   ├── login_page.py          # SSO 로그인 흐름
│   ├── signup_page.py         # 약관 동의 후처리
│   ├── chat_page.py           # 파사드(Facade) — 세 컴포넌트 조합 + wait_up_to()
│   └── components/            # Component Object Pattern
│       ├── chat_input_component.py   # 채팅 입력·전송·AI 응답 대기
│       ├── plus_menu_component.py    # + 버튼 메뉴(파일·이미지·PPT·웹 검색), upload_file(), select_plus_menu_item()
│       └── lnb_component.py          # LNB 대화 목록 조회·삭제, wait_for_lnb_loaded(), get_lnb_hrefs()
├── tests/
│   ├── ui/
│   │   ├── test_message_send.py      # TS-001
│   │   ├── test_new_chat.py          # TS-002
│   │   ├── test_input_features.py    # TS-003
│   │   ├── test_plus_menu.py         # TS-004
│   │   └── test_lnb_management.py   # TS-005
│   └── api/
│       └── test_community_api.py    # TS-006 (TC_015~020, negative 케이스 포함)
├── test_data/
│   └── test_upload.txt        # 파일 업로드 TC용 더미 파일
├── utils/
│   └── download.py            # 다운로드 완료 감지 (Chrome .crdownload / Firefox .part 병행)
├── docs/
│   ├── bugs/
│   │   └── TC_009/            # 버그 재현 GIF 및 스크린샷
│   ├── images/                # README 데모 이미지
│   ├── test_cases.csv         # TC/TS 전체 목록
│   ├── bug-report.md          # 발견 결함 5건
│   ├── troubleshooting.md     # 트러블슈팅 기록 (21건)
│   ├── architecture.md        # (이 문서) 구조 · 테스트 구성 · 결과
│   └── implementation.md      # 주요 구현 13선
├── reports/                   # 실패 시 자동 저장되는 스크린샷
├── allure-results/            # Allure raw 데이터 (environment.properties 포함)
├── .github/
│   └── workflows/
│       ├── lint.yml           # GitHub Actions — push 게이트 (Ruff 정적 검사)
│       └── e2e.yml            # GitHub Actions — 수동 트리거 (API·UI, 대상 서비스 접속 필요)
├── conftest.py                # Fixture 정의 (크로스 브라우저, 인증, 쿠키 캐싱, 실패 훅)
├── ruff.toml                  # Ruff 정적 분석 설정 (E/F/W/I rules, isort)
├── requirements.txt           # 런타임 의존성
├── requirements-dev.txt       # 개발·CI 전용 도구 (Ruff)
├── Jenkinsfile
├── pytest.ini
├── .env.example               # 환경 변수 템플릿
└── .env                       # 자격증명 (gitignore 처리, 직접 생성 필요)
```

## 테스트 구성

UI 5개 시나리오 14개 TC + API 1개 시나리오 6개 TC, **총 20개 TC**.

| TS ID | 테스트 스위트 | TC | 설명 |
|---|---|---|---|
| TS-001 | 메시지 전송 E2E | TC_001 | 사용자 메시지 입력 → 전송 → AI 응답 노드 확인까지 단일 E2E 검증 |
| TS-002 | 새 대화 전환 | TC_002~003 | 새 대화 클릭 후 화면 초기화 확인, LNB에서 기존 대화 복원 확인 |
| TS-003 | 입력창 동작 | TC_004~006 | 빈 입력 차단, Shift+Enter 줄바꿈(미전송), Enter 전송 후 AI 응답 출력 |
| TS-004 | + 버튼 메뉴 | TC_007~011 | 파일 업로드 칩 노출, 이미지·PPT 생성, 웹 검색 (**TC_009는 `xfail(strict=True)`로 버그 추적**) |
| TS-005 | LNB 대화 목록 관리 | TC_012~014 | 가상화 환경에서 새로고침 보존·삭제를 href 기준으로 검증 |
| TS-006 | 에이전트 API & 인증 | TC_015~020 | 에이전트 목록·수·상세 조회 + 미인증·유효하지 않은 토큰·잘못된 인증 스킴 음성(negative) 케이스 |

> 전체 TC 목록: [test_cases.csv](test_cases.csv)
> `pytest -m "ui and not slow"`로 PR 단위 빠른 피드백 루프를 지원합니다.

## 테스트 결과

| 구분 | TC 수 | 결과 |
|---|---|---|
| UI (TS-001 ~ TS-005) | 14 | **12 passed · 1 skipped(CI headless) · 1 xfail** (TC_009: 다운로드 미저장 버그) |
| API (TS-006) | 6 | **6 passed** |
| **총계** | **20** | **18 passed · 1 skipped · 1 xfail · 0 failed** |

### 크로스 브라우저 호환성

`--browser all` 실행 기준입니다. **Chrome · Edge · Firefox를 로컬에서 직접 실행해 검증**했고, 브라우저별 이슈(Firefox CDP 미지원 · 팝오버 타이밍 · 다운로드 확장자)를 해결했습니다. CI(GitHub Actions)는 Chrome으로 상시 실행합니다.

| TS | 주요 TC | Chrome | Edge | Firefox | 비고 |
|---|---|:---:|:---:|:---:|---|
| TS-001~003 | TC_001~006 메시지·입력 | ✅ | ✅ | ✅ | |
| TS-004 | TC_007 + 메뉴 노출 | ✅ | ✅ | ✅ | |
| TS-004 | TC_008 파일 업로드 | ✅ | ✅ | ✅ | send_keys 풀패스로 OS 다이얼로그 우회 |
| TS-004 | TC_009 이미지 다운로드 | xfail | xfail | xfail | 앱 버그, 브라우저 무관 |
| TS-004 | TC_010 PPT 생성 | ✅ | ✅ | ✅ | `.part` 감지로 Firefox 다운로드 완료 판별 |
| TS-004 | TC_011 웹 검색 | ✅ | ✅ | ✅ | |
| TS-005 | TC_012~014 LNB 관리 | ✅ | ✅ | ✅ | `select_plus_menu_item` 팝오버 대기 적용 |
| TS-006 | TC_015~020 API | ✅ | — | — | 브라우저 독립 (requests 기반) |

> Firefox 쿠키 주입은 `add_cookie` 폴백, 다운로드 설정은 `options.set_preference`로 처리해 CDP 의존 없이 동등하게 동작합니다.

### Allure 리포트 구성

- **환경 정보**: Python 버전, OS, 동적 브라우저명(`--browser` 옵션 반영), Target URL, Git Commit, Build Number
- **4계층 트리**: `epic("AI Helpy Chat") → feature("메시지 전송") → story("TS-001 · …") → step("[TC_001] …")`
- **실패 첨부**: 모든 실패 케이스에 자동 스크린샷
- **xfail 첨부**: TC_009의 재현 스크린샷 + GIF(`docs/bugs/TC_009/`)와 `@allure.issue` 링크

### 발견 결함

| ID | 시나리오 | 현상 | 추적 방식 |
|----|---|---|---|
| TC_009 | TS-004 플러스 메뉴 | 다운로드 응답이 디스크에 저장되지 않음 | `xfail(strict=True)` + `@allure.issue` + 재현 증거(스크린샷·GIF) |

> 전체 결함 목록: [bug-report.md](bug-report.md) (5건)

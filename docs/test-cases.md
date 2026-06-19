# 테스트 케이스 — 설계 기준 & 전체 목록

> AI Helpy Chat (qaproject.elice.io) · 총 **20 TC** (UI 14 · API 6)
> 18 passed · 1 skip · 1 xfail · 0 fail

테스트 케이스는 임의로 늘리지 않고, **요구사항 분해 → 기법 적용 → 우선순위**의 일관된 기준으로 도출했습니다.
원본 데이터는 [`test_cases.csv`](test_cases.csv), 설계·코드 상세는 [주요 구현 13선](implementation.md) 참고.

---

## 1. 어떻게 만들었나 — 설계 기준 6축

| 설계 방식 | 적용 위치 (실제 TC) |
|---|---|
| **요구사항·기능 분해** | 서비스를 6개 기능 영역(메시지 전송·새 대화·입력·+메뉴·LNB·API)으로 나눠 영역별로 누락 없이 도출 |
| **동등분할 / 경계값** | 빈 입력창 전송 비활성화(TC_004), 웹검색 응답 충분성 `len > 50`(TC_011) |
| **정상 / 예외(네거티브)** | 정상 전송→응답(TC_001) ↔ 인증 헤더 없이 401/403(TC_018), Shift+Enter 미전송(TC_005) |
| **상태 전이·지속성** | 새로고침 후 LNB 유지(TC_013), 삭제 반영(TC_014), 기존 대화 복원(TC_003) |
| **계층 분리** | UI 사용자 시나리오 14 / API 계약 검증 6 |
| **리스크 우선순위** | 핵심 채팅 플로우(송수신·새 대화) 우선, 부가 기능(이미지·PPT·웹검색) 후순위 |

각 TC는 **단일 검증 목적 + 측정 가능한 기대/실제 결과**로 작성했습니다 (예: `입력창 value == ""`).

---

## 2. 무엇이 있나 — 전체 20 TC

### TS-001 · 메시지 전송 (UI)

| TC ID | 테스트 케이스 | 검증 항목 | 결과 |
|---|---|---|:---:|
| TC_001 | 전송 버튼 클릭 시 입력창 초기화 및 AI 응답 출력 | 입력창 `value == ""` / AI 응답 텍스트 존재 | ✅ PASS |

### TS-002 · 새 대화 (UI)

| TC ID | 테스트 케이스 | 검증 항목 | 결과 |
|---|---|---|:---:|
| TC_002 | 새 대화 버튼 클릭 후 빈 화면 전환 | URL 변경 / 입력창 초기화 / 이전 메시지 미표시 | ✅ PASS |
| TC_003 | LNB에서 기존 대화 클릭 후 내용 복원 | LNB 항목 존재 / 클릭 후 메시지 표시 | ✅ PASS |

### TS-003 · 메시지 입력 (UI)

| TC ID | 테스트 케이스 | 검증 항목 | 결과 |
|---|---|---|:---:|
| TC_004 | 빈 입력창에서 전송 버튼 비활성화 *(경계값)* | SEND 버튼 `disabled` 속성 존재 | ✅ PASS |
| TC_005 | Shift+Enter 입력 시 줄바꿈만, 전송 미동작 *(예외)* | `value`에 줄바꿈 포함 / AI 응답 요소 0개 | ✅ PASS |
| TC_006 | Enter 키 전송 후 AI 응답 출력 | AI 응답 텍스트 존재 | ✅ PASS |

### TS-004 · + 버튼 메뉴 (UI)

| TC ID | 테스트 케이스 | 검증 항목 | 결과 |
|---|---|---|:---:|
| TC_007 | + 버튼 클릭 시 4종 메뉴 노출 | 파일 업로드·이미지 생성·PPT 생성·웹 검색 메뉴 표시 | ✅ PASS |
| TC_008 | 파일 업로드 후 입력창 첨부 칩 노출 | file input 경로 전달 / 첨부 칩 `is_displayed` | ⏭️ SKIP *(CI)* |
| TC_009 | 이미지 생성 후 다운로드 버튼 클릭 시 파일 저장 | 이미지 응답 노출 / 다운로드 후 파일 개수 증가 | ⚠️ XFAIL *(앱 버그)* |
| TC_010 | PPT 생성 후 결과 노출 및 다운로드 | PPT 결과 버튼 노출 / 다운로드 후 파일 개수 증가 | ✅ PASS |
| TC_011 | 웹 검색 후 AI 응답 충분성 *(경계값)* | AI 응답 텍스트 존재 / `len > 50` | ✅ PASS |

### TS-005 · LNB 대화 목록 (UI)

| TC ID | 테스트 케이스 | 검증 항목 | 결과 |
|---|---|---|:---:|
| TC_012 | 메시지 전송 후 LNB에 새 항목 추가 | 전송 후 LNB href 셋 1개 증가 | ✅ PASS |
| TC_013 | 페이지 새로고침 후 LNB 목록 유지 *(지속성)* | 새로고침 전후 href 셋 동일 | ✅ PASS |
| TC_014 | LNB 첫 항목 삭제 후 목록에서 제거 *(상태 전이)* | 삭제 대상 href가 LNB에서 사라짐 | ✅ PASS |

### TS-006 · API 계약 검증

| TC ID | 테스트 케이스 | 검증 항목 | 결과 |
|---|---|---|:---:|
| TC_015 | `GET /agent` 200 및 리스트 구조 | status 200 / 응답 타입 `list` / `len > 0` | ✅ PASS |
| TC_016 | `GET /agent/count` 200 및 count 정수 | status 200 / count 타입 `int` / `count >= 0` | ✅ PASS |
| TC_017 | `GET /agent/{id}` 200 및 상세 구조 | status 200 / 응답 타입 `dict` / id 일치 | ✅ PASS |
| TC_018 | 인증 헤더 없이 요청 시 거부 *(네거티브)* | status `401` 또는 `403` | ✅ PASS |
| TC_019 | 유효하지 않은 토큰(만료·변조 JWT)으로 요청 시 거부 *(네거티브)* | status `401`/`403`/`409` (게이트웨이가 403을 409로 래핑 → inner `_result.status_code == 403` 확인) | ✅ PASS |
| TC_020 | 잘못된 인증 스킴(Basic)으로 요청 시 거부 *(네거티브)* | status `401` 또는 `403` | ✅ PASS |

---

> ⏭️ **TC_008 (SKIP)** — 파일 업로드는 헤드리스 CI 환경에서 OS 파일 선택창 제약으로 file input이 노출되지 않아 `@pytest.mark.skipif(CI)`로 **CI에서만 skip**, 로컬에서는 정상 통과합니다. (CI 결과 표기 `1 skip`이 이 케이스)
>
> ⚠️ **TC_009 (XFAIL)** — 이미지 생성 결과 다운로드 미저장은 앱 자체 결함으로, skip이 아닌 `@pytest.mark.xfail(strict=True)`로 파이프라인에 유지해 수정 시 자동 감지되게 했습니다. 상세는 [버그 리포트 BUG-005](bug-report.md) 참고.
>
> → CI 기준 결과: **18 passed · 1 skip(TC_008) · 1 xfail(TC_009) · 0 fail** = 20 TC

---

## 3. 테스트 함수 ↔ TC 매핑 (13 함수 = 20 TC)

pytest 함수는 **13개**, 검증하는 테스트 케이스는 **20개**입니다. 연속된 사용자 흐름은 상태를 공유하는 **하나의 시나리오 함수**로 묶어, 흐름 안에서 여러 TC를 단계(`allure.step`)로 검증했기 때문입니다. (예: 입력 → 전송 → 응답을 한 함수에서 순차 확인)

| 테스트 함수 | 검증 TC | 비고 |
|---|---|---|
| `test_send_via_button_shows_ai_response` | TC_001 | |
| `test_new_chat_and_history_preserved` | TC_002, TC_003 | 새 대화 → 기존 대화 복원 흐름 |
| `test_input_features_scenario` | TC_004, TC_005, TC_006 | 빈 입력·Shift+Enter·Enter 전송 |
| `test_plus_button_shows_all_menus` | TC_007 | |
| `test_file_upload_via_plus_menu` | TC_008 | CI skip |
| `test_image_creation_via_plus_menu` | TC_009 | xfail (앱 버그) |
| `test_ppt_creation_via_plus_menu` | TC_010 | |
| `test_web_search_via_plus_menu` | TC_011 | |
| `test_lnb_lifecycle` | TC_012, TC_013, TC_014 | 추가 → 유지 → 삭제 라이프사이클 |
| `test_agent_read_flow` | TC_015, TC_016, TC_017 | 목록 → 수 → 상세 조회 플로우 |
| `test_unauthorized_returns_401_or_403` | TC_018 | |
| `test_invalid_token_returns_auth_error` | TC_019 | |
| `test_wrong_auth_scheme_returns_401_or_403` | TC_020 | |

> 13개 함수(UI 9 · API 4) → 20개 TC(UI 14 · API 6). 시나리오 통합 함수 4개(`new_chat`·`input_features`·`lnb_lifecycle`·`agent_read_flow`)가 여러 TC를 묶어 함수 수와 TC 수의 차이를 만듭니다.

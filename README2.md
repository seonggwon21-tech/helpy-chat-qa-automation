# 2026-05-27 작업 기록

기존 포트폴리오(`README.md`)에 추가된 내용을 별도로 정리한 문서입니다.

---

## 1. Component Object Pattern 도입

### 변경 전
`ChatPage` 단일 클래스가 채팅 입력·플러스 메뉴·LNB 관리를 모두 담당 → SRP 위반.

### 변경 후
`pages/components/` 디렉터리를 신설하고 역할별로 분리.

```
pages/
├── chat_page.py               # 파사드(Facade) — 컴포넌트를 조합해 노출
└── components/
    ├── chat_input_component.py   # 채팅 입력·전송·AI 응답 대기
    ├── plus_menu_component.py    # + 버튼 메뉴(파일·이미지·PPT·웹 검색)
    └── lnb_component.py          # LNB 대화 목록 조회·삭제
```

`ChatPage`는 세 컴포넌트 인스턴스를 공개 속성으로 노출하고, `send_message()` / `wait_for_ai_response()` 처럼 fixture에서 자주 쓰이는 액션만 위임 메서드로 래핑합니다.

```python
# 테스트에서 컴포넌트에 직접 접근
chat_page = ChatPage(driver)
chat_page.chat_input.start_new_chat()
chat_page.plus_menu.open_menu()
hrefs = chat_page.lnb.get_chat_hrefs()   # JS 원자 수집
```

**`LnbComponent.get_chat_hrefs()`** — LNB 항목 href를 JavaScript로 한 번에 수집해 `StaleElementReferenceException`을 구조적으로 방지합니다 (트러블슈팅 #12·#14 동일 패턴 컴포넌트 수준으로 흡수).

---

## 2. API Negative 테스트 추가 (TC_019, TC_020)

기존 `TestChatroomAuth`에 인증 음성(negative) 케이스 2개를 추가해 총 4개 API 케이스로 확장.

| TC | 제목 | 검증 내용 |
|----|------|----------|
| TC_018 | 미인증 요청 | 인증 헤더 없이 요청 시 401/403 반환 |
| **TC_019** | 유효하지 않은 토큰 | 서명 불일치 JWT 사용 시 인증 거부 |
| **TC_020** | 잘못된 인증 스킴 | `Basic` 스킴 사용 시 401/403 반환 |

**TC_019 특이사항**: 이 API는 백엔드 인증 실패(403)를 게이트웨이가 **409로 래핑**해 반환합니다. 401/403/409 모두 인증 거부로 처리하되, 409일 경우 응답 body의 `_result.status_code == 403`을 추가 검증해 실제 인증 실패임을 확인합니다 (트러블슈팅 #16 참고).

---

## 3. Ruff 정적 분석 CI 도입

현업 시니어 피드백: *"CI/CD 잘 구성 해놓으셨네요. 정적분석 도구만 붙여 놓으면 충분하실듯."*

### 추가 파일

**`ruff.toml`**
```toml
target-version = "py311"

[lint]
select = ["E", "F", "W", "I"]   # pycodestyle · pyflakes · isort
ignore = [
    "E501",  # line too long — Selenium 로케이터·URL 예외
    "E221",  # multiple spaces before operator — 로케이터 컬럼 정렬 허용
]

[lint.isort]
known-first-party = ["pages", "config", "utils"]
```

**`requirements-dev.txt`**
```
ruff>=0.4.0
```

**`.github/workflows/qa.yml`** — Lint job 추가
```yaml
lint:
  name: Lint (Ruff)
  steps:
    - run: pip install -r requirements-dev.txt --quiet
    - run: ruff check .
```

### GitHub Actions 파이프라인 (변경 후)

```
push → Lint (Ruff) → API Tests → UI Tests
```

### 수정된 lint 오류 (8건)

| 규칙 | 파일 | 내용 |
|------|------|------|
| I001 × 6 | config.py, conftest.py, base_page.py, chat_input_component.py, plus_menu_component.py, login_page.py | 표준 라이브러리 / 서드파티 / 자체 모듈 사이 빈 줄 추가 + 알파벳 순 정렬 |
| F401 | conftest.py | `DEFAULT_API_TIMEOUT` 미사용 import 제거 |
| F541 | conftest.py | `f"Browser=Chrome"` → `"Browser=Chrome"` |

---

## 4. CI 복구

### AUTH_TOKEN 방식 재복귀
`/login/otp` 엔드포인트가 `otp` 필드를 다시 필수로 변경해 자동 로그인 재불가.  
`auth_token` fixture를 `AUTH_TOKEN` 환경변수 전용으로 단순화하고, `qa.yml`에 secret 전달 추가.  
→ 트러블슈팅 #15 참고.

### TC_012 StaleElementReferenceException 수정
LNB 동적 갱신 중 `find_elements` + `get_attribute` 조합이 stale 오류를 유발.  
`LnbComponent.get_chat_hrefs()` JS 방식으로 교체.  
→ 트러블슈팅 #14 참고.

---

## 5. 트러블슈팅 신규 기록

| # | 현상 | 원인 | 해결 |
|---|------|------|------|
| **#14** | TC_012 LNB 신규 항목 대기 중 `StaleElementReferenceException` | `long_wait.until` 람다 재진입 시 LNB 재렌더링으로 요소 참조 무효화 | JS `execute_script`로 href 원자 수집 (`LnbComponent.get_chat_hrefs()`) |
| **#15** | GitHub Actions API Tests 422 오류 재발 | `/login/otp` 엔드포인트가 `otp` 필드를 다시 필수로 변경 | `auth_token` fixture AUTH_TOKEN 전용으로 단순화, GitHub Secrets 등록 |
| **#16** | TC_019 유효하지 않은 토큰 → 409 응답 | 이 API는 백엔드 인증 실패(403)를 API 게이트웨이가 409로 래핑해 반환 | 409도 인증 거부로 허용, body 내부 `_result.status_code == 403` 추가 검증 |

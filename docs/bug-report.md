# Bug Report

> 프로젝트: AI Helpy Chat (qaproject.elice.io)  
> 테스트 환경: Windows 11, Chrome, Python 3.14.4  
> 작성일: 2026-05-20

---

## BUG-001 · LNB 대화 삭제 후 카운트 검증 오작동

| 항목 | 내용 |
|---|---|
| **심각도** | Medium |
| **우선순위** | Medium |
| **상태** | 확인됨 (테스트 로직으로 우회) |
| **발견 경위** | TC_014 자동화 테스트 실행 중 |

**환경**
- URL: `https://qaproject.elice.io/ai-helpy-chat`
- 브라우저: Chrome

**재현 단계**
1. 메시지를 전송하여 LNB에 대화 항목 생성
2. LNB 첫 번째 항목에 hover → `...` 버튼 클릭
3. 삭제 → 확인 다이얼로그에서 삭제 확정
4. 삭제 전후 LNB 항목 수 비교

**기대 결과**  
삭제 후 LNB 항목 수가 1 감소해야 함.

**실제 결과**  
LNB가 lazy-load 방식으로 하단 항목을 자동 보충하여 총 카운트가 삭제 전과 동일하게 유지됨.

**비고**  
삭제된 항목의 URL이 LNB에서 사라졌는지 확인하는 방식으로 검증 로직 변경하여 우회.

---

## BUG-002 · AI 응답 생성 시간 기본 타임아웃(10초) 초과

| 항목 | 내용 |
|---|---|
| **심각도** | Low |
| **우선순위** | Low |
| **상태** | 확인됨 (테스트 대기 시간 조정으로 우회) |
| **발견 경위** | TC_012 자동화 테스트 실행 중 |

**환경**
- URL: `https://qaproject.elice.io/ai-helpy-chat`
- 브라우저: Chrome

**재현 단계**
1. 채팅 입력창에 메시지 입력 후 전송
2. AI 응답이 화면에 나타날 때까지 대기 (기본 대기: 10초)

**기대 결과**  
10초 이내 AI 응답이 화면에 출력되어야 함.

**실제 결과**  
서버 부하 또는 응답 길이에 따라 응답 생성이 10초를 초과하는 경우 발생.  
`TimeoutException`으로 테스트 실패.

**비고**  
해당 TC에 한해 대기 시간을 60초로 설정하여 우회.  
서비스 응답 SLA 기준이 없어 버그로 단정하기 어려우나, 성능 관점에서 모니터링 필요.

---

## BUG-003 · 로그인 셀렉터 — `name` 속성 변경으로 인한 불일치

| 항목 | 내용 |
|---|---|
| **심각도** | High |
| **우선순위** | High |
| **상태** | 수정 완료 |
| **발견 경위** | UI 테스트 사전 조건(Fixture) 실행 중 |

**환경**
- URL: `https://accounts.elice.io/accounts/signin/me`
- 브라우저: Chrome

**재현 단계**
1. `https://qaproject.elice.io` 접속
2. SSO 리다이렉트 후 로그인 폼 노출
3. `input[name='loginId']` 셀렉터로 이메일 필드 접근 시도

**기대 결과**  
셀렉터가 이메일 입력 필드를 정상적으로 찾아야 함.

**실제 결과**  
`NoSuchElementException` 발생. 실제 필드의 `name` 속성이 변경되어 셀렉터가 매칭되지 않음.

**수정 내용**  
`name` 속성 대신 `type` 속성 기반 셀렉터로 변경하여 속성값 변경에 강건하게 대응.

```python
# 수정 전
LOGIN_ID_INPUT = (By.CSS_SELECTOR, "input[name='loginId']")

# 수정 후
LOGIN_ID_INPUT = (By.CSS_SELECTOR, "input[type='email']")
```

---

## BUG-004 · `data-testid` 대소문자 불일치로 셀렉터 매칭 실패

| 항목 | 내용 |
|---|---|
| **심각도** | Medium |
| **우선순위** | Medium |
| **상태** | 수정 완료 |
| **발견 경위** | 로그인 성공 여부 검증 로직 실행 중 |

**환경**
- URL: `https://qaproject.elice.io/ai-helpy-chat`
- 브라우저: Chrome

**재현 단계**
1. 로그인 완료 후 `is_login_successful()` 호출
2. `svg[data-testid='personIcon']` 셀렉터로 요소 탐색

**기대 결과**  
로그인 성공 후 프로필 아이콘 요소가 탐색되어 `True` 반환.

**실제 결과**  
`TimeoutException` 발생 후 `False` 반환. URL은 정상이나 아이콘을 찾지 못함.

**원인**  
CSS 속성값은 대소문자를 구분하며, 실제 `data-testid` 값은 `PersonIcon`(대문자 P).

**수정 내용**

```python
# 수정 전
(By.CSS_SELECTOR, "svg[data-testid='personIcon']")

# 수정 후
(By.CSS_SELECTOR, "button > svg[data-testid='PersonIcon']")
```

---

## BUG-005 · 이미지 생성 다운로드 버튼 클릭 시 파일 미저장

| 항목 | 내용 |
|---|---|
| **심각도** | Normal |
| **우선순위** | Medium |
| **상태** | 미해결 (앱 버그) |
| **발견 경위** | TC_009 자동화 테스트 실행 중 |

**환경**
- URL: `https://qaproject.elice.io/ai-helpy-chat`
- 브라우저: Chrome / Windows 11

**재현 단계**
1. 새 대화 화면에서 `+` 버튼 클릭
2. `이미지 생성` 메뉴 선택
3. 프롬프트 입력 후 전송 (예: "고양이")
4. AI 응답에 이미지 노출 확인
5. 이미지에 hover → 다운로드 버튼 클릭

**기대 결과**  
다운로드 버튼 클릭 시 이미지 파일이 Downloads 폴더에 저장되어야 함.

**실제 결과**  
다운로드 버튼 클릭 후 아무 반응 없음. 파일이 저장되지 않음.  
60초 폴링 후 `AssertionError: [BUG] 이미지 파일이 다운로드되지 않았습니다.`

**비고**  
- 이미지 생성 및 노출 단계까지는 정상 동작
- 수동 테스트에서도 동일 증상 재현 → 앱 자체 결함으로 판단
- `@pytest.mark.xfail(strict=True)` 로 처리하여 테스트 결과에 XFAIL로 기록
- 버그 재현 GIF 및 스크린샷: `docs/bugs/TC_009/`
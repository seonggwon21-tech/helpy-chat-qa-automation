# 🤖 HelpyChat QA Automation Framework

본 프로젝트는 HelpyChat 서비스의 품질을 보증하기 위해 구축된 **End-to-End (E2E) UI 테스트 자동화 프레임워크**입니다. 
Page Object Model(POM) 디자인 패턴을 기반으로 작성되었으며, Allure 리포트 생성 및 Jira 자동 결함 트래킹 기능을 포함하여 실무와 동일한 파이프라인을 경험할 수 있도록 구성되었습니다.

---

## 🏗️ Architecture & Tech Stack
* **Language**: Python 3.10+
* **Testing Framework**: Pytest
* **Browser Automation**: Selenium WebDriver
* **Reporting**: Allure Framework
* **CI/CD Integration**: Jira REST API (Auto Bug Ticketing)

---

## 📁 Directory Structure
`helpychat-automation/`
 ├── `pages/`               # Page Object Model 클래스 모음 (UI 로케이터 및 액션)
 │    ├── `base_page.py`    # 공통 동작 (클릭, 대기, 텍스트 입력 등)
 │    ├── `chat_page.py`    # 메인 채팅 화면 조작
 │    ├── `login_page.py`   # 로그인 폼 조작
 │    └── `signup_page.py`  # 최초 온보딩(약관 동의) 조작
 ├── `tests/`               # 테스트 케이스 스크립트 모음
 │    ├── `ui/`             # E2E UI 시나리오 테스트
 │    └── `api/`            # API 정합성 테스트 (추가 확장 예정)
 ├── `.env`                 # 민감한 환경 변수 (Git 커밋 제외 대상)
 ├── `.gitignore`           # Git 추적 제외 목록 파일
 ├── `conftest.py`          # Pytest Fixture 및 Jira 연동 Hook(자동 티켓팅) 설정
 ├── `pytest.ini`           # Pytest 환경 설정 (로깅 포맷 및 Allure 수집 옵션)
 └── `README.md`            # 프로젝트 개요 및 실행 가이드

---

## 🛠️ 환경 셋팅 및 실행 가이드 (Getting Started)

본 프로젝트를 로컬 PC에서 실행하기 위해서는 파이썬 패키지 외에도 리포트 생성을 위한 추가 환경 구성이 필요합니다. 아래 순서대로 터미널에 입력하여 셋팅을 진행해 주세요.

### 1. 필수 패키지 설치
UI 자동화 제어, API 통신, 리포트 데이터 수집, 환경 변수 관리를 위한 파이썬 라이브러리들을 설치합니다.
> 아래 명령어를 복사해서 터미널에 입력하세요:
`pip install pytest selenium allure-pytest requests python-dotenv`

### 2. 환경 변수 설정 (.env)
프로젝트 최상위 경로에 `.env` 파일을 생성하고 아래 양식에 맞게 본인의 정보를 입력합니다.
⚠️ **[보안 주의]** `.env` 파일은 절대 Git에 커밋하지 마세요. 반드시 `.gitignore`에 등록해야 합니다.

`TEST_USER_ID=your_id@example.com`
`TEST_USER_PW=your_password`
`JIRA_BASE_URL=https://your-domain.atlassian.net`
`JIRA_EMAIL=your_jira_email@example.com`
`JIRA_API_TOKEN=your_jira_api_token`
`JIRA_PROJECT_KEY=YOUR_PROJECT_KEY`

### 3. Allure 리포트 환경 구성
Allure는 생성된 JSON 데이터를 시각적인 웹 리포트로 렌더링하기 위해 내부적으로 Java와 Node.js를 사용합니다.

* **① JAVA_HOME 환경 변수 등록:** PC에 Java(JDK 8 이상)가 설치되어 있고 환경 변수가 세팅되어 있어야 합니다.
* **② Allure CLI 툴 설치:** Node.js 기반으로 아래 명령어를 터미널에 입력해 전역 설치합니다.
> 아래 명령어를 복사해서 터미널에 입력하세요:
`npm install -g allure-commandline --save-dev`

---

## 🚀 How to Run (테스트 실행)

`pytest.ini`에 필수 옵션이 모두 세팅되어 있으므로, 복잡한 옵션 없이 **명령어 하나**로 전체 테스트를 실행하고 Allure 결과 데이터를 수집할 수 있습니다.

> 아래 명령어를 복사해서 터미널에 입력하세요:
`pytest`

*(참고: 특정 폴더만 단독으로 실행하고 싶을 경우 `pytest tests/ui/` 와 같이 입력합니다.)*

---

## 📊 Reporting & Issue Tracking

### 1. 테스트 결과 리포트 확인 (Allure)
테스트가 완료되면 아래 명령어를 터미널에 입력하여 웹 브라우저에 Allure 대시보드를 띄웁니다.
> 아래 명령어를 복사해서 터미널에 입력하세요:
`allure serve allure-results`

### 2. Auto Ticketing (Jira 연동)
테스트 실행 중 검증(Assertion)에 실패하거나 Timeout 에러가 발생할 경우, `conftest.py`의 Pytest Hook이 이를 감지하여 다음 액션을 자동으로 수행합니다.
1. 에러가 발생한 즉시 브라우저 스크린샷 캡처
2. 에러 로그 정제 후 지정된 Jira 보드에 버그(Bug) 티켓 자동 생성
3. 생성된 Jira 티켓에 캡처한 스크린샷 파일 직접 첨부 (Direct Attach)

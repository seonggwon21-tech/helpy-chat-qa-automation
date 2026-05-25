pipeline {
    agent any

    stages {
        stage('체크아웃') {
            steps {
                checkout scm
            }
        }

        stage('패키지 설치') {
            steps {
                bat 'C:\\Python314\\python.exe -m pip install -r requirements.txt --quiet'
            }
        }

        stage('UI 테스트 실행') {
            steps {
                bat 'C:\\Python314\\python.exe -m pytest -m "ui and not slow" --tb=short -v --junitxml=result-ui.xml --alluredir=allure-results'
            }
        }

        stage('API 테스트 실행') {
            steps {
                withCredentials([
                    string(credentialsId: 'AUTH_TOKEN', variable: 'AUTH_TOKEN')
                ]) {
                    bat 'set BASE_API_URL=https://api-community.elice.io && C:\\Python314\\python.exe -m pytest -m api --tb=short -v --junitxml=result-api.xml --alluredir=allure-results'
                }
            }
        }
    }

    post {
        always {
            junit 'result-ui.xml, result-api.xml'
            allure includeProperties: false, jdk: '', results: [[path: 'allure-results']]
        }
        failure {
            echo '테스트 실패 - reports/screenshots 폴더에서 스크린샷 확인'
        }
    }
}

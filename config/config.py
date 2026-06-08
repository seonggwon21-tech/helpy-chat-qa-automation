import os

from dotenv import load_dotenv

load_dotenv()

DEFAULT_WAIT_TIME: int = 10

# 호스트 루트만 지정 (conftest가 "/ai-helpy-chat" 경로를 덧붙임). 프로젝트 중 호스트 변경됨.
BASE_UI_URL: str = os.getenv("BASE_UI_URL", "https://qaproject.elice.io")
BASE_API_URL: str = os.getenv("BASE_API_URL", "")

TEST_USER: dict[str, str | None] = {
    "id": os.getenv("TEST_USER_ID"),
    "pw": os.getenv("TEST_USER_PW"),
}

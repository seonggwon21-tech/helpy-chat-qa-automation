import os
from dotenv import load_dotenv

load_dotenv()

DEFAULT_WAIT_TIME: int = 10
DEFAULT_API_TIMEOUT: int = 30

BASE_UI_URL: str = os.getenv("BASE_UI_URL", "https://qaproject.elice.io")
BASE_API_URL: str = os.getenv("BASE_API_URL", "")

TEST_USER: dict[str, str | None] = {
    "id": os.getenv("TEST_USER_ID"),
    "pw": os.getenv("TEST_USER_PW"),
}

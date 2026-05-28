"""다운로드 완료 감지 유틸리티."""

import time
from pathlib import Path


def wait_for_download(download_dir: Path, before_count: int, timeout: int = 60) -> bool:
    """다운로드 완료를 감지합니다.

    Chrome(.crdownload) / Firefox(.part) 임시 확장자를 병행 감지하므로
    브라우저 종류에 무관하게 동작합니다.

    Args:
        download_dir: 브라우저 다운로드 디렉터리 경로.
        before_count: 다운로드 시작 전 파일 수.
        timeout: 최대 대기 시간(초). 기본값 60.

    Returns:
        timeout 내에 다운로드가 완료되면 True, 초과하면 False.
    """
    for _ in range(timeout):
        current = list(download_dir.iterdir())
        if len(current) > before_count and not any(
            f.name.endswith((".crdownload", ".part")) for f in current
        ):
            return True
        time.sleep(1)
    return False

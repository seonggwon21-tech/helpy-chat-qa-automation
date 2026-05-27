"""
공통 로거 유틸리티.

사용 지침:
- CI 환경에서는 pytest.ini의 log_cli=true 설정과 함께 사용하면 중복 출력이 발생할 수 있습니다.
  pytest log_cli로 콘솔 출력을 일원화하는 경우, LOG_FILE 환경변수만 설정해 파일 로그를 분리하세요.
- LOG_FILE 환경변수를 설정하면 해당 경로에 파일 로그가 누적됩니다.
  예: LOG_FILE=logs/test_run.log pytest
"""

import logging
import os
from pathlib import Path


def get_custom_logger(name: str) -> logging.Logger:
    """공통 포매터가 적용된 로거를 반환합니다.

    Args:
        name: 로거 이름 (일반적으로 __name__ 전달)

    Returns:
        설정된 Logger 인스턴스

    환경변수:
        LOG_FILE: 설정 시 해당 경로의 파일에도 로그를 기록합니다.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")

        # 콘솔 핸들러
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        # 파일 핸들러 (LOG_FILE 환경변수 설정 시 활성화)
        log_file = os.getenv("LOG_FILE")
        if log_file:
            Path(log_file).parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        logger.setLevel(logging.INFO)
    return logger

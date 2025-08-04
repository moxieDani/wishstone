import logging
import os
from datetime import datetime

def setup_logger(name: str, level: str = "INFO") -> logging.Logger:
    """
    Logger 설정 함수
    
    Args:
        name: Logger 이름 (보통 모듈명)
        level: 로그 레벨 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        설정된 Logger 객체
    """
    
    # 로그 레벨 설정
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    # Logger 생성
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # 이미 핸들러가 있다면 중복 생성 방지
    if logger.handlers:
        return logger
    
    # 로그 포맷 설정
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 콘솔 핸들러 설정
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 파일 핸들러 설정 (선택적)
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 일별 로그 파일
    log_filename = f"{log_dir}/wishstone_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(log_filename, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)  # 파일에는 모든 레벨 기록
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger

def get_logger(name: str) -> logging.Logger:
    """
    기존 Logger 가져오기 또는 새로 생성
    
    Args:
        name: Logger 이름
    
    Returns:
        Logger 객체
    """
    return setup_logger(name)

# 전역 로거들
crypto_logger = setup_logger("crypto")
database_logger = setup_logger("database") 
ai_logger = setup_logger("ai_analyzer")
routes_logger = setup_logger("routes")
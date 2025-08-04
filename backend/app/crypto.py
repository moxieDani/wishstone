import os
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from .logger_config import crypto_logger as logger

class AES128Crypto:
    def __init__(self):
        # .env에서 key와 iv 읽어오기
        self.key = os.getenv('AES_KEY')
        self.iv = os.getenv('AES_IV')
        
        if not self.key or not self.iv:
            raise ValueError("AES_KEY와 AES_IV가 .env 파일에 설정되어야 합니다.")
        
        # Base64 디코딩 (만약 .env에 Base64로 저장된 경우)
        try:
            self.key = base64.b64decode(self.key)
            self.iv = base64.b64decode(self.iv)
        except:
            # 문자열로 저장된 경우 바이트로 변환
            self.key = self.key.encode('utf-8')[:16]  # AES128은 16바이트 키
            self.iv = self.iv.encode('utf-8')[:16]   # IV도 16바이트
        
        # 키와 IV 길이 확인
        if len(self.key) != 16:
            raise ValueError("AES128 키는 16바이트여야 합니다.")
        if len(self.iv) != 16:
            raise ValueError("IV는 16바이트여야 합니다.")
    
    def encrypt(self, plaintext):
        """텍스트를 AES128로 암호화 (복호화는 지원하지 않음)"""
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        
        # 텍스트를 바이트로 변환하고 패딩 추가
        plaintext_bytes = plaintext.encode('utf-8')
        padded_data = pad(plaintext_bytes, AES.block_size)
        
        # 암호화
        encrypted_data = cipher.encrypt(padded_data)
        
        # Base64로 인코딩하여 반환
        return base64.b64encode(encrypted_data).decode('utf-8')

def generate_key_iv():
    """새로운 키와 IV 생성 (Base64 인코딩)"""
    key = os.urandom(16)  # 16바이트 = 128비트
    iv = os.urandom(16)   # 16바이트 IV
    
    logger.debug("다음 값들을 .env 파일에 추가하세요:")
    logger.debug(f"AES_KEY={base64.b64encode(key).decode('utf-8')}")
    logger.debug(f"AES_IV={base64.b64encode(iv).decode('utf-8')}")

def initialize_crypto():
    """AES 암호화 객체 초기화"""
    try:
        aes_crypto = AES128Crypto()
        return aes_crypto
    except Exception as e:
        logger.error(f"❌ AES128 암호화 초기화 실패: {e}")
        logger.debug(f"AES 초기화 오류 상세: Exception type: {type(e).__name__}")
        logger.debug("새로운 키와 IV를 생성하려면 다음 값들을 .env 파일에 추가하세요:")
        generate_key_iv()
        return None
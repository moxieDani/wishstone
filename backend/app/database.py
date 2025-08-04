import sqlite3
import atexit
from datetime import datetime
from .crypto import initialize_crypto
from .logger_config import database_logger as logger

# 데이터베이스 연결 객체 (전역 변수)
db_connection = None
aes_crypto = None

def init_database():
    """데이터베이스 초기화 및 테이블 생성"""
    global db_connection, aes_crypto
    
    # AES 암호화 객체 초기화
    aes_crypto = initialize_crypto()
    
    try:
        # 데이터베이스 연결
        db_connection = sqlite3.connect('wishstone_database.db', check_same_thread=False)
        cursor = db_connection.cursor()
        
        # 테이블 존재 여부 확인
        cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='WishStone_Records'
        """)
        
        table_exists = cursor.fetchone()
        
        if not table_exists:
            # 테이블 생성
            cursor.execute("""
            CREATE TABLE WishStone_Records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_ip TEXT,
                user_text TEXT,
                wish_type TEXT,
                sentiment TEXT,
                country_name TEXT,
                current_time TEXT,
                utc_time TEXT,
                timezone TEXT
            )
            """)
            db_connection.commit()
        
        # 테이블 상태 확인 (정상 로직이므로 로그 제거)
        cursor.execute("SELECT COUNT(*) FROM WishStone_Records")
        record_count = cursor.fetchone()[0]
        
    except Exception as e:
        logger.error(f"❌ 데이터베이스 초기화 오류: {str(e)}")
        logger.debug(f"데이터베이스 초기화 오류 상세: Exception type: {type(e).__name__}")
        logger.debug(f"오류 발생 위치: 데이터베이스 연결 또는 테이블 생성 과정")
        return False
    
    return True

def close_database():
    """데이터베이스 연결 종료"""
    global db_connection
    
    if db_connection:
        try:
            db_connection.close()
        except Exception as e:
            logger.error(f"❌ 데이터베이스 종료 오류: {str(e)}")
            logger.debug(f"데이터베이스 종료 오류 상세: Exception type: {type(e).__name__}")

def insert_record(client_ip, user_text, wish_type, sentiment, country_name, current_time, utc_time, timezone):
    """데이터베이스에 레코드 삽입 (client_ip는 암호화하여 저장)"""
    global db_connection, aes_crypto
    
    if not db_connection:
        logger.error("❌ 데이터베이스 연결이 없습니다.")
        return False
    
    if not aes_crypto:
        logger.error("❌ AES 암호화 객체가 초기화되지 않았습니다.")
        return False
    
    try:
        cursor = db_connection.cursor()
        
        # client_ip를 AES128로 암호화 (정상 로직이므로 로그 제거)
        encrypted_ip = aes_crypto.encrypt(client_ip)
        
        cursor.execute("""
        INSERT INTO WishStone_Records 
        (client_ip, user_text, wish_type, sentiment, country_name, current_time, utc_time, timezone)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            encrypted_ip,
            user_text,
            wish_type,
            sentiment,
            country_name,
            current_time,
            utc_time,
            timezone
        ))
        
        db_connection.commit()
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 데이터베이스 삽입 오류: {str(e)}")
        logger.debug(f"삽입 오류 상세: Exception type: {type(e).__name__}")
        logger.debug(f"삽입 시도 데이터: user_text={user_text[:50] if user_text else 'None'}...")
        return False

def check_daily_limit():
    """오늘 처리된 요청 수 확인 (제한: 100건/일)"""
    global db_connection
    
    if not db_connection:
        logger.error("❌ 데이터베이스 연결이 없습니다.")
        return False
    
    try:
        cursor = db_connection.cursor()
        
        # 오늘 날짜 (UTC 기준)
        today = datetime.now().strftime('%Y-%m-%d')
        
        # 오늘 처리된 요청 수 조회
        cursor.execute("""
        SELECT COUNT(*) FROM WishStone_Records 
        WHERE DATE(utc_time) = ?
        """, (today,))
        
        today_count = cursor.fetchone()[0]
        
        if today_count >= 100:
            logger.warning(f"🚫 일일 처리 제한 초과! 오늘 처리된 요청: {today_count}/100")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 일일 제한 확인 오류: {str(e)}")
        logger.debug(f"일일 제한 확인 오류 상세: Exception type: {type(e).__name__}")
        return False

def check_ip_daily_limit(client_ip):
    """특정 IP의 오늘 처리 횟수 확인 (제한: 1회/일)"""
    global db_connection, aes_crypto
    
    if not db_connection:
        logger.error("❌ 데이터베이스 연결이 없습니다.")
        return False
    
    if not aes_crypto:
        logger.error("❌ AES 암호화 객체가 초기화되지 않았습니다.")
        return False
    
    try:
        cursor = db_connection.cursor()
        
        # 오늘 날짜 (UTC 기준)
        today = datetime.now().strftime('%Y-%m-%d')
        
        # 확인할 IP를 AES128로 암호화 (정상 로직이므로 로그 제거)
        encrypted_ip = aes_crypto.encrypt(client_ip)
        
        # 해당 암호화된 IP가 오늘 처리된 횟수 조회
        cursor.execute("""
        SELECT COUNT(*) FROM WishStone_Records 
        WHERE DATE(utc_time) = ? AND client_ip = ?
        """, (today, encrypted_ip))
        
        ip_today_count = cursor.fetchone()[0]
        
        if ip_today_count >= 1:
            logger.warning(f"🚫 IP별 일일 처리 제한 초과! IP 처리 횟수: {ip_today_count}/1")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"❌ IP 일일 제한 확인 오류: {str(e)}")
        logger.debug(f"IP 제한 확인 오류 상세: Exception type: {type(e).__name__}")
        logger.debug(f"확인 시도 IP: {client_ip}")
        return False

def get_records():
    """저장된 레코드 조회 (최근 10개)"""
    global db_connection
    
    if not db_connection:
        return {
            "success": False,
            "message": "데이터베이스 연결이 없습니다."
        }
    
    try:
        cursor = db_connection.cursor()
        
        # 최근 10개 레코드 조회
        cursor.execute("""
        SELECT * FROM WishStone_Records 
        ORDER BY utc_time DESC 
        LIMIT 10
        """)
        
        columns = [description[0] for description in cursor.description]
        records = cursor.fetchall()
        
        # 딕셔너리 형태로 변환
        result = []
        for record in records:
            result.append(dict(zip(columns, record)))
        
        return {
            "success": True,
            "records": result,
            "count": len(result)
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"레코드 조회 오류: {str(e)}"
        }

# 애플리케이션 종료 시 데이터베이스 연결 종료
atexit.register(close_database)
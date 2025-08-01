from flask import Blueprint, request, jsonify
import requests
import sqlite3
import os
import atexit
from typing import Literal
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from datetime import datetime
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

bp = Blueprint('api', __name__)

# 데이터베이스 연결 객체 (전역 변수)
db_connection = None

# Pydantic 모델 정의
class Category(BaseModel):
    wish_type: Literal["Material", "Feeling", "Achieve"]
    sentiment: Literal["Positive", "Negative", "Nutural"]

# LangChain을 통한 LLM 초기화
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
prompt = PromptTemplate.from_template("다음 텍스트를 분석해서 wish_type과 sentiment를 분류해주세요: {context}")
chain = prompt | llm.with_structured_output(Category)

def init_database():
    """데이터베이스 초기화 및 테이블 생성"""
    global db_connection
    
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
            print("✅ WishStone_Records 테이블이 생성되었습니다.")
        else:
            print("✅ WishStone_Records 테이블이 이미 존재합니다.")
            
        # 테이블 상태 확인
        cursor.execute("SELECT COUNT(*) FROM WishStone_Records")
        record_count = cursor.fetchone()[0]
        print(f"📊 현재 데이터베이스에 {record_count}개의 레코드가 있습니다.")
        
    except Exception as e:
        print(f"❌ 데이터베이스 초기화 오류: {str(e)}")
        return False
    
    return True

def close_database():
    """데이터베이스 연결 종료"""
    global db_connection
    
    if db_connection:
        try:
            db_connection.close()
            print("✅ 데이터베이스 연결이 종료되었습니다.")
        except Exception as e:
            print(f"❌ 데이터베이스 종료 오류: {str(e)}")

def insert_record(user_text, wish_type, sentiment, country_name, current_time, utc_time, timezone):
    """데이터베이스에 레코드 삽입"""
    global db_connection
    
    if not db_connection:
        print("❌ 데이터베이스 연결이 없습니다.")
        return False
    
    try:
        cursor = db_connection.cursor()
        
        cursor.execute("""
        INSERT INTO WishStone_Records 
        (user_text, wish_type, sentiment, country_name, current_time, utc_time, timezone)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            user_text,
            wish_type,
            sentiment,
            country_name,
            current_time,
            utc_time,
            timezone
        ))
        
        db_connection.commit()
        
        # 삽입된 레코드 ID 가져오기
        record_id = cursor.lastrowid
        print(f"💾 데이터베이스에 레코드가 저장되었습니다. (ID: {record_id})")
        
        return True
        
    except Exception as e:
        print(f"❌ 데이터베이스 삽입 오류: {str(e)}")
        return False

def analyze_text(text):
    """텍스트 분석 함수"""
    try:
        result = chain.invoke({"context": text})
        return {
            "success": True,
            "wish_type": result.wish_type,
            "sentiment": result.sentiment
        }
    except Exception as e:
        print(f"텍스트 분석 오류: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@bp.route("/process-all", methods=["POST"])
def process_all_info():
    """모든 정보를 처리하고 콘솔에 출력하는 API"""
    try:
        data = request.get_json()
        
        # 클라이언트에서 전달받은 정보
        user_text = data.get("text", "")
        client_ip = data.get("ip_address", "")
        timezone = data.get("timezone", "")
        current_time = data.get("current_time", "")
        utc_time = data.get("utc_time", "")
        country_name = data.get("country_name", "")
        
        print("\n" + "="*60)
        print("📊 WishStone - 처리 결과")
        print("="*60)
        print(f"⏰ 처리 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-"*60)
        
        # 입력 텍스트 출력
        print(f"💬 입력한 텍스트: {user_text}")
        print("-"*60)
        
        # AI 텍스트 분석 수행
        wish_type = "Unknown"
        sentiment = "Unknown"
        
        if user_text.strip():
            analysis_result = analyze_text(user_text)
            if analysis_result["success"]:
                wish_type = analysis_result['wish_type']
                sentiment = analysis_result['sentiment']
                print(f"🤖 AI 분석 결과:")
                print(f"   • 소원 유형: {wish_type}")
                print(f"   • 감정: {sentiment}")
            else:
                print(f"🤖 AI 분석 실패: {analysis_result.get('error', '알 수 없는 오류')}")
        else:
            print("🤖 AI 분석: 텍스트가 비어있음")
        
        print("-"*60)
        
        # 클라이언트 정보 출력
        print(f"🖧 IP 정보:")
        print(f"   • IP 주소: {client_ip}")
        print(f"⏰ 시간 정보:")
        print(f"   • 타임존: {timezone}")
        print(f"   • 현재 시각: {current_time}")
        print(f"   • UTC 시각: {utc_time}")
        print(f"🌎 위치 정보:")
        print(f"   • 국가명: {country_name}")
        
        print("="*60)
        
        # 데이터베이스에 정보 저장
        db_success = insert_record(
            user_text=user_text,
            wish_type=wish_type,
            sentiment=sentiment,
            country_name=country_name,
            current_time=current_time,
            utc_time=utc_time,
            timezone=timezone
        )
        
        if db_success:
            print("✅ 데이터베이스 저장 완료!")
        else:
            print("❌ 데이터베이스 저장 실패!")
            
        print("✅ 처리 완료!")
        print("="*60 + "\n")
        
        return jsonify({
            "success": True,
            "message": "모든 정보가 성공적으로 처리되었습니다.",
            "database_saved": db_success
        })
        
    except Exception as e:
        print(f"\n❌ 처리 중 오류 발생: {str(e)}\n")
        return jsonify({
            "success": False,
            "message": f"처리 중 오류가 발생했습니다: {str(e)}"
        })

@bp.route("/get-records", methods=["GET"])
def get_records():
    """저장된 레코드 조회 API (선택적 기능)"""
    global db_connection
    
    if not db_connection:
        return jsonify({
            "success": False,
            "message": "데이터베이스 연결이 없습니다."
        })
    
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
        
        return jsonify({
            "success": True,
            "records": result,
            "count": len(result)
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"레코드 조회 오류: {str(e)}"
        })

# Blueprint 생성 시 데이터베이스 초기화
print("🚀 WishStone API 초기화 중...")
init_success = init_database()

if not init_success:
    print("❌ 데이터베이스 초기화에 실패했습니다.")
else:
    print("✅ WishStone API가 성공적으로 초기화되었습니다.")

# 애플리케이션 종료 시 데이터베이스 연결 종료
atexit.register(close_database)
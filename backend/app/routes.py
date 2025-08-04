from flask import Blueprint, request, jsonify
from datetime import datetime
from .database import (
    init_database, 
    insert_record, 
    check_daily_limit, 
    check_ip_daily_limit, 
    get_records
)
from .ai_analyzer import analyze_text
from .logger_config import routes_logger as logger

bp = Blueprint('api', __name__)

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
        
        # 일일 제한 확인 (100건/일)
        if not check_daily_limit():
            return jsonify({
                "success": False,
                "message": "일일 처리 제한을 초과했습니다. 내일 다시 시도해주세요. (제한: 100건/일)"
            })
        
        # IP별 일일 제한 확인 (1회/일)
        if not check_ip_daily_limit(client_ip):
            return jsonify({
                "success": False,
                "message": f"해당 IP는 오늘 이미 처리되었습니다. 내일 다시 시도해주세요. (IP별 제한: 1회/일)"
            })
        
        wish_type = "Unknown"
        sentiment = "Unknown"
        
        if user_text.strip():
            analysis_result = analyze_text(user_text)
            if analysis_result["success"]:
                wish_type = analysis_result['wish_type']
                sentiment = analysis_result['sentiment']
        
        # 데이터베이스에 정보 저장
        db_success = insert_record(
            client_ip=client_ip,
            user_text=user_text,
            wish_type=wish_type,
            sentiment=sentiment,
            country_name=country_name,
            current_time=current_time,
            utc_time=utc_time,
            timezone=timezone
        )
        
        # 데이터베이스 저장 결과는 insert_record 함수에서 처리        
        return jsonify({
            "success": True,
            "message": "모든 정보가 성공적으로 처리되었습니다.",
            "database_saved": db_success
        })
        
    except Exception as e:
        logger.error(f"❌ process_all_info 처리 중 오류 발생: {str(e)}")
        logger.debug(f"process_all_info 오류 상세: Exception type: {type(e).__name__}")
        logger.debug(f"요청 데이터: user_text={user_text[:100] if user_text else 'None'}...")
        logger.debug(f"클라이언트 정보: IP={client_ip}, 국가={country_name}")
        return jsonify({
            "success": False,
            "message": f"처리 중 오류가 발생했습니다: {str(e)}"
        })

@bp.route("/get-records", methods=["GET"])
def get_records_api():
    """저장된 레코드 조회 API (선택적 기능)"""
    result = get_records()
    return jsonify(result)

# Blueprint 생성 시 데이터베이스 초기화
init_success = init_database()

if not init_success:
    logger.error("❌ WishStone API 초기화 실패 - 데이터베이스 초기화에 실패했습니다.")
    logger.debug("API 초기화 실패: 데이터베이스 연결 또는 테이블 생성 과정에서 오류 발생")
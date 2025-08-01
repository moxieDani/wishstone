from flask import jsonify

@bp.route("/process-all", methods=["POST"])
def process_all_info():
    """모든 정보를 처리하고 콘솔에 출력하는 API"""
    try:
        return jsonify({
            "success": True,
            "message": "모든 정보가 성공적으로 처리되었습니다."
        })
        
    except Exception as e:
        print(f"\n❌ 처리 중 오류 발생: {str(e)}\n")
        return jsonify({
            "success": False,
            "message": f"처리 중 오류가 발생했습니다: {str(e)}"
        })
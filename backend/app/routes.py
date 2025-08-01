from flask import Blueprint, request, jsonify
import requests
from typing import Literal
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from datetime import datetime
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

bp = Blueprint('api', __name__)

# Pydantic 모델 정의
class Category(BaseModel):
    wish_type: Literal["Material", "Feeling", "Achieve"]
    sentiment: Literal["Positive", "Negative", "Nutural"]

# LangChain을 통한 LLM 초기화
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
prompt = PromptTemplate.from_template("다음 텍스트를 분석해서 wish_type과 sentiment를 분류해주세요: {context}")
chain = prompt | llm.with_structured_output(Category)

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
        if user_text.strip():
            analysis_result = analyze_text(user_text)
            if analysis_result["success"]:
                print(f"🤖 AI 분석 결과:")
                print(f"   • 소원 유형: {analysis_result['wish_type']}")
                print(f"   • 감정: {analysis_result['sentiment']}")
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
        print("✅ 처리 완료!")
        print("="*60 + "\n")
        
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
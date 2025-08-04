from typing import Literal
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from .logger_config import ai_logger as logger

# Pydantic 모델 정의
class Category(BaseModel):
    wish_type: Literal["Material", "Feeling", "Achieve"]
    sentiment: Literal["Positive", "Negative", "Nutural"]

# LangChain 체인을 위한 전역 변수 (지연 초기화)
_llm = None
_chain = None

def _get_chain():
    """LangChain 체인을 지연 초기화"""
    global _llm, _chain
    if _chain is None:
        _llm = ChatOpenAI(model="gpt-4.1-nano", temperature=0)
        prompt = PromptTemplate.from_template("{context}")
        _chain = prompt | _llm.with_structured_output(Category)
    return _chain

def analyze_text(text):
    """텍스트 분석 함수"""
    try:
        chain = _get_chain()
        result = chain.invoke({"context": text})
        return {
            "success": True,
            "wish_type": result.wish_type,
            "sentiment": result.sentiment
        }
    except Exception as e:
        logger.error(f"텍스트 분석 오류: {e}")
        logger.debug(f"AI 분석 오류 상세: Exception type: {type(e).__name__}")
        logger.debug(f"분석 시도 텍스트 길이: {len(text)} 문자")
        logger.debug(f"분석 시도 텍스트 샘플: {text[:100]}...")
        return {
            "success": False,
            "error": str(e)
        }
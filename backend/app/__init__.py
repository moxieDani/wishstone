from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

def create_app():
    # 환경변수 로드
    load_dotenv()
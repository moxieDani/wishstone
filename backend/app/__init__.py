from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

def create_app():
    # 환경변수 로드
    load_dotenv()
    
    app = Flask(__name__)
    
    # CORS 설정 (SvelteKit과의 통신을 위해)
    CORS(app, origins=["http://localhost:5173", "http://localhost:4173"])
    
    # 라우트 등록
    from .routes import bp as routes_bp
    app.register_blueprint(routes_bp, url_prefix='/api')
    
    return app
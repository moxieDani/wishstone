from flask import Flask
from flask_cors import CORS
from app.routes import bp

app = Flask(__name__)

# CORS 설정 (프론트엔드에서 API 호출을 위해 필요)
CORS(app)

# Blueprint 등록
app.register_blueprint(bp, url_prefix='/api')

@app.route("/")
def index():
    return {"message": "Backend API Server is running"}

if __name__ == "__main__":
    print("🚀 WishStone Backend API Server 시작...")   
    app.run(debug=True, port=5847)
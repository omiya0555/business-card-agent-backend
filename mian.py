from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from strands_agent_config import load_agent
import base64

app = FastAPI()
agent = load_agent()

# CORS（React用）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    # 画像データを読み取り
    content = await file.read()
    image_b64 = base64.b64encode(content).decode("utf-8")

    # 仮：画像を解析したと仮定してテキストを生成（後で実際にparse API呼び出し）
    fake_extracted_info = {
        "name": "山田 太郎",
        "company": "ABC株式会社",
        "position": "営業部長",
        "email": "taro@abc.co.jp",
    }

    # Prompt を構築
    prompt = f"{fake_extracted_info['name']}さん（{fake_extracted_info['company']}の{fake_extracted_info['position']}）について教えてください。"

    # 応答生成（非同期）
    response = await agent.run(prompt)
    return response  # StrandsAgentが生成した形式そのまま返す

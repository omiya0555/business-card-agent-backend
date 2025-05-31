from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from strands import Agent

from upstage_client import parse_document

agent = Agent(
    system_prompt=
        """
        You are a business card information extraction agent.
        Your task is to extract information from business card images and generate a response based on the extracted data.
        You will receive an image file of a business card, and you should extract the following information:
        """,
)

app = FastAPI()

# CORS
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

    # Upstage API呼び出し
    parsed_result = parse_document(
        file_bytes=content,
        filename=file.filename,
        mime_type=file.content_type
    )

    prompt = f"""
    以下の名刺情報をもとに、ビジネスカードの内容を要約してください。
    名刺情報: {parsed_result}
    """

    # 応答生成
    response = agent(prompt)
    return response

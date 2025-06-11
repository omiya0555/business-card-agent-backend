from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from upstage_client_info_extract import extract_information
from member_scraper import find_member_page, get_member_details
from strands import Agent, tool

app = FastAPI()

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# メンバーURLを取得するツール
@tool
def get_member_url(name: str) -> str:
    """
    指定された名前のメンバーの詳細ページURLを取得します。
    """
    member_url = find_member_page(name)
    if not member_url:
        return f"該当するメンバーが見つかりませんでした: {name}"
    return member_url

# 自己紹介ページの内容を取得するツール
@tool
def get_member_bio(member_url: str) -> str:
    """
    メンバー詳細ページから自己紹介情報を取得します。
    """
    member_bio = get_member_details(member_url)
    if "error" in member_bio:
        return f"自己紹介情報の取得に失敗しました: {member_bio['error']}"
    return member_bio

# Claudeモデルを使用するAgentの定義
agent = Agent(
    tools=[get_member_url, get_member_bio],
    system_prompt="""
    You are a business card information extraction agent.
    Your task is to extract information from business card images and generate a response based on the extracted data.
    You will also retrieve additional information from the company's members page if needed.
    """
)

# エンドポイントの定義
@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    """
    名刺画像をアップロードし、情報を抽出し、自己紹介情報を取得して回答を生成するエンドポイント
    """
    # 画像データを読み取り
    content = await file.read()

    # 情報抽出
    try:
        extracted_info = extract_information(
            file_bytes=content,
            filename=file.filename,
            mime_type=file.content_type,
        )
    except Exception as e:
        return {"error": f"Failed to extract information: {str(e)}"}

    # 名前を取得
    member_name = extracted_info.get("name", "").split("\n")[0]  # 改行で分割して最初の部分を使用
    if not member_name:
        return {"error": "名刺情報から名前を取得できませんでした。"}

    # メンバーURLを取得
    try:
        member_url = get_member_url(member_name)
        if "該当するメンバーが見つかりませんでした" in member_url:
            return {"error": member_url}

        # 自己紹介情報を取得
        member_bio = get_member_bio(member_url)
        if "自己紹介情報の取得に失敗しました" in member_bio:
            return {"error": member_bio}

    except Exception as e:
        return {"error": f"Failed to retrieve member information: {str(e)}"}

    # Claudeモデルで回答を生成
    try:
        prompt = f"""
        以下の名刺情報と自己紹介情報をもとに、ビジネスカードの内容を要約してください。
        名刺情報: {extracted_info}
        自己紹介情報: {member_bio}
        """
        response = agent(prompt)
    except Exception as e:
        return {"error": f"Failed to generate response: {str(e)}"}

    # 結果を返す
    return {
        "extracted_info": extracted_info,
        "member_url": member_url,
        "member_bio": member_bio,
        "response": response,
    }

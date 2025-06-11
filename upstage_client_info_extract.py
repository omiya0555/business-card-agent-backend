import os
import dotenv
import base64
import json
from openai import OpenAI

dotenv.load_dotenv()

UPSTAGE_API_KEY = os.getenv("UPSTAGE_API_KEY")
UPSTAGE_INFO_EXTRACT_URL = os.getenv("UPSTAGE_INFO_EXTRACT_URL")

if not UPSTAGE_API_KEY:
    raise ValueError("環境変数 'UPSTAGE_API_KEY' が設定されていません。")

if not UPSTAGE_INFO_EXTRACT_URL:
    raise ValueError("環境変数 'UPSTAGE_INFO_EXTRACT_URL' が設定されていません。")

def extract_information(file_bytes, filename, mime_type="image/png"):
    """
    Upstage Universal Information Extraction APIを使って
    名刺画像から name, company_name, position を抽出します。
    """
    # 画像をbase64エンコード
    base64_data = base64.b64encode(file_bytes).decode("utf-8")

    # OpenAI互換クライアント
    client = OpenAI(
        api_key=UPSTAGE_API_KEY,
        base_url=UPSTAGE_INFO_EXTRACT_URL
    )

    # スキーマ定義
    schema = {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "The full name on the business card"
            },
            "company_name": {
                "type": "string",
                "description": "The company name on the business card"
            },
            "position": {
                "type": "string",
                "description": "The job title or position on the business card"
            }
        }
    }

    # APIリクエスト
    try:
        extraction_response = client.chat.completions.create(
            model="information-extract",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:{mime_type};base64,{base64_data}"}
                        }
                    ]
                }
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "business_card_schema",
                    "schema": schema
                }
            }
        )

        # 結果をパース
        content = extraction_response.choices[0].message.content
        result = json.loads(content)
        return result

    except Exception as e:
        return {"error": f"Failed to extract information: {str(e)}"}

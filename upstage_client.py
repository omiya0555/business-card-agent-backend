import requests
import os
import dotenv

dotenv.load_dotenv()

UPSTAGE_API_KEY = os.getenv("UPSTAGE_API_KEY")
UPSTAGE_API_URL = os.getenv("UPSTAGE_API_URL")

if not UPSTAGE_API_KEY:
    raise ValueError("環境変数 'UPSTAGE_API_KEY' が設定されていません。")

if not UPSTAGE_API_URL:
    raise ValueError("環境変数 'UPSTAGE_API_URL' が設定されていません。")

def parse_document(file_bytes, filename, mime_type="image/png"):
    headers = {
        "Authorization": f"Bearer {UPSTAGE_API_KEY}",
    }

    files = {
        "document": (filename, file_bytes, mime_type),
    }

    # 必要なパラメータを追加
    data = {
        "ocr": "force",  # OCRを強制的に使用
        "base64_encoding": "['table']",  # テーブルデータをエンコード
        "model": "document-parse",  # 使用するモデル名
    }

    response = requests.post(UPSTAGE_API_URL, headers=headers, files=files, data=data)

    if response.status_code != 200:
        raise Exception(f"Upstage API error: {response.status_code}, {response.text}")

    return response.json()

import requests
import os
import dotenv

dotenv.load_dotenv()

UPSTAGE_API_KEY = os.getenv("UPSTAGE_API_KEY")
UPSTAGE_API_URL = os.getenv("UPSTAGE_API_URL")

def parse_document(file_bytes, filename, mime_type="image/png"):
    headers = {
        "Authorization": f"Bearer {UPSTAGE_API_KEY}",
    }

    files = {
        "document": (filename, file_bytes, mime_type),
    }

    response = requests.post(UPSTAGE_API_URL, headers=headers, files=files)
    print(response.status_code, response.text)

    if response.status_code != 200:
        raise Exception(f"Upstage API error: {response.status_code}, {response.text}")

    return response.json()

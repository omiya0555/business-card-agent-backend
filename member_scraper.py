import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_URL = "https://fusic.co.jp/members"

def find_member_page(name: str) -> str:
    """
    指定された名前のメンバーの詳細ページURLを取得します。
    """
    try:
        # メンバー一覧ページを取得
        response = requests.get(BASE_URL, timeout=5)
        response.raise_for_status()

        # BeautifulSoupでHTMLを解析
        soup = BeautifulSoup(response.text, "html.parser")

        # 全てのメンバーリストアイテムを取得
        member_list_items = soup.select("div.c-member__list ul li")

        for item in member_list_items:
            # 各アイテムから名前とリンクを取得
            name_tag = item.find("p", attrs={"data-item": "title"})
            link_tag = item.find("a")

            if name_tag and link_tag:
                member_name_from_html = name_tag.get_text(strip=True)

                # 検索名とHTML内の名前から空白を除去して比較
                normalized_query_name = "".join(name.split())  # 半角・全角スペースを除去
                normalized_html_name = "".join(member_name_from_html.split())

                if normalized_query_name in normalized_html_name:
                    href = link_tag.get("href")
                    if href:
                        return urljoin(BASE_URL, href)  # 完全なURLを返す

        return f"{name} さんのプロフィールが見つかりませんでした。"

    except Exception as e:
        return {"error": f"Failed to find member page: {str(e)}"}

def get_member_details(member_url: str) -> dict:
    """
    メンバー詳細ページから必要な情報を取得します。
    """
    try:
        # メンバー詳細ページを取得
        response = requests.get(member_url, timeout=5)
        response.raise_for_status()

        # BeautifulSoupでHTMLを解析
        soup = BeautifulSoup(response.text, "html.parser")

        # 必要な情報を抽出
        name = soup.find("p", {"data-item": "title"}).get_text(strip=True)
        department = soup.find("p", {"data-item": "department"}).get_text(strip=True)
        comment = soup.find("div", {"data-item": "comment"}).get_text(strip=True)

        # 略歴
        bio_section = soup.find("div", {"data-col-type": "text"}, text="略歴")
        bio = bio_section.find_next("p").get_text(strip=True) if bio_section else "略歴情報が見つかりませんでした。"

        # 担当・スキル
        skills_section = soup.find("div", {"data-col-type": "text"}, text="担当・スキル")
        skills = skills_section.find_next("p").get_text(strip=True) if skills_section else "担当・スキル情報が見つかりませんでした。"

        # プライベート
        private_section = soup.find("div", {"data-col-type": "text"}, text="プライベート")
        private = private_section.find_next("p").get_text(strip=True) if private_section else "プライベート情報が見つかりませんでした。"

        # 資格情報
        certifications = []
        certification_sections = soup.find_all("ul", {"class": "general-certification"})
        for section in certification_sections:
            certifications.extend([li.get_text(strip=True) for li in section.find_all("li")])

        # 結果を辞書形式で返す
        return {
            "name": name,
            "department": department,
            "comment": comment,
            "bio": bio,
            "skills": skills,
            "private": private,
            "certifications": certifications,
        }

    except Exception as e:
        return {"error": f"Failed to get member details: {str(e)}"}

import streamlit as st
import requests
import re

# ✅ あなたの楽天アプリIDに置き換えてください
application_id = "1089430039707781272"

# -------------------------------
# 🔍 商品情報を楽天APIから取得（ItemLookup → Search フォールバック対応）
# -------------------------------
def get_item_data(url):
    try:
        # --- ① ItemLookup API ---
        api1 = "https://app.rakuten.co.jp/services/api/IchibaItem/ItemLookup/20170426"
        res = requests.get(api1, params={"applicationId": application_id, "itemUrl": url, "format": "json"})
        d = res.json()
        if "Items" in d and d["Items"]:
            item = d["Items"][0]["Item"]
        else:
            # --- ② Item Search API にフォールバック（キーワードで検索） ---
            m = re.search(r'/([^/]+)/([^/?#]+)/?$', url)
            keyword = m.group(2) if m else ""
            api2 = "https://app.rakuten.co.jp/services/api/IchibaItem/Search/20220601"
            res2 = requests.get(api2, params={
                "applicationId": application_id,
                "keyword": keyword,
                "hits": 1,
                "format": "json"
            })
            d2 = res2.json()
            if "Items" not in d2 or not d2["Items"]:
                return {"error": "商品が見つかりませんでした（両API失敗）"}
            item = d2["Items"][0]["Item"]

        return {
            "title": item["itemName"],
            "price": item["itemPrice"],
            "review": item["reviewAverage"],
            "count": item["reviewCount"],
            "image": item["mediumImageUrls"][0]["imageUrl"],
            "url": item["itemUrl"]
        }
    except Exception as e:
        return {"error": str(e)}

# -------------------------------
# 📝 HTML出力関数（クリックされやすいデザイン）
# -------------------------------
def generate_html(products: list) -> str:
    html = "<h2>楽天商品比較まとめ</h2>\n"
    for product in products:
        html += f"""
        <div style="border: 1px solid #ccc; border-radius: 12px; padding: 16px; margin-bottom: 24px; display: flex; gap: 16px;">
          <img src="{product['image']}" alt="{product['title']}" style="width: 150px; height: auto; border-radius: 8px;" />
          <div style="flex: 1;">
            <h3 style="margin-top: 0;">
              <a href="{product['url']}" target="_blank" style="text-decoration: none; color: #0074c2;">
                {product['title']}
              </a>
            </h3>
            <p style="margin: 4px 0;">💴 <strong>{product['price']}</strong></p>
            <p style="margin: 4px 0;">⭐ {product['review_avg']} / 5.0（{product['review_count']}件）</p>
            <a href="{product['url']}" target="_blank" style="display: inline-block; margin-top: 8px; padding: 8px 16px; background-color: #ff6600; color: white; text-decoration: none; border-radius: 6px;">
              ▶ 今すぐチェック
            </a>
          </div>
        </div>
        """
    return html

# -------------------------------
# 🚀 Streamlit アプリ本体
# -------------------------------
st.title("📦 楽天商品 比較まとめツール")

urls_text = st.text_area("楽天商品のURLを1行ずつ入力してください")

# 比較記事を生成
if st.button("比較記事を生成"):
    urls = urls_text.strip().splitlines()
    if not urls:
        st.warning("URLを入力してください")
    else:
        products = []
        output_md = "# 📦 楽天市場 商品比較まとめ\n\n"
        failed_urls = []

        for idx, url in enumerate(urls, 1):
            data = get_item_data(url)
            st.write(f"🔍 {idx}番目のAPI応答:", data)  # デバッグ表示

            if "error" in data:
                st.error(f"{idx}. 取得エラー: {data['error']}")
                output_md += f"## {idx}. 取得エラー\n- URL: {url}\n- ⚠️ エラー: {data['error']}\n\n"
                failed_urls.append(url)
                continue

            st.subheader(f"{idx}. {data['title']}")
            st.image(data["im]()

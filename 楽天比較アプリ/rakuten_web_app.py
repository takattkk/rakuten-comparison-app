import streamlit as st
import requests
import re

# ✅ 楽天アプリIDを入力
application_id = "1089430039707781272"

# -------------------------------
# 🔍 商品情報を楽天APIから正確に取得（ItemCodeSearch）
# -------------------------------
def get_item_data(url):
    try:
        m = re.search(r'rakuten\.co\.jp/([^/]+)/([^/?#]+)', url)
        if not m:
            return {"error": "URLからitemCodeを抽出できませんでした"}
        shop_id, item_id = m.group(1), m.group(2)
        item_code = f"{shop_id}:{item_id}"

        api_url = "https://app.rakuten.co.jp/services/api/IchibaItem/ItemCodeSearch/20170628"
        params = {
            "applicationId": application_id,
            "itemCode": item_code,
            "format": "json"
        }
        res = requests.get(api_url, params=params)
        data = res.json()

        if "Items" not in data or not data["Items"]:
            return {"error": "商品が見つかりませんでした"}

        item = data["Items"][0]["Item"]
        return {
            "title": item["itemName"],
            "price": item.get("itemPrice", "不明"),
            "review": item.get("reviewAverage", "不明"),
            "count": item.get("reviewCount", "不明"),
            "image": item["mediumImageUrls"][0]["imageUrl"],
            "url": item["itemUrl"]
        }

    except Exception as e:
        return {"error": str(e)}

# -------------------------------
# 📝 HTML出力（クリックされやすいアフィリエイト向け）
# -------------------------------
def generate_html(products):
    html = "<h2>楽天商品比較まとめ</h2>\n"
    for p in products:
        html += f"""
        <div style="border:1px solid #ddd; border-radius:10px; padding:16px; margin-bottom:20px; display:flex; gap:16px;">
          <img src="{p['image']}" alt="{p['title']}" style="width:150px; border-radius:8px;">
          <div>
            <h3 style="margin:0 0 10px;"><a href="{p['url']}" target="_blank" style="text-decoration:none; color:#0074c2;">{p['title']}</a></h3>
            <p>💴 <strong>{p['price']}</strong></p>
            <p>⭐ {p['review_avg']} / 5.0（{p['review_count']}件）</p>
            <a href="{p['url']}" target="_blank" style="display:inline-block; margin-top:10px; background:#ff6600; color:#fff; padding:8px 16px; border-radius:6px; text-decoration:none;">▶ 今すぐチェック</a>
          </div>
        </div>
        """
    return html

# -------------------------------
# 🚀 Streamlit アプリ本体
# -------------------------------
st.title("📦 楽天商品 比較まとめツール")

urls_text = st.text_area("楽天商品のURLを1行ずつ入力してください")

if st.button("比較記事を生成"):
    urls = urls_text.strip().splitlines()
    if not urls:
        st.warning("URLを入力してください")
    else:
        products = []
        output_md = "# 📦 楽天市場 商品比較まとめ\n\n"

        for idx, url in enumerate(urls, 1):
            data = get_item_data(url)
            if "error" in data:
                st.error(f"{idx}. エラー: {data['error']}")
                output_md += f"## {idx}. 取得エラー\n- URL: {url}\n- ⚠️ エラー: {data['error']}\n\n"
                continue

            st.subheader(f"{idx}. {data['title']}")
            st.image(data["image"], width=200)
            st.markdown(f"🏷️ **価格**: ¥{data['price']:,}" if isinstance(data["price"], int) else f"🏷️ **価格**: {data['price']}")
            st.markdown(f"⭐ **評価**: {data['review']} / 5.0（{data['count']}件）")
            st.markdown(f"[🔗 商品リンク]({data['url']})")

            output_md += f"## {idx}. [{data['title']}]({data['url']})\n"
            output_md += f"- 🏷️ 価格: ¥{data['price']:,}\n" if isinstance(data["price"], int) else f"- 🏷️ 価格: {data['price']}\n"
            output_md += f"- ⭐ 評価: {data['review']} / 5.0（{data['count']}件）\n"
            output_md += f"- ![商品画像]({data['image']})\n\n"

            products.append({
                "title": data['title'],
                "price": f"¥{data['price']:,}" if isinstance(data["price"], int) else data['price'],
                "review_avg": data['review'],
                "review_count": data['count'],
                "image": data['image'],
                "url": data['url']
            })

        st.session_state["products"] = products
        st.session_state["output_md"] = output_md

        st.download_button("📄 Markdown記事をダウンロード", data=output_md, file_name="rakuten_summary.md", mime="text/markdown")
        st.success("Markdown記事が生成されました ✅")

# HTML出力
if "products" in st.session_state and st.session_state["products"]:
    if st.button("HTML記事として出力"):
        html_content = generate_html(st.session_state["products"])
        st.markdown("### 💾 コピーしてブログに貼り付けてください")
        st.code(html_content, language="html")

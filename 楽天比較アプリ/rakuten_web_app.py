import streamlit as st
import requests
import re

# アプリIDをここに入れてください
application_id = "1089430039707781272"

def get_item_data(url):
    try:
        m = re.search(r'rakuten\.co\.jp/([^/]+)/([^/?#]+)', url)
        if not m:
            return {"error": "URLからitemCodeを抽出できませんでした"}

        shop_id = m.group(1)
        item_id = m.group(2)
        item_code = f"{shop_id}:{item_id}"

        api_url = "https://app.rakuten.co.jp/services/api/IchibaItem/Search/20170706"
        params = {
            "applicationId": application_id,
            "itemCode": item_code,
            "format": "json"
        }
        res = requests.get(api_url, params=params)
        data = res.json()

        if "Items" not in data or len(data["Items"]) == 0:
            return {"error": "商品が見つかりませんでした"}

        item = data["Items"][0]["Item"]
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

# --- Streamlitアプリ本体 ---

st.title("📦 楽天商品 比較まとめツール")

urls_text = st.text_area("楽天商品のURLを1行ずつ入力してください")

if st.button("比較記事を生成"):
    urls = urls_text.strip().splitlines()
    if not urls:
        st.warning("URLを入力してください")
    else:
        output_md = "# 📦 楽天市場 商品比較まとめ\n\n"

        for idx, url in enumerate(urls, 1):
            data = get_item_data(url)
            if "error" in data:
                st.error(f"{idx}. 取得エラー: {data['error']}")
                output_md += f"## {idx}. 取得エラー\n- URL: {url}\n- ⚠️ エラー: {data['error']}\n\n"
                continue

            st.subheader(f"{idx}. {data['title']}")
            st.image(data["image"], width=200)
            st.markdown(f"🏷️ **価格**: ¥{data['price']:,}")
            st.markdown(f"⭐ **評価**: {data['review']} / 5.0（{data['count']}件）")
            st.markdown(f"[🔗 商品リンク]({data['url']})")

            output_md += f"## {idx}. [{data['title']}]({data['url']})\n"
            output_md += f"- 🏷️ 価格: ¥{data['price']:,}\n"
            output_md += f"- ⭐ 評価: {data['review']} / 5.0（{data['count']}件）\n"
            output_md += f"- ![商品画像]({data['image']})\n\n"

        st.markdown("---")
        st.download_button("📄 Markdown記事をダウンロード", data=output_md, file_name="rakuten_summary.md", mime="text/markdown")

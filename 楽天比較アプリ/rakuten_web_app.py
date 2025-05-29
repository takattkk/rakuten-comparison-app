import streamlit as st
import requests
import re

# アプリIDをここに入れてください
application_id = "1089430039707781272"

def generate_html(products: list) -> str:
    html = "<h2>楽天商品比較まとめ</h2>\n"
    for product in products:
        html += f"""
        <div style="margin-bottom: 20px;">
            <h3><a href="{product['url']}" target="_blank">{product['title']}</a></h3>
            <p>価格: {product['price']}</p>
            <p>レビュー: {product['review_avg']} ({product['review_count']}件)</p>
        </div>
        """
    return html

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

            products.append({
                "title": data['title'],
                "price": f"¥{data['price']:,}",
                "review_avg": data['review'],
                "review_count": data['count'],
                "image": data['image'],
                "url": data['url']
            })

        # セッションに保存
        st.session_state["products"] = products
        st.session_state["output_md"] = output_md

        st.markdown("---")
        st.download_button("📄 Markdown記事をダウンロード", data=output_md, file_name="rakuten_summary.md", mime="text/markdown")

# セッションに保存された商品情報があればHTML出力ボタンを表示
if "products" in st.session_state and st.session_state["products"]:
    if st.button("HTML記事として出力"):
        html_content = generate_html(st.session_state["products"])
        st.markdown("### 💾 コピーしてブログに貼り付けてください")
        st.code(html_content, language='html')

def generate_html(products: list) -> str:
    html = "<h2>楽天商品比較まとめ</h2>\n"
    for product in products:
        html += f"""
        <div style="margin-bottom: 20px;">
            <h3><a href="{product['url']}" target="_blank">{product['title']}</a></h3>
            <p>価格: {product['price']}</p>
            <p>レビュー: {product['review_avg']} ({product['review_count']}件)</p>
        </div>
        """
    return html

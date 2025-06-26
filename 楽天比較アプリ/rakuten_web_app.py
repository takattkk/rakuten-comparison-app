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

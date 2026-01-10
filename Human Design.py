import streamlit as st
import google.generativeai as genai
import os
import time
from PIL import Image

# --- 1. 設定與讀取知識庫 ---
st.set_page_config(page_title="YG 人類圖全能大腦", layout="wide")

@st.cache_data(show_spinner=False)
def get_knowledge_base():
    base_path = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_path, "knowledge_base.txt")
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            st.error(f"讀取檔案失敗: {e}")
    return None

knowledge_context = get_knowledge_base()

# --- 2. 側邊欄 ---
with st.sidebar:
    st.header("🔑 系統設定")
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
        st.success("✅ API 金鑰已載入")
    else:
        api_key = st.text_input("請輸入 Gemini API Key", type="password")
    
    st.divider()
    st.caption("版本：2.6 (極致流量優化版)")
    st.caption("作者：李晏駒 (YG)")

# --- 3. 主畫面 ---
st.title("🛡️ 人類圖全自動解答系統：職涯財賦版")

tab_manual, tab_ai = st.tabs(["✍️ 手動輸入分析", "📸 截圖自動辨識"])

with tab_manual:
    st.subheader("請輸入數據")
    c1, c2 = st.columns(2)
    with c1:
        u_type = st.selectbox("1. 您的類型", ["生產者", "顯示生產者", "投射者", "顯示者", "反映者"])
        u_auth = st.text_input("2. 內在權威")
    with c2:
        u_ch = st.text_input("3. 通道數字")
        u_gt = st.text_input("4. 閘門數字")

    user_query = st.text_area("💬 您特別想問什麼？", placeholder="例如：我想月入 30 萬該怎麼做？")

    if st.button("🚀 啟動 AI 大腦深度分析", use_container_width=True):
        if not api_key:
            st.error("❌ 請先設定 API 金鑰")
        elif not knowledge_context:
            st.error("❌ 找不到知識庫檔案")
        else:
            with st.spinner("AI 正在深度檢索文獻 (免費版約需 30-60 秒)..."):
                try:
                    genai.configure(api_key=api_key)
                    
                    # 測試發現 2.0-flash 免費版限制較多，若 429 則改用 1.5-flash
                    model_name = 'gemini-2.0-flash'
                    model = genai.GenerativeModel(model_name)
                    
                    # 【終極優化】：只抓取前 5 萬字元，這能極大提高成功率
                    # 5 萬字元已包含大量人類圖核心解析
                    optimized_context = knowledge_context[:50000]
                    
                    prompt = f"""
                    你是一位人類圖職涯導師。請根據以下文獻核心：
                    {optimized_context}
                    
                    數據：類型 {u_type}, 權威 {u_auth}, 通道 {u_ch}, 閘門 {u_gt}
                    問題：{user_query}
                    請直接給出具體且具備洞察力的賺錢建議。請用繁體中文。
                    """
                    
                    response = model.generate_content(prompt)
                    st.success("### 📜 深度分析報告")
                    st.markdown(response.text)
                except Exception as e:
                    if "429" in str(e):
                        st.warning("⚠️ 免費版 API 正在冷卻。請等待 45 秒後再試，或嘗試更換 API Key。")
                    else:
                        st.error(f"分析失敗：{e}")

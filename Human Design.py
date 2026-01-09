import streamlit as st
import google.generativeai as genai
import os
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
    st.caption("版本：2.5 (流量穩定版)")
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
            with st.spinner("AI 正在翻閱 7 本文獻，請稍候..."):
                try:
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel('gemini-2.0-flash')
                    
                    # 【關鍵優化】：將 context 限制在 15 萬字元內
                    # 這大約等於 20-30 萬 Token，能確保在免費版的 TPM (每分鐘 Token 限制) 內安全運作
                    safe_context = knowledge_context[:150000] 
                    
                    prompt = f"""
                    你是一位精通人類圖職涯與財富的導師。
                    請根據這份文獻精華內容回答：
                    --- 文獻開始 ---
                    {safe_context}
                    --- 文獻結束 ---
                    
                    使用者數據：
                    類型：{u_type} / 權威：{u_auth} / 通道：{u_ch} / 閘門：{u_gt}
                    
                    問題：{user_query}
                    
                    請給出極其具體、根據書中邏輯的職涯與賺錢建議。請以繁體中文回答。
                    """
                    
                    response = model.generate_content(prompt)
                    st.success("### 📜 深度分析報告")
                    st.markdown(response.text)
                except Exception as e:
                    if "429" in str(e):
                        st.error("⚠️ 目前流量擁擠！請『等待 60 秒』後再按一次按鈕，這是免費版 API 的限制。")
                    else:
                        st.error(f"系統分析失敗：{e}")

# 辨識分頁部分邏輯相同，建議同步修改模型名稱為 gemini-2.0-flash

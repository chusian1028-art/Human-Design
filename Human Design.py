import streamlit as st
import google.generativeai as genai
import os
from PIL import Image

st.set_page_config(page_title="YG 人類圖全能大腦", layout="wide")

@st.cache_data(show_spinner=False)
def get_knowledge_base():
    base_path = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_path, "knowledge_base.txt")
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    return None

knowledge_context = get_knowledge_base()

with st.sidebar:
    st.header("🔑 系統設定")
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
    else:
        api_key = st.text_input("請輸入 Gemini API Key", type="password")
    
    # 診斷功能：列出模型
    if st.button("🔍 診斷：測試 API 權限"):
        if api_key:
            try:
                genai.configure(api_key=api_key)
                models = [m.name for m in genai.list_models()]
                st.write("您的 API Key 可用的模型列表：")
                st.code("\n".join(models))
            except Exception as e:
                st.error(f"診斷失敗：{e}")

    st.divider()
    st.caption("版本：2.3 (診斷增強版)")
    st.caption("作者：李晏駒 (YG)")

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

    user_query = st.text_area("💬 您特別想問什麼？")

    if st.button("🚀 啟動 AI 大腦深度分析", use_container_width=True):
        if not api_key:
            st.error("❌ 尚未設定 API 金鑰")
        elif not knowledge_context:
            st.error("❌ 找不到知識庫檔案")
        else:
            with st.spinner("AI 正在分析..."):
                try:
                    genai.configure(api_key=api_key)
                    # 嘗試加上完整路徑
                    model = genai.GenerativeModel('models/gemini-1.5-flash')
                    
                    prompt = f"請根據以下知識庫內容：\n{knowledge_context[:800000]}\n\n使用者數據：類型 {u_type}, 權威 {u_auth}, 通道 {u_ch}, 閘門 {u_gt}\n問題：{user_query}\n請詳細回答。"
                    
                    response = model.generate_content(prompt)
                    st.success("### 分析報告")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"系統分析失敗：{e}\n提示：請嘗試點選左側『診斷』按鈕確認模型名稱。")

# 辨識分頁省略，邏輯相同

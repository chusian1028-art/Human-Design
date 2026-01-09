import streamlit as st
import google.generativeai as genai
import os
from PIL import Image

# --- 1. 設定與讀取知識庫 ---
st.set_page_config(page_title="YG 人類圖全能大腦", layout="wide")

@st.cache_data(show_spinner=False)
def get_knowledge_base():
    """讀取合併後的知識庫檔案"""
    base_path = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_path, "knowledge_base.txt")
    
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                if content.strip():
                    return content
        except Exception as e:
            st.error(f"讀取檔案時發生錯誤: {e}")
            return None
    return None

knowledge_context = get_knowledge_base()

# --- 2. 側邊欄：API Key 與 診斷功能 ---
with st.sidebar:
    st.header("🔑 系統設定")
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
        st.success("✅ API 金鑰已載入")
    else:
        api_key = st.text_input("請輸入 Gemini API Key", type="password")
    
    if st.button("🔍 測試 API 權限"):
        if api_key:
            try:
                genai.configure(api_key=api_key)
                models = [m.name for m in genai.list_models()]
                st.write("可用模型：")
                st.code("\n".join(models))
            except Exception as e:
                st.error(f"診斷失敗：{e}")
    
    st.divider()
    st.caption("版本：2.4 (2.0-Flash 升級版)")
    st.caption("作者：李晏駒 (YG)")

# --- 3. 主畫面介面 ---
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
            st.error("❌ 找不到知識庫檔案 `knowledge_base.txt`，請確認已上傳")
        else:
            with st.spinner("AI 正在翻閱文獻..."):
                try:
                    genai.configure(api_key=api_key)
                    # 關鍵修正：改用診斷清單中確定的模型名稱
                    model = genai.GenerativeModel('gemini-2.0-flash')
                    
                    prompt = f"""
                    你是一位人類圖專家。背景知識：
                    {knowledge_context[:900000]}
                    
                    使用者數據：{u_type}, {u_auth}, 通道:{u_ch}, 閘門:{u_gt}
                    問題：{user_query}
                    請精確回答。
                    """
                    response = model.generate_content(prompt)
                    st.success("### 📜 深度分析報告")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"系統分析失敗：{e}")

with tab_ai:
    st.header("📸 AI 掃描辨識")
    up_img = st.file_uploader("請上傳人類圖截圖", type=["png", "jpg", "jpeg"])
    if up_img:
        img = Image.open(up_img)
        st.image(img, width=300)
        if st.button("啟動 AI 判讀"):
            if api_key:
                try:
                    genai.configure(api_key=api_key)
                    # 同樣換成 2.0-flash
                    model = genai.GenerativeModel('gemini-2.0-flash')
                    res = model.generate_content(["識別此圖的類型、權威、通道、閘門。", img])
                    st.info(f"AI 識別結果：\n\n{res.text}")
                except Exception as e:
                    st.error(f"辨識失敗：{e}")

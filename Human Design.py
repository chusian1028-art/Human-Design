import streamlit as st
import google.generativeai as genai
import os

# --- 1. 系統設定與知識庫讀取 ---
st.set_page_config(page_title="YG 人類圖全能大腦", layout="wide")

@st.cache_data(show_spinner=False)
def get_knowledge_base():
    base_path = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_path, "knowledge_base.txt")
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    return None

# 定義一個搜尋函數，優先從你的資料中抓取相關內容
def find_relevant_content(full_text, keywords):
    """
    在文獻中搜尋包含關鍵字的段落
    """
    paragraphs = full_text.split('\n')
    found_segments = []
    
    for para in paragraphs:
        # 如果段落裡包含任何一個關鍵字（如：投射者、26 閘門等）
        if any(keyword in para for keyword in keywords if keyword):
            found_segments.append(para)
            if len(found_segments) > 50: # 抓取前 50 條相關資訊即可，避免太多
                break
    
    return "\n".join(found_segments)

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
    st.caption("版本：3.0 (文獻檢索優先版)")
    st.caption("作者：李晏駒 (YG)")

# --- 3. 主畫面 ---
st.title("🛡️ 人類圖解答系統：文獻檢索版")
st.info("本版本會先搜尋您的 7 本文獻，僅將相關片段交給 AI 進行繁體中文分析，解決擁擠問題。")

st.subheader("請輸入數據")
c1, c2 = st.columns(2)
with c1:
    u_type = st.selectbox("1. 您的類型", ["投射者", "生產者", "顯示生產者", "顯示者", "反映者"])
    u_auth = st.text_input("2. 內在權威 (如: 直覺)")
with c2:
    u_ch = st.text_input("3. 通道數字 (如: 10-20)")
    u_gt = st.text_input("4. 閘門數字 (如: 26, 51)")

user_query = st.text_area("💬 您特別想問什麼？", placeholder="例如：我想月入 30 萬該怎麼做？")

if st.button("🚀 啟動文獻檢索與深度分析", use_container_width=True):
    if not api_key:
        st.error("❌ 請輸入 API Key")
    elif not knowledge_context:
        st.error("❌ 找不到 `knowledge_base.txt` 檔案")
    else:
        with st.spinner("正在掃描文獻並分析中..."):
            try:
                # 準備關鍵字清單
                keywords = [u_type, u_auth]
                if u_ch: keywords.extend(u_ch.replace('-', ',').split(','))
                if u_gt: keywords.extend(u_gt.replace(' ', '').split(','))
                
                # 第一步：先從你的 txt 檔案裡過濾資料
                relevant_data = find_relevant_content(knowledge_context, keywords)
                
                if not relevant_data:
                    relevant_data = "（文獻中未找到直接關鍵字，請 AI 根據通用人類圖知識回答）"

                # 第二步：把精簡過的資料給 AI
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.0-flash')
                
                prompt = f"""
                你是一位人類圖財富導師，請優先根據以下從使用者的 7 本文獻中檢索出的片段進行回答。
                
                【文獻檢索片段】：
                {relevant_data[:10000]}  # 傳送量縮減為原來的 1%，保證不塞車
                
                【使用者人類圖數據】：
                類型：{u_type} / 權威：{u_auth} / 通道：{u_ch} / 閘門：{u_gt}
                
                【使用者問題】：
                {user_query}
                
                請嚴格遵守：
                1. 回答必須使用「繁體中文」。
                2. 優先引用文獻內容，若文獻不足，再結合人類圖專業知識。
                3. 針對「月入 30 萬」這個目標，給出極具操作性的職涯與賺錢建議。
                """
                
                response = model.generate_content(prompt)
                st.success("### 📜 深度分析報告 (繁體中文)")
                st.markdown(response.text)
                
            except Exception as e:
                st.error(f"分析失敗：{e}")

st.divider()
st.caption("資料來源：YG 自媒體事業專屬知識庫。建議回歸內在權威做決定。")

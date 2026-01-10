import streamlit as st
import google.generativeai as genai
import os
import re

# --- 1. 系統設定與讀取 ---
st.set_page_config(page_title="YG 人類圖全能大腦", layout="wide")

@st.cache_data(show_spinner=False)
def get_knowledge_base():
    base_path = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_path, "knowledge_base.txt")
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read().split('\n\n') # 以段落切分
    return []

def local_search(paragraphs, keywords):
    """本地端搜尋，過濾出最相關的文獻段落"""
    results = []
    for para in paragraphs:
        if any(key.strip() in para for key in keywords if key.strip()):
            results.append(para.strip())
            if len(results) > 15: # 限制數量，確保不爆 API 流量
                break
    return "\n\n".join(results)

all_paragraphs = get_knowledge_base()

# --- 2. 側邊欄：API 與 版本資訊 ---
with st.sidebar:
    st.header("🔑 系統設定")
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
        st.success("✅ API 金鑰已載入")
    else:
        api_key = st.text_input("請輸入 Gemini API Key", type="password")
    
    st.divider()
    st.caption("版本：3.8 (AI 繁體整理版)")
    st.caption("作者：李晏駒 (YG)")

# --- 3. 主畫面 ---
st.title("🛡️ 人類圖深度分析：職涯財賦版")

c1, c2 = st.columns(2)
with c1:
    u_type = st.selectbox("您的類型", ["投射者", "生產者", "顯示生產者", "顯示者", "反映者"])
    u_auth = st.text_input("內在權威", value="直覺")
with c2:
    u_ch = st.text_input("通道數字", placeholder="10-20, 7-31")
    u_gt = st.text_area("閘門數字 (可貼上一長串)", value="31,41,10,15,7,4,20,64,13,54,43,28,27,14,26,45,14,9,62,46,,19,38,54,43")

user_query = st.text_area("💬 您特別想問什麼？", value="我要月入30萬，該怎麼發揮天賦？")

if st.button("🚀 啟動 AI 深度文獻整理", use_container_width=True):
    if not api_key:
        st.error("❌ 請輸入 API Key")
    elif not all_paragraphs:
        st.error("❌ 找不到文獻檔案")
    else:
        with st.spinner("正在搜尋文獻並由 AI 整理報告中..."):
            try:
                # 第一步：整理搜尋關鍵字
                ch_list = re.split(r'[,\s-]+', u_ch) if u_ch else []
                gt_list = re.split(r'[,\s]+', u_gt) if u_gt else []
                search_terms = [u_type, u_auth] + ch_list + gt_list
                
                # 第二步：本地搜尋 (不花錢、不限流)
                relevant_context = local_search(all_paragraphs, search_terms)
                
                # 第三步：交給 AI 整理
                genai.configure(api_key=api_key)
                # 使用你清單中確定的 2.0-flash
                model = genai.GenerativeModel('gemini-2.0-flash')
                
                prompt = f"""
                你是人類圖財賦專家。請根據以下從使用者 7 本文獻中抓取出的【原文片段】進行整理。
                
                【任務】：
                1. 將所有內容整理為「繁體中文」。
                2. 針對使用者的目標「{user_query}」進行深度對齊。
                3. 以結構化方式輸出：類型優勢、關鍵通道解讀、以及具體的「月入 30 萬」致富路徑。
                
                【文獻原文】：
                {relevant_context}
                
                【使用者數據】：
                類型：{u_type} / 權威：{u_auth} / 通道：{u_ch} / 閘門：{u_gt}
                """
                
                response = model.generate_content(prompt)
                
                st.success("### 📜 深度分析報告 (繁體中文整理版)")
                st.markdown(response.text)
                
            except Exception as e:
                st.error(f"系統分析失敗：{e}")

st.divider()
st.caption("資料來源：YG 專屬人類圖文獻庫。建議回歸內在權威做決定。")

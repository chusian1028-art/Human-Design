import streamlit as st
import google.generativeai as genai
import os

# --- 1. 設定與讀取知識庫 ---
st.set_page_config(page_title="YG 人類圖全能大腦", layout="wide")

@st.cache_data(show_spinner=False)
def get_knowledge_base():
    base_path = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_path, "knowledge_base.txt")
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    return None

def smart_search(full_text, keywords):
    """精準搜尋關鍵字相關段落，避免爆流量"""
    if not full_text: return ""
    lines = full_text.split('\n')
    relevant_chunks = []
    
    # 搜尋包含類型、權威或通道數字的行
    for line in lines:
        if any(key in line for key in keywords if key):
            relevant_chunks.append(line)
            if len(relevant_chunks) > 100: # 限制長度，確保不超過免費版上限
                break
    return "\n".join(relevant_chunks)

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
    st.caption("版本：3.7 (精準檢索避災版)")
    st.caption("作者：李晏駒 (YG)")

# --- 3. 主畫面 ---
st.title("🛡️ 人類圖解答系統：文獻精準檢索版")
st.info("已優化流量：系統會先在 2.25MB 文獻中搜尋與您相關的段落，再交由 AI 分析，徹底解決擁擠問題。")

st.subheader("請輸入數據")
c1, c2 = st.columns(2)
with c1:
    u_type = st.selectbox("您的類型", ["投射者", "生產者", "顯示生產者", "顯示者", "反映者"])
    u_auth = st.text_input("內在權威 (如: 直覺)")
with c2:
    u_ch = st.text_input("通道數字 (如: 10-20)")
    u_gt = st.text_input("閘門數字 (如: 26, 51)")

user_query = st.text_area("💬 您特別想問什麼？", placeholder="例如：我想月入 30 萬該怎麼做？")

if st.button("🚀 啟動深度分析", use_container_width=True):
    if not api_key:
        st.error("❌ 請輸入 API Key")
    elif not knowledge_context:
        st.error("❌ 找不到 `knowledge_base.txt`，請檢查 GitHub 檔案。")
    else:
        with st.spinner("正在精準檢索文獻內容..."):
            try:
                # 1. 建立關鍵字清單 (包含類型、數字等)
                search_keys = [u_type, u_auth]
                if u_ch: search_keys.extend(u_ch.replace('-', ' ').split())
                if u_gt: search_keys.extend(u_gt.replace(',', ' ').split())
                
                # 2. 本地搜尋，不佔用 API 流量
                filtered_info = smart_search(knowledge_context, search_keys)
                
                # 3. 呼叫 AI (使用你清單中確定的 2.0-flash)
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.0-flash')
                
                prompt = f"""
                你是一位人類圖專家。請根據以下從使用者的 7 本經典文獻中檢索出的【相關片段】來回答問題。
                如果文獻片段中沒有提到，請結合你專業的人類圖知識庫。
                
                【文獻片段】：
                {filtered_info}
                
                【使用者人類圖數據】：
                類型：{u_type} / 權威：{u_auth} / 通道：{u_ch} / 閘門：{u_gt}
                
                【問題】：
                {user_query}
                
                【要求】：
                1. 必須使用「繁體中文」回答。
                2. 請針對「月入 30 萬」這個目標，根據其人類圖的原廠設定，給出最具體的策略與職涯建議。
                """
                
                response = model.generate_content(prompt)
                st.success("### 📜 深度分析報告 (繁體中文)")
                st.markdown(response.text)
                
            except Exception as e:
                if "429" in str(e):
                    st.error("⚠️ 流量限制：請等待 30 秒後再試。若持續發生，建議更換 API Key。")
                else:
                    st.error(f"系統分析失敗：{e}")

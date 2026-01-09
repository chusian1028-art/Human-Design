import streamlit as st
import google.generativeai as genai
import os

# --- 1. 設定與讀取知識庫 ---
st.set_page_config(page_title="YG 人類圖全能大腦", layout="wide")

@st.cache_data
def get_knowledge_base():
    """讀取合併後的 7 本書知識庫檔案"""
    file_path = "knowledge_base.txt"
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    return None

knowledge_context = get_knowledge_base()

# --- 2. 側邊欄：API Key 設定 ---
with st.sidebar:
    st.header("🔑 系統設定")
    # 優先從 Streamlit Secrets 讀取，若無則顯示輸入框
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
        st.success("✅ API 金鑰已從系統安全設定中載入")
    else:
        api_key = st.sidebar.text_input("請輸入 Gemini API Key", type="password")
        st.info("💡 建議將 API Key 設定在 Streamlit 後台的 Secrets 中以保證安全。")
    
    st.divider()
    st.caption("版本：2.0 (全資料庫連動版)")
    st.caption("作者：李晏駒 (YG)")

# --- 3. 主畫面介面 ---
st.title("🛡️ 人類圖全自動解答系統：職涯財賦版")
st.write("本系統已連動 7 本經典文獻，會直接根據書本內容回答你的職場原廠設定。")

# 建立分頁
tab_manual, tab_ai = st.tabs(["✍️ 手動輸入分析", "📸 截圖自動辨識"])

# --- 分頁：手動輸入 ---
with tab_manual:
    st.subheader("請輸入你的人類圖數據")
    c1, c2 = st.columns(2)
    with c1:
        u_type = st.selectbox("1. 您的類型", ["生產者", "顯示生產者", "投射者", "顯示者", "反映者"])
        u_auth = st.text_input("2. 內在權威 (如: 情緒, 薦骨)")
    with c2:
        u_ch = st.text_input("3. 通道數字 (如: 10-20, 26-44)")
        u_gt = st.text_input("4. 閘門數字 (如: 26, 56, 1)")

    user_query = st.text_area("💬 您特別想問什麼？", placeholder="例如：根據我的通道，我在自媒體事業該如何發揮天賦賺錢？")

    if st.button("🚀 啟動 AI 大腦深度分析", use_container_width=True):
        if not api_key:
            st.error("❌ 尚未設定 API 金鑰，請在左側選單填寫。")
        elif not knowledge_context:
            st.error("❌ 在 GitHub 倉庫中找不到 `knowledge_base.txt`，請確認檔案已上傳。")
        else:
            with st.spinner("AI 正在翻閱 7 本經典文獻，為您尋找正確答案..."):
                try:
                    genai.configure(api_key=api_key)
                    # 使用 Gemini 1.5 Pro，具備超大緩存空間處理數十萬字內容
                    model = genai.GenerativeModel('gemini-1.5-pro')
                    
                    # 構建 Prompt (給 AI 的超級指令)
                    prompt = f"""
                    你是一位精通人類圖財富與職涯的專家。
                    你的知識背景是以下提供的『知識庫』全文內容：
                    --- 知識庫開始 ---
                    {knowledge_context[:800000]}  # 傳送內容供 AI 檢索
                    --- 知識庫結束 ---
                    
                    使用者的數據：
                    - 類型：{u_type}
                    - 權威：{u_auth}
                    - 通道：{u_ch}
                    - 閘門：{u_gt}
                    
                    問題：{user_query}
                    
                    請嚴格根據知識庫中的內容（特別是《人類圖財賦密碼》、《找回原廠設定》），
                    直接給予最精確、詳細的職涯與賺錢建議。請不要只給頁碼，要給出書中的具體解讀。
                    請用溫暖且具備洞察力的口吻，並以繁體中文回答。
                    """
                    
                    response = model.generate_content(prompt)
                    st.success("### 📜 深度分析報告 (根據文獻解答)")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"系統分析失敗：{e}")

# --- 分頁：截圖辨識 ---
with tab_ai:
    st.header("📸 AI 掃描辨識")
    up_img = st.file_uploader("請上傳人類圖截圖", type=["png", "jpg", "jpeg"])
    if up_img:
        st.image(up_img, width=300)
        if st.button("啟動 AI 判讀"):
            if api_key:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-1.5-pro')
                res = model.generate_content(["請識別此人類圖的類型、通道與閘門數字，用繁體中文回答。", Image.open(up_img)])
                st.info(f"AI 識別結果：\n\n{res.text}")
                st.write("💡 識別後，您可以將數據填入『手動輸入』標籤以獲取深度報告。")

st.divider()
st.caption("資料來源：人類圖大資料庫 (YG 自媒體事業專屬)。建議回歸內在權威做決定。")

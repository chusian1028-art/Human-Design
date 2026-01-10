import streamlit as st
import google.generativeai as genai
import os
import time

# --- 1. 系統設定 ---
st.set_page_config(page_title="YG 人類圖全能大腦", layout="wide")

# --- 2. 側邊欄：API 設定 ---
with st.sidebar:
    st.header("🔑 系統設定")
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
        st.success("✅ API 金鑰已載入")
    else:
        api_key = st.text_input("請輸入 Gemini API Key", type="password")
    
    st.divider()
    st.caption("版本：3.5 (檔案預載穩定版)")
    st.caption("作者：李晏駒 (YG)")

# --- 3. 核心功能：上傳檔案至 Google ---
def upload_to_gemini(path):
    """將檔案上傳至 Google File API，避免占用 Prompt 流量"""
    try:
        file = genai.upload_file(path=path, mime_type="text/plain")
        while file.state.name == "PROCESSING":
            time.sleep(2)
            file = genai.get_file(file.name)
        return file
    except Exception as e:
        st.error(f"檔案預載失敗：{e}")
        return None

# --- 4. 主畫面 ---
st.title("🛡️ 人類圖解答系統：文獻雲端檢索版")
st.info("本版本將 2.25MB 文獻直接上傳雲端，不再佔用對話流量，徹底解決 429 擁擠問題。")

st.subheader("請輸入數據")
c1, c2 = st.columns(2)
with c1:
    u_type = st.selectbox("您的類型", ["投射者", "生產者", "顯示生產者", "顯示者", "反映者"])
    u_auth = st.text_input("內在權威 (如: 直覺)")
with c2:
    u_ch = st.text_input("通道數字 (如: 10-20)")
    u_gt = st.text_input("閘門數字 (如: 26, 51)")

user_query = st.text_area("💬 您特別想問什麼？", placeholder="例如：我想月入 30 萬該怎麼做？")

if st.button("🚀 啟動雲端文獻深度分析", use_container_width=True):
    if not api_key:
        st.error("❌ 請輸入 API Key")
    else:
        with st.spinner("正在雲端翻閱 7 本文獻... (此方式最省流量)"):
            try:
                genai.configure(api_key=api_key)
                
                # 為了穩定性，免費版建議使用 1.5-flash，它對文件處理非常強大
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # 取得本機檔案路徑
                base_path = os.path.dirname(os.path.abspath(__file__))
                txt_path = os.path.join(base_path, "knowledge_base.txt")
                
                if not os.path.exists(txt_path):
                    st.error("❌ 找不到 knowledge_base.txt，請確認檔案已上傳至 GitHub。")
                else:
                    # 把檔案送上雲端
                    uploaded_file = upload_to_gemini(txt_path)
                    
                    if uploaded_file:
                        # 這是最省流量的 Prompt：直接叫 AI 去看雲端那份檔案
                        prompt = f"""
                        你是人類圖專家。請根據上傳的文獻內容回答。
                        
                        使用者數據：
                        - 類型：{u_type}
                        - 權威：{u_auth}
                        - 通道：{u_ch}
                        - 閘門：{u_gt}
                        
                        問題：{user_query}
                        
                        請嚴格執行：
                        1. 必須全程使用「繁體中文」回答。
                        2. 優先從文獻中尋找關於「{u_type}」和「{u_ch}」的具體建議。
                        3. 針對「月入 30 萬」目標，提供這份人類圖原廠設定下的具體致富路徑。
                        """
                        
                        # 同時傳送檔案與指令
                        response = model.generate_content([uploaded_file, prompt])
                        
                        st.success("### 📜 深度分析報告 (根據文獻解讀)")
                        st.markdown(response.text)
                        
                        # 回答完後刪除雲端暫存檔（保護隱私且節省空間）
                        genai.delete_file(uploaded_file.name)
                        
            except Exception as e:
                if "429" in str(e):
                    st.error("⚠️ 流量限制：請等待 30 秒後再按一次。")
                else:
                    st.error(f"系統分析失敗：{e}")

import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

# 1. 串接 Gemini API (從 Streamlit Secrets 讀取金鑰)
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=GOOGLE_API_KEY)
except:
    st.error("請先在 Streamlit Secrets 中設定 GOOGLE_API_KEY")

# 2. 從資料庫中提取的內容 (確保內容準確)
HD_DATABASE = {
    "types": {
        "生產者": "【打造世界的偉大創造者】具備強大的薦骨動能，是生來建造世界的偉大工作者。策略是「等待回應」，當你快樂投入真心喜愛的事時，能建立屬於自己的王國。",
        "顯示生產者": "【重視效率的工作者】手腳明快、有效率，傾向先求有再求好。策略同樣是「等待回應」，需學習耐性以免浪費能量。",
        "投射者": "【新一代的領導者】專長是協助並支持生產者工作得更有效率，適合作為傑出的顧問、管理者與協調者。策略是「等待被邀請」，唯有被看見才華並獲邀，才能發揮真正影響力。",
        "顯示者": "【唯一能主動發起的類型】具備強大發起行動並影響眾人的能力，是天然的領導者原型。策略是「告知」，在行動前告知相關人士可大幅降低抗拒。",
        "反映者": "【環境的仲裁者】能體驗並評斷整體環境的品質，反映出周遭人事物狀態。策略是「等待28天」，需隨月亮週期運轉以獲得清明決定。"
    },
    "career_advice": {
        "閘門 1": "【創意自我表達】適合藝術、寫作或任何能展現獨特個人觀點的創意工作。",
        "閘門 11": "【教育與想法】天生的教師，適合傳達知識、分享啟發性理念與哲學。",
        "閘門 13": "【傾聽者】具備深層聆聽天賦，適合輔導、諮商或需要協助他人重新連結人生目的之職務。"
    }
}

# 3. 定義 AI 讀圖邏輯
def analyze_chart(image):
    model = genai.GenerativeModel('gemini-1.5-pro')
    prompt = """
    這是一張人類圖截圖。請幫我分析圖中的文字，並回傳以下資訊：
    1. 類型 (如：生產者、投射者、顯示者、反映者)
    2. 有定義（有顏色）的通道 (例如 26-44, 10-20 等)
    3. 有定義（有顏色）的閘門數字列表。
    請用繁體中文回答，格式請固定為：
    類型: [結果]
    通道: [數字組合]
    閘門: [數字列表]
    """
    response = model.generate_content([prompt, image])
    return response.text

# 4. Streamlit 介面設計
st.title("💡 人類圖全自動職業建議儀")
st.write("上傳截圖，讓 AI 同時為你判讀人類圖並提供《財賦密碼》建議！")

uploaded_file = st.file_uploader("請上傳人類圖截圖...", type=["png", "jpg", "jpeg"])

if uploaded_file:
    img = Image.open(uploaded_file)
    st.image(img, width=300)
    
    with st.spinner("AI 正在深度判讀圖表內容..."):
        try:
            analysis_result = analyze_chart(img)
            st.subheader("🤖 AI 判讀結果")
            st.code(analysis_result)
            
            # 根據 AI 判讀結果展示資料庫建議 (此處可進一步寫解析邏輯)
            if "生產者" in analysis_result:
                st.success(f"**您的類型建議：** {HD_DATABASE['types']['生產者']}")
            elif "投射者" in analysis_result:
                st.success(f"**您的類型建議：** {HD_DATABASE['types']['投射者']}")
            # ... 其他類型的解析邏輯
            
        except Exception as e:
            st.error(f"分析失敗，請檢查 API 設定或圖片品質。錯誤訊息：{e}")

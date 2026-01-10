import streamlit as st
import os
import re

# --- 1. 系統設定 ---
st.set_page_config(page_title="YG 人類圖文獻檢索系統", layout="wide")

# --- 2. 核心搜尋引擎 (純 Python 處理) ---
@st.cache_data(show_spinner=False)
def get_knowledge_base():
    base_path = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_path, "knowledge_base.txt")
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            # 讀取並以「雙換行」切分段落，這通常是書中知識點的自然分隔
            content = f.read()
            return content.split('\n\n')
    return []

def keyword_search(paragraphs, keywords):
    """
    精準搜尋包含關鍵字的段落，並去除重複
    """
    results = []
    for para in paragraphs:
        # 只要段落中包含任何一個關鍵字，就抓出來
        if any(key.strip() in para for key in keywords if key.strip()):
            results.append(para.strip())
    # 去除重複段落並保持順序
    return list(dict.fromkeys(results))

# 預載入文獻
all_paragraphs = get_knowledge_base()

# --- 3. 主畫面介面 ---
st.title("🛡️ 人類圖原廠設定：文獻自動檢索系統")
st.markdown("---")

if not all_paragraphs:
    st.error("❌ 找不到 `knowledge_base.txt`，請確認檔案已上傳至 GitHub 根目錄。")
else:
    # 介面佈局
    with st.container():
        st.subheader("📊 輸入您的數據")
        c1, c2, c3 = st.columns([2, 2, 3])
        
        with c1:
            u_type = st.selectbox("1. 您的類型", ["投射者", "生產者", "顯示生產者", "顯示者", "反映者"])
            u_auth = st.text_input("2. 內在權威", value="直覺")
            
        with c2:
            u_ch = st.text_input("3. 通道數字 (用空格或逗號分開)", placeholder="10-20, 7-31")
            u_gt = st.text_input("4. 閘門數字 (用逗號分開)", placeholder="31, 41, 10...")
            
        with c3:
            st.info("💡 **系統說明**：\n本系統將直接檢索您提供的 7 本人類圖文獻。不使用 AI API，因此不受流量限制。建議針對特定閘門查看原文解說。")

    if st.button("🚀 啟動文獻全方位檢索", use_container_width=True):
        # 整理關鍵字
        # 處理通道：把 10-20 拆成 10, 20
        ch_list = re.split(r'[,\s-]+', u_ch) if u_ch else []
        # 處理閘門：拆分數字
        gt_list = re.split(r'[,\s]+', u_gt) if u_gt else []
        
        # 建立搜尋清單 (類型、權威、通道、閘門)
        search_terms = [u_type, u_auth] + ch_list + gt_list
        search_terms = [t for t in search_terms if t] # 過濾空值

        st.success(f"🔍 正在針對關鍵字：{', '.join(search_terms)} 進行文獻比對...")

        # 執行搜尋
        found_content = keyword_search(all_paragraphs, search_terms)

        if found_content:
            # 使用 Tabs 呈現不同分類，畫面更整潔
            tab1, tab2 = st.tabs(["📜 相關文獻原文", "📌 關鍵字速查"])
            
            with tab1:
                st.write(f"共找到 {len(found_content)} 段相關文獻片段：")
                for i, text in enumerate(found_content):
                    with st.expander(f"文獻片段 {i+1}", expanded=(i==0)):
                        st.markdown(text)
            
            with tab2:
                st.write("您可以利用瀏覽器搜尋 (Ctrl+F) 在下方快速定位：")
                full_result = "\n\n---\n\n".join(found_content)
                st.text_area("所有結果全文：", value=full_result, height=500)
        else:
            st.warning("⚠️ 在文獻中找不到與您輸入數據完全匹配的文字，請嘗試簡化關鍵字（例如只輸入數字）。")

st.divider()
st.caption("資料來源：李晏駒 (YG) 專屬人類圖大資料庫。本系統僅提供文獻檢索，不代表醫療或職業診斷建議。")

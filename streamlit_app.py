import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
from collections import defaultdict
import threading
import time
import os

# ✅ 구글 시트 인증
scopes = ["https://www.googleapis.com/auth/spreadsheets"]
credentials = Credentials.from_service_account_info(
    dict(st.secrets["gcp_service_account"]),
    scopes=scopes
)
client = gspread.authorize(credentials)

# ✅ 시트에서 데이터 가져오는 함수
def fetch_sheet_data():
    worksheet = client.open_by_key("1Q1RbrQJ4mipUzogBpfN6dY6TOOLxrYZPkRpvlANUAo8").worksheet("시트4")
    rows = worksheet.get_all_values()
    return pd.DataFrame(rows)

# ✅ 30분마다 Excel 업데이트하는 스레드 함수
def update_excel_every_30_minutes():
    while True:
        try:
            df = fetch_sheet_data()
            if os.path.exists("data.xlsx"):
                os.remove("data.xlsx")
            df.to_excel("data.xlsx", index=False)
            print("🔄 data.xlsx 파일 업데이트 완료")
        except Exception as e:
            print(f"❌ Excel 업데이트 오류: {e}")
        time.sleep(1800)  # 30분

# ✅ 스레드 시작
threading.Thread(target=update_excel_every_30_minutes, daemon=True).start()

# ✅ data.xlsx 파일이 없으면 시트에서 최초 저장
if not os.path.exists("data.xlsx"):
    try:
        df = fetch_sheet_data()
        df.to_excel("data.xlsx", index=False)
        print("📥 최초 data.xlsx 저장 완료")
    except Exception as e:
        st.error(f"❌ 최초 Excel 생성 오류: {e}")
        st.stop()

# ✅ data.xlsx 파일 불러오기
try:
    df_raw = pd.read_excel("data.xlsx")
except Exception as e:
    st.error(f"❌ data.xlsx 파일 로딩 중 오류: {e}")
    st.stop()

# ✅ 2줄 헤더 처리
multi_header = df_raw.iloc[:2]
data = df_raw.iloc[2:].copy()
multi_columns = []
current_main = ""
for main, sub in zip(multi_header.iloc[0], multi_header.iloc[1]):
    if main:
        current_main = main
    if sub.strip() == "":
        multi_columns.append(current_main)
    else:
        multi_columns.append(f"{current_main}_{sub}")
data.columns = multi_columns
data.reset_index(drop=True, inplace=True)

# ✅ 상태 컬럼 생성
type_status_counter = defaultdict(int)
for idx, col in enumerate(data.columns):
    if "_" not in col and col not in ["이름", "전화번호뒷자리", "총이수율", "총이수율(%)", "이수여부"]:
        type_status_counter[col] += 1
        base_col = f"{col}_{type_status_counter[col]}차시"
        if base_col in data.columns:
            data[f"{base_col}_상태"] = data.iloc[:, idx]

# ✅ UI 세팅
st.set_page_config(page_title="이수율 확인 시스템", layout="centered")
st.markdown("""
<style>
.title-box {
    background-color: #003366;
    color: white;
    padding: 1.5rem;
    border-radius: 0.5rem;
    text-align: center;
    margin-bottom: 2rem;
}
.title-box h1 {
    margin-bottom: 0.2rem;
    font-size: 1.7rem;
}
.title-box p {
    font-size: 1.6rem;
    margin-top: 0.3rem;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)
st.markdown('<div class="title-box"><h1>📚 [2025 교실혁명 선도교사 양성연수]</h1><p>수강 정보 및 이수 현황 확인</p></div>', unsafe_allow_html=True)

# ✅ 사용자 입력
name = st.text_input("👤 이름을 입력하세요: ", placeholder="예: 홍길동")
phone_last4 = st.text_input("📱 전화번호 뒷 네 자리를 입력하세요: ", max_chars=4, placeholder="예: 1234")

# ✅ 수료 기준 안내
st.markdown("""
<div style="background-color:#fffbe6; border-left: 5px solid #ffc107; padding: 1.2rem 1.5rem; margin: 1.5rem 0 1rem 0; border-radius: 8px;">
    <p style="margin: 0; font-size: 1rem; line-height: 1.5;">
        📌 <b>수료 기준 안내</b><br><br>
        ✅ 전체 <b>40개 차시 중 80%(32개)</b> 이상 이수 시 수료<br>
        ✅ 각 차시는 수업 시간의 <b>80%</b> 이상 참여해야 이수 인정<br>
    </p>
</div>
""", unsafe_allow_html=True)

# ✅ 이하 사용자 검색 및 이수율 출력 로직 이어짐...

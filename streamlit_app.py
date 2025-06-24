# ✅ Streamlit + Google Sheet 기반 이수율 시스템 전체 코드

import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

# ✅ 구글 시트 인증
scopes = ["https://www.googleapis.com/auth/spreadsheets"]
credentials = Credentials.from_service_account_info(
    dict(st.secrets["gcp_service_account"]),
    scopes=scopes
)
client = gspread.authorize(credentials)

# ✅ 구글 시트 열기
try:
    sheet = client.open_by_key("1owM9EXygtbj8EO-jYL5Lr1rixU-sT8LJ_h8k1aLnSTI").sheet1
    records = sheet.get_all_records()
except Exception as e:
    st.error(f"❌ 구글 시트 접근 중 오류: {e}")
    st.stop()

# ✅ UI 설정
st.set_page_config(page_title="알파코 이수율 확인 시스템", layout="centered")

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
    .info-box {
        background-color: #f7f7f9;
        padding: 1.2rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .table-box {
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #ccc;
        margin-bottom: 1.5rem;
        background-color: #fff;
    }
    .notice-box {
        background-color:#fffbe6;
        border-left: 5px solid #ffc107;
        padding: 1.2rem 1.5rem;
        margin: 2rem 0 1rem 0;
        border-radius: 8px;
        font-size: 0.95rem;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="title-box"><h1>‍📚 2025 교실혁명 선도교사 양성연수</h1><p>이수율 조회 시스템</p></div>', unsafe_allow_html=True)

st.markdown("""
<div class="notice-box">
📌 <b>수료 기준 안내</b><br><br>
✅ 전체 <b>40개 차시 중 80%(32개 차시)</b> 이상 이수 시 수료<br>
✅ <b>2,400분 중 1,920분</b> 이상 참여 시 수료<br>
※ 단, 차시별로 80% 이상 이수 시 해당 차시 인정
</div>
""", unsafe_allow_html=True)

# ✅ 사용자 입력
name = st.text_input("👤 이름을 입력하세요: ", placeholder="예: 홍길동")
phone_last4 = st.text_input("📱 전화번호 뒷 네 자리를 입력하세요: ", max_chars=4, placeholder="예: 1234")

# ✅ 사용자 찾기 함수
def find_user(name, phone_last4):
    for user in records:
        if user["이름"] == name and str(user["전화번호뒷자리"]).zfill(4) == phone_last4:
            return user
    return None

def safe_int(value):
    value = str(value).replace("분", "")
    try:
        return int(value)
    except:
        return 0

# ✅ 조회 버튼
if st.button("📥 이수율 조회하기"):
    if not name or not phone_last4:
        st.warning("⚠️ 이름과 전화번호 뒷자리를 모두 입력해주세요.")
    else:
        user = find_user(name, phone_last4)

        if user:
            st.success(f"🎉 {user['이름']} 선생님의 이수 정보")

            # 사전진단 & 사전워크숍
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"""
                <div class='info-box'>
                    <b>① 사전진단 (2차시 / 120분)</b><br>
                    <p>{user['사전진단']}분</p>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                <div class='info-box'>
                    <b>② 사전워크숍 (3차시 / 180분)</b><br>
                    <p>{user['사전워크샵']}분</p>
                </div>
                """, unsafe_allow_html=True)

            # 원격연수 상세 테이블
            st.markdown("""
            <div class='table-box'>
                <b>③ 원격연수 (16차시 / 800분)</b><br><br>
                <table style='width:100%; border-collapse: collapse;'>
                <tr>""" +
                "".join([f"<th style='border:1px solid #ccc;'> {i+1}차시 </th>" for i in range(16)]) +
                "</tr><tr>" +
                "".join([f"<td style='border:1px solid #ccc; text-align:center;'>00분</td>" for _ in range(16)]) +
                "</tr></table>
            </div>""", unsafe_allow_html=True)

            # 집합연수
            st.markdown("""
            <div class='table-box'>
                <b>④ 집합연수 (14차시 / 700분)</b><br><br>
                <table style='width:100%; border-collapse: collapse;'>
                <tr>""" +
                "".join([f"<th style='border:1px solid #ccc;'> {i+1}차시 </th>" for i in range(14)]) +
                "</tr><tr>" +
                "".join([f"<td style='border:1px solid #ccc; text-align:center;'>00분</td>" for _ in range(14)]) +
                "</tr></table>
            </div>""", unsafe_allow_html=True)

            # 컨퍼런스
            st.markdown("""
            <div class='table-box'>
                <b>⑤ 컨퍼런스 (5차시 / 250분)</b><br><br>
                <table style='width:100%; border-collapse: collapse;'>
                <tr>""" +
                "".join([f"<th style='border:1px solid #ccc;'> {i+1}차시 </th>" for i in range(5)]) +
                "</tr><tr>" +
                "".join([f"<td style='border:1px solid #ccc; text-align:center;'>00분</td>" for _ in range(5)]) +
                "</tr></table>
            </div>""", unsafe_allow_html=True)

            # ✅ 총 이수 시간 표시
            total_minutes = sum(safe_int(user[k]) for k in ["사전진단", "사전워크샵", "원격연수", "집합연수", "컨퍼런스"])
            st.markdown(f"""
            <div style='margin-top:1.5rem;'>
                <h5>총 이수 시간 (이수율)</h5>
                <p><b>{total_minutes}분 ({user['총이수율']}%) / 2400분</b></p>
            </div>
            """, unsafe_allow_html=True)

            # ✅ 이수 여부
            if user["이수여부"] == "이수":
                st.success("✅ 이수 완료")
            else:
                st.error("📌 미이수")

        else:
            st.error("😢 입력하신 정보와 일치하는 사용자가 없습니다.")

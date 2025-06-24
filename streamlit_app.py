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
    .info-block {
        padding: 1rem;
        border-radius: 10px;
        background-color: #f8f9fa;
        margin-bottom: 1.5rem;
    }
    .info-block h4 {
        font-size: 18px;
        margin-bottom: 0.5rem;
    }
    .info-block p {
        font-size: 22px;
        font-weight: 600;
        margin: 0;
        color: #222;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="title-box"><h1>‍📚 [2025 교실혁명 선도교사 양성연수(5권역)] 🧑‍🏫</h1><p><이수 현황 확인></p></div>', unsafe_allow_html=True)
st.markdown("##### ※ 이수 시간에 대한 확인은 강의 종료 후 48시간 뒤 조회 가능합니다. ")

# ✅ 사용자 입력
name = st.text_input("👤 이름을 입력하세요: ", placeholder="예: 홍길동")
phone_last4 = st.text_input("📱 전화번호 뒷 네 자리를 입력하세요: ", max_chars=4, placeholder="예: 1234")

st.markdown("---")

# ✅ 사용자 찾기 함수
def find_user(name, phone_last4):
    for user in records:
        if user["이름"] == name and str(user["전화번호뒷자리"]).zfill(4) == phone_last4:
            return user
    return None

# ✅ 안전한 숫자 변환
def safe_int(value):
    try:
        return int(str(value).replace("분", "").strip())
    except:
        return 0

# ✅ 조회 버튼 동작
if st.button("📥 이수율 조회하기"):
    if not name or not phone_last4:
        st.warning("⚠️ 이름과 전화번호 뒷자리를 모두 입력해주세요.")
    else:
        user = find_user(name, phone_last4)
        if user:
            st.success(f"🎉 {user['이름']} 선생님의 이수 정보")

            # ✅ 전체 차시별 박스 테이블 렌더링
            def render_block(title, count, minutes, prefix):
                cols = "".join([f"<td style='border:1px solid #ccc; text-align:center;'>{i}차시</td>" for i in range(1, count+1)])
                values = "".join([f"<td style='border:1px solid #ccc; text-align:center;'>{safe_int(user.get(f'{prefix}{i}차', 0))}분</td>" for i in range(1, count+1)])
                return f"""
                <div class="info-block">
                    <h4>{title}</h4>
                    <table style="border-collapse: collapse; width:100%;">
                        <tr>{cols}</tr>
                        <tr>{values}</tr>
                    </table>
                </div>"""

            html_blocks = ""
            html_blocks += render_block("① 사전진단 (2차시 / 100분)", 2, 100, "사전진단_")
            html_blocks += render_block("② 사전워크숍 (3차시 / 150분)", 3, 150, "사전워크숍_")
            html_blocks += render_block("③ 원격연수 (16차시 / 800분)", 16, 800, "원격연수_")
            html_blocks += render_block("④ 집합연수 (14차시 / 700분)", 14, 700, "집합연수_")
            html_blocks += render_block("⑤ 컨퍼런스 (5차시 / 250분)", 5, 250, "컨퍼런스_")

            st.markdown(html_blocks, unsafe_allow_html=True)

            # ✅ 총합
            all_keys = [f"사전진단_{i}차" for i in range(1,3)] + \
                       [f"사전워크숍_{i}차" for i in range(1,4)] + \
                       [f"원격연수_{i}차" for i in range(1,17)] + \
                       [f"집합연수_{i}차" for i in range(1,15)] + \
                       [f"컨퍼런스_{i}차" for i in range(1,6)]
            total_min = sum([safe_int(user.get(k, 0)) for k in all_keys])

            st.markdown(f"""
                <div style="text-align:right; font-weight:600; margin-top:1rem; font-size:1.1rem;">
                총 이수 시간 (이수율)<br>
                {total_min}분 ({round(total_min/2000*100)}%) / 2000분
                </div>
            """, unsafe_allow_html=True)

        else:
            st.error("😢 입력하신 정보와 일치하는 사용자가 없습니다.")

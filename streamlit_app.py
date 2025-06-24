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

# ✅ 페이지 설정
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
    table {
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 1.5rem;
    }
    th, td {
        border: 1px solid #ccc;
        padding: 6px;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# ✅ 제목
st.markdown('<div class="title-box"><h1>‍📚 [2025 교실혁명 선도교사 양성연수(5권역)] 🧑‍🏫</h1><p><이수 현황 확인></p></div>', unsafe_allow_html=True)
st.markdown("##### ※ 이수 시간에 대한 확인은 강의 종료 후 48시간 뒤 조회 가능합니다.")

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

# ✅ 시각화용 테이블 렌더 함수
def render_table(title, session_count, total_minutes, prefix, user):
    st.markdown(f"### {title} ({session_count}차시 / {total_minutes}분)")

    headers = "".join([f"<th>{i+1}차시</th>" for i in range(session_count)])
    values = "".join([
        f"<td>{user.get(f'{prefix}{i+1}', '00')}분</td>" for i in range(session_count)
    ])

    st.markdown(f"""
    <table>
        <tr>{headers}</tr>
        <tr>{values}</tr>
    </table>
    """, unsafe_allow_html=True)

# ✅ 총 시간 계산
def safe_int(value):
    try:
        return int(str(value).replace("분", "").strip())
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

            # ✅ 항목별 테이블 출력
            render_table("① 사전진단", 2, 100, "사전진단", user)
            render_table("② 사전워크숍", 3, 150, "사전워크숍", user)
            render_table("③ 원격연수", 16, 800, "원격연수", user)
            render_table("④ 집합연수", 14, 700, "집합연수", user)
            render_table("⑤ 컨퍼런스", 5, 250, "컨퍼런스", user)

            # ✅ 총 시간 및 퍼센트
            total_time = 0
            total_target = 2000  # 기준

            for section, count in [
                ("사전진단", 2),
                ("사전워크숍", 3),
                ("원격연수", 16),
                ("집합연수", 14),
                ("컨퍼런스", 5),
            ]:
                for i in range(1, count + 1):
                    total_time += safe_int(user.get(f"{section}{i}", "0"))

            percentage = round((total_time / total_target) * 100, 1)

            st.markdown("---")
            st.markdown(f"### 총 이수 시간 (이수율)")
            st.markdown(f"**{total_time}분 ({percentage}%) / {total_target}분**")
        else:
            st.error("😢 입력하신 정보와 일치하는 사용자가 없습니다.")

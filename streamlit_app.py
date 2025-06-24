import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

# ✅ 페이지 설정
st.set_page_config(page_title="알파코 이수율 확인 시스템", layout="centered")

# ✅ 스타일 + 상단 타이틀 + 안내문
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
.block {
    background-color: #f7f7f9;
    padding: 1.2rem;
    border-radius: 10px;
    margin-bottom: 1.5rem;
}
.block h5 {
    margin-bottom: 0.3rem;
    font-weight: bold;
}
.block p {
    font-size: 1.5rem;
    font-weight: 600;
    margin: 0;
}
table {
    width: 100%;
    border-collapse: collapse;
    font-size: 14px;
    margin-top: 10px;
}
th, td {
    border: 1px solid #ccc;
    padding: 8px 10px;
    text-align: center;
}
.gray-note {
    font-size: 13px;
    color: #666;
    margin-top: 4px;
}
</style>

<div class="title-box">
    <h1>📚 [2025 교실혁명 선도교사 양성연수(5권역)] 🧑‍🏫</h1>
    <p>&lt;이수 현황 확인&gt;</p>
</div>
""", unsafe_allow_html=True)

st.markdown("##### ※ 이수 시간에 대한 확인은 강의 종료 후 48시간 뒤 조회 가능합니다.")

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

# ✅ 사용자 입력
name = st.text_input("👤 이름을 입력하세요:", placeholder="예: 홍길동")
phone_last4 = st.text_input("📱 전화번호 뒷 네 자리를 입력하세요:", max_chars=4, placeholder="예: 1234")
st.markdown("---")

# ✅ 유틸 함수
def find_user(name, phone_last4):
    for user in records:
        if user["이름"] == name and str(user["전화번호뒷자리"]).zfill(4) == phone_last4:
            return user
    return None

def safe_int(value):
    try:
        return int(str(value).replace("분", "").strip())
    except:
        return 0

# ✅ 카드형 블록 출력
def render_block(title, session_count, total_minutes, key_prefix, user):
    total = 0
    for i in range(1, session_count + 1):
        total += safe_int(user.get(f"{key_prefix}{i}", "0"))

    st.markdown(f"""
    <div class="block">
        <h5>☑️ {title} ({session_count}차시 / {total_minutes}분)</h5>
        <p>{total}분</p>
    </div>
    """, unsafe_allow_html=True)
    return total

# ✅ 원격연수 테이블
def render_remote_table(user):
    val = safe_int(user.get("원격연수", "0"))
    st.markdown(f"""
    <div class="block">
        <h5>☑️ 원격연수 (9과정 16차시 / 960분)</h5>
        <p>{val}분</p>
        <table>
            <tr>
                <th>1~2과정</th><th>3~4과정</th><th>5과정</th>
                <th>6과정</th><th>7과정</th><th>8~9과정</th>
            </tr>
            <tr>
                <td>{safe_int(user.get("과정1", 0)) + safe_int(user.get("과정2", 0))}분</td>
                <td>{safe_int(user.get("과정3", 0)) + safe_int(user.get("과정4", 0))}분</td>
                <td>{safe_int(user.get("과정5", 0))}분</td>
                <td>{safe_int(user.get("과정6", 0))}분</td>
                <td>{safe_int(user.get("과정7", 0))}분</td>
                <td>{safe_int(user.get("과정8", 0)) + safe_int(user.get("과정9", 0))}분</td>
            </tr>
        </table>
        <p class="gray-note">*과정이 나눠서 진행될 경우 마지막 과정 종료 후 이수 시간이 입력됩니다.</p>
    </div>
    """, unsafe_allow_html=True)
    return val

# ✅ 조회 버튼
if st.button("📥 이수율 조회하기"):
    if not name or not phone_last4:
        st.warning("⚠️ 이름과 전화번호 뒷자리를 모두 입력해주세요.")
    else:
        user = find_user(name, phone_last4)

        if user:
            st.success(f"🎉 {user['이름']} 선생님의 이수 정보")

            total = 0
            total += render_block("사전진단", 2, 120, "사전진단", user)
            total += render_block("사전워크숍", 3, 180, "사전워크숍", user)
            total += render_remote_table(user)
            total += render_block("집합연수", 14, 840, "집합연수", user)
            total += render_block("컨퍼런스", 5, 300, "컨퍼런스", user)

            st.markdown("---")
            percent = round((total / 2400) * 100, 1) if total else 0
            st.markdown("### 총 이수 시간 (이수율)")
            st.markdown(f"**{total}분 ({percent}%) / 2400분**")

            if user.get("이수여부") == "이수":
                st.success("✅ 이수 완료")
            else:
                st.error("📌 미이수")
        else:
            st.error("😢 입력하신 정보와 일치하는 사용자가 없습니다.")

import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

scopes = ["https://www.googleapis.com/auth/spreadsheets"]
credentials = Credentials.from_service_account_info(
    dict(st.secrets["gcp_service_account"]),  # 여기에 문제가 없다는 전제
    scopes=scopes
)
client = gspread.authorize(credentials)

# ✅ 시트 열기
try:
    sheet = client.open_by_key("1owM9EXygtbj8EO-jYL5Lr1rixU-sT8LJ_h8k1aLnSTI").sheet1
    records = sheet.get_all_records()
except Exception as e:
    st.error(f"❌ 구글 시트 접근 중 오류: {e}")
    st.stop()

# ✅ 기본 설정
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
    </style>
""", unsafe_allow_html=True)

# ✅ 상단 타이틀
st.markdown('<div class="title-box"><h1>‍📚 [2025 교실혁명 선도교사 양성연수(5권역)] 🧑‍🏫</h1><p><이수 현황 확인></p></div>', unsafe_allow_html=True)

# ✅ 사용자 입력
name = st.text_input("👤 이름을 입력하세요: ", placeholder="예: 홍길동")
phone_last4 = st.text_input("📱 전화번호 뒷 네 자리를 입력하세요: ", max_chars=4, placeholder="예: 1234")

# ✅ 수료 기준 안내
st.markdown("""
<div style="background-color:#fffbe6; border-left: 5px solid #ffc107; padding: 1.2rem 1.5rem; margin: 1.5rem 0 1rem 0; border-radius: 8px;">
    <p style="margin: 0; font-size: 1rem; line-height: 1.5;">
        📌 <b>수료 기준 안내</b><br><br>
        ✅ 전체 <b>40개 차시 중 80%(32개 차시)</b> 이상 이수 시 수료<br>
        ✅ <b>2,400분 중 1,920분</b> 이상 참여 시 수료<br>
        <span style="color:#666;">※ 단, 차시별로 80% 이상 이수 시 해당 차시 인정</span>
    </p>
</div>
""", unsafe_allow_html=True)

# ✅ 함수 정의
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

def render_course_table(title, count, prefix):
    header = "".join([f"<td style='border:1px solid black; padding:6px 10px; text-align:center;'>{i}차시</td>" for i in range(1, count+1)])
    values = "".join([f"<td style='border:1px solid black; padding:6px 10px; text-align:center;'>{str(user.get(f'{prefix}{i}차', '00'))}분</td>" for i in range(1, count+1)])
    return f"""
    <div style="background-color:#f9f9f9; border-radius:10px; padding:1rem; margin-bottom:1.5rem;">
        <b>{title}</b>
        <table style="border-collapse:collapse; width:100%; margin-top:0.5rem;">
            <tr>{header}</tr>
            <tr>{values}</tr>
        </table>
    </div>
    """

# ✅ 버튼 클릭 시 동작
if st.button("📥 이수율 조회하기"):
    if not name or not phone_last4:
        st.warning("⚠️ 이름과 전화번호 뒷자리를 모두 입력해주세요.")
    else:
        user = find_user(name, phone_last4)
        if user:
            st.success(f"✅ {user['이름']} 선생님의 이수 정보")

            # ✅ 차시별 테이블 출력
            st.markdown(render_course_table("① 사전진단 (2차시 / 100분)", 2, "사전진단_"), unsafe_allow_html=True)
            st.markdown(render_course_table("② 사전워크숍 (3차시 / 150분)", 3, "사전워크숍_"), unsafe_allow_html=True)
            st.markdown(render_course_table("③ 원격연수 (16차시 / 800분)", 16, "원격연수_"), unsafe_allow_html=True)
            st.markdown(render_course_table("④ 집합연수 (14차시 / 700분)", 14, "집합연수_"), unsafe_allow_html=True)
            st.markdown(render_course_table("⑤ 컨퍼런스 (5차시 / 250분)", 5, "컨퍼런스_"), unsafe_allow_html=True)

            # ✅ 총 이수 시간 / 차시 계산
            all_keys = [f"사전진단_{i}차" for i in range(1,3)] + \
                       [f"사전워크숍_{i}차" for i in range(1,4)] + \
                       [f"원격연수_{i}차" for i in range(1,17)] + \
                       [f"집합연수_{i}차" for i in range(1,15)] + \
                       [f"컨퍼런스_{i}차" for i in range(1,6)]
            total_min = sum([safe_int(user.get(k, 0)) for k in all_keys])
            completed_sessions = sum([1 for k in all_keys if safe_int(user.get(k, 0)) >= 40])
            completion_percent = round((completed_sessions / 40) * 100)

            # ✅ 총 이수율 표시
            st.markdown("""
                <div style="border-top:1px solid #ccc; margin-top:2rem; padding-top:1rem; font-weight:600; font-size:1.1rem; text-align:center;">
                    총 이수율<br>
                    {:02d}차시 / 40차시 ({:.0f}%)
                </div>
            """.format(completed_sessions, completion_percent), unsafe_allow_html=True)

            # ✅ 이수 여부
            if user.get("이수여부") == "이수":
                st.markdown("""
                    <div style="margin-top:1rem; background-color:#fce4ec; padding:1rem; text-align:center; border-radius:10px; color:#880e4f; font-weight:600;">
                        📌 <b>이수</b>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                    <div style="margin-top:1rem; background-color:#fce4ec; padding:1rem; text-align:center; border-radius:10px; color:#880e4f; font-weight:600;">
                        ❌ <b>미이수</b>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.error("😢 입력하신 정보와 일치하는 사용자가 없습니다.")

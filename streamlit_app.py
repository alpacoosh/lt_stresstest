import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
from collections import defaultdict

# ✅ 구글 시트 인증
scopes = ["https://www.googleapis.com/auth/spreadsheets"]
credentials = Credentials.from_service_account_info(
    dict(st.secrets["gcp_service_account"]),
    scopes=scopes
)
client = gspread.authorize(credentials)

@st.cache_data(ttl=5)
def load_sheet_data():
    worksheet = client.open_by_key("1Q1RbrQJ4mipUzogBpfN6dY6TOOLxrYZPkRpvlANUAo8").worksheet("시트4")
    rows = worksheet.get_all_values()
    return pd.DataFrame(rows)

try:
    df_raw = load_sheet_data()
except Exception as e:
    st.error(f"❌ 구글 시트 접근 중 오류: {e}")
    st.stop()

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

type_status_counter = defaultdict(int)
for idx, col in enumerate(data.columns):
    if "_" not in col and col not in ["이름", "전화번호뒷자리", "총이수율", "총이수율(%)", "이수여부"]:
        type_status_counter[col] += 1
        base_col = f"{col}_{type_status_counter[col]}차시"
        if base_col in data.columns:
            data[f"{base_col}_상태"] = data.iloc[:, idx]

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

st.markdown("""
<div style="text-align:center; margin-top:-1.5rem; margin-bottom:2rem;">
    <img src="https://raw.githubusercontent.com/alpacoosh/lt_stresstest/main/logo.png" style="max-width:300px;">
</div>
""", unsafe_allow_html=True)

name = st.text_input("👤 이름을 입력하세요: ", placeholder="예: 홍길동")
phone_last4 = st.text_input("📱 전화번호 뒷 네 자리를 입력하세요: ", max_chars=4, placeholder="예: 1234")

st.markdown("""
<div style="background-color:#fffbe6; border-left: 5px solid #ffc107; padding: 1.2rem 1.5rem; margin: 1.5rem 0 1rem 0; border-radius: 8px;">
    <p style="margin: 0; font-size: 1rem; line-height: 1.5;">
        📌 <b>수료 기준 안내</b><br><br>
        ✅ 전체 <b>40개 차시 중 80%(32개)</b> 이상 이수 시 수료<br>
        ✅ 각 차시는 수업 시간의 <b>80%</b> 이상 참여해야 이수 인정<br>
    </p>
</div>
""", unsafe_allow_html=True)

# 세션 상태 초기화
if "user" not in st.session_state:
    st.session_state["user"] = None
if "agree_clicked" not in st.session_state:
    st.session_state["agree_clicked"] = False
if "confirm_status" not in st.session_state:
    st.session_state["confirm_status"] = None

def render_table(title, prefix, count, user):
    if prefix == "원격연수":
        font_size = "0.55rem"
    else:
        font_size = "0.7rem"
    padding = "1px 6px"
    height = "28px"
    min_width = "38px"

    if prefix == "사전진단":
        submit1_col_idx = 3
        complete1_col_idx = 4
        submit2_col_idx = 6
        complete2_col_idx = 7
        html = f"""
        <div style="background-color:#f9f9f9; border-radius:10px; padding:0.6rem; margin-bottom:1rem;">
            <b style="font-size:0.95rem;">{title}</b>
            <table style="border-collapse:collapse; width:100%; margin-top:0.3rem; text-align:center; font-size:{font_size};">
                <tr>
                    <td colspan="2" style="border:1px solid black; padding:{padding}; height:{height}; font-weight:bold; width:50%;">1차시</td>
                    <td colspan="2" style="border:1px solid black; padding:{padding}; height:{height}; font-weight:bold; width:50%;">2차시</td>
                </tr>
                <tr>
                    <td style="border:1px solid black; padding:{padding}; height:{height}; width:25%;">{user[f'{prefix}_1차시']}</td>
                    <td style="border:1px solid black; padding:{padding}; height:{height}; width:25%;">{user.iloc[submit1_col_idx]}</td>
                    <td style="border:1px solid black; padding:{padding}; height:{height}; width:25%;">{user[f'{prefix}_2차시']}</td>
                    <td style="border:1px solid black; padding:{padding}; height:{height}; width:25%;">{user.iloc[submit2_col_idx]}</td>
                </tr>
                <tr>
                    <td colspan="2" style="border:1px solid black; padding:{padding}; height:{height}; background-color:#FFE0B2;">{user.iloc[complete1_col_idx]}</td>
                    <td colspan="2" style="border:1px solid black; padding:{padding}; height:{height}; background-color:#FFE0B2;">{user.iloc[complete2_col_idx]}</td>
                </tr>
            </table>
        </div>
        """
        return html

    headers = "".join([
        f"<td style='border:1px solid black; padding:{padding}; min-width:{min_width}; height:{height}; "
        f"text-align:center; font-size:{font_size}; vertical-align:middle; font-weight:bold;'>{i}차시</td>"
        for i in range(1, count + 1)
    ])
    minutes = "".join([
        f"<td style='border:1px solid black; padding:{padding}; height:{height}; text-align:center; "
        f"font-size:{font_size}; vertical-align:middle;'>{user.get(f'{prefix}_{i}차시', '00분')}</td>"
        for i in range(1, count + 1)
    ])
    statuses = "".join([
        f"<td style='border:1px solid black; padding:{padding}; height:{height}; text-align:center; "
        f"font-size:{font_size}; vertical-align:middle; background-color:"
        f"{'#FFE0B2' if prefix in ['사전진단', '원격연수', '집합연수'] else '#E6E6E6'};'>"
        f"{user.get(f'{prefix}_{i}차시_상태', '')}</td>"
        for i in range(1, count + 1)
    ])
    return f"""
    <div style="background-color:#f9f9f9; border-radius:10px; padding:0.6rem; margin-bottom:1rem;">
        <b style="font-size:0.95rem;">{title}</b>
        <table style="border-collapse:collapse; width:100%; margin-top:0.3rem;">
            <tr>{headers}</tr>
            <tr>{minutes}</tr>
            <tr>{statuses}</tr>
        </table>
    </div>
    """

# st.write("컬럼 종류:", list(data.columns))


# 조회 버튼
if st.button("📥 이수율 조회하기"):
    if not name or not phone_last4:
        st.warning("⚠️ 이름과 전화번호 뒷자리를 모두 입력해주세요.")
        st.session_state["user"] = None
    else:
        row = data[(data["이름"] == name) & (data["전화번호뒷자리"] == phone_last4)]
        if len(row) == 0:
            st.error("😢 입력하신 정보와 일치하는 사용자가 없습니다.")
            st.session_state["user"] = None
        else:
            st.session_state["user"] = row.iloc[0]
            st.session_state["agree_clicked"] = False
            st.session_state["confirm_status"] = None

user = st.session_state.get("user")

if user is not None:
    st.success(f"✅ {user['이름']} 선생님의 이수 정보")
    summary_fields = [
        ("사전진단", 88, 89, 90),
        ("사전워크숍", 92, 93, 94),
        ("원격연수", 96, 97, 98),
        ("집합연수", 100, 101, 102),
        ("컨퍼런스", 104, 105, 106)
    ]

    summary_table_html = f"""
    <div style="margin-top:2rem; background-color:#f9f9f9; border-radius:10px; padding:0.8rem; margin-bottom:1.2rem;">
    <h4 style="font-weight:600; color:#003366; font-size:1rem;">📘 {user['이름']} 선생님의 연수 수강 정보</h4>
    <table style="border-collapse: collapse; width: 100%; font-size: 0.7rem; text-align: center; margin-top: 0.5rem;">
    <tr style=" color:black;">
        <th style="border: 1px solid black; padding: 6px;">연수유형</th>
        <th style="border: 1px solid black; padding: 6px;">수강 정보</th>
        <th style="border: 1px solid black; padding: 6px;">일자</th>
        <th style="border: 1px solid black; padding: 6px;">비고</th>
    </tr>
    """
    for label, col_sugang, col_date, col_note in summary_fields:
        summary_table_html += f"""
    <tr>
        <td style="border: 1px solid black; padding: 5px; vertical-align: middle;">{label}</td>
        <td style="border: 1px solid black; padding: 5px; vertical-align: middle;">{user.iloc[col_sugang]}</td>
        <td style="border: 1px solid black; padding: 5px; vertical-align: middle;">{user.iloc[col_date]}</td>
        <td style="border: 1px solid black; padding: 5px; vertical-align: middle;">{user.iloc[col_note]}</td>
    </tr>
    """
    summary_table_html += """
    </table>
    </div>
    """
    st.markdown(summary_table_html, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(render_table("① 사전진단 (2차시 / 100분)", "사전진단", 2, user), unsafe_allow_html=True)
    with col2:
        st.markdown(render_table("② 사전워크숍 (3차시 / 150분) - KERIS 확인", "사전워크숍", 3, user), unsafe_allow_html=True)
    st.markdown(render_table("③ 원격연수 (16차시 / 800분)", "원격연수", 16, user), unsafe_allow_html=True)
    st.markdown(render_table("④ 집합연수 (14차시 / 700분)", "집합연수", 14, user), unsafe_allow_html=True)
    st.markdown(render_table("⑤ 컨퍼런스 (5차시 / 250분) - KERIS 확인", "컨퍼런스", 5, user), unsafe_allow_html=True)

    completed_sessions = int(user.get('총이수차시', 0))
    percent = round(completed_sessions / 40 * 100)

    st.markdown(f"""
        <div style="border-top:1px solid #ccc; margin-top:2rem; padding-top:1rem; font-weight:600; font-size:1.1rem; text-align:center;">
            총 이수율<br>
            <p style="font-size:0.9rem;">*사전워크숍과 컨퍼런스를 제외한 32차시만 합산됩니다.</p>
            {completed_sessions:02d}차시 / 32차시
        </div>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # st.write("서명 실제 값:", repr(user.get("서명", "")))

    # ✅ 서명 값이 TRUE면 동의 관련 UI 숨김
    if user.get("서명", "").strip().upper() == "TRUE":
        st.info("이미 이수 내역 확인 동의를 완료하셨습니다.")
    else:
        if not st.session_state["agree_clicked"]:
            c1, c2, c3 = st.columns([4.6, 3, 4.4])
            with c2:
                if st.button("이수 내역 확인 동의", key="agree_btn"):
                    st.session_state["agree_clicked"] = True

        if st.session_state["agree_clicked"]:
            st.info("이수 내역에 이의 없음을 확인합니다.")
            r1, r2, r3 = st.columns([8, 1, 1])
            with r2:
                if st.button("YES", key="yes_btn"):
                    st.session_state["confirm_status"] = "YES"
            with r3:
                if st.button("NO", key="no_btn"):
                    st.session_state["confirm_status"] = "NO"

            if st.session_state["confirm_status"] == "YES":
                st.success("동의가 정상적으로 접수되었습니다. 감사합니다.")
                # 구글 시트에 TRUE 기록
                signature_col_idx = data.columns.get_loc("서명") + 1
                row_idx = user.name + 3  # df_raw 기준 실제 시트 row (헤더2줄+1부터 시작)
                ws = client.open_by_key("1Q1RbrQJ4mipUzogBpfN6dY6TOOLxrYZPkRpvlANUAo8").worksheet("시트4")
                ws.update_cell(row_idx, signature_col_idx, "TRUE")
            
            elif st.session_state["confirm_status"] == "NO":
                st.warning("동의하지 않으셨습니다. 문의사항은 운영팀에 연락해주세요.")
                # 구글 시트에 FALSE 기록
                signature_col_idx = data.columns.get_loc("서명") + 1
                row_idx = user.name + 3
                ws = client.open_by_key("1Q1RbrQJ4mipUzogBpfN6dY6TOOLxrYZPkRpvlANUAo8").worksheet("시트4")
                ws.update_cell(row_idx, signature_col_idx, "FALSE")
    
    
    



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

# ✅ 시트 불러오기
try:
    worksheet = client.open_by_key("1owM9EXygtbj8EO-jYL5Lr1rixU-sT8LJ_h8k1aLnSTI").worksheet("시트4")
    rows = worksheet.get_all_values()
    df_raw = pd.DataFrame(rows)
except Exception as e:
    st.error(f"❌ 구글 시트 접근 중 오류: {e}")
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

# ✅ 연수 요약 info_blocks: 87~106 컬럼 기반
info_blocks = []
type_labels = ["사전진단", "사전워크숍", "원격연수", "집합연수", "콘퍼런스"]
for i in range(5):
    base_idx = 87 + i * 4
    cols = data.columns[base_idx:base_idx+4]
    row_values = data.iloc[0][cols].tolist()
    info_blocks.append((row_values[0], row_values[1], row_values[2], row_values[3]))

# ✅ 상태 컬럼 생성
type_status_counter = defaultdict(int)
for idx, col in enumerate(data.columns):
    if "_" not in col and col not in ["이름", "전화번호뒷자리", "총이수율", "총이수율(%)", "이수여부"]:
        type_status_counter[col] += 1
        base_col = f"{col}_{type_status_counter[col]}차시"
        if base_col in data.columns:
            data[f"{base_col}_상태"] = data.iloc[:, idx]

# ✅ UI
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

def render_table(title, prefix, count):
    compact = count >= 14
    font_size = "0.7rem" if compact else "1rem"
    padding = "2px 4px" if compact else "6px 10px"
    min_width = "38px" if compact else "60px"
    headers = "".join([
        f"<td style='border:1px solid black; padding:{padding}; min-width:{min_width}; text-align:center; font-size:{font_size};'>{i}차시</td>"
        for i in range(1, count+1)
    ])
    minutes = "".join([
        f"<td style='border:1px solid black; padding:{padding}; text-align:center; font-size:{font_size};'>{user.get(f'{prefix}_{i}차시', '00분')}</td>"
        for i in range(1, count+1)
    ])
    statuses = "".join([
        f"<td style='border:1px solid black; padding:{padding}; text-align:center; font-size:{font_size}; background-color:#ffe0b2;'>{user.get(f'{prefix}_{i}차시_상태', '')}</td>"
        for i in range(1, count+1)
    ])
    return f"""
    <div style="background-color:#f9f9f9; border-radius:10px; padding:0.8rem; margin-bottom:1.2rem;">
        <b style="font-size:0.95rem;">{title}</b>
        <table style="border-collapse:collapse; width:100%; margin-top:0.4rem;">
            <tr>{headers}</tr>
            <tr>{minutes}</tr>
            <tr>{statuses}</tr>
        </table>
    </div>
    """

if st.button("📥 이수율 조회하기"):
    if not name or not phone_last4:
        st.warning("⚠️ 이름과 전화번호 뒷자리를 모두 입력해주세요.")
    else:
        row = data[(data["이름"] == name) & (data["전화번호뒷자리"] == phone_last4)]
        if len(row) == 0:
            st.error("😢 입력하신 정보와 일치하는 사용자가 없습니다.")
        else:
            user = row.iloc[0]
            st.success(f"✅ {user['이름']} 선생님의 이수 정보")

            # ✅ 연수 요약 테이블 출력
            st.markdown("### 🗓️ 연수 수강 정보 요약")
            table_html = """
<div style='background-color:#f9f9f9; border-radius:10px; padding:1rem;'>
<table style='border-collapse: collapse; width: 100%;'>
<thead>
<tr style="background-color:#eee;">
    <th style='padding:6px; text-align:center;'>연수 유형</th>
    <th style='padding:6px; text-align:center;'>차시</th>
    <th style='padding:6px; text-align:center;'>일정</th>
    <th style='padding:6px; text-align:left;'>비고</th>
</tr>
</thead>
<tbody>
"""
            for title, a, b, c in info_blocks:
                table_html += f"""
<tr>
    <td style='padding:6px; text-align:center;'>{title.strip()}</td>
    <td style='padding:6px; text-align:center;'>{a.strip()}</td>
    <td style='padding:6px; text-align:center;'>{b.strip()}</td>
    <td style='padding:6px; text-align:left;'>{c.strip()}</td>
</tr>
"""
            table_html += """
</tbody>
</table>
</div>
"""
            st.markdown(table_html, unsafe_allow_html=True)

            # ✅ 차시별 테이블 출력
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(render_table("① 사전진단 (2차시 / 100분)", "사전진단", 2), unsafe_allow_html=True)
            with col2:
                st.markdown(render_table("② 사전워크숍 (3차시 / 150분)", "사전워크숍", 3), unsafe_allow_html=True)
            st.markdown(render_table("③ 원격연수 (16차시 / 800분)", "원격연수", 16), unsafe_allow_html=True)
            st.markdown(render_table("④ 집합연수 (14차시 / 700분)", "집합연수", 14), unsafe_allow_html=True)
            st.markdown(render_table("⑤ 컨퍼런스 (5차시 / 250분)", "컨퍼런스", 5), unsafe_allow_html=True)

            # ✅ 이수율 계산
            completed_sessions = int(user.get('총이수율', 0))
            percent = round(completed_sessions / 40 * 100)
            st.markdown(f"""
<div style="border-top:1px solid #ccc; margin-top:2rem; padding-top:1rem; font-weight:600; font-size:1.1rem; text-align:center;">
    총 이수율<br>
    {completed_sessions:02d}차시 / 40차시 ({percent}%)
</div>
""", unsafe_allow_html=True)
            st.markdown(f"""
<div style="margin-top:1rem; background-color:#f8d7da; padding:1rem; text-align:center; border-radius:10px; color:#721c24; font-weight:600;">
    📌 <b>{'이수' if user.get('이수여부') == '이수' else '미이수'}</b>
</div>
""", unsafe_allow_html=True)

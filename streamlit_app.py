# ... (상단 인증 및 설정 동일) ...
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
    .title-box2 {
        background-color: #003366;
        height:60px;
        color: white;
        border-radius: 0.5rem;
        text-align: center;
        margin-bottom: 1rem;
    }
    .title-box h1 {
        margin-bottom: 0.2rem;
        font-size: 1.7rem;
    }
    .title-box2 h1 {
        font-size: 1.2rem;
    }
    .title-box p {
        font-size: 1.6rem;
        margin-top: 0.3rem;
        font-weight: 600;
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
    
def safe_int(value):
    value = value.replace("분","")
    try:
        return int(value)
    except:
        return 0

    
st.markdown("""
<div style="background-color:#fffbe6; border-left: 5px solid #ffc107; padding: 1.2rem 1.5rem; margin: 0.1rem 0 0.5rem 0; border-radius: 8px;">
    <p style="margin: 0; font-size: 1rem; line-height: 1.5;">
        📌 <b>수료 기준 안내</b><br><br>
        ✅ 전체 <b>40개 차시 중 80%(32개 차시)</b> 이상 이수 시 수료<br>
        ✅ <b>2,400분 중 1,920분</b> 이상 참여 시 수료<br>
        <span style="color:#666;">※ 단, 차시별로 80% 이상 이수 시 해당 차시 인정</span>
    </p>
</div>
""", unsafe_allow_html=True)


# 조회 버튼
if st.button("📥 이수율 조회하기"):
    if not name or not phone_last4:
        st.warning("⚠️ 이름과 전화번호 뒷자리를 모두 입력해주세요.")
    else:

        user = find_user(name, phone_last4)
        # 안내 문구 바로 아래 추가
        
        
        if user:
            st.success(f"🎉 {user['이름']} 선생님의 이수 정보")

            # 사전진단 & 사전워크숍
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("""
                <div style="background-color:#f7f7f9; padding:1.2rem; border-radius:10px;">
                    <h5 style="margin-bottom:0.3rem;">☑️ <b>사전진단 (2차시 / 120분)</b></h5>
                    <p style="font-size:1.5rem; font-weight:600;">{}분</p>
                </div>
                """.format(user["사전진단"]), unsafe_allow_html=True)

            with col2:
                st.markdown("""
                <div style="background-color:#f7f7f9; padding:1.2rem; border-radius:10px;">
                    <h5 style="margin-bottom:0.3rem;">☑️ <b>사전워크숍 (3차시 / 180분)</b></h5>
                    <p style="font-size:1.5rem; font-weight:600;">{}분</p>
                </div>
                """.format(user["사전워크샵"]), unsafe_allow_html=True)

            st.markdown("---")

            st.markdown(f"""
                            <div style="background-color:#f7f7f9; padding:1.2rem; border-radius:10px; text-align:center;">
                                <h5 style="margin-bottom:0.3rem;">☑️ <b>원격연수 (9과정 16차시 / 960분)</b></h5>
                                <p style="font-size:1.5rem; font-weight:600;">{user["원격연수"]}분</p>
                                <table style="margin: 0 auto; border-collapse: collapse; font-size: 0.95rem;">
                                    <tr>
                                        <th style="padding:6px 10px; border:1px solid #ddd;">1~2과정</th>
                                        <th style="padding:6px 10px; border:1px solid #ddd;">3~4과정</th>
                                        <th style="padding:6px 10px; border:1px solid #ddd;">5과정</th>
                                        <th style="padding:6px 10px; border:1px solid #ddd;">6과정</th>
                                        <th style="padding:6px 10px; border:1px solid #ddd;">7과정</th>
                                        <th style="padding:6px 10px; border:1px solid #ddd;">8~9과정</th>
                                    </tr>
                                    <tr>
                                        <td style="padding:6px 10px; border:1px solid #ddd;">{safe_int(user["과정1"]) + safe_int(user["과정2"])}분</td>
                                        <td style="padding:6px 10px; border:1px solid #ddd;">{safe_int(user["과정3"]) + safe_int(user["과정4"])}분</td>
                                        <td style="padding:6px 10px; border:1px solid #ddd;">{safe_int(user["과정5"])}분</td>
                                        <td style="padding:6px 10px; border:1px solid #ddd;">{safe_int(user["과정6"])}분</td>
                                        <td style="padding:6px 10px; border:1px solid #ddd;">{safe_int(user["과정7"])}분</td>
                                        <td style="padding:6px 10px; border:1px solid #ddd;">{safe_int(user["과정8"]) + safe_int(user["과정9"])}분</td>
                                    </tr>
                                </table>
                            </div>
                            <p>*과정이 나눠서 진행될 경우 마지막 과정 종료 후 이수 시간이 입력됩니다.</p>
                            """, unsafe_allow_html=True)

            st.markdown("---")

            # 집합연수 & 컨퍼런스
            col3, col4 = st.columns(2)
            with col3:
                st.markdown("""
                <div style="background-color:#f7f7f9; padding:1.2rem; border-radius:10px;">
                    <h5 style="margin-bottom:0.3rem;">☑️ <b>집합연수 (14차시 / 840분)</b></h5>
                    <p style="font-size:1.5rem; font-weight:600;">{}분</p>
                </div>
                """.format(user["집합연수"]), unsafe_allow_html=True)

            with col4:
                st.markdown("""
                <div style="background-color:#f7f7f9; padding:1.2rem; border-radius:10px;">
                    <h5 style="margin-bottom:0.3rem;">☑️ <b>컨퍼런스 (5차시 / 300분)</b></h5>
                    <p style="font-size:1.5rem; font-weight:600;">{}분</p>
                </div>
                """.format(user["컨퍼런스"]), unsafe_allow_html=True)

            # 총 이수율
            st.divider()

            def safe_int(value):
                try:
                    return int(value)
                except:
                    return 0
            
            total_minutes = sum(safe_int(user[k]) for k in ["사전진단", "사전워크샵", "원격연수", "집합연수", "컨퍼런스"])



            st.metric(label="총 이수 시간 (이수율)", value=f"{total_minutes}분 ({user['총이수율']}%) / 2400분")

            if user["이수여부"] == "이수":
                st.success("✅ 이수 완료")
            else:
                st.error("📌 미이수")
        else:
            st.error("😢 입력하신 정보와 일치하는 사용자가 없습니다.")

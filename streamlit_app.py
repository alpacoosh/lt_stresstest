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

# ✅ 이수율 조회 버튼 누르면 실행
if st.button("📥 이수율 조회하기"):
    if not name or not phone_last4:
        st.warning("⚠️ 이름과 전화번호 뒷자리를 모두 입력해주세요.")
    else:
        user = find_user(name, phone_last4)
        if user:
            st.success(f"✅ {user['이름']} 선생님의 이수 정보")

            # ✅ 각 블록 출력
            st.markdown(render_course_table("① 사전진단 (2차시 / 100분)", 2, "사전진단_"), unsafe_allow_html=True)
            st.markdown(render_course_table("② 사전워크숍 (3차시 / 150분)", 3, "사전워크숍_"), unsafe_allow_html=True)
            st.markdown(render_course_table("③ 원격연수 (16차시 / 800분)", 16, "원격연수_"), unsafe_allow_html=True)
            st.markdown(render_course_table("④ 집합연수 (14차시 / 700분)", 14, "집합연수_"), unsafe_allow_html=True)
            st.markdown(render_course_table("⑤ 컨퍼런스 (5차시 / 250분)", 5, "컨퍼런스_"), unsafe_allow_html=True)

            # ✅ 총 이수 시간 및 차시 계산
            all_keys = [f"사전진단_{i}차" for i in range(1,3)] + \
                       [f"사전워크숍_{i}차" for i in range(1,4)] + \
                       [f"원격연수_{i}차" for i in range(1,17)] + \
                       [f"집합연수_{i}차" for i in range(1,15)] + \
                       [f"컨퍼런스_{i}차" for i in range(1,6)]
            total_min = sum([safe_int(user.get(k, 0)) for k in all_keys])
            completed_sessions = sum([1 for k in all_keys if safe_int(user.get(k, 0)) >= 40])
            completion_percent = round((completed_sessions / 40) * 100)

            # ✅ 총 이수율
            st.markdown("""
                <div style="border-top:1px solid #ccc; margin-top:2rem; padding-top:1rem; font-weight:600; font-size:1.1rem; text-align:center;">
                    총 이수율<br>
                    {:02d}차시 / 40차시 ({:.0f}%)
                </div>
            """.format(completed_sessions, completion_percent), unsafe_allow_html=True)

            # ✅ 이수 여부 박스
            if user.get("이수여부") == "이수":
                st.markdown("""
                    <div style="margin-top:1rem; background-color:#fce4ec; padding:1rem; text-align:center; border-radius:10px; color:#880e4f;">
                        📌 <b>이수</b>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                    <div style="margin-top:1rem; background-color:#fce4ec; padding:1rem; text-align:center; border-radius:10px; color:#880e4f;">
                        ❌ <b>미이수</b>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.error("😢 입력하신 정보와 일치하는 사용자가 없습니다.")

import streamlit as st
import Script_Engineer_QuanLyBaiLam
import Script_Login

def render():
    submissions = Script_Engineer_QuanLyBaiLam.get_all_submissions()

    c1, c2 = st.columns([1, 2])
    with c1:
        sub_filter = st.selectbox(
            "Môn học",
            ["ALL", "MATH", "CHEM"],
            format_func=lambda x: "Tất cả" if x == "ALL" else ("Toán học" if x == "MATH" else "Hóa học")
        )
    with c2:
        user_search = st.text_input("Tìm học viên", placeholder="sv001 / Nguyễn Minh Quân...")

    filtered = Script_Engineer_QuanLyBaiLam.filter_submissions(submissions, sub_filter, user_search)

    if not filtered:
        st.info("Chưa có bài làm khớp bộ lọc.")
        return

    headers = ["Mã bài", "Học viên", "Môn", "Điểm", "Thời gian", "Năng lực", "Ngày nộp"]
    rows = []
    for s in filtered:
        sub_name = "Toán" if s["subject"] == "MATH" else "Hóa"
        score_before = Script_Login.theta_to_score100(s["theta_before"])
        score_after = Script_Login.theta_to_score100(s["theta_after"])
        diff_score = score_after - score_before
        diff_str = f"+{diff_score}" if diff_score >= 0 else str(diff_score)
        color_str = "#124874" if diff_score >= 0 else "#CF373D"

        rows.append([
            f"<b>{s['submission_id']}</b>",
            f"{s.get('full_name', s['username'])} (<code>{s['username']}</code>)",
            f'<span class="badge-blue">{sub_name}</span>',
            f"<b>{s['score_10']}/10</b> ({s['correct_count']}/{s['total_questions']})",
            f"{s['duration_sec']}s",
            f"<b>{score_after}/100</b> (<span style='color:{color_str}; font-weight:700;'>{diff_str}</span>)",
            s["timestamp"]
        ])

    st.markdown(Script_Login.render_html_table(headers, rows), unsafe_allow_html=True)

    st.markdown('<div class="section-heading">Chi tiết & Quản lý bài làm</div>', unsafe_allow_html=True)
    selected_id = st.selectbox(
        "Chọn bài thi",
        [x["submission_id"] for x in filtered],
        format_func=lambda sid: next(
            f"{x['submission_id']} | {x.get('full_name', x['username'])} | {x['score_10']}/10 ({x['timestamp']})"
            for x in filtered if x["submission_id"] == sid
        )
    )

    detail = Script_Engineer_QuanLyBaiLam.get_submission_detail(selected_id)
    if detail:
        st.markdown(
            f'<div class="kbs-box">'
            f'<b>Mã bài:</b> <code>{detail["submission_id"]}</code> | '
            f'<b>Học viên:</b> {detail.get("full_name", detail["username"])} (<code>{detail["username"]}</code>) | '
            f'<b>Điểm:</b> {detail["score_10"]}/10 | <b>Tổng thời gian:</b> {detail["duration_sec"]}s / {detail["expected_sec"]}s'
            f'</div>',
            unsafe_allow_html=True
        )
        new_conc = st.text_area("Nhận xét chuyên gia", value=detail.get("expert_conclusion", ""), key=f"conc_{selected_id}")
        new_sc = st.number_input("Điểm số (thang 10)", 0.0, 10.0, float(detail["score_10"]), 0.25, key=f"sc_{selected_id}")
        b1, b2 = st.columns(2)
        with b1:
            if st.button("Lưu cập nhật bài làm", type="primary", use_container_width=True):
                ok, msg = Script_Engineer_QuanLyBaiLam.update_submission_conclusion(selected_id, new_conc, new_sc)
                if ok:
                    st.success(msg)
                    st.rerun()
        with b2:
            if st.button("Xóa bài làm này", type="secondary", use_container_width=True):
                ok, msg = Script_Engineer_QuanLyBaiLam.delete_submission(selected_id)
                if ok:
                    st.success(msg)
                    st.rerun()

        for idx, r in enumerate(detail.get("question_reviews", []), 1):
            badge = "badge-blue" if r["is_correct"] else "badge-red"
            status_text = "ĐÚNG" if r["is_correct"] else "SAI"
            f_info = Script_Login.get_formula_rule_info(r.get("formula_rule", "DRV_POW"))
            time_badge = f'<span class="badge-outline">Thời gian: {r["time_spent_sec"]}s / {r.get("expected_time", "-")}s</span>' if "time_spent_sec" in r else ""
            st.markdown(
                f'<div class="kbs-box {"" if r["is_correct"] else "accent"}" style="padding:0.65rem 1rem; margin-bottom:0.4rem;">'
                f'<span class="{badge}">Câu {idx:02d}: {status_text}</span> '
                f'<span class="badge-outline">{r["id"]}</span> '
                f'<span class="badge-outline">{f_info["name"]}</span> '
                f'{time_badge}'
                f'</div>',
                unsafe_allow_html=True
            )
            st.markdown(f"**Đề:** {r['content']}")
            st.markdown(f"- **Chọn:** `{r['user_choice'] or 'Trống'}` | **Đáp án đúng:** `{r['correct_answer']}`")
            st.markdown(f"- **Cách làm:** {r.get('general_method', f_info['general_method'])}")
            st.markdown(f"- **Lời giải:** {r['explanation']}")
            st.markdown("<hr style='margin:0.65rem 0 0.9rem 0; border:none; border-top:1px solid #E2E8F0;'>", unsafe_allow_html=True)

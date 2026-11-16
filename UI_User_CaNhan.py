import streamlit as st
import Script_User_CaNhan
import Script_Login

def render():
    username = st.session_state.username
    profile = Script_User_CaNhan.get_personal_competency_report(username)

    st.markdown('<div class="section-heading">Tiến độ 6 chuyên đề</div>', unsafe_allow_html=True)
    headers = ["Mã", "Chuyên đề", "Môn", "Kết quả", "Trạng thái"]
    rows = []
    for node in profile["node_breakdown"]:
        status_cls = "badge-red" if node["status"] == "Cần ôn lại" else "badge-blue"
        rows.append([
            f"<code>{node['code']}</code>",
            f"<b>{node['name']}</b>",
            node["subject_vi"],
            f"{node['correct']}/{node['total']} ({node['accuracy']}%)",
            f'<span class="{status_cls}">{node["status"]}</span>'
        ])
    st.markdown(Script_Login.render_html_table(headers, rows), unsafe_allow_html=True)

    with st.expander("Cập nhật thông tin cá nhân"):
        with st.form("form_update_self"):
            c1, c2 = st.columns(2)
            with c1:
                new_fname = st.text_input("Họ và tên", value=profile["full_name"])
            with c2:
                new_pwd = st.text_input("Mật khẩu mới (để trống nếu giữ nguyên)", type="password")
            if st.form_submit_button("Lưu thông tin", type="primary"):
                ok, msg = Script_User_CaNhan.update_own_account(username, new_fname, new_pwd)
                if ok:
                    st.session_state.full_name = new_fname
                    st.success(msg)
                    st.rerun()

    st.markdown('<div class="section-heading">Lịch sử bài làm cá nhân</div>', unsafe_allow_html=True)
    if profile["history"]:
        h_headers = ["Mã bài", "Môn", "Điểm", "Thời gian", "Năng lực", "Ngày nộp"]
        h_rows = []
        for h in profile["history"]:
            sub_vi = "Toán" if h["subject"] == "MATH" else "Hóa"
            s100 = Script_Login.theta_to_score100(h["theta_after"])
            h_rows.append([
                f"<b>{h['submission_id']}</b>",
                sub_vi,
                f"<b>{h['score_10']}/10</b>",
                f"{h['duration_sec']}s",
                f"<b>{s100}/100</b>",
                h["timestamp"]
            ])
        st.markdown(Script_Login.render_html_table(h_headers, h_rows), unsafe_allow_html=True)

        chosen_sub = st.selectbox(
            "Chọn bài thi để xem chi tiết hoặc xóa:",
            [h["submission_id"] for h in profile["history"]],
            format_func=lambda sid: next(
                f"{h['submission_id']} | Điểm: {h['score_10']}/10 ({h['timestamp']})"
                for h in profile["history"] if h["submission_id"] == sid
            )
        )
        detail = next((h for h in profile["history"] if h["submission_id"] == chosen_sub), None)
        if detail:
            st.markdown(
                f'<div class="kbs-box accent">'
                f'<b>Nhận xét (<code>{detail["submission_id"]}</code>):</b> {detail["expert_conclusion"]}'
                f'</div>',
                unsafe_allow_html=True
            )
            if st.button("Xóa bài thi này khỏi lịch sử", type="secondary"):
                ok, msg = Script_User_CaNhan.delete_own_submission(username, chosen_sub)
                if ok:
                    st.success(msg)
                    st.rerun()

            for idx, r in enumerate(detail.get("question_reviews", []), 1):
                b_cls = "badge-blue" if r["is_correct"] else "badge-red"
                f_info = Script_Login.get_formula_rule_info(r.get("formula_rule", "DRV_POW"))
                time_badge = f'<span class="badge-outline">Thời gian: {r["time_spent_sec"]}s / {r.get("expected_time", "-")}s</span>' if "time_spent_sec" in r else ""
                st.markdown(
                    f'<div class="kbs-box {"" if r["is_correct"] else "accent"}" style="padding:0.55rem 0.9rem; margin-bottom:0.4rem;">'
                    f'<span class="{b_cls}">Câu {idx:02d}: {"ĐÚNG" if r["is_correct"] else "SAI"}</span> '
                    f'<span class="badge-outline">{f_info["name"]}</span> '
                    f'{time_badge}'
                    f'</div>',
                    unsafe_allow_html=True
                )
                st.markdown(f"**Đề:** {r['content']}")
                st.markdown(f"- **Bạn chọn:** `{r['user_choice'] or 'Trống'}` | **Đáp án đúng:** `{r['correct_answer']}`")
                st.markdown(f"- **Cách làm:** {r.get('general_method', f_info['general_method'])}")
                st.markdown(f"- **Lời giải:** {r['explanation']}")
                st.markdown("<hr style='margin:0.65rem 0 0.85rem 0; border:none; border-top:1px solid #E2E8F0;'>", unsafe_allow_html=True)
    else:
        st.info("Chưa có lịch sử bài làm.")

import streamlit as st
import Script_User_TrangChu
import Script_Login

def render():
    username = st.session_state.username
    dashboard = Script_User_TrangChu.get_student_dashboard(username)
    diff_names = {"DE": "Cơ bản (Dễ)", "TRUNG_BINH": "Trung bình", "KHA": "Khá", "KHO": "Nâng cao (Khó)"}
    rec_vi = diff_names.get(dashboard["recommended_difficulty"], dashboard["recommended_difficulty"])

    st.markdown(
        f'<div class="kpi-grid">'
        f'<div class="kpi-card"><div class="stat-label">Năng lực Toán</div><div class="stat-value-blue">{dashboard["score_math"]}/100</div><div class="stat-sub">{dashboard["level_math"].split(" - ")[0]}</div></div>'
        f'<div class="kpi-card"><div class="stat-label">Năng lực Hóa</div><div class="stat-value-blue">{dashboard["score_chem"]}/100</div><div class="stat-sub">{dashboard["level_chem"].split(" - ")[0]}</div></div>'
        f'<div class="kpi-card"><div class="stat-label">Đề đã làm</div><div class="stat-value-blue">{dashboard["completed_exams"]}</div><div class="stat-sub">Đúng TB: {dashboard["avg_accuracy"]}%</div></div>'
        f'<div class="kpi-card accent"><div class="stat-label">Mức đề gợi ý</div><div class="stat-value-red" style="font-size:1.25rem;">{rec_vi}</div><div class="stat-sub">Thích ứng IRT</div></div>'
        f'</div>',
        unsafe_allow_html=True
    )

    st.markdown('<div class="section-heading">Tiến độ 6 chuyên đề trọng tâm</div>', unsafe_allow_html=True)
    headers = ["Mã", "Chuyên đề", "Môn", "Số câu đúng", "Mức độ nắm vững"]
    rows = []
    for m in dashboard["concept_mastery"]:
        badge = "badge-red" if m["mastery_pct"] < 50 else "badge-blue"
        rows.append([
            f"<code>{m['node']}</code>",
            f"<b>{m['name']}</b>",
            m["subject_vi"],
            f"{m['correct']}/{m['total']}",
            f'<span class="{badge}">{m["mastery_pct"]}%</span>'
        ])
    st.markdown(Script_Login.render_html_table(headers, rows), unsafe_allow_html=True)

    st.markdown('<div class="section-heading">Khuyến nghị ôn tập</div>', unsafe_allow_html=True)
    for rec in dashboard["recommendations"]:
        st.markdown(
            f'<div class="kbs-box accent">'
            f'<span class="badge-red">{rec["priority"]}</span> <b>{rec["title"]}</b>'
            f'<div style="font-size:0.86rem; color:#0F172A; margin-top:0.35rem;">{rec["reason"]}</div>'
            f'</div>',
            unsafe_allow_html=True
        )

    if st.button("Tạo đề luyện tập ngay", type="primary", use_container_width=True):
        st.session_state.current_page = "USR_TAOBAI"
        st.rerun()

    with st.expander("Bảng công thức & Cách giải tổng quát 6 chuyên đề"):
        for r_code, r_meta in Script_Login.get_all_formula_rules().items():
            st.markdown(f"**{r_meta['name']}**: {r_meta['latex_formula']}")
            st.caption(r_meta["general_method"])

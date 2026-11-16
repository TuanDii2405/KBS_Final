import streamlit as st
import Script_Engineer_TrangChu
import Script_Login

def render():
    data = Script_Engineer_TrangChu.get_dashboard_overview()

    st.markdown(
        f'<div class="kpi-grid">'
        f'<div class="kpi-card"><div class="stat-label">Câu hỏi</div><div class="stat-value-blue">{data["total_questions"]}</div><div class="stat-sub">Toán: {data["math_count"]} | Hóa: {data["chem_count"]}</div></div>'
        f'<div class="kpi-card"><div class="stat-label">Học viên</div><div class="stat-value-blue">{data["total_students"]}</div><div class="stat-sub">TaiKhoan.txt</div></div>'
        f'<div class="kpi-card"><div class="stat-label">Bài nộp</div><div class="stat-value-blue">{data["total_submissions"]}</div><div class="stat-sub">TB: {data["avg_duration"]}s/câu</div></div>'
        f'<div class="kpi-card accent"><div class="stat-label">Lệch độ khó</div><div class="stat-value-red">{data["drift_alerts"]}</div><div class="stat-sub">Cần hiệu chỉnh</div></div>'
        f'</div>',
        unsafe_allow_html=True
    )

    st.markdown('<div class="section-heading">Phân bố 6 chuyên đề</div>', unsafe_allow_html=True)
    headers = ["Mã", "Chuyên đề", "Môn", "Dễ", "T.Bình", "Khá", "Khó", "Tổng"]
    rows = []
    for row in data["topic_distribution"]:
        rows.append([
            f"<code>{row['code']}</code>",
            f"<b>{row['name']}</b>",
            row["subject"],
            str(row["de"]),
            str(row["tb"]),
            str(row["kha"]),
            f'<span class="badge-red">{row["kho"]}</span>',
            f"<b>{row['total']}</b>"
        ])
    st.markdown(Script_Login.render_html_table(headers, rows), unsafe_allow_html=True)

    st.markdown('<div class="section-heading">Quản lý luật suy diễn (LuatSuyDien.txt)</div>', unsafe_allow_html=True)
    rules = data["active_rules"]
    rule_headers = ["Mã luật", "Tên luật", "Ưu tiên", "Điều kiện", "Hành động"]
    rule_rows = [
        [
            f"<code>{r['id']}</code>",
            f"<b>{r['name']}</b>",
            f'<span class="{"badge-red" if r["priority"] == "HIGH" else "badge-blue"}">{r["priority"]}</span>',
            r["condition_vi"],
            r["action_vi"]
        ]
        for r in rules
    ]
    st.markdown(Script_Login.render_html_table(rule_headers, rule_rows), unsafe_allow_html=True)

    tab_add_r, tab_edit_r, tab_del_r = st.tabs(["Thêm luật", "Sửa luật", "Xóa luật"])

    with tab_add_r:
        with st.form("form_add_rule", clear_on_submit=True):
            rc1, rc2, rc3 = st.columns([1, 2, 1])
            with rc1:
                new_rid = st.text_input("Mã luật", placeholder="R_CUSTOM_01")
            with rc2:
                new_rname = st.text_input("Tên luật", placeholder="Luật cảnh báo thời gian")
            with rc3:
                new_rprio = st.selectbox("Mức ưu tiên", ["HIGH", "NORMAL"])
            new_rcond = st.text_input("Điều kiện kích hoạt")
            new_ract = st.text_input("Hành động suy diễn")
            if st.form_submit_button("Thêm luật", type="primary"):
                ok, msg = Script_Engineer_TrangChu.add_inference_rule(new_rid, new_rname, new_rprio, new_rcond, new_ract)
                if ok:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

    with tab_edit_r:
        if rules:
            sel_rid = st.selectbox("Chọn mã luật cần sửa", [r["id"] for r in rules], key="edit_rule_sel")
            cur_rule = next(r for r in rules if r["id"] == sel_rid)
            with st.form("form_edit_rule"):
                ec1, ec2 = st.columns([2, 1])
                with ec1:
                    e_name = st.text_input("Tên luật", value=cur_rule["name"])
                with ec2:
                    e_prio = st.selectbox("Mức ưu tiên", ["HIGH", "NORMAL"], index=0 if cur_rule["priority"] == "HIGH" else 1)
                e_cond = st.text_input("Điều kiện", value=cur_rule["condition_vi"])
                e_act = st.text_input("Hành động", value=cur_rule["action_vi"])
                if st.form_submit_button("Lưu cập nhật", type="primary"):
                    ok, msg = Script_Engineer_TrangChu.update_inference_rule(sel_rid, e_name, e_prio, e_cond, e_act)
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

    with tab_del_r:
        if rules:
            del_rid = st.selectbox("Chọn mã luật cần xóa", [r["id"] for r in rules], key="del_rule_sel")
            if st.button("Xóa luật đã chọn", type="primary"):
                ok, msg = Script_Engineer_TrangChu.delete_inference_rule(del_rid)
                if ok:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

    with st.expander("Tra cứu 16 quy tắc công thức chuẩn"):
        for r_code, r_meta in Script_Login.get_all_formula_rules().items():
            st.markdown(f"**`{r_code}` — {r_meta['name']}**: {r_meta['latex_formula']}")
            st.caption(r_meta["general_method"])

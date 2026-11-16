import streamlit as st
import Script_Engineer_QuanLyNguoiDung
import Script_Login

def render():
    users = Script_Engineer_QuanLyNguoiDung.get_all_student_profiles()

    st.markdown('<div class="section-heading">Danh sách học viên (TaiKhoan.txt)</div>', unsafe_allow_html=True)
    headers = ["Mã TK", "Họ và tên", "Toán (Thang 100)", "Hóa (Thang 100)", "Số đề", "Chuyên đề cần củng cố"]
    rows = []
    for u in users:
        rows.append([
            f"<code>{u['username']}</code>",
            f"<b>{u['full_name']}</b>",
            f"<b>{u['score_math']}/100</b> <span class='badge-outline'>{u['level_math']}</span>",
            f"<b>{u['score_chem']}/100</b> <span class='badge-outline'>{u['level_chem']}</span>",
            f"{u['exams_taken']}",
            f"<span class='badge-red'>{u['weakest_topic']}</span>"
        ])
    st.markdown(Script_Login.render_html_table(headers, rows), unsafe_allow_html=True)

    st.markdown('<div class="section-heading">Quản lý tài khoản học viên</div>', unsafe_allow_html=True)
    tab_add, tab_edit, tab_del = st.tabs(["Thêm học viên", "Sửa hồ sơ & năng lực", "Xóa học viên"])

    with tab_add:
        with st.form("form_add_student", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            with c1:
                nu_id = st.text_input("Mã tài khoản", placeholder="sv005")
            with c2:
                nu_name = st.text_input("Họ và tên", placeholder="Lê Hoàng Nam")
            with c3:
                nu_pass = st.text_input("Mật khẩu", value="123456")
            s1, s2 = st.columns(2)
            with s1:
                nu_math = st.slider("Năng lực Toán khởi tạo", 0, 100, 50)
            with s2:
                nu_chem = st.slider("Năng lực Hóa khởi tạo", 0, 100, 50)
            if st.form_submit_button("Tạo học viên mới", type="primary", use_container_width=True):
                ok, msg = Script_Engineer_QuanLyNguoiDung.create_student_account(nu_id, nu_name, nu_pass, nu_math, nu_chem)
                if ok:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

    with tab_edit:
        if users:
            target_u = st.selectbox(
                "Chọn học viên",
                [u["username"] for u in users],
                format_func=lambda uname: next(f"{x['full_name']} ({x['username']})" for x in users if x["username"] == uname)
            )
            cur_u = next(x for x in users if x["username"] == target_u)
            with st.form("form_edit_student"):
                ec1, ec2 = st.columns(2)
                with ec1:
                    e_name = st.text_input("Họ và tên", value=cur_u["full_name"])
                with ec2:
                    e_pass = st.text_input("Mật khẩu", value=cur_u["password"])
                es1, es2 = st.columns(2)
                with es1:
                    e_math = st.slider("Điểm năng lực Toán (0 - 100)", 0, 100, int(cur_u["score_math"]))
                with es2:
                    e_chem = st.slider("Điểm năng lực Hóa (0 - 100)", 0, 100, int(cur_u["score_chem"]))
                reset_chk = st.checkbox("Đặt lại thống kê 6 chuyên đề về 0")
                if st.form_submit_button("Lưu thay đổi", type="primary", use_container_width=True):
                    ok, msg = Script_Engineer_QuanLyNguoiDung.update_student_profile(
                        target_u, e_name, e_pass, e_math, e_chem, reset_chk
                    )
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

    with tab_del:
        if users:
            del_u = st.selectbox(
                "Chọn học viên cần xóa",
                [u["username"] for u in users],
                format_func=lambda uname: next(f"{x['full_name']} ({x['username']})" for x in users if x["username"] == uname),
                key="del_stu_sel"
            )
            if st.button("Xóa tài khoản học viên", type="primary"):
                ok, msg = Script_Engineer_QuanLyNguoiDung.delete_student_account(del_u)
                if ok:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

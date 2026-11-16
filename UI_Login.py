import streamlit as st
import Script_Login

def render():
    st.markdown("""
    <style>
        .block-container {
            max-width: 440px !important;
            padding-top: 4.5rem !important;
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown(
        '<div class="top-brand-bar" style="justify-content:center; margin-bottom:1rem;">'
        '<div class="top-brand-title">ĐĂNG NHẬP HỆ THỐNG</div>'
        '</div>',
        unsafe_allow_html=True
    )

    tab_login, tab_reg = st.tabs(["Đăng nhập", "Đăng ký"])

    with tab_login:
        with st.form("form_login"):
            u_name = st.text_input("Tài khoản", placeholder="engineer / sv001")
            u_pass = st.text_input("Mật khẩu", type="password", placeholder="123456")
            btn_login = st.form_submit_button("Đăng nhập", type="primary", use_container_width=True)

            if btn_login:
                ok, user_info, msg = Script_Login.authenticate(u_name.strip(), u_pass.strip())
                if ok:
                    st.session_state.authenticated = True
                    st.session_state.username = user_info["username"]
                    st.session_state.full_name = user_info["full_name"]
                    st.session_state.role = user_info["role"]
                    st.session_state.current_page = "ENG_HOME" if user_info["role"] == "engineer" else "USR_HOME"
                    st.rerun()
                else:
                    st.error(msg)

        st.caption("Tài khoản mẫu: `engineer` | `sv001` | `sv002` (Mật khẩu: `123456`)")

    with tab_reg:
        with st.form("form_register", clear_on_submit=True):
            reg_user = st.text_input("Tài khoản mới", placeholder="sv005")
            reg_name = st.text_input("Họ và tên", placeholder="Nguyễn Văn An")
            reg_pass = st.text_input("Mật khẩu", type="password")
            reg_pass2 = st.text_input("Xác nhận mật khẩu", type="password")
            btn_reg = st.form_submit_button("Tạo tài khoản", type="secondary", use_container_width=True)

            if btn_reg:
                if reg_pass != reg_pass2:
                    st.error("Mật khẩu xác nhận không khớp.")
                else:
                    ok, msg = Script_Login.register_user(reg_user.strip(), reg_pass.strip(), reg_name.strip())
                    if ok:
                        st.success(msg)
                    else:
                        st.error(msg)

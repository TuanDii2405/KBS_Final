import streamlit as st
import UI_Login
import UI_Engineer_TrangChu
import UI_Engineer_QuanLyDeThi
import UI_Engineer_QuanLyBaiLam
import UI_Engineer_QuanLyNguoiDung
import UI_Engineer_ThongKe
import UI_User_TrangChu
import UI_User_TaoBaiLam
import UI_User_LamBai
import UI_User_CaNhan

st.set_page_config(
    page_title="KBS Trắc Nghiệm",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def inject_custom_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        :root {
            --bg-white: #FFFFFF;
            --bg-subtle: #F8FAFC;
            --cerulean: #124874;
            --cerulean-dark: #0D3556;
            --jasper: #CF373D;
            --jasper-dark: #A8282D;
            --text-dark: #0F172A;
            --text-gray: #475569;
            --border-line: #E2E8F0;
            --border-strong: #CBD5E1;
        }

        [data-testid="stSidebar"], [data-testid="collapsedControl"], header[data-testid="stHeader"] {
            display: none !important;
        }

        .block-container {
            padding-top: 1.25rem !important;
            padding-bottom: 3rem !important;
            max-width: 1040px !important;
        }

        html, body, [class*="css"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            color: var(--text-dark);
            background-color: var(--bg-white);
        }

        .stApp {
            background-color: var(--bg-white);
        }

        /* Code badge đồng bộ bảng màu Cerulean thay vì xanh lá mặc định */
        code {
            color: var(--cerulean) !important;
            background-color: #F1F5F9 !important;
            border: 1px solid #E2E8F0 !important;
            padding: 0.12rem 0.4rem !important;
            border-radius: 3px !important;
            font-size: 0.8em !important;
            font-weight: 600 !important;
        }

        /* Chỉ style Form sạch sẽ, KHÔNG đụng vào stVerticalBlockBorderWrapper để tránh lồng khung */
        [data-testid="stForm"] {
            background-color: var(--bg-white) !important;
            border: 1px solid var(--border-strong) !important;
            border-radius: 4px !important;
            padding: 1.25rem !important;
        }

        .katex {
            font-size: 1.05em !important;
            color: #0F172A;
        }

        /* Thanh tiêu đề trên cùng */
        .top-brand-bar {
            background-color: var(--cerulean);
            color: #FFFFFF;
            padding: 0.85rem 1.25rem;
            border-bottom: 3px solid var(--jasper);
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.75rem;
            border-radius: 4px;
        }

        .top-brand-title {
            font-size: 1.02rem;
            font-weight: 700;
            letter-spacing: 0.03em;
            margin: 0;
        }

        .top-user-badge {
            font-size: 0.82rem;
            color: #E2E8F0;
            font-weight: 500;
        }

        .top-user-badge b {
            color: #FFFFFF;
        }

        /* Nút bấm không bao giờ bị gãy dòng */
        div.stButton > button, div.stFormSubmitButton > button {
            white-space: nowrap !important;
            border-radius: 4px !important;
            font-size: 0.84rem !important;
            padding: 0.48rem 0.75rem !important;
            min-height: 38px !important;
            transition: background-color 0.15s ease, border-color 0.15s ease;
        }

        div.stButton > button[kind="primary"], div.stFormSubmitButton > button[kind="primary"] {
            background-color: var(--jasper) !important;
            color: #FFFFFF !important;
            border: 1px solid var(--jasper) !important;
            font-weight: 600 !important;
        }

        div.stButton > button[kind="primary"]:hover, div.stFormSubmitButton > button[kind="primary"]:hover {
            background-color: var(--jasper-dark) !important;
            border-color: var(--jasper-dark) !important;
        }

        div.stButton > button[kind="secondary"], div.stFormSubmitButton > button[kind="secondary"] {
            background-color: var(--cerulean) !important;
            color: #FFFFFF !important;
            border: 1px solid var(--cerulean) !important;
            font-weight: 500 !important;
        }

        div.stButton > button[kind="secondary"]:hover, div.stFormSubmitButton > button[kind="secondary"]:hover {
            background-color: var(--cerulean-dark) !important;
            border-color: var(--cerulean-dark) !important;
        }

        /* Lưới 4 thẻ KPI cao đều nhau tuyệt đối */
        .kpi-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 12px;
            margin: 0.75rem 0 1.25rem 0;
        }

        .kpi-card {
            background-color: var(--bg-white);
            border: 1px solid var(--border-strong);
            border-top: 3px solid var(--cerulean);
            border-radius: 4px;
            padding: 0.9rem 1rem;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            min-height: 102px;
        }

        .kpi-card.accent {
            border-top-color: var(--jasper);
        }

        .stat-label {
            font-size: 0.73rem;
            font-weight: 700;
            text-transform: uppercase;
            color: var(--text-gray);
            letter-spacing: 0.04em;
        }

        .stat-value-blue {
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--cerulean);
            line-height: 1.2;
            margin: 0.25rem 0;
        }

        .stat-value-red {
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--jasper);
            line-height: 1.2;
            margin: 0.25rem 0;
        }

        .stat-sub {
            font-size: 0.78rem;
            color: var(--text-gray);
        }

        /* Thẻ nội dung & Khuyến nghị */
        .kbs-box {
            background-color: var(--bg-white);
            border: 1px solid var(--border-strong);
            border-left: 4px solid var(--cerulean);
            border-radius: 4px;
            padding: 0.95rem 1.1rem;
            margin-bottom: 0.75rem;
        }

        .kbs-box.accent {
            border-left-color: var(--jasper);
        }

        /* Tiêu đề phân khu */
        .section-heading {
            font-size: 0.85rem;
            font-weight: 700;
            color: var(--cerulean);
            border-left: 4px solid var(--jasper);
            padding-left: 0.65rem;
            margin: 1.35rem 0 0.75rem 0;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }

        /* Nhãn trạng thái */
        .badge-blue {
            background-color: var(--cerulean);
            color: #FFFFFF;
            font-size: 0.73rem;
            font-weight: 600;
            padding: 0.2rem 0.55rem;
            border-radius: 3px;
            margin-right: 0.35rem;
            display: inline-block;
            white-space: nowrap;
        }

        .badge-red {
            background-color: var(--jasper);
            color: #FFFFFF;
            font-size: 0.73rem;
            font-weight: 600;
            padding: 0.2rem 0.55rem;
            border-radius: 3px;
            margin-right: 0.35rem;
            display: inline-block;
            white-space: nowrap;
        }

        .badge-outline {
            border: 1px solid var(--cerulean);
            color: var(--cerulean);
            background-color: #F8FAFC;
            font-size: 0.73rem;
            font-weight: 500;
            padding: 0.16rem 0.5rem;
            border-radius: 3px;
            margin-right: 0.35rem;
            display: inline-block;
            white-space: nowrap;
        }

        /* Bảng dữ liệu chuẩn */
        .clean-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.85rem;
            margin-bottom: 1rem;
            border: 1px solid var(--border-strong);
        }

        .clean-table th {
            background-color: var(--cerulean);
            color: #FFFFFF;
            text-align: left;
            padding: 0.65rem 0.8rem;
            font-weight: 600;
            font-size: 0.75rem;
            border-bottom: 2px solid var(--jasper);
            text-transform: uppercase;
            letter-spacing: 0.03em;
            white-space: nowrap;
        }

        .clean-table td {
            padding: 0.6rem 0.8rem;
            border-bottom: 1px solid var(--border-line);
            border-right: 1px solid var(--border-line);
            background-color: var(--bg-white);
            color: var(--text-dark);
            vertical-align: middle;
        }

        .clean-table tr:nth-child(even) td {
            background-color: var(--bg-subtle);
        }

        .clean-table tr:hover td {
            background-color: #F1F5F9;
        }
    </style>
    """, unsafe_allow_html=True)

def init_session():
    defaults = {
        "authenticated": False,
        "username": None,
        "full_name": None,
        "role": None,
        "current_page": "LOGIN",
        "active_exam": None,
        "exam_result": None
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

def render_top_navigation():
    role_tag = "QUẢN TRỊ" if st.session_state.role == "engineer" else "HỌC VIÊN"
    st.markdown(
        f'<div class="top-brand-bar">'
        f'<div class="top-brand-title">KBS TRẮC NGHIỆM</div>'
        f'<div class="top-user-badge">[{role_tag}] <b>{st.session_state.full_name}</b> ({st.session_state.username})</div>'
        f'</div>',
        unsafe_allow_html=True
    )

    cur = st.session_state.current_page

    if st.session_state.role == "engineer":
        nav_items = [
            ("ENG_HOME", "Tổng quan"),
            ("ENG_DETHI", "Câu hỏi"),
            ("ENG_BAILAM", "Bài làm"),
            ("ENG_NGUOIDUNG", "Học viên"),
            ("ENG_THONGKE", "Độ khó")
        ]
        cols = st.columns([1.15, 1.1, 1.1, 1.1, 1.1, 0.85])
        for idx, (page_code, label) in enumerate(nav_items):
            with cols[idx]:
                btn_type = "primary" if cur == page_code else "secondary"
                if st.button(label, key=f"nav_{page_code}", type=btn_type, use_container_width=True):
                    st.session_state.current_page = page_code
                    st.rerun()
        with cols[5]:
            if st.button("Thoát", key="nav_logout_eng", type="secondary", use_container_width=True):
                for k in list(st.session_state.keys()):
                    del st.session_state[k]
                st.rerun()
    else:
        nav_items = [
            ("USR_HOME", "Trang chủ"),
            ("USR_TAOBAI", "Tạo đề"),
            ("USR_LAMBAI", "Làm bài"),
            ("USR_CANHAN", "Cá nhân")
        ]
        cols = st.columns([1.15, 1.15, 1.15, 1.15, 0.9])
        for idx, (page_code, label) in enumerate(nav_items):
            with cols[idx]:
                btn_type = "primary" if cur == page_code else "secondary"
                if st.button(label, key=f"nav_{page_code}", type=btn_type, use_container_width=True):
                    st.session_state.current_page = page_code
                    st.rerun()
        with cols[4]:
            if st.button("Thoát", key="nav_logout_usr", type="secondary", use_container_width=True):
                for k in list(st.session_state.keys()):
                    del st.session_state[k]
                st.rerun()

    st.markdown("<div style='height:0.25rem;'></div>", unsafe_allow_html=True)

def main():
    inject_custom_css()
    init_session()

    if not st.session_state.authenticated:
        UI_Login.render()
        return

    render_top_navigation()

    page = st.session_state.current_page
    if page == "ENG_HOME":
        UI_Engineer_TrangChu.render()
    elif page == "ENG_DETHI":
        UI_Engineer_QuanLyDeThi.render()
    elif page == "ENG_BAILAM":
        UI_Engineer_QuanLyBaiLam.render()
    elif page == "ENG_NGUOIDUNG":
        UI_Engineer_QuanLyNguoiDung.render()
    elif page == "ENG_THONGKE":
        UI_Engineer_ThongKe.render()
    elif page == "USR_HOME":
        UI_User_TrangChu.render()
    elif page == "USR_TAOBAI":
        UI_User_TaoBaiLam.render()
    elif page == "USR_LAMBAI":
        UI_User_LamBai.render()
    elif page == "USR_CANHAN":
        UI_User_CaNhan.render()
    else:
        if st.session_state.role == "engineer":
            UI_Engineer_TrangChu.render()
        else:
            UI_User_TrangChu.render()

if __name__ == "__main__":
    main()

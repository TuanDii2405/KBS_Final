import streamlit as st
import Script_User_TaoBaiLam
import Script_Login

def render():
    username = st.session_state.username
    diff_names = {"DE": "Dễ (Cơ bản)", "TRUNG_BINH": "Trung bình", "KHA": "Khá (Vận dụng)", "KHO": "Khó (Vận dụng cao)"}

    st.markdown('<div class="section-heading">Thiết lập đề luyện tập cá nhân hóa</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        subject = st.selectbox(
            "1. Môn học",
            ["MATH", "CHEM"],
            format_func=lambda x: "Toán học (Đạo hàm & Nguyên hàm)" if x == "MATH" else "Hóa học (Cân bằng PTHH & Phản ứng vô cơ)",
            key="usr_gen_sub"
        )
    with c2:
        sub_nodes = Script_Login.get_filtered_concept_nodes(subject=subject)
        concept_node = st.selectbox(
            "2. Chuyên đề",
            ["ALL"] + list(sub_nodes.keys()),
            format_func=lambda k: "Tất cả chuyên đề của môn" if k == "ALL" else sub_nodes[k]["name"],
            key="usr_gen_node"
        )

    c3, c4 = st.columns(2)
    with c3:
        sub_rules = Script_Login.get_filtered_formula_rules(subject=subject, concept_node=concept_node)
        formula_rule = st.selectbox(
            "3. Quy tắc công thức",
            ["ALL"] + list(sub_rules.keys()),
            format_func=lambda k: "Tất cả quy tắc công thức" if k == "ALL" else sub_rules[k]["name"],
            key="usr_gen_rule"
        )
    with c4:
        sub_forms = Script_Login.get_filtered_question_forms(subject=subject, concept_node=concept_node, formula_rule=formula_rule)
        question_form = st.selectbox(
            "4. Dạng câu hỏi",
            ["ALL"] + list(sub_forms.keys()),
            format_func=lambda k: "Tất cả dạng câu hỏi của phần này" if k == "ALL" else sub_forms[k],
            key="usr_gen_form"
        )

    c5, c6 = st.columns(2)
    with c5:
        mode = st.radio(
            "5. Chế độ chọn câu hỏi",
            ["ADAPTIVE_IRT", "CUSTOM_DIFFICULTY"],
            format_func=lambda x: "Thích ứng năng lực (IRT)" if x == "ADAPTIVE_IRT" else "Chọn độ khó cố định"
        )
    with c6:
        num_questions = st.slider("6. Số lượng câu hỏi", min_value=5, max_value=25, value=10, step=5)
        target_difficulty = "ADAPTIVE"
        if mode == "CUSTOM_DIFFICULTY":
            target_difficulty = st.selectbox("Mức độ khó", ["DE", "TRUNG_BINH", "KHA", "KHO"], format_func=lambda k: diff_names[k])

    if formula_rule != "ALL":
        r_meta = Script_Login.get_formula_rule_info(formula_rule)
        st.info(f"**Công thức ({r_meta['name']}):** {r_meta['latex_formula']}\n\n**Cách làm:** {r_meta['general_method']}")

    if st.button("Khởi tạo đề thi", type="primary", use_container_width=True):
        exam_pack = Script_User_TaoBaiLam.assemble_personalized_exam(
            username=username,
            subject=subject,
            concept_node=concept_node,
            formula_rule=formula_rule,
            question_form=question_form,
            mode=mode,
            target_difficulty=target_difficulty,
            num_questions=num_questions
        )
        st.session_state.active_exam = exam_pack
        st.session_state.exam_result = None

    exam = st.session_state.get("active_exam")
    if exam:
        sub_vi = "Toán học" if exam["subject"] == "MATH" else "Hóa học"
        st.markdown(
            f'<div class="kbs-box" style="margin-top:0.85rem;">'
            f'<span class="badge-blue">{exam["exam_id"]}</span> '
            f'<span class="badge-outline">Môn: {sub_vi}</span> '
            f'<span class="badge-outline">{len(exam["questions"])} câu</span> '
            f'<span class="badge-red">Định mức: {exam["total_expected_time"]} giây</span>'
            f'<div style="font-size:0.84rem; color:#475569; margin-top:0.45rem;">{exam["selection_rationale"]}</div>'
            f'</div>',
            unsafe_allow_html=True
        )
        if st.button("Bắt đầu làm bài ngay", type="primary", use_container_width=True):
            st.session_state.current_page = "USR_LAMBAI"
            st.rerun()

import streamlit as st
import Script_Engineer_QuanLyDeThi
import Script_Login

def render():
    diff_names = {"DE": "Dễ", "TRUNG_BINH": "Trung bình", "KHA": "Khá", "KHO": "Khó"}
    all_f_rules = Script_Login.get_all_formula_rules()

    tab_list, tab_add, tab_edit, tab_sympy = st.tabs([
        "Danh sách",
        "Thêm câu hỏi",
        "Sửa / Xóa",
        "Sinh tự động SymPy"
    ])

    with tab_list:
        c0, c1, c2 = st.columns([1, 1.5, 1.5])
        with c0:
            sub_f = st.selectbox(
                "Môn học",
                ["ALL", "MATH", "CHEM"],
                format_func=lambda s: "Tất cả" if s == "ALL" else ("Toán" if s == "MATH" else "Hóa"),
                key="flt_sub"
            )
        with c1:
            valid_nodes = Script_Login.get_filtered_concept_nodes(subject=sub_f)
            node_f = st.selectbox(
                "Chuyên đề",
                ["ALL"] + list(valid_nodes.keys()),
                format_func=lambda k: "Tất cả chuyên đề" if k == "ALL" else valid_nodes[k]["name"],
                key="flt_node"
            )
        with c2:
            valid_rules = Script_Login.get_filtered_formula_rules(subject=sub_f, concept_node=node_f)
            rule_f = st.selectbox(
                "Quy tắc công thức",
                ["ALL"] + list(valid_rules.keys()),
                format_func=lambda k: "Tất cả quy tắc" if k == "ALL" else valid_rules[k]["name"],
                key="flt_rule"
            )

        c3, c4, c5 = st.columns([1.6, 1, 1.4])
        with c3:
            valid_forms = Script_Login.get_filtered_question_forms(subject=sub_f, concept_node=node_f, formula_rule=rule_f)
            form_f = st.selectbox(
                "Dạng bài",
                ["ALL"] + list(valid_forms.keys()),
                format_func=lambda k: "Tất cả dạng bài" if k == "ALL" else valid_forms[k],
                key="flt_form"
            )
        with c4:
            diff_f = st.selectbox(
                "Độ khó",
                ["ALL", "DE", "TRUNG_BINH", "KHA", "KHO"],
                format_func=lambda k: "Tất cả" if k == "ALL" else diff_names[k],
                key="flt_diff"
            )
        with c5:
            kw = st.text_input("Từ khóa", placeholder="Q_MATH_001, tiếp tuyến...")

        questions = Script_Engineer_QuanLyDeThi.filter_questions(
            subject=sub_f, concept_node=node_f, formula_rule=rule_f, question_form=form_f, difficulty=diff_f, keyword=kw
        )
        st.caption(f"Tìm thấy {len(questions)} câu hỏi (hiển thị tối đa 30 câu):")

        for q in questions[:30]:
            b_cls = "badge-red" if q["difficulty"] in ["KHA", "KHO"] else "badge-blue"
            node_name = Script_Login.get_concept_name(q["concept_node"])
            f_info = Script_Login.get_formula_rule_info(q.get("formula_rule", "DRV_POW"))
            form_name = Script_Login.get_question_form_name(q.get("question_form", "FORM_EXPR"))

            st.markdown(
                f'<div class="kbs-box" style="padding:0.75rem 1rem; margin-bottom:0.4rem;">'
                f'<div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:6px;">'
                f'<div><span class="badge-blue">{q["id"]}</span>'
                f'<span class="badge-outline">{node_name}</span>'
                f'<span class="badge-outline">{f_info["name"]}</span>'
                f'<span class="badge-outline">{form_name}</span></div>'
                f'<div><span class="{b_cls}">{diff_names.get(q["difficulty"], q["difficulty"])}</span>'
                f'<span class="badge-outline">{q["expected_time"]}s</span></div>'
                f'</div></div>',
                unsafe_allow_html=True
            )
            st.markdown(f"**Đề:** {q['content']}")
            st.markdown(
                f"- **A.** {q['options']['A']}\n"
                f"- **B.** {q['options']['B']}\n"
                f"- **C.** {q['options']['C']}\n"
                f"- **D.** {q['options']['D']}"
            )
            st.markdown(f"**Cách làm:** {q.get('general_method', f_info['general_method'])}")
            st.markdown(f"**Đáp án `{q['answer']}`:** {q['explanation']}")
            st.markdown("<hr style='margin:0.75rem 0 1rem 0; border:none; border-top:1px solid #E2E8F0;'>", unsafe_allow_html=True)

    with tab_add:
        with st.expander("Công cụ chuyển nhanh biểu thức sang LaTeX", expanded=False):
            raw_math = st.text_input("Biểu thức Toán", value="(2*x + 1)/(x - 1)")
            math_latex = Script_Login.format_math_to_latex(raw_math)
            st.code(math_latex, language="latex")
            st.markdown(f"Xem trước Toán: {math_latex}")

            raw_chem = st.text_input("Phương trình Hóa", value="FeS2 + 8HNO3 -> Fe(NO3)3 + 2H2SO4 + 5NO + 2H2O")
            chem_latex = Script_Login.format_chem_to_latex(raw_chem)
            st.code(chem_latex, language="latex")
            st.markdown(f"Xem trước Hóa: {chem_latex}")

        a_sub = st.selectbox("Môn học", ["MATH", "CHEM"], format_func=lambda s: "Toán học" if s == "MATH" else "Hóa học", key="add_sub")
        a_nodes = Script_Login.get_filtered_concept_nodes(subject=a_sub)
        n_node = st.selectbox("Chuyên đề", list(a_nodes.keys()), format_func=lambda k: a_nodes[k]["name"], key="add_node")
        a_rules = Script_Login.get_filtered_formula_rules(subject=a_sub, concept_node=n_node)
        n_f_rule = st.selectbox("Quy tắc công thức", list(a_rules.keys()), format_func=lambda k: a_rules[k]["name"], key="add_rule")
        a_forms = Script_Login.get_filtered_question_forms(subject=a_sub, concept_node=n_node, formula_rule=n_f_rule)
        n_q_form = st.selectbox("Dạng câu hỏi", list(a_forms.keys()), format_func=lambda k: a_forms[k], key="add_form")

        sc1, sc2, sc3 = st.columns(3)
        with sc1:
            n_steps = st.number_input("Số bước giải (1-5)", 1, 5, 2)
        with sc2:
            n_time = st.number_input("Thời gian (giây)", 15, 300, 55)
        with sc3:
            n_ans = st.selectbox("Đáp án đúng", ["A", "B", "C", "D"])

        rule_meta = all_f_rules[n_f_rule]
        st.caption(f"Công thức chuẩn: {rule_meta['latex_formula']}")

        n_content = st.text_area("Nội dung đề (LaTeX trong $...$)", value="Cho hàm số $y = (x^2+2)(3x-1)$. Đạo hàm $y'$ của hàm số là:")
        oa = st.text_input("Phương án A", value="$y' = 9x^2 - 2x + 6$")
        ob = st.text_input("Phương án B", value="$y' = 6x$")
        oc = st.text_input("Phương án C", value="$y' = 3x^2 - 2x + 6$")
        od = st.text_input("Phương án D", value="$y' = 9x^2 + 2x - 6$")
        n_method = st.text_input("Cách làm tổng quát", value=rule_meta["general_method"])
        n_exp = st.text_input("Lời giải chi tiết", value="Áp dụng $(u \\cdot v)' = u'v + uv' = 2x(3x - 1) + (x^2 + 2)\\cdot 3 = 9x^2 - 2x + 6$.")

        if st.button("Lưu câu hỏi mới", type="primary", use_container_width=True):
            ok, msg, diff_res = Script_Engineer_QuanLyDeThi.add_manual_question({
                "subject": a_sub,
                "topic": a_nodes[n_node]["topic"],
                "concept_node": n_node,
                "formula_rule": n_f_rule,
                "question_form": n_q_form,
                "q_type": "THEORY" if n_steps == 1 else ("ALGORITHMIC" if n_steps == 2 else "APPLICATION"),
                "steps": n_steps,
                "expected_time": n_time,
                "content": n_content,
                "options": {"A": oa, "B": ob, "C": oc, "D": od},
                "answer": n_ans,
                "general_method": n_method,
                "explanation": n_exp
            })
            if ok:
                st.success(f"{msg} | Độ khó: {diff_res}")
            else:
                st.error(msg)

    with tab_edit:
        all_qs = Script_Engineer_QuanLyDeThi.load_knowledge_base()["questions"]
        if not all_qs:
            st.info("Ngân hàng câu hỏi trống.")
        else:
            sel_qid = st.selectbox(
                "Chọn câu hỏi cần Sửa hoặc Xóa",
                [q["id"] for q in all_qs],
                format_func=lambda qid: next(f"{q['id']} | {Script_Login.get_concept_name(q['concept_node'])} | {q['content'][:55]}..." for q in all_qs if q["id"] == qid)
            )
            cur_q = next(q for q in all_qs if q["id"] == sel_qid)
            q_sub = cur_q["subject"]

            e_nodes = Script_Login.get_filtered_concept_nodes(subject=q_sub)
            node_keys = list(e_nodes.keys())
            e_node = st.selectbox(
                "Chuyên đề",
                node_keys,
                index=node_keys.index(cur_q["concept_node"]) if cur_q["concept_node"] in node_keys else 0,
                format_func=lambda k: e_nodes[k]["name"],
                key="edit_q_node"
            )

            e_rules = Script_Login.get_filtered_formula_rules(subject=q_sub, concept_node=e_node)
            rule_keys = list(e_rules.keys())
            e_rule = st.selectbox(
                "Quy tắc công thức",
                rule_keys,
                index=rule_keys.index(cur_q.get("formula_rule")) if cur_q.get("formula_rule") in rule_keys else 0,
                format_func=lambda k: e_rules[k]["name"],
                key="edit_q_rule"
            )

            e_forms = Script_Login.get_filtered_question_forms(subject=q_sub, concept_node=e_node, formula_rule=e_rule)
            form_keys = list(e_forms.keys())
            e_form = st.selectbox(
                "Dạng câu hỏi",
                form_keys,
                index=form_keys.index(cur_q.get("question_form")) if cur_q.get("question_form") in form_keys else 0,
                format_func=lambda k: e_forms[k],
                key="edit_q_form"
            )

            ec1, ec2, ec3 = st.columns(3)
            diff_keys = ["DE", "TRUNG_BINH", "KHA", "KHO"]
            with ec1:
                e_diff = st.selectbox("Độ khó", diff_keys, index=diff_keys.index(cur_q["difficulty"]) if cur_q["difficulty"] in diff_keys else 1, format_func=lambda k: diff_names[k])
            with ec2:
                e_time = st.number_input("Thời gian (giây)", 15, 300, int(cur_q.get("expected_time", 50)), key="edit_q_time")
            with ec3:
                ans_keys = ["A", "B", "C", "D"]
                e_ans = st.selectbox("Đáp án đúng", ans_keys, index=ans_keys.index(cur_q["answer"]) if cur_q["answer"] in ans_keys else 0, key="edit_q_ans")

            e_content = st.text_area("Nội dung đề", value=cur_q["content"], key="edit_q_content")
            e_oa = st.text_input("Phương án A", value=cur_q["options"]["A"], key="edit_q_oa")
            e_ob = st.text_input("Phương án B", value=cur_q["options"]["B"], key="edit_q_ob")
            e_oc = st.text_input("Phương án C", value=cur_q["options"]["C"], key="edit_q_oc")
            e_od = st.text_input("Phương án D", value=cur_q["options"]["D"], key="edit_q_od")
            e_method = st.text_input("Cách làm tổng quát", value=cur_q.get("general_method", ""), key="edit_q_method")
            e_exp = st.text_input("Lời giải", value=cur_q.get("explanation", ""), key="edit_q_exp")

            bc1, bc2 = st.columns(2)
            with bc1:
                if st.button("Cập nhật câu hỏi", type="primary", use_container_width=True):
                    ok, msg = Script_Engineer_QuanLyDeThi.update_question(sel_qid, {
                        "concept_node": e_node,
                        "formula_rule": e_rule,
                        "question_form": e_form,
                        "difficulty": e_diff,
                        "expected_time": e_time,
                        "content": e_content,
                        "options": {"A": e_oa, "B": e_ob, "C": e_oc, "D": e_od},
                        "answer": e_ans,
                        "general_method": e_method,
                        "explanation": e_exp
                    })
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
            with bc2:
                if st.button("Xóa câu hỏi này", type="secondary", use_container_width=True):
                    ok, msg = Script_Engineer_QuanLyDeThi.delete_question(sel_qid)
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

    with tab_sympy:
        m_sub = st.selectbox("1. Môn học", ["MATH", "CHEM"], format_func=lambda s: "Toán học" if s == "MATH" else "Hóa học", key="m_sub")
        m_nodes = Script_Login.get_filtered_concept_nodes(subject=m_sub)
        m_node = st.selectbox("2. Chuyên đề", list(m_nodes.keys()), format_func=lambda k: m_nodes[k]["name"], key="m_node")
        m_rules = Script_Login.get_filtered_formula_rules(subject=m_sub, concept_node=m_node)
        m_f_rule = st.selectbox("3. Quy tắc công thức", list(m_rules.keys()), format_func=lambda k: m_rules[k]["name"], key="m_rule")
        m_forms = Script_Login.get_filtered_question_forms(subject=m_sub, concept_node=m_node, formula_rule=m_f_rule)
        m_form = st.selectbox("4. Dạng câu hỏi", list(m_forms.keys()), format_func=lambda k: m_forms[k], key="m_form")
        stem_labels = (
            [
                "Mẫu 1: Cho hàm số [loại] y = f(x) = ...",
                "Mẫu 2: Cho hàm số y = ...",
                "Mẫu 3: Xét hàm số f(x) = ...",
                "Mẫu 4: Cho đường cong (C): y = ..."
            ]
            if m_sub == "MATH"
            else [
                "Mẫu 1: Cho sơ đồ phản ứng ...",
                "Mẫu 2: Xét phương trình hóa học ...",
                "Mẫu 3: Cân bằng phương trình phản ứng ...",
                "Mẫu 4: Trong phòng thí nghiệm, xét phản ứng ..."
            ]
        )
        m_style = st.selectbox(
            "5. Mẫu câu dẫn (R_TRANS_STEM)",
            [0, 1, 2, 3],
            format_func=lambda idx: stem_labels[idx]
        )

        if st.button("Sinh câu hỏi bằng SymPy", type="primary", use_container_width=True):
            prev_q = st.session_state.get("last_ai_q", {})
            prev_content = prev_q.get("content", "") if prev_q else ""
            new_q = None
            for attempt in range(8):
                cand = Script_Engineer_QuanLyDeThi.generate_question_by_rule_and_sympy(
                    concept_node=m_node,
                    formula_rule=m_f_rule,
                    question_form=m_form,
                    target_difficulty="TRUNG_BINH",
                    stem_style_idx=m_style,
                    seed_offset=attempt * 19 + len(prev_content)
                )
                new_q = cand
                if cand["content"] != prev_content:
                    break
            st.session_state["last_ai_q"] = new_q

        gen_q = st.session_state.get("last_ai_q")
        if gen_q:
            st.markdown(
                f'<div class="kbs-box">'
                f'<span class="badge-blue">{Script_Login.get_concept_name(gen_q["concept_node"])}</span> '
                f'<span class="badge-outline">{Script_Login.get_formula_rule_info(gen_q["formula_rule"])["name"]}</span> '
                f'<span class="badge-red">{diff_names.get(gen_q["difficulty"], gen_q["difficulty"])}</span>'
                f'</div>',
                unsafe_allow_html=True
            )
            st.markdown(f"**Đề:** {gen_q['content']}")
            st.markdown(
                f"- **A.** {gen_q['options']['A']}\n"
                f"- **B.** {gen_q['options']['B']}\n"
                f"- **C.** {gen_q['options']['C']}\n"
                f"- **D.** {gen_q['options']['D']}"
            )
            st.markdown(f"**Cách làm:** {gen_q['general_method']}")
            st.markdown(f"**Lời giải (`{gen_q['answer']}`):** {gen_q['explanation']}")

            if st.button("Lưu câu vừa sinh vào Knowledge.txt", type="secondary", use_container_width=True):
                ok, msg = Script_Engineer_QuanLyDeThi.commit_generated_question(gen_q)
                if ok:
                    st.success(msg)

        st.markdown('<div class="section-heading">Mở rộng đủ 200 câu hỏi</div>', unsafe_allow_html=True)
        if st.button("Tự động sinh & nạp đủ 200 câu hỏi (100 Toán + 100 Hóa) vào Knowledge.txt", type="secondary", use_container_width=True):
            total_after = Script_Engineer_QuanLyDeThi.expand_knowledge_base_to_200()
            st.success(f"Đã nạp đủ {total_after} câu hỏi vào Knowledge.txt!")

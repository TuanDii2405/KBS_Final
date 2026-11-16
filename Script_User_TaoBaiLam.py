import math
import time
import Script_Login
import Script_Engineer_QuanLyDeThi

def _fisher_information(theta: float, a: float, b: float) -> float:
    p = 1.0 / (1.0 + math.exp(-a * (theta - b)))
    return (a ** 2) * p * (1.0 - p)

def assemble_personalized_exam(
    username: str,
    subject: str,
    concept_node: str = "ALL",
    formula_rule: str = "ALL",
    question_form: str = "ALL",
    mode: str = "ADAPTIVE_IRT",
    target_difficulty: str = "ADAPTIVE",
    num_questions: int = 10
) -> dict:
    acc_db = Script_Login.load_accounts_db()
    user = acc_db["users"].get(username, next(iter(acc_db["users"].values())))
    theta = float(user["theta_math"] if subject == "MATH" else user["theta_chem"])
    recent_ids = set(user.get("recent_questions", []))
    prereq_graph = Script_Login.get_prerequisite_graph()

    # Ràng buộc chặt chẽ: Đảm bảo concept_node, formula_rule, question_form thuộc đúng môn học
    valid_nodes = Script_Login.get_filtered_concept_nodes(subject=subject)
    if concept_node != "ALL" and concept_node not in valid_nodes:
        concept_node = "ALL"

    valid_rules = Script_Login.get_filtered_formula_rules(subject=subject, concept_node=concept_node)
    if formula_rule != "ALL" and formula_rule not in valid_rules:
        formula_rule = "ALL"

    valid_forms = Script_Login.get_filtered_question_forms(subject=subject, concept_node=concept_node, formula_rule=formula_rule)
    if question_form != "ALL" and question_form not in valid_forms:
        question_form = "ALL"

    pool = Script_Engineer_QuanLyDeThi.filter_questions(
        subject=subject,
        concept_node=concept_node,
        formula_rule=formula_rule,
        question_form=question_form
    )

    scored_candidates = []
    for q in pool:
        node = q["concept_node"]
        n_stat = user["node_stats"].get(node, {"correct": 0, "total": 0})
        mastery = (n_stat["correct"] / n_stat["total"]) if n_stat["total"] > 0 else 0.5

        weakness_boost = 1.0 - mastery
        for child_node, prereqs in prereq_graph.items():
            c_stat = user["node_stats"].get(child_node, {"correct": 0, "total": 0})
            if c_stat["total"] > 0 and (c_stat["correct"] / c_stat["total"]) < 0.45 and node in prereqs:
                weakness_boost += 0.35

        novelty = 0.0 if q["id"] in recent_ids else 1.0

        if mode == "ADAPTIVE_IRT":
            fisher = _fisher_information(theta, float(q.get("irt_a", 1.2)), float(q["irt_b"]))
            utility = 0.55 * fisher + 0.30 * weakness_boost + 0.15 * novelty
        else:
            diff_match = 1.5 if q["difficulty"] == target_difficulty else 0.2
            utility = diff_match + 0.25 * weakness_boost + 0.15 * novelty

        scored_candidates.append((utility, q))

    scored_candidates.sort(key=lambda x: x[0], reverse=True)
    selected = [item[1] for item in scored_candidates[:num_questions]]

    node_keys = list(valid_nodes.keys())
    while len(selected) < num_questions:
        idx = len(selected) + 1
        fb_node = concept_node if concept_node != "ALL" else node_keys[idx % len(node_keys)]
        fb_rules_dict = Script_Login.get_filtered_formula_rules(subject=subject, concept_node=fb_node)
        fb_rule_keys = list(fb_rules_dict.keys())
        fb_rule = formula_rule if (formula_rule != "ALL" and formula_rule in fb_rules_dict) else fb_rule_keys[idx % len(fb_rule_keys)]

        fb_forms_dict = Script_Login.get_filtered_question_forms(subject=subject, concept_node=fb_node, formula_rule=fb_rule)
        fb_form_keys = list(fb_forms_dict.keys())
        fb_form = question_form if (question_form != "ALL" and question_form in fb_forms_dict) else fb_form_keys[idx % len(fb_form_keys)]

        dyn_q = Script_Engineer_QuanLyDeThi.generate_question_by_rule_and_sympy(
            fb_node, fb_rule, fb_form, stem_style_idx=idx % 4, seed_offset=idx + int(time.time()) % 50
        )
        dyn_q["id"] = f"Q_DYN_{idx:02d}"
        selected.append(dyn_q)

    total_time = sum(int(q["expected_time"]) for q in selected)
    score_100 = Script_Login.theta_to_score100(theta)

    rationale = (
        f"Tối ưu hàm thông tin Fisher theo năng lực ({score_100}/100), ưu tiên quy tắc đang yếu."
        if mode == "ADAPTIVE_IRT"
        else "Rút trích theo đúng chuyên đề, quy tắc công thức và độ khó cố định đã chọn."
    )

    return {
        "exam_id": f"DE_{subject}_{int(time.time()) % 100000}",
        "subject": subject,
        "concept_node": concept_node,
        "formula_rule": formula_rule,
        "question_form": question_form,
        "mode": mode,
        "questions": selected,
        "total_expected_time": total_time,
        "student_theta": round(theta, 2),
        "student_score_100": score_100,
        "selection_rationale": rationale
    }

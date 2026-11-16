import datetime
import math
import Script_Login
import Script_Engineer_QuanLyDeThi

def grade_and_update_knowledge_state(
    username: str,
    exam: dict,
    user_answers: dict,
    total_duration: int,
    question_times: dict = None
) -> dict:
    acc_db = Script_Login.load_accounts_db()
    his_db = Script_Login.load_history_db()
    kb = Script_Engineer_QuanLyDeThi.load_knowledge_base()
    user = acc_db["users"].get(username, next(iter(acc_db["users"].values())))
    prereq_graph = Script_Login.get_prerequisite_graph()

    subject = exam["subject"]
    theta_key = "theta_math" if subject == "MATH" else "theta_chem"
    theta_before = float(user.get(theta_key, 0.0))
    theta_current = theta_before

    questions = exam["questions"]
    expected_total = max(1, int(exam["total_expected_time"]))
    q_times_map = question_times or {}

    correct_count = 0
    failed_nodes = set()
    failed_rules = set()
    reviews = []
    kb_map = {q["id"]: q for q in kb["questions"]}
    diff_vi_map = {"DE": "Dễ", "TRUNG_BINH": "Trung bình", "KHA": "Khá", "KHO": "Khó"}
    fallback_q_time = max(1, round(total_duration / max(1, len(questions))))

    for q in questions:
        qid = q["id"]
        u_choice = user_answers.get(qid)
        is_correct = (u_choice == q["answer"])
        f_rule = q.get("formula_rule", "DRV_POW" if subject == "MATH" else "BAL_ATOM")
        f_info = Script_Login.get_formula_rule_info(f_rule)

        q_exp_time = max(1, int(q.get("expected_time", 45)))
        q_spent = max(1, int(round(q_times_map.get(qid, fallback_q_time))))
        time_factor_q = q_spent / q_exp_time

        if is_correct:
            correct_count += 1
        else:
            failed_nodes.add(q["concept_node"])
            failed_rules.add(f_info["name"])

        a = float(q.get("irt_a", 1.25))
        b = float(q["irt_b"])
        p_theta = 1.0 / (1.0 + math.exp(-a * (theta_current - b)))

        if is_correct:
            speed_weight = 1.0 if time_factor_q <= 1.25 else (0.55 if time_factor_q >= 1.75 else 0.8)
            theta_current += 0.28 * speed_weight * a * (1.0 - p_theta)
        else:
            guess_penalty = 1.25 if time_factor_q < 0.35 else 1.0
            theta_current -= 0.28 * guess_penalty * a * p_theta

        node = q["concept_node"]
        user["node_stats"].setdefault(node, {"correct": 0, "total": 0})
        user["node_stats"][node]["total"] += 1
        if is_correct:
            user["node_stats"][node]["correct"] += 1

        if qid in kb_map:
            kq = kb_map[qid]
            old_att = int(kq.get("attempts", 0))
            old_cr = float(kq.get("correct_rate", 0.5))
            old_avg_t = float(kq.get("avg_time", kq["expected_time"]))

            new_att = old_att + 1
            kq["attempts"] = new_att
            kq["correct_rate"] = round(((old_cr * old_att) + (1.0 if is_correct else 0.0)) / new_att, 3)
            kq["avg_time"] = round(((old_avg_t * old_att) + q_spent) / new_att, 1)

        reviews.append({
            "id": qid,
            "concept_node": node,
            "formula_rule": f_rule,
            "question_form": q.get("question_form", "FORM_EXPR"),
            "difficulty": diff_vi_map.get(q["difficulty"], q["difficulty"]),
            "irt_b": b,
            "time_spent_sec": q_spent,
            "expected_time": q_exp_time,
            "content": q["content"],
            "user_choice": u_choice,
            "correct_answer": q["answer"],
            "is_correct": is_correct,
            "general_method": q.get("general_method", f_info["general_method"]),
            "explanation": q["explanation"]
        })

    theta_after = round(max(-3.0, min(3.0, theta_current)), 2)
    theta_delta = round(theta_after - theta_before, 2)
    user[theta_key] = theta_after

    recent = user.get("recent_questions", [])
    recent.extend([q["id"] for q in questions if not q["id"].startswith("Q_DYN")])
    user["recent_questions"] = recent[-25:]

    prereq_names = []
    for f_node in failed_nodes:
        for p_node in prereq_graph.get(f_node, []):
            p_name = Script_Login.get_concept_name(p_node)
            if p_name not in prereq_names:
                prereq_names.append(p_name)

    score_10 = round((correct_count / max(1, len(questions))) * 10.0, 2)
    if failed_rules:
        conclusion = (
            f"Đạt {score_10}/10 điểm. Cần lưu ý quy tắc: {', '.join(failed_rules)}. "
            f"Nên ôn lại: {', '.join(prereq_names) if prereq_names else 'Lý thuyết cốt lõi chuyên đề hiện tại'}."
        )
    else:
        conclusion = (
            f"Đạt {score_10}/10 điểm! Nắm vững tất cả quy tắc công thức trong đề. "
            f"Điểm năng lực: {Script_Login.theta_to_score100(theta_after)}/100."
        )

    submission_record = {
        "submission_id": f"BAI_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "username": username,
        "full_name": user["full_name"],
        "subject": subject,
        "score_10": score_10,
        "correct_count": correct_count,
        "total_questions": len(questions),
        "duration_sec": total_duration,
        "expected_sec": expected_total,
        "theta_before": round(theta_before, 2),
        "theta_after": theta_after,
        "theta_delta": theta_delta,
        "competency_level": Script_Login.classify_theta(theta_after).split(" - ")[0],
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "expert_conclusion": conclusion,
        "weak_nodes": list(failed_nodes),
        "question_reviews": reviews
    }

    his_db["submissions"].append(submission_record)
    Script_Login.save_accounts_db(acc_db)
    Script_Login.save_history_db(his_db)
    Script_Engineer_QuanLyDeThi.save_knowledge_base(kb)

    return submission_record

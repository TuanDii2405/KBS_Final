import Script_Login

def get_student_dashboard(username: str) -> dict:
    acc_db = Script_Login.load_accounts_db()
    his_db = Script_Login.load_history_db()
    user = acc_db["users"].get(username, next(iter(acc_db["users"].values())))
    subs = [s for s in his_db["submissions"] if s["username"] == username]

    theta_m = float(user.get("theta_math", 0.0))
    theta_c = float(user.get("theta_chem", 0.0))

    avg_acc = 0
    if subs:
        tot_c = sum(s["correct_count"] for s in subs)
        tot_q = max(1, sum(s["total_questions"] for s in subs))
        avg_acc = round((tot_c / tot_q) * 100, 1)

    concept_mastery = []
    weak_nodes = []
    all_nodes = Script_Login.get_all_concept_nodes()
    prereq_graph = Script_Login.get_prerequisite_graph()

    for node_code, meta in all_nodes.items():
        stat = user["node_stats"].get(node_code, {"correct": 0, "total": 0})
        pct = round((stat["correct"] / stat["total"]) * 100) if stat["total"] > 0 else 50
        concept_mastery.append({
            "node": node_code,
            "name": meta["name"],
            "subject_vi": "Toán" if meta["subject"] == "MATH" else "Hóa",
            "correct": stat["correct"],
            "total": stat["total"],
            "mastery_pct": pct
        })
        if stat["total"] > 0 and pct < 50:
            weak_nodes.append(node_code)

    recommendations = []
    for w_node in weak_nodes:
        prereqs = prereq_graph.get(w_node, [])
        w_name = Script_Login.get_concept_name(w_node)
        if prereqs:
            p_name = Script_Login.get_concept_name(prereqs[0])
            recommendations.append({
                "priority": "Cao",
                "title": f"Ôn lại chuyên đề nền tảng: {p_name}",
                "reason": f"Tỷ lệ đúng dưới 50% ở '{w_name}'. Nên củng cố '{p_name}' trước."
            })
        else:
            recommendations.append({
                "priority": "Cao",
                "title": f"Củng cố chuyên đề: {w_name}",
                "reason": f"Luyện thêm các câu cơ bản thuộc '{w_name}' để đạt trên 65%."
            })

    if not recommendations:
        rec_diff = Script_Login.theta_to_recommended_difficulty((theta_m + theta_c) / 2)
        diff_vi = {"DE": "Cơ bản", "TRUNG_BINH": "Trung bình", "KHA": "Khá", "KHO": "Nâng cao"}[rec_diff]
        recommendations.append({
            "priority": "Khuyên dùng",
            "title": f"Luyện đề thích ứng mức {diff_vi}",
            "reason": f"Đã nắm vững nền tảng 6 chuyên đề. Luyện mức {diff_vi} để nâng điểm năng lực."
        })

    return {
        "score_math": Script_Login.theta_to_score100(theta_m),
        "level_math": Script_Login.classify_theta(theta_m),
        "score_chem": Script_Login.theta_to_score100(theta_c),
        "level_chem": Script_Login.classify_theta(theta_c),
        "completed_exams": len(subs),
        "avg_accuracy": avg_acc,
        "recommended_difficulty": Script_Login.theta_to_recommended_difficulty((theta_m + theta_c) / 2),
        "recommendations": recommendations,
        "concept_mastery": concept_mastery
    }

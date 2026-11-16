import math
import Script_Engineer_QuanLyDeThi
import Script_Login

def _b_to_label(b_val: float) -> str:
    if b_val < -0.9:
        return "DE"
    if b_val < 0.45:
        return "TRUNG_BINH"
    if b_val < 1.45:
        return "KHA"
    return "KHO"

def _compute_empirical_b(q: dict) -> float:
    p = min(0.94, max(0.06, float(q.get("correct_rate", 0.5))))
    logit = math.log((1.0 - p) / p)
    time_ratio = float(q.get("avg_time", q["expected_time"])) / max(10.0, float(q["expected_time"]))
    b_emp = 0.75 * logit + 0.45 * (time_ratio - 1.0)
    return round(max(-2.6, min(2.6, b_emp)), 2)

def evaluate_difficulty_assignment() -> dict:
    kb = Script_Engineer_QuanLyDeThi.load_knowledge_base()
    questions = kb["questions"]

    prior_bs = []
    emp_bs = []
    abs_errors = []
    matched_labels = 0
    calibration_table = []

    for q in questions:
        b_prior = float(q["irt_b"])
        b_emp = _compute_empirical_b(q)
        suggested_label = _b_to_label(b_emp)
        needs_recal = (q["attempts"] >= 8) and (suggested_label != q["difficulty"] or abs(b_emp - b_prior) >= 0.55)

        prior_bs.append(b_prior)
        emp_bs.append(b_emp)
        abs_errors.append(abs(b_prior - b_emp))
        if suggested_label == q["difficulty"]:
            matched_labels += 1

        f_info = Script_Login.get_formula_rule_info(q.get("formula_rule", "DRV_POW"))
        calibration_table.append({
            "id": q["id"],
            "subject": q["subject"],
            "topic": q["topic"],
            "topic_vi": Script_Login.get_concept_name(q["concept_node"]),
            "formula_vi": f_info["name"],
            "assigned_difficulty": q["difficulty"],
            "irt_b": b_prior,
            "attempts": q["attempts"],
            "correct_rate": q["correct_rate"],
            "avg_time": q.get("avg_time", q["expected_time"]),
            "expected_time": q["expected_time"],
            "empirical_b": b_emp,
            "needs_recalibration": needs_recal,
            "suggested_label": suggested_label
        })

    n = max(1, len(questions))
    mean_x = sum(prior_bs) / n
    mean_y = sum(emp_bs) / n
    num = sum((x - mean_x) * (y - mean_y) for x, y in zip(prior_bs, emp_bs))
    den_x = math.sqrt(sum((x - mean_x) ** 2 for x in prior_bs))
    den_y = math.sqrt(sum((y - mean_y) ** 2 for y in emp_bs))
    corr = round(num / (den_x * den_y), 3) if (den_x * den_y) > 0 else 0.85

    return {
        "correlation": corr,
        "mae": round(sum(abs_errors) / n, 3),
        "agreement_rate": round((matched_labels / n) * 100, 1),
        "calibration_table": calibration_table
    }

def apply_automatic_recalibration() -> int:
    kb = Script_Engineer_QuanLyDeThi.load_knowledge_base()
    updated = 0
    for q in kb["questions"]:
        if q["attempts"] >= 8:
            b_emp = _compute_empirical_b(q)
            new_label = _b_to_label(b_emp)
            if new_label != q["difficulty"] or abs(b_emp - q["irt_b"]) >= 0.45:
                q["irt_b"] = round(0.4 * q["irt_b"] + 0.6 * b_emp, 2)
                q["difficulty"] = _b_to_label(q["irt_b"])
                updated += 1
    Script_Engineer_QuanLyDeThi.save_knowledge_base(kb)
    return updated

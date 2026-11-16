import Script_Login
import Script_Engineer_QuanLyDeThi

def get_dashboard_overview() -> dict:
    kb = Script_Engineer_QuanLyDeThi.load_knowledge_base()
    acc_db = Script_Login.load_accounts_db()
    his_db = Script_Login.load_history_db()
    rules_db = Script_Login.load_rules_db()

    questions = kb["questions"]
    students = [u for u in acc_db["users"].values() if u["role"] == "student"]
    submissions = his_db["submissions"]

    math_count = sum(1 for q in questions if q["subject"] == "MATH")
    chem_count = sum(1 for q in questions if q["subject"] == "CHEM")

    avg_duration = 52
    if submissions:
        total_sec = sum(s["duration_sec"] for s in submissions)
        total_q = max(1, sum(s["total_questions"] for s in submissions))
        avg_duration = round(total_sec / total_q, 1)

    drift_alerts = 0
    for q in questions:
        if q["attempts"] >= 8:
            if (q["correct_rate"] <= 0.30 and q["difficulty"] != "KHO") or (q["correct_rate"] >= 0.85 and q["difficulty"] != "DE"):
                drift_alerts += 1

    topic_distribution = []
    for node_code, meta in Script_Login.get_all_concept_nodes().items():
        t_qs = [q for q in questions if q.get("concept_node") == node_code]
        topic_distribution.append({
            "code": node_code,
            "name": meta["name"],
            "subject": "Toán" if meta["subject"] == "MATH" else "Hóa",
            "de": sum(1 for x in t_qs if x["difficulty"] == "DE"),
            "tb": sum(1 for x in t_qs if x["difficulty"] == "TRUNG_BINH"),
            "kha": sum(1 for x in t_qs if x["difficulty"] == "KHA"),
            "kho": sum(1 for x in t_qs if x["difficulty"] == "KHO"),
            "total": len(t_qs)
        })

    return {
        "total_questions": len(questions),
        "math_count": math_count,
        "chem_count": chem_count,
        "total_students": len(students),
        "total_submissions": len(submissions),
        "avg_duration": avg_duration,
        "drift_alerts": drift_alerts,
        "topic_distribution": topic_distribution,
        "active_rules": rules_db.get("rules", [])
    }

def add_inference_rule(rule_id: str, name: str, priority: str, condition_vi: str, action_vi: str):
    if not rule_id or not name or not condition_vi or not action_vi:
        return False, "Vui lòng nhập đầy đủ mã luật, tên luật, điều kiện và hành động."
    db = Script_Login.load_rules_db()
    rules = db.get("rules", [])
    if any(r["id"] == rule_id for r in rules):
        return False, f"Mã luật '{rule_id}' đã tồn tại."
    rules.append({
        "id": rule_id.strip(),
        "name": name.strip(),
        "priority": priority,
        "condition_vi": condition_vi.strip(),
        "action_vi": action_vi.strip()
    })
    db["rules"] = rules
    Script_Login.save_rules_db(db)
    return True, f"Đã thêm luật '{rule_id}' vào LuatSuyDien.txt."

def update_inference_rule(rule_id: str, name: str, priority: str, condition_vi: str, action_vi: str):
    db = Script_Login.load_rules_db()
    for r in db.get("rules", []):
        if r["id"] == rule_id:
            r["name"] = name.strip()
            r["priority"] = priority
            r["condition_vi"] = condition_vi.strip()
            r["action_vi"] = action_vi.strip()
            Script_Login.save_rules_db(db)
            return True, f"Đã cập nhật luật '{rule_id}'."
    return False, f"Không tìm thấy luật '{rule_id}'."

def delete_inference_rule(rule_id: str):
    db = Script_Login.load_rules_db()
    before = len(db.get("rules", []))
    db["rules"] = [r for r in db.get("rules", []) if r["id"] != rule_id]
    if len(db["rules"]) < before:
        Script_Login.save_rules_db(db)
        return True, f"Đã xóa luật '{rule_id}' khỏi LuatSuyDien.txt."
    return False, f"Không tìm thấy luật '{rule_id}'."

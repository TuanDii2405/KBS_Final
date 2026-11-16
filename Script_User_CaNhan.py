import Script_Login

def get_personal_competency_report(username: str) -> dict:
    acc_db = Script_Login.load_accounts_db()
    his_db = Script_Login.load_history_db()
    user = acc_db["users"].get(username, next(iter(acc_db["users"].values())))
    history = [s for s in reversed(his_db.get("submissions", [])) if s["username"] == username]

    node_breakdown = []
    for code, meta in Script_Login.get_all_concept_nodes().items():
        stat = user["node_stats"].get(code, {"correct": 0, "total": 0})
        total = stat["total"]
        correct = stat["correct"]
        acc = round((correct / total) * 100) if total > 0 else 0
        if total == 0:
            status = "Chưa làm"
        elif acc < 50:
            status = "Cần ôn lại"
        elif acc < 80:
            status = "Đạt"
        else:
            status = "Thành thạo"

        node_breakdown.append({
            "code": code,
            "name": meta["name"],
            "subject_vi": "Toán" if meta["subject"] == "MATH" else "Hóa",
            "correct": correct,
            "total": total,
            "accuracy": acc,
            "status": status
        })

    return {
        "username": username,
        "full_name": user["full_name"],
        "node_breakdown": node_breakdown,
        "history": history
    }

def update_own_account(username: str, full_name: str, new_password: str = ""):
    db = Script_Login.load_accounts_db()
    if username not in db["users"]:
        return False, "Không tìm thấy tài khoản."
    if full_name and full_name.strip():
        db["users"][username]["full_name"] = full_name.strip()
    if new_password and new_password.strip():
        db["users"][username]["password"] = new_password.strip()
    Script_Login.save_accounts_db(db)
    return True, "Đã cập nhật thông tin cá nhân."

def delete_own_submission(username: str, submission_id: str):
    his_db = Script_Login.load_history_db()
    before = len(his_db.get("submissions", []))
    his_db["submissions"] = [
        s for s in his_db.get("submissions", [])
        if not (s["submission_id"] == submission_id and s["username"] == username)
    ]
    if len(his_db["submissions"]) < before:
        Script_Login.save_history_db(his_db)
        return True, f"Đã xóa bài thi {submission_id}."
    return False, "Không tìm thấy bài thi cần xóa."

import Script_Login

def get_all_student_profiles() -> list:
    acc_db = Script_Login.load_accounts_db()
    his_db = Script_Login.load_history_db()
    submissions = his_db.get("submissions", [])
    profiles = []

    for username, u in acc_db["users"].items():
        if u["role"] != "student":
            continue
        user_subs = [s for s in submissions if s["username"] == username]
        weakest_node = "Nắm vững đều 6 chuyên đề"
        lowest_acc = 1.01
        for node_id, stats in u.get("node_stats", {}).items():
            if stats["total"] > 0:
                acc = stats["correct"] / stats["total"]
                if acc < lowest_acc and acc < 0.65:
                    lowest_acc = acc
                    weakest_node = f"{Script_Login.get_concept_name(node_id)} ({int(acc*100)}%)"

        t_math = u.get("theta_math", 0.0)
        t_chem = u.get("theta_chem", 0.0)
        profiles.append({
            "username": username,
            "full_name": u["full_name"],
            "password": u.get("password", "123456"),
            "score_math": Script_Login.theta_to_score100(t_math),
            "level_math": Script_Login.classify_theta(t_math).split(" - ")[0],
            "score_chem": Script_Login.theta_to_score100(t_chem),
            "level_chem": Script_Login.classify_theta(t_chem).split(" - ")[0],
            "exams_taken": len(user_subs),
            "weakest_topic": weakest_node
        })
    return profiles

def create_student_account(username: str, full_name: str, password: str, score_math: int = 50, score_chem: int = 50):
    return Script_Login.register_user(username.strip(), password.strip(), full_name.strip(), score_math, score_chem)

def update_student_profile(username: str, full_name: str, password: str, score_math: int, score_chem: int, reset_stats: bool = False):
    db = Script_Login.load_accounts_db()
    if username not in db["users"]:
        return False, f"Không tìm thấy học viên {username}."
    u = db["users"][username]
    if full_name and full_name.strip():
        u["full_name"] = full_name.strip()
    if password and password.strip():
        u["password"] = password.strip()
    u["theta_math"] = Script_Login.score100_to_theta(score_math)
    u["theta_chem"] = Script_Login.score100_to_theta(score_chem)
    if reset_stats:
        u["node_stats"] = {node: {"correct": 0, "total": 0} for node in Script_Login.get_all_concept_nodes()}
        u["recent_questions"] = []
    Script_Login.save_accounts_db(db)
    return True, f"Đã cập nhật hồ sơ học viên {username}."

def update_student_score(username: str, score_math: int, score_chem: int):
    db = Script_Login.load_accounts_db()
    if username not in db["users"]:
        return False, f"Không tìm thấy học viên {username}."
    db["users"][username]["theta_math"] = Script_Login.score100_to_theta(score_math)
    db["users"][username]["theta_chem"] = Script_Login.score100_to_theta(score_chem)
    Script_Login.save_accounts_db(db)
    return True, f"Đã cập nhật điểm năng lực của {username}: Toán = {score_math}/100, Hóa = {score_chem}/100."

def delete_student_account(username: str):
    if username == "engineer":
        return False, "Không thể xóa tài khoản quản trị viên."
    db = Script_Login.load_accounts_db()
    if username in db["users"]:
        del db["users"][username]
        Script_Login.save_accounts_db(db)
        return True, f"Đã xóa tài khoản học viên '{username}' khỏi TaiKhoan.txt."
    return False, f"Không tìm thấy học viên '{username}'."

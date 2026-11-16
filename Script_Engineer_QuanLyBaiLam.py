import Script_Login

def get_all_submissions() -> list:
    his_db = Script_Login.load_history_db()
    acc_db = Script_Login.load_accounts_db()
    users = acc_db.get("users", {})
    result = []
    for s in reversed(his_db.get("submissions", [])):
        item = s.copy()
        if "full_name" not in item:
            item["full_name"] = users.get(item["username"], {}).get("full_name", item["username"])
        result.append(item)
    return result

def filter_submissions(submissions: list, sub_filter: str = "ALL", user_search: str = "") -> list:
    kw = user_search.strip().lower()
    out = []
    for s in submissions:
        if sub_filter != "ALL" and s["subject"] != sub_filter:
            continue
        if kw and (kw not in s["username"].lower() and kw not in s.get("full_name", "").lower()):
            continue
        out.append(s)
    return out

def get_submission_detail(submission_id: str):
    for s in get_all_submissions():
        if s["submission_id"] == submission_id:
            return s
    return None

def update_submission_conclusion(submission_id: str, new_conclusion: str, new_score: float = None):
    his_db = Script_Login.load_history_db()
    for s in his_db.get("submissions", []):
        if s["submission_id"] == submission_id:
            s["expert_conclusion"] = new_conclusion.strip()
            if new_score is not None:
                s["score_10"] = round(float(new_score), 2)
            Script_Login.save_history_db(his_db)
            return True, f"Đã cập nhật bài làm {submission_id}."
    return False, f"Không tìm thấy bài làm {submission_id}."

def delete_submission(submission_id: str):
    his_db = Script_Login.load_history_db()
    before = len(his_db.get("submissions", []))
    his_db["submissions"] = [s for s in his_db.get("submissions", []) if s["submission_id"] != submission_id]
    if len(his_db["submissions"]) < before:
        Script_Login.save_history_db(his_db)
        return True, f"Đã xóa bài làm {submission_id} khỏi LichSuBaiLam.txt."
    return False, f"Không tìm thấy bài làm {submission_id}."

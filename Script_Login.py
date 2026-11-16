import json
import os
import re
import sympy as sp

ACCOUNT_FILE = "TaiKhoan.txt"
HISTORY_FILE = "LichSuBaiLam.txt"
RULES_FILE = "LuatSuyDien.txt"

x_sym = sp.Symbol("x", real=True)
_RULES_CACHE = None

def format_math_to_latex(expr_str: str) -> str:
    if not expr_str or not expr_str.strip():
        return ""
    cleaned = expr_str.strip()
    if cleaned.startswith("$") and cleaned.endswith("$"):
        return cleaned
    try:
        normalized = cleaned.replace("^", "**")
        expr = sp.sympify(normalized, locals={"x": x_sym, "e": sp.E, "pi": sp.pi})
        return f"${sp.latex(expr)}$"
    except Exception:
        return f"${cleaned}$"

def format_chem_to_latex(chem_str: str) -> str:
    if not chem_str or not chem_str.strip():
        return ""
    s = chem_str.strip()
    if s.startswith("$") and s.endswith("$"):
        return s
    s = s.replace("->", " \\rightarrow ")
    s = re.sub(r"([A-Za-z\)])(\d+)", r"\1_\2", s)
    return f"${s}$"

def render_html_table(headers: list, rows: list) -> str:
    th_html = "".join(f"<th>{h}</th>" for h in headers)
    tr_list = []
    for r in rows:
        td_html = "".join(f"<td>{cell}</td>" for cell in r)
        tr_list.append(f"<tr>{td_html}</tr>")
    tbody_html = "".join(tr_list)
    return f'<table class="clean-table"><thead><tr>{th_html}</tr></thead><tbody>{tbody_html}</tbody></table>'

def load_rules_db() -> dict:
    """Đọc toàn bộ tri thức Ontology, Quy tắc công thức & Tập luật trực tiếp từ LuatSuyDien.txt."""
    global _RULES_CACHE
    if os.path.exists(RULES_FILE):
        try:
            with open(RULES_FILE, "r", encoding="utf-8") as f:
                _RULES_CACHE = json.load(f)
                return _RULES_CACHE
        except Exception:
            pass
    return _RULES_CACHE or {
        "concept_nodes": {},
        "formula_rules": {},
        "question_forms": {},
        "prerequisite_graph": {},
        "rules": []
    }

def save_rules_db(data: dict):
    global _RULES_CACHE
    _RULES_CACHE = data
    with open(RULES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_all_concept_nodes() -> dict:
    return load_rules_db().get("concept_nodes", {})

def get_all_formula_rules() -> dict:
    return load_rules_db().get("formula_rules", {})

def get_all_question_forms() -> dict:
    raw = load_rules_db().get("question_forms", {})
    return {k: (v["name"] if isinstance(v, dict) else str(v)) for k, v in raw.items()}

def get_question_forms_meta() -> dict:
    raw = load_rules_db().get("question_forms", {})
    return {
        k: (v if isinstance(v, dict) else {"name": str(v), "subject": "CHEM" if "CHEM" in k else "MATH", "concept_nodes": []})
        for k, v in raw.items()
    }

def get_filtered_concept_nodes(subject: str = "ALL") -> dict:
    nodes = get_all_concept_nodes()
    if subject == "ALL":
        return nodes
    return {k: v for k, v in nodes.items() if v.get("subject") == subject}

def get_filtered_formula_rules(subject: str = "ALL", concept_node: str = "ALL") -> dict:
    rules = get_all_formula_rules()
    nodes = get_all_concept_nodes()
    out = {}
    for rk, rv in rules.items():
        r_node = rv.get("concept_node")
        r_sub = rv.get("subject") or nodes.get(r_node, {}).get("subject", "MATH")
        if subject != "ALL" and r_sub != subject:
            continue
        if concept_node != "ALL" and r_node != concept_node:
            continue
        out[rk] = rv
    return out

def get_filtered_question_forms(subject: str = "ALL", concept_node: str = "ALL", formula_rule: str = "ALL") -> dict:
    forms_meta = get_question_forms_meta()
    rules = get_all_formula_rules()
    nodes = get_all_concept_nodes()

    inferred_sub = subject
    if inferred_sub == "ALL" and concept_node != "ALL":
        inferred_sub = nodes.get(concept_node, {}).get("subject", "ALL")
    if inferred_sub == "ALL" and formula_rule != "ALL":
        r_node = rules.get(formula_rule, {}).get("concept_node")
        inferred_sub = nodes.get(r_node, {}).get("subject", "ALL")

    allowed_by_rule = None
    if formula_rule != "ALL" and formula_rule in rules:
        allowed_by_rule = set(rules[formula_rule].get("allowed_forms", []))

    out = {}
    for fk, fmeta in forms_meta.items():
        if inferred_sub != "ALL" and fmeta.get("subject") != inferred_sub:
            continue
        if concept_node != "ALL" and fmeta.get("concept_nodes") and concept_node not in fmeta["concept_nodes"]:
            continue
        if allowed_by_rule is not None and fk not in allowed_by_rule:
            continue
        out[fk] = fmeta["name"]

    if not out:
        for fk, fmeta in forms_meta.items():
            if inferred_sub == "ALL" or fmeta.get("subject") == inferred_sub:
                out[fk] = fmeta["name"]
    return out

def get_prerequisite_graph() -> dict:
    return load_rules_db().get("prerequisite_graph", {})

def get_concept_name(node_code: str) -> str:
    return get_all_concept_nodes().get(node_code, {}).get("name", node_code)

def get_formula_rule_info(rule_code: str) -> dict:
    return get_all_formula_rules().get(rule_code, {
        "name": rule_code,
        "concept_node": "MATH_DERIV_01",
        "latex_formula": "",
        "general_method": "Áp dụng quy tắc chuẩn của chuyên đề."
    })

def get_question_form_name(form_code: str) -> str:
    return get_all_question_forms().get(form_code, form_code)

def theta_to_score100(theta: float) -> int:
    val = round(((float(theta) + 3.0) / 6.0) * 100)
    return max(5, min(100, val))

def score100_to_theta(score100: float) -> float:
    theta = ((float(score100) / 100.0) * 6.0) - 3.0
    return round(max(-3.0, min(3.0, theta)), 2)

def classify_theta(theta: float) -> str:
    score = theta_to_score100(theta)
    if score < 35:
        return "Cần củng cố nền tảng"
    if score < 58:
        return "Trung bình - Đạt chuẩn cơ bản"
    if score < 78:
        return "Khá - Vận dụng tốt"
    return "Giỏi - Nắm vững chuyên đề"

def theta_to_recommended_difficulty(theta: float) -> str:
    if theta < -0.8:
        return "DE"
    if theta < 0.4:
        return "TRUNG_BINH"
    if theta < 1.3:
        return "KHA"
    return "KHO"

def _default_node_stats():
    return {node: {"correct": 0, "total": 0} for node in get_all_concept_nodes()}

def load_accounts_db() -> dict:
    load_rules_db()
    if not os.path.exists(ACCOUNT_FILE):
        data = {"users": {}}
        save_accounts_db(data)
        return data
    try:
        with open(ACCOUNT_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            for u in data.get("users", {}).values():
                u.setdefault("node_stats", _default_node_stats())
                for n in get_all_concept_nodes():
                    u["node_stats"].setdefault(n, {"correct": 0, "total": 0})
            return data
    except Exception:
        return {"users": {}}

def save_accounts_db(data: dict):
    clean_data = {"users": data.get("users", {})}
    with open(ACCOUNT_FILE, "w", encoding="utf-8") as f:
        json.dump(clean_data, f, ensure_ascii=False, indent=2)

def load_history_db() -> dict:
    if not os.path.exists(HISTORY_FILE):
        h_data = {"submissions": []}
        save_history_db(h_data)
        return h_data
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            h_data = json.load(f)
            h_data.setdefault("submissions", [])
            return h_data
    except Exception:
        return {"submissions": []}

def save_history_db(h_data: dict):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(h_data, f, ensure_ascii=False, indent=2)

def authenticate(username: str, password: str):
    if not username or not password:
        return False, None, "Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu."
    db = load_accounts_db()
    user = db["users"].get(username)
    if not user or user["password"] != password:
        return False, None, "Tên đăng nhập hoặc mật khẩu không chính xác."
    return True, {
        "username": user["username"],
        "full_name": user["full_name"],
        "role": user["role"]
    }, "Đăng nhập thành công."

def register_user(username: str, password: str, full_name: str, score_math: int = 50, score_chem: int = 50):
    if not username or not password or not full_name:
        return False, "Vui lòng điền đầy đủ thông tin."
    db = load_accounts_db()
    if username in db["users"]:
        return False, f"Tài khoản '{username}' đã tồn tại."
    db["users"][username] = {
        "username": username,
        "password": password,
        "full_name": full_name,
        "role": "student",
        "theta_math": score100_to_theta(score_math),
        "theta_chem": score100_to_theta(score_chem),
        "node_stats": _default_node_stats(),
        "recent_questions": []
    }
    save_accounts_db(db)
    return True, f"Tạo tài khoản '{full_name}' ({username}) thành công!"

import json
import math
import os
import random
import re
from collections import defaultdict
import sympy as sp
import Script_Login

KNOWLEDGE_FILE = "Knowledge.txt"
x_sym = sp.Symbol("x", real=True)

# ==============================================================================
# KHO TRI THỨC HÓA HỌC ĐỒ SỘ: 250+ HÓA CHẤT & ĐỘNG CƠ SINH 1.700+ PHẢN ỨNG
# ==============================================================================

CHEM_METALS = {
    "K": {"val": 1, "active": 1, "passive": False, "water": True, "ox_state": 1},
    "Na": {"val": 1, "active": 2, "passive": False, "water": True, "ox_state": 1},
    "Ba": {"val": 2, "active": 3, "passive": False, "water": True, "ox_state": 2},
    "Ca": {"val": 2, "active": 4, "passive": False, "water": True, "ox_state": 2},
    "Mg": {"val": 2, "active": 5, "passive": False, "water": False, "ox_state": 2},
    "Al": {"val": 3, "active": 6, "passive": True, "water": False, "ox_state": 3},
    "Zn": {"val": 2, "active": 7, "passive": False, "water": False, "ox_state": 2},
    "Cr": {"val": 3, "active": 8, "passive": True, "water": False, "ox_state": 3},
    "Fe": {"val": 2, "active": 9, "passive": True, "water": False, "ox_state": 3}, # +2 với HCl/H2SO4 loãng, +3 với HNO3/Cl2
    "Ni": {"val": 2, "active": 10, "passive": False, "water": False, "ox_state": 2},
    "Sn": {"val": 2, "active": 11, "passive": False, "water": False, "ox_state": 2},
    "Pb": {"val": 2, "active": 12, "passive": False, "water": False, "ox_state": 2},
    "Cu": {"val": 2, "active": 14, "passive": False, "water": False, "ox_state": 2},
    "Ag": {"val": 1, "active": 15, "passive": False, "water": False, "ox_state": 1},
}

CHEM_CATIONS = [
    ("Na", 1, True), ("K", 1, True), ("Li", 1, True), ("NH4", 1, True),
    ("Mg", 2, False), ("Ca", 2, False), ("Ba", 2, False), ("Al", 3, False),
    ("Zn", 2, False), ("Fe", 2, False), ("Fe3", 3, False), ("Cu", 2, False),
    ("Ag", 1, False), ("Pb", 2, False), ("Mn", 2, False), ("Cr", 3, False)
]

CHEM_ANIONS = [
    ("Cl", 1), ("Br", 1), ("I", 1), ("NO3", 1), ("SO4", 2),
    ("CO3", 2), ("SO3", 2), ("PO4", 3), ("S", 2), ("OH", 1)
]

# Bảng tính tan chuẩn: True = Tan, False = Kết tủa / Không tan
def is_soluble(cat: str, an: str) -> bool:
    if cat in ("Na", "K", "Li", "NH4"):
        return True
    if an == "NO3":
        return True
    if an in ("Cl", "Br", "I"):
        if cat in ("Ag", "Pb"):
            return False
        return True
    if an == "SO4":
        if cat in ("Ba", "Pb", "Ca", "Ag"):
            return False
        return True
    if an == "OH":
        if cat in ("Na", "K", "Li", "NH4", "Ba", "Ca"):
            return True
        return False
    # CO3, SO3, PO4, S hầu hết không tan trừ kiềm/NH4 (MgS, CaS, BaS thủy phân/tan)
    if an == "S" and cat in ("Ba", "Ca", "Mg"):
        return True
    return False

PRECIP_COLOR = {
    "AgCl": "trắng", "AgBr": "vàng nhạt", "AgI": "vàng đậm",
    "BaSO4": "trắng", "PbSO4": "trắng", "CaSO4": "ít tan trắng",
    "CaCO3": "trắng", "BaCO3": "trắng", "MgCO3": "trắng",
    "Cu(OH)2": "xanh lam", "Fe(OH)3": "nâu đỏ", "Fe(OH)2": "trắng xanh",
    "Al(OH)3": "keo trắng", "Zn(OH)2": "keo trắng", "Mg(OH)2": "trắng",
    "CuS": "đen", "PbS": "đen", "Ag2S": "đen", "FeS": "đen", "ZnS": "trắng"
}

def make_formula(cat: str, c_val: int, an: str, a_val: int) -> str:
    c_sym = "Fe" if cat == "Fe3" else cat
    g = math.gcd(c_val, a_val)
    c_cnt = a_val // g
    a_cnt = c_val // g
    poly_cat = cat in ("NH4",)
    poly_an = an in ("NO3", "SO4", "CO3", "SO3", "PO4", "OH")

    c_part = f"({c_sym}){c_cnt}" if (poly_cat and c_cnt > 1) else (f"{c_sym}{c_cnt}" if c_cnt > 1 else c_sym)
    a_part = f"({an}){a_cnt}" if (poly_an and a_cnt > 1) else (f"{an}{a_cnt}" if a_cnt > 1 else an)
    return f"{c_part}{a_part}"

def parse_chem_formula(formula: str) -> dict:
    """Phân tích công thức hóa học thành từ điển số nguyên tử từng nguyên tố."""
    tokens = re.findall(r"([A-Z][a-z]?|\(|\)|\d+)", formula)
    stack = [defaultdict(int)]
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        if tok == "(":
            stack.append(defaultdict(int))
            i += 1
        elif tok == ")":
            top = stack.pop()
            mult = 1
            if i + 1 < len(tokens) and tokens[i + 1].isdigit():
                mult = int(tokens[i + 1])
                i += 2
            else:
                i += 1
            for el, cnt in top.items():
                stack[-1][el] += cnt * mult
        elif tok[0].isalpha():
            mult = 1
            if i + 1 < len(tokens) and tokens[i + 1].isdigit():
                mult = int(tokens[i + 1])
                i += 2
            else:
                i += 1
            stack[-1][tok] += mult
        else:
            i += 1
    return dict(stack[0])

def balance_chemical_equation_sympy(reactants: list, products: list) -> tuple:
    """Cân bằng mọi PTHH bằng không gian hạt nhân ma trận SymPy (Matrix.nullspace)."""
    all_species = reactants + products
    parsed_r = [parse_chem_formula(f) for f in reactants]
    parsed_p = [parse_chem_formula(f) for f in products]
    elements = sorted({el for d in parsed_r + parsed_p for el in d.keys()})

    matrix_rows = []
    for el in elements:
        row = [d.get(el, 0) for d in parsed_r] + [-d.get(el, 0) for d in parsed_p]
        matrix_rows.append(row)

    mat = sp.Matrix(matrix_rows)
    null = mat.nullspace()
    if not null:
        return None
    vec = null[0]
    lcm_den = 1
    for val in vec:
        frac = sp.Rational(val)
        lcm_den = sp.ilcm(lcm_den, frac.q)
    int_vec = [int(sp.Rational(val) * lcm_den) for val in vec]
    if int_vec[0] < 0:
        int_vec = [-x for x in int_vec]
    if any(x <= 0 for x in int_vec):
        return None
    g = 0
    for x in int_vec:
        g = math.gcd(g, x)
    int_vec = [x // g for x in int_vec]
    n_r = len(reactants)
    return int_vec[:n_r], int_vec[n_r:]

def _chem_to_ltx(formula: str) -> str:
    s = re.sub(r"([A-Za-z\)])(\d+)", r"\1_\2", formula)
    return f"\\text{{{s}}}" if "_" not in s else re.sub(r"([A-Za-z]+)", lambda m: f"\\text{{{m.group(1)}}}", s)

def _format_eq_latex(reactants: list, products: list, r_coeffs=None, p_coeffs=None, arrow="\\rightarrow") -> str:
    r_parts = []
    for idx, f in enumerate(reactants):
        c = "" if (not r_coeffs or r_coeffs[idx] == 1) else str(r_coeffs[idx])
        r_parts.append(f"{c}{_chem_to_ltx(f)}")
    p_parts = []
    for idx, f in enumerate(products):
        c = "" if (not p_coeffs or p_coeffs[idx] == 1) else str(p_coeffs[idx])
        p_parts.append(f"{c}{_chem_to_ltx(f)}")
    return f"${' + '.join(r_parts)} {arrow} {' + '.join(p_parts)}$"

def _build_chemical_catalog_and_reactions():
    """Khởi tạo 250+ hóa chất và 1.700+ phương trình hóa học chuẩn xác."""
    chemicals = set()
    for m in CHEM_METALS:
        chemicals.add(m)
    chemicals.update(["O2", "Cl2", "Br2", "I2", "S", "P", "C", "N2", "H2", "Si", "H2O", "CO", "CO2", "SO2", "SO3", "NO", "NO2", "N2O", "NH3", "H2S", "PH3"])
    chemicals.update(["HCl", "HBr", "HI", "HNO3", "H2SO4", "H3PO4", "H2CO3", "H2SO3", "FeS2", "FeS", "Cu2S", "CuS", "FeO", "Fe2O3", "Fe3O4", "CuO", "Al2O3", "ZnO", "MgO", "CaO", "BaO", "Na2O", "K2O", "KMnO4", "KClO3", "K2Cr2O7", "MnO2"])

    for cat, c_val, _ in CHEM_CATIONS:
        for an, a_val in CHEM_ANIONS:
            chemicals.add(make_formula(cat, c_val, an, a_val))

    reactions = {
        "BAL_ATOM": [],
        "BAL_GROUP": [],
        "BAL_ALGEBRA": [],
        "BAL_ION": [],
        "BAL_REDOX_STD": [],
        "BAL_REDOX_ENV": [],
        "BAL_REDOX_SELF": [],
        "BAL_REDOX_MULTI": [],
        "REACT_TYPE_4": [],
        "REACT_REDOX_ID": [],
        "REACT_EXCHANGE_COND": [],
        "REACT_ELECTROCHEM": []
    }

    # 1. Kim loại + Phi kim (O2, Cl2, S) -> BAL_ATOM, REACT_TYPE_4, BAL_REDOX_STD
    nonmetals = [
        ("O2", "O", 2, {"Fe": ("Fe3O4", 3)}),
        ("Cl2", "Cl", 1, {"Fe": ("FeCl3", 3)}),
        ("Br2", "Br", 1, {"Fe": ("FeBr3", 3)}),
        ("S", "S", 2, {"Fe": ("FeS", 2)})
    ]
    for m, m_meta in CHEM_METALS.items():
        for nm, an_sym, an_val, specials in nonmetals:
            if m in ("Ag", "Hg", "Pt", "Au") and nm in ("O2", "S"):
                continue
            if m in specials:
                prod = specials[m][0]
            else:
                prod = make_formula(m, m_meta["val"], an_sym, an_val)
            bal = balance_chemical_equation_sympy([m, nm], [prod])
            if bal:
                rec = {"r": [m, nm], "p": [prod], "rc": bal[0], "pc": bal[1], "type": "Hóa hợp & Oxi hóa - khử", "desc": f"{m} tác dụng với {nm}"}
                reactions["BAL_ATOM"].append(rec)
                reactions["REACT_TYPE_4"].append(rec)
                reactions["BAL_REDOX_STD"].append(rec)
                reactions["REACT_REDOX_ID"].append(rec)

    # 2. Kim loại đứng trước H + HCl / H2SO4 loãng -> REACT_ELECTROCHEM, REACT_TYPE_4, BAL_ATOM
    for m, m_meta in CHEM_METALS.items():
        if m_meta["active"] < 13:
            m_val = 2 if m == "Fe" else m_meta["val"]
            for acid, an_sym, an_val in [("HCl", "Cl", 1), ("HBr", "Br", 1), ("H2SO4", "SO4", 2)]:
                if m in ("Ba", "Ca", "Pb") and acid == "H2SO4":
                    continue
                salt = make_formula(m, m_val, an_sym, an_val)
                bal = balance_chemical_equation_sympy([m, acid], [salt, "H2"])
                if bal:
                    rec = {"r": [m, acid], "p": [salt, "H2"], "rc": bal[0], "pc": bal[1], "type": "Phản ứng thế & Oxi hóa - khử", "desc": f"{m} tan trong axit {acid} loãng giải phóng khí H2"}
                    reactions["BAL_ATOM"].append(rec)
                    reactions["REACT_TYPE_4"].append(rec)
                    reactions["REACT_ELECTROCHEM"].append(rec)

    # 3. Kim loại + HNO3 -> Muối nitrat + Sản phẩm khử (NO, NO2, N2O, N2, NH4NO3) + H2O -> BAL_REDOX_ENV
    red_products = [("NO", 3, 1), ("NO2", 1, 1), ("N2O", 8, 2), ("N2", 10, 2), ("NH4NO3", 8, 2)]
    for m, m_meta in CHEM_METALS.items():
        if m in ("Pt", "Au"):
            continue
        m_val = 3 if m == "Fe" else m_meta["val"]
        salt = make_formula(m, m_val, "NO3", 1)
        for sp_khu, e_gain, n_atoms in red_products:
            if m in ("Cu", "Ag", "Pb") and sp_khu in ("N2O", "N2", "NH4NO3"):
                continue
            bal = balance_chemical_equation_sympy([m, "HNO3"], [salt, sp_khu, "H2O"])
            if bal:
                env_acid = bal[0][0] * m_val
                rec = {
                    "r": [m, "HNO3"], "p": [salt, sp_khu, "H2O"],
                    "rc": bal[0], "pc": bal[1],
                    "metal": m, "sp_khu": sp_khu, "env_acid": env_acid,
                    "type": "Oxi hóa - khử có môi trường axit"
                }
                reactions["BAL_REDOX_ENV"].append(rec)
                reactions["BAL_REDOX_STD"].append(rec)

    # 4. Kim loại + H2SO4 đặc nóng -> Muối sunfat + SO2/H2S/S + H2O
    for m, m_meta in CHEM_METALS.items():
        m_val = 3 if m == "Fe" else m_meta["val"]
        salt = make_formula(m, m_val, "SO4", 2)
        for sp_khu in ["SO2", "H2S", "S"]:
            if m in ("Cu", "Ag") and sp_khu != "SO2":
                continue
            bal = balance_chemical_equation_sympy([m, "H2SO4"], [salt, sp_khu, "H2O"])
            if bal:
                rec = {"r": [m, "H2SO4"], "p": [salt, sp_khu, "H2O"], "rc": bal[0], "pc": bal[1], "metal": m, "sp_khu": sp_khu, "env_acid": bal[0][0] * m_val // 2 if (bal[0][0] * m_val) % 2 == 0 else bal[1][0]}
                reactions["BAL_REDOX_ENV"].append(rec)

    # 5. Phản ứng trao đổi ion: Muối tan + Muối tan / Bazơ tan / Axit -> Sinh ra 1.200+ phản ứng có kết tủa hoặc khí!
    soluble_salts = []
    for cat, c_val, _ in CHEM_CATIONS:
        for an, a_val in CHEM_ANIONS:
            if an == "OH":
                continue
            if is_soluble(cat, an):
                soluble_salts.append((cat, c_val, an, a_val, make_formula(cat, c_val, an, a_val)))

    # Thêm bazơ tan & axit mạnh làm tác nhân trao đổi
    for idx1 in range(len(soluble_salts)):
        c1, cv1, a1, av1, f1 = soluble_salts[idx1]
        for idx2 in range(idx1 + 1, len(soluble_salts)):
            c2, cv2, a2, av2, f2 = soluble_salts[idx2]
            if c1 == c2 or a1 == a2:
                continue
            # Sản phẩm trao đổi: (c1, a2) và (c2, a1)
            sol12 = is_soluble(c1, a2)
            sol21 = is_soluble(c2, a1)
            if not (sol12 and sol21):
                p1 = make_formula(c1, cv1, a2, av2)
                p2 = make_formula(c2, cv2, a1, av1)
                if p1 == p2 or f1 == f2:
                    continue
                bal = balance_chemical_equation_sympy([f1, f2], [p1, p2])
                if bal:
                    precip = p1 if not sol12 else p2
                    rec = {
                        "r": [f1, f2], "p": [p1, p2], "rc": bal[0], "pc": bal[1],
                        "precip": precip, "color": PRECIP_COLOR.get(precip, "ít tan"),
                        "type": "Phản ứng trao đổi ion (không oxi hóa - khử)"
                    }
                    reactions["BAL_GROUP"].append(rec)
                    reactions["REACT_EXCHANGE_COND"].append(rec)
                    reactions["REACT_TYPE_4"].append(rec)

    # Bazơ tan + Muối tan -> Kết tủa hiđroxit
    alkalis = [("Na", 1, "NaOH"), ("K", 1, "KOH"), ("Ba", 2, "Ba(OH)2"), ("Ca", 2, "Ca(OH)2")]
    for alk_c, alk_v, alk_f in alkalis:
        for c2, cv2, a2, av2, f2 in soluble_salts:
            if c2 in ("Na", "K", "Li", "NH4", "Ba", "Ca"):
                continue
            p_oh = make_formula(c2, cv2, "OH", 1)
            p_salt = make_formula(alk_c, alk_v, a2, av2)
            bal = balance_chemical_equation_sympy([alk_f, f2], [p_oh, p_salt])
            if bal:
                rec = {
                    "r": [alk_f, f2], "p": [p_oh, p_salt], "rc": bal[0], "pc": bal[1],
                    "precip": p_oh, "color": PRECIP_COLOR.get(p_oh, "kết tủa"),
                    "type": "Phản ứng trao đổi tạo kết tủa hiđroxit"
                }
                reactions["BAL_GROUP"].append(rec)
                reactions["REACT_EXCHANGE_COND"].append(rec)

    # 6. Kim loại đẩy kim loại khỏi dung dịch muối -> REACT_ELECTROCHEM
    metal_list = [(m, meta) for m, meta in CHEM_METALS.items() if not meta["water"] and m not in ("Cr", "Sn", "Pb")]
    for m1, meta1 in metal_list:
        for m2, meta2 in metal_list:
            if meta1["active"] < meta2["active"] and m1 != m2:
                v1 = 2 if m1 == "Fe" else meta1["val"]
                v2 = 2 if m2 == "Fe" else meta2["val"]
                for an, av in [("NO3", 1), ("SO4", 2), ("Cl", 1)]:
                    if m2 == "Ag" and an in ("Cl", "SO4"):
                        continue
                    s_in = make_formula(m2, v2, an, av)
                    s_out = make_formula(m1, v1, an, av)
                    bal = balance_chemical_equation_sympy([m1, s_in], [s_out, m2])
                    if bal:
                        rec = {"r": [m1, s_in], "p": [s_out, m2], "rc": bal[0], "pc": bal[1], "m1": m1, "m2": m2, "type": "Phản ứng thế kim loại"}
                        reactions["REACT_ELECTROCHEM"].append(rec)
                        reactions["REACT_TYPE_4"].append(rec)

    # 7. Đa nguyên tố, tự oxi hóa - khử, đốt cháy đại số, ion rút gọn
    multi_specs = [
        (["FeS2", "HNO3"], ["Fe(NO3)3", "H2SO4", "NO", "H2O"]),
        (["FeS2", "HNO3"], ["Fe(NO3)3", "H2SO4", "NO2", "H2O"]),
        (["Cu2S", "HNO3"], ["Cu(NO3)2", "CuSO4", "NO", "H2O"]),
        (["Cu2S", "HNO3"], ["Cu(NO3)2", "H2SO4", "NO2", "H2O"]),
        (["FeS", "HNO3"], ["Fe(NO3)3", "H2SO4", "NO", "H2O"]),
        (["Fe3O4", "HNO3"], ["Fe(NO3)3", "NO", "H2O"]),
        (["Fe3O4", "HNO3"], ["Fe(NO3)3", "NO2", "H2O"]),
        (["FeO", "HNO3"], ["Fe(NO3)3", "NO", "H2O"]),
        (["FeCO3", "HNO3"], ["Fe(NO3)3", "NO", "CO2", "H2O"]),
        (["Fe3O4", "H2SO4"], ["Fe2(SO4)3", "SO2", "H2O"]),
    ]
    for r, p in multi_specs:
        bal = balance_chemical_equation_sympy(r, p)
        if bal:
            reactions["BAL_REDOX_MULTI"].append({"r": r, "p": p, "rc": bal[0], "pc": bal[1]})

    alg_specs = [
        (["FeS2", "O2"], ["Fe2O3", "SO2"]),
        (["FeS", "O2"], ["Fe2O3", "SO2"]),
        (["Cu2S", "O2"], ["CuO", "SO2"]),
        (["NH3", "O2"], ["NO", "H2O"]),
        (["NH3", "O2"], ["N2", "H2O"]),
        (["H2S", "O2"], ["SO2", "H2O"]),
        (["PH3", "O2"], ["P2O5", "H2O"]),
        (["Fe3O4", "CO"], ["Fe", "CO2"]),
        (["Fe2O3", "CO"], ["Fe", "CO2"]),
        (["FeO", "Al"], ["Fe", "Al2O3"]),
        (["Fe3O4", "Al"], ["Fe", "Al2O3"]),
    ]
    for r, p in alg_specs:
        bal = balance_chemical_equation_sympy(r, p)
        if bal:
            reactions["BAL_ALGEBRA"].append({"r": r, "p": p, "rc": bal[0], "pc": bal[1]})

    self_specs = [
        (["Cl2", "NaOH"], ["NaCl", "NaClO", "H2O"]),
        (["Cl2", "KOH"], ["KCl", "KClO3", "H2O"]),
        (["Cl2", "Ca(OH)2"], ["CaCl2", "Ca(ClO)2", "H2O"]),
        (["Br2", "KOH"], ["KBr", "KBrO3", "H2O"]),
        (["NO2", "NaOH"], ["NaNO2", "NaNO3", "H2O"]),
        (["NO2", "KOH"], ["KNO2", "KNO3", "H2O"]),
        (["S", "NaOH"], ["Na2S", "Na2SO3", "H2O"]),
        (["KMnO4"], ["K2MnO4", "MnO2", "O2"]),
        (["KClO3"], ["KCl", "O2"]),
        (["NH4NO3"], ["N2O", "H2O"]),
    ]
    for r, p in self_specs:
        bal = balance_chemical_equation_sympy(r, p)
        if bal:
            reactions["BAL_REDOX_SELF"].append({"r": r, "p": p, "rc": bal[0], "pc": bal[1]})

    ion_specs = [
        (["Fe^{2+}", "MnO4^-", "H^+"], ["Fe^{3+}", "Mn^{2+}", "H2O"], [5, 1, 8], [5, 1, 4]),
        (["Cu", "H^+", "NO3^-"], ["Cu^{2+}", "NO", "H2O"], [3, 8, 2], [3, 2, 4]),
        (["Cu", "H^+", "NO3^-"], ["Cu^{2+}", "NO2", "H2O"], [1, 4, 2], [1, 2, 2]),
        (["Fe", "H^+", "NO3^-"], ["Fe^{3+}", "NO", "H2O"], [1, 4, 1], [1, 1, 2]),
        (["Ag", "H^+", "NO3^-"], ["Ag^+", "NO", "H2O"], [3, 4, 1], [3, 1, 2]),
        (["Mg", "H^+", "NO3^-"], ["Mg^{2+}", "N2O", "H2O"], [4, 10, 2], [4, 1, 5]),
        (["Zn", "H^+", "NO3^-"], ["Zn^{2+}", "NH4^+", "H2O"], [4, 10, 1], [4, 1, 3]),
        (["Al", "H^+", "NO3^-"], ["Al^{3+}", "NO", "H2O"], [1, 4, 1], [1, 1, 2]),
        (["Cr2O7^{2-}", "Fe^{2+}", "H^+"], ["Cr^{3+}", "Fe^{3+}", "H2O"], [1, 6, 14], [2, 6, 7]),
        (["Cl^-", "MnO4^-", "H^+"], ["Cl2", "Mn^{2+}", "H2O"], [10, 2, 16], [5, 2, 8]),
        (["Br^-", "MnO4^-", "H^+"], ["Br2", "Mn^{2+}", "H2O"], [10, 2, 16], [5, 2, 8]),
        (["I^-", "MnO4^-", "H^+"], ["I2", "Mn^{2+}", "H2O"], [10, 2, 16], [5, 2, 8]),
        (["SO3^{2-}", "MnO4^-", "H^+"], ["SO4^{2-}", "Mn^{2+}", "H2O"], [5, 2, 6], [5, 2, 3]),
        (["NO2^-", "MnO4^-", "H^+"], ["NO3^-", "Mn^{2+}", "H2O"], [5, 2, 6], [5, 2, 3]),
        (["Fe^{2+}", "NO3^-", "H^+"], ["Fe^{3+}", "NO", "H2O"], [3, 1, 4], [3, 1, 2]),
        (["FeS2", "H^+", "NO3^-"], ["Fe^{3+}", "SO4^{2-}", "NO", "H2O"], [1, 4, 5], [1, 2, 5, 2]),
        (["Cu2S", "H^+", "NO3^-"], ["Cu^{2+}", "SO4^{2-}", "NO", "H2O"], [3, 16, 10], [6, 3, 10, 8]),
        (["Ba^{2+}", "SO4^{2-}"], ["BaSO4"], [1, 1], [1]),
        (["Ag^+", "Cl^-"], ["AgCl"], [1, 1], [1]),
        (["Ca^{2+}", "CO3^{2-}"], ["CaCO3"], [1, 1], [1]),
        (["Fe^{3+}", "OH^-"], ["Fe(OH)3"], [1, 3], [1]),
        (["Cu^{2+}", "OH^-"], ["Cu(OH)2"], [1, 2], [1]),
        (["Al^{3+}", "OH^-"], ["Al(OH)3"], [1, 3], [1]),
        (["CO3^{2-}", "H^+"], ["CO2", "H2O"], [1, 2], [1, 1]),
        (["HCO3^-", "OH^-"], ["CO3^{2-}", "H2O"], [1, 1], [1, 1]),
    ]
    for r, p, rc, pc in ion_specs:
        reactions["BAL_ION"].append({"r": r, "p": p, "rc": rc, "pc": pc})

    return sorted(chemicals), reactions

CHEM_CATALOG, CHEM_REACTIONS_DB = _build_chemical_catalog_and_reactions()

def get_chemical_knowledge_stats() -> dict:
    total_rxns = sum(len(v) for v in CHEM_REACTIONS_DB.values())
    return {
        "total_chemicals": len(CHEM_CATALOG),
        "total_reactions": total_rxns,
        "by_rule": {k: len(v) for k, v in CHEM_REACTIONS_DB.items()}
    }

def convert_expr_to_latex(expr_str: str) -> str:
    return Script_Login.format_math_to_latex(expr_str)

def _build_stem_intro(expr_latex: str, func_desc: str, style_idx: int) -> str:
    templates = [
        f"Cho hàm số {func_desc} $y = f(x) = {expr_latex}$.",
        f"Cho hàm số $y = {expr_latex}$.",
        f"Xét hàm số $f(x)$ xác định bởi công thức $f(x) = {expr_latex}$.",
        f"Cho đường cong $(C)$ là đồ thị của hàm số $y = {expr_latex}$.",
        f"Biết $f(x) = {expr_latex}$ là hàm số có đạo hàm trên tập xác định.",
        f"Cho đồ thị $(C): y = {expr_latex}$."
    ]
    return templates[style_idx % len(templates)]

def infer_question_difficulty(content: str, q_type: str, steps: int, expected_time: int):
    type_weights = {"THEORY": 0.0, "ALGORITHMIC": 0.45, "APPLICATION": 0.95, "SYNTHESIS": 1.5}
    token_markers = [
        "\\ln", "\\log", "\\sin", "\\cos", "\\tan", "\\sqrt", "\\int", "\\frac",
        "tiếp tuyến", "song song", "vuông góc", "cực trị", "đồng biến", "tham số",
        "từng phần", "đổi biến", "FeS_2", "Cu_2S", "HNO_3", "thụ động"
    ]
    marker_hits = sum(1 for m in token_markers if m.lower() in content.lower())
    complexity_score = round(steps * 0.55 + type_weights.get(q_type, 0.4) + marker_hits * 0.22 + (expected_time / 90.0) * 0.4, 2)

    if steps <= 1 and q_type == "THEORY" and complexity_score < 1.35:
        return "DE", round(max(-2.2, -1.7 + 0.25 * complexity_score), 2), {
            "steps": steps, "complexity_score": complexity_score, "triggered_rule": "R_DIFF_01 (Mức Dễ)"
        }
    if steps <= 2 and complexity_score < 2.15:
        return "TRUNG_BINH", round(-0.5 + 0.35 * (complexity_score - 1.2), 2), {
            "steps": steps, "complexity_score": complexity_score, "triggered_rule": "R_DIFF_02 (Mức Trung bình)"
        }
    if steps == 3 or complexity_score < 2.85:
        return "KHA", round(0.6 + 0.35 * (complexity_score - 2.0), 2), {
            "steps": steps, "complexity_score": complexity_score, "triggered_rule": "R_DIFF_03 (Mức Khá)"
        }
    return "KHO", round(min(2.5, 1.5 + 0.35 * (complexity_score - 2.7)), 2), {
        "steps": steps, "complexity_score": complexity_score, "triggered_rule": "R_DIFF_04 (Mức Khó)"
    }

def _generate_chem_question_from_db(formula_rule: str, question_form: str, stem_style_idx: int, seed_offset: int):
    pool = CHEM_REACTIONS_DB.get(formula_rule) or CHEM_REACTIONS_DB["BAL_ATOM"]
    rxn = random.choice(pool) if seed_offset == 0 else pool[(seed_offset + random.randint(0, len(pool) - 1)) % len(pool)]
    r_list, p_list, rc, pc = rxn["r"], rxn["p"], rxn["rc"], rxn["pc"]
    unbalanced_ltx = _format_eq_latex(r_list, p_list)
    balanced_ltx = _format_eq_latex(r_list, p_list, rc, pc)
    chem_intros = [
        f"Cho sơ đồ phản ứng: {unbalanced_ltx}.",
        f"Xét phương trình hóa học: {unbalanced_ltx}.",
        f"Cân bằng phương trình phản ứng sau với hệ số nguyên tối giản: {unbalanced_ltx}.",
        f"Trong phòng thí nghiệm, xét phản ứng: {unbalanced_ltx}."
    ]
    intro = chem_intros[stem_style_idx % len(chem_intros)]

    if formula_rule in ("BAL_ATOM", "BAL_GROUP", "BAL_ALGEBRA", "BAL_ION"):
        if question_form == "FORM_CHEM_PRODUCT" and "precip" in rxn:
            precip = rxn["precip"]
            color = rxn["color"]
            content = f"Trộn hai dung dịch chứa {_chem_to_ltx(r_list[0])} và {_chem_to_ltx(r_list[1])} thu được sản phẩm kết tủa nào sau đây?"
            wrong1 = _chem_to_ltx(p_list[1] if p_list[0] == precip else p_list[0])
            options = {
                "A": f"${_chem_to_ltx(precip)}\\downarrow$ ({color})",
                "B": f"${wrong1}$",
                "C": "Không xảy ra phản ứng",
                "D": "Chỉ có khí $\\text{{H}}_2$ thoát ra"
            }
            explanation = f"Phương trình: {balanced_ltx}. Kết tủa thu được là ${_chem_to_ltx(precip)}$ ({color})."
            return content, options, explanation, 2, 50, "ALGORITHMIC"

        if question_form == "FORM_CHEM_RATIO" and len(rc) >= 2:
            ratio_g = math.gcd(rc[0], rc[1])
            a_r, b_r = rc[0] // ratio_g, rc[1] // ratio_g
            content = f"{intro} Tỉ lệ hệ số nguyên tối giản giữa ${_chem_to_ltx(r_list[0])}$ và ${_chem_to_ltx(r_list[1])}$ là:"
            options = {
                "A": f"${a_r}:{b_r}$",
                "B": f"${b_r}:{a_r}$" if a_r != b_r else f"${a_r}:{b_r + 1}$",
                "C": f"${a_r + 1}:{b_r}$",
                "D": f"${a_r}:{b_r + 2}$"
            }
            explanation = f"Phương trình cân bằng: {balanced_ltx}. Tỉ lệ hệ số tối giản là ${a_r}:{b_r}$."
            return content, options, explanation, 2, 50, "ALGORITHMIC"

        total_coeff = sum(rc) + sum(pc)
        prod_coeff = sum(pc)
        if (seed_offset + stem_style_idx) % 2 == 0:
            content = f"{intro} Tổng hệ số nguyên tối giản của tất cả các chất trong phương trình là:"
            ans_val = total_coeff
        else:
            content = f"{intro} Tổng hệ số nguyên tối giản của các chất sản phẩm là:"
            ans_val = prod_coeff
        options = {
            "A": f"${ans_val}$",
            "B": f"${ans_val + 2}$",
            "C": f"${max(2, ans_val - 2)}$",
            "D": f"${ans_val + 4}$"
        }
        explanation = f"Phương trình cân bằng chuẩn: {balanced_ltx}. Đáp án đúng là ${ans_val}$."
        steps = 3 if formula_rule in ("BAL_ALGEBRA", "BAL_ION") else 2
        return content, options, explanation, steps, 45 + steps * 15, ("APPLICATION" if steps >= 3 else "ALGORITHMIC")

    elif formula_rule in ("BAL_REDOX_STD", "BAL_REDOX_ENV", "BAL_REDOX_SELF", "BAL_REDOX_MULTI"):
        if question_form == "FORM_CHEM_RATIO" and len(rc) >= 2:
            if "env_acid" in rxn and (seed_offset % 2 == 1):
                g = math.gcd(rc[0], rxn["env_acid"])
                a_r, e_r = rc[0] // g, rxn["env_acid"] // g
                content = f"{intro} Tỉ lệ giữa số nguyên tử ${_chem_to_ltx(rxn['metal'])}$ và số phân tử ${_chem_to_ltx(r_list[1])}$ đóng vai trò môi trường tạo muối là:"
                options = {
                    "A": f"${a_r}:{e_r}$",
                    "B": f"${rc[0]}:{rc[1]}$" if (rc[0], rc[1]) != (a_r, e_r) else f"${a_r}:{e_r + 2}$",
                    "C": f"${a_r}:{e_r + 1}$",
                    "D": f"${e_r}:{a_r}$"
                }
                explanation = f"PTHH: {balanced_ltx}. Có ${rxn['env_acid']}$ phân tử axit tạo muối đóng vai trò môi trường, tỉ lệ tối giản là ${a_r}:{e_r}$."
                return content, options, explanation, 3, 90, "APPLICATION"
            g = math.gcd(rc[0], rc[1])
            a_r, b_r = rc[0] // g, rc[1] // g
            content = f"{intro} Tỉ lệ hệ số nguyên tối giản giữa ${_chem_to_ltx(r_list[0])}$ và ${_chem_to_ltx(r_list[1])}$ là:"
            options = {
                "A": f"${a_r}:{b_r}$",
                "B": f"${b_r}:{a_r}$" if a_r != b_r else f"${a_r}:{b_r + 2}$",
                "C": f"${a_r + 1}:{b_r}$",
                "D": f"${a_r}:{b_r + 3}$"
            }
            explanation = f"Cân bằng thăng bằng electron: {balanced_ltx}. Tỉ lệ là ${a_r}:{b_r}$."
            return content, options, explanation, 3, 85, "APPLICATION"

        total_coeff = sum(rc) + sum(pc)
        content = f"{intro} Tổng hệ số nguyên tối giản của các chất trong phương trình đã cân bằng là:"
        options = {
            "A": f"${total_coeff}$",
            "B": f"${total_coeff + 3}$",
            "C": f"${max(3, total_coeff - 2)}$",
            "D": f"${total_coeff + 6}$"
        }
        explanation = f"PTHH cân bằng: {balanced_ltx}. Tổng hệ số $= {total_coeff}$."
        steps = 4 if formula_rule == "BAL_REDOX_MULTI" else 3
        return content, options, explanation, steps, (115 if steps == 4 else 85), ("SYNTHESIS" if steps == 4 else "APPLICATION")

    elif formula_rule == "REACT_EXCHANGE_COND":
        precip = rxn.get("precip", p_list[0])
        color = rxn.get("color", "kết tủa")
        content = f"Khi trộn dung dịch ${_chem_to_ltx(r_list[0])}$ với dung dịch ${_chem_to_ltx(r_list[1])}$, hiện tượng thu được là:"
        options = {
            "A": f"Xuất hiện kết tủa ${_chem_to_ltx(precip)}$ ({color})",
            "B": "Không có phản ứng xảy ra",
            "C": "Chỉ có khí không màu thoát ra",
            "D": "Dung dịch chuyển hoàn toàn sang màu đỏ"
        }
        explanation = f"Phản ứng trao đổi ion xảy ra do tạo kết tủa: {balanced_ltx}."
        return content, options, explanation, 2, 45, "ALGORITHMIC"

    elif formula_rule == "REACT_ELECTROCHEM":
        if "m1" in rxn:
            m1, m2 = rxn["m1"], rxn["m2"]
            content = f"Cho kim loại ${_chem_to_ltx(m1)}$ dư vào dung dịch ${_chem_to_ltx(r_list[1])}$. Sản phẩm thu được sau phản ứng là:"
            options = {
                "A": f"${_chem_to_ltx(p_list[0])}$ và kim loại ${_chem_to_ltx(m2)}$",
                "B": "Không xảy ra phản ứng",
                "C": f"${_chem_to_ltx(p_list[0])}$ và khí $\\text{{H}}_2$",
                "D": f"Chỉ có khí $\\text{{O}}_2$ thoát ra"
            }
            explanation = f"Kim loại ${_chem_to_ltx(m1)}$ đứng trước ${_chem_to_ltx(m2)}$ trong dãy hoạt động hóa học: {balanced_ltx}."
            return content, options, explanation, 2, 45, "ALGORITHMIC"
        content = f"Cho kim loại ${_chem_to_ltx(r_list[0])}$ tác dụng với dung dịch ${_chem_to_ltx(r_list[1])}$ loãng. Phương trình đúng là:"
        options = {
            "A": balanced_ltx,
            "B": "Không xảy ra phản ứng",
            "C": _format_eq_latex(r_list, [p_list[0], "O2"]),
            "D": _format_eq_latex(r_list, [p_list[0], "H2O"])
        }
        explanation = f"${_chem_to_ltx(r_list[0])}$ đứng trước $\\text{{H}}$ nên phản ứng: {balanced_ltx}."
        return content, options, explanation, 1, 35, "THEORY"

    else:
        rxn_type = rxn.get("type", "Phản ứng hóa học vô cơ")
        content = f"Phản ứng hóa học {balanced_ltx} thuộc loại phản ứng nào dưới đây?"
        distractors = ["Phản ứng hóa hợp & Oxi hóa - khử", "Phản ứng trao đổi ion (không oxi hóa - khử)", "Phản ứng thế & Oxi hóa - khử", "Phản ứng phân hủy"]
        others = [d for d in distractors if d != rxn_type][:3]
        options = {"A": rxn_type, "B": others[0], "C": others[1], "D": others[2]}
        explanation = f"Dựa vào số chất tham gia, sản phẩm và sự thay đổi số oxi hóa, đây là {rxn_type}."
        return content, options, explanation, 1, 35, "THEORY"

def generate_question_by_rule_and_sympy(concept_node: str, formula_rule: str, question_form: str, target_difficulty: str = "TRUNG_BINH", stem_style_idx: int = 0, seed_offset: int = 0):
    all_nodes = Script_Login.get_all_concept_nodes()
    if concept_node not in all_nodes:
        concept_node = "MATH_DERIV_01"
    subject = all_nodes[concept_node]["subject"]
    topic = all_nodes[concept_node]["topic"]

    valid_rules = Script_Login.get_filtered_formula_rules(subject=subject, concept_node=concept_node)
    if formula_rule not in valid_rules:
        formula_rule = next(iter(valid_rules.keys()))

    valid_forms = Script_Login.get_filtered_question_forms(subject=subject, concept_node=concept_node, formula_rule=formula_rule)
    if question_form not in valid_forms:
        question_form = next(iter(valid_forms.keys()))

    rule_info = Script_Login.get_formula_rule_info(formula_rule)
    general_method = rule_info["general_method"]

    # ==================== NHÓM HÓA HỌC (SINH TỪ KHO 1.700+ PHẢN ỨNG) ====================
    if subject == "CHEM":
        content, options, explanation, steps, exp_time, q_type = _generate_chem_question_from_db(
            formula_rule, question_form, stem_style_idx, seed_offset
        )
        diff_label, irt_b, trace = infer_question_difficulty(content, q_type, steps, expected_time=exp_time)
        trace["applied_transform_rule"] = f"R_TRANS_STEM (Mẫu Hóa #{(stem_style_idx % 4) + 1}) + Kho {get_chemical_knowledge_stats()['total_reactions']} PTHH"
        return {
            "subject": subject,
            "topic": topic,
            "concept_node": concept_node,
            "formula_rule": formula_rule,
            "question_form": question_form,
            "q_type": q_type,
            "steps": steps,
            "difficulty": diff_label,
            "irt_b": irt_b,
            "irt_a": 1.25,
            "expected_time": exp_time,
            "attempts": random.randint(10, 28),
            "correct_rate": round(random.uniform(0.32, 0.85), 2),
            "avg_time": exp_time + random.randint(-6, 14),
            "content": content,
            "options": options,
            "answer": "A",
            "general_method": general_method,
            "explanation": explanation,
            "rule_trace": trace
        }

    # ==================== NHÓM TOÁN HỌC (SINH BẰNG SYMPY) ====================
    if formula_rule == "DRV_POW":
        a = ((seed_offset + random.randint(1, 4)) % 4) + 1
        b = ((seed_offset + random.randint(2, 6)) % 5) + 2
        c = ((seed_offset + random.randint(1, 5)) % 5) + 1
        d = random.choice([-3, -1, 2, 4])
        poly_expr = a * x_sym**3 - b * x_sym**2 + c * x_sym + d
        deriv_expr = sp.diff(poly_expr, x_sym)
        latex_poly = sp.latex(poly_expr)
        latex_deriv = sp.latex(deriv_expr)
        intro = _build_stem_intro(latex_poly, "đa thức bậc ba", stem_style_idx)

        if question_form == "FORM_VAL_POINT":
            x0 = random.choice([-1, 1, 2])
            val = int(deriv_expr.subs(x_sym, x0))
            content = f"{intro} Giá trị của đạo hàm $f'({x0})$ bằng:"
            options = {"A": f"${val}$", "B": f"${val + 2 * b}$", "C": f"${int(poly_expr.subs(x_sym, x0))}$", "D": f"${val - 3 * a}$"}
            explanation = f"Ta có $y' = {latex_deriv}$. Thay $x = {x0}$ được $y'({x0}) = {val}$."
            steps, exp_time, q_type = 2, 45, "ALGORITHMIC"
        elif question_form == "FORM_TANGENT_SLOPE":
            x0 = random.choice([1, 2])
            k_val = int(deriv_expr.subs(x_sym, x0))
            content = f"{intro} Hệ số góc $k$ của tiếp tuyến với đồ thị tại điểm có hoành độ $x_0 = {x0}$ là:"
            options = {"A": f"$k = {k_val}$", "B": f"$k = {k_val + 4}$", "C": f"$k = {-k_val if k_val != 0 else 5}$", "D": f"$k = {int(poly_expr.subs(x_sym, x0))}$"}
            explanation = f"Hệ số góc tiếp tuyến tại $x_0 = {x0}$ là $k = y'({x0}) = {k_val}$."
            steps, exp_time, q_type = 2, 50, "APPLICATION"
        elif question_form == "FORM_TANGENT_EQ":
            x0 = 1
            y0 = int(poly_expr.subs(x_sym, x0))
            k_val = int(deriv_expr.subs(x_sym, x0))
            tang_eq = sp.expand(k_val * (x_sym - x0) + y0)
            content = f"{intro} Phương trình tiếp tuyến của đồ thị hàm số tại điểm $M({x0}; {y0})$ là:"
            options = {
                "A": f"$y = {sp.latex(tang_eq)}$",
                "B": f"$y = {sp.latex(sp.expand(k_val * (x_sym + x0) + y0))}$",
                "C": f"$y = {sp.latex(sp.expand((k_val + 3) * (x_sym - x0) + y0))}$",
                "D": f"$y = {sp.latex(sp.expand(k_val * x_sym - y0))}$"
            }
            explanation = f"Ta có $y'({x0}) = {k_val}$. Tiếp tuyến: $y = {k_val}(x - {x0}) + ({y0}) = {sp.latex(tang_eq)}$."
            steps, exp_time, q_type = 3, 80, "APPLICATION"
        elif question_form == "FORM_SOLVE_COND":
            quad_expr = x_sym**3 - 3 * a * x_sym**2 + 2
            q_deriv = sp.diff(quad_expr, x_sym)
            content = f"{_build_stem_intro(sp.latex(quad_expr), 'bậc ba', stem_style_idx)} Tập nghiệm của phương trình $y' = 0$ là:"
            options = {"A": f"$S = \\{{0; {2 * a}\\}}$", "B": f"$S = \\{{0; {a}\\}}$", "C": f"$S = \\{{-{2 * a}; 0\\}}$", "D": f"$S = \\{{{2 * a}\\}}$"}
            explanation = f"Ta có $y' = {sp.latex(q_deriv)} = 3x(x - {2 * a}) = 0 \\Leftrightarrow x = 0$ hoặc $x = {2 * a}$."
            steps, exp_time, q_type = 2, 55, "ALGORITHMIC"
        else:
            content = f"{intro} Biểu thức đạo hàm $y'$ của hàm số là:"
            options = {
                "A": f"$y' = {latex_deriv}$",
                "B": f"$y' = {sp.latex(a * x_sym**2 - b * x_sym + c)}$",
                "C": f"$y' = {sp.latex(3 * a * x_sym**2 + 2 * b * x_sym + c)}$",
                "D": f"$y' = {sp.latex(3 * a * x_sym**3 - 2 * b * x_sym + c)}$"
            }
            explanation = f"Áp dụng $(x^n)' = n \\cdot x^{{n-1}}$, ta thu được $y' = {latex_deriv}$."
            steps, exp_time, q_type = 1, 35, "THEORY"

    elif formula_rule == "DRV_PROD":
        a = random.choice([1, 2, 3, 4])
        b = random.choice([2, 3, 5])
        u_expr = x_sym**2 + a
        v_expr = b * x_sym - 1
        prod_deriv = sp.expand(sp.diff(u_expr * v_expr, x_sym))
        buggy_1 = sp.expand(sp.diff(u_expr, x_sym) * sp.diff(v_expr, x_sym))
        buggy_2 = sp.expand(sp.diff(u_expr, x_sym) * v_expr - u_expr * sp.diff(v_expr, x_sym))
        intro = _build_stem_intro(f"({sp.latex(u_expr)})({sp.latex(v_expr)})", "dạng tích", stem_style_idx)

        if question_form in ["FORM_VAL_POINT", "FORM_TANGENT_SLOPE"]:
            x0 = random.choice([1, 2])
            val = int(prod_deriv.subs(x_sym, x0))
            content = f"{intro} Giá trị của đạo hàm $y'$ tại $x_0 = {x0}$ bằng:"
            options = {"A": f"${val}$", "B": f"${int(buggy_1.subs(x_sym, x0))}$", "C": f"${val - b}$", "D": f"${val + 2 * a}$"}
            explanation = f"Ta có $y' = {sp.latex(prod_deriv)} \\Rightarrow y'({x0}) = {val}$."
            steps, exp_time, q_type = 2, 60, "ALGORITHMIC"
        else:
            content = f"{intro} Đạo hàm của hàm số đã cho là:"
            options = {"A": f"$y' = {sp.latex(prod_deriv)}$", "B": f"$y' = {sp.latex(buggy_1)}$", "C": f"$y' = {sp.latex(buggy_2)}$", "D": f"$y' = {sp.latex(prod_deriv + b)}$"}
            explanation = f"Áp dụng $(u \\cdot v)' = u'v + uv' = {sp.latex(prod_deriv)}$."
            steps, exp_time, q_type = 2, 55, "ALGORITHMIC"

    elif formula_rule == "DRV_QUOT":
        a = random.choice([2, 3, 4])
        b = random.choice([1, 2, 3])
        d = random.choice([-1, -2, 1])
        det_val = a * d - b
        if det_val == 0:
            b += 1
            det_val = a * d - b
        expr_latex = f"\\frac{{{a}x + {b}}}{{x {'+' if d > 0 else '-'} {abs(d)}}}"
        denom_sq = f"(x {'+' if d > 0 else '-'} {abs(d)})^2"
        intro = _build_stem_intro(expr_latex, "phân thức hữu tỉ", stem_style_idx)

        if question_form in ["FORM_VAL_POINT", "FORM_TANGENT_SLOPE"]:
            x0 = -d + 1
            content = f"{intro} Hệ số góc của tiếp tuyến với đồ thị tại điểm có hoành độ $x_0 = {x0}$ bằng:"
            options = {"A": f"${det_val}$", "B": f"${-det_val}$", "C": f"${a * d + b}$", "D": f"${det_val * 2}$"}
            explanation = f"Ta có $y' = \\frac{{{det_val}}}{{{denom_sq}}} \\Rightarrow y'({x0}) = {det_val}$."
            steps, exp_time, q_type = 2, 55, "APPLICATION"
        else:
            content = f"{intro} Đạo hàm $y'$ của hàm số với mọi $x \\neq {-d}$ là:"
            options = {
                "A": f"$y' = \\frac{{{det_val}}}{{{denom_sq}}}$",
                "B": f"$y' = \\frac{{{-det_val}}}{{{denom_sq}}}$",
                "C": f"$y' = \\frac{{{a * d + b}}}{{{denom_sq}}}$",
                "D": f"$y' = \\frac{{{a}}}{{{denom_sq}}}$"
            }
            explanation = f"Áp dụng $\\left(\\frac{{ax+b}}{{cx+d}}\\right)' = \\frac{{ad - bc}}{{(cx+d)^2}} = \\frac{{{det_val}}}{{{denom_sq}}}$."
            steps, exp_time, q_type = 2, 50, "ALGORITHMIC"

    elif formula_rule == "DRV_HIGH":
        a = random.choice([1, 2, 3])
        b = random.choice([2, 4, 5])
        poly = a * x_sym**4 - b * x_sym**3 + 3 * x_sym**2 - x_sym + 2
        d1 = sp.diff(poly, x_sym)
        d2 = sp.diff(d1, x_sym)
        intro = _build_stem_intro(sp.latex(poly), "đa thức bậc bốn", stem_style_idx)
        if question_form == "FORM_VAL_POINT":
            x0 = random.choice([1, 2])
            val = int(d2.subs(x_sym, x0))
            content = f"{intro} Giá trị đạo hàm cấp hai $y''({x0})$ bằng:"
            options = {"A": f"${val}$", "B": f"${int(d1.subs(x_sym, x0))}$", "C": f"${val + 6 * a}$", "D": f"${val - 2 * b}$"}
            explanation = f"Ta có $y' = {sp.latex(d1)}$ và $y'' = {sp.latex(d2)}$. Thay $x = {x0}$ thu được $y''({x0}) = {val}$."
            steps, exp_time, q_type = 3, 75, "APPLICATION"
        else:
            content = f"{intro} Biểu thức đạo hàm cấp hai $y''$ của hàm số là:"
            options = {"A": f"$y'' = {sp.latex(d2)}$", "B": f"$y'' = {sp.latex(d1)}$", "C": f"$y'' = {sp.latex(sp.diff(d2, x_sym))}$", "D": f"$y'' = {sp.latex(d2 + 6)}$"}
            explanation = f"Tính hai lần đạo hàm: $y' = {sp.latex(d1)} \\Rightarrow y'' = {sp.latex(d2)}$."
            steps, exp_time, q_type = 2, 65, "ALGORITHMIC"

    elif formula_rule == "DRV_PARAM_TAN":
        a = random.choice([1, 2])
        poly = a * x_sym**3 - 3 * a * x_sym + 1
        k_target = 9 * a
        x0 = 2
        y0 = int(poly.subs(x_sym, x0))
        tang = sp.expand(k_target * (x_sym - x0) + y0)
        tang2 = sp.expand(k_target * (x_sym + x0) + int(poly.subs(x_sym, -x0)))
        intro = _build_stem_intro(sp.latex(poly), "bậc ba", stem_style_idx)
        content = f"{intro} Phương trình tiếp tuyến của $(C)$ có hoành độ tiếp điểm dương và song song với đường thẳng $d: y = {k_target}x + 5$ là:"
        options = {
            "A": f"$y = {sp.latex(tang)}$",
            "B": f"$y = {sp.latex(tang2)}$",
            "C": f"$y = {sp.latex(k_target * x_sym + 5)}$",
            "D": f"$y = {sp.latex(tang + 4)}$"
        }
        explanation = f"Do $\\Delta \\parallel d \\Rightarrow y'(x_0) = {k_target} \\Rightarrow x_0 = 2$ (vì $x_0 > 0$). Suy ra $y_0 = {y0}$, tiếp tuyến $y = {sp.latex(tang)}$."
        steps, exp_time, q_type = 4, 115, "SYNTHESIS"

    elif formula_rule == "DRV_CHAIN":
        a = random.choice([1, 2, 3])
        b = random.choice([2, 4, 6])
        inner = a * x_sym**2 + b
        inner_ltx = sp.latex(inner)
        if question_form == "FORM_VAL_POINT":
            n_pow = 3
            comp_expr = inner**n_pow
            deriv_comp = sp.diff(comp_expr, x_sym)
            x0 = 1
            val = int(deriv_comp.subs(x_sym, x0))
            buggy_no_uprime = int((n_pow * inner**(n_pow - 1)).subs(x_sym, x0))
            c_intro = _build_stem_intro(f"({inner_ltx})^{n_pow}", "hợp", stem_style_idx)
            content = f"{c_intro} Giá trị của đạo hàm $f'(1)$ là:"
            options = {"A": f"${val}$", "B": f"${buggy_no_uprime}$", "C": f"${val // 2}$", "D": f"${int(comp_expr.subs(x_sym, x0))}$"}
            explanation = f"Áp dụng $[u(x)^3]' = 3u^2 \\cdot u'(x)$. Thay $x = 1$ thu được ${val}$."
            steps, exp_time, q_type = 3, 75, "APPLICATION"
        else:
            sqrt_ltx = f"\\sqrt{{{inner_ltx}}}"
            c_intro = _build_stem_intro(sqrt_ltx, "chứa căn thức", stem_style_idx)
            content = f"{c_intro} Đạo hàm của hàm số là:"
            options = {
                "A": f"$y' = \\frac{{{a}x}}{{\\sqrt{{{inner_ltx}}}}}$",
                "B": f"$y' = \\frac{{1}}{{2\\sqrt{{{inner_ltx}}}}}$",
                "C": f"$y' = \\frac{{{2*a}x}}{{\\sqrt{{{inner_ltx}}}}}$",
                "D": f"$y' = \\frac{{{a}}}{{\\sqrt{{{inner_ltx}}}}}$"
            }
            explanation = f"Áp dụng $(\\sqrt{{u}})' = \\frac{{u'}}{{2\\sqrt{{u}}}} = \\frac{{{a}x}}{{\\sqrt{{{inner_ltx}}}}}$."
            steps, exp_time, q_type = 2, 55, "ALGORITHMIC"

    elif formula_rule == "DRV_TRIG":
        k = random.choice([2, 3, 4, 5])
        trig_type = (seed_offset + stem_style_idx) % 3
        if trig_type == 0:
            expr_latex = f"\\sin({k}x)"
            ans_A, ans_B, ans_C, ans_D = f"$y' = {k}\\cos({k}x)$", f"$y' = \\cos({k}x)$", f"$y' = -{k}\\cos({k}x)$", f"$y' = {k}\\sin({k}x)$"
            exp_txt = f"Áp dụng $(\\sin u)' = u'\\cos u \\Rightarrow y' = {k}\\cos({k}x)$."
        elif trig_type == 1:
            expr_latex = f"\\cos({k}x)"
            ans_A, ans_B, ans_C, ans_D = f"$y' = -{k}\\sin({k}x)$", f"$y' = {k}\\sin({k}x)$", f"$y' = -\\sin({k}x)$", f"$y' = -{k}\\cos({k}x)$"
            exp_txt = f"Áp dụng $(\\cos u)' = -u'\\sin u \\Rightarrow y' = -{k}\\sin({k}x)$."
        else:
            expr_latex = f"\\tan({k}x)"
            ans_A, ans_B, ans_C, ans_D = f"$y' = \\frac{{{k}}}{{\\cos^2({k}x)}}$", f"$y' = \\frac{{1}}{{\\cos^2({k}x)}}$", f"$y' = -\\frac{{{k}}}{{\\sin^2({k}x)}}$", f"$y' = {k}\\cot({k}x)$"
            exp_txt = f"Áp dụng $(\\tan u)' = \\frac{{u'}}{{\\cos^2 u}} \\Rightarrow y' = \\frac{{{k}}}{{\\cos^2({k}x)}}$."
        t_intro = _build_stem_intro(expr_latex, "lượng giác", stem_style_idx)
        content = f"{t_intro} Đạo hàm của hàm số trên tập xác định là:"
        options = {"A": ans_A, "B": ans_B, "C": ans_C, "D": ans_D}
        explanation = exp_txt
        steps, exp_time, q_type = 1, 35, "THEORY"

    elif formula_rule == "DRV_EXP":
        base_a = random.choice([2, 3, 5, 7])
        k = random.choice([2, 3, 4])
        if question_form == "FORM_VAL_POINT":
            expr_latex = f"e^{{{k}x - {k}}}"
            e_intro = _build_stem_intro(expr_latex, "mũ tự nhiên", stem_style_idx)
            content = f"{e_intro} Giá trị của đạo hàm $f'(1)$ bằng:"
            options = {"A": f"${k}$", "B": "$1$", "C": f"${k}e$", "D": "$0$"}
            explanation = f"Ta có $f'(x) = {k}e^{{{k}x - {k}}} \\Rightarrow f'(1) = {k}$."
            steps, exp_time, q_type = 2, 50, "ALGORITHMIC"
        else:
            expr_latex = f"{base_a}^{{{k}x + 1}}"
            e_intro = _build_stem_intro(expr_latex, "mũ", stem_style_idx)
            content = f"{e_intro} Biểu thức đạo hàm $y'$ là:"
            options = {
                "A": f"$y' = {k} \\cdot {base_a}^{{{k}x + 1}} \\ln {base_a}$",
                "B": f"$y' = {base_a}^{{{k}x + 1}} \\ln {base_a}$",
                "C": f"$y' = {k} \\cdot {base_a}^{{{k}x + 1}}$",
                "D": f"$y' = \\frac{{{base_a}^{{{k}x + 1}}}}{{\\ln {base_a}}}$"
            }
            explanation = f"Áp dụng $(a^u)' = u' \\cdot a^u \\ln a$ với $a = {base_a}, u = {k}x + 1$."
            steps, exp_time, q_type = 2, 50, "ALGORITHMIC"

    elif formula_rule == "DRV_LOG":
        k = random.choice([2, 4, 6])
        m = random.choice([3, 5, 7])
        u_inner = x_sym**2 + k * x_sym + m
        u_prime = sp.diff(u_inner, x_sym)
        expr_latex = f"\\ln({sp.latex(u_inner)})"
        intro = _build_stem_intro(expr_latex, "logarit", stem_style_idx)
        content = f"{intro} Đạo hàm của hàm số trên tập xác định là:"
        options = {
            "A": f"$y' = \\frac{{{sp.latex(u_prime)}}}{{{sp.latex(u_inner)}}}$",
            "B": f"$y' = \\frac{{1}}{{{sp.latex(u_inner)}}}$",
            "C": f"$y' = ({sp.latex(u_prime)})\\ln({sp.latex(u_inner)})$",
            "D": f"$y' = \\frac{{2x}}{{{sp.latex(u_inner)}}}$"
        }
        explanation = f"Áp dụng $(\\ln u)' = \\frac{{u'}}{{u}}$ với $u = {sp.latex(u_inner)}$."
        steps, exp_time, q_type = 2, 55, "ALGORITHMIC"

    elif formula_rule == "DRV_EXTREMA":
        r1 = random.choice([1, 2])
        poly = x_sym**3 - 3 * r1 * x_sym**2 + 4
        d1 = sp.diff(poly, x_sym)
        intro = _build_stem_intro(sp.latex(poly), "bậc ba", stem_style_idx)
        if question_form == "FORM_FUNC_PROP":
            content = f"Tìm tất cả giá trị của tham số $m$ để hàm số $y = \\frac{{1}}{{3}}x^3 - mx^2 + (m + 2)x - 1$ đồng biến trên $\\mathbb{{R}}$."
            options = {"A": "$-1 \\le m \\le 2$", "B": "$m < -1$ hoặc $m > 2$", "C": "$-2 \\le m \\le 1$", "D": "$m \\ge 2$"}
            explanation = "Ta có $y' = x^2 - 2mx + m + 2 \\ge 0, \\forall x \\in \\mathbb{R} \\Leftrightarrow \\Delta' = m^2 - m - 2 \\le 0 \\Leftrightarrow -1 \\le m \\le 2$."
            steps, exp_time, q_type = 4, 120, "SYNTHESIS"
        else:
            content = f"{intro} Hàm số đã cho nghịch biến trên khoảng nào dưới đây?"
            options = {"A": f"$(0; {2 * r1})$", "B": f"$(-\\infty; 0)$", "C": f"$({2 * r1}; +\\infty)$", "D": f"$(-{r1}; {r1})$"}
            explanation = f"Ta có $y' = {sp.latex(d1)} = 3x(x - {2 * r1}) < 0 \\Leftrightarrow 0 < x < {2 * r1}$."
            steps, exp_time, q_type = 3, 75, "APPLICATION"

    elif formula_rule in ["INT_POW", "INT_LINEAR"]:
        a = random.choice([3, 6, 9])
        b = random.choice([2, 4, 8])
        c = random.choice([1, 3, 5])
        f_expr = a * x_sym**2 - b * x_sym + c
        F_expr = sp.integrate(f_expr, x_sym)
        deriv_wrong = sp.diff(f_expr, x_sym)
        if question_form == "FORM_VAL_POINT":
            c0 = random.choice([2, 4, 5])
            val_at_1 = int(F_expr.subs(x_sym, 1)) + c0
            content = f"Cho hàm số $f(x) = {sp.latex(f_expr)}$. Biết $F(x)$ là một nguyên hàm của $f(x)$ thỏa mãn $F(0) = {c0}$. Giá trị của $F(1)$ bằng:"
            options = {"A": f"${val_at_1}$", "B": f"${val_at_1 - c0}$", "C": f"${val_at_1 + 2}$", "D": f"${int(f_expr.subs(x_sym, 1)) + c0}$"}
            explanation = f"Ta có $F(x) = {sp.latex(F_expr)} + C \\Rightarrow C = {c0} \\Rightarrow F(1) = {val_at_1}$."
            steps, exp_time, q_type = 3, 75, "APPLICATION"
        else:
            content = f"Họ tất cả các nguyên hàm của hàm số $f(x) = {sp.latex(f_expr)}$ trên $\\mathbb{{R}}$ là:"
            options = {
                "A": f"$F(x) = {sp.latex(F_expr)} + C$",
                "B": f"$F(x) = {sp.latex(deriv_wrong)} + C$",
                "C": f"$F(x) = {sp.latex(F_expr + x_sym**2)} + C$",
                "D": f"$F(x) = {sp.latex(a * x_sym**3 - b * x_sym**2 + c * x_sym)} + C$"
            }
            explanation = f"Áp dụng $\\int x^n dx = \\frac{{x^{{n+1}}}}{{n+1}} + C$, ta được $F(x) = {sp.latex(F_expr)} + C$."
            steps, exp_time, q_type = 1, 40, "THEORY"

    elif formula_rule == "INT_TRIG_EXP":
        k = random.choice([2, 3, 4])
        content = f"Họ nguyên hàm của hàm số $f(x) = e^{{{k}x}} + \\cos({k}x)$ trên $\\mathbb{{R}}$ là:"
        options = {
            "A": f"$F(x) = \\frac{{1}}{{{k}}}e^{{{k}x}} + \\frac{{1}}{{{k}}}\\sin({k}x) + C$",
            "B": f"$F(x) = {k}e^{{{k}x}} - {k}\\sin({k}x) + C$",
            "C": f"$F(x) = e^{{{k}x}} + \\sin({k}x) + C$",
            "D": f"$F(x) = \\frac{{1}}{{{k}}}e^{{{k}x}} - \\frac{{1}}{{{k}}}\\sin({k}x) + C$"
        }
        explanation = f"Áp dụng $\\int e^{{kx}}dx = \\frac{{1}}{{k}}e^{{kx}}$ và $\\int \\cos(kx)dx = \\frac{{1}}{{k}}\\sin(kx) + C$."
        steps, exp_time, q_type = 2, 50, "ALGORITHMIC"

    elif formula_rule == "INT_SUBST":
        n_p = random.choice([4, 5, 6])
        k = random.choice([2, 3])
        inner = x_sym**2 + k
        content = f"Tìm họ nguyên hàm $I = \\int 2x({sp.latex(inner)})^{n_p} dx$ bằng phương pháp đổi biến số:"
        options = {
            "A": f"$I = \\frac{{({sp.latex(inner)})^{{{n_p + 1}}}}}{{{n_p + 1}}} + C$",
            "B": f"$I = \\frac{{({sp.latex(inner)})^{{{n_p + 1}}}}}{{{2 * (n_p + 1)}}} + C$",
            "C": f"$I = {n_p}({sp.latex(inner)})^{{{n_p - 1}}} + C$",
            "D": f"$I = \\frac{{({sp.latex(inner)})^{{{n_p}}}}}{{{n_p}}} + C$"
        }
        explanation = f"Đặt $u = {sp.latex(inner)} \\Rightarrow du = 2xdx \\Rightarrow I = \\frac{{u^{{{n_p + 1}}}}}{{{n_p + 1}}} + C$."
        steps, exp_time, q_type = 3, 80, "APPLICATION"

    elif formula_rule == "INT_PARTS":
        k = random.choice([1, 2, 3])
        content = f"Sử dụng phương pháp nguyên hàm từng phần, tìm họ nguyên hàm $F(x) = \\int (x + {k})e^x dx$:"
        options = {
            "A": f"$F(x) = (x + {k - 1})e^x + C$",
            "B": f"$F(x) = (x + {k + 1})e^x + C$",
            "C": f"$F(x) = (x + {k})e^x + C$",
            "D": f"$F(x) = ({k}x + 1)e^x + C$"
        }
        explanation = f"Đặt $u = x + {k}, dv = e^x dx \\Rightarrow F(x) = (x + {k - 1})e^x + C$."
        steps, exp_time, q_type = 3, 90, "APPLICATION"

    else:
        a = random.choice([2, 3, 5])
        b = random.choice([1, 4, 7])
        content = f"Họ nguyên hàm của hàm số $f(x) = \\frac{{1}}{{{a}x + {b}}}$ trên khoảng $\\left(-\\frac{{{b}}}{{{a}}}; +\\infty\\right)$ là:"
        options = {
            "A": f"$F(x) = \\frac{{1}}{{{a}}}\\ln|{a}x + {b}| + C$",
            "B": f"$F(x) = \\ln|{a}x + {b}| + C$",
            "C": f"$F(x) = {a}\\ln|{a}x + {b}| + C$",
            "D": f"$F(x) = -\\frac{{{a}}}{{({a}x + {b})^2}} + C$"
        }
        explanation = f"Áp dụng $\\int \\frac{{dx}}{{ax + b}} = \\frac{{1}}{{a}}\\ln|ax + b| + C$."
        steps, exp_time, q_type = 2, 55, "ALGORITHMIC"

    diff_label, irt_b, trace = infer_question_difficulty(content, q_type, steps, expected_time=exp_time)
    trace["applied_transform_rule"] = f"R_TRANS_STEM (Mẫu #{(stem_style_idx % 6) + 1}) + R_BUGGY_GEN"

    return {
        "subject": subject,
        "topic": topic,
        "concept_node": concept_node,
        "formula_rule": formula_rule,
        "question_form": question_form,
        "q_type": q_type,
        "steps": steps,
        "difficulty": diff_label,
        "irt_b": irt_b,
        "irt_a": 1.25,
        "expected_time": exp_time,
        "attempts": random.randint(10, 28),
        "correct_rate": round(random.uniform(0.32, 0.85), 2),
        "avg_time": exp_time + random.randint(-6, 14),
        "content": content,
        "options": options,
        "answer": "A",
        "general_method": general_method,
        "explanation": explanation,
        "rule_trace": trace
    }

def _seed_initial_knowledge():
    seed_specs = [
        ("MATH_DERIV_01", "DRV_POW", "FORM_EXPR", 0),
        ("MATH_DERIV_01", "DRV_POW", "FORM_VAL_POINT", 1),
        ("MATH_DERIV_01", "DRV_POW", "FORM_TANGENT_SLOPE", 2),
        ("MATH_DERIV_01", "DRV_POW", "FORM_TANGENT_EQ", 3),
        ("MATH_DERIV_01", "DRV_PROD", "FORM_EXPR", 0),
        ("MATH_DERIV_01", "DRV_QUOT", "FORM_EXPR", 2),
        ("MATH_DERIV_01", "DRV_HIGH", "FORM_HIGH_ORDER", 4),
        ("MATH_DERIV_01", "DRV_PARAM_TAN", "FORM_TANGENT_EQ", 5),
        ("MATH_DERIV_02", "DRV_CHAIN", "FORM_EXPR", 0),
        ("MATH_DERIV_02", "DRV_TRIG", "FORM_EXPR", 1),
        ("MATH_DERIV_02", "DRV_EXP", "FORM_EXPR", 2),
        ("MATH_DERIV_02", "DRV_LOG", "FORM_EXPR", 0),
        ("MATH_DERIV_02", "DRV_EXTREMA", "FORM_MONOTONIC", 1),
        ("MATH_INTEG_01", "INT_POW", "FORM_EXPR", 0),
        ("MATH_INTEG_01", "INT_LINEAR", "FORM_VAL_POINT", 1),
        ("MATH_INTEG_01", "INT_TRIG_EXP", "FORM_EXPR", 3),
        ("MATH_INTEG_01", "INT_SUBST", "FORM_EXPR", 4),
        ("MATH_INTEG_01", "INT_PARTS", "FORM_EXPR", 5),
        ("MATH_INTEG_01", "INT_FRAC", "FORM_EXPR", 0),
        ("CHEM_BAL_01", "BAL_ATOM", "FORM_CHEM_COEFF", 0),
        ("CHEM_BAL_01", "BAL_GROUP", "FORM_CHEM_COEFF", 1),
        ("CHEM_BAL_01", "BAL_ALGEBRA", "FORM_CHEM_COEFF", 2),
        ("CHEM_BAL_01", "BAL_ION", "FORM_CHEM_COEFF", 3),
        ("CHEM_BAL_02", "BAL_REDOX_STD", "FORM_CHEM_RATIO", 0),
        ("CHEM_BAL_02", "BAL_REDOX_ENV", "FORM_CHEM_RATIO", 1),
        ("CHEM_BAL_02", "BAL_REDOX_SELF", "FORM_CHEM_RATIO", 2),
        ("CHEM_BAL_02", "BAL_REDOX_MULTI", "FORM_CHEM_COEFF", 3),
        ("CHEM_REACT_01", "REACT_TYPE_4", "FORM_CHEM_CLASS", 0),
        ("CHEM_REACT_01", "REACT_REDOX_ID", "FORM_CHEM_CLASS", 1),
        ("CHEM_REACT_01", "REACT_EXCHANGE_COND", "FORM_CHEM_PRODUCT", 2),
        ("CHEM_REACT_01", "REACT_ELECTROCHEM", "FORM_CHEM_PRODUCT", 3)
    ]
    questions = []
    m_idx, c_idx = 1, 1
    for idx, (node, f_rule, q_form, style) in enumerate(seed_specs):
        q = generate_question_by_rule_and_sympy(node, f_rule, q_form, "TRUNG_BINH", style, seed_offset=idx * 7)
        q.pop("rule_trace", None)
        if q["subject"] == "MATH":
            q["id"] = f"Q_MATH_{m_idx:03d}"
            m_idx += 1
        else:
            q["id"] = f"Q_CHEM_{c_idx:03d}"
            c_idx += 1
        questions.append(q)
    return {"questions": questions}

def load_knowledge_base() -> dict:
    if not os.path.exists(KNOWLEDGE_FILE):
        kb = _seed_initial_knowledge()
        save_knowledge_base(kb)
        return kb
    try:
        with open(KNOWLEDGE_FILE, "r", encoding="utf-8") as f:
            kb = json.load(f)
            kb.setdefault("questions", [])
            for q in kb["questions"]:
                q.setdefault("formula_rule", "DRV_POW" if q["subject"] == "MATH" else "BAL_ATOM")
                q.setdefault("question_form", "FORM_EXPR" if q["subject"] == "MATH" else "FORM_CHEM_COEFF")
                if "general_method" not in q:
                    q["general_method"] = Script_Login.get_formula_rule_info(q["formula_rule"])["general_method"]
            return kb
    except Exception:
        kb = _seed_initial_knowledge()
        save_knowledge_base(kb)
        return kb

def save_knowledge_base(kb: dict):
    with open(KNOWLEDGE_FILE, "w", encoding="utf-8") as f:
        json.dump({"questions": kb.get("questions", [])}, f, ensure_ascii=False, indent=2)

def filter_questions(subject="ALL", concept_node="ALL", formula_rule="ALL", question_form="ALL", difficulty="ALL", keyword=""):
    kb = load_knowledge_base()
    result = []
    kw = keyword.strip().lower()
    for q in kb["questions"]:
        if subject != "ALL" and q["subject"] != subject:
            continue
        if concept_node != "ALL" and q.get("concept_node") != concept_node:
            continue
        if formula_rule != "ALL" and q.get("formula_rule") != formula_rule:
            continue
        if question_form != "ALL" and q.get("question_form") != question_form:
            continue
        if difficulty != "ALL" and q["difficulty"] != difficulty:
            continue
        if kw and (kw not in q["content"].lower() and kw not in q["id"].lower()):
            continue
        result.append(q)
    return result

def add_manual_question(q_data: dict):
    if not q_data.get("content") or not all(q_data.get("options", {}).values()):
        return False, "Vui lòng nhập đầy đủ đề bài và 4 phương án A, B, C, D.", "N/A"

    kb = load_knowledge_base()
    sub = q_data["subject"]
    existing_ids = [
        int(x["id"].split("_")[-1])
        for x in kb["questions"]
        if x["subject"] == sub and x["id"].split("_")[-1].isdigit()
    ]
    next_idx = (max(existing_ids) + 1) if existing_ids else 1
    q_id = f"Q_{sub}_{next_idx:03d}"

    diff_label, irt_b, _ = infer_question_difficulty(
        content=q_data["content"],
        q_type=q_data["q_type"],
        steps=int(q_data["steps"]),
        expected_time=int(q_data["expected_time"])
    )

    f_rule = q_data.get("formula_rule", "DRV_POW" if sub == "MATH" else "BAL_ATOM")
    gen_method = q_data.get("general_method") or Script_Login.get_formula_rule_info(f_rule)["general_method"]

    new_frame = {
        "id": q_id,
        "subject": sub,
        "topic": q_data["topic"],
        "concept_node": q_data["concept_node"],
        "formula_rule": f_rule,
        "question_form": q_data.get("question_form", "FORM_EXPR" if sub == "MATH" else "FORM_CHEM_COEFF"),
        "q_type": q_data["q_type"],
        "steps": int(q_data["steps"]),
        "difficulty": diff_label,
        "irt_b": irt_b,
        "irt_a": 1.25,
        "expected_time": int(q_data["expected_time"]),
        "attempts": 0,
        "correct_rate": 0.5,
        "avg_time": int(q_data["expected_time"]),
        "content": q_data["content"].strip(),
        "options": q_data["options"],
        "answer": q_data["answer"],
        "general_method": gen_method,
        "explanation": q_data.get("explanation") or gen_method
    }
    kb["questions"].insert(0, new_frame)
    save_knowledge_base(kb)
    return True, f"Đã thêm câu hỏi {q_id} vào Knowledge.txt", f"{diff_label} (b={irt_b})"

def update_question(q_id: str, updated_data: dict):
    kb = load_knowledge_base()
    for idx, q in enumerate(kb["questions"]):
        if q["id"] == q_id:
            q["concept_node"] = updated_data.get("concept_node", q["concept_node"])
            nodes = Script_Login.get_all_concept_nodes()
            if q["concept_node"] in nodes:
                q["subject"] = nodes[q["concept_node"]]["subject"]
                q["topic"] = nodes[q["concept_node"]]["topic"]
            q["formula_rule"] = updated_data.get("formula_rule", q.get("formula_rule"))
            q["question_form"] = updated_data.get("question_form", q.get("question_form"))
            q["difficulty"] = updated_data.get("difficulty", q["difficulty"])
            q["expected_time"] = int(updated_data.get("expected_time", q["expected_time"]))
            q["content"] = updated_data.get("content", q["content"]).strip()
            q["options"] = updated_data.get("options", q["options"])
            q["answer"] = updated_data.get("answer", q["answer"])
            q["general_method"] = updated_data.get("general_method", q.get("general_method", ""))
            q["explanation"] = updated_data.get("explanation", q.get("explanation", ""))
            kb["questions"][idx] = q
            save_knowledge_base(kb)
            return True, f"Đã cập nhật câu hỏi {q_id} thành công."
    return False, f"Không tìm thấy câu hỏi {q_id}."

def delete_question(q_id: str):
    kb = load_knowledge_base()
    before = len(kb["questions"])
    kb["questions"] = [q for q in kb["questions"] if q["id"] != q_id]
    if len(kb["questions"]) < before:
        save_knowledge_base(kb)
        return True, f"Đã xóa câu hỏi {q_id} khỏi Knowledge.txt."
    return False, f"Không tìm thấy mã câu hỏi {q_id}."

def commit_generated_question(gen_q: dict):
    return add_manual_question(gen_q)[:2]

def expand_knowledge_base_to_200():
    kb = load_knowledge_base()
    existing = kb["questions"]
    math_qs = [q for q in existing if q["subject"] == "MATH"]
    chem_qs = [q for q in existing if q["subject"] == "CHEM"]

    math_blueprint = [
        ("MATH_DERIV_01", "DRV_POW", "FORM_EXPR"),
        ("MATH_DERIV_01", "DRV_POW", "FORM_VAL_POINT"),
        ("MATH_DERIV_01", "DRV_POW", "FORM_TANGENT_SLOPE"),
        ("MATH_DERIV_01", "DRV_POW", "FORM_TANGENT_EQ"),
        ("MATH_DERIV_01", "DRV_POW", "FORM_SOLVE_COND"),
        ("MATH_DERIV_01", "DRV_PROD", "FORM_EXPR"),
        ("MATH_DERIV_01", "DRV_PROD", "FORM_VAL_POINT"),
        ("MATH_DERIV_01", "DRV_QUOT", "FORM_EXPR"),
        ("MATH_DERIV_01", "DRV_QUOT", "FORM_TANGENT_SLOPE"),
        ("MATH_DERIV_01", "DRV_HIGH", "FORM_HIGH_ORDER"),
        ("MATH_DERIV_01", "DRV_HIGH", "FORM_VAL_POINT"),
        ("MATH_DERIV_01", "DRV_PARAM_TAN", "FORM_TANGENT_EQ"),
        ("MATH_DERIV_02", "DRV_CHAIN", "FORM_EXPR"),
        ("MATH_DERIV_02", "DRV_CHAIN", "FORM_VAL_POINT"),
        ("MATH_DERIV_02", "DRV_TRIG", "FORM_EXPR"),
        ("MATH_DERIV_02", "DRV_EXP", "FORM_EXPR"),
        ("MATH_DERIV_02", "DRV_EXP", "FORM_VAL_POINT"),
        ("MATH_DERIV_02", "DRV_LOG", "FORM_EXPR"),
        ("MATH_DERIV_02", "DRV_EXTREMA", "FORM_MONOTONIC"),
        ("MATH_DERIV_02", "DRV_EXTREMA", "FORM_FUNC_PROP"),
        ("MATH_INTEG_01", "INT_POW", "FORM_EXPR"),
        ("MATH_INTEG_01", "INT_LINEAR", "FORM_VAL_POINT"),
        ("MATH_INTEG_01", "INT_TRIG_EXP", "FORM_EXPR"),
        ("MATH_INTEG_01", "INT_SUBST", "FORM_EXPR"),
        ("MATH_INTEG_01", "INT_PARTS", "FORM_EXPR"),
        ("MATH_INTEG_01", "INT_FRAC", "FORM_EXPR")
    ]

    chem_blueprint = [
        ("CHEM_BAL_01", "BAL_ATOM", "FORM_CHEM_COEFF"),
        ("CHEM_BAL_01", "BAL_GROUP", "FORM_CHEM_COEFF"),
        ("CHEM_BAL_01", "BAL_GROUP", "FORM_CHEM_PRODUCT"),
        ("CHEM_BAL_01", "BAL_ALGEBRA", "FORM_CHEM_COEFF"),
        ("CHEM_BAL_01", "BAL_ION", "FORM_CHEM_COEFF"),
        ("CHEM_BAL_02", "BAL_REDOX_STD", "FORM_CHEM_RATIO"),
        ("CHEM_BAL_02", "BAL_REDOX_ENV", "FORM_CHEM_RATIO"),
        ("CHEM_BAL_02", "BAL_REDOX_ENV", "FORM_CHEM_COEFF"),
        ("CHEM_BAL_02", "BAL_REDOX_SELF", "FORM_CHEM_RATIO"),
        ("CHEM_BAL_02", "BAL_REDOX_MULTI", "FORM_CHEM_COEFF"),
        ("CHEM_REACT_01", "REACT_TYPE_4", "FORM_CHEM_CLASS"),
        ("CHEM_REACT_01", "REACT_REDOX_ID", "FORM_CHEM_CLASS"),
        ("CHEM_REACT_01", "REACT_EXCHANGE_COND", "FORM_CHEM_PRODUCT"),
        ("CHEM_REACT_01", "REACT_ELECTROCHEM", "FORM_CHEM_PRODUCT")
    ]

    while len(math_qs) < 100:
        idx = len(math_qs) + 1
        node, f_rule, q_form = math_blueprint[idx % len(math_blueprint)]
        q = generate_question_by_rule_and_sympy(node, f_rule, q_form, stem_style_idx=idx % 6, seed_offset=idx * 3)
        q.pop("rule_trace", None)
        q["id"] = f"Q_MATH_{idx:03d}"
        math_qs.append(q)

    while len(chem_qs) < 100:
        idx = len(chem_qs) + 1
        node, f_rule, q_form = chem_blueprint[idx % len(chem_blueprint)]
        q = generate_question_by_rule_and_sympy(node, f_rule, q_form, stem_style_idx=idx % 4, seed_offset=idx * 13)
        q.pop("rule_trace", None)
        q["id"] = f"Q_CHEM_{idx:03d}"
        chem_qs.append(q)

    kb["questions"] = math_qs + chem_qs
    save_knowledge_base(kb)
    return len(kb["questions"])

def generate_demo_exam(subject: str, num_questions: int, difficulty_mode: str):
    pool = filter_questions(subject=subject)
    if difficulty_mode != "CAN_BANG":
        exact = [q for q in pool if q["difficulty"] == difficulty_mode]
        others = [q for q in pool if q["difficulty"] != difficulty_mode]
        selected = exact[:num_questions]
        if len(selected) < num_questions:
            selected.extend(others[:num_questions - len(selected)])
        return selected

    quotas = {"DE": 0.25, "TRUNG_BINH": 0.35, "KHA": 0.25, "KHO": 0.15}
    selected = []
    used_ids = set()
    for diff, ratio in quotas.items():
        need = max(1, round(num_questions * ratio))
        candidates = [q for q in pool if q["difficulty"] == diff and q["id"] not in used_ids]
        for c in candidates[:need]:
            selected.append(c)
            used_ids.add(c["id"])

    for q in pool:
        if len(selected) >= num_questions:
            break
        if q["id"] not in used_ids:
            selected.append(q)
            used_ids.add(q["id"])
    return selected[:num_questions]

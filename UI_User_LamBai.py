import time
import streamlit as st
import streamlit.components.v1 as components
import Script_User_LamBai
import Script_Login

def _commit_question_elapsed(exam: dict):
    questions = exam["questions"]
    cur_idx = exam.get("current_q_idx", 0)
    if 0 <= cur_idx < len(questions):
        cur_qid = questions[cur_idx]["id"]
        now_ts = time.time()
        enter_ts = exam.get("question_enter_ts", now_ts)
        elapsed = max(0.0, now_ts - enter_ts)
        exam.setdefault("question_times", {})
        exam["question_times"][cur_qid] = exam["question_times"].get(cur_qid, 0.0) + elapsed
    exam["question_enter_ts"] = time.time()

def _render_live_timers(
    exam_start_ts: float,
    question_enter_ts: float,
    question_accumulated_sec: float,
    expected_total_sec: int,
    expected_q_sec: int,
    exam_id: str,
    cur_num: int,
    total_q: int,
    sub_vi: str
):
    exam_start_ms = int(exam_start_ts * 1000)
    q_enter_ms = int(question_enter_ts * 1000)
    q_acc_ms = int(question_accumulated_sec * 1000)
    html_code = f"""
    <div style="font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                background: #FFFFFF; border: 1px solid #CBD5E1; border-top: 3px solid #124874;
                border-radius: 4px; padding: 10px 16px; display: flex;
                justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
        <div style="font-size: 13px; color: #0F172A;">
            <span style="background:#124874; color:#FFF; padding:3px 8px; border-radius:3px; font-weight:600; margin-right:6px;">{exam_id}</span>
            <span style="border:1px solid #124874; color:#124874; padding:2px 8px; border-radius:3px; margin-right:6px;">{sub_vi}</span>
            <span style="border:1px solid #124874; color:#124874; padding:2px 8px; border-radius:3px;">Câu {cur_num:02d}/{total_q:02d}</span>
        </div>
        <div style="display:flex; align-items:center; gap: 12px;">
            <div style="background: #F8FAFC; border: 1px solid #CBD5E1; color: #124874; padding: 5px 10px; border-radius: 3px;
                        font-weight: 600; font-size: 13px;">
                Câu này: <span id="kbs-q-clock">00:00</span> <span style="font-weight:400; color:#64748B;">/ {expected_q_sec}s</span>
            </div>
            <div style="background: #CF373D; color: #FFFFFF; padding: 5px 12px; border-radius: 3px;
                        font-weight: 700; font-size: 13px; letter-spacing: 0.03em;">
                Tổng: <span id="kbs-total-clock">00:00</span> <span style="font-weight:400; opacity:0.85;">/ {expected_total_sec // 60:02d}:{expected_total_sec % 60:02d}</span>
            </div>
        </div>
    </div>
    <script>
        (function() {{
            const examStartMs = {exam_start_ms};
            const qEnterMs = {q_enter_ms};
            const qAccMs = {q_acc_ms};
            const totalEl = document.getElementById("kbs-total-clock");
            const qEl = document.getElementById("kbs-q-clock");
            function fmt(sec) {{
                const m = String(Math.floor(sec / 60)).padStart(2, '0');
                const s = String(sec % 60).padStart(2, '0');
                return m + ":" + s;
            }}
            function tick() {{
                const now = Date.now();
                if (totalEl) {{
                    totalEl.textContent = fmt(Math.max(0, Math.floor((now - examStartMs) / 1000)));
                }}
                if (qEl) {{
                    qEl.textContent = fmt(Math.max(0, Math.floor((qAccMs + (now - qEnterMs)) / 1000)));
                }}
            }}
            tick();
            setInterval(tick, 1000);
        }})();
    </script>
    """
    components.html(html_code, height=64)

def render():
    exam = st.session_state.get("active_exam")
    result = st.session_state.get("exam_result")

    if result:
        render_exam_result(result)
        return

    if not exam:
        st.info("Chưa có đề thi đang mở.")
        if st.button("Tạo đề luyện tập", type="primary"):
            st.session_state.current_page = "USR_TAOBAI"
            st.rerun()
        return

    now_ts = time.time()
    if "exam_start_ts" not in exam:
        exam["exam_start_ts"] = now_ts
    if "current_q_idx" not in exam:
        exam["current_q_idx"] = 0
    if "question_times" not in exam:
        exam["question_times"] = {}
    if "user_answers" not in exam:
        exam["user_answers"] = {}
    if "question_enter_ts" not in exam:
        exam["question_enter_ts"] = now_ts

    questions = exam["questions"]
    cur_idx = exam["current_q_idx"]
    q = questions[cur_idx]
    qid = q["id"]

    diff_names = {"DE": "Dễ", "TRUNG_BINH": "Trung bình", "KHA": "Khá", "KHO": "Khó"}
    sub_vi = "Toán học" if exam["subject"] == "MATH" else "Hóa học"

    _render_live_timers(
        exam_start_ts=exam["exam_start_ts"],
        question_enter_ts=exam["question_enter_ts"],
        question_accumulated_sec=exam["question_times"].get(qid, 0.0),
        expected_total_sec=int(exam["total_expected_time"]),
        expected_q_sec=int(q.get("expected_time", 45)),
        exam_id=exam["exam_id"],
        cur_num=cur_idx + 1,
        total_q=len(questions),
        sub_vi=sub_vi
    )

    # Thanh điều hướng từng câu (cho phép nhảy qua lại nhưng vẫn đo thời gian từng câu chính xác)
    nav_cols = st.columns(min(len(questions), 10))
    for i in range(len(questions)):
        col_i = nav_cols[i % len(nav_cols)]
        q_item_id = questions[i]["id"]
        is_answered = exam["user_answers"].get(q_item_id) is not None
        label = f"{i+1:02d} ✓" if is_answered else f"{i+1:02d}"
        btn_type = "primary" if i == cur_idx else "secondary"
        with col_i:
            if st.button(label, key=f"qnav_{i}", type=btn_type, use_container_width=True):
                _commit_question_elapsed(exam)
                exam["current_q_idx"] = i
                st.rerun()

    st.markdown("<div style='height:0.4rem;'></div>", unsafe_allow_html=True)

    node_name = Script_Login.get_concept_name(q["concept_node"])
    f_info = Script_Login.get_formula_rule_info(q.get("formula_rule", "DRV_POW"))
    diff_vi = diff_names.get(q["difficulty"], q["difficulty"])

    st.markdown(
        f'<div class="kbs-box" style="padding:0.6rem 1rem; margin-bottom:0.65rem;">'
        f'<div style="display:flex; justify-content:space-between; flex-wrap:wrap; gap:6px;">'
        f'<div><span class="badge-blue">Câu {cur_idx + 1:02d}</span>'
        f'<span class="badge-outline">{node_name}</span>'
        f'<span class="badge-outline">{f_info["name"]}</span></div>'
        f'<div><span class="badge-red">{diff_vi}</span>'
        f'<span class="badge-outline">Định mức: {q["expected_time"]}s</span></div>'
        f'</div></div>',
        unsafe_allow_html=True
    )

    st.markdown(f"**{q['content']}**")

    saved_ans = exam["user_answers"].get(qid)
    opts = ["A", "B", "C", "D"]
    default_index = opts.index(saved_ans) if saved_ans in opts else None

    choice = st.radio(
        f"Đáp án Câu {cur_idx + 1:02d}:",
        options=opts,
        format_func=lambda opt, q_obj=q: f"**{opt}.** {q_obj['options'][opt]}",
        key=f"radio_q_{qid}_{cur_idx}",
        index=default_index,
        label_visibility="collapsed"
    )
    if choice is not None:
        exam["user_answers"][qid] = choice

    st.markdown("<hr style='margin:1rem 0; border:none; border-top:1px solid #E2E8F0;'>", unsafe_allow_html=True)

    c_prev, c_next, c_submit = st.columns([1, 1, 1.4])
    with c_prev:
        if cur_idx > 0:
            if st.button("← Câu trước", type="secondary", use_container_width=True):
                _commit_question_elapsed(exam)
                exam["current_q_idx"] = cur_idx - 1
                st.rerun()
    with c_next:
        if cur_idx < len(questions) - 1:
            if st.button("Câu tiếp theo →", type="secondary", use_container_width=True):
                _commit_question_elapsed(exam)
                exam["current_q_idx"] = cur_idx + 1
                st.rerun()
    with c_submit:
        if st.button("Nộp bài & Chấm điểm", type="primary", use_container_width=True):
            _commit_question_elapsed(exam)
            total_duration = max(1, int(time.time() - exam["exam_start_ts"]))
            eval_res = Script_User_LamBai.grade_and_update_knowledge_state(
                username=st.session_state.username,
                exam=exam,
                user_answers=exam["user_answers"],
                total_duration=total_duration,
                question_times=exam["question_times"]
            )
            st.session_state.exam_result = eval_res
            st.session_state.active_exam = None
            st.rerun()

def render_exam_result(result):
    s_before = Script_Login.theta_to_score100(result["theta_before"])
    s_after = Script_Login.theta_to_score100(result["theta_after"])
    s_delta = s_after - s_before
    delta_sign = "+" if s_delta >= 0 else ""

    st.markdown(
        f'<div class="kpi-grid">'
        f'<div class="kpi-card"><div class="stat-label">Điểm số</div><div class="stat-value-blue">{result["score_10"]}/10</div><div class="stat-sub">Đúng {result["correct_count"]}/{result["total_questions"]} câu</div></div>'
        f'<div class="kpi-card"><div class="stat-label">Tổng thời gian</div><div class="stat-value-blue">{result["duration_sec"]}s</div><div class="stat-sub">Định mức: {result["expected_sec"]}s</div></div>'
        f'<div class="kpi-card accent"><div class="stat-label">Điểm năng lực</div><div class="stat-value-red">{s_after}/100 ({delta_sign}{s_delta})</div><div class="stat-sub">Trước thi: {s_before}/100</div></div>'
        f'<div class="kpi-card"><div class="stat-label">Xếp loại</div><div class="stat-value-blue" style="font-size:1.25rem;">{result["competency_level"]}</div><div class="stat-sub">Đã lưu kết quả</div></div>'
        f'</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        f'<div class="kbs-box accent"><b>Nhận xét:</b> {result["expert_conclusion"]}</div>',
        unsafe_allow_html=True
    )

    st.markdown('<div class="section-heading">Chi tiết đáp án, thời gian từng câu & Cách làm tổng quát</div>', unsafe_allow_html=True)
    for idx, item in enumerate(result["question_reviews"], 1):
        tag_cls = "badge-blue" if item["is_correct"] else "badge-red"
        status_txt = "ĐÚNG" if item["is_correct"] else "SAI"
        f_info = Script_Login.get_formula_rule_info(item.get("formula_rule", "DRV_POW"))
        q_time_str = f"{item.get('time_spent_sec', '-')}s / {item.get('expected_time', '-')}s"

        st.markdown(
            f'<div class="kbs-box {"" if item["is_correct"] else "accent"}" style="padding:0.55rem 0.9rem; margin-bottom:0.4rem;">'
            f'<span class="{tag_cls}">Câu {idx:02d}: {status_txt}</span> '
            f'<span class="badge-outline">{item["id"]}</span> '
            f'<span class="badge-outline">{f_info["name"]}</span> '
            f'<span class="badge-outline">Thời gian: {q_time_str}</span>'
            f'</div>',
            unsafe_allow_html=True
        )
        st.markdown(f"**Đề:** {item['content']}")
        st.markdown(f"- **Bạn chọn:** `{item['user_choice'] or 'Trống'}` | **Đáp án đúng:** `{item['correct_answer']}`")
        st.markdown(f"- **Cách làm tổng quát:** {item.get('general_method', f_info['general_method'])}")
        st.markdown(f"- **Lời giải:** {item['explanation']}")
        st.markdown("<hr style='margin:0.7rem 0 0.9rem 0; border:none; border-top:1px solid #E2E8F0;'>", unsafe_allow_html=True)

    if st.button("Tạo đề luyện tập mới", type="primary", use_container_width=True):
        st.session_state.exam_result = None
        st.session_state.current_page = "USR_TAOBAI"
        st.rerun()

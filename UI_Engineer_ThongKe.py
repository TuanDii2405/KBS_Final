import streamlit as st
import Script_Engineer_ThongKe
import Script_Login

def render():
    eval_data = Script_Engineer_ThongKe.evaluate_difficulty_assignment()
    diff_names = {"DE": "Dễ", "TRUNG_BINH": "Trung bình", "KHA": "Khá", "KHO": "Khó"}

    st.markdown(
        f'<div class="kpi-grid" style="grid-template-columns: repeat(3, 1fr);">'
        f'<div class="kpi-card"><div class="stat-label">Hệ số tương quan (r)</div><div class="stat-value-blue">{eval_data["correlation"]}</div><div class="stat-sub">Tương quan Pearson</div></div>'
        f'<div class="kpi-card"><div class="stat-label">Sai số tuyệt đối (MAE)</div><div class="stat-value-blue">{eval_data["mae"]}</div><div class="stat-sub">Độ lệch độ khó b</div></div>'
        f'<div class="kpi-card accent"><div class="stat-label">Tỷ lệ khớp nhãn</div><div class="stat-value-red">{eval_data["agreement_rate"]}%</div><div class="stat-sub">Lý thuyết & thực tế</div></div>'
        f'</div>',
        unsafe_allow_html=True
    )

    st.markdown('<div class="section-heading">Đối sánh độ khó lý thuyết & thực nghiệm</div>', unsafe_allow_html=True)

    headers = ["Mã câu", "Chuyên đề", "Quy tắc", "Độ khó gán", "Lượt làm", "Tỷ lệ đúng", "TG Thực/Chuẩn", "Trạng thái"]
    rows = []
    for item in eval_data["calibration_table"][:45]:
        status_tag = "badge-red" if item["needs_recalibration"] else "badge-blue"
        sug_vi = diff_names.get(item["suggested_label"], item["suggested_label"])
        orig_vi = diff_names.get(item["assigned_difficulty"], item["assigned_difficulty"])
        status_label = f"Đổi -> {sug_vi}" if item["needs_recalibration"] else "Ổn định"

        rows.append([
            f"<code>{item['id']}</code>",
            item["topic_vi"],
            item["formula_vi"],
            f"<b>{orig_vi}</b>",
            str(item["attempts"]),
            f"{int(item['correct_rate']*100)}%",
            f"{item['avg_time']}s / {item['expected_time']}s",
            f'<span class="{status_tag}">{status_label}</span>'
        ])

    st.markdown(Script_Login.render_html_table(headers, rows), unsafe_allow_html=True)

    if st.button("Hiệu chỉnh tự động độ khó vào Knowledge.txt", type="primary", use_container_width=True):
        updated_count = Script_Engineer_ThongKe.apply_automatic_recalibration()
        st.success(f"Đã tự động hiệu chỉnh độ khó cho {updated_count} câu hỏi.")
        st.rerun()

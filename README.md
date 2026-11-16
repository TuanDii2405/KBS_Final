# HỆ THỐNG THI TRẮC NGHIỆM CÁ NHÂN HÓA NGƯỜI HỌC (KBS - KNOWLEDGE-BASED SYSTEM)

Tài liệu này giải thích toàn bộ cách hệ thống hoạt động từ tổng quan đến từng chi tiết nhỏ nhất (Use Case, Sơ đồ luồng hoạt động, cách đếm thời gian làm bài thực tế, cách lọc tri thức 3 tầng, cách tính điểm IRT, cách sinh câu hỏi bằng `SymPy` và cấu trúc 4 file `.txt`). Nội dung được trình bày song song theo hai góc nhìn:

* **Góc nhìn đời thường (dễ hiểu cho người không chuyên):** Dùng ví dụ thực tế, giải thích từng nút bấm và ý nghĩa từng con số.

* **Góc nhìn học thuật & kỹ thuật (dành cho giảng viên / hội đồng chấm đồ án):** Chỉ rõ tên file, tên hàm, công thức toán học và luồng dữ liệu bên dưới.

## 1. Giới thiệu tổng quan: Hệ thống này làm được gì?

### 1.1. Giải thích đơn giản cho mọi người

Hãy tưởng tượng khi bạn đi học với một **gia sư giỏi**:

* Gia sư không phát cho mọi học sinh cùng một tờ đề thi giống hệt nhau.

* Nếu thấy bạn làm tốt các câu cơ bản, gia sư sẽ nâng dần độ khó lên mức Khá, Giỏi.

* Nếu thấy bạn làm sai câu "Đạo hàm hàm hợp", gia sư biết ngay bạn đang bị hổng kiến thức ở phần gốc là "Đạo hàm cơ bản", từ đó nhắc bạn ôn lại đúng phần gốc đó kèm công thức tổng quát.

* Khi hết câu hỏi trong sách, gia sư có thể tự chế ra câu hỏi mới bằng cách đổi số, đổi cách hỏi và tạo ra các "đáp án bẫy" giống hệt những lỗi học sinh hay nhầm lẫn.

Phần mềm **Hệ thống Thi Trắc nghiệm Cá nhân hóa** này đóng vai trò chính xác như người gia sư đó, tập trung vào 2 môn **Toán học** (Đạo hàm, Nguyên hàm) và **Hóa học** (Cân bằng phương trình, Phản ứng vô cơ).

### 1.2. Giải thích dưới góc độ chuyên môn (Hệ cơ sở tri thức - KBS)

Hệ thống được thiết kế theo kiến trúc **Hệ cơ sở tri thức lai (Hybrid Knowledge-Based System)** kết hợp 4 trụ cột:

1. **Biểu diễn tri thức theo Khung tham số hóa (Parametric Frame-Based Representation) & Mạng ngữ nghĩa 3 tầng (Ontology):** Phân tách rõ ràng từ *Chuyên đề lớn* $\rightarrow$ *Quy tắc công thức hạt nhân* $\rightarrow$ *Dạng câu hỏi cụ thể*, kết hợp đồ thị điều kiện tiên quyết (Prerequisite Graph).

2. **Mô hình Lý thuyết ứng đáp câu hỏi 2 tham số (2PL-IRT - Item Response Theory):** Định lượng năng lực người học ($\theta$) và độ khó câu hỏi ($b$), sử dụng hàm thông tin Fisher $I(\theta)$ để chọn câu hỏi mang lại lượng thông tin đo lường cao nhất.

3. **Động cơ suy diễn tiến & suy diễn lùi (Forward & Backward Chaining Inference Engine):**

   * *Suy diễn tiến:* Tự động gán nhãn độ khó ban đầu cho câu hỏi mới và tự động hiệu chỉnh lại độ khó sau khi thu thập dữ liệu làm bài thực tế.

   * *Suy diễn lùi:* Truy vết ngược trên đồ thị tiên quyết để chẩn đoán lỗ hổng kiến thức gốc khi học viên làm sai.

4. **Sinh câu hỏi tự động bằng Tính toán biểu tượng (Symbolic Computation với SymPy):** Tự động lấy đạo hàm, nguyên hàm, xuất mã chuẩn $\text{LaTeX}$, biến đổi lời dẫn đề bài và tính toán phương án nhiễu (Buggy Distractors) từ các lỗi sai điển hình.

## 2. Phân tích Use Case (Các ca sử dụng của từng nhóm người dùng)

Hệ thống có **2 tác nhân (Actors)** chính với quyền hạn tách biệt hoàn toàn:

### 2.1. Sơ đồ tổng quan các Use Case

```
flowchart LR
    subgraph HeThong["HỆ THỐNG KBS THI TRẮC NGHIỆM CÁ NHÂN HÓA"]
        UC_Auth["UC01: Đăng nhập / Đăng ký tài khoản"]
        
        subgraph NhomHocVien["Phân hệ Học viên (Student)"]
            UC_U1["UC02: Xem bảng năng lực & gợi ý ôn tập (Suy diễn lùi)"]
            UC_U2["UC03: Tạo đề thi thích ứng IRT hoặc theo bộ lọc 3 tầng"]
            UC_U3["UC04: Làm bài thi có đồng hồ đếm giây trực tiếp"]
            UC_U4["UC05: Nộp bài, chấm điểm IRT & xem cách giải tổng quát"]
            UC_U5["UC06: Quản lý hồ sơ & xóa lịch sử bài làm cá nhân"]
        end

        subgraph NhomQuanTri["Phân hệ Kỹ sư tri thức / Giáo viên (Engineer)"]
            UC_E1["UC07: Xem thống kê tổng quan & Quản lý CRUD Luật suy diễn"]
            UC_E2["UC08: Lọc 3 tầng & Quản lý CRUD Ngân hàng 200 câu hỏi"]
            UC_E3["UC09: Sinh câu hỏi tự động bằng SymPy & Chuyển đổi LaTeX"]
            UC_E4["UC10: Kiểm tra, sửa nhận xét/điểm & xóa bài làm học viên"]
            UC_E5["UC11: Quản lý CRUD tài khoản & điều chỉnh năng lực học viên"]
            UC_E6["UC12: Kiểm định thực nghiệm & hiệu chỉnh tự động độ khó"]
        end
    end

    Student(["Học viên (Student)"]) --> UC_Auth
    Student --> UC_U1
    Student --> UC_U2
    Student --> UC_U3
    Student --> UC_U4
    Student --> UC_U5

    Engineer(["Kỹ sư tri thức / Giáo viên (Engineer)"]) --> UC_Auth
    Engineer --> UC_E1
    Engineer --> UC_E2
    Engineer --> UC_E3
    Engineer --> UC_E4
    Engineer --> UC_E5
    Engineer --> UC_E6

```

### 2.2. Đặc tả chi tiết 12 Use Case trong hệ thống

| Mã UC | Tên Use Case | Tác nhân | Đầu vào (Input) | Xử lý bên trong (File & Hàm chịu trách nhiệm) | Đầu ra (Output) | 
| ----- | ----- | ----- | ----- | ----- | ----- | 
| **UC01** | Đăng nhập & Đăng ký | Học viên, Giáo viên | `username`, `password`, `full_name` | `Script_Login.authenticate()` hoặc `register_user()` kiểm tra/ghi vào `TaiKhoan.txt`. | Khởi tạo `st.session_state`, điều hướng vào trang chủ tương ứng với `role`. | 
| **UC02** | Xem năng lực & gợi ý ôn tập | Học viên | `username` đang đăng nhập | `Script_User_TrangChu.get_student_dashboard()` quy đổi $\theta \rightarrow [5, 100]$, kiểm tra chuyên đề dưới 50% và dò ngược `prerequisite_graph`. | Bảng % làm chủ 6 chuyên đề + Thẻ lộ trình khuyên ôn lại chuyên đề nền tảng. | 
| **UC03** | Tạo đề thi cá nhân hóa | Học viên | Môn, Chuyên đề, Quy tắc, Dạng bài, Chế độ (`ADAPTIVE_IRT` / `CUSTOM`), Số câu | `Script_User_TaoBaiLam.assemble_personalized_exam()` lọc câu hỏi đúng nhánh tri thức, chấm điểm $U(q)$ theo hàm Fisher $I(\theta)$. Nếu thiếu câu, gọi `SymPy` sinh bù. | Gói đề thi `active_exam` lưu trong `st.session_state` kèm tổng thời gian định mức. | 
| **UC04** | Làm bài thi & Đếm giờ trực tiếp | Học viên | Gói đề thi `active_exam` | `UI_User_LamBai._render_live_timer()` ghi mốc `exam_start_ts = time.time()` và nhúng bộ đếm JavaScript chạy từng giây `MM:SS`. | Giao diện phòng thi hiển thị công thức $\text{LaTeX}$ và đồng hồ nhảy số mỗi giây. | 
| **UC05** | Nộp bài, chấm điểm IRT & Chẩn đoán | Học viên | Các phương án đã chọn `user_answers` | `Script_User_LamBai.grade_and_update_knowledge_state()` tính tổng giây thực tế, cập nhật $\theta_{\text{sau}}$, cập nhật `attempts`/`correct_rate`/`avg_time` vào `Knowledge.txt` và lưu bài vào `LichSuBaiLam.txt`. | Điểm thang 10, biến thiên năng lực (ví dụ `56/100 (+4)`), nhận xét chuyên gia và lời giải từng câu. | 
| **UC06** | Quản lý hồ sơ & lịch sử cá nhân | Học viên | Họ tên mới, mật khẩu mới, mã bài thi muốn xóa | `Script_User_CaNhan.update_own_account()` và `delete_own_submission()` cập nhật `TaiKhoan.txt`, `LichSuBaiLam.txt`. | Hồ sơ cá nhân và danh sách lịch sử bài thi được cập nhật tức thì. | 
| **UC07** | Quản lý CRUD Luật suy diễn | Giáo viên | Mã luật, Tên luật, Mức ưu tiên, Điều kiện, Hành động | `Script_Engineer_TrangChu.add_inference_rule()`, `update_inference_rule()`, `delete_inference_rule()` ghi trực tiếp vào `LuatSuyDien.txt`. | Bảng tập luật suy diễn được thêm mới, chỉnh sửa hoặc xóa. | 
| **UC08** | Quản lý CRUD Ngân hàng câu hỏi | Giáo viên | Nội dung đề, 4 đáp án A/B/C/D, quy tắc, dạng bài, số bước giải, thời gian | `Script_Engineer_QuanLyDeThi.add_manual_question()`, `update_question()`, `delete_question()` kết hợp `infer_question_difficulty()` tự động gán độ khó. | Câu hỏi được Thêm / Sửa / Xóa trong `Knowledge.txt`. | 
| **UC09** | Sinh câu hỏi tự động bằng SymPy | Giáo viên | Chuyên đề, Quy tắc công thức, Dạng câu hỏi, Mẫu biến đổi câu dẫn (1-4) | `Script_Engineer_QuanLyDeThi.generate_question_by_rule_and_sympy()` dùng `sp.diff`, `sp.integrate`, `sp.latex` tính đáp án đúng và tạo 3 đáp án nhiễu. | Câu hỏi mới hoàn chỉnh kèm vết luật kích hoạt, có thể lưu ngay vào `Knowledge.txt`. | 
| **UC10** | Quản lý & Sửa/Xóa bài làm học viên | Giáo viên | Mã bài nộp `submission_id`, nhận xét mới, điểm số mới | `Script_Engineer_QuanLyBaiLam.update_submission_conclusion()` và `delete_submission()` thao tác trên `LichSuBaiLam.txt`. | Bài làm của học viên được cập nhật lời phê/điểm số hoặc xóa khỏi lịch sử. | 
| **UC11** | Quản lý CRUD Học viên | Giáo viên | Mã học viên, Họ tên, Mật khẩu, Điểm Toán/Hóa (0-100), tùy chọn Reset tiến độ | `Script_Engineer_QuanLyNguoiDung.create_student_account()`, `update_student_profile()`, `delete_student_account()`. | Danh sách học viên trong `TaiKhoan.txt` được cập nhật. | 
| **UC12** | Kiểm định & Hiệu chỉnh độ khó | Giáo viên | Thống kê `attempts`, `correct_rate`, `avg_time` của 200 câu hỏi | `Script_Engineer_ThongKe.evaluate_difficulty_assignment()` và `apply_automatic_recalibration()` tính độ khó thực nghiệm $b_{\text{emp}}$ và cập nhật lại nhãn độ khó. | Chỉ số tương quan Pearson $r$, sai số $\text{MAE}$, tỷ lệ đồng thuận và cập nhật `Knowledge.txt`. | 

## 3. Sơ đồ hoạt động (Activity / Sequence Diagrams) của các luồng cốt lõi

### 3.1. Sơ đồ luồng hoạt động từ lúc Học viên Tạo đề $\rightarrow$ Làm bài $\rightarrow$ Chấm điểm & Cập nhật tri thức

```
sequenceDiagram
    autonumber
    actor SV as Học viên (Student)
    participant UI_Tao as UI_User_TaoBaiLam.py
    participant Sc_Tao as Script_User_TaoBaiLam.py
    participant UI_Thi as UI_User_LamBai.py
    participant Sc_Thi as Script_User_LamBai.py
    participant DB as 4 File .txt (CSDL Tri thức)

    SV->>UI_Tao: 1. Chọn Môn -> Chuyên đề -> Quy tắc -> Dạng bài -> Số câu
    UI_Tao->>Sc_Tao: 2. Gọi assemble_personalized_exam()
    Sc_Tao->>DB: 3. Đọc năng lực theta (TaiKhoan.txt) & Ngân hàng câu hỏi (Knowledge.txt)
    Sc_Tao->>Sc_Tao: 4. Chấm điểm từng câu hỏi U(q) = 0.55*Fisher + 0.30*Weakness + 0.15*Novelty
    alt Nếu ngân hàng thiếu câu ở dạng đặc thù
        Sc_Tao->>Sc_Tao: 5. Gọi SymPy tự động sinh biến thể câu hỏi mới (Q_DYN_xx)
    end
    Sc_Tao-->>UI_Tao: 6. Trả về gói đề thi active_exam
    SV->>UI_Thi: 7. Bấm "Bắt đầu làm bài ngay"
    UI_Thi->>UI_Thi: 8. Ghi nhận exam_start_ts = time.time() & Chạy đồng hồ JS đếm giây
    SV->>UI_Thi: 9. Chọn đáp án A/B/C/D cho các câu & Bấm "Nộp bài"
    UI_Thi->>Sc_Thi: 10. Gửi user_answers + total_duration = time.time() - exam_start_ts
    Sc_Thi->>Sc_Thi: 11. Chấm đúng/sai, tính p_theta và cập nhật năng lực theta_after
    Sc_Thi->>Sc_Thi: 12. Suy diễn lùi trên prerequisite_graph tìm chuyên đề gốc cần ôn lại
    Sc_Thi->>DB: 13. Lưu năng lực mới (TaiKhoan.txt), thống kê câu hỏi (Knowledge.txt) & lịch sử (LichSuBaiLam.txt)
    Sc_Thi-->>UI_Thi: 14. Hiển thị điểm số, biến thiên năng lực & Cách giải tổng quát từng câu

```

### 3.2. Sơ đồ thuật toán Tự động hiệu chỉnh độ khó câu hỏi (Self-Calibrating Knowledge Base)

```
flowchart TD
    A["Câu hỏi mới nhập hoặc mới sinh bằng SymPy"] --> B["Suy diễn tiến (infer_question_difficulty):<br/>Tính complexity_score từ số bước, loại bài, ký hiệu LaTeX, thời gian"]
    B --> C["Gán nhãn độ khó khởi tạo (Prior Difficulty):<br/>Dễ / Trung bình / Khá / Khó và tham số irt_b ban đầu"]
    C --> D["Đưa vào Knowledge.txt phục vụ học viên làm bài"]
    D --> E["Mỗi lần học viên nộp bài:<br/>Tăng attempts + 1, cập nhật tỷ lệ đúng (correct_rate) & thời gian TB (avg_time)"]
    E --> F{"Số lượt làm bài<br/>attempts >= 8?"}
    F -- "Chưa đủ (< 8 lượt)" --> G["Giữ nguyên độ khó khởi tạo để thu thập thêm mẫu"]
    F -- "Đã đủ (>= 8 lượt)" --> H["Tính độ khó thực nghiệm b_emp:<br/>b_emp = 0.75 * ln((1 - p)/p) + 0.45 * (avg_time/expected_time - 1)"]
    H --> I{"Độ lệch |b_emp - irt_b| >= 0.45<br/>hoặc đổi nhãn độ khó?"}
    I -- "Không lệch đáng kể" --> J["Đánh dấu trạng thái: Ổn định"]
    I -- "Có lệch (Câu quá dễ hoặc quá khó so với dự kiến)" --> K["Phát cảnh báo lệch độ khó (Drift Alert)<br/>Cập nhật: irt_b_mới = 0.4 * irt_b + 0.6 * b_emp"]

```

## 4. Giải thích cực kỳ chi tiết các cơ chế kỹ thuật bên trong ("Làm sao chương trình làm được như vậy?")

Phần này giải đáp trực tiếp các câu hỏi kỹ thuật thường gặp khi bảo vệ đồ án hoặc khi đọc code.

### 4.1. Làm sao đồng hồ đếm thời gian làm bài chạy mượt từng giây mà không bị đơ?

* **Vấn đề thường gặp của Streamlit:** Streamlit hoạt động theo cơ chế chạy lại từ trên xuống dưới (top-to-bottom rerun) mỗi khi bấm nút. Nếu dùng vòng lặp `while True: time.sleep(1)` trong Python để đếm giờ, toàn bộ trang web sẽ bị đơ (không thể bấm chọn đáp án A, B, C, D được), hoặc nếu không có vòng lặp thì đồng hồ đứng im ở `00:00`.

* **Cách giải quyết trong hệ thống (`UI_User_LamBai.py` & `Script_User_LamBai.py`):**
  Hệ thống kết hợp **Mốc thời gian máy chủ Python (Server Timestamp)** và **Bộ đếm giao diện JavaScript (Client-side Live Timer)** qua 3 bước:

  1. **Bước 1 — Đóng dấu thời điểm bắt đầu (Python):** Ngay khoảnh khắc học viên mở đề thi trong `UI_User_LamBai.py`, hệ thống kiểm tra và lưu mốc thời gian thực của hệ thống (tính bằng giây từ Epoch) vào bộ nhớ phiên:

     ```
     if "exam_start_ts" not in exam:
         exam["exam_start_ts"] = time.time()
     
     ```

     Nhờ lưu trong `st.session_state.active_exam`, dù học viên có thao tác gì trên trang thì mốc `exam_start_ts` vẫn giữ nguyên, không bị reset về 0.

  2. **Bước 2 — Hiển thị đồng hồ nhảy số trực tiếp từng giây (JavaScript):** Hàm `_render_live_timer()` đổi `exam_start_ts` sang mili-giây (`start_ms = int(start_ts * 1000)`) rồi truyền vào một khung HTML độc lập thông qua `streamlit.components.v1.html(...)`. Bên trong khung này, hàm `setInterval(tick, 1000)` của JavaScript tự động lấy `Date.now() - startMs` mỗi 1000ms (1 giây) để cập nhật chuỗi `MM:SS` lên thẻ `<span id="kbs-live-clock">`. Vì chạy trên trình duyệt (Client-side), đồng hồ nhảy từng giây cực mượt mà **không làm tải lại trang Python**.

  3. **Bước 3 — Tính thời gian thực tế chính xác khi bấm Nộp bài (Python):** Khi học viên bấm nút `"Nộp bài & Chấm điểm"`, Python lấy thời điểm hiện tại trừ đi mốc bắt đầu:

     ```
     total_duration = max(1, int(time.time() - exam["exam_start_ts"]))
     
     ```

     Con số `total_duration` (giây) này là thời gian thực tế chính xác tuyệt đối, được truyền sang `Script_User_LamBai.grade_and_update_knowledge_state()` để chấm điểm tốc độ và lưu vào `LichSuBaiLam.txt`.

### 4.2. Làm sao bộ lọc thông minh biết chọn "Đạo hàm" thì không hiện dạng bài "Hóa học"?

* **Nguyên nhân gây lỗi ở các hệ thống thông thường:** Nếu để 4 ô chọn (Môn học, Chuyên đề, Quy tắc công thức, Dạng bài) đọc từ 4 danh sách độc lập, người dùng chọn Chuyên đề *Đạo hàm* nhưng ô Dạng bài vẫn liệt kê cả *"Tìm hệ số cân bằng tối giản"* của Hóa học.

* **Cách giải quyết bằng Lọc phụ thuộc 3 tầng (Cascading Ontology Filter trong `Script_Login.py`):**
  Trong `Script_Login.py`, mỗi thực thể tri thức đều lưu khóa ngoại trỏ về tầng trên của nó:

  * Mỗi `concept_node` lưu thuộc tính `"subject": "MATH"` hoặc `"CHEM"`.

  * Mỗi `formula_rule` lưu thuộc tính `"concept_node"` và danh sách `"allowed_forms"` (chỉ những dạng câu hỏi nào hợp lệ với công thức đó).

  * Mỗi `question_form` lưu thuộc tính `"subject"` và danh sách `"concept_nodes"` được phép áp dụng.

  * Khi người dùng chọn trên giao diện, 3 hàm lọc tuần tự sẽ khóa chặt dữ liệu:

    1. `get_filtered_concept_nodes(subject)` $\rightarrow$ Khi chọn Toán (`MATH`), chỉ trả về 3 chuyên đề Toán.

    2. `get_filtered_formula_rules(subject, concept_node)` $\rightarrow$ Khi chọn `MATH_DERIV_01`, chỉ trả về 3 quy tắc công thức thuộc chuyên đề đó (`DRV_POW`, `DRV_PROD`, `DRV_QUOT`).

    3. `get_filtered_question_forms(subject, concept_node, formula_rule)` $\rightarrow$ Chỉ trả về các dạng câu hỏi nằm trong `allowed_forms` của quy tắc đang chọn (ví dụ chọn `INT_POW` - Nguyên hàm lũy thừa thì chỉ hiện dạng *Tìm biểu thức* và *Tính giá trị* $F(x_0)$, tự động ẩn dạng *Viết phương trình tiếp tuyến* và ẩn toàn bộ dạng bài Hóa học).

### 4.3. Làm sao hệ thống không bao giờ bị lỗi rò rỉ thẻ HTML `<tr><td>` ra màn hình?

* **Nguyên nhân gây lỗi:** Bộ phân tích Markdown của Streamlit (CommonMark) có một quy tắc ngặt nghèo: nếu chuỗi HTML nhiều dòng có chứa các dòng thụt lề từ 4 khoảng trắng trở lên hoặc ngắt dòng giữa các thẻ `<tr>`, Markdown sẽ hiểu nhầm phần bên trong là một khối mã nguồn (`<pre><code>`) và in nguyên văn chữ `<tr><td>...` ra màn hình người dùng.

* **Cách giải quyết triệt để (`Script_Login.render_html_table`):**
  Mọi bảng dữ liệu trong toàn bộ hệ thống đều đi qua hàm `Script_Login.render_html_table(headers, rows)`. Hàm này nén toàn bộ thẻ `<table class="clean-table"><thead>...</thead><tbody>...</tbody></table>` thành **một chuỗi HTML liền khối duy nhất trên 1 dòng**, không có ký tự xuống dòng hay khoảng trắng thừa, đảm bảo trình duyệt luôn hiển thị thành bảng kẻ ô chuẩn 100%.

### 4.4. Ví dụ tính toán từng bước khi Chấm điểm & Cập nhật năng lực (Walkthrough bằng số thực tế)

Giả sử học viên **Nguyễn Minh Quân (`sv001`)** có năng lực môn Toán trước khi thi là $\theta_{\text{trước}} = 0.35$.

* **Quy đổi ra thang điểm 100 trên giao diện (`theta_to_score100`):**
  

  $$
  \text{Điểm năng lực} = \text{round}\left(\frac{\theta + 3.0}{6.0} \times 100\right) = \text{round}\left(\frac{0.35 + 3.0}{6.0} \times 100\right) = 56\text{/100 điểm}
  $$

* **Xét Câu số 1 trong đề thi:** Có độ khó $b = 0.05$, độ phân biệt $a = 1.25$.

  * Xác suất học viên làm đúng câu này theo mô hình 2PL-IRT là:
    

    $$
    P(\theta) = \frac{1}{1 + e^{-a(\theta - b)}} = \frac{1}{1 + e^{-1.25(0.35 - 0.05)}} = \frac{1}{1 + e^{-0.375}} \approx 0.593\text{ (tức 59.3\%)}
    $$

  * **Trường hợp 1 (Học viên trả lời ĐÚNG trong thời gian định mức, `speed_weight = 1.0`):**
    

    $$
    \theta_{\text{mới}} = \theta_{\text{cũ}} + 0.28 \times \text{speed\_weight} \times a \times [1 - P(\theta)]
    $$

    $$
    \theta_{\text{mới}} = 0.35 + 0.28 \times 1.0 \times 1.25 \times (1 - 0.593) = 0.35 + 0.142 = 0.492
    $$

    
    (*Nếu học viên làm đúng một câu rất khó có* $P(\theta) = 0.20$*, lượng điểm cộng sẽ lớn gấp đôi vì* $1 - P(\theta) = 0.80$).

  * **Trường hợp 2 (Học viên trả lời SAI và nộp bài quá nhanh dưới 35% thời gian định mức** $\rightarrow$ **bị phạt lỗi đánh lụi `guess_penalty = 1.25`):**
    

    $$
    \theta_{\text{mới}} = \theta_{\text{cũ}} - 0.28 \times \text{guess\_penalty} \times a \times P(\theta)
    $$

    $$
    \theta_{\text{mới}} = 0.35 - 0.28 \times 1.25 \times 1.25 \times 0.593 \approx 0.09
    $$

### 4.5. Cấu trúc chi tiết của 4 File Dữ liệu `.txt` (Định dạng JSON UTF-8)

#### 1) File `Knowledge.txt` (Lưu 200 khung tri thức câu hỏi)

Mỗi câu hỏi là một đối tượng JSON chứa đầy đủ 16 thuộc tính:

```
{
  "id": "Q_MATH_004",
  "subject": "MATH",
  "topic": "DAO_HAM",
  "concept_node": "MATH_DERIV_01",
  "formula_rule": "DRV_QUOT",
  "question_form": "FORM_TANGENT_SLOPE",
  "q_type": "APPLICATION",
  "steps": 2,
  "difficulty": "TRUNG_BINH",
  "irt_b": 0.05,
  "irt_a": 1.3,
  "expected_time": 55,
  "attempts": 22,
  "correct_rate": 0.64,
  "avg_time": 54,
  "content": "Cho đường cong $(C)$ là đồ thị của hàm số phân thức $y = \\frac{2x + 1}{x - 1}$. Hệ số góc $k$ của tiếp tuyến với $(C)$ tại điểm có hoành độ $x_0 = 2$ là:",
  "options": {
    "A": "$k = -3$",
    "B": "$k = 3$",
    "C": "$k = -1$",
    "D": "$k = 5$"
  },
  "answer": "A",
  "general_method": "Với hàm phân thức bậc nhất $y = \\frac{ax+b}{cx+d}$, tính đạo hàm thương $y' = \\frac{ad - bc}{(cx+d)^2}$. Hệ số góc tiếp tuyến tại điểm có hoành độ $x_0$ là $k = y'(x_0)$.",
  "explanation": "Ta có $y' = \\frac{2(-1) - 1 \\cdot 1}{(x - 1)^2} = \\frac{-3}{(x - 1)^2}$. Tại $x_0 = 2$, hệ số góc tiếp tuyến là $k = y'(2) = \\frac{-3}{(2 - 1)^2} = -3$."
}

```

#### 2) File `TaiKhoan.txt` (Lưu hồ sơ năng lực người học)

Lưu điểm năng lực `theta_math`, `theta_chem`, lịch sử câu hỏi vừa gặp `recent_questions` và thống kê số câu đúng/tổng trên từng chuyên đề `node_stats`:

```
{
  "username": "sv001",
  "password": "123456",
  "full_name": "Nguyễn Minh Quân",
  "role": "student",
  "theta_math": 0.35,
  "theta_chem": -0.45,
  "node_stats": {
    "MATH_DERIV_01": { "correct": 7, "total": 8 },
    "MATH_DERIV_02": { "correct": 3, "total": 8 }
  },
  "recent_questions": ["Q_MATH_001", "Q_MATH_004"]
}

```

#### 3) File `LuatSuyDien.txt` (Lưu Ontology 3 tầng & Tập luật suy diễn)

Lưu toàn bộ từ điển `concept_nodes`, `formula_rules`, `question_forms`, đồ thị `prerequisite_graph`, mẫu biến đổi câu dẫn `stem_transformation_rules` và danh sách `rules`.

#### 4) File `LichSuBaiLam.txt` (Lưu vết chấm bài và giải thích từng câu)

Mỗi lần nộp bài tạo ra một bản ghi `submission_id` chứa điểm số, `duration_sec`, `expected_sec`, `theta_before`, `theta_after`, `expert_conclusion` và mảng `question_reviews` lưu chi tiết từng câu hỏi trong đề.

## 5. Cấu trúc phân loại tri thức 3 tầng (Chống nhầm lẫn chéo giữa các môn)

Hệ thống quản lý **200 câu hỏi chuẩn** $\text{LaTeX}$ (100 câu Toán + 100 câu Hóa) được phân loại nghiêm ngặt theo hình cây 3 tầng. Khi người dùng chọn **Môn Toán**, hệ thống chỉ hiển thị các chuyên đề, công thức và dạng bài của Toán (không bao giờ trộn lẫn dạng bài của Hóa sang Toán và ngược lại).

### Tầng 1: 6 Chuyên đề lớn (`concept_node`)

| Mã chuyên đề | Tên chuyên đề trọng tâm | Môn học | Chuyên đề tiên quyết (Cần học trước) | 
| ----- | ----- | ----- | ----- | 
| `MATH_DERIV_01` | Định nghĩa đạo hàm & Tiếp tuyến đồ thị | Toán học | *(Chuyên đề gốc)* | 
| `MATH_DERIV_02` | Đạo hàm hàm hợp & Lượng giác - Mũ - Logarit | Toán học | `MATH_DERIV_01` | 
| `MATH_INTEG_01` | Nguyên hàm cơ bản & Tính chất tuyến tính | Toán học | `MATH_DERIV_01`, `MATH_DERIV_02` | 
| `CHEM_REACT_01` | Phân loại các phản ứng hóa học vô cơ | Hóa học | *(Chuyên đề gốc)* | 
| `CHEM_BAL_01` | Bảo toàn nguyên tố & Cân bằng PTHH cơ bản | Hóa học | `CHEM_REACT_01` | 
| `CHEM_BAL_02` | Cân bằng phản ứng Oxi hóa - Khử (Thăng bằng electron) | Hóa học | `CHEM_BAL_01`, `CHEM_REACT_01` | 

### Tầng 2: 16 Quy tắc công thức hạt nhân (`formula_rule`)

Mỗi câu hỏi không chỉ gắn với tên chương chung chung mà được gắn trực tiếp với **quy tắc công thức cụ thể** và **cách làm tổng quát**:

* **Nhóm Đạo hàm (7 quy tắc):**

  1. `DRV_POW`: Đạo hàm hàm lũy thừa $(x^n)' = n \cdot x^{n-1}$ và đa thức.

  2. `DRV_PROD`: Đạo hàm của tích $(u \cdot v)' = u'v + uv'$.

  3. `DRV_QUOT`: Đạo hàm của thương $\left(\frac{u}{v}\right)' = \frac{u'v - uv'}{v^2}$ và hàm phân thức bậc nhất $\left(\frac{ax+b}{cx+d}\right)' = \frac{ad-bc}{(cx+d)^2}$.

  4. `DRV_CHAIN`: Đạo hàm hàm hợp $[u(x)^n]' = n \cdot u(x)^{n-1} \cdot u'(x)$ và căn thức $(\sqrt{u})' = \frac{u'}{2\sqrt{u}}$.

  5. `DRV_TRIG`: Đạo hàm hàm lượng giác $(\sin u)' = u'\cos u$, $(\cos u)' = -u'\sin u$, $(\tan u)' = \frac{u'}{\cos^2 u}$.

  6. `DRV_EXP`: Đạo hàm hàm số mũ $(a^x)' = a^x \ln a$, $(e^u)' = u'e^u$, $(a^u)' = u'a^u \ln a$.

  7. `DRV_LOG`: Đạo hàm hàm số logarit $(\ln u)' = \frac{u'}{u}$, $(\log_a u)' = \frac{u'}{u \ln a}$.

* **Nhóm Nguyên hàm (3 quy tắc):**
  8. `INT_POW`: Nguyên hàm lũy thừa $\int x^n dx = \frac{x^{n+1}}{n+1} + C$.
  9. `INT_LINEAR`: Tính chất tuyến tính $\int [k \cdot f(x) \pm m \cdot g(x)]dx$.
  10. `INT_TRIG_EXP`: Nguyên hàm hàm lượng giác và hàm mũ $\int e^{kx+m}dx$, $\int \cos(kx)dx$.

* **Nhóm Hóa học (6 quy tắc):**
  11. `BAL_ATOM`: Bảo toàn nguyên tử các nguyên tố đơn lẻ.
  12. `BAL_GROUP`: Bảo toàn nhóm nguyên tử ($-\text{OH}, -\text{NO}_3, =\text{SO}_4, =\text{CO}_3$).
  13. `BAL_REDOX_STD`: Thăng bằng electron phản ứng Oxi hóa - Khử cơ bản ($\sum n_{e \text{ nhường}} = \sum n_{e \text{ nhận}}$).
  14. `BAL_REDOX_ENV`: Cân bằng Oxi hóa - Khử có môi trường axit ($\text{HNO}_3, \text{H}_2\text{SO}_4$ đặc).
  15. `REACT_TYPE_4`: Phân loại 4 phản ứng vô cơ (Hóa hợp, Phân hủy, Thế, Trao đổi).
  16. `REACT_REDOX_ID`: Xác định vai trò chất khử, chất oxi hóa và phản ứng tự oxi hóa - khử.

### Tầng 3: 8 Dạng bài tập cụ thể (`question_form`)

* **5 dạng bài dành riêng cho môn Toán:**

  * `FORM_EXPR`: Tìm công thức / biểu thức đạo hàm hoặc nguyên hàm.

  * `FORM_VAL_POINT`: Tính giá trị đạo hàm $f'(x_0)$ hoặc nguyên hàm $F(x_0)$ tại một điểm.

  * `FORM_TANGENT_SLOPE`: Tính hệ số góc $k = y'(x_0)$ của tiếp tuyến tại điểm.

  * `FORM_TANGENT_EQ`: Viết phương trình tiếp tuyến của đồ thị hàm số.

  * `FORM_SOLVE_COND`: Giải phương trình / bất phương trình đạo hàm hoặc đồng nhất hệ số nguyên hàm.

* **3 dạng bài dành riêng cho môn Hóa:**

  * `FORM_CHEM_COEFF`: Tìm hệ số cân bằng tối giản hoặc tổng hệ số các chất.

  * `FORM_CHEM_RATIO`: Tìm tỉ lệ hệ số chất khử, chất oxi hóa hoặc axit môi trường.

  * `FORM_CHEM_CLASS`: Nhận diện loại phản ứng hóa học và vai trò các chất.

## 6. Cơ chế hoạt động của 4 Bài toán thông minh trong hệ thống

### 6.1. Bài toán 1: Xác định độ khó câu hỏi mới & Tự động hiệu chỉnh từ thực tế

* **Khi mới nhập hoặc mới sinh câu hỏi (Chưa có học sinh làm thử):**
  Hệ thống đọc cấu trúc câu hỏi (số bước biến đổi `steps`, dạng tư duy `q_type`, thời gian dự kiến `expected_time` và các ký hiệu toán/hóa phức tạp như $\ln, \sqrt{\dots}, \int, \text{FeS}_2, \text{HNO}_3$) để tính **Điểm độ phức tạp (Complexity Score)** và kích hoạt luật `R_DIFF_01` $\rightarrow$ `R_DIFF_04` xếp câu hỏi vào 4 mức: **Dễ, Trung bình, Khá, Khó**.

* **Khi đã có từ 8 lượt học sinh làm bài trở lên (Hiệu chỉnh thực nghiệm):**
  Một câu hỏi ban đầu giáo viên nghĩ là "Trung bình", nhưng thực tế 85% học sinh đều làm sai và tốn gấp đôi thời gian $\rightarrow$ thực chất câu đó là câu **Khó**. Hệ thống tính độ khó thực nghiệm $b_{\text{emp}}$ dựa trên tỷ lệ làm đúng $p$ và thời gian làm bài trung bình $t_{\text{avg}}$:

  $$
  b_{\text{emp}} = 0.75 \cdot \ln\left(\frac{1 - p}{p}\right) + 0.45 \cdot \left(\frac{t_{\text{avg}}}{t_{\text{expected}}} - 1\right)
  $$

  Sau đó cập nhật lại độ khó theo công thức kết hợp: $b_{\text{mới}} = 0.4 \cdot b_{\text{ban đầu}} + 0.6 \cdot b_{\text{emp}}$.

### 6.2. Bài toán 2: Chọn câu hỏi cá nhân hóa theo năng lực (Adaptive Testing)

Mỗi học viên có một chỉ số năng lực $\theta \in [-3.0, +3.0]$ (được quy đổi ra **thang điểm 0 - 100** trên giao diện để dễ hiểu). Khi học viên bấm tạo đề thích ứng, hệ thống chấm điểm từng câu hỏi ứng viên trong ngân hàng bằng hàm mục tiêu $U(q)$:

$$
U(q) = 0.55 \cdot I(\theta, q) + 0.30 \cdot W(\text{node}) + 0.15 \cdot N(q)
$$

Trong đó:

* $I(\theta, q) = a^2 \cdot P(\theta) \cdot [1 - P(\theta)]$: **Hàm thông tin Fisher** — ưu tiên chọn những câu hỏi có độ khó $b$ sát với trình độ hiện tại $\theta$ của học viên nhất (không quá dễ gây nhàm chán, không quá khó gây nản).

* $W(\text{node})$: **Trọng số bù đắp lỗ hổng** — ưu tiên rút trích các chuyên đề mà học viên đang có tỷ lệ làm đúng thấp.

* $N(q)$: **Độ mới (Novelty)** — ưu tiên những câu học viên chưa gặp trong các lần thi gần đây.

### 6.3. Bài toán 3: Chấm điểm năng lực & Chẩn đoán lỗ hổng kiến thức

Sau khi học viên nộp bài (có **đồng hồ đếm giây trực tiếp** trên màn hình):

1. **Cập nhật năng lực:** Nếu làm đúng câu khó trong thời gian chuẩn, điểm năng lực tăng mạnh. Nếu làm sai câu dễ hoặc đánh lụi quá nhanh (dưới 35% thời gian định mức), điểm năng lực giảm tương ứng.

2. **Suy diễn lùi tìm nguyên nhân gốc:** Nếu học viên làm sai nhiều ở chuyên đề nâng cao (ví dụ `MATH_DERIV_02` - Đạo hàm hàm hợp), luật `R_DIAG_01` sẽ dò ngược đồ thị tiên quyết (`prerequisite_graph`) để khuyên học viên quay lại ôn chuyên đề gốc (`MATH_DERIV_01` - Đạo hàm cơ bản) kèm theo lời giải và công thức tổng quát của từng câu.

### 6.4. Bài toán 4: Tự động biến đổi đề & Sinh phương án nhiễu bằng SymPy

Thay vì lưu các câu hỏi tĩnh nhàm chán, hệ thống tích hợp thư viện `SymPy` kết hợp 2 tập luật:

* **Luật biến đổi câu dẫn (`R_TRANS_STEM`):** Cùng một hàm số $y = 2x^3 - 3x^2 + 1$, hệ thống tự động luân phiên cách phát biểu đề:

  * *Mẫu 1:* "Cho hàm số đa thức bậc ba $y = f(x) = 2x^3 - 3x^2 + 1$..."

  * *Mẫu 2:* "Cho hàm số $y = 2x^3 - 3x^2 + 1$..."

  * *Mẫu 3:* "Xét hàm số $f(x)$ xác định bởi công thức $f(x) = 2x^3 - 3x^2 + 1$..."

  * *Mẫu 4:* "Cho đường cong $(C)$ là đồ thị của hàm số $y = 2x^3 - 3x^2 + 1$..."

* **Luật sinh phương án nhiễu thông minh (`R_BUGGY_GEN`):** Các đáp án sai (B, C, D) không phải số ngẫu nhiên vô lý mà được tính từ lỗi sai thực tế:

  * Quên nhân $u'(x)$ khi tính đạo hàm hàm hợp $[u(x)^n]'$.

  * Nhầm công thức đạo hàm tích $(u \cdot v)' = u' \cdot v'$.

  * Quên nhân $\ln a$ khi tính đạo hàm $(a^x)'$ hoặc nhầm đạo hàm với nguyên hàm.

## 7. Cấu trúc 25 File Mã nguồn trong Dự án (Tổ chức rõ ràng, tách biệt)

Toàn bộ dự án gồm **25 file mã nguồn & dữ liệu** (cộng thêm file `README.md` này là 26 file) đặt chung trong một thư mục gốc, chia làm 4 nhóm rõ ràng:

| Nhóm file | Tên file cụ thể | Vai trò và chức năng chính | 
| ----- | ----- | ----- | 
| **1. Điều phối chính (1 file)** | `Main.py` | Cấu hình trang, nạp CSS giao diện tối giản (40% Trắng `#FFFFFF` - 30% Xanh Cerulean `#124874` - 20% Đỏ Jasper `#CF373D`) và thanh điều hướng ngang trên cùng. | 
| **2. Dữ liệu tri thức (4 file `.txt`)** | `LuatSuyDien.txt` | Lưu cây phân loại 3 tầng (6 chuyên đề, 16 quy tắc công thức, 8 dạng bài), đồ thị tiên quyết và tập luật suy diễn. | 
|  | `Knowledge.txt` | Ngân hàng **200 câu hỏi trắc nghiệm** chuẩn $\text{LaTeX}$ (100 câu Toán + 100 câu Hóa) kèm cách giải tổng quát và thông số độ khó IRT. | 
|  | `TaiKhoan.txt` | Lưu danh sách tài khoản Quản trị viên & Học viên, điểm năng lực Toán/Hóa và thống kê số câu đúng/tổng trên từng chuyên đề. | 
|  | `LichSuBaiLam.txt` | Lưu lịch sử các bài thi đã nộp, thời gian làm bài, biến thiên năng lực và chi tiết đúng/sai từng câu. | 
| **3. Xử lý nghiệp vụ (10 file `Script_*.py`)** | `Script_Login.py` | Đọc/ghi 4 file `.txt`, xác thực đăng nhập, chuẩn hóa biểu thức sang $\text{LaTeX}$, lọc phụ thuộc 3 tầng và tạo bảng chuẩn. | 
|  | `Script_Engineer_TrangChu.py` | Tổng hợp số liệu hệ thống, phân bố 6 chuyên đề và xử lý Thêm/Sửa/Xóa (CRUD) tập luật suy diễn. | 
|  | `Script_Engineer_QuanLyDeThi.py` | Lọc câu hỏi 3 tầng, sinh câu hỏi tự động bằng `SymPy`, gán độ khó và xử lý Thêm/Sửa/Xóa (CRUD) câu hỏi. | 
|  | `Script_Engineer_QuanLyBaiLam.py` | Tra cứu, lọc, sửa nhận xét/điểm số và xóa lịch sử bài làm của học viên. | 
|  | `Script_Engineer_QuanLyNguoiDung.py` | Quản lý hồ sơ năng lực học viên, Thêm/Sửa/Xóa tài khoản học viên và đặt lại tiến độ. | 
|  | `Script_Engineer_ThongKe.py` | Tính hệ số tương quan Pearson ($r$), sai số tuyệt đối trung bình ($\text{MAE}$) và hiệu chỉnh tự động độ khó câu hỏi. | 
|  | `Script_User_TrangChu.py` | Tính toán bảng tiến độ 6 chuyên đề và chạy suy diễn lùi đưa ra khuyến nghị ôn tập cho học viên. | 
|  | `Script_User_TaoBaiLam.py` | Thuật toán rút trích đề thi cá nhân hóa theo hàm thông tin Fisher $I(\theta)$ và tự động gọi `SymPy` bù câu hỏi khi thiếu. | 
|  | `Script_User_LamBai.py` | Chấm điểm bài thi, cập nhật năng lực $\theta$ theo thời gian thực tế, lưu lịch sử và cập nhật thống kê câu hỏi. | 
|  | `Script_User_CaNhan.py` | Tổng hợp báo cáo năng lực cá nhân, cập nhật thông tin tài khoản và xóa lịch sử bài thi cá nhân. | 
| **4. Giao diện hiển thị (10 file `UI_*.py`)** | `UI_Login.py` | Màn hình đăng nhập/đăng ký tối giản nằm chính giữa màn hình. | 
|  | `UI_Engineer_TrangChu.py` | Giao diện tổng quan quản trị và bảng quản lý CRUD luật suy diễn. | 
|  | `UI_Engineer_QuanLyDeThi.py` | Giao diện ngân hàng câu hỏi $\text{LaTeX}$, bộ lọc phụ thuộc 3 tầng, CRUD câu hỏi và bộ sinh đề `SymPy`. | 
|  | `UI_Engineer_QuanLyBaiLam.py` | Giao diện danh sách bài nộp, xem chi tiết từng câu và Sửa/Xóa bài làm. | 
|  | `UI_Engineer_QuanLyNguoiDung.py` | Giao diện quản lý danh sách học viên và Thêm/Sửa/Xóa hồ sơ học viên. | 
|  | `UI_Engineer_ThongKe.py` | Giao diện đối sánh độ khó lý thuyết - thực tế và nút hiệu chỉnh tự động. | 
|  | `UI_User_TrangChu.py` | Giao diện trang chủ học viên, bảng phần trăm làm chủ 6 chuyên đề và sổ tay công thức. | 
|  | `UI_User_TaoBaiLam.py` | Giao diện thiết lập đề thi thông minh theo Môn $\rightarrow$ Chuyên đề $\rightarrow$ Quy tắc công thức $\rightarrow$ Dạng bài. | 
|  | `UI_User_LamBai.py` | Phòng làm bài thi trực tuyến tích hợp **đồng hồ đếm giờ trực tiếp (Live Timer)** và trang kết quả chi tiết. | 
|  | `UI_User_CaNhan.py` | Giao diện hồ sơ cá nhân, cập nhật mật khẩu/họ tên và xem lại/xóa lịch sử bài thi. | 

## 8. Hướng dẫn cài đặt và chạy chương trình trên Visual Studio Code

### Bước 1: Chuẩn bị môi trường

1. Đảm bảo máy tính đã cài đặt **Python** (phiên bản 3.9 trở lên).

2. Giải nén toàn bộ các file vào cùng một thư mục (ví dụ: `KBS_ThiTracNghiem`).

3. Mở thư mục này bằng phần mềm **Visual Studio Code (VS Code)**.

### Bước 2: Cài đặt thư viện cần thiết

Mở cửa sổ Terminal trong VS Code (nhấn tổ hợp phím `` Ctrl + ` ``) và chạy lệnh sau:

```
pip install streamlit sympy

```

### Bước 3: Khởi chạy ứng dụng

Tại cửa sổ Terminal của VS Code, chạy lệnh:

```
streamlit run Main.py

```

Trình duyệt web sẽ tự động mở ứng dụng tại địa chỉ `http://localhost:8501`.

## 9. Tài khoản đăng nhập mẫu & Kịch bản Demo đồ án

### 9.1. Danh sách tài khoản có sẵn

| Phân quyền | Tên đăng nhập | Mật khẩu | Đặc điểm hồ sơ mẫu | 
| ----- | ----- | ----- | ----- | 
| **Quản trị viên / Giáo viên** | `engineer` | `123456` | Toàn quyền quản lý ngân hàng 200 câu hỏi, tập luật, học viên, bài làm và kiểm định độ khó. | 
| **Học viên 1 (Trung bình - Khá)** | `sv001` | `123456` | Mạnh Đạo hàm cơ bản (88%), nhưng đang yếu Đạo hàm hàm hợp (38%) và Oxi hóa - Khử (29%). | 
| **Học viên 2 (Giỏi)** | `sv002` | `123456` | Nắm vững cả 6 chuyên đề, hệ thống sẽ tự động gợi ý đề mức Khá - Khó. | 
| **Học viên 3 (Lệch môn)** | `sv003` | `123456` | Yếu môn Toán nhưng rất giỏi môn Hóa học. | 
| **Học viên 4 (Cần củng cố)** | `sv004` | `123456` | Năng lực nền tảng còn thấp ở cả 2 môn, hệ thống ưu tiên rút trích câu Dễ và Trung bình. | 

### 9.2. Kịch bản thuyết trình & Demo 5 phút trước Hội đồng

1. **Bước 1 — Demo Phân quyền Học viên (`sv001` / `123456`):**

   * Tại **Trang chủ**, chỉ vào bảng *Tiến độ 6 chuyên đề* và phần *Khuyến nghị ôn tập* để cho thấy hệ suy diễn lùi phát hiện `sv001` đang yếu phần Đạo hàm hàm hợp và khuyên ôn lại Đạo hàm cơ bản.

   * Chuyển sang mục **Tạo đề**: Chọn môn *Toán học* $\rightarrow$ Chuyên đề *Định nghĩa đạo hàm & Tiếp tuyến* $\rightarrow$ Quy tắc *Đạo hàm lũy thừa* $x^n$ $\rightarrow$ Dạng bài *Tính giá trị đạo hàm tại điểm* để chứng minh bộ lọc tri thức 3 tầng hoạt động thông minh, không bị lẫn câu hỏi Hóa học.

   * Bấm **Khởi tạo đề thi** $\rightarrow$ **Bắt đầu làm bài ngay**: Chỉ vào **đồng hồ đếm giây trực tiếp** góc phải trên và các công thức $\text{LaTeX}$ sắc nét. Chọn đáp án, bấm **Nộp bài** để xem điểm năng lực mới kèm *Cách làm tổng quát* từng câu.

2. **Bước 2 — Demo Phân quyền Kỹ sư tri thức / Giáo viên (`engineer` / `123456`):**

   * Tại **Tổng quan**: Trình bày bảng phân bố 200 câu hỏi trên 6 chuyên đề và thử Thêm/Sửa/Xóa một luật suy diễn trong `LuatSuyDien.txt`.

   * Tại **Câu hỏi**:

     * Tab *Danh sách*: Lọc thử theo từng quy tắc công thức ($x^n$, $u \cdot v$, $\frac{u}{v}$, $a^x$, bảo toàn e...).

     * Tab *Sửa / Xóa (CRUD)*: Chọn 1 câu hỏi bất kỳ, sửa nội dung hoặc đáp án và lưu lại.

     * Tab *Sinh tự động SymPy*: Chọn 1 quy tắc công thức và đổi giữa 4 mẫu câu dẫn (`R_TRANS_STEM`), bấm sinh tự động để thấy `SymPy` tự tính đạo hàm/nguyên hàm và tạo phương án nhiễu.

   * Tại **Độ khó**: Bấm nút **Hiệu chỉnh tự động độ khó vào Knowledge.txt** để chứng minh khả năng tự học và cập nhật độ khó từ dữ liệu làm bài thực tế.
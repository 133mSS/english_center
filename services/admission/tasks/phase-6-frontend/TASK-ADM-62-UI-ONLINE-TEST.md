# TASK-ADM-62: Giao diện Làm bài Khảo thí Trực tuyến Đếm ngược & Tra cứu (test.html)

- **Mã nhiệm vụ**: `TASK-ADM-62`
- **Phân kỳ**: `Phase 6: Giao diện Người dùng Frontend (UI)`
- **Độ ưu tiên**: `P1`
- **Yêu cầu chức năng liên quan**: `FR-TST-01` đến `FR-TST-05`
- **Quy chuẩn lập trình**: `Vanilla Web & Design System`

---

## 1. Mục tiêu Nghiệp vụ & Kỹ thuật
Xây dựng Cổng Khảo thí Trực tuyến (Online Entrance Placement Test Portal) thân thiện cho thí sinh mới:
1. **Màn hình Tiếp nhận Thông tin (Pre-exam Screen)**:
   - Thí sinh nhập: Họ tên, Email, Số điện thoại.
   - Chọn bài test hoặc làm đề thi chuẩn mặc định (45 phút).
   - Xem hướng dẫn làm bài và nhấn nút "Bắt đầu làm bài".
2. **Màn hình Phòng thi Trực tuyến (Exam In-Progress Screen)**:
   - **Đồng hồ Đếm ngược Nổi (Sticky Countdown Timer)**: Hiển thị thời gian làm bài còn lại (ví dụ: `44:59`). Khi thời gian về `00:00`, tự động khóa form và gửi bài nộp ngay lập tức.
   - Thanh điều hướng câu hỏi (Question Palette): 1, 2, 3... 40 (đổi màu xanh khi câu hỏi đã được chọn đáp án).
   - Phần thi Listening: Khung phát âm thanh audio kèm thanh điều khiển.
   - Phần thi Reading: Khung đọc văn bản có thanh cuộn độc lập bên cạnh câu hỏi.
   - Phần thi Grammar: Câu hỏi trắc nghiệm 4 lựa chọn (A/B/C/D) dễ bấm.
   - Nút "Nộp bài" có hộp thoại xác nhận số câu đã làm / chưa làm.
3. **Màn hình Kết quả & Đề xuất Lộ trình (Post-exam Result Screen)**:
   - Hiển thị bảng điểm bóc tách: Điểm Nghe, Điểm Đọc, Điểm Ngữ pháp và Tổng điểm.
   - Khóa học đề xuất phù hợp nhất kèm ghi chú tư vấn học vụ.
   - Nút **"Đăng ký Nhập học Ngay"** (giữ chỗ 48h cho lớp học sắp khai giảng của khóa học đó).

---

## 2. Phạm vi File Tác động

### File tạo mới hoặc chỉnh sửa:
- `services/admission/frontend/test.html`
- `services/admission/frontend/js/test-exam.js`
- `services/admission/frontend/css/test-exam.css` (nếu cần bố cục chia đôi màn hình)

---

## 3. Kế hoạch Triển khai (Step-by-step)
1. Xây dựng cấu trúc Single Page Application (SPA) trên `test.html` với 3 view: `#view-intro`, `#view-exam`, `#view-result`.
2. Viết hàm JavaScript:
   - `startTest()`: Gọi API lấy đề thi, ẩn intro và hiển thị exam view, khởi động timer đếm ngược.
   - `renderQuestions()`: Phân chia 3 tab hoặc hiển thị theo thứ tự từng kỹ năng.
   - `handleSelectAnswer(qId, option)`: Lưu câu trả lời vào mảng `studentAnswers`, cập nhật màu sắc trên Question Palette.
   - `submitExam()`: Thu thập câu trả lời, gọi `api.post('/api/admission/tests/public/submit', payload)`.
   - `displayResult(data)`: Hiển thị điểm số từng kỹ năng, khóa học đề xuất và các lớp có sẵn.
3. Đảm bảo âm thanh file nghe phát mượt mà trên các trình duyệt.

---

## 4. Tiêu chí Nghiệm thu (Acceptance Criteria)
- [ ] Thí sinh làm bài thi hiển thị đồng hồ đếm ngược chính xác, khi hết giờ bài tự động nộp thành công.
- [ ] Nộp bài xong hiển thị ngay điểm số chi tiết từng phần thi và lộ trình khóa học đề xuất.
- [ ] Bấm nút "Đăng ký Nhập học Ngay" chuyển hướng mượt mà sang form tuyển sinh giữ chỗ 48h.

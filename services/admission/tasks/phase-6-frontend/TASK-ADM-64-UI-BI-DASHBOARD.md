# TASK-ADM-64: Dashboard Trực quan hóa Báo cáo BI Tuyển sinh (bi-dashboard.html)

- **Mã nhiệm vụ**: `TASK-ADM-64`
- **Phân kỳ**: `Phase 6: Giao diện Người dùng Frontend (UI)`
- **Độ ưu tiên**: `P2`
- **Yêu cầu chức năng liên quan**: `BI-01`, `BI-02`, `BI-03`, `BI-FUN-01..04`, `BI-REV-01..02`, `BI-OCC-01`
- **Quy chuẩn lập trình**: `Vanilla Web & Design System` (Vanilla JS, CSS Variables, SVG/Canvas thuần hoặc thư viện biểu đồ nhẹ nếu có)

---

## 1. Mục tiêu Nghiệp vụ & Kỹ thuật
Xây dựng Trung tâm Báo cáo Trực quan Hóa (BI Executive Dashboard) phục vụ Ban Giám đốc và Trưởng phòng Tuyển sinh theo dõi các chỉ số thời gian thực:
1. **Các Thẻ Chỉ số Tổng quan (Metric KPI Cards)**:
   - **Doanh thu Tiềm năng 48h (Pipeline Revenue)**: Hiển thị giá trị tiền kèm số đơn `PENDING` còn hạn.
   - **Doanh thu Thực tế Trong kỳ (Realized Revenue)**: Hiển thị tổng tiền từ các đơn `APPROVED`.
   - **Tỷ lệ Lấp đầy Trung bình (Average Occupancy Rate)**: Tỷ lệ % có thanh tiến độ (Progress bar).
   - **Tỷ lệ Chuyển đổi Thanh toán (Paid Conversion Rate)**: Tỷ lệ % đơn thành công.
2. **Biểu đồ Phễu Chuyển Đổi (Admissions Funnel Chart)**:
   - Thể hiện trực quan 4 bước: Test $\rightarrow$ Nộp bài $\rightarrow$ Giữ chỗ 48h $\rightarrow$ Đã thanh toán.
   - Hiển thị tỷ lệ rơi rớt (Drop-off Rate) tại từng bước để nhanh chóng phát hiện điểm nghẽn.
3. **Bảng Xếp hạng Khóa học Hàng đầu (Top Courses Table)**:
   - Danh sách khóa học có lượng đăng ký tuyển sinh cao nhất kèm doanh thu tiềm năng và thực thu.
4. **Bộ Lọc Khoảng Thời Gian (Date Filter)**:
   - Bộ chọn thời gian: Hôm nay, 7 ngày qua, Tháng này, hoặc Tùy chọn khoảng ngày.

---

## 2. Phạm vi File Tác động

### File tạo mới hoặc chỉnh sửa:
- `services/admission/frontend/bi-dashboard.html`
- `services/admission/frontend/js/bi-dashboard.js`
- `services/admission/frontend/css/bi-dashboard.css`

### Thư viện và tài nguyên dùng chung:
- `/shared/css/variables.css`
- `/shared/css/components.css`
- `/shared/js/auth.js`
- `/shared/js/api.js`

---

## 3. Kế hoạch Triển khai (Step-by-step)
1. Bố cục trang theo dạng Grid Dashboard (Thẻ KPI phía trên, Biểu đồ phễu ở giữa, Bảng chi tiết bên dưới).
2. Viết hàm JavaScript:
   - `loadDashboardData(fromDate, toDate)`:
     - Gọi đồng thời `api.get('/api/admission/bi/funnel')` và `api.get('/api/admission/bi/courses-revenue')`.
     - Render số liệu lên các thẻ KPI.
     - Vẽ biểu đồ thanh ngang phễu chuyển đổi bằng HTML/CSS thuần (sử dụng width % và màu sắc gradient).
     - Render bảng xếp hạng khóa học.
   - `handleFilterChange()`: Tải lại dữ liệu khi người dùng thay đổi ngày tháng.
3. Sử dụng các biến màu từ design system: `--color-primary`, `--color-success`, `--color-warning`.

---

## 4. Tiêu chí Nghiệm thu (Acceptance Criteria)
- [ ] Mở trang `http://localhost:8080/admission/bi-dashboard.html` hiển thị đầy đủ các chỉ số thống kê.
- [ ] Biểu đồ phễu trực quan, thể hiện rõ tỷ lệ chuyển đổi qua các giai đoạn.
- [ ] Đổi bộ lọc ngày tháng $\rightarrow$ Dữ liệu trên toàn dashboard được làm mới tương ứng.

# TASK-ADM-61: Giao diện Bàn Tuyển sinh, Giữ chỗ 48h & Xét duyệt (enrollments.html)

- **Mã nhiệm vụ**: `TASK-ADM-61`
- **Phân kỳ**: `Phase 6: Giao diện Người dùng Frontend (UI)`
- **Độ ưu tiên**: `P0 (Bắt buộc)`
- **Yêu cầu chức năng liên quan**: `FR-ENR-01` đến `FR-ENR-07`
- **Quy chuẩn lập trình**: `Vanilla Web & Design System`

---

## 1. Mục tiêu Nghiệp vụ & Kỹ thuật
Xây dựng giao diện trung tâm làm việc hàng ngày của Nhân viên tuyển sinh & Học vụ (Admissions Desk):
1. **Bảng Danh sách Đơn đăng ký Tuyển sinh**:
   - Hiển thị danh sách đơn kèm: Mã đơn (`ENR-xxxx`), Tên học viên, Số điện thoại, Email, Lớp học đăng ký, Trạng thái đơn (`PENDING`, `APPROVED`, `CANCELLED`, `EXPIRED`), Thời gian tạo đơn.
   - **Đồng hồ Đếm ngược Giữ chỗ 48h**: Đối với đơn `PENDING`, hiển thị thời gian giữ chỗ còn lại (ví dụ: `23h 45m` màu cam; nếu dưới 4h chuyển sang màu đỏ cảnh báo).
2. **Bộ Thao tác Hành động Nhanh (Action Buttons)**:
   - Nút **"Duyệt Tiền Mặt"** (Mở modal nhập số phiếu thu và số tiền nhận được).
   - Nút **"Gia Hạn 48h"** (Mở modal chọn số giờ gia hạn và lý do).
   - Nút **"Hủy Đơn"** (Xác nhận hủy đơn để giải phóng slot giữ chỗ).
   - Nút **"Xuất Excel Danh sách"** (Gọi API xuất CSV/Excel tải về máy).
3. **Form Tiếp Đón Trực Tiếp Tại Quầy ("Tạo Đơn Tuyển Sinh Mới")**:
   - Nhân viên nhập nhanh thông tin học viên và chọn lớp học còn slot trống để tạo đơn ngay tại bàn tư vấn.

---

## 2. Phạm vi File Tác động

### File tạo mới hoặc chỉnh sửa:
- `services/admission/frontend/enrollments.html`
- `services/admission/frontend/js/enrollments.js`

### Thư viện và tài nguyên dùng chung:
- `/shared/css/variables.css`
- `/shared/css/components.css`
- `/shared/js/auth.js`
- `/shared/js/api.js`

---

## 3. Kế hoạch Triển khai (Step-by-step)
1. Xây dựng bộ lọc trạng thái: Tất cả, Đang giữ chỗ (`PENDING`), Đã nhập học (`APPROVED`), Đã hủy (`CANCELLED`), Hết hạn (`EXPIRED`).
2. Viết hàm JavaScript:
   - `loadEnrollments(filter)`: Gọi `api.get('/api/admission/enrollments')`.
   - `startCountdownTimers()`: Chạy `setInterval` mỗi 1 giây để cập nhật thời gian đếm ngược của các đơn `PENDING` trên bảng.
   - `handleManualApprove(id)`: Gọi `api.post('/api/admission/enrollments/' + id + '/approve-manual', payload)`. Bắt lỗi `ADM_CLASS_FULL` nếu lớp đã đầy và cảnh báo người dùng.
   - `handleExtendHold(id)`: Gọi `api.post('/api/admission/enrollments/' + id + '/extend-hold', payload)`.
   - `handleExportRoster(classId)`: Kích hoạt tải file CSV qua trình duyệt.
3. Sử dụng Design Tokens: `--color-warning` cho `PENDING`, `--color-success` cho `APPROVED`, `--color-danger` cho `CANCELLED`/`EXPIRED`.

---

## 4. Tiêu chí Nghiệm thu (Acceptance Criteria)
- [ ] Giao diện tải và hiển thị danh sách đơn mượt mà, đồng hồ đếm ngược chạy từng giây chính xác.
- [ ] Bấm nút duyệt tiền mặt $\rightarrow$ Đơn chuyển sang `APPROVED`, badge đổi sang màu xanh lá cây tức thì.
- [ ] Nếu lớp học đã đủ sĩ số trần, nút duyệt bị từ chối và hiển thị thông báo lỗi rõ ràng.
- [ ] Giao diện responsive trên cả máy tính bàn và máy tính bảng tại quầy tuyển sinh.

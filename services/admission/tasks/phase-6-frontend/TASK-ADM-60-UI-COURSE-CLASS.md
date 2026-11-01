# TASK-ADM-60: Giao diện Quản lý Khóa học & Lớp học (courses.html, classes.html)

- **Mã nhiệm vụ**: `TASK-ADM-60`
- **Phân kỳ**: `Phase 6: Giao diện Người dùng Frontend (UI)`
- **Độ ưu tiên**: `P1`
- **Yêu cầu chức năng liên quan**: `FR-ACA-01`, `FR-ACA-02`, `FR-ACA-04`, `FR-FAC-03`
- **Quy chuẩn lập trình**: `Vanilla Web & Design System` (Vanilla JS, CSS Variables từ `/shared/css/variables.css`, không build tool)

---

## 1. Mục tiêu Nghiệp vụ & Kỹ thuật
Hoàn thiện giao diện web quản lý danh mục đào tạo cho Học vụ và Quản trị viên:
1. **Trang Quản lý Khóa học (`services/admission/frontend/courses.html`)**:
   - Hiển thị danh sách khóa học dạng bảng hoặc lưới card (Mã khóa, Tên khóa, Trình độ, Học phí, Thời lượng).
   - Nút "Thêm khóa học mới": Mở modal nhập thông tin có validation phía client.
   - Nút sửa thông tin và nút ngưng hoạt động.
2. **Trang Quản lý Lớp học (`services/admission/frontend/classes.html`)**:
   - Hiển thị danh sách lớp học kèm thông tin: Tên lớp, Khóa học, Phòng học, Giáo viên phụ trách, Lịch học (Ca & Ngày trong tuần), Sĩ số hiện tại / Sĩ số trần (`current / max`), Trạng thái (`OPEN`, `IN_PROGRESS`, `COMPLETED`, `CANCELLED`).
   - Modal "Mở lớp học mới": Tự động tải danh sách Khóa học, Phòng học và Giáo viên để người dùng chọn từ Dropdown; kiểm tra trước sức chứa phòng và cảnh báo xung đột lịch.
   - Badge trạng thái trực quan: Màu xanh lá cho `OPEN`, xanh dương cho `IN_PROGRESS`, xám cho `COMPLETED`, đỏ cho `CANCELLED`.

---

## 2. Phạm vi File Tác động

### File tạo mới hoặc chỉnh sửa:
- `services/admission/frontend/courses.html`
- `services/admission/frontend/classes.html`
- `services/admission/frontend/js/courses.js` (hoặc nhúng trong thẻ script nếu đơn giản)
- `services/admission/frontend/js/classes.js`

### Thư viện và tài nguyên dùng chung:
- `/shared/css/variables.css`
- `/shared/css/base.css`
- `/shared/css/components.css`
- `/shared/css/layout.css`
- `/shared/js/auth.js`
- `/shared/js/api.js`
- `/shared/js/layout.js`

---

## 3. Kế hoạch Triển khai (Step-by-step)
1. Cấu trúc khung HTML sử dụng thẻ chuẩn ngữ nghĩa (`main`, `header`, `section`, `table`).
2. Nhúng đầy đủ các file CSS và JS từ `/shared/`.
3. Viết hàm JavaScript:
   - `loadCourses()`: Gọi `api.get('/api/admission/courses')`, render HTML table.
   - `handleCreateCourse()`: Lấy form data, gọi `api.post('/api/admission/courses', payload)`, hiển thị Toast thông báo và reload danh sách.
   - `loadClasses()`: Gọi `api.get('/api/admission/classes')`, hiển thị badge sĩ số `approved / max`.
   - `handleCreateClass()`: Bắt lỗi nếu API trả về `ADM_ROOM_CAPACITY_EXCEEDED` hoặc `ADM_ROOM_CONFLICT` và hiển thị thông báo lỗi thân thiện trên form modal.
4. Kiểm tra trải nghiệm trên trình duyệt (F5 hot reload qua Nginx Gateway).

---

## 4. Tiêu chí Nghiệm thu (Acceptance Criteria)
- [ ] Mở giao diện trên trình duyệt qua Nginx `http://localhost:8080/admission/courses.html` và `classes.html` hiển thị chuẩn đẹp, đồng bộ với layout chung.
- [ ] Thêm khóa học và mở lớp thành công, dữ liệu cập nhật tức thì lên bảng.
- [ ] Nhập lớp có sĩ số vượt sức chứa phòng $\rightarrow$ Giao diện hiển thị thông báo lỗi rõ ràng từ trường `error.message`.

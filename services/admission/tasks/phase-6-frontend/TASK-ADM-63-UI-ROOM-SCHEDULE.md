# TASK-ADM-63: Giao diện Quản lý Phòng học & Lịch phân ca (rooms.html)

- **Mã nhiệm vụ**: `TASK-ADM-63`
- **Phân kỳ**: `Phase 6: Giao diện Người dùng Frontend (UI)`
- **Độ ưu tiên**: `P2`
- **Yêu cầu chức năng liên quan**: `FR-FAC-01`, `FR-FAC-02`, `FR-FAC-03`
- **Quy chuẩn lập trình**: `Vanilla Web & Design System`

---

## 1. Mục tiêu Nghiệp vụ & Kỹ thuật
Xây dựng giao diện quản lý cơ sở vật chất và bố trí phòng học:
1. **Quản lý Danh sách Phòng học (`admission.rooms`)**:
   - Hiển thị danh mục phòng học theo chi nhánh cơ sở.
   - Thể hiện trực quan sức chứa tối đa của từng phòng (`capacity`).
   - Cho phép thêm mới phòng học, sửa tên phòng, cập nhật sức chứa hoặc tạm ngưng hoạt động phòng đang sửa chữa.
2. **Bảng Thời Khóa Biểu Phòng Học (Room Schedule Grid)**:
   - Hiển thị lịch phân bổ phòng học trực quan theo ma trận: Dòng là Ca học (Ca 1 đến Ca 6), Cột là Ngày trong tuần (Thứ 2 đến Chủ nhật).
   - Ô có lớp học đang chiếm chỗ hiển thị tên lớp, khóa học, giáo viên và sĩ số. Giúp nhân viên học vụ dễ dàng nhận biết phòng nào đang trống ca nào để xếp lớp mới mà không bị xung đột.

---

## 2. Phạm vi File Tác động

### File tạo mới hoặc chỉnh sửa:
- `services/admission/frontend/rooms.html`
- `services/admission/frontend/js/rooms.js`

---

## 3. Kế hoạch Triển khai (Step-by-step)
1. Xây dựng giao diện danh sách phòng học và modal thêm phòng mới.
2. Xây dựng grid thời khóa biểu ca học tuần.
3. Viết hàm JavaScript:
   - `loadRooms()`: Gọi API lấy danh sách phòng.
   - `loadRoomSchedule(roomId)`: Gọi API lấy các lớp đang mở trong phòng đó và vẽ lên lưới lịch học.
   - `handleCreateRoom()`: Gửi request tạo phòng mới.
4. Tích hợp Design Tokens từ `/shared/css/variables.css`.

---

## 4. Tiêu chí Nghiệm thu (Acceptance Criteria)
- [ ] Nhân viên thêm phòng học mới thành công, hiển thị đầy đủ trên danh mục.
- [ ] Lưới lịch học thể hiện rõ ràng các ca đã có lớp và các ca còn trống của phòng.
- [ ] Giao diện trực quan, dễ thao tác và không phát sinh lỗi console JavaScript.

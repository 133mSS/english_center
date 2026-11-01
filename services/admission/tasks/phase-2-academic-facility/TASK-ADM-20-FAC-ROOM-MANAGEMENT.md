# TASK-ADM-20: Quản lý Danh mục Phòng học, Ca học & Mẫu Ngày học

- **Mã nhiệm vụ**: `TASK-ADM-20`
- **Phân kỳ**: `Phase 2: Cơ sở vật chất & Đào tạo (FAC/ACA)`
- **Độ ưu tiên**: `P1`
- **Yêu cầu chức năng liên quan**: `FR-FAC-01`, `FR-FAC-02`
- **Quy tắc bất biến bảo vệ**: `INV-SYS-01`

---

## 1. Mục tiêu Nghiệp vụ & Kỹ thuật
Xây dựng phân hệ quản lý tài nguyên cơ sở vật chất phục vụ công tác xếp lớp học:
1. **CRUD Danh mục Phòng học (`admission.rooms`)**:
   - Thêm mới, chỉnh sửa, xem danh sách và kích hoạt/vô hiệu hóa phòng học.
   - Các trường thông tin: Mã phòng (`code`, duy nhất), Tên phòng (`name`), Sức chứa tối đa (`capacity >= 1`), Chi nhánh (`branch_name`), Trạng thái hoạt động (`is_active`).
2. **Cấu hình Ca học & Mẫu ngày học tiêu chuẩn**:
   - Định nghĩa các ca học tiêu chuẩn (Shift):
     - `CA_1`: 08:00 - 09:30
     - `CA_2`: 09:45 - 11:15
     - `CA_3`: 14:00 - 15:30
     - `CA_4`: 15:45 - 17:15
     - `CA_5`: 17:45 - 19:15
     - `CA_6`: 19:30 - 21:00
   - Định nghĩa các mẫu ngày trong tuần (`day_pattern`):
     - `MON_WED_FRI`: Thứ 2, 4, 6
     - `TUE_THU_SAT`: Thứ 3, 5, 7
     - `SAT_SUN`: Thứ 7, Chủ nhật
     - `DAILY`: Tất cả các ngày trong tuần

---

## 2. Phạm vi File Tác động

### File tạo mới hoặc chỉnh sửa:
- `services/admission/backend/src/main/java/com/englishcenter/admission/controller/RoomController.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/service/RoomService.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/service/impl/RoomServiceImpl.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/repository/RoomRepository.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/entity/Room.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/dto/room/CreateRoomRequest.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/dto/room/UpdateRoomRequest.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/dto/room/RoomResponse.java`

---

## 3. Đặc tả API Hợp đồng

### 3.1. Thêm mới Phòng học
- **URL**: `POST /api/admission/rooms`
- **Header**: `Authorization: Bearer <Staff/Admin_Token>`
- **Request Body**:
  ```json
  {
    "code": "ROOM-P201",
    "name": "Phòng Lab 201",
    "capacity": 25,
    "branch_name": "Cơ sở Cầu Giấy"
  }
  ```
- **Validation**:
  - `code`: Không được rỗng, tối đa 50 ký tự, không được trùng với phòng đã có (trả về 409 `ADM_ROOM_CODE_EXISTS`).
  - `capacity`: Bắt buộc là số nguyên dương $\ge 1$ (`@Min(1)`).

### 3.2. Lấy Danh sách Phòng học
- **URL**: `GET /api/admission/rooms`
- **Query Params**: `branch_name`, `is_active`, `min_capacity`
- **Response**: Trả về mảng danh sách phòng học sắp xếp theo mã phòng.

---

## 4. Kế hoạch Triển khai (Step-by-step)
1. Tạo Entity `Room.java` có annotation JPA và các trường theo đúng DDL schema `admission.rooms`.
2. Tạo `RoomRepository` với method `boolean existsByCode(String code)`.
3. Trong `RoomServiceImpl`:
   - Viết các phương thức: `createRoom`, `updateRoom`, `getRooms`, `toggleRoomActive`.
   - Kiểm tra mã trùng trước khi thêm/sửa, ném lỗi nghiệp vụ rõ ràng.
4. Trong `RoomController`: Khai báo các endpoints RESTful với phân quyền `hasAnyRole('ADMIN', 'STAFF')`.
5. Viết comment tiếng Việt đầy đủ.

---

## 5. Tiêu chí Nghiệm thu (Acceptance Criteria)
- [ ] Tạo phòng học với `capacity = 0` hoặc âm $\rightarrow$ Bị chặn ngay từ tầng validation với mã lỗi 400.
- [ ] Tạo phòng học với mã trùng lặp $\rightarrow$ Trả về mã lỗi HTTP 409 `ADM_ROOM_CODE_EXISTS`.
- [ ] Lấy danh sách phòng theo chi nhánh hoạt động chuẩn xác, định dạng `snake_case`.

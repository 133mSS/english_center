# TASK-ADM-22: Quản lý Mở Lớp học, Kiểm tra Sức chứa Phòng & Vòng đời Lớp

- **Mã nhiệm vụ**: `TASK-ADM-22`
- **Phân kỳ**: `Phase 2: Cơ sở vật chất & Đào tạo (FAC/ACA)`
- **Độ ưu tiên**: `P0 (Bắt buộc)`
- **Yêu cầu chức năng liên quan**: `FR-ACA-02`, `FR-ACA-04`, `FR-FAC-03`
- **Quy tắc bất biến bảo vệ**: `INV-SYS-01`

---

## 1. Mục tiêu Nghiệp vụ & Kỹ thuật
Xây dựng chức năng quản lý lớp học đào tạo và kiểm soát chặt chẽ giới hạn vật lý của cơ sở vật chất:
1. **Mở lớp học mới (`admission.classes`)**:
   - Gán Khóa học (`course_id`), Phòng học (`room_id`), Giáo viên (`teacher_id`).
   - Cấu hình ca học (`start_time`, `end_time`), mẫu ngày học (`day_pattern`).
   - Ngày khai giảng (`start_date`), ngày bế giảng dự kiến (`end_date`), trong đó `end_date > start_date`.
   - Sĩ số tối thiểu (`min_students`), Sĩ số tối đa (`max_students`).
2. **Ràng buộc Sức chứa Phòng (FR-FAC-03)**:
   - Trước khi tạo lớp, bắt buộc kiểm tra sức chứa của phòng:
     $$\text{class.max\_students} \le \text{room.capacity}$$
   - Nếu `max_students > room.capacity`, hệ thống lập tức từ chối và trả về mã lỗi HTTP 400 `ADM_ROOM_CAPACITY_EXCEEDED`.
3. **Quản lý Vòng đời Lớp học (FR-ACA-04)**:
   - Các trạng thái hợp lệ: `OPEN` (Đang tuyển sinh) $\rightarrow$ `IN_PROGRESS` (Đang diễn ra) $\rightarrow$ `COMPLETED` (Đã bế giảng), hoặc `CANCELLED` (Hủy lớp nếu không đủ sĩ số).
   - Không được phép mở tuyển sinh cho lớp đã `COMPLETED` hoặc `CANCELLED`.

---

## 2. Phạm vi File Tác động

### File tạo mới hoặc chỉnh sửa:
- `services/admission/backend/src/main/java/com/englishcenter/admission/controller/ClassController.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/service/ClassService.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/service/impl/ClassServiceImpl.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/repository/ClassRepository.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/entity/ClassEntity.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/dto/clazz/CreateClassRequest.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/dto/clazz/UpdateClassStatusRequest.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/dto/clazz/ClassResponse.java`

---

## 3. Đặc tả API Hợp đồng

### 3.1. Tạo mới Lớp học
- **URL**: `POST /api/admission/classes`
- **Header**: `Authorization: Bearer <Staff/Admin_Token>`
- **Request Body**:
  ```json
  {
    "course_id": 1,
    "room_id": 2,
    "teacher_id": "USR-2026-0005",
    "name": "Lớp IELTS 6.5 Sáng 2-4-6",
    "day_pattern": "MON_WED_FRI",
    "start_time": "08:00:00",
    "end_time": "09:30:00",
    "start_date": "2026-11-15",
    "end_date": "2027-02-15",
    "min_students": 10,
    "max_students": 20
  }
  ```
- **Xử lý Kiểm tra Sức chứa**:
  - Tra cứu `room` theo `room_id`. Nếu không tồn tại $\rightarrow$ 404 `ADM_ROOM_NOT_FOUND`.
  - Nếu `request.getMaxStudents() > room.getCapacity()`:
    ```json
    {
      "success": false,
      "error": {
        "code": "ADM_ROOM_CAPACITY_EXCEEDED",
        "message": "Sĩ số lớp (25) vượt quá sức chứa tối đa của phòng học (20)"
      }
    }
    ```

### 3.2. Cập nhật Trạng thái Vòng đời Lớp
- **URL**: `PATCH /api/admission/classes/{id}/status`
- **Request Body**:
  ```json
  {
    "status": "IN_PROGRESS"
  }
  ```

---

## 4. Kế hoạch Triển khai (Step-by-step)
1. Tạo JPA Entity `ClassEntity` ánh xạ vào bảng `admission.classes`.
2. Trong `ClassServiceImpl`:
   - Viết logic `createClass`:
     - Kiểm tra tồn tại của Course, Room, Teacher (Teacher phải có `role = 'TEACHER'`).
     - Kiểm tra `request.max_students <= room.capacity`. Nếu không thỏa mãn $\rightarrow$ Ném `BusinessException(ErrorCode.ADM_ROOM_CAPACITY_EXCEEDED)`.
     - Gọi `ConflictEngine` để kiểm tra trùng lịch phòng và giáo viên (xem TASK-ADM-23).
     - Khởi tạo trạng thái mặc định `OPEN`.
3. Viết comment tiếng Việt chi tiết cho từng luồng nghiệp vụ.

---

## 5. Tiêu chí Nghiệm thu (Acceptance Criteria)
- [ ] Mở lớp với phòng có sức chứa 15 nhưng đặt `max_students = 20` $\rightarrow$ Nhận lỗi HTTP 400 kèm mã `ADM_ROOM_CAPACITY_EXCEEDED`.
- [ ] Mở lớp với `start_date >= end_date` $\rightarrow$ Bị chặn với mã lỗi HTTP 400 Validation Error.
- [ ] Chuyển trạng thái lớp sang `COMPLETED` thành công khi kết thúc khóa học.

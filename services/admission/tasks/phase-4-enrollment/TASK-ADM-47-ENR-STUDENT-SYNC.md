# TASK-ADM-47: Tự động Đồng bộ Hồ sơ Học viên sang Student Service khi Duyệt Thành công

- **Mã nhiệm vụ**: `TASK-ADM-47`
- **Phân kỳ**: `Phase 4: Tuyển sinh, Giữ chỗ 48h & Xét duyệt (ENR)`
- **Độ ưu tiên**: `P0 (Bắt buộc)`
- **Yêu cầu chức năng liên quan**: `FR-ENR-08`
- **Quy tắc bất biến bảo vệ**: `INV-SYS-02` (Giao tiếp liên service qua API REST)

---

## 1. Mục tiêu Nghiệp vụ & Kỹ thuật
Bảo đảm tính liên tục của luồng nghiệp vụ giữa Tuyển sinh và Học vụ: Ngay khi một đơn đăng ký được xét duyệt thành công (`status = APPROVED`), hệ thống phải tự động đồng bộ thông tin sang **Student Service** (Port 8082) để:
1. Tạo mới hồ sơ học viên chính thức trong schema `student.students` (nếu chưa có).
2. Xếp học viên vào danh sách lớp học của phân hệ quản lý học tập (`student.class_enrollments`).
3. Đảm bảo tính nhất quán cuối cùng (Eventual Consistency):
   - Nếu Student Service tạm thời bận hoặc lỗi mạng, hệ thống ghi nhận cờ `synced_to_student_service = false` và thực hiện retry qua Scheduled Job nền thay vì làm rollback giao dịch duyệt đơn.

---

## 2. Phạm vi File Tác động

### File tạo mới hoặc chỉnh sửa:
- `services/admission/backend/src/main/java/com/englishcenter/admission/client/StudentServiceClient.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/helper/StudentServiceSyncHelper.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/entity/Enrollment.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/service/impl/EnrollmentServiceImpl.java`

---

## 3. Đặc tả Hợp đồng REST Tích hợp

### Request sang Student Service:
- **Method**: `POST http://student-service:8082/api/student/students`
- **Request Body**:
  ```json
  {
    "user_id": "USR-2026-0045",
    "full_name": "Tran Thi Mai",
    "email": "mai.tran@gmail.com",
    "phone": "0988776655",
    "enrolled_class_id": "CLS-2026-0010",
    "enrollment_id": "ENR-2026-0089"
  }
  ```
- **Response Kỳ vọng từ Student Service (HTTP 201 Created)**:
  ```json
  {
    "success": true,
    "data": {
      "student_id": 105,
      "student_code": "STU-2026-0045",
      "status": "ACTIVE"
    },
    "message": "Đã tạo hồ sơ học viên thành công"
  }
  ```

---

## 4. Kế hoạch Triển khai (Step-by-step)
1. Thêm trường `is_synced_to_student` (boolean, default false) vào thực thể `Enrollment`.
2. Xây dựng component `StudentServiceSyncHelper.java`:
   - Phương thức `@Async public void syncStudentProfile(Enrollment enrollment)`.
   - Chuẩn bị payload và gọi qua `StudentServiceClient`.
   - Khi nhận phản hồi 2xx $\rightarrow$ Đánh dấu `enrollment.setIsSyncedToStudent(true)`.
   - Bắt các lỗi `RestClientException` $\rightarrow$ Ghi log cảnh báo `WARN`, để cờ `false` cho job retry định kỳ quét lại.
3. Tích hợp gọi helper này ngay sau khi `approveEnrollment` lưu DB thành công.
4. Viết comment tiếng Việt chi tiết.

---

## 5. Tiêu chí Nghiệm thu (Acceptance Criteria)
- [ ] Duyệt đơn thành công $\rightarrow$ Gửi request HTTP POST chính xác sang Student Service với định dạng `snake_case`.
- [ ] Khi Student Service phản hồi 201 Created $\rightarrow$ Cờ đồng bộ trong đơn được cập nhật thành `true`.
- [ ] Khi Student Service tạm thời offline $\rightarrow$ Việc duyệt đơn của Admission Service vẫn hoàn tất, không bị rollback hay crash 500.

# TASK-ADM-40: Đăng ký Tuyển sinh Đa kênh (Online & Trực tiếp tại Quầy)

- **Mã nhiệm vụ**: `TASK-ADM-40`
- **Phân kỳ**: `Phase 4: Tuyển sinh, Giữ chỗ 48h & Xét duyệt (ENR)`
- **Độ ưu tiên**: `P0 (Bắt buộc)`
- **Yêu cầu chức năng liên quan**: `FR-ENR-01`, `FR-ENR-02`, `FR-ENR-03`
- **Quy tắc bất biến bảo vệ**: `INV-ADM-01`, `INV-SYS-01`

---

## 1. Mục tiêu Nghiệp vụ & Kỹ thuật
Xây dựng luồng tiếp nhận đơn đăng ký nhập học đa kênh cho học viên:
1. **Kênh Trực tuyến (Online Portal)**: Học viên tự truy cập website tuyển sinh, chọn lớp học và điền thông tin đăng ký (Họ tên, Email, Số điện thoại, Ghi chú).
2. **Kênh Trực tiếp tại Quầy (Admissions Desk)**: Nhân viên học vụ tiếp đón phụ huynh/học viên tại văn phòng trung tâm và tạo đơn đăng ký trên hệ thống quản trị.
3. **Quy trình tiếp nhận đơn**:
   - Tự động sinh/tra cứu tài khoản người dùng `STUDENT` theo email (gọi `UserService.getOrCreateStudentUser`).
   - Kiểm tra lớp học có ở trạng thái `OPEN` hay không.
   - Kiểm tra slot khả dụng của lớp: Nếu lớp đã hết chỗ trống ($\text{Available Slots} \le 0$) $\rightarrow$ Từ chối tạo đơn với mã lỗi `ADM_CLASS_FULL`.
   - Sinh mã đơn đăng ký dạng `ENR-yyyy-XXXX`.
   - Thiết lập trạng thái ban đầu là `PENDING`.
   - Gán thời hạn giữ chỗ: `hold_expires_at = NOW() + 48 HOURS`.
   - Gọi Finance Service để tạo hóa đơn học phí tương ứng (hoặc ghi nhận yêu cầu thanh toán).

---

## 2. Phạm vi File Tác động

### File tạo mới hoặc chỉnh sửa:
- `services/admission/backend/src/main/java/com/englishcenter/admission/controller/EnrollmentController.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/service/EnrollmentService.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/service/impl/EnrollmentServiceImpl.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/repository/EnrollmentRepository.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/entity/Enrollment.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/dto/enrollment/CreateEnrollmentRequest.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/dto/enrollment/EnrollmentResponse.java`

---

## 3. Đặc tả API Hợp đồng

### Request: `POST /api/admission/enrollments` (Public hoặc Authenticated)
```json
{
  "class_id": 10,
  "full_name": "Tran Thi Mai",
  "email": "mai.tran@gmail.com",
  "phone": "0988776655",
  "notes": "Đăng ký ca tối 3-5-7"
}
```

### Response Thành công (HTTP 201 Created):
```json
{
  "success": true,
  "data": {
    "enrollment_id": "ENR-2026-0089",
    "class_id": 10,
    "class_name": "IELTS 6.0 Tối 3-5-7",
    "student_id": "USR-2026-0045",
    "student_name": "Tran Thi Mai",
    "status": "PENDING",
    "hold_expires_at": "2026-11-03T21:30:00",
    "created_at": "2026-11-01T21:30:00"
  },
  "message": "Tạo đơn đăng ký thành công, thời gian giữ chỗ của bạn là 48 giờ"
}
```

---

## 4. Kế hoạch Triển khai (Step-by-step)
1. Tạo DTO `CreateEnrollmentRequest` có `@NotNull`, `@NotBlank`, `@Email`.
2. Trong `EnrollmentServiceImpl.createEnrollment`:
   - `@Transactional`: Đảm bảo đồng bộ dữ liệu.
   - Kiểm tra lớp tồn tại và `clazz.getStatus() == ClassStatus.OPEN`.
   - Tính toán slot khả dụng hiện tại (gọi hàm `ClassService.getClassCapacity`).
   - Nếu `capacity.getAvailableSlots() <= 0`: Ném `BusinessException(ErrorCode.ADM_CLASS_FULL)`.
   - Gọi `UserService.getOrCreateStudentUser(email, fullName, phone)`.
   - Tạo thực thể `Enrollment`:
     - Gán `status = EnrollmentStatus.PENDING`.
     - Gán `holdExpiresAt = LocalDateTime.now().plusHours(48)`.
   - Lưu vào `admission.enrollments`.
   - Gọi `FinanceServiceClient` tạo hóa đơn (nếu đã cấu hình).
3. Viết comment tiếng Việt đầy đủ.

---

## 5. Tiêu chí Nghiệm thu (Acceptance Criteria)
- [ ] Tạo đơn cho lớp đang có chỗ trống $\rightarrow$ Nhận mã HTTP 201 Created, `hold_expires_at` đúng bằng thời điểm hiện tại cộng 48 tiếng.
- [ ] Tạo đơn cho lớp đã kín chỗ $\rightarrow$ Trả về mã lỗi HTTP 400 kèm mã `ADM_CLASS_FULL`.
- [ ] Không rò rỉ ngoại lệ 500 khi thông tin đầu vào không hợp lệ.

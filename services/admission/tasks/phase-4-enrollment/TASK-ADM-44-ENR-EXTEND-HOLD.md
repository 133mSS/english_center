# TASK-ADM-44: Tính năng Gia hạn Giữ chỗ Học vụ Kèm Lý do Nghiệp vụ

- **Mã nhiệm vụ**: `TASK-ADM-44`
- **Phân kỳ**: `Phase 4: Tuyển sinh, Giữ chỗ 48h & Xét duyệt (ENR)`
- **Độ ưu tiên**: `P1`
- **Yêu cầu chức năng liên quan**: `FR-ENR-05`
- **Quy tắc bất biến bảo vệ**: `INV-ADM-01`, `INV-SYS-01`

---

## 1. Mục tiêu Nghiệp vụ & Kỹ thuật
Cho phép Nhân viên học vụ (`STAFF`) hoặc Quản trị viên (`ADMIN`) thực hiện gia hạn thêm thời gian giữ chỗ cho học viên khi có lý do chính đáng (ví dụ: học viên chờ chuyển khoản ngân hàng, đang công tác, hoặc phụ huynh xin thêm thời gian):
1. **Kiểm tra tính hợp lệ trước khi gia hạn**:
   - Đơn đăng ký phải đang ở trạng thái `PENDING`.
   - Nếu đơn đã `APPROVED`, `CANCELLED` hoặc `EXPIRED` $\rightarrow$ Từ chối với lỗi `ADM_INVALID_STATE_TRANSITION`.
   - Kiểm tra sĩ số lớp học: Nếu tổng số đơn đã duyệt `APPROVED` của lớp hiện tại đã bằng `max_students` $\rightarrow$ Từ chối gia hạn vì lớp đã kín học viên chính thức.
2. **Cập nhật Thời hạn Giữ chỗ Mới**:
   - Nhận số giờ muốn gia hạn thêm (`extended_hours`, ví dụ 24h hoặc 48h).
   - Thiết lập:
     $$\text{hold\_expires\_at} = \max(\text{hold\_expires\_at}, \text{NOW()}) + \text{extended\_hours}$$
3. **Lưu vết Lý do Gia hạn**:
   - Bắt buộc nhập lý do (`reason`), ghi nối tiếp vào trường `notes` của đơn đăng ký kèm tên nhân viên thực hiện và mốc thời gian để phục vụ kiểm toán học vụ.

---

## 2. Phạm vi File Tác động

### File tạo mới hoặc chỉnh sửa:
- `services/admission/backend/src/main/java/com/englishcenter/admission/controller/EnrollmentController.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/service/EnrollmentService.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/service/impl/EnrollmentServiceImpl.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/dto/enrollment/ExtendHoldRequest.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/dto/enrollment/EnrollmentResponse.java`

---

## 3. Đặc tả API Hợp đồng

### Request: `POST /api/admission/enrollments/{id}/extend-hold`
- **Header**: `Authorization: Bearer <Staff/Admin_Token>`
- **Request Body**:
  ```json
  {
    "extended_hours": 24,
    "reason": "Phụ huynh xin thêm 24h để chờ nhận lương đầu tháng chuyển khoản"
  }
  ```
- **Validation**:
  - `extended_hours`: Số nguyên dương, tối thiểu 1 giờ, tối đa 72 giờ (`@Min(1)`, `@Max(72)`).
  - `reason`: Bắt buộc nhập, tối thiểu 5 ký tự (`@NotBlank`).

### Response Thành công (HTTP 200 OK):
```json
{
  "success": true,
  "data": {
    "enrollment_id": "ENR-2026-0089",
    "status": "PENDING",
    "previous_hold_expires_at": "2026-11-03T21:30:00",
    "new_hold_expires_at": "2026-11-04T21:30:00",
    "notes": "Đăng ký ca tối 3-5-7 | [Gia hạn 24h bởi staff.hoa]: Phụ huynh xin thêm 24h để chờ nhận lương"
  },
  "message": "Gia hạn giữ chỗ thành công thêm 24 giờ"
}
```

---

## 4. Kế hoạch Triển khai (Step-by-step)
1. Tạo DTO `ExtendHoldRequest` có validation annotation.
2. Trong `EnrollmentServiceImpl.extendHold(Long enrollmentId, ExtendHoldRequest request)`:
   - `@Transactional`.
   - Tìm kiếm đơn đăng ký theo ID. Nếu không có $\rightarrow$ Ném `ADM_ENROLLMENT_NOT_FOUND`.
   - Kiểm tra `enrollment.getStatus() == EnrollmentStatus.PENDING`.
   - Lấy thông tin user nhân viên đang đăng nhập từ `SecurityUtils.getCurrentUserId()`.
   - Tính toán mốc thời gian mới và cập nhật `holdExpiresAt`.
   - Nối thêm vết ghi chú vào trường `notes`.
   - Lưu lại vào database.
3. Viết comment tiếng Việt chi tiết.

---

## 5. Tiêu chí Nghiệm thu (Acceptance Criteria)
- [ ] Học vụ gia hạn thành công $\rightarrow$ `hold_expires_at` tăng thêm số giờ chỉ định, trường `notes` ghi nhận rõ ai đã gia hạn và lý do.
- [ ] Gia hạn trên một đơn đã `CANCELLED` hoặc `EXPIRED` $\rightarrow$ Nhận mã lỗi HTTP 400 `ADM_INVALID_STATE_TRANSITION`.
- [ ] Cố tình truyền `extended_hours = 0` hoặc âm $\rightarrow$ Bị chặn ngay từ tầng validation.

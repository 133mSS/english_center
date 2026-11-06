# TASK-ADM-46: Quy trình Duyệt Đơn Nộp Tiền mặt Tại Quầy Dành cho Học vụ

- **Mã nhiệm vụ**: `TASK-ADM-46`
- **Phân kỳ**: `Phase 4: Tuyển sinh, Giữ chỗ 48h & Xét duyệt (ENR)`
- **Độ ưu tiên**: `P1`
- **Yêu cầu chức năng liên quan**: `FR-ENR-07`, `INV-ADM-01`, `INV-ADM-03`
- **Quy tắc bất biến bảo vệ**: `INV-ADM-01`, `INV-ADM-03`

---

## 1. Mục tiêu Nghiệp vụ & Kỹ thuật
Xây dựng tính năng cho phép Nhân viên học vụ (`STAFF`) hoặc Quản trị viên (`ADMIN`) duyệt đơn trực tiếp khi phụ huynh hoặc học viên đến văn phòng trung tâm nộp học phí bằng tiền mặt hoặc quẹt thẻ POS tại quầy:
1. **Xác thực quyền hạn**:
   - Chỉ người dùng có vai trò `ADMIN` hoặc `STAFF` mới có quyền gọi API này.
2. **Kiểm tra trạng thái hợp lệ (INV-ADM-03)**:
   - Chỉ cho phép duyệt các đơn đang ở trạng thái `PENDING`.
   - Nếu đơn đang ở trạng thái `CANCELLED` hoặc `EXPIRED` $\rightarrow$ Từ chối chuyển thẳng sang `APPROVED` để tuân thủ máy trạng thái (State Machine). Cần tạo đơn mới hoặc gia hạn trước.
3. **Bảo vệ sĩ số trần (INV-ADM-01)**:
   - Bắt buộc kiểm tra `currentApprovedCount < maxStudents`. Nếu lớp đã đầy $\rightarrow$ Báo lỗi `ADM_CLASS_FULL`.
4. **Ghi nhận thông tin thanh toán tại quầy**:
   - Ghi nhận thông tin hóa đơn tiền mặt, mã phiếu thu hoặc lý do vào trường `notes` của đơn.
   - Chuyển trạng thái đơn sang `APPROVED`.
   - Đồng bộ ngay hồ sơ sang Student Service.

---

## 2. Phạm vi File Tác động

### File tạo mới hoặc chỉnh sửa:
- `services/admission/backend/src/main/java/com/englishcenter/admission/controller/EnrollmentController.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/service/EnrollmentService.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/service/impl/EnrollmentServiceImpl.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/dto/enrollment/ManualApproveRequest.java`

---

## 3. Đặc tả API Hợp đồng

### Request: `POST /api/admission/enrollments/{id}/approve-manual`
- **Header**: `Authorization: Bearer <Staff/Admin_Token>`
- **Request Body**:
  ```json
  {
    "receipt_number": "PT-2026-0042",
    "payment_method": "CASH",
    "amount_received": 4500000.0,
    "notes": "Học viên nộp tiền mặt trực tiếp tại quầy tuyển sinh Cầu Giấy"
  }
  ```

### Response Thành công (HTTP 200 OK):
```json
{
  "success": true,
  "data": {
    "enrollment_id": "ENR-2026-0089",
    "status": "APPROVED",
    "approved_by": "staff.hoa",
    "approved_at": "2026-11-01T21:45:00",
    "receipt_number": "PT-2026-0042"
  },
  "message": "Duyệt đơn nhập học tiền mặt tại quầy thành công"
}
```

---

## 4. Kế hoạch Triển khai (Step-by-step)
1. Tạo DTO `ManualApproveRequest` có validation `@NotNull`, `@Positive`.
2. Trong `EnrollmentController`:
   - `@PreAuthorize("hasAnyRole('ADMIN', 'STAFF')")`.
3. Trong `EnrollmentServiceImpl.approveManual`:
   - Kiểm tra đơn tồn tại.
   - Kiểm tra `enrollment.getStatus() == EnrollmentStatus.PENDING`. Nếu đơn là `CANCELLED` $\rightarrow$ Ném `BusinessException(ErrorCode.ADM_INVALID_STATE_TRANSITION)` để thỏa mãn Invariant `INV-ADM-03`.
   - Gọi hàm duyệt có Invariant Guard `approveEnrollment(enrollmentId)` để khóa dòng và kiểm tra `max_students`.
   - Nối ghi chú phiếu thu tiền mặt vào `notes`.
4. Viết comment tiếng Việt chi tiết.

---

## 5. Tiêu chí Nghiệm thu (Acceptance Criteria)
- [ ] Nhân viên học vụ duyệt đơn `PENDING` thành công khi lớp còn chỗ.
- [ ] Học viên hoặc người ngoài gọi API này $\rightarrow$ Nhận mã HTTP 403 Forbidden.
- [ ] Cố tình duyệt một đơn đang ở trạng thái `CANCELLED` $\rightarrow$ Bị từ chối với mã lỗi HTTP 400 `ADM_INVALID_STATE_TRANSITION`, bài test `INV-ADM-03` đảm bảo xanh:
  ```bash
  python3 -m unittest discover -s tests/invariants -p "test_admission_invariants.py" -v
  ```

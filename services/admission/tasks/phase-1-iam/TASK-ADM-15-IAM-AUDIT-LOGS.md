# TASK-ADM-15: Hệ thống Truy vấn Nhật ký Kiểm toán & Cảnh báo An toàn Tài khoản

- **Mã nhiệm vụ**: `TASK-ADM-15`
- **Phân kỳ**: `Phase 1: Quản trị Định danh & Phiên (IAM)`
- **Độ ưu tiên**: `P1`
- **Yêu cầu chức năng liên quan**: `FR-IAM-07`, `BI-SEC-01`
- **Quy tắc bất biến bảo vệ**: `INV-SYS-01`, `INV-SEC-01`

---

## 1. Mục tiêu Nghiệp vụ & Kỹ thuật
Xây dựng cơ chế lưu vết bảo mật và cung cấp API truy vấn nhật ký kiểm toán cho Quản trị viên (`ADMIN`):
1. **Ghi nhật ký tập trung**: Cung cấp hàm tiện ích `AuditLogService.log(...)` để ghi nhận các sự kiện:
   - `LOGIN_SUCCESS`: Đăng nhập thành công.
   - `LOGIN_FAILED`: Đăng nhập thất bại (sai pass hoặc không tồn tại).
   - `REFRESH_TOKEN`: Làm mới phiên làm việc.
   - `LOGOUT`: Đăng xuất chủ động.
   - `PASSWORD_CHANGED`: Thay đổi mật khẩu thành công.
   - `ACCOUNT_LOCKED`: Tài khoản bị khóa bởi quản trị viên.
   - `ACCOUNT_UNLOCKED`: Mở khóa tài khoản.
2. **Cảnh báo Brute-force**:
   - Khi phát hiện một IP hoặc một `email` có quá 5 lần `LOGIN_FAILED` liên tiếp trong vòng 10 phút, hệ thống tự động gắn cờ cảnh báo và tạm khóa đăng nhập từ IP này trong 15 phút.
3. **API Truy vấn Nhật ký Kiểm toán**:
   - Cung cấp API phân trang (`page`, `size`), hỗ trợ lọc theo: `user_id`, `event_type`, `from_date`, `to_date`.

---

## 2. Phạm vi File Tác động

### File tạo mới hoặc chỉnh sửa:
- `services/admission/backend/src/main/java/com/englishcenter/admission/controller/AuditLogController.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/service/AuditLogService.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/service/impl/AuditLogServiceImpl.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/repository/AuthAuditLogRepository.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/dto/audit/AuditLogResponse.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/dto/audit/AuditLogFilterRequest.java`

---

## 3. Đặc tả API Hợp đồng

### API: `GET /api/admission/audit-logs`
- **Header**: `Authorization: Bearer <Admin_Token>`
- **Query Params**:
  - `user_id`: (Tùy chọn) Mã người dùng cần tra cứu
  - `event_type`: (Tùy chọn) Loại sự kiện (`LOGIN_FAILED`, `LOGIN_SUCCESS`, ...)
  - `from_date`: Ngày bắt đầu (ISO-8601: `2026-11-01T00:00:00`)
  - `to_date`: Ngày kết thúc
  - `page`: Trang hiện tại (mặc định 0)
  - `size`: Số bản ghi mỗi trang (mặc định 20)
- **Response Thành công (HTTP 200 OK)**:
  ```json
  {
    "success": true,
    "data": {
      "items": [
        {
          "log_id": 105,
          "user_id": "USR-2026-0001",
          "event_type": "LOGIN_SUCCESS",
          "ip_address": "192.168.1.50",
          "user_agent": "Mozilla/5.0 ... Chrome/120.0",
          "created_at": "2026-11-01T08:30:15"
        }
      ],
      "total_items": 1,
      "total_pages": 1,
      "current_page": 0
    },
    "message": "Truy vấn nhật ký kiểm toán thành công"
  }
  ```

---

## 4. Kế hoạch Triển khai (Step-by-step)
1. Trong `AuthAuditLogRepository`:
   - Viết query đếm số lần `LOGIN_FAILED` trong 10 phút gần nhất của IP:
     `countRecentFailedLogins(String ipAddress, LocalDateTime since)`.
   - Viết truy vấn phân trang với JPA `Pageable` và Dynamic Specification để lọc theo điều kiện linh hoạt.
2. Trong `AuditLogServiceImpl`:
   - Xây dựng phương thức `recordEvent(String userId, String eventType, String ip, String userAgent, String details)`.
   - Bổ sung `@Async` để việc ghi log không làm chậm thời gian phản hồi của API chính.
3. Trong `AuditLogController`: Khai báo endpoint có bảo vệ quyền Admin.
4. Viết comment tiếng Việt chi tiết cho từng lớp.

---

## 5. Tiêu chí Nghiệm thu (Acceptance Criteria)
- [ ] Mọi hành động đăng nhập, đổi pass đều tự động sinh ra bản ghi trong `admission.auth_audit_logs`.
- [ ] Gọi API tra cứu với tài khoản non-admin $\rightarrow$ Trả về 403 Forbidden.
- [ ] Admin tra cứu nhật ký có phân trang và lọc dữ liệu chính xác theo `event_type`.

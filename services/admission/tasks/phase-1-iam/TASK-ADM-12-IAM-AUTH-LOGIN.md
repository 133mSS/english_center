# TASK-ADM-12: API Đăng nhập, Cấp JWT Kép & Ghi Nhận Nhật ký Kiểm toán Bảo mật

- **Mã nhiệm vụ**: `TASK-ADM-12`
- **Phân kỳ**: `Phase 1: Quản trị Định danh & Phiên (IAM)`
- **Độ ưu tiên**: `P0 (Bắt buộc)`
- **Yêu cầu chức năng liên quan**: `FR-IAM-03`, `FR-IAM-07`
- **Quy tắc bất biến bảo vệ**: `INV-SYS-01`, `INV-SEC-03`

---

## 1. Mục tiêu Nghiệp vụ & Kỹ thuật
Xây dựng API đăng nhập chuẩn mực cho tất cả các nhóm người dùng (Admin, Staff, Teacher, Student):
1. Nhận thông tin đăng nhập (`email`, `password`) từ Client.
2. Kiểm tra thông tin người dùng:
   - Nếu tài khoản không tồn tại hoặc mật khẩu sai: Ghi nhật ký sự kiện `LOGIN_FAILED` vào `auth_audit_logs` kèm địa chỉ IP và User-Agent, sau đó ném lỗi `ADM_INVALID_CREDENTIALS` (HTTP 401).
   - Nếu tài khoản bị khóa (`is_active = false`): Ném lỗi `ADM_ACCOUNT_LOCKED` (HTTP 403).
3. Nếu đăng nhập thành công:
   - Sinh Access Token (15 phút, stateless).
   - Sinh Refresh Token ngẫu nhiên (hoặc JWT 7 ngày), lưu bản ghi vào `admission.refresh_tokens` kèm thời hạn `expires_at = NOW() + 7 DAYS`.
   - Ghi nhật ký sự kiện `LOGIN_SUCCESS` vào `auth_audit_logs`.
   - Trả về cặp token và thông tin người dùng.

---

## 2. Phạm vi File Tác động

### File tạo mới hoặc chỉnh sửa:
- `services/admission/backend/src/main/java/com/englishcenter/admission/controller/AuthController.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/service/AuthService.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/service/impl/AuthServiceImpl.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/repository/RefreshTokenRepository.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/repository/AuthAuditLogRepository.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/dto/auth/LoginRequest.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/dto/auth/LoginResponse.java`

---

## 3. Đặc tả API Hợp đồng

### Request: `POST /api/admission/auth/login`
```json
{
  "email": "admin@englishcenter.edu.vn",
  "password": "Password@123"
}
```

### Response Thành công (HTTP 200 OK):
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "d7a8f9e2b1c34a56...",
    "token_type": "Bearer",
    "expires_in": 900,
    "user": {
      "user_id": "USR-2026-0001",
      "email": "admin@englishcenter.edu.vn",
      "full_name": "Nguyen Van Admin",
      "role": "ADMIN"
    }
  },
  "message": "Đăng nhập thành công"
}
```

### Response Thất bại (HTTP 401 Unauthorized):
```json
{
  "success": false,
  "error": {
    "code": "ADM_INVALID_CREDENTIALS",
    "message": "Email hoặc mật khẩu không chính xác"
  }
}
```

---

## 4. Kế hoạch Triển khai (Step-by-step)
1. Tạo DTO `LoginRequest` có `@NotBlank` và `@Email`.
2. Tạo DTO `LoginResponse` theo định dạng `snake_case`.
3. Trong `AuthServiceImpl`:
   - Lấy client IP từ header `X-Forwarded-For` hoặc `request.getRemoteAddr()`.
   - Tìm user theo email. Nếu không có hoặc `!passwordEncoder.matches(password, user.getPasswordHash())`:
     - Ghi log `LOGIN_FAILED` với `user_id = null`, email nhập vào, và ip address.
     - Ném `BusinessException(ErrorCode.ADM_INVALID_CREDENTIALS)`.
   - Kiểm tra `!user.getIsActive()`: Ném lỗi `ADM_ACCOUNT_LOCKED`.
   - Sinh Access Token và Refresh Token.
   - Lưu Refresh Token vào `admission.refresh_tokens`.
   - Ghi log `LOGIN_SUCCESS`.
4. Trả về `ResponseEntity.ok(ApiResponse.success(data, "Đăng nhập thành công"))`.
5. Viết comment tiếng Việt đầy đủ.

---

## 5. Tiêu chí Nghiệm thu (Acceptance Criteria)
- [ ] Gửi đúng tài khoản mật khẩu $\rightarrow$ Nhận được cặp `access_token` và `refresh_token`, trong database có thêm 1 bản ghi `refresh_tokens` và 1 bản ghi `auth_audit_logs` sự kiện `LOGIN_SUCCESS`.
- [ ] Gửi sai mật khẩu $\rightarrow$ Nhận HTTP 401, trong database ghi sự kiện `LOGIN_FAILED`.
- [ ] Mọi trường trong response JSON đều dùng chuẩn `snake_case`.

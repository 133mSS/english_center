# TASK-ADM-14: Quy trình Quên mật khẩu & Đặt lại Mật khẩu qua Token Email 15 phút

- **Mã nhiệm vụ**: `TASK-ADM-14`
- **Phân kỳ**: `Phase 1: Quản trị Định danh & Phiên (IAM)`
- **Độ ưu tiên**: `P1`
- **Yêu cầu chức năng liên quan**: `FR-IAM-06`
- **Quy tắc bất biến bảo vệ**: `INV-SYS-01`, `INV-SEC-03`

---

## 1. Mục tiêu Nghiệp vụ & Kỹ thuật
Xây dựng luồng khôi phục tài khoản tự phục vụ (Self-service Password Reset):
1. **Yêu cầu khôi phục (`forgot-password`)**:
   - Nhận `email` từ người dùng.
   - Nếu email tồn tại trong hệ thống: Sinh chuỗi mã ngẫu nhiên bảo mật (Secure Random UUID/Token), lưu vào bảng `admission.password_reset_tokens` kèm thời hạn `expires_at = NOW() + 15 MINUTES`.
   - Giả lập gửi email (hoặc gọi dịch vụ gửi mail) chứa đường dẫn kèm token đặt lại mật khẩu: `https://center.edu.vn/reset-password?token=XYZ`.
   - *Ngăn chặn dò quét email (Email Enumeration)*: Luôn trả về phản hồi thành công chung chung: *"Nếu email tồn tại trong hệ thống, hướng dẫn đặt lại mật khẩu đã được gửi đến hòm thư của bạn"*.
2. **Đặt lại mật khẩu mới (`reset-password`)**:
   - Nhận `token` và `new_password`.
   - Kiểm tra tính hợp lệ của token trong `password_reset_tokens`: chưa sử dụng (`is_used = false`) và chưa hết hạn (`expires_at > NOW()`).
   - Cập nhật mật khẩu mới đã băm (BCrypt) vào bảng `admission.users`.
   - Đánh dấu token đã sử dụng `is_used = true`.
   - Thu hồi toàn bộ `refresh_tokens` cũ của người dùng này để buộc đăng nhập lại từ đầu trên tất cả các thiết bị.
   - Ghi nhận sự kiện `PASSWORD_CHANGED` vào `admission.auth_audit_logs`.

---

## 2. Phạm vi File Tác động

### File tạo mới hoặc chỉnh sửa:
- `services/admission/backend/src/main/java/com/englishcenter/admission/controller/AuthController.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/service/AuthService.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/service/impl/AuthServiceImpl.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/repository/PasswordResetTokenRepository.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/dto/auth/ForgotPasswordRequest.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/dto/auth/ResetPasswordRequest.java`

---

## 3. Đặc tả API Hợp đồng

### 3.1. API Yêu cầu Đặt lại Mật khẩu
- **URL**: `POST /api/admission/auth/forgot-password`
- **Request Body**:
  ```json
  {
    "email": "student@englishcenter.edu.vn"
  }
  ```
- **Response**: Trả về HTTP 200 kèm thông báo thành công chung.

### 3.2. API Thiết lập Mật khẩu Mới
- **URL**: `POST /api/admission/auth/reset-password`
- **Request Body**:
  ```json
  {
    "token": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "new_password": "NewSecretPassword@2026"
  }
  ```
- **Response**: Trả về HTTP 200 kèm thông báo mật khẩu đã được cập nhật thành công.

---

## 4. Kế hoạch Triển khai (Step-by-step)
1. Tạo JPA Entity `PasswordResetToken` tương ứng với bảng `admission.password_reset_tokens`.
2. Tạo `PasswordResetTokenRepository` hỗ trợ tìm kiếm theo token.
3. Trong `AuthServiceImpl`:
   - `forgotPassword(String email)`: Sinh token ngẫu nhiên, lưu DB, ghi log console thông tin link khôi phục mật khẩu.
   - `resetPassword(String token, String newPassword)`: Validate token, cập nhật `password_hash`, đánh dấu `is_used = true`, thu hồi refresh tokens, ghi log audit.
4. Viết comment tiếng Việt đầy đủ.

---

## 5. Tiêu chí Nghiệm thu (Acceptance Criteria)
- [ ] Gửi yêu cầu với email bất kỳ $\rightarrow$ Luôn nhận HTTP 200 với thông điệp bảo mật.
- [ ] Sử dụng token đã hết hạn 15 phút $\rightarrow$ Nhận lỗi HTTP 400 `ADM_TOKEN_EXPIRED`.
- [ ] Đặt lại mật khẩu thành công $\rightarrow$ Đăng nhập bằng mật khẩu mới thành công, mật khẩu cũ không còn tác dụng.

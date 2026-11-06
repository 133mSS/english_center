# TASK-ADM-11: Quản lý Tài khoản Nhân sự (Staff/Teacher) & Khóa/Mở khóa Tài khoản

- **Mã nhiệm vụ**: `TASK-ADM-11`
- **Phân kỳ**: `Phase 1: Quản trị Định danh & Phiên (IAM)`
- **Độ ưu tiên**: `P1`
- **Yêu cầu chức năng liên quan**: `FR-IAM-02`, `FR-IAM-05`
- **Quy tắc bất biến bảo vệ**: `INV-SEC-01`, `INV-SYS-01`

---

## 1. Mục tiêu Nghiệp vụ & Kỹ thuật
Cho phép Quản trị viên (`ADMIN`) quản lý danh sách nhân sự của trung tâm:
1. Tạo mới tài khoản cho Học vụ (`STAFF`) hoặc Giáo viên (`TEACHER`) với đầy đủ thông tin: Email, Họ tên, Số điện thoại, Giới tính, Ngày sinh.
2. Cập nhật thông tin hồ sơ nhân viên.
3. Kích hoạt hoặc Khóa tài khoản (`is_active = false/true`). Khi tài khoản bị khóa (`is_active = false`), hệ thống lập tức vô hiệu hóa mọi phiên làm việc hiện hành của người dùng này và chặn toàn bộ các cuộc gọi API tiếp theo.
4. Ghi nhận sự kiện `ACCOUNT_LOCKED` hoặc `ACCOUNT_UNLOCKED` vào bảng `admission.auth_audit_logs`.

---

## 2. Phạm vi File Tác động

### File tạo mới hoặc chỉnh sửa:
- `services/admission/backend/src/main/java/com/englishcenter/admission/controller/UserController.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/service/UserService.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/service/impl/UserServiceImpl.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/dto/user/CreateUserRequest.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/dto/user/UpdateUserRequest.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/dto/user/UserResponse.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/dto/user/ToggleActiveRequest.java`

---

## 3. Đặc tả API Hợp đồng

### 3.1. Tạo Tài khoản Nhân sự
- **URL**: `POST /api/admission/users`
- **Header**: `Authorization: Bearer <Admin_Token>`
- **Request Body**:
  ```json
  {
    "email": "teacher.lan@englishcenter.edu.vn",
    "password": "Password@123",
    "role": "TEACHER",
    "full_name": "Nguyen Thi Lan",
    "phone": "0987654321",
    "gender": "FEMALE",
    "date_of_birth": "1992-05-15"
  }
  ```
- **Validation**:
  - `email`: Phải đúng định dạng email, không được trùng lặp (nếu trùng trả về 409 `ADM_USER_EMAIL_EXISTS`).
  - `role`: Chỉ cho phép `STAFF` hoặc `TEACHER` (không cho phép tạo thêm `ADMIN` qua API này nếu không có super-admin).
  - `password`: Tối thiểu 8 ký tự.

### 3.2. Khóa / Mở khóa Tài khoản
- **URL**: `PATCH /api/admission/users/{id}/status`
- **Header**: `Authorization: Bearer <Admin_Token>`
- **Request Body**:
  ```json
  {
    "is_active": false,
    "reason": "Nhân viên nghỉ việc"
  }
  ```
- **Hành động nghiệp vụ đi kèm**:
  - Cập nhật `users.is_active = false`.
  - Cập nhật toàn bộ `refresh_tokens` của user thành `is_revoked = true`.
  - Ghi bản ghi vào `auth_audit_logs` với sự kiện `ACCOUNT_LOCKED`.

---

## 4. Kế hoạch Triển khai (Step-by-step)
1. Tạo DTOs với đầy đủ annotation validation `@NotBlank`, `@Email`, `@Pattern`.
2. Trong `UserServiceImpl`:
   - Viết phương thức `createUser(CreateUserRequest request)`: Kiểm tra email trùng, mã hóa mật khẩu bằng BCrypt, lưu DB, ghi log.
   - Viết phương thức `toggleUserStatus(String userId, boolean isActive, String reason)`: Cập nhật trạng thái, thu hồi toàn bộ refresh token nếu bị khóa.
3. Trong `UserController`: Khai báo endpoints với `@PreAuthorize("hasRole('ADMIN')")`.
4. Viết comment tiếng Việt chi tiết cho từng phương thức.

---

## 5. Tiêu chí Nghiệm thu (Acceptance Criteria)
- [ ] Tài khoản có `role = STAFF` cố tình gọi API tạo user bị chặn với mã HTTP 403 Forbidden.
- [ ] Admin tạo tài khoản nhân viên thành công, mật khẩu trong database được mã hóa an toàn.
- [ ] Khóa tài khoản thành công $\rightarrow$ Toàn bộ token đang dùng của user đó bị thu hồi, gửi request mới bằng token cũ nhận mã HTTP 401 Unauthorized (`ADM_TOKEN_INVALID`).

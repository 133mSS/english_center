# TASK-ADM-02: Thiết lập Spring Security 6 & Bộ Cấp phát Token Kép (Access/Refresh)

- **Mã nhiệm vụ**: `TASK-ADM-02`
- **Phân kỳ**: `Phase 0: Nền móng & Hạ tầng (INF)`
- **Độ ưu tiên**: `P0 (Bắt buộc)`
- **Yêu cầu chức năng liên quan**: FR-IAM-03, FR-IAM-04, FR-IAM-05
- **Quy tắc bất biến bảo vệ**: `INV-SEC-01`, `INV-SEC-03` (Bảo mật tài khoản & Không hardcode secret)

---

## 1. Mục tiêu Nghiệp vụ & Kỹ thuật
Xây dựng lớp bảo mật xác thực và phân quyền tập trung cho toàn bộ ứng dụng sử dụng Spring Security 6 và JWT:
1. Cấu hình Filter Chain không duy trì trạng thái phía server (`SessionCreationPolicy.STATELESS`).
2. Cấp phát cơ chế Token Kép (Dual JWT):
   - **Access Token**: Thời hạn ngắn (15 phút), chứa claims `sub` (user_id), `email`, `role`, `full_name`. Dùng để xác thực trên từng request qua header `Authorization: Bearer <token>`.
   - **Refresh Token**: Thời hạn dài (7 ngày), lưu trạng thái trong bảng `admission.refresh_tokens` để quản lý phiên và hỗ trợ thu hồi lập tức khi cần thiết.
3. Mã hóa mật khẩu bằng thuật toán chuẩn công nghiệp `BCryptPasswordEncoder`.
4. Đọc JWT Secret Key từ biến môi trường `JWT_SECRET` (tối thiểu 256 bits), tuyệt đối không hardcode trong mã nguồn.

---

## 2. Phạm vi File Tác động

### File tạo mới hoặc chỉnh sửa:
- `services/admission/backend/src/main/java/com/englishcenter/admission/config/SecurityConfig.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/security/JwtAuthenticationFilter.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/security/JwtTokenProvider.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/security/CustomUserDetailsService.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/security/SecurityUtils.java`

### File cấm sửa đổi:
- `tests/invariants/*`

---

## 3. Đặc tả Kỹ thuật Chi tiết

### 3.1. Phân quyền Endpoint trong SecurityFilterChain
```java
http
    .csrf(csrf -> csrf.disable())
    .cors(cors -> cors.configure(http))
    .sessionManagement(sess -> sess.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
    .authorizeHttpRequests(auth -> auth
        // Public endpoints
        .requestMatchers("/api/admission/auth/login").permitAll()
        .requestMatchers("/api/admission/auth/refresh").permitAll()
        .requestMatchers("/api/admission/auth/forgot-password").permitAll()
        .requestMatchers("/api/admission/auth/reset-password").permitAll()
        .requestMatchers(HttpMethod.GET, "/api/admission/courses/**").permitAll()
        .requestMatchers(HttpMethod.GET, "/api/admission/classes/**").permitAll()
        .requestMatchers(HttpMethod.POST, "/api/admission/enrollments").permitAll()
        .requestMatchers("/api/admission/tests/public/**").permitAll()
        .requestMatchers("/api/admission/webhooks/**").permitAll()
        // Admin only
        .requestMatchers("/api/admission/users/**").hasRole("ADMIN")
        // Staff & Admin
        .requestMatchers("/api/admission/rooms/**").hasAnyRole("ADMIN", "STAFF")
        .requestMatchers("/api/admission/enrollments/*/approve-manual").hasAnyRole("ADMIN", "STAFF")
        .requestMatchers("/api/admission/bi/**").hasAnyRole("ADMIN", "STAFF")
        // Authenticated
        .anyRequest().authenticated()
    )
    .addFilterBefore(jwtAuthenticationFilter, UsernamePasswordAuthenticationFilter.class);
```

### 3.2. Cấu trúc Claims trong Access Token
```json
{
  "sub": "USR-2026-0001",
  "email": "student@englishcenter.edu.vn",
  "role": "STUDENT",
  "full_name": "Nguyen Van A",
  "iat": 1772540000,
  "exp": 1772540900
}
```

---

## 4. Kế hoạch Triển khai (Step-by-step)
1. Cấu hình Bean `PasswordEncoder` trả về `new BCryptPasswordEncoder()`.
2. Tạo `JwtTokenProvider.java`:
   - Hàm `generateAccessToken(User user)` với hạn 15 phút (900,000 ms).
   - Hàm `generateRefreshToken(User user)` với hạn 7 ngày.
   - Hàm `validateToken(String token)` kiểm tra chữ ký và hạn sử dụng.
   - Hàm `getUserIdFromToken(String token)` và `getUserRoleFromToken(String token)`.
3. Xây dựng `JwtAuthenticationFilter.java`:
   - Trích xuất token từ header `Authorization: Bearer <token>`.
   - Kiểm tra tính hợp lệ và nạp đối tượng `UsernamePasswordAuthenticationToken` vào `SecurityContextHolder`.
4. Tạo `SecurityUtils.java` hỗ trợ lấy `user_id` và `role` của người dùng đang đăng nhập trong Service layer.
5. Viết comment tiếng Việt chi tiết cho từng phương thức.

---

## 5. Tiêu chí Nghiệm thu (Acceptance Criteria)
- [ ] Khi gọi API công khai (như `GET /api/admission/courses`), không cần gửi Bearer Token vẫn trả về 200 OK.
- [ ] Khi gọi API yêu cầu quyền (như `POST /api/admission/users`), nếu không có token hoặc token sai $\rightarrow$ Trả về 401 Unauthorized.
- [ ] Nếu người dùng có `role = STUDENT` cố tình gọi API của Admin $\rightarrow$ Trả về 403 Forbidden.
- [ ] Chạy bộ kiểm thử Invariant `INV-SEC-03` đạt `OK` (không lộ mật khẩu plaintext vào git).

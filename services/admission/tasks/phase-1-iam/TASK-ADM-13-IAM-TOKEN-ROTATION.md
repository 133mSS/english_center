# TASK-ADM-13: Cơ chế Refresh Token Rotation & Thu hồi Token Đang hoạt động

- **Mã nhiệm vụ**: `TASK-ADM-13`
- **Phân kỳ**: `Phase 1: Quản trị Định danh & Phiên (IAM)`
- **Độ ưu tiên**: `P0 (Bắt buộc)`
- **Yêu cầu chức năng liên quan**: `FR-IAM-04`
- **Quy tắc bất biến bảo vệ**: `INV-SYS-01`, `INV-SEC-01`

---

## 1. Mục tiêu Nghiệp vụ & Kỹ thuật
Xây dựng cơ chế làm mới phiên an toàn tuyệt đối chống tấn công lặp lại (Replay Attack) với kỹ thuật **Refresh Token Rotation**:
1. Nhận `refresh_token` từ Client.
2. Tra cứu trong cơ sở dữ liệu `admission.refresh_tokens`:
   - Nếu token không tồn tại, đã hết hạn (`expires_at < NOW()`), hoặc đã bị thu hồi (`is_revoked = true`):
     - Lập tức chặn yêu cầu, trả về lỗi HTTP 401 `ADM_TOKEN_INVALID`.
     - *Phát hiện gian lận*: Nếu token đã bị thu hồi trước đó mà lại được mang ra gọi làm mới $\rightarrow$ Nghi ngờ rò rỉ token! Lập tức thu hồi **toàn bộ** refresh token thuộc về `user_id` đó và ghi nhật ký cảnh báo bảo mật.
3. Nếu token hợp lệ:
   - Đánh dấu token hiện tại thành `is_revoked = true` (Revoke token cũ).
   - Tạo một cặp `access_token` và `refresh_token` hoàn toàn mới.
   - Lưu refresh token mới vào database.
   - Ghi nhận sự kiện `REFRESH_TOKEN` vào `admission.auth_audit_logs`.
   - Trả về cặp token mới cho Client.

---

## 2. Phạm vi File Tác động

### File tạo mới hoặc chỉnh sửa:
- `services/admission/backend/src/main/java/com/englishcenter/admission/controller/AuthController.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/service/AuthService.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/service/impl/AuthServiceImpl.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/repository/RefreshTokenRepository.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/dto/auth/RefreshTokenRequest.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/dto/auth/RefreshTokenResponse.java`

---

## 3. Đặc tả API Hợp đồng

### Request: `POST /api/admission/auth/refresh`
```json
{
  "refresh_token": "d7a8f9e2b1c34a56..."
}
```

### Response Thành công (HTTP 200 OK):
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.new...",
    "refresh_token": "9b3c4d5e6f7a8123.new...",
    "token_type": "Bearer",
    "expires_in": 900
  },
  "message": "Làm mới phiên làm việc thành công"
}
```

### Response Lỗi (HTTP 401 Unauthorized):
```json
{
  "success": false,
  "error": {
    "code": "ADM_TOKEN_INVALID",
    "message": "Phiên làm việc không hợp lệ hoặc đã hết hạn"
  }
}
```

---

## 4. Kế hoạch Triển khai (Step-by-step)
1. Trong `RefreshTokenRepository`:
   - Viết query `Optional<RefreshToken> findByTokenHash(String tokenHash);` (hoặc `findByToken`).
   - Viết query update thu hồi toàn bộ token của user: `revokeAllUserTokens(String userId)`.
2. Trong `AuthServiceImpl`:
   - Viết phương thức `refreshToken(RefreshTokenRequest request)`:
   - Bọc trong `@Transactional`.
   - Kiểm tra `token.getIsRevoked()`: Nếu true, gọi `revokeAllUserTokens(token.getUserId())`, ghi audit log sự kiện nghi ngờ giả mạo, ném `BusinessException(ErrorCode.ADM_TOKEN_INVALID)`.
   - Kiểm tra `token.getExpiresAt().isBefore(LocalDateTime.now())`: Ném `BusinessException(ErrorCode.ADM_TOKEN_EXPIRED)`.
   - Cập nhật `token.setIsRevoked(true)`.
   - Cấp phát refresh token mới, lưu vào DB và trả về response.
3. Viết comment tiếng Việt giải thích cơ chế Rotation.

---

## 5. Tiêu chí Nghiệm thu (Acceptance Criteria)
- [ ] Dùng `refresh_token` hợp lệ gọi API $\rightarrow$ Nhận được cặp token mới.
- [ ] Dùng lại ngay chính `refresh_token` vừa dùng để gọi lần 2 $\rightarrow$ Bị từ chối HTTP 401, token cũ đã bị thu hồi.
- [ ] Dùng token đã thu hồi để cố tình gọi refresh $\rightarrow$ Toàn bộ các phiên đang mở của user đó bị hủy hết để phòng vệ.

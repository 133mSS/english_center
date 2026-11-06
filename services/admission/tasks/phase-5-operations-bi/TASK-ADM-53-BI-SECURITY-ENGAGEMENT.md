# TASK-ADM-53: API Giám sát DAU/MAU & Phát hiện Bất thường Tấn công Đăng nhập (BI-03)

- **Mã nhiệm vụ**: `TASK-ADM-53`
- **Phân kỳ**: `Phase 5: Xuất Dữ liệu & Phân tích BI (OPS/BI)`
- **Độ ưu tiên**: `P1`
- **Yêu cầu chức năng liên quan**: `BI-03`, `BI-USR-01`, `BI-SEC-01`
- **Quy tắc bất biến bảo vệ**: `INV-SYS-01`, `INV-SEC-01`

---

## 1. Mục tiêu Nghiệp vụ & Kỹ thuật
Xây dựng API Giám sát Sức khỏe Vận hành & An toàn Hệ thống dành riêng cho Ban Quản trị (`ADMIN`):
1. **Mức độ Gắn kết Người dùng (BI-USR-01 - DAU / MAU)**:
   - Đo lường số lượng người dùng tích cực hàng ngày (Daily Active Users - DAU) và hàng tháng (Monthly Active Users - MAU).
   - Phân rã số lượng theo từng vai trò: `STUDENT`, `TEACHER`, `STAFF`.
   - Căn cứ vào số lượng `user_id` duy nhất có sự kiện `LOGIN_SUCCESS` trong ngày/tháng từ bảng `admission.auth_audit_logs`.
2. **Cảnh báo Tấn công & Tỷ lệ Đăng nhập Thất bại (BI-SEC-01 - Failed Login Rate)**:
   - Tính toán tỷ lệ thất bại:
     $$\text{Failed Login Rate} = \frac{\text{Số lượt LOGIN\_FAILED trong 24h}}{\text{Tổng lượt thử đăng nhập trong 24h}} \times 100\% \quad (\text{Ngưỡng an toàn } \le 5\%)$$
   - Phát hiện các IP hoặc tài khoản có hành vi bất thường (Top 5 IP có nhiều lần đăng nhập thất bại nhất trong ngày).

---

## 2. Phạm vi File Tác động

### File tạo mới hoặc chỉnh sửa:
- `services/admission/backend/src/main/java/com/englishcenter/admission/controller/BiAnalyticsController.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/service/BiAnalyticsService.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/service/impl/BiAnalyticsServiceImpl.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/repository/AuthAuditLogRepository.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/dto/bi/SecurityEngagementReportResponse.java`

---

## 3. Đặc tả API Hợp đồng

### API: `GET /api/admission/bi/security-engagement`
- **Header**: `Authorization: Bearer <Admin_Token>`
- **Response Thành công (HTTP 200 OK)**:
  ```json
  {
    "success": true,
    "data": {
      "engagement": {
        "dau": 145,
        "mau": 1280,
        "active_by_role": {
          "student": 110,
          "teacher": 25,
          "staff": 10
        }
      },
      "security": {
        "failed_login_rate": 2.4,
        "total_attempts_24h": 320,
        "failed_attempts_24h": 8,
        "status": "NORMAL",
        "suspicious_ips": [
          { "ip_address": "14.161.22.8", "failed_count": 5, "last_attempt": "2026-11-01T20:15:00" }
        ]
      }
    },
    "message": "Truy vấn báo cáo an toàn và gắn kết thành công"
  }
  ```

---

## 4. Kế hoạch Triển khai (Step-by-step)
1. Thêm các hàm truy vấn thống kê vào `AuthAuditLogRepository`:
   - `countDistinctActiveUsers(LocalDateTime since)`
   - `countDistinctActiveUsersByRole(Role role, LocalDateTime since)`
   - `countEventsSince(String eventType, LocalDateTime since)`
   - `findTopSuspiciousIps(LocalDateTime since, Pageable pageable)`
2. Trong `BiAnalyticsServiceImpl.getSecurityEngagementReport`:
   - Tính toán tỷ lệ failed login rate, nếu $> 5\%$ gắn cờ `status = "WARNING"`.
3. Trong `BiAnalyticsController`: Khóa quyền `@PreAuthorize("hasRole('ADMIN')")`.
4. Viết comment tiếng Việt đầy đủ.

---

## 5. Tiêu chí Nghiệm thu (Acceptance Criteria)
- [ ] Chỉ Admin mới được quyền gọi API này (Staff hoặc Student gọi bị 403 Forbidden).
- [ ] Thống kê DAU/MAU và tỷ lệ đăng nhập thất bại chính xác dựa trên dữ liệu nhật ký kiểm toán.
- [ ] Danh sách suspicious IPs trả về danh sách các địa chỉ IP có lượt thử sai nhiều nhất.

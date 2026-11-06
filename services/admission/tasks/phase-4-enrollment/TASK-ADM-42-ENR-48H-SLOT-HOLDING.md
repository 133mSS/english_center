# TASK-ADM-42: Cơ chế Cấp Slot Giữ chỗ 48h Cho Đơn Đăng ký PENDING

- **Mã nhiệm vụ**: `TASK-ADM-42`
- **Phân kỳ**: `Phase 4: Tuyển sinh, Giữ chỗ 48h & Xét duyệt (ENR)`
- **Độ ưu tiên**: `P0 (Bắt buộc)`
- **Yêu cầu chức năng liên quan**: `FR-ENR-03`, `FR-ACA-05`
- **Quy tắc bất biến bảo vệ**: `INV-ADM-01`, `INV-SYS-01`

---

## 1. Mục tiêu Nghiệp vụ & Kỹ thuật
Xây dựng cơ chế giữ chỗ có thời hạn (48h Slot Holding) tạo điều kiện cho học viên hoàn tất thủ tục thanh toán học phí:
1. **Khởi tạo Thời hạn Giữ chỗ**:
   - Khi bất kỳ đơn đăng ký mới nào được tạo ở trạng thái `PENDING`, hệ thống tự động thiết lập:
     $$\text{hold\_expires\_at} = \text{created\_at} + 48\text{ giờ}$$
2. **Chiếm giữ Slot Khả dụng**:
   - Trong thời gian 48 giờ này (khi `hold_expires_at > NOW()`), slot giữ chỗ của học viên được bảo vệ tuyệt đối: không ai khác có thể đăng ký đè vào slot này.
   - Slot này được tính vào `Active Held Count` của lớp học (xem TASK-ADM-24).
3. **Phản ánh Trạng thái trên Giao diện**:
   - Trả về thời gian đếm ngược còn lại (`remaining_seconds`) để giao diện hiển thị đồng hồ đếm ngược cảnh báo thời gian thanh toán cho học viên.

---

## 2. Phạm vi File Tác động

### File tạo mới hoặc chỉnh sửa:
- `services/admission/backend/src/main/java/com/englishcenter/admission/entity/Enrollment.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/service/impl/EnrollmentServiceImpl.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/dto/enrollment/EnrollmentDetailResponse.java`

---

## 3. Đặc tả Kỹ thuật Chi tiết

### 3.1. Entity Mapping trong `Enrollment.java`
```java
@Column(name = "hold_expires_at")
private LocalDateTime holdExpiresAt;

@Column(name = "status", nullable = false)
@Enumerated(EnumType.STRING)
private EnrollmentStatus status; // PENDING, APPROVED, CANCELLED, EXPIRED
```

### 3.2. Tính toán Thời gian Còn lại
```java
public Long getRemainingHoldingSeconds() {
    if (this.status != EnrollmentStatus.PENDING || this.holdExpiresAt == null) {
        return 0L;
    }
    long seconds = Duration.between(LocalDateTime.now(), this.holdExpiresAt).getSeconds();
    return Math.max(0L, seconds);
}
```

---

## 4. Kế hoạch Triển khai (Step-by-step)
1. Đảm bảo cột `hold_expires_at` có kiểu `TIMESTAMP WITH TIME ZONE` trong DDL và `LocalDateTime` trong Java Entity.
2. Tại phương thức tạo đơn trong `EnrollmentServiceImpl`, gán `enrollment.setHoldExpiresAt(LocalDateTime.now().plusHours(48))`.
3. Bổ sung trường `remaining_seconds` trong DTO trả về cho Client.
4. Đảm bảo chỉ mục Partial Index `idx_enrollments_pending_hold` trên PostgreSQL được kích hoạt để tăng tốc truy vấn.
5. Viết comment tiếng Việt đầy đủ.

---

## 5. Tiêu chí Nghiệm thu (Acceptance Criteria)
- [ ] Đơn vừa tạo có `status = PENDING` và `hold_expires_at` chính xác sau 48 tiếng.
- [ ] Sau khi tạo đơn, gọi API capacity của lớp thấy `active_held_count` tăng thêm 1 và `available_slots` giảm đi 1.
- [ ] Trả về trường `remaining_seconds` đầy đủ định dạng `snake_case`.

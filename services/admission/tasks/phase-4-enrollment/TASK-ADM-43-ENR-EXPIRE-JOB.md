# TASK-ADM-43: Scheduled Background Job Tự động Thu hồi Slot Quá hạn (EXPIRED)

- **Mã nhiệm vụ**: `TASK-ADM-43`
- **Phân kỳ**: `Phase 4: Tuyển sinh, Giữ chỗ 48h & Xét duyệt (ENR)`
- **Độ ưu tiên**: `P0 (Bắt buộc)`
- **Yêu cầu chức năng liên quan**: `FR-ENR-04`, `BI-FUN-04`
- **Quy tắc bất biến bảo vệ**: `INV-SYS-01`

---

## 1. Mục tiêu Nghiệp vụ & Kỹ thuật
Xây dựng tiến trình nền tự động (Scheduled Background Job) chạy định kỳ để giải phóng tài nguyên lớp học khi học viên không thanh toán học phí đúng hạn:
1. **Quét định kỳ các đơn quá hạn**:
   - Sử dụng Spring `@Scheduled(cron = "0 */5 * * * *")` (chạy mỗi 5 phút một lần hoặc mỗi phút một lần).
   - Tìm kiếm tất cả các đơn đăng ký thỏa mãn điều kiện:
     $$\text{status} = \text{'PENDING'} \quad \text{VÀ} \quad \text{hold\_expires\_at} < \text{NOW()}$$
2. **Chuyển đổi trạng thái**:
   - Cập nhật trạng thái các đơn này sang `EXPIRED`.
   - Ghi nhận `updated_at = NOW()`.
   - Tự động giải phóng slot giữ chỗ, giúp `Available Slots` của lớp học tăng lên ngay lập tức cho các học viên khác đăng ký.
3. **Ghi log vận hành**:
   - Ghi log rõ ràng số lượng đơn đăng ký đã bị thu hồi trong mỗi đợt quét.

---

## 2. Phạm vi File Tác động

### File tạo mới hoặc chỉnh sửa:
- `services/admission/backend/src/main/java/com/englishcenter/admission/job/HoldSlotExpirationJob.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/service/EnrollmentService.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/service/impl/EnrollmentServiceImpl.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/repository/EnrollmentRepository.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/AdmissionApplication.java` (Thêm `@EnableScheduling`)

---

## 3. Thuật toán & Kỹ thuật Xử lý

### 3.1. Truy vấn Cập nhật Hàng loạt (Batch Update) trong `EnrollmentRepository`
```java
@Modifying
@Query("UPDATE Enrollment e " +
       "SET e.status = 'EXPIRED', e.updatedAt = :now " +
       "WHERE e.status = 'PENDING' AND e.holdExpiresAt < :now")
int expireOverdueEnrollments(@Param("now") LocalDateTime now);
```

### 3.2. Cấu trúc Job
```java
@Component
public class HoldSlotExpirationJob {

    private static final Logger log = LoggerFactory.getLogger(HoldSlotExpirationJob.class);
    private final EnrollmentService enrollmentService;

    public HoldSlotExpirationJob(EnrollmentService enrollmentService) {
        this.enrollmentService = enrollmentService;
    }

    /**
     * Tiến trình quét và thu hồi slot giữ chỗ quá hạn 48h.
     * Chạy định kỳ 5 phút một lần.
     */
    @Scheduled(cron = "0 */5 * * * *")
    public void scanAndExpireOverdueSlots() {
        log.info("Bắt đầu tiến trình quét đơn giữ chỗ quá hạn 48h...");
        int expiredCount = enrollmentService.expireOverdueEnrollments();
        if (expiredCount > 0) {
            log.info("Đã thu hồi thành công {} đơn giữ chỗ quá hạn, chuyển sang trạng thái EXPIRED.", expiredCount);
        }
    }
}
```

---

## 4. Kế hoạch Triển khai (Step-by-step)
1. Thêm annotation `@EnableScheduling` vào class khởi chạy `AdmissionApplication.java`.
2. Tạo interface method và query `@Modifying` trong `EnrollmentRepository`.
3. Trong `EnrollmentServiceImpl`:
   - Viết method `@Transactional public int expireOverdueEnrollments()`.
4. Tạo package `com.englishcenter.admission.job` và xây dựng class `HoldSlotExpirationJob.java`.
5. Viết unit test giả lập cập nhật các bản ghi có `hold_expires_at` nằm trong quá khứ.
6. Viết comment tiếng Việt chi tiết.

---

## 5. Tiêu chí Nghiệm thu (Acceptance Criteria)
- [ ] Khởi tạo 2 đơn `PENDING` có `hold_expires_at` nhỏ hơn thời điểm hiện tại. Khi job kích hoạt $\rightarrow$ Cả 2 đơn tự động chuyển sang `EXPIRED`.
- [ ] Đơn `PENDING` còn thời hạn (`hold_expires_at > NOW()`) tuyệt đối không bị ảnh hưởng, giữ nguyên trạng thái.
- [ ] Không gây deadlock cơ sở dữ liệu khi có nhiều bản ghi cập nhật cùng lúc.

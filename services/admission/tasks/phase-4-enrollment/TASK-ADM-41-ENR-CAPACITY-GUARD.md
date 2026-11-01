# TASK-ADM-41: Bảo vệ Sĩ số Trần Tuyệt đối khi Duyệt Đơn (Invariant Guard INV-ADM-01)

- **Mã nhiệm vụ**: `TASK-ADM-41`
- **Phân kỳ**: `Phase 4: Tuyển sinh, Giữ chỗ 48h & Xét duyệt (ENR)`
- **Độ ưu tiên**: `P0 (Bắt buộc Tuyệt đối)`
- **Yêu cầu chức năng liên quan**: `FR-ENR-02`
- **Quy tắc bất biến bảo vệ**: `INV-ADM-01` (Không bao giờ duyệt đơn nếu lớp đã đủ sĩ số tối đa)

---

## 1. Mục tiêu Nghiệp vụ & Kỹ thuật
Bảo vệ quy tắc bất biến quan trọng nhất của phân hệ Tuyển sinh: **Tuyệt đối không bao giờ được phép chuyển trạng thái đơn đăng ký sang `APPROVED` nếu sĩ số học viên chính thức (`APPROVED`) của lớp đó đã đạt trần `max_students`**:
1. Áp dụng cơ chế kiểm tra chặn (Guard Clause) trên tất cả các luồng chuyển trạng thái sang `APPROVED`:
   - Duyệt tiền mặt thủ công tại quầy bởi Học vụ (`approve-manual`).
   - Duyệt tự động khi nhận webhook hóa đơn `PAID` từ Finance Service.
   - Cập nhật trạng thái trực tiếp qua API Admin.
2. Kiểm tra xung đột đồng thời (Concurrency Control):
   - Sử dụng cơ chế khóa bi quan (`PESSIMISTIC_WRITE`) hoặc truy vấn đếm khóa dòng trên lớp học để ngăn chặn race condition khi nhiều nhân viên hoặc webhook cùng duyệt đơn đồng thời ở slot cuối cùng.
3. Nếu sĩ số đã đạt `APPROVED >= max_students`:
   - Lập tức từ chối thao tác, giữ nguyên trạng thái đơn (thường là `PENDING`).
   - Ném ngoại lệ nghiệp vụ `BusinessException(ErrorCode.ADM_CLASS_FULL)`.

---

## 2. Phạm vi File Tác động

### File tạo mới hoặc chỉnh sửa:
- `services/admission/backend/src/main/java/com/englishcenter/admission/service/impl/EnrollmentServiceImpl.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/repository/EnrollmentRepository.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/repository/ClassRepository.java`

### File cấm sửa đổi:
- `tests/invariants/test_admission_invariants.py` (Tuyệt đối không sửa assertion của bài test)

---

## 3. Thuật toán Kiểm tra Khóa Dòng & Invariant Guard

```java
@Transactional
public Enrollment approveEnrollment(Long enrollmentId) {
    // 1. Tìm đơn đăng ký
    Enrollment enrollment = enrollmentRepository.findById(enrollmentId)
        .orElseThrow(() -> new BusinessException(ErrorCode.ADM_ENROLLMENT_NOT_FOUND));

    // 2. Kiểm tra nếu đơn đã APPROVED rồi thì bỏ qua (Idempotency)
    if (enrollment.getStatus() == EnrollmentStatus.APPROVED) {
        return enrollment;
    }

    // 3. Khóa dòng lớp học để phòng ngừa xung đột đa luồng
    ClassEntity clazz = classRepository.findByIdWithLock(enrollment.getClazz().getId())
        .orElseThrow(() -> new BusinessException(ErrorCode.ADM_CLASS_NOT_FOUND));

    // 4. Đếm số lượng học viên đã APPROVED thực tế hiện tại
    long currentApprovedCount = enrollmentRepository.countByClassIdAndStatus(
        clazz.getId(), 
        EnrollmentStatus.APPROVED
    );

    // 5. INVARIANT GUARD: Kiểm tra sĩ số trần
    if (currentApprovedCount >= clazz.getMaxStudents()) {
        throw new BusinessException(
            ErrorCode.ADM_CLASS_FULL, 
            "Không thể duyệt đơn: Lớp " + clazz.getName() + " đã đủ sĩ số tối đa (" + clazz.getMaxStudents() + " học viên)"
        );
    }

    // 6. Cho phép chuyển trạng thái
    enrollment.setStatus(EnrollmentStatus.APPROVED);
    enrollment.setApprovedAt(LocalDateTime.now());
    enrollmentRepository.save(enrollment);

    // 7. Đồng bộ hồ sơ sang Student Service (TASK-ADM-47)
    studentServiceSyncHelper.syncStudentProfile(enrollment);

    return enrollment;
}
```

---

## 4. Kế hoạch Triển khai (Step-by-step)
1. Thêm phương thức truy vấn có khóa dòng trong `ClassRepository`:
   ```java
   @Lock(LockModeType.PESSIMISTIC_WRITE)
   @Query("SELECT c FROM ClassEntity c WHERE c.id = :id")
   Optional<ClassEntity> findByIdWithLock(@Param("id") Long id);
   ```
2. Cài đặt hàm `approveEnrollment` trong `EnrollmentServiceImpl` tuân thủ chuẩn xác thuật toán trên.
3. Đảm bảo mọi API duyệt đơn (`PUT /api/admission/enrollments/{id}/status`, `POST /api/admission/enrollments/{id}/approve-manual`, và webhook) đều bắt buộc đi qua hàm lõi này.
4. Viết comment tiếng Việt chi tiết cho logic bảo vệ invariant.

---

## 5. Tiêu chí Nghiệm thu (Acceptance Criteria)
- [ ] Lớp CLS-01 có `max_students = 20` và đã có 20 học viên trạng thái `APPROVED`. Khi Staff gọi API duyệt đơn thứ 21 $\rightarrow$ Nhận lỗi HTTP 400 Bad Request kèm mã lỗi `ADM_CLASS_FULL`, trạng thái đơn giữ nguyên `PENDING`.
- [ ] Chạy bộ kiểm thử tự động Invariant đạt kết quả `OK` 100%:
  ```bash
  python3 -m unittest discover -s tests/invariants -p "test_admission_invariants.py" -v
  ```

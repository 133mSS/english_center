# TASK-ADM-24: API Tính toán Slot Khả dụng Theo Thời gian Thực

- **Mã nhiệm vụ**: `TASK-ADM-24`
- **Phân kỳ**: `Phase 2: Cơ sở vật chất & Đào tạo (FAC/ACA)`
- **Độ ưu tiên**: `P0 (Bắt buộc)`
- **Yêu cầu chức năng liên quan**: `FR-ACA-05`, `FR-ENR-02`
- **Quy tắc bất biến bảo vệ**: `INV-ADM-01`, `INV-SYS-01`

---

## 1. Mục tiêu Nghiệp vụ & Kỹ thuật
Cung cấp API và hàm nội bộ tính toán chính xác số lượng chỗ trống còn lại của một lớp học theo thời gian thực (Real-time Available Slots):
1. **Công thức chuẩn xác định slot khả dụng**:
   $$\text{Available Slots} = \text{max\_students} - \text{Approved Count} - \text{Active Held Count}$$
   Trong đó:
   - `max_students`: Sĩ số tối đa được thiết lập cho lớp học.
   - `Approved Count`: Số lượng đơn đăng ký của lớp có `status = 'APPROVED'`.
   - `Active Held Count`: Số lượng đơn đăng ký của lớp có `status = 'PENDING'` VÀ thời hạn giữ chỗ chưa hết hạn (`hold_expires_at > NOW()`).
2. **Ý nghĩa nghiệp vụ**:
   - Nếu $\text{Available Slots} \le 0$: Lớp học đã kín chỗ, không thể tiếp nhận thêm bất kỳ đơn giữ chỗ mới nào.
   - Giúp giao diện hiển thị cho học viên biết lớp còn bao nhiêu chỗ trống (ví dụ: *"Chỉ còn 3 chỗ trống"*).

---

## 2. Phạm vi File Tác động

### File tạo mới hoặc chỉnh sửa:
- `services/admission/backend/src/main/java/com/englishcenter/admission/controller/ClassController.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/service/ClassService.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/service/impl/ClassServiceImpl.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/repository/EnrollmentRepository.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/dto/clazz/ClassCapacityResponse.java`

---

## 3. Đặc tả Kỹ thuật & Truy vấn SQL

### 3.1. Phương thức trong `EnrollmentRepository`
```java
// Đếm số học viên đã chính thức nhập học
long countByClassIdAndStatus(Long classId, EnrollmentStatus status);

// Đếm số đơn đang giữ chỗ 48h còn hiệu lực
@Query("SELECT COUNT(e) FROM Enrollment e " +
       "WHERE e.clazz.id = :classId " +
       "  AND e.status = 'PENDING' " +
       "  AND e.holdExpiresAt > :now")
long countActiveHeldSlots(@Param("classId") Long classId, @Param("now") LocalDateTime now);
```

### 3.2. Đặc tả API Endpoint
- **URL**: `GET /api/admission/classes/{id}/capacity` (Public API)
- **Response Thành công (HTTP 200 OK)**:
  ```json
  {
    "success": true,
    "data": {
      "class_id": 10,
      "class_name": "Lớp IELTS 6.5 Sáng 2-4-6",
      "max_students": 20,
      "approved_count": 14,
      "active_held_count": 3,
      "available_slots": 3,
      "is_full": false
    },
    "message": "Tra cứu sĩ số lớp thành công"
  }
  ```

---

## 4. Kế hoạch Triển khai (Step-by-step)
1. Thêm các hàm đếm vào `EnrollmentRepository`.
2. Trong `ClassServiceImpl`:
   - Viết hàm `getClassCapacity(Long classId)`: Lấy thông tin lớp, gọi 2 hàm đếm từ repository, tính `available_slots = max - approved - held`.
   - Nếu `available_slots < 0`, chuẩn hóa trả về 0.
   - Thiết lập `is_full = (available_slots == 0)`.
3. Bổ sung endpoint trong `ClassController`.
4. Viết comment tiếng Việt đầy đủ.

---

## 5. Tiêu chí Nghiệm thu (Acceptance Criteria)
- [ ] Lớp có `max = 20`, 18 học viên `APPROVED`, 2 đơn `PENDING` (còn hạn 48h) $\rightarrow$ `available_slots = 0`, `is_full = true`.
- [ ] Khi 1 đơn `PENDING` hết hạn (quá 48h) $\rightarrow$ Đơn đó không được tính vào `active_held_count`, `available_slots` tự động tăng lên 1 mà không cần can thiệp thủ công.
- [ ] Mọi trường trong response đều dùng `snake_case`.

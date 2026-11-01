# TASK-ADM-23: Động cơ Chống Xung đột Lịch Phòng & Giảng viên (Conflict Engine)

- **Mã nhiệm vụ**: `TASK-ADM-23`
- **Phân kỳ**: `Phase 2: Cơ sở vật chất & Đào tạo (FAC/ACA)`
- **Độ ưu tiên**: `P0 (Bắt buộc)`
- **Yêu cầu chức năng liên quan**: `FR-ACA-03`
- **Quy tắc bất biến bảo vệ**: `INV-SYS-01`

---

## 1. Mục tiêu Nghiệp vụ & Kỹ thuật
Xây dựng Động cơ Phân tích Xung đột Lịch học (`ConflictEngine`) nhằm phát hiện và ngăn chặn triệt để tình trạng xung đột tài nguyên khi xếp lớp:
1. **Xung đột Phòng học (`ADM_ROOM_CONFLICT`)**:
   - Một phòng học không thể phục vụ 2 lớp học khác nhau có cùng mẫu ngày (`day_pattern`) và giao thoa về mặt thời gian (Time Overlap) trong cùng khoảng thời gian khóa học diễn ra (`[start_date, end_date]`).
2. **Xung đột Giảng viên (`ADM_TEACHER_CONFLICT`)**:
   - Một giáo viên không thể đứng lớp cùng lúc tại 2 lớp khác nhau có cùng mẫu ngày và giao thoa thời gian trong cùng khoảng ngày.
3. **Quy tắc giao thoa thời gian chuẩn (Interval Overlap Rule)**:
   - Hai khoảng thời gian $[S_1, E_1]$ và $[S_2, E_2]$ bị giao thoa khi và chỉ khi:
     $$\max(S_1, S_2) < \min(E_1, E_2)$$
   - Áp dụng đồng thời cho cả khoảng ngày hoạt động (`start_date` $\rightarrow$ `end_date`) và khung giờ trong ngày (`start_time` $\rightarrow$ `end_time`).

---

## 2. Phạm vi File Tác động

### File tạo mới hoặc chỉnh sửa:
- `services/admission/backend/src/main/java/com/englishcenter/admission/engine/ConflictEngine.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/engine/dto/ConflictCheckRequest.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/engine/dto/ConflictCheckResult.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/repository/ClassRepository.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/service/impl/ClassServiceImpl.java`

---

## 3. Thuật toán & Câu truy vấn Phát hiện Xung đột

### 3.1. Truy vấn Kiểm tra Xung đột Phòng học
```sql
SELECT c FROM ClassEntity c
WHERE c.room.id = :roomId
  AND c.status IN ('OPEN', 'IN_PROGRESS')
  AND (:classId IS NULL OR c.id <> :classId)
  AND c.dayPattern = :dayPattern
  AND (c.startDate <= :endDate AND c.endDate >= :startDate)
  AND (c.startTime < :endTime AND c.endTime > :startTime)
```
Nếu tìm thấy ít nhất 1 lớp $\rightarrow$ Xung đột phòng học! Ném lỗi `ADM_ROOM_CONFLICT` kèm tên lớp đang chiếm chỗ.

### 3.2. Truy vấn Kiểm tra Xung đột Giáo viên
```sql
SELECT c FROM ClassEntity c
WHERE c.teacher.id = :teacherId
  AND c.status IN ('OPEN', 'IN_PROGRESS')
  AND (:classId IS NULL OR c.id <> :classId)
  AND c.dayPattern = :dayPattern
  AND (c.startDate <= :endDate AND c.endDate >= :startDate)
  AND (c.startTime < :endTime AND c.endTime > :startTime)
```
Nếu tìm thấy ít nhất 1 lớp $\rightarrow$ Xung đột giáo viên! Ném lỗi `ADM_TEACHER_CONFLICT` kèm tên lớp đang trùng lịch.

---

## 4. Kế hoạch Triển khai (Step-by-step)
1. Thêm các câu truy vấn `@Query` kiểm tra xung đột vào `ClassRepository`.
2. Tạo component `ConflictEngine.java` với phương thức:
   ```java
   /**
    * Kiểm tra xung đột lịch học của phòng và giáo viên
    * @param request Thông tin lịch lớp cần kiểm tra
    * @throws BusinessException nếu phát hiện bất kỳ xung đột nào
    */
   void validateScheduleConflict(ConflictCheckRequest request);
   ```
3. Tích hợp `ConflictEngine.validateScheduleConflict` vào đầu hàm `createClass` và `updateClass` của `ClassServiceImpl`.
4. Viết unit test giả lập các trường hợp:
   - Trùng giờ nhưng khác ngày trong tuần $\rightarrow$ Hợp lệ.
   - Trùng ngày, trùng phòng, khung giờ sát nhau (08:00 - 09:30 và 09:30 - 11:00) $\rightarrow$ Không xung đột.
   - Trùng ngày, trùng phòng, giao thoa 15 phút $\rightarrow$ Phát hiện xung đột chính xác.
5. Viết comment tiếng Việt chi tiết cho logic kiểm tra.

---

## 5. Tiêu chí Nghiệm thu (Acceptance Criteria)
- [ ] Mở lớp A (Phòng 101, T2-4-6, 08:00 - 09:30). Mở tiếp lớp B (Phòng 101, T2-4-6, 09:00 - 10:30) $\rightarrow$ Trả về mã lỗi HTTP 409 `ADM_ROOM_CONFLICT`.
- [ ] Gán Thầy Hùng dạy Lớp A (08:00 - 09:30), sau đó gán Thầy Hùng dạy Lớp C ở phòng khác cùng ca (08:00 - 09:30) $\rightarrow$ Trả về mã lỗi HTTP 409 `ADM_TEACHER_CONFLICT`.
- [ ] Không có xung đột $\rightarrow$ Cho phép lưu lớp thành công.

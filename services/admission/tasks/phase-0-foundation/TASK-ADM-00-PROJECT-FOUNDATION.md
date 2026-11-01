# TASK-ADM-00: Thiết lập Nền tảng Đa tầng, Jackson snake_case & Global Exception Handler

- **Mã nhiệm vụ**: `TASK-ADM-00`
- **Phân kỳ**: `Phase 0: Nền móng & Hạ tầng (INF)`
- **Độ ưu tiên**: `P0 (Bắt buộc)`
- **Yêu cầu chức năng liên quan**: Toàn bộ hệ thống (FR-IAM, FR-FAC, FR-ACA, FR-TST, FR-ENR, FR-OPS)
- **Quy tắc bất biến bảo vệ**: `INV-SYS-01` (Quy ước định dạng `snake_case` toàn diện)

---

## 1. Mục tiêu Nghiệp vụ & Kỹ thuật
Thiết lập chuẩn kiến trúc 3 tầng (Controller - Service - Repository) trong Spring Boot 3.3 (Java 21), đảm bảo:
1. Định dạng JSON giao tiếp giữa Client và Backend luôn tuân thủ chuẩn `snake_case` thông qua Jackson cấu hình tập trung.
2. Cấu trúc Response đồng nhất với `ApiResponse<T>` cho cả trường hợp thành công và thất bại.
3. Bộ bắt ngoại lệ tập trung `@RestControllerAdvice` bắt các lỗi: validation (`MethodArgumentNotValidException`), nghiệp vụ (`BusinessException`), thực thể không tìm thấy (`EntityNotFoundException`), xung đột dữ liệu (`DataIntegrityViolationException`), và lỗi không mong muốn (500), tuyệt đối không để lộ Java StackTrace ra ngoài.

---

## 2. Phạm vi File Tác động

### File tạo mới hoặc chỉnh sửa:
- `services/admission/backend/src/main/java/com/englishcenter/admission/common/dto/ApiResponse.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/common/dto/ErrorDetail.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/common/exception/BusinessException.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/common/exception/ErrorCode.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/common/exception/GlobalExceptionHandler.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/config/JacksonConfig.java`
- `services/admission/backend/src/main/resources/application.properties`

### File cấm sửa đổi:
- `tests/invariants/*`
- Các service khác (`student`, `learning`, `finance`)

---

## 3. Đặc tả Kỹ thuật Chi tiết

### 3.1. Cấu hình Jackson snake_case
Áp dụng cấu hình `PropertyNamingStrategies.SNAKE_CASE` để tự động chuyển đổi:
- Java Property: `maxStudents` $\leftrightarrow$ JSON Field: `max_students`
- Java Property: `holdExpiresAt` $\leftrightarrow$ JSON Field: `hold_expires_at`

### 3.2. Cấu trúc `ApiResponse<T>`
```java
// Thành công:
{
  "success": true,
  "data": { ... },
  "message": "Thực hiện thành công"
}

// Thất bại:
{
  "success": false,
  "error": {
    "code": "ADM_CLASS_FULL",
    "message": "Lớp học đã đạt sĩ số tối đa"
  }
}
```

### 3.3. Danh mục Mã lỗi Chuẩn (`ErrorCode`)
- `ADM_INVALID_CREDENTIALS` (401): Thông tin đăng nhập không chính xác
- `ADM_TOKEN_EXPIRED` (401): Phiên làm việc đã hết hạn
- `ADM_TOKEN_INVALID` (401): Token không hợp lệ hoặc đã bị thu hồi
- `ADM_FORBIDDEN` (403): Không có quyền truy cập chức năng này
- `ADM_USER_NOT_FOUND` (404): Người dùng không tồn tại
- `ADM_COURSE_NOT_FOUND` (404): Khóa học không tồn tại
- `ADM_CLASS_NOT_FOUND` (404): Lớp học không tồn tại
- `ADM_ENROLLMENT_NOT_FOUND` (404): Đơn đăng ký không tồn tại
- `ADM_ROOM_NOT_FOUND` (404): Phòng học không tồn tại
- `ADM_COURSE_CODE_EXISTS` (409): Mã khóa học đã tồn tại
- `ADM_CLASS_FULL` (400): Lớp học đã đạt sĩ số tối đa
- `ADM_ROOM_CAPACITY_EXCEEDED` (400): Sĩ số tối đa vượt quá sức chứa của phòng
- `ADM_ROOM_CONFLICT` (409): Phòng học bị trùng lịch với lớp khác
- `ADM_TEACHER_CONFLICT` (409): Giảng viên bị trùng lịch dạy với lớp khác
- `ADM_HOLD_EXPIRED` (400): Đơn đăng ký đã hết thời hạn giữ chỗ 48h
- `ADM_INVALID_STATE_TRANSITION` (400): Chuyển trạng thái đơn không hợp lệ
- `ADM_VALIDATION_ERROR` (400): Dữ liệu gửi lên không đúng định dạng

---

## 4. Kế hoạch Triển khai (Step-by-step)
1. Tạo package `com.englishcenter.admission.common.dto` và tạo `ApiResponse.java`, `ErrorDetail.java`.
2. Tạo package `com.englishcenter.admission.common.exception` và định nghĩa `ErrorCode.java` enum, `BusinessException.java`.
3. Cài đặt `@RestControllerAdvice` trong `GlobalExceptionHandler.java` bắt:
   - `BusinessException` $\rightarrow$ Trả về mã lỗi HTTP tương ứng kèm `ErrorCode`.
   - `MethodArgumentNotValidException` $\rightarrow$ Bắt lỗi `@Valid` trường đầu tiên hoặc tổng hợp các trường vi phạm và trả về `ADM_VALIDATION_ERROR`.
   - `Exception` chung $\rightarrow$ Trả về lỗi 500 kèm mã `INTERNAL_SERVER_ERROR`, không để lộ stack trace.
4. Tạo `JacksonConfig.java` cấu hình ObjectMapper hoặc cấu hình trong `application.properties`:
   ```properties
   spring.jackson.property-naming-strategy=SNAKE_CASE
   spring.jackson.deserialization.fail-on-unknown-properties=false
   ```
5. Viết comment tiếng Việt đầy đủ cho từng class và phương thức.

---

## 5. Tiêu chí Nghiệm thu (Acceptance Criteria)
- [ ] Gửi Request với trường payload `snake_case` (ví dụ `{"course_code": "IELTS-01"}`), Java Backend tự động map vào entity/DTO field `courseCode`.
- [ ] Mọi Response từ Controller trả về đúng mẫu chuẩn `{"success": true/false, ...}`.
- [ ] Khi ném `BusinessException(ErrorCode.ADM_CLASS_FULL)`, client nhận được HTTP 400 và JSON:
  ```json
  {
    "success": false,
    "error": {
      "code": "ADM_CLASS_FULL",
      "message": "Lớp học đã đạt sĩ số tối đa"
    }
  }
  ```
- [ ] Bộ Invariant Test `INV-SYS-01` chạy đạt `OK`.

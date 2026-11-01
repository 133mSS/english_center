# TASK-ADM-03: Cấu hình HTTP Clients Tích hợp Liên Service (Finance & Student)

- **Mã nhiệm vụ**: `TASK-ADM-03`
- **Phân kỳ**: `Phase 0: Nền móng & Hạ tầng (INF)`
- **Độ ưu tiên**: `P1`
- **Yêu cầu chức năng liên quan**: FR-ENR-01, FR-ENR-06, FR-ENR-08 (Hợp đồng liên Service)
- **Quy tắc bất biến bảo vệ**: `INV-SYS-02` (Không cross-schema query, chỉ giao tiếp qua REST API)

---

## 1. Mục tiêu Nghiệp vụ & Kỹ thuật
Xây dựng lớp giao tiếp HTTP Client độc lập (sử dụng Spring Boot 3 `RestClient` hoặc `WebClient`) để gọi sang hai phân hệ lân cận:
1. **Finance Service** (Port 8084):
   - Gọi API sinh hóa đơn học phí khi phát sinh đơn đăng ký mới (`POST http://finance-service:8084/api/finance/invoices`).
   - Nhận diện trạng thái hóa đơn.
2. **Student Service** (Port 8082):
   - Gọi API tạo hoặc kích hoạt hồ sơ học vụ khi đơn đăng ký được duyệt (`POST http://student-service:8082/api/student/students`).
3. Đảm bảo có cơ chế timeout, retry và xử lý lỗi mềm dẻo (Circuit Breaker / Fallback) để sự cố của service lân cận không làm sập luồng đăng ký của Admission.

---

## 2. Phạm vi File Tác động

### File tạo mới hoặc chỉnh sửa:
- `services/admission/backend/src/main/java/com/englishcenter/admission/client/FinanceServiceClient.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/client/StudentServiceClient.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/client/dto/CreateInvoiceRequest.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/client/dto/InvoiceResponse.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/client/dto/CreateStudentProfileRequest.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/client/dto/StudentProfileResponse.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/config/RestClientConfig.java`

---

## 3. Đặc tả Hợp đồng Giao tiếp Liên Service

### 3.1. Gọi Finance Service - Tạo Hóa đơn
- **URL**: `POST ${services.finance.url}/api/finance/invoices`
- **Request Body**:
  ```json
  {
    "enrollment_id": "ENR-2026-0001",
    "student_id": "USR-2026-0001",
    "amount": 4500000.0,
    "due_date": "2026-11-03T23:59:59"
  }
  ```
- **Response**: Trả về `invoice_id` và trạng thái `UNPAID`.

### 3.2. Gọi Student Service - Tạo Hồ sơ Học viên
- **URL**: `POST ${services.student.url}/api/student/students`
- **Request Body**:
  ```json
  {
    "user_id": "USR-2026-0001",
    "full_name": "Nguyen Van A",
    "email": "student@englishcenter.edu.vn",
    "phone": "0912345678",
    "enrolled_class_id": "CLS-2026-0001"
  }
  ```
- **Response**: Trả về `student_code` (ví dụ `STU-0001`) và trạng thái hồ sơ `ACTIVE`.

---

## 4. Kế hoạch Triển khai (Step-by-step)
1. Thêm cấu hình URL của các service vào `application.properties`:
   ```properties
   services.finance.url=${FINANCE_SERVICE_URL:http://localhost:8084}
   services.student.url=${STUDENT_SERVICE_URL:http://localhost:8082}
   ```
2. Cấu hình Bean `RestClient` với timeout kết nối 3s và đọc dữ liệu 5s trong `RestClientConfig.java`.
3. Xây dựng interface và implementation `FinanceServiceClient`:
   - Bắt các lỗi HTTP 4xx, 5xx và bọc vào `BusinessException` hoặc ghi log cảnh báo khi không thể kết nối.
4. Xây dựng interface và implementation `StudentServiceClient`:
   - Đảm bảo gọi bất đồng bộ (`@Async`) hoặc có cơ chế bù đắp nếu Student Service tạm thời gián đoạn.
5. Viết comment tiếng Việt đầy đủ cho từng hàm xử lý.

---

## 5. Tiêu chí Nghiệm thu (Acceptance Criteria)
- [ ] Khi mock endpoint của Finance Service trả về 201 Created, `FinanceServiceClient` trích xuất thành công `invoice_id`.
- [ ] Khi Finance Service sập (Connection Refused), hàm ném ngoại lệ rõ ràng hoặc xử lý fallback, ghi nhận log hệ thống.
- [ ] Đảm bảo 100% payload trao đổi giữa các service sử dụng chuẩn `snake_case`.

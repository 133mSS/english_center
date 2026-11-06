# English Center Management System

## What this is (Bản chất hệ thống)

Hệ thống quản lý vận hành, đào tạo, tuyển sinh và học phí cho Trung tâm Anh ngữ.

Người dùng bao gồm 4 vai trò chính: **Quản trị viên (Admin)**, **Học vụ (Staff)**, **Giáo viên (Teacher)**, và **Học viên (Student)**.

Dự án áp dụng kiến trúc **Microservices Polyglot Monorepo**:
- **Admission Service** (Port 8081): Java 21 Spring Boot 3.3 (chịu trách nhiệm Cấp phát JWT Auth, Khóa học, Lớp học, Xét duyệt tuyển sinh).
- **Student Service** (Port 8082): Python FastAPI (Hồ sơ học viên, Điểm danh buổi học).
- **Learning Service** (Port 8083): Python FastAPI (Kho học liệu, Slide, Sổ điểm đánh giá).
- **Finance Service** (Port 8084): Python FastAPI (Biểu phí, Hóa đơn, Ghi nhận thanh toán).
- **Nginx API Gateway** (Port 8080): Điểm truy cập duy nhất, định tuyến API và phục vụ giao diện tĩnh.
- **PostgreSQL 16** (Port 5432): 4 schema độc lập (`admission`, `student`, `learning`, `finance`).

### Ranh giới nghiệp vụ bất biến (Core Invariants)
- **Không tự bịa dữ liệu**: Mọi trạng thái học phí, điểm thi, sĩ số phải phản ánh đúng từ database, không suy diễn.
- **Không vượt sĩ số**: Không bao giờ duyệt đơn đăng ký (`APPROVED`) nếu lớp học đã đạt `max_students`.
- **Cô lập dữ liệu người dùng**: Học viên chỉ xem được hồ sơ, điểm số, hóa đơn của chính mình. Giáo viên chỉ điểm danh và chấm điểm các lớp mình phụ trách.
- **Tính toàn vẹn thanh toán**: Hóa đơn chỉ chuyển sang `PAID` khi tổng số tiền thanh toán thực tế `>=` số tiền hóa đơn. Không ghi nhận lặp giao dịch có cùng `transaction_ref`.

---

## How features get built (Quy trình phát triển)

Mỗi đơn vị công việc (Task) được mô tả tại `docs/tasks/`:

1. **Đọc kỹ Task & Contract**: Xem file task trong `docs/tasks/active/`, đối chiếu với `docs/contract.md` và `docs/invariants.md`. Không tự suy diễn mở rộng phạm vi.
2. **Làm việc từng bước nhỏ**: Thay đổi tối giản, code rõ ràng, không over-engineering.
3. **Bảo vệ Invariant Tests**: Sau khi code, bắt buộc chạy kiểm thử:
   ```bash
   python3 -m unittest discover -s tests/invariants -p "test_*.py" -v
   ```
   Tất cả 15 tests phải xanh (`OK`). Nếu test fail, phải sửa code nghiệp vụ, **tuyệt đối không sửa assertion của test** để che giấu lỗi.
4. **Báo cáo nghiệm thu**: Ghi lại file đã sửa, test đã chạy vào `docs/tasks/completed/`.

---

## Conventions (Quy ước làm việc thực dụng)

- **Đơn giản & Trực tiếp**: Ưu tiên giải pháp dễ hiểu, dễ chạy trên máy cá nhân. Không cài thêm thư viện phức tạp nếu thư viện chuẩn đã giải quyết được.
- **Định dạng API**: Toàn bộ Request payload, Response JSON và Query params bắt buộc dùng **`snake_case`**.
- **Không Emoji trong code**: Không dùng emoji trong code logic, log backend, commit message kỹ thuật hoặc tên biến. Emoji chỉ dùng trên giao diện người dùng nếu cần thiết.
- **Frontend Hot-Reload**: Nginx ánh xạ trực tiếp thư mục `services/{module}/frontend/` và `shared/`. Khi sửa HTML/JS/CSS, chỉ cần lưu file và ấn **F5** trên trình duyệt, không cần build lại Docker.
- **Khi xảy ra lỗi**: Chứng minh lỗi bằng test case hoặc log cụ thể, tìm đúng nguyên nhân gốc rễ (root cause) và sửa dứt điểm. Không dùng mẹo tạm bợ (workaround).

---

## Coding Rules & Standards (Quy chuẩn Lập trình cho Agent)

### 1. Kiến trúc Đa tầng & Phân chia Trách nhiệm (Layered Architecture)
- **Spring Boot (Java 21 - Admission Service)**:
  - Bắt buộc tuân thủ 3 tầng: `Controller` (Validate & nhận/trả DTO) ➔ `Service` (Nghiệp vụ cốt lõi) ➔ `Repository` (Spring Data JPA).
  - Không viết business logic trong Controller. Controller chỉ nhận DTO, kiểm tra `@Valid`, gọi Service và trả về `ResponseEntity<ApiResponse<T>>`.
  - Mọi thao tác ghi/sửa dữ liệu nhiều bước phải có annotation `@Transactional`.
  - Cấu hình Jackson `PropertyNamingStrategies.SNAKE_CASE` để tự động ánh xạ giữa Java `camelCase` và JSON `snake_case`.
- **FastAPI (Python 3.11 - Student, Learning, Finance Services)**:
  - Phân tầng rõ ràng: `routers/` (Định tuyến API) ➔ `services/` (Logic nghiệp vụ) ➔ `models/` / `crud/` (SQLAlchemy / Database).
  - Sử dụng Pydantic v2 `BaseModel` cho mọi Request/Response schema, ép kiểu chặt chẽ bằng Type Hints (`typing`).
  - Không nối chuỗi SQL thủ công (Raw SQL string interpolation) để phòng ngừa triệt để lỗi SQL Injection.

### 2. Định dạng Response & Bắt lỗi Toàn cục (Global Exception Handling)
- **Cấu trúc Response Chuẩn**:
  - Thành công: `{"success": true, "data": { ... }, "message": "Thông báo thân thiện"}`
  - Thất bại: `{"success": false, "error": {"code": "MÃ_LỖI_NGHIỆP_VỤ", "message": "Mô tả lỗi"}}`
- **Xử lý Ngoại lệ Tập trung**:
  - Java: Bắt buộc dùng `@RestControllerAdvice` bắt các lỗi `MethodArgumentNotValidException`, `BusinessException`, `EntityNotFoundException`. Tuyệt đối không để lộ Java StackTrace 500 ra client.
  - Python: Bắt buộc dùng `@app.exception_handler(HTTPException)` và `@app.exception_handler(RequestValidationError)` để format lại response JSON chuẩn.
- **HTTP Status Codes chuẩn REST**: `200 OK`, `201 Created`, `400 Bad Request`, `401 Unauthorized`, `403 Forbidden`, `404 Not Found`, `409 Conflict`.

### 3. Ranh giới Cơ sở Dữ liệu & Microservices (Database Isolation)
- **Tuyệt đối không Cross-Schema Query**: Mỗi service chỉ được truy vấn schema của mình (`admission.*`, `student.*`, `learning.*`, `finance.*`). Cấm viết câu lệnh SQL JOIN chéo schema giữa các service.
- **Giao tiếp liên Service**: Mọi nhu cầu lấy hoặc đồng bộ dữ liệu giữa các module bắt buộc phải thông qua REST API nội bộ hoặc event/webhook.

### 4. Quy chuẩn Frontend (Vanilla JS & Design System)
- **Design Tokens**: Bắt buộc sử dụng CSS variables từ `/shared/css/variables.css` (ví dụ: `var(--color-primary)`). Không tự ý hardcode mã màu hex trong CSS riêng của module.
- **Gọi API**: Mọi request API từ giao diện phải gọi qua wrapper `/shared/js/api.js` và đính kèm JWT Token tự động từ `/shared/js/auth.js`.
- **Trải nghiệm người dùng**: Luôn có trạng thái chờ (loading spinner hoặc disable nút bấm) khi gọi API và hiển thị thông báo lỗi rõ ràng cho người dùng từ trường `error.message`.

### 5. Code Đơn giản, Comment Chi tiết & Clean Code (KISS Principle)
- **Code Đơn giản & Trực diện (KISS)**: Ưu tiên cách viết code sáng sủa, tường minh, dễ hiểu và dễ debug. Tuyệt đối không over-engineering, không lạm dụng các design pattern phức tạp hoặc trừu tượng hóa quá mức nếu bài toán không đòi hỏi.
- **Comment Chi tiết & Tận tâm**:
  - Mọi Controller, Service method, Endpoint handler, DTO/Model, và Helper function bắt buộc có comment tiếng Việt giải thích: mục đích hàm, ý nghĩa các tham số đầu vào, kết quả trả về và các ngoại lệ/mã lỗi có thể ném ra.
  - Các khối xử lý logic nghiệp vụ trọng yếu (như kiểm tra xung đột phòng/giáo viên, thuật toán chấm điểm, chuyển trạng thái đơn 48h, tính toán số tiền) phải có comment giải thích từng bước (step-by-step) để bất kỳ thành viên nào trong nhóm cũng hiểu và bảo trì được ngay.
- **Không commit bí mật**: Mật khẩu, JWT secret key, API key luôn phải đọc từ biến môi trường (`os.getenv` hoặc `System.getenv`), không hardcode trong code.
- **Không emoji trong code**: Không dùng emoji trong code logic, tên hàm, tên biến, log backend hoặc commit message kỹ thuật (chỉ dùng trên giao diện người dùng nếu cần).
- **Giữ nguyên docstrings**: Bảo toàn các comment và docstring hiện có không liên quan đến phạm vi thay đổi.

### 6. Cổng Kiểm soát Chất lượng (Testing Quality Gate)
- Sau khi viết hoặc sửa bất kỳ dòng code nào, Agent bắt buộc phải chạy bộ Invariant Tests:
  ```bash
  python3 -m unittest discover -s tests/invariants -p "test_*.py" -v
  ```
- Toàn bộ 15 tests phải xanh (`OK`). Tuyệt đối không sửa assertion của file test để đối phó với lỗi code.

---

## Architecture & Ports (Bản đồ Dịch vụ)

| Thành phần | Cổng | Công nghệ | Nhiệm vụ chính |
|---|---|---|---|
| **Gateway** | `8080` | Nginx Alpine | Reverse proxy, static file server, hot-reload |
| **Admission** | `8081` | Spring Boot 3.3 (Java 21) | Auth (JWT), Khóa học, Lớp học, Tuyển sinh |
| **Student** | `8082` | FastAPI (Python 3.11) | Hồ sơ học viên, Điểm danh |
| **Learning** | `8083` | FastAPI (Python 3.11) | Học liệu, Slide, Sổ điểm đánh giá |
| **Finance** | `8084` | FastAPI (Python 3.11) | Biểu phí, Lập hóa đơn, Ghi nhận đóng tiền |
| **Database** | `5432` | PostgreSQL 16 | 4 schema riêng: `admission`, `student`, `learning`, `finance` |

### Các lệnh điều khiển hệ thống
```bash
# Khởi chạy toàn bộ hệ thống
docker compose up -d --build

# Dừng hệ thống
docker compose down

# Chạy bộ Invariant Tests kiểm soát chất lượng
python3 -m unittest discover -s tests/invariants -p "test_*.py" -v

# Kiểm tra cấu hình Docker
docker compose config
```

---

## Visual Language (Ngôn ngữ Thiết kế)

Màu sắc trên giao diện mang ý nghĩa nghiệp vụ rõ ràng, định nghĩa tại `shared/css/variables.css`:

| Token | Giá trị Hex | Ý nghĩa sử dụng |
|---|---|---|
| `--color-primary` | `#2563eb` | Hành động chính, link, sidebar active, button chính |
| `--color-success` | `#16a34a` | Đã thanh toán (`PAID`), đã duyệt (`APPROVED`), có mặt (`PRESENT`) |
| `--color-warning` | `#f59e0b` | Chờ duyệt (`PENDING`), đi muộn (`LATE`), cảnh báo hạn nộp |
| `--color-danger` | `#dc2626` | Chưa thanh toán (`UNPAID`), từ chối (`REJECTED`), vắng mặt (`ABSENT`) |
| `--color-info` | `#0ea5e9` | Thông tin khóa học, badge bổ trợ, thông báo |
| `--color-bg` | `#f8fafc` | Nền ứng dụng Slate nhẹ |
| `--color-surface` | `#ffffff` | Nền thẻ Card, Modal, Bảng dữ liệu |

Mọi trang HTML của các module chỉ cần nhúng:
```html
<link rel="stylesheet" href="/shared/css/variables.css">
<link rel="stylesheet" href="/shared/css/base.css">
<link rel="stylesheet" href="/shared/css/components.css">
<link rel="stylesheet" href="/shared/css/layout.css">
<script src="/shared/js/auth.js"></script>
<script src="/shared/js/api.js"></script>
<script src="/shared/js/layout.js"></script>
```

---

## Document Map (Bản đồ Tài liệu SSOT)

- `docs/spec.md`: Đặc tả nghiệp vụ chi tiết & Explicit Non-Goals.
- `docs/contract.md`: Hợp đồng kỹ thuật (API, Domain Model, State Machine, Phân quyền).
- `docs/invariants.md`: Danh mục 15 quy tắc bất biến (P0/P1) và mapping test.
- `docs/state.md`: Nhật ký tiến độ dự án (Chỉ Team Lead cập nhật).
- `docs/agent-workflow.md`: Quy trình phối hợp đa Agent và ranh giới quyền sửa file.
- `docs/decisions/`: Architecture Decision Records (ADR-001 đến ADR-005).
- `docs/tasks/`: Task backlog và chi tiết công việc đang thực hiện.

---

## Status & Increments (Nhật ký Tiến độ Dự án)

### Wave 0 — Nền móng Kỹ thuật & Project Scaffolding (Hoàn tất)
- Dựng hoàn chỉnh bộ điều phối 6 container trong `docker-compose.yml`.
- Thiết lập Nginx Gateway định tuyến API và mount trực tiếp frontends.
- Khởi tạo PostgreSQL 16 với 4 schema và bộ dữ liệu seed mẫu tại `scripts/init-db.sql`.
- Hoàn thiện Design System chung (`shared/`): CSS Variables, Components, Dynamic Sidebar/Header, Trang đăng nhập 1-Click test và Trang chủ Tổng quan Dashboard.
- Xây dựng mã nguồn mẫu cho cả 4 services:
  - `admission-service`: REST Controller, JPA Entity, cấu hình snake_case, JwtUtil.
  - `student-service`, `learning-service`, `finance-service`: FastAPI endpoints kết nối database tương ứng.
- Tạo bộ kiểm thử tự động 15 Invariant Tests tại `tests/invariants/` (100% Passed).

### Wave 1 — Chức năng Cốt lõi Sprint 1 (Đang triển khai)
- **TASK-W1-ADM-01**: Kiểm tra sĩ số lớp trước khi duyệt đơn đăng ký (`INV-ADM-01`).
- **TASK-W1-STU-01**: Ngăn chặn trùng lặp điểm danh trong ngày của học viên (`INV-STU-01`).
- **TASK-W1-LRN-01**: Ràng buộc thang điểm hợp lệ `0 <= score <= max_score` (`INV-LRN-01`).
- **TASK-W1-FIN-01**: Cơ chế Idempotency thanh toán chống lặp `transaction_ref` (`INV-FIN-02`).

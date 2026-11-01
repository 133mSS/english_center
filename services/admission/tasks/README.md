# Kế hoạch & Danh mục Task Phân hệ Tuyển sinh & Định danh (Admission & Identity Service)

> **Căn cứ tài liệu kỹ thuật chuẩn (SSOT - Ver 1 v3.5)**:
> - Đặc tả Nghiệp vụ & BI: [`admission-ba-bi-spec.md`](../docs/admission-ba-bi-spec.md)
> - Đặc tả Kiến trúc Kỹ thuật: [`admission-tech-spec.md`](../docs/admission-tech-spec.md)
> - Đặc tả Cơ sở dữ liệu: [`admission-schema-spec.md`](../docs/admission-schema-spec.md)
> - Đặc tả Thiết kế UML: [`admission-uml-spec.md`](../docs/admission-uml-spec.md)
> - Quy chuẩn Lập trình: [`AGENTS.md`](../../../AGENTS.md) | [`GEMINI.md`](../../../GEMINI.md)

---

## 1. Tổng quan Kiến trúc & Nguyên tắc Triển khai

Phân hệ **Admission Service** (Port 8081) được xây dựng trên nền tảng **Java 21 + Spring Boot 3.3.4**, chịu trách nhiệm:
1. Xác thực tập trung (Dual JWT), phân quyền RBAC và quản lý phiên người dùng cho toàn bộ hệ thống.
2. Quản lý cơ sở vật chất (Phòng học, ca học) và danh mục đào tạo (Khóa học, lớp học).
3. Động cơ chống xung đột lịch học (Conflict Engine) cho phòng học và giảng viên.
4. Nền tảng khảo thí đầu vào trực tuyến 3 kỹ năng (Listening, Reading, Grammar) và tự động đề xuất lộ trình.
5. Quy trình tuyển sinh đa kênh, bảo vệ sĩ số trần, giữ chỗ 48h và liên kết thanh toán với Finance Service, đồng bộ hồ sơ sang Student Service.
6. Hệ thống báo cáo phân tích thông minh (BI Funnel, Pipeline Revenue, DAU/MAU).

### Nguyên tắc Bất biến Bắt buộc Tuân thủ:
- **Kiến trúc 3 tầng chuẩn**: `Controller` (Validate DTO) $\rightarrow$ `Service` (Business logic, `@Transactional`) $\rightarrow$ `Repository` (Spring Data JPA).
- **Chuẩn hóa API**: 100% Request Payload, Response JSON và Query Params sử dụng `snake_case`.
- **Cấu trúc Response Chuẩn**:
  - Thành công: `{"success": true, "data": { ... }, "message": "Thông báo"}`
  - Thất bại: `{"success": false, "error": {"code": "MÃ_LỖI", "message": "Mô tả lỗi"}}`
- **Cô lập Schema**: Chỉ đọc/ghi trong schema `admission.*`. Không truy vấn trực tiếp schema của các service khác.
- **Bảo toàn Invariant Tests**: Luôn chạy `python3 -m unittest discover -s tests/invariants -p "test_*.py" -v` và bảo đảm 100% xanh.

---

## 2. Ma trận Phân kỳ & Danh mục Toàn bộ Tasks (WBS)

Hệ thống được chia thành **7 Phases** với tổng cộng **32 Tasks** rõ ràng, độc lập và có thứ tự ưu tiên:

```
Phase 0: Nền móng & Hạ tầng (INF)
   │
   ├── Phase 1: Quản trị Định danh & Phiên (IAM) ──┐
   │                                               │
   ├── Phase 2: Cơ sở vật chất & Đào tạo (FAC/ACA) ┼── Phase 4: Tuyển sinh & Giữ chỗ 48h (ENR)
   │                                               │         │
   └── Phase 3: Khảo thí Đầu vào (TST) ────────────┘         ├── Phase 5: Xuất dữ liệu & BI (OPS/BI)
                                                             │
                                                             └── Phase 6: Giao diện Người dùng (UI)
```

### Bảng Tổng hợp Toàn bộ Task

| Task ID | Tên Nhiệm vụ | FR Liên quan | Độ ưu tiên | File Task Chi tiết |
|---|---|---|---|---|
| **Phase 0: Nền móng & Hạ tầng** | | | | |
| `TASK-ADM-00` | Thiết lập Nền tảng Đa tầng, Jackson snake_case & Global Exception Handler | N/A | **P0** (Bắt buộc) | [`TASK-ADM-00-PROJECT-FOUNDATION.md`](phase-0-foundation/TASK-ADM-00-PROJECT-FOUNDATION.md) |
| `TASK-ADM-01` | Khởi tạo Schema PostgreSQL 12 Bảng, Ràng buộc DDL & Dữ liệu Mẫu | N/A | **P0** (Bắt buộc) | [`TASK-ADM-01-SCHEMA-MIGRATION.md`](phase-0-foundation/TASK-ADM-01-SCHEMA-MIGRATION.md) |
| `TASK-ADM-02` | Thiết lập Spring Security 6 & Bộ Cấp phát Token Kép (Access/Refresh) | N/A | **P0** (Bắt buộc) | [`TASK-ADM-02-SECURITY-JWT.md`](phase-0-foundation/TASK-ADM-02-SECURITY-JWT.md) |
| `TASK-ADM-03` | Cấu hình HTTP Clients Tích hợp Liên Service (Finance & Student) | N/A | **P1** | [`TASK-ADM-03-INTERSERVICE-CLIENTS.md`](phase-0-foundation/TASK-ADM-03-INTERSERVICE-CLIENTS.md) |
| **Phase 1: Quản trị Định danh & Phiên (IAM)** | | | | |
| `TASK-ADM-10` | Tự động Sinh Tài khoản Học viên khi Test hoặc Đăng ký Online | FR-IAM-01 | **P1** | [`TASK-ADM-10-IAM-AUTO-STUDENT.md`](phase-1-iam/TASK-ADM-10-IAM-AUTO-STUDENT.md) |
| `TASK-ADM-11` | Quản lý Tài khoản Nhân sự (Staff/Teacher) & Khóa/Mở khóa Tài khoản | FR-IAM-02, 05 | **P1** | [`TASK-ADM-11-IAM-USER-MANAGEMENT.md`](phase-1-iam/TASK-ADM-11-IAM-USER-MANAGEMENT.md) |
| `TASK-ADM-12` | API Đăng nhập, Cấp JWT Kép & Ghi Nhận Nhật ký Kiểm toán Bảo mật | FR-IAM-03, 07 | **P0** | [`TASK-ADM-12-IAM-AUTH-LOGIN.md`](phase-1-iam/TASK-ADM-12-IAM-AUTH-LOGIN.md) |
| `TASK-ADM-13` | Cơ chế Refresh Token Rotation & Thu hồi Token Đang hoạt động | FR-IAM-04 | **P0** | [`TASK-ADM-13-IAM-TOKEN-ROTATION.md`](phase-1-iam/TASK-ADM-13-IAM-TOKEN-ROTATION.md) |
| `TASK-ADM-14` | Quy trình Quên mật khẩu & Đặt lại Mật khẩu qua Token Email 15 phút | FR-IAM-06 | **P1** | [`TASK-ADM-14-IAM-PASSWORD-RESET.md`](phase-1-iam/TASK-ADM-14-IAM-PASSWORD-RESET.md) |
| `TASK-ADM-15` | Hệ thống Truy vấn Nhật ký Kiểm toán & Cảnh báo An toàn Tài khoản | FR-IAM-07, BI-SEC-01 | **P1** | [`TASK-ADM-15-IAM-AUDIT-LOGS.md`](phase-1-iam/TASK-ADM-15-IAM-AUDIT-LOGS.md) |
| **Phase 2: Cơ sở Vật chất & Đào tạo (FAC/ACA)** | | | | |
| `TASK-ADM-20` | Quản lý Danh mục Phòng học, Ca học & Mẫu Ngày học | FR-FAC-01, 02 | **P1** | [`TASK-ADM-20-FAC-ROOM-MANAGEMENT.md`](phase-2-academic-facility/TASK-ADM-20-FAC-ROOM-MANAGEMENT.md) |
| `TASK-ADM-21` | Quản lý Khóa học, Học phí Chuẩn & Khóa học Tiên quyết | FR-ACA-01, INV-ADM-02 | **P0** | [`TASK-ADM-21-ACA-COURSE-MANAGEMENT.md`](phase-2-academic-facility/TASK-ADM-21-ACA-COURSE-MANAGEMENT.md) |
| `TASK-ADM-22` | Quản lý Mở Lớp học, Kiểm tra Sức chứa Phòng & Vòng đời Lớp | FR-ACA-02, 04, FR-FAC-03 | **P0** | [`TASK-ADM-22-ACA-CLASS-MANAGEMENT.md`](phase-2-academic-facility/TASK-ADM-22-ACA-CLASS-MANAGEMENT.md) |
| `TASK-ADM-23` | Động cơ Chống Xung đột Lịch Phòng & Giảng viên (Conflict Engine) | FR-ACA-03 | **P0** | [`TASK-ADM-23-ACA-CONFLICT-ENGINE.md`](phase-2-academic-facility/TASK-ADM-23-ACA-CONFLICT-ENGINE.md) |
| `TASK-ADM-24` | API Tính toán Slot Khả dụng Theo Thời gian Thực | FR-ACA-05 | **P0** | [`TASK-ADM-24-ACA-AVAILABLE-SLOTS.md`](phase-2-academic-facility/TASK-ADM-24-ACA-AVAILABLE-SLOTS.md) |
| **Phase 3: Khảo thí Đầu vào Chuyên sâu (TST)** | | | | |
| `TASK-ADM-30` | Quản lý Ngân hàng Bộ Đề & Câu hỏi 3 Kỹ năng (Listening, Reading, Grammar) | FR-TST-01, 02 | **P1** | [`TASK-ADM-30-TST-TESTSET-MANAGEMENT.md`](phase-3-testing/TASK-ADM-30-TST-TESTSET-MANAGEMENT.md) |
| `TASK-ADM-31` | Động cơ Khảo thí Trực tuyến Countdown, Tự động Chấm & Bóc tách Kỹ năng | FR-TST-03, 04 | **P0** | [`TASK-ADM-31-TST-EXAM-ENGINE.md`](phase-3-testing/TASK-ADM-31-TST-EXAM-ENGINE.md) |
| `TASK-ADM-32` | Động cơ Đề xuất Khóa học Tự động Theo Điểm Khảo thí | FR-TST-05 | **P1** | [`TASK-ADM-32-TST-RECOMMENDATION.md`](phase-3-testing/TASK-ADM-32-TST-RECOMMENDATION.md) |
| **Phase 4: Tuyển sinh, Giữ chỗ 48h & Xét duyệt (ENR)** | | | | |
| `TASK-ADM-40` | Đăng ký Tuyển sinh Đa kênh (Online & Trực tiếp tại Quầy) | FR-ENR-01 | **P0** | [`TASK-ADM-40-ENR-MULTI-CHANNEL.md`](phase-4-enrollment/TASK-ADM-40-ENR-MULTI-CHANNEL.md) |
| `TASK-ADM-41` | Bảo vệ Sĩ số Trần Tuyệt đối khi Duyệt Đơn (Invariant Guard INV-ADM-01) | FR-ENR-02, INV-ADM-01 | **P0** (Bắt buộc) | [`TASK-ADM-41-ENR-CAPACITY-GUARD.md`](phase-4-enrollment/TASK-ADM-41-ENR-CAPACITY-GUARD.md) |
| `TASK-ADM-42` | Cơ chế Cấp Slot Giữ chỗ 48h Cho Đơn Đăng ký PENDING | FR-ENR-03 | **P0** | [`TASK-ADM-42-ENR-48H-SLOT-HOLDING.md`](phase-4-enrollment/TASK-ADM-42-ENR-48H-SLOT-HOLDING.md) |
| `TASK-ADM-43` | Scheduled Background Job Tự động Thu hồi Slot Quá hạn (EXPIRED) | FR-ENR-04 | **P0** | [`TASK-ADM-43-ENR-EXPIRE-JOB.md`](phase-4-enrollment/TASK-ADM-43-ENR-EXPIRE-JOB.md) |
| `TASK-ADM-44` | Tính năng Gia hạn Giữ chỗ Học vụ Kèm Lý do Nghiệp vụ | FR-ENR-05 | **P1** | [`TASK-ADM-44-ENR-EXTEND-HOLD.md`](phase-4-enrollment/TASK-ADM-44-ENR-EXTEND-HOLD.md) |
| `TASK-ADM-45` | Webhook Tiếp nhận Hóa đơn PAID từ Finance Service & Tự động Duyệt | FR-ENR-06 | **P0** | [`TASK-ADM-45-ENR-AUTO-APPROVE-FINANCE.md`](phase-4-enrollment/TASK-ADM-45-ENR-AUTO-APPROVE-FINANCE.md) |
| `TASK-ADM-46` | Quy trình Duyệt Đơn Nộp Tiền mặt Tại Quầy Dành cho Học vụ | FR-ENR-07 | **P1** | [`TASK-ADM-46-ENR-MANUAL-APPROVE.md`](phase-4-enrollment/TASK-ADM-46-ENR-MANUAL-APPROVE.md) |
| `TASK-ADM-47` | Tự động Đồng bộ Hồ sơ Học viên sang Student Service khi Duyệt Thành công | FR-ENR-08 | **P0** | [`TASK-ADM-47-ENR-STUDENT-SYNC.md`](phase-4-enrollment/TASK-ADM-47-ENR-STUDENT-SYNC.md) |
| **Phase 5: Xuất Dữ liệu & Phân tích BI (OPS/BI)** | | | | |
| `TASK-ADM-50` | Xuất Danh sách Học viên Lớp học & Điểm Khảo thí ra File Excel/CSV | FR-OPS-01, 02 | **P1** | [`TASK-ADM-50-OPS-EXPORT.md`](phase-5-operations-bi/TASK-ADM-50-OPS-EXPORT.md) |
| `TASK-ADM-51` | API Phân tích Phễu Chuyển đổi Tuyển sinh 4 Giai đoạn (BI-01) | BI-01, BI-FUN-01..04 | **P1** | [`TASK-ADM-51-BI-FUNNEL-ANALYTICS.md`](phase-5-operations-bi/TASK-ADM-51-BI-FUNNEL-ANALYTICS.md) |
| `TASK-ADM-52` | API Báo cáo Xếp hạng Khóa học, Doanh thu Tiềm năng & Lấp đầy (BI-02) | BI-02, BI-REV-01..02 | **P1** | [`TASK-ADM-52-BI-REVENUE-OCCUPANCY.md`](phase-5-operations-bi/TASK-ADM-52-BI-REVENUE-OCCUPANCY.md) |
| `TASK-ADM-53` | API Giám sát DAU/MAU & Phát hiện Bất thường Tấn công Đăng nhập (BI-03) | BI-03, BI-USR-01, SEC-01 | **P1** | [`TASK-ADM-53-BI-SECURITY-ENGAGEMENT.md`](phase-5-operations-bi/TASK-ADM-53-BI-SECURITY-ENGAGEMENT.md) |
| **Phase 6: Giao diện Người dùng Frontend (UI)** | | | | |
| `TASK-ADM-60` | Giao diện Quản lý Khóa học & Lớp học (`courses.html`, `classes.html`) | FR-ACA-01..04 | **P1** | [`TASK-ADM-60-UI-COURSE-CLASS.md`](phase-6-frontend/TASK-ADM-60-UI-COURSE-CLASS.md) |
| `TASK-ADM-61` | Giao diện Bàn Tuyển sinh, Giữ chỗ 48h & Xét duyệt (`enrollments.html`) | FR-ENR-01..07 | **P0** | [`TASK-ADM-61-UI-ENROLLMENT-DESK.md`](phase-6-frontend/TASK-ADM-61-UI-ENROLLMENT-DESK.md) |
| `TASK-ADM-62` | Giao diện Làm bài Khảo thí Trực tuyến Đếm ngược & Tra cứu (`test.html`) | FR-TST-01..05 | **P1** | [`TASK-ADM-62-UI-ONLINE-TEST.md`](phase-6-frontend/TASK-ADM-62-UI-ONLINE-TEST.md) |
| `TASK-ADM-63` | Giao diện Quản lý Phòng học & Lịch phân ca (`rooms.html`) | FR-FAC-01..03 | **P2** | [`TASK-ADM-63-UI-ROOM-SCHEDULE.md`](phase-6-frontend/TASK-ADM-63-UI-ROOM-SCHEDULE.md) |
| `TASK-ADM-64` | Dashboard Trực quan hóa Báo cáo BI Tuyển sinh (`bi-dashboard.html`) | BI-01..03 | **P2** | [`TASK-ADM-64-UI-BI-DASHBOARD.md`](phase-6-frontend/TASK-ADM-64-UI-BI-DASHBOARD.md) |

---

## 3. Quy chuẩn Nghiệm thu & Testing Quality Gate

Mỗi khi hoàn thành một task, lập trình viên / AI Agent bắt buộc thực hiện kiểm tra:
1. **Kiểm tra biên dịch & Khởi động**:
   ```bash
   mvn clean test-compile -f services/admission/backend/pom.xml
   ```
2. **Kiểm tra tính toàn vẹn Invariant Suite**:
   ```bash
   python3 -m unittest discover -s tests/invariants -p "test_*.py" -v
   ```
   Tất cả 15 bài kiểm thử phải đạt kết quả `OK`. Tuyệt đối không được phép sửa đổi assertions của test invariant.
3. **Quy chuẩn Code**:
   - Sử dụng chú thích tiếng Việt chi tiết cho mọi phương thức và lớp.
   - Không chứa hardcoded credentials hoặc chuỗi nối SQL thủ công.
   - Định dạng dữ liệu trao đổi JSON đồng nhất `snake_case`.

# Bảng Theo Dõi Tiến Độ Toàn Bộ Tasks (Admission Module Checklist)

> **Hướng dẫn sử dụng**:
> - Đánh dấu `[x]` khi hoàn thành một task và kiểm tra test invariant tương ứng đạt `OK`.
> - Ghi rõ **Người thực hiện (Assignee)** và **Ngày hoàn thành** để báo cáo tiến độ Sprint.
> - Luôn chạy bộ kiểm thử chất lượng trước khi tick:
>   ```bash
>   python3 -m unittest discover -s tests/invariants -p "test_*.py" -v
>   ```

---

## 1. Bảng Tổng Hợp Trạng Thái Phân Kỳ

| Phân kỳ | Số lượng Task | Hoàn thành | Tỷ lệ (%) | Trạng thái |
|---|:---:|:---:|:---:|:---:|
| **Phase 0: Nền móng & Hạ tầng (INF)** | 4 | 0 | 0% | 🟡 Chưa bắt đầu |
| **Phase 1: Quản trị Định danh & Phiên (IAM)** | 6 | 0 | 0% | 🟡 Chưa bắt đầu |
| **Phase 2: Cơ sở Vật chất & Đào tạo (FAC/ACA)** | 5 | 0 | 0% | 🟡 Chưa bắt đầu |
| **Phase 3: Khảo thí Đầu vào Chuyên sâu (TST)** | 3 | 0 | 0% | 🟡 Chưa bắt đầu |
| **Phase 4: Tuyển sinh, Giữ chỗ 48h & Xét duyệt (ENR)** | 8 | 0 | 0% | 🟡 Chưa bắt đầu |
| **Phase 5: Xuất Dữ liệu & Phân tích BI (OPS/BI)** | 4 | 0 | 0% | 🟡 Chưa bắt đầu |
| **Phase 6: Giao diện Người dùng Frontend (UI)** | 5 | 0 | 0% | 🟡 Chưa bắt đầu |
| **TỔNG CỘNG** | **35 Tasks** | **0** | **0%** | **Sẵn sàng triển khai** |

---

## 2. Chi Tiết Checklist Từng Nhiệm Vụ

### Phase 0: Nền móng & Hạ tầng Kỹ thuật Cốt lõi (INF)
- [ ] **`TASK-ADM-00`**: Thiết lập Nền tảng Đa tầng, Jackson snake_case & Global Exception Handler
  - *File chi tiết*: [`phase-0-foundation/TASK-ADM-00-PROJECT-FOUNDATION.md`](phase-0-foundation/TASK-ADM-00-PROJECT-FOUNDATION.md)
  - *Invariant*: `INV-SYS-01`
  - *Assignee*: `_______________` | *Ngày xong*: `____/__/__`
- [ ] **`TASK-ADM-01`**: Khởi tạo Schema PostgreSQL 12 Bảng, Ràng buộc DDL & Dữ liệu Mẫu
  - *File chi tiết*: [`phase-0-foundation/TASK-ADM-01-SCHEMA-MIGRATION.md`](phase-0-foundation/TASK-ADM-01-SCHEMA-MIGRATION.md)
  - *Invariant*: `INV-SYS-02`
  - *Assignee*: `_______________` | *Ngày xong*: `____/__/__`
- [ ] **`TASK-ADM-02`**: Thiết lập Spring Security 6 & Bộ Cấp phát Token Kép (Access 15m / Refresh 7d)
  - *File chi tiết*: [`phase-0-foundation/TASK-ADM-02-SECURITY-JWT.md`](phase-0-foundation/TASK-ADM-02-SECURITY-JWT.md)
  - *Invariant*: `INV-SEC-01`, `INV-SEC-03`
  - *Assignee*: `_______________` | *Ngày xong*: `____/__/__`
- [ ] **`TASK-ADM-03`**: Cấu hình HTTP Clients Tích hợp Liên Service (Finance & Student)
  - *File chi tiết*: [`phase-0-foundation/TASK-ADM-03-INTERSERVICE-CLIENTS.md`](phase-0-foundation/TASK-ADM-03-INTERSERVICE-CLIENTS.md)
  - *Invariant*: `INV-SYS-02` (Không cross-schema query, gọi REST trực tiếp)
  - *Assignee*: `_______________` | *Ngày xong*: `____/__/__`

---

### Phase 1: Quản trị Định danh & Phiên làm việc (IAM)
- [ ] **`TASK-ADM-10`**: Tự động Sinh Tài khoản Học viên khi Test hoặc Đăng ký Online (`FR-IAM-01`)
  - *File chi tiết*: [`phase-1-iam/TASK-ADM-10-IAM-AUTO-STUDENT.md`](phase-1-iam/TASK-ADM-10-IAM-AUTO-STUDENT.md)
  - *Assignee*: `_______________` | *Ngày xong*: `____/__/__`
- [ ] **`TASK-ADM-11`**: Quản lý Tài khoản Nhân sự (Staff/Teacher) & Khóa/Mở khóa Tài khoản (`FR-IAM-02`, `FR-IAM-05`)
  - *File chi tiết*: [`phase-1-iam/TASK-ADM-11-IAM-USER-MANAGEMENT.md`](phase-1-iam/TASK-ADM-11-IAM-USER-MANAGEMENT.md)
  - *Assignee*: `_______________` | *Ngày xong*: `____/__/__`
- [ ] **`TASK-ADM-12`**: API Đăng nhập, Cấp JWT Kép & Ghi Nhận Nhật ký Kiểm toán Bảo mật (`FR-IAM-03`, `FR-IAM-07`)
  - *File chi tiết*: [`phase-1-iam/TASK-ADM-12-IAM-AUTH-LOGIN.md`](phase-1-iam/TASK-ADM-12-IAM-AUTH-LOGIN.md)
  - *Assignee*: `_______________` | *Ngày xong*: `____/__/__`
- [ ] **`TASK-ADM-13`**: Cơ chế Refresh Token Rotation & Thu hồi Token Đang hoạt động (`FR-IAM-04`)
  - *File chi tiết*: [`phase-1-iam/TASK-ADM-13-IAM-TOKEN-ROTATION.md`](phase-1-iam/TASK-ADM-13-IAM-TOKEN-ROTATION.md)
  - *Assignee*: `_______________` | *Ngày xong*: `____/__/__`
- [ ] **`TASK-ADM-14`**: Quy trình Quên mật khẩu & Đặt lại Mật khẩu qua Token Email 15 phút (`FR-IAM-06`)
  - *File chi tiết*: [`phase-1-iam/TASK-ADM-14-IAM-PASSWORD-RESET.md`](phase-1-iam/TASK-ADM-14-IAM-PASSWORD-RESET.md)
  - *Assignee*: `_______________` | *Ngày xong*: `____/__/__`
- [ ] **`TASK-ADM-15`**: Hệ thống Truy vấn Nhật ký Kiểm toán & Cảnh báo An toàn Tài khoản (`FR-IAM-07`, `BI-SEC-01`)
  - *File chi tiết*: [`phase-1-iam/TASK-ADM-15-IAM-AUDIT-LOGS.md`](phase-1-iam/TASK-ADM-15-IAM-AUDIT-LOGS.md)
  - *Assignee*: `_______________` | *Ngày xong*: `____/__/__`

---

### Phase 2: Cơ sở Vật chất & Quản lý Đào tạo (FAC/ACA)
- [ ] **`TASK-ADM-20`**: Quản lý Danh mục Phòng học, Ca học & Mẫu Ngày học (`FR-FAC-01`, `FR-FAC-02`)
  - *File chi tiết*: [`phase-2-academic-facility/TASK-ADM-20-FAC-ROOM-MANAGEMENT.md`](phase-2-academic-facility/TASK-ADM-20-FAC-ROOM-MANAGEMENT.md)
  - *Assignee*: `_______________` | *Ngày xong*: `____/__/__`
- [ ] **`TASK-ADM-21`**: Quản lý Khóa học, Học phí Chuẩn & Khóa học Tiên quyết (`FR-ACA-01`)
  - *File chi tiết*: [`phase-2-academic-facility/TASK-ADM-21-ACA-COURSE-MANAGEMENT.md`](phase-2-academic-facility/TASK-ADM-21-ACA-COURSE-MANAGEMENT.md)
  - *Invariant*: `INV-ADM-02` (Mã khóa học duy nhất)
  - *Assignee*: `_______________` | *Ngày xong*: `____/__/__`
- [ ] **`TASK-ADM-22`**: Quản lý Mở Lớp học, Kiểm tra Sức chứa Phòng & Vòng đời Lớp (`FR-ACA-02`, `FR-ACA-04`, `FR-FAC-03`)
  - *File chi tiết*: [`phase-2-academic-facility/TASK-ADM-22-ACA-CLASS-MANAGEMENT.md`](phase-2-academic-facility/TASK-ADM-22-ACA-CLASS-MANAGEMENT.md)
  - *Assignee*: `_______________` | *Ngày xong*: `____/__/__`
- [ ] **`TASK-ADM-23`**: Động cơ Chống Xung đột Lịch Phòng & Giảng viên (Conflict Engine) (`FR-ACA-03`)
  - *File chi tiết*: [`phase-2-academic-facility/TASK-ADM-23-ACA-CONFLICT-ENGINE.md`](phase-2-academic-facility/TASK-ADM-23-ACA-CONFLICT-ENGINE.md)
  - *Assignee*: `_______________` | *Ngày xong*: `____/__/__`
- [ ] **`TASK-ADM-24`**: API Tính toán Slot Khả dụng Theo Thời gian Thực (`FR-ACA-05`)
  - *File chi tiết*: [`phase-2-academic-facility/TASK-ADM-24-ACA-AVAILABLE-SLOTS.md`](phase-2-academic-facility/TASK-ADM-24-ACA-AVAILABLE-SLOTS.md)
  - *Assignee*: `_______________` | *Ngày xong*: `____/__/__`

---

### Phase 3: Khảo thí Đầu vào Chuyên sâu (TST)
- [ ] **`TASK-ADM-30`**: Quản lý Ngân hàng Bộ Đề & Câu hỏi 3 Kỹ năng (Listening, Reading, Grammar) (`FR-TST-01`, `FR-TST-02`)
  - *File chi tiết*: [`phase-3-testing/TASK-ADM-30-TST-TESTSET-MANAGEMENT.md`](phase-3-testing/TASK-ADM-30-TST-TESTSET-MANAGEMENT.md)
  - *Assignee*: `_______________` | *Ngày xong*: `____/__/__`
- [ ] **`TASK-ADM-31`**: Động cơ Khảo thí Trực tuyến Countdown, Tự động Chấm & Bóc tách Kỹ năng (`FR-TST-03`, `FR-TST-04`)
  - *File chi tiết*: [`phase-3-testing/TASK-ADM-31-TST-EXAM-ENGINE.md`](phase-3-testing/TASK-ADM-31-TST-EXAM-ENGINE.md)
  - *Assignee*: `_______________` | *Ngày xong*: `____/__/__`
- [ ] **`TASK-ADM-32`**: Động cơ Đề xuất Khóa học Tự động Theo Điểm Khảo thí (`FR-TST-05`)
  - *File chi tiết*: [`phase-3-testing/TASK-ADM-32-TST-RECOMMENDATION.md`](phase-3-testing/TASK-ADM-32-TST-RECOMMENDATION.md)
  - *Assignee*: `_______________` | *Ngày xong*: `____/__/__`

---

### Phase 4: Tuyển sinh, Giữ chỗ 48h & Xét duyệt (ENR)
- [ ] **`TASK-ADM-40`**: Đăng ký Tuyển sinh Đa kênh (Online & Trực tiếp tại Quầy) (`FR-ENR-01`)
  - *File chi tiết*: [`phase-4-enrollment/TASK-ADM-40-ENR-MULTI-CHANNEL.md`](phase-4-enrollment/TASK-ADM-40-ENR-MULTI-CHANNEL.md)
  - *Assignee*: `_______________` | *Ngày xong*: `____/__/__`
- [ ] **`TASK-ADM-41`**: Bảo vệ Sĩ số Trần Tuyệt đối khi Duyệt Đơn (Invariant Guard INV-ADM-01) (`FR-ENR-02`)
  - *File chi tiết*: [`phase-4-enrollment/TASK-ADM-41-ENR-CAPACITY-GUARD.md`](phase-4-enrollment/TASK-ADM-41-ENR-CAPACITY-GUARD.md)
  - *Invariant*: `INV-ADM-01` (Không vượt sĩ số trần)
  - *Assignee*: `_______________` | *Ngày xong*: `____/__/__`
- [ ] **`TASK-ADM-42`**: Cơ chế Cấp Slot Giữ chỗ 48h Cho Đơn Đăng ký PENDING (`FR-ENR-03`)
  - *File chi tiết*: [`phase-4-enrollment/TASK-ADM-42-ENR-48H-SLOT-HOLDING.md`](phase-4-enrollment/TASK-ADM-42-ENR-48H-SLOT-HOLDING.md)
  - *Assignee*: `_______________` | *Ngày xong*: `____/__/__`
- [ ] **`TASK-ADM-43`**: Scheduled Background Job Tự động Thu hồi Slot Quá hạn (EXPIRED) (`FR-ENR-04`)
  - *File chi tiết*: [`phase-4-enrollment/TASK-ADM-43-ENR-EXPIRE-JOB.md`](phase-4-enrollment/TASK-ADM-43-ENR-EXPIRE-JOB.md)
  - *Assignee*: `_______________` | *Ngày xong*: `____/__/__`
- [ ] **`TASK-ADM-44`**: Tính năng Gia hạn Giữ chỗ Học vụ Kèm Lý do Nghiệp vụ (`FR-ENR-05`)
  - *File chi tiết*: [`phase-4-enrollment/TASK-ADM-44-ENR-EXTEND-HOLD.md`](phase-4-enrollment/TASK-ADM-44-ENR-EXTEND-HOLD.md)
  - *Assignee*: `_______________` | *Ngày xong*: `____/__/__`
- [ ] **`TASK-ADM-45`**: Webhook Tiếp nhận Hóa đơn PAID từ Finance Service & Tự động Duyệt (`FR-ENR-06`)
  - *File chi tiết*: [`phase-4-enrollment/TASK-ADM-45-ENR-AUTO-APPROVE-FINANCE.md`](phase-4-enrollment/TASK-ADM-45-ENR-AUTO-APPROVE-FINANCE.md)
  - *Invariant*: `INV-ADM-01`
  - *Assignee*: `_______________` | *Ngày xong*: `____/__/__`
- [ ] **`TASK-ADM-46`**: Quy trình Duyệt Đơn Nộp Tiền mặt Tại Quầy Dành cho Học vụ (`FR-ENR-07`)
  - *File chi tiết*: [`phase-4-enrollment/TASK-ADM-46-ENR-MANUAL-APPROVE.md`](phase-4-enrollment/TASK-ADM-46-ENR-MANUAL-APPROVE.md)
  - *Invariant*: `INV-ADM-01`, `INV-ADM-03` (State machine)
  - *Assignee*: `_______________` | *Ngày xong*: `____/__/__`
- [ ] **`TASK-ADM-47`**: Tự động Đồng bộ Hồ sơ Học viên sang Student Service khi Duyệt Thành công (`FR-ENR-08`)
  - *File chi tiết*: [`phase-4-enrollment/TASK-ADM-47-ENR-STUDENT-SYNC.md`](phase-4-enrollment/TASK-ADM-47-ENR-STUDENT-SYNC.md)
  - *Assignee*: `_______________` | *Ngày xong*: `____/__/__`

---

### Phase 5: Xuất Dữ liệu & Báo cáo Thông minh BI (OPS/BI)
- [ ] **`TASK-ADM-50`**: Xuất Danh sách Học viên Lớp học & Điểm Khảo thí ra File Excel/CSV (`FR-OPS-01`, `FR-OPS-02`)
  - *File chi tiết*: [`phase-5-operations-bi/TASK-ADM-50-OPS-EXPORT.md`](phase-5-operations-bi/TASK-ADM-50-OPS-EXPORT.md)
  - *Assignee*: `_______________` | *Ngày xong*: `____/__/__`
- [ ] **`TASK-ADM-51`**: API Phân tích Phễu Chuyển đổi Tuyển sinh 4 Giai đoạn (`BI-01`, `BI-FUN-01..04`)
  - *File chi tiết*: [`phase-5-operations-bi/TASK-ADM-51-BI-FUNNEL-ANALYTICS.md`](phase-5-operations-bi/TASK-ADM-51-BI-FUNNEL-ANALYTICS.md)
  - *Assignee*: `_______________` | *Ngày xong*: `____/__/__`
- [ ] **`TASK-ADM-52`**: API Báo cáo Xếp hạng Khóa học, Doanh thu Tiềm năng & Lấp đầy (`BI-02`, `BI-REV-01..02`)
  - *File chi tiết*: [`phase-5-operations-bi/TASK-ADM-52-BI-REVENUE-OCCUPANCY.md`](phase-5-operations-bi/TASK-ADM-52-BI-REVENUE-OCCUPANCY.md)
  - *Assignee*: `_______________` | *Ngày xong*: `____/__/__`
- [ ] **`TASK-ADM-53`**: API Giám sát DAU/MAU & Phát hiện Bất thường Tấn công Đăng nhập (`BI-03`, `BI-USR-01`, `SEC-01`)
  - *File chi tiết*: [`phase-5-operations-bi/TASK-ADM-53-BI-SECURITY-ENGAGEMENT.md`](phase-5-operations-bi/TASK-ADM-53-BI-SECURITY-ENGAGEMENT.md)
  - *Assignee*: `_______________` | *Ngày xong*: `____/__/__`

---

### Phase 6: Giao diện Người dùng Frontend (UI)
- [ ] **`TASK-ADM-60`**: Giao diện Quản lý Khóa học & Lớp học (`courses.html`, `classes.html`)
  - *File chi tiết*: [`phase-6-frontend/TASK-ADM-60-UI-COURSE-CLASS.md`](phase-6-frontend/TASK-ADM-60-UI-COURSE-CLASS.md)
  - *Assignee*: `_______________` | *Ngày xong*: `____/__/__`
- [ ] **`TASK-ADM-61`**: Giao diện Bàn Tuyển sinh, Giữ chỗ 48h & Xét duyệt (`enrollments.html`)
  - *File chi tiết*: [`phase-6-frontend/TASK-ADM-61-UI-ENROLLMENT-DESK.md`](phase-6-frontend/TASK-ADM-61-UI-ENROLLMENT-DESK.md)
  - *Assignee*: `_______________` | *Ngày xong*: `____/__/__`
- [ ] **`TASK-ADM-62`**: Giao diện Làm bài Khảo thí Trực tuyến Đếm ngược & Tra cứu (`test.html`)
  - *File chi tiết*: [`phase-6-frontend/TASK-ADM-62-UI-ONLINE-TEST.md`](phase-6-frontend/TASK-ADM-62-UI-ONLINE-TEST.md)
  - *Assignee*: `_______________` | *Ngày xong*: `____/__/__`
- [ ] **`TASK-ADM-63`**: Giao diện Quản lý Phòng học & Lịch phân ca (`rooms.html`)
  - *File chi tiết*: [`phase-6-frontend/TASK-ADM-63-UI-ROOM-SCHEDULE.md`](phase-6-frontend/TASK-ADM-63-UI-ROOM-SCHEDULE.md)
  - *Assignee*: `_______________` | *Ngày xong*: `____/__/__`
- [ ] **`TASK-ADM-64`**: Dashboard Trực quan hóa Báo cáo BI Tuyển sinh (`bi-dashboard.html`)
  - *File chi tiết*: [`phase-6-frontend/TASK-ADM-64-UI-BI-DASHBOARD.md`](phase-6-frontend/TASK-ADM-64-UI-BI-DASHBOARD.md)
  - *Assignee*: `_______________` | *Ngày xong*: `____/__/__`

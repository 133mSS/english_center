# Nhật Ký Hoạt Động & Phối Hợp Làm Việc (Admission Module Worklog)

> **Mục đích của file này**:  
> Đây là nơi **toàn bộ thành viên trong nhóm** (Developer, Tech Lead, AI Agent, Tester) bắt buộc ghi nhận lịch sử công việc để tránh xung đột mã nguồn (merge conflict), nắm bắt ai đang làm gì, sửa file nào, thêm mới/xóa bỏ thành phần nào và kết quả kiểm thử tương ứng.

---

## 1. Bảng Trạng Thái Công Việc Đang Diễn Ra (Active Work In-Progress)

*Bảng này dùng để đăng ký task trước khi code, giúp các thành viên không làm trùng hoặc đè code lên nhau.*

| Task ID | Thành viên phụ trách | Nhánh Git (Branch) | Thời điểm bắt đầu | Trạng thái | Ghi chú & Phạm vi can thiệp |
|---|---|---|---|---|---|
| *Ví dụ: TASK-ADM-00* | *Nguyễn Văn A* | *feature/adm-foundation* | *2026-11-02 08:30* | 🟡 `IN_PROGRESS` | *Đang tạo ApiResponse.java & GlobalExceptionHandler.java* |
| *(Trống)* | | | | | *(Chưa có ai nhận task tiếp theo)* |

> **Quy tắc phối hợp nhóm**:
> 1. **Trước khi bắt đầu code**: Thêm một dòng vào bảng trên với trạng thái `IN_PROGRESS`.
> 2. **Trong khi code**: Chỉ sửa đổi các file trong phạm vi cho phép được quy định tại file mô tả task tương ứng.
> 3. **Sau khi code xong**: Chạy `python3 -m unittest discover -s tests/invariants -p "test_*.py" -v`, sau đó chuyển task sang bảng Lịch sử Hoàn thành bên dưới và tick vào [`CHECKLIST.md`](CHECKLIST.md).

---

## 2. Quy Chuẩn Ghi Chép Nhật Ký (Log Entry Template)

Mỗi khi hoàn thành hoặc bàn giao một phần việc, thành viên bổ sung một bản ghi vào **Mục 3 (Lịch sử Chi tiết)** theo mẫu chuẩn sau:

```markdown
### [YYYY-MM-DD HH:mm] - [TÊN_THÀNH_VIÊN] - [MÃ_TASK]
- **Nhánh Git (Branch)**: `feature/ten-nhanh`
- **Mục tiêu công việc**: Tóm tắt 1 câu việc vừa làm.
- **Chi tiết thay đổi**:
  - 🟢 **Thêm mới (Added)**: Danh sách file tạo mới.
  - 🟡 **Cập nhật / Nâng cấp (Updated)**: Danh sách file đã sửa & lý do sửa.
  - 🔴 **Xóa bỏ (Deleted)**: Danh sách file/hàm đã xóa (nếu có).
- **Trạng thái Quality Gate**:
  - Invariant Tests: `15/15 Tests OK`
  - Compile / Build: `Build Success` (hoặc N/A nếu là docs/frontend)
- **Ghi chú bàn giao**: Lưu ý cho người tiếp theo hoặc các phân hệ khác (Student, Finance).
```

---

## 3. Lịch Sử Chi Tiết Các Phiên Làm Việc (Historical Log Entries)

### [2026-11-01 21:45] - Team Lead & AI Assistant - TASK-ADM-PLANNING
- **Nhánh Git (Branch)**: `feature/admission`
- **Mục tiêu công việc**: Hoàn tất tài liệu kiến trúc Ver 1 (v3.5), thiết lập 32 task chi tiết, checklist tiến độ và danh mục 55 API Endpoints của phân hệ Admission.
- **Chi tiết thay đổi**:
  - 🟢 **Thêm mới (Added)**:
    - `services/admission/tasks/README.md`: Kế hoạch WBS 7 phân kỳ và kiến trúc triển khai.
    - `services/admission/tasks/CHECKLIST.md`: Bảng theo dõi tiến độ sprint với checkbox từng task.
    - `services/admission/tasks/API_CATALOG.md`: Danh mục chuẩn 55 API Endpoints với HTTP method, quyền RBAC và payload.
    - `services/admission/tasks/WORKLOG.md`: File nhật ký phối hợp làm việc nhóm.
    - `services/admission/tasks/phase-0-foundation/`: 4 tasks nền móng hạ tầng (TASK-ADM-00 đến TASK-ADM-03).
    - `services/admission/tasks/phase-1-iam/`: 6 tasks định danh & phiên JWT (TASK-ADM-10 đến TASK-ADM-15).
    - `services/admission/tasks/phase-2-academic-facility/`: 5 tasks phòng học & lớp học (TASK-ADM-20 đến TASK-ADM-24).
    - `services/admission/tasks/phase-3-testing/`: 3 tasks khảo thí & đề xuất khóa học (TASK-ADM-30 đến TASK-ADM-32).
    - `services/admission/tasks/phase-4-enrollment/`: 8 tasks tuyển sinh & giữ chỗ 48h (TASK-ADM-40 đến TASK-ADM-47).
    - `services/admission/tasks/phase-5-operations-bi/`: 4 tasks xuất dữ liệu & BI (TASK-ADM-50 đến TASK-ADM-53).
    - `services/admission/tasks/phase-6-frontend/`: 5 tasks giao diện người dùng (TASK-ADM-60 đến TASK-ADM-64).
  - 🟡 **Cập nhật / Nâng cấp (Updated)**:
    - Thống nhất nguyên tắc giao tiếp liên service: Gọi **TRỰC TIẾP** qua private network Docker (`http://student-service:8082`, `http://finance-service:8084`), không đi vòng qua Nginx Gateway.
- **Trạng thái Quality Gate**:
  - Invariant Tests: `15/15 OK (Ran in 0.002s)`
- **Ghi chú bàn giao**: Toàn bộ tài liệu kỹ thuật và task backlog đã sẵn sàng để các lập trình viên bắt đầu nhận việc từ Phase 0 (`TASK-ADM-00` và `TASK-ADM-01`).

---

### [2026-10-25 22:45] - Project Initialization - WAVE-0
- **Nhánh Git (Branch)**: `main` / `dev`
- **Mục tiêu công việc**: Khởi tạo kiến trúc Microservices Monorepo, thiết lập Docker Compose 6 container, cấu hình Nginx Gateway và khởi tạo PostgreSQL 16 với 4 schema (`admission`, `student`, `learning`, `finance`).
- **Trạng thái Quality Gate**:
  - Bộ kiểm thử 15 bài Invariant Tests ban đầu: `15/15 OK`.

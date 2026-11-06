# TASK-ADM-50: Xuất Danh sách Học viên Lớp học & Điểm Khảo thí ra File Excel/CSV

- **Mã nhiệm vụ**: `TASK-ADM-50`
- **Phân kỳ**: `Phase 5: Xuất Dữ liệu & Phân tích BI (OPS/BI)`
- **Độ ưu tiên**: `P1`
- **Yêu cầu chức năng liên quan**: `FR-OPS-01`, `FR-OPS-02`
- **Quy tắc bất biến bảo vệ**: `INV-SYS-01`

---

## 1. Mục tiêu Nghiệp vụ & Kỹ thuật
Cung cấp công cụ hỗ trợ công tác vận hành lớp học và báo cáo cho Nhân viên học vụ (`STAFF`) và Giáo viên (`TEACHER`):
1. **Xuất Danh sách Học viên của Lớp (`FR-OPS-01`)**:
   - Cho phép xuất danh sách toàn bộ học viên chính thức (`APPROVED`) và giữ chỗ (`PENDING`) của một lớp học ra file chuẩn:
     - Định dạng CSV (hỗ trợ UTF-8 with BOM để mở trên Excel không bị lỗi font tiếng Việt).
     - Định dạng Excel `.xlsx` (sử dụng Apache POI nếu cần hoặc CSV tiêu chuẩn).
   - Các cột thông tin: STT, Mã đơn đăng ký, Mã học viên, Họ và tên, Email, Số điện thoại, Trạng thái đơn, Ngày đăng ký.
2. **Xuất Bảng Điểm Khảo thí Đầu vào (`FR-OPS-02`)**:
   - Cho phép lọc và xuất kết quả khảo thí theo Bộ đề thi (`test_set_id`) hoặc khoảng thời gian.
   - Các cột thông tin: STT, Mã bài nộp, Họ tên thí sinh, Email, Số điện thoại, Điểm Nghe, Điểm Đọc, Điểm Ngữ pháp, Tổng điểm, Khóa học đề xuất, Thời gian nộp bài.

---

## 2. Phạm vi File Tác động

### File tạo mới hoặc chỉnh sửa:
- `services/admission/backend/src/main/java/com/englishcenter/admission/controller/ExportController.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/service/ExportService.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/service/impl/ExportServiceImpl.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/util/CsvExportHelper.java`

---

## 3. Đặc tả API Hợp đồng

### 3.1. Xuất Danh sách Lớp học
- **URL**: `GET /api/admission/exports/classes/{classId}/roster?format=csv`
- **Header**: `Authorization: Bearer <Staff/Teacher/Admin_Token>`
- **Response**: Trả về `byte[]` với Header:
  - `Content-Type: text/csv; charset=UTF-8`
  - `Content-Disposition: attachment; filename="class_{classId}_roster.csv"`

### 3.2. Xuất Bảng Điểm Khảo thí
- **URL**: `GET /api/admission/exports/tests/{testSetId}/results?format=csv`
- **Header**: `Authorization: Bearer <Staff/Admin_Token>`
- **Response**: File CSV bảng điểm UTF-8.

---

## 4. Kế hoạch Triển khai (Step-by-step)
1. Xây dựng tiện ích `CsvExportHelper.java`:
   - Ghi byte BOM `\uFEFF` ở đầu file để Microsoft Excel tự động nhận diện UTF-8.
   - Xử lý escape dấu phẩy và xuống dòng trong text.
2. Trong `ExportServiceImpl`:
   - `exportClassRoster(Long classId)`: Lấy thông tin lớp và danh sách `Enrollment`, chuyển đổi thành các dòng CSV.
   - `exportTestResults(Long testSetId)`: Lấy danh sách `TestSubmission`, format các cột điểm số và khóa học đề xuất.
3. Trong `ExportController`: Khai báo endpoints trả về `ResponseEntity<byte[]>`.
4. Viết comment tiếng Việt đầy đủ.

---

## 5. Tiêu chí Nghiệm thu (Acceptance Criteria)
- [ ] Tải file CSV về máy, mở bằng Microsoft Excel tiếng Việt không bị vỡ font hay lỗi ký tự đặc biệt.
- [ ] Dữ liệu khớp 100% với các bản ghi trong cơ sở dữ liệu.
- [ ] Giáo viên chỉ có quyền xuất danh sách lớp mà mình phụ trách.

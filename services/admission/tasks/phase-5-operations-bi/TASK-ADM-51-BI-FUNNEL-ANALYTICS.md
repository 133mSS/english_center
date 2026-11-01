# TASK-ADM-51: API Phân tích Phễu Chuyển đổi Tuyển sinh 4 Giai đoạn (BI-01)

- **Mã nhiệm vụ**: `TASK-ADM-51`
- **Phân kỳ**: `Phase 5: Xuất Dữ liệu & Phân tích BI (OPS/BI)`
- **Độ ưu tiên**: `P1`
- **Yêu cầu chức năng liên quan**: `BI-01`, `BI-FUN-01`, `BI-FUN-02`, `BI-FUN-03`, `BI-FUN-04`
- **Quy tắc bất biến bảo vệ**: `INV-SYS-01`

---

## 1. Mục tiêu Nghiệp vụ & Kỹ thuật
Xây dựng API Báo cáo Phễu Chuyển đổi Tuyển sinh (Admissions Conversion Funnel) phục vụ công tác điều hành của Ban Giám đốc và Trưởng phòng Tuyển sinh:
1. **Theo dõi dòng chuyển dịch qua 4 giai đoạn cốt lõi**:
   - **Giai đoạn 1 (Làm Test)**: Số lượng lượt bắt đầu làm bài test đầu vào.
   - **Giai đoạn 2 (Hoàn thành Test)**: Số lượng thí sinh hoàn thành nộp bài (`test_submissions`).
   - **Giai đoạn 3 (Giữ chỗ 48h)**: Số lượng đơn đăng ký phát sinh (`status = PENDING` hoặc đã qua giai đoạn này).
   - **Giai đoạn 4 (Nhập học Chính thức)**: Số lượng đơn đã đóng phí và được duyệt (`status = APPROVED`).
2. **Tính toán 4 Chỉ số KPI Chiến lược**:
   - **BI-FUN-01 (Test Completion Rate)**: $\frac{\text{Số bài nộp}}{\text{Số lượt bắt đầu}} \times 100\%$ (Ngưỡng kỳ vọng $\ge 70\%$).
   - **BI-FUN-02 (Test-to-Enrollment Rate)**: $\frac{\text{Số đơn phát sinh}}{\text{Số bài test nộp}} \times 100\%$ (Ngưỡng kỳ vọng $\ge 40\%$).
   - **BI-FUN-03 (Paid Conversion Rate)**: $\frac{\text{Tổng đơn APPROVED}}{\text{Tổng đơn PENDING phát sinh}} \times 100\%$ (Ngưỡng kỳ vọng $\ge 65\%$).
   - **BI-FUN-04 (Expired Hold Rate)**: $\frac{\text{Tổng đơn EXPIRED}}{\text{Tổng đơn phát sinh}} \times 100\%$ (Ngưỡng an toàn $\le 25\%$).

---

## 2. Phạm vi File Tác động

### File tạo mới hoặc chỉnh sửa:
- `services/admission/backend/src/main/java/com/englishcenter/admission/controller/BiAnalyticsController.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/service/BiAnalyticsService.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/service/impl/BiAnalyticsServiceImpl.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/dto/bi/FunnelReportResponse.java`

---

## 3. Đặc tả API Hợp đồng

### API: `GET /api/admission/bi/funnel`
- **Header**: `Authorization: Bearer <Staff/Admin_Token>`
- **Query Params**:
  - `from_date`: Ngày bắt đầu (ví dụ `2026-10-01`)
  - `to_date`: Ngày kết thúc (ví dụ `2026-10-31`)
  - `course_id`: (Tùy chọn) Lọc theo khóa học
- **Response Thành công (HTTP 200 OK)**:
  ```json
  {
    "success": true,
    "data": {
      "stages": [
        { "stage_id": 1, "name": "Bắt đầu làm Test", "count": 120, "conversion_rate": 100.0 },
        { "stage_id": 2, "name": "Hoàn thành Test", "count": 96, "conversion_rate": 80.0 },
        { "stage_id": 3, "name": "Đăng ký Giữ chỗ 48h", "count": 48, "conversion_rate": 50.0 },
        { "stage_id": 4, "name": "Nhập học Chính thức (PAID)", "count": 36, "conversion_rate": 75.0 }
      ],
      "kpis": {
        "test_completion_rate": 80.0,
        "test_to_enrollment_rate": 50.0,
        "paid_conversion_rate": 75.0,
        "expired_hold_rate": 18.75
      },
      "summary": {
        "is_healthy": true,
        "bottleneck_warning": null
      }
    },
    "message": "Phân tích phễu chuyển đổi tuyển sinh thành công"
  }
  ```

---

## 4. Kế hoạch Triển khai (Step-by-step)
1. Trong `EnrollmentRepository` và `TestSubmissionRepository`, bổ sung các câu truy vấn đếm theo khoảng thời gian (`between from_date and to_date`).
2. Trong `BiAnalyticsServiceImpl.getFunnelReport`:
   - Thực hiện tổng hợp số liệu các giai đoạn.
   - Tính toán các tỷ lệ phần trăm theo công thức, làm tròn 2 chữ số thập phân.
   - Đưa ra cảnh báo tắc nghẽn (`bottleneck_warning`) nếu `expired_hold_rate > 25.0%`.
3. Trong `BiAnalyticsController`: Khai báo endpoint có bảo vệ quyền truy cập.
4. Viết comment tiếng Việt đầy đủ.

---

## 5. Tiêu chí Nghiệm thu (Acceptance Criteria)
- [ ] Số liệu tính toán tỷ lệ phần trăm chính xác theo công thức nghiệp vụ.
- [ ] Phản hồi API chuẩn định dạng `snake_case`, không chứa dữ liệu suy diễn vô căn cứ.
- [ ] Hỗ trợ lọc theo khoảng ngày linh hoạt.

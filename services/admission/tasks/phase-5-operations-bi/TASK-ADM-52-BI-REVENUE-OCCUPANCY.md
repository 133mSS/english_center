# TASK-ADM-52: API Báo cáo Xếp hạng Khóa học, Doanh thu Tiềm năng & Lấp đầy (BI-02)

- **Mã nhiệm vụ**: `TASK-ADM-52`
- **Phân kỳ**: `Phase 5: Xuất Dữ liệu & Phân tích BI (OPS/BI)`
- **Độ ưu tiên**: `P1`
- **Yêu cầu chức năng liên quan**: `BI-02`, `BI-REV-01`, `BI-REV-02`, `BI-OCC-01`
- **Quy tắc bất biến bảo vệ**: `INV-SYS-01`

---

## 1. Mục tiêu Nghiệp vụ & Kỹ thuật
Xây dựng API Báo cáo Hiệu quả Thương mại Khóa học & Doanh thu Tuyển sinh:
1. **Xếp hạng Khóa học (Top Courses by Volume)**:
   - Xếp hạng các khóa học có lượng đăng ký tuyển sinh cao nhất theo số lượng đơn đăng ký phát sinh.
2. **Doanh thu Tiềm năng Đang giữ chỗ (BI-REV-01 - Pipeline Potential Revenue)**:
   - Đo lường tổng giá trị tiền học phí của tất cả các đơn `PENDING` còn thời hạn giữ chỗ 48h (`hold_expires_at > NOW()`):
     $$\text{Pipeline Revenue} = \sum (\text{Số đơn PENDING trong hạn} \times \text{Học phí lớp})$$
3. **Doanh thu Tuyển sinh Thực tế (BI-REV-02 - Realized Admission Revenue)**:
   - Tổng số tiền học phí từ các đơn đã được duyệt thành công (`APPROVED`) trong kỳ:
     $$\text{Realized Revenue} = \sum (\text{Số đơn APPROVED} \times \text{Học phí lớp})$$
4. **Tỷ lệ Lấp đầy Sĩ số Trung bình (BI-OCC-01 - Average Class Occupancy)**:
   - Đánh giá mức độ tối ưu hóa công suất phòng và lớp:
     $$\text{Occupancy Rate} = \frac{\sum \text{Sĩ số APPROVED}}{\sum \text{max\_students của lớp OPEN/IN\_PROGRESS}} \times 100\% \quad (\text{Mục tiêu } \ge 80\%)$$

---

## 2. Phạm vi File Tác động

### File tạo mới hoặc chỉnh sửa:
- `services/admission/backend/src/main/java/com/englishcenter/admission/controller/BiAnalyticsController.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/service/BiAnalyticsService.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/service/impl/BiAnalyticsServiceImpl.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/dto/bi/RevenueOccupancyReportResponse.java`

---

## 3. Đặc tả API Hợp đồng

### API: `GET /api/admission/bi/courses-revenue`
- **Header**: `Authorization: Bearer <Staff/Admin_Token>`
- **Query Params**: `from_date`, `to_date`
- **Response Thành công (HTTP 200 OK)**:
  ```json
  {
    "success": true,
    "data": {
      "pipeline_potential_revenue": 45000000.0,
      "realized_admission_revenue": 185000000.0,
      "average_occupancy_rate": 84.5,
      "top_courses": [
        {
          "course_id": 1,
          "course_code": "IELTS-6.5",
          "title": "IELTS Chuyên Sâu 6.5+",
          "approved_enrollments": 25,
          "pending_enrollments": 5,
          "realized_revenue": 187500000.0,
          "pipeline_revenue": 37500000.0
        }
      ]
    },
    "message": "Báo cáo doanh thu tuyển sinh và tỷ lệ lấp đầy thành công"
  }
  ```

---

## 4. Kế hoạch Triển khai (Step-by-step)
1. Viết câu lệnh SQL JPQL tổng hợp doanh thu theo từng khóa học trong `EnrollmentRepository`:
   ```sql
   SELECT e.clazz.course.id, e.clazz.course.code, e.clazz.course.title,
          COUNT(CASE WHEN e.status = 'APPROVED' THEN 1 END),
          COUNT(CASE WHEN e.status = 'PENDING' AND e.holdExpiresAt > :now THEN 1 END),
          SUM(CASE WHEN e.status = 'APPROVED' THEN e.clazz.course.tuitionFee ELSE 0 END),
          SUM(CASE WHEN e.status = 'PENDING' AND e.holdExpiresAt > :now THEN e.clazz.course.tuitionFee ELSE 0 END)
   FROM Enrollment e
   GROUP BY e.clazz.course.id, e.clazz.course.code, e.clazz.course.title
   ```
2. Trong `BiAnalyticsServiceImpl`: Thực hiện tính toán và ánh xạ vào DTO.
3. Viết comment tiếng Việt chi tiết cho phương thức.

---

## 5. Tiêu chí Nghiệm thu (Acceptance Criteria)
- [ ] Tính toán số tiền doanh thu tiềm năng và thực tế hoàn toàn chính xác theo biểu phí khóa học và số lượng đơn.
- [ ] Đơn `EXPIRED` hoặc `CANCELLED` tuyệt đối không bị tính vào doanh thu tiềm năng hay thực tế.
- [ ] Tỷ lệ lấp đầy sĩ số phản ánh trung thực tình trạng các lớp học đang mở.

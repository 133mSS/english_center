# TASK-ADM-32: Động cơ Đề xuất Khóa học Tự động Theo Điểm Khảo thí

- **Mã nhiệm vụ**: `TASK-ADM-32`
- **Phân kỳ**: `Phase 3: Khảo thí Đầu vào Chuyên sâu (TST)`
- **Độ ưu tiên**: `P1`
- **Yêu cầu chức năng liên quan**: `FR-TST-05`, `BI-FUN-02`
- **Quy tắc bất biến bảo vệ**: `INV-SYS-01`

---

## 1. Mục tiêu Nghiệp vụ & Kỹ thuật
Xây dựng Động cơ Quy tắc Đề xuất Khóa học (Recommendation Rule Engine) giúp định hướng lộ trình học tập tối ưu cho học viên ngay sau khi hoàn thành bài khảo thí:
1. **Quản lý Quy tắc Đề xuất (`admission.test_recommendation_rules`)**:
   - Cho phép Quản trị viên/Học vụ cấu hình ngưỡng điểm cho từng bộ đề:
     - `min_score`: Điểm tối thiểu (bao gồm, ví dụ: 0.0, 40.0, 65.0, 80.0)
     - `max_score`: Điểm tối đa (bao gồm, ví dụ: 39.9, 64.9, 79.9, 100.0)
     - `recommended_course_id`: Khóa học tương ứng đề xuất cho thang điểm này.
     - `advice_note`: Lời khuyên học vụ tùy biến (ví dụ: *"Bạn nên củng cố ngữ pháp trước khi bước vào luyện thi IELTS cấp tốc"*).
2. **Khớp nối Quy tắc (Rule Matching)**:
   - Khi có điểm tổng kết bài thi (`total_score`), hệ thống tự động tìm kiếm quy tắc thỏa mãn:
     $$\text{min\_score} \le \text{total\_score} \le \text{max\_score}$$
   - Trả về thông tin chi tiết của khóa học được đề xuất kèm danh sách các lớp học sắp khai giảng của khóa học đó để học viên có thể bấm "Đăng ký ngay" (giữ chỗ 48h).

---

## 2. Phạm vi File Tác động

### File tạo mới hoặc chỉnh sửa:
- `services/admission/backend/src/main/java/com/englishcenter/admission/controller/RecommendationRuleController.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/service/RecommendationService.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/service/impl/RecommendationServiceImpl.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/repository/TestRecommendationRuleRepository.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/entity/TestRecommendationRule.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/dto/test/CreateRuleRequest.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/dto/test/RecommendationResultDTO.java`

---

## 3. Đặc tả Kỹ thuật & Logic Khớp Quy tắc

### 3.1. Truy vấn Tìm Quy tắc Phù hợp
```java
@Query("SELECT r FROM TestRecommendationRule r " +
       "WHERE r.testSet.id = :testSetId " +
       "  AND :score >= r.minScore AND :score <= r.maxScore")
Optional<TestRecommendationRule> findMatchingRule(
    @Param("testSetId") Long testSetId, 
    @Param("score") Double score
);
```

### 3.2. Cấu trúc Trả về cho Học viên
```json
{
  "total_score": 72.5,
  "recommended_course": {
    "course_id": 3,
    "code": "IELTS-6.0",
    "title": "IELTS Intermediate Bứt Phá 6.0+",
    "tuition_fee": 6800000.0,
    "advice_note": "Điểm Nghe và Đọc của bạn rất tốt. Khóa học này sẽ giúp bạn hoàn thiện kỹ năng Viết và Nói."
  },
  "upcoming_classes": [
    {
      "class_id": 12,
      "class_name": "IELTS 6.0 Tối 3-5-7",
      "start_date": "2026-11-20",
      "available_slots": 5
    }
  ]
}
```

---

## 4. Kế hoạch Triển khai (Step-by-step)
1. Tạo Entity `TestRecommendationRule` ánh xạ bảng `admission.test_recommendation_rules`.
2. Tạo Repository với hàm `findMatchingRule`.
3. Trong `RecommendationServiceImpl`:
   - Viết hàm CRUD quy tắc dành cho Staff/Admin.
   - Viết hàm `getRecommendation(Long testSetId, Double totalScore)`: Tìm rule, lấy thông tin khóa học và các lớp `OPEN` có `available_slots > 0` gần nhất.
4. Tích hợp kết quả đề xuất vào luồng nộp bài thi của `PlacementTestServiceImpl`.
5. Viết comment tiếng Việt đầy đủ.

---

## 5. Tiêu chí Nghiệm thu (Acceptance Criteria)
- [ ] Thí sinh thi đạt 75/100 $\rightarrow$ Đề xuất chính xác khóa học tương ứng với dải điểm 65.0 - 79.9 cấu hình trong DB.
- [ ] Gửi kèm danh sách các lớp học còn chỗ trống đang mở tuyển sinh để học viên nộp đơn trực tiếp.
- [ ] Thao tác cấu hình quy tắc của Staff hoạt động trơn tru qua REST API.

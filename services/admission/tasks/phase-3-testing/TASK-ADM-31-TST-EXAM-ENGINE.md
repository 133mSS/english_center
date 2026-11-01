# TASK-ADM-31: Động cơ Khảo thí Trực tuyến Countdown, Tự động Chấm & Bóc tách Kỹ năng

- **Mã nhiệm vụ**: `TASK-ADM-31`
- **Phân kỳ**: `Phase 3: Khảo thí Đầu vào Chuyên sâu (TST)`
- **Độ ưu tiên**: `P0 (Bắt buộc)`
- **Yêu cầu chức năng liên quan**: `FR-TST-03`, `FR-TST-04`, `BI-FUN-01`
- **Quy tắc bất biến bảo vệ**: `INV-SYS-01`

---

## 1. Mục tiêu Nghiệp vụ & Kỹ thuật
Xây dựng Động cơ thi trực tuyến hoàn chỉnh phục vụ đánh giá năng lực ứng viên:
1. **Lấy nội dung đề thi làm bài (Bảo mật Đáp án)**:
   - Học viên gọi API lấy đề thi: Trả về toàn bộ danh sách câu hỏi trắc nghiệm, media audio, đoạn văn đọc hiểu.
   - **Bảo mật tuyệt đối**: Trường `correct_option` bị loại bỏ khỏi JSON trả về Client (`@JsonIgnore` hoặc dùng DTO riêng `PublicQuestionDTO`) để chống lộ đáp án qua Inspect Element.
2. **Nộp bài & Chấm điểm Tự động (Auto-Grading)**:
   - Nhận danh sách câu trả lời của thí sinh: `[{"question_id": 1, "selected_option": "B"}, ...]`.
   - Đối chiếu với đáp án đúng trong cơ sở dữ liệu.
   - Bóc tách điểm số độc lập cho từng phần thi:
     - `listening_score`: Tổng điểm các câu đúng thuộc kỹ năng `LISTENING`.
     - `reading_score`: Tổng điểm các câu đúng thuộc kỹ năng `READING`.
     - `grammar_score`: Tổng điểm các câu đúng thuộc kỹ năng `GRAMMAR`.
     - `total_score = listening_score + reading_score + grammar_score`.
3. **Lưu kết quả bài thi (`admission.test_submissions`)**:
   - Lưu trữ `test_set_id`, `user_id` (nếu có), thông tin thí sinh (`full_name`, `email`, `phone`), thời gian bắt đầu, thời gian nộp bài, điểm số chi tiết.

---

## 2. Phạm vi File Tác động

### File tạo mới hoặc chỉnh sửa:
- `services/admission/backend/src/main/java/com/englishcenter/admission/controller/PlacementTestController.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/service/PlacementTestService.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/service/impl/PlacementTestServiceImpl.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/repository/TestSubmissionRepository.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/entity/TestSubmission.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/dto/test/TakeTestResponse.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/dto/test/SubmitTestRequest.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/dto/test/TestResultResponse.java`

---

## 3. Đặc tả API Hợp đồng

### 3.1. Lấy Đề thi Bắt đầu Làm bài
- **URL**: `GET /api/admission/tests/public/{setId}/start`
- **Response**: Trả về `test_set` và danh sách câu hỏi (không chứa trường `correct_option`).

### 3.2. Nộp Bài thi & Nhận Kết quả Tức thì
- **URL**: `POST /api/admission/tests/public/submit`
- **Request Body**:
  ```json
  {
    "test_set_id": 1,
    "email": "hocvien.moi@gmail.com",
    "full_name": "Nguyen Van B",
    "phone": "0912345678",
    "answers": [
      { "question_id": 101, "selected_option": "B" },
      { "question_id": 102, "selected_option": "A" }
    ]
  }
  ```
- **Response Thành công (HTTP 200 OK)**:
  ```json
  {
    "success": true,
    "data": {
      "submission_id": 501,
      "total_score": 75.0,
      "listening_score": 25.0,
      "reading_score": 30.0,
      "grammar_score": 20.0,
      "recommended_course": {
        "course_id": 2,
        "course_code": "IELTS-5.5",
        "title": "IELTS Pre-Intermediate Mục Tiêu 5.5"
      }
    },
    "message": "Nộp bài và chấm điểm thành công"
  }
  ```

---

## 4. Kế hoạch Triển khai (Step-by-step)
1. Tạo JPA Entity `TestSubmission` lưu bản ghi kết quả bài làm.
2. Trong `PlacementTestServiceImpl`:
   - Viết hàm `getTestForExam(Long testSetId)`: Lọc câu hỏi và chuyển sang `PublicQuestionDTO` (giấu đáp án đúng).
   - Viết hàm `submitAndGrade(SubmitTestRequest request)`:
     - Tự động sinh/lấy tài khoản học viên từ email (gọi `UserService.getOrCreateStudentUser`).
     - Tải danh sách câu hỏi và đáp án gốc từ DB.
     - Lặp qua từng câu trả lời của thí sinh, so sánh với `correct_option`.
     - Phân loại cộng điểm theo kỹ năng tương ứng.
     - Lưu bài làm vào `test_submissions`.
     - Gọi `RecommendationService` để lấy khóa học phù hợp (TASK-ADM-32).
3. Viết comment tiếng Việt đầy đủ.

---

## 5. Tiêu chí Nghiệm thu (Acceptance Criteria)
- [ ] API lấy đề thi tuyệt đối không để lộ đáp án đúng trong response JSON.
- [ ] Trắc nghiệm chấm điểm tự động chính xác từng kỹ năng, tổng điểm bằng tổng của 3 kỹ năng cộng lại.
- [ ] Thí sinh nộp bài thi thành công tự động được tạo tài khoản trong `admission.users` nếu là thí sinh mới.

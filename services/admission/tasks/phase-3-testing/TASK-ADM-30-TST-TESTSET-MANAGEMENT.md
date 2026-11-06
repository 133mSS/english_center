# TASK-ADM-30: Quản lý Ngân hàng Bộ Đề & Câu hỏi 3 Kỹ năng (Listening, Reading, Grammar)

- **Mã nhiệm vụ**: `TASK-ADM-30`
- **Phân kỳ**: `Phase 3: Khảo thí Đầu vào Chuyên sâu (TST)`
- **Độ ưu tiên**: `P1`
- **Yêu cầu chức năng liên quan**: `FR-TST-01`, `FR-TST-02`
- **Quy tắc bất biến bảo vệ**: `INV-SYS-01`

---

## 1. Mục tiêu Nghiệp vụ & Kỹ thuật
Xây dựng ngân hàng đề thi khảo thí phân loại trình độ đầu vào chuẩn hóa 3 kỹ năng:
1. **Quản lý Bộ đề thi (`admission.test_sets`)**:
   - Thêm mới, chỉnh sửa, xem danh sách bộ đề.
   - Các trường: Mã đề (`code`, duy nhất), Tên bộ đề (`title`), Thời lượng làm bài đếm ngược (`duration_minutes`, mặc định 45 phút), Điểm tối đa (`total_max_score`, thường là 100 điểm), Trạng thái kích hoạt (`is_active`).
2. **Quản lý Câu hỏi bóc tách 3 Kỹ năng (`admission.test_questions`)**:
   - Mỗi câu hỏi thuộc về 1 bộ đề, phân loại theo kỹ năng:
     - `LISTENING`: Đính kèm đường dẫn file âm thanh `audio_url`.
     - `READING`: Đính kèm đoạn văn bản đọc hiểu `passage_text`.
     - `GRAMMAR`: Câu hỏi trắc nghiệm ngữ pháp & từ vựng.
   - Cấu trúc trắc nghiệm 4 lựa chọn: `option_a`, `option_b`, `option_c`, `option_d`.
   - Đáp án đúng: `correct_option` (`'A'`, `'B'`, `'C'`, `'D'`).
   - Trọng số điểm câu hỏi: `score_weight` (ví dụ: 1.0 hoặc 2.0).

---

## 2. Phạm vi File Tác động

### File tạo mới hoặc chỉnh sửa:
- `services/admission/backend/src/main/java/com/englishcenter/admission/controller/TestManagementController.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/service/TestManagementService.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/service/impl/TestManagementServiceImpl.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/repository/TestSetRepository.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/repository/TestQuestionRepository.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/entity/TestSet.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/entity/TestQuestion.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/dto/test/CreateTestSetRequest.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/dto/test/CreateQuestionRequest.java`

---

## 3. Đặc tả API Hợp đồng

### 3.1. Tạo mới Bộ đề thi
- **URL**: `POST /api/admission/tests/sets`
- **Header**: `Authorization: Bearer <Staff/Admin_Token>`
- **Request Body**:
  ```json
  {
    "code": "TEST-ENTRY-2026-A1",
    "title": "Đề Khảo Thí Đầu Vào Chuẩn 3 Kỹ Năng Đợt 1",
    "duration_minutes": 45,
    "description": "Dành cho học viên đăng ký các khóa IELTS Foundation"
  }
  ```

### 3.2. Thêm Câu hỏi vào Bộ đề
- **URL**: `POST /api/admission/tests/sets/{setId}/questions`
- **Request Body**:
  ```json
  {
    "skill": "LISTENING",
    "audio_url": "https://cdn.englishcenter.edu.vn/audio/part1-q1.mp3",
    "passage_text": null,
    "question_text": "What time will the bus arrive at the terminal?",
    "option_a": "At 8:15 AM",
    "option_b": "At 8:30 AM",
    "option_c": "At 9:00 AM",
    "option_d": "At 9:15 AM",
    "correct_option": "B",
    "score_weight": 2.0,
    "display_order": 1
  }
  ```

---

## 4. Kế hoạch Triển khai (Step-by-step)
1. Tạo JPA Entities `TestSet` và `TestQuestion` với quan hệ `@OneToMany(mappedBy = "testSet")`.
2. Tạo Repositories và khai báo các phương thức tìm kiếm câu hỏi theo đề thi sắp xếp theo `display_order`.
3. Trong `TestManagementServiceImpl`:
   - Viết các hàm CRUD bộ đề và câu hỏi.
   - Tự động cộng dồn `total_max_score` của bộ đề khi thêm câu hỏi mới.
4. Trong `TestManagementController`: Khai báo endpoints với phân quyền Staff/Admin.
5. Viết comment tiếng Việt đầy đủ.

---

## 5. Tiêu chí Nghiệm thu (Acceptance Criteria)
- [ ] Thêm câu hỏi với `correct_option = 'E'` $\rightarrow$ Bị chặn bởi validation (chỉ chấp nhận A, B, C, D).
- [ ] Thêm câu hỏi Listening bắt buộc có `audio_url`, thêm câu hỏi Reading bắt buộc có `passage_text`.
- [ ] Truy vấn bộ đề hiển thị đầy đủ tổng số câu hỏi và tổng điểm tối đa chuẩn xác.

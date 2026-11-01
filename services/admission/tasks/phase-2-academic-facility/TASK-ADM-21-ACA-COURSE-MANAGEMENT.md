# TASK-ADM-21: Quản lý Khóa học, Học phí Chuẩn & Khóa học Tiên quyết

- **Mã nhiệm vụ**: `TASK-ADM-21`
- **Phân kỳ**: `Phase 2: Cơ sở vật chất & Đào tạo (FAC/ACA)`
- **Độ ưu tiên**: `P0 (Bắt buộc)`
- **Yêu cầu chức năng liên quan**: `FR-ACA-01`
- **Quy tắc bất biến bảo vệ**: `INV-ADM-02` (Mã khóa học duy nhất), `INV-SYS-01`

---

## 1. Mục tiêu Nghiệp vụ & Kỹ thuật
Xây dựng danh mục khóa học chuẩn làm gốc rễ cho toàn bộ phân hệ đào tạo và tuyển sinh:
1. **CRUD Khóa học (`admission.courses`)**:
   - Thêm mới, chỉnh sửa, xem chi tiết và ngưng tuyển sinh khóa học.
   - Các trường thông tin: Mã khóa (`code`, duy nhất, ví dụ `ENG-B1`, `IELTS-6.5`), Tên khóa (`title`), Trình độ (`level`: `BEGINNER`, `INTERMEDIATE`, `ADVANCED`), Thời lượng (`duration_weeks` $\ge 1$), Học phí niêm yết (`tuition_fee` $> 0$), Mô tả tổng quan (`description`).
2. **Khóa học Tiên quyết (Prerequisite Course)**:
   - Cho phép liên kết trường `prerequisite_course_id` trỏ tới chính bảng `courses`.
   - Ngăn chặn vòng lặp phụ thuộc (Circular Dependency): Khóa A không được yêu cầu tiên quyết là chính khóa A, và không được tạo vòng lặp $A \rightarrow B \rightarrow A$.
3. **Bảo vệ Tính duy nhất (Invariant INV-ADM-02)**:
   - Đảm bảo mã `code` luôn là duy nhất trên toàn hệ thống.

---

## 2. Phạm vi File Tác động

### File tạo mới hoặc chỉnh sửa:
- `services/admission/backend/src/main/java/com/englishcenter/admission/controller/CourseController.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/service/CourseService.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/service/impl/CourseServiceImpl.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/repository/CourseRepository.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/entity/Course.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/dto/course/CreateCourseRequest.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/dto/course/UpdateCourseRequest.java`
- `services/admission/backend/src/main/java/com/englishcenter/admission/dto/course/CourseResponse.java`

---

## 3. Đặc tả API Hợp đồng

### 3.1. Tạo mới Khóa học
- **URL**: `POST /api/admission/courses`
- **Header**: `Authorization: Bearer <Staff/Admin_Token>`
- **Request Body**:
  ```json
  {
    "code": "IELTS-6.5",
    "title": "IELTS Chuyên Sâu Mục Tiêu 6.5+",
    "level": "ADVANCED",
    "duration_weeks": 12,
    "tuition_fee": 7500000.0,
    "prerequisite_course_id": 2,
    "description": "Khóa luyện thi 4 kỹ năng chuẩn đề Cambridge"
  }
  ```
- **Validation**:
  - `code`: Không rỗng, viết hoa không dấu, không trùng lặp (trả về 409 `ADM_COURSE_CODE_EXISTS`).
  - `tuition_fee`: Bắt buộc là số thực dương $> 0$.
  - `duration_weeks`: Bắt buộc là số nguyên dương $\ge 1$.

### 3.2. Lấy Danh mục Khóa học Công khai
- **URL**: `GET /api/admission/courses` (Không yêu cầu đăng nhập)
- **Query Params**: `level`, `is_active`
- **Response**: Trả về danh sách khóa học kèm thông tin khóa học tiên quyết (nếu có).

---

## 4. Kế hoạch Triển khai (Step-by-step)
1. Cập nhật `Course.java` Entity với đầy đủ annotation JPA, quan hệ `@ManyToOne` tự tham chiếu cho `prerequisiteCourse`.
2. Trong `CourseRepository`:
   - Viết method `boolean existsByCode(String code);`.
   - Viết method `boolean existsByCodeAndIdNot(String code, Long id);` dùng cho kiểm tra khi cập nhật.
3. Trong `CourseServiceImpl`:
   - Kiểm tra mã khóa học duy nhất trước khi lưu.
   - Kiểm tra `prerequisite_course_id != current_course_id`.
   - Bắt ngoại lệ và ném `BusinessException(ErrorCode.ADM_COURSE_CODE_EXISTS)`.
4. Viết comment tiếng Việt đầy đủ.

---

## 5. Tiêu chí Nghiệm thu (Acceptance Criteria)
- [ ] Tạo khóa học với mã đã tồn tại $\rightarrow$ Trả về mã HTTP 409 kèm mã lỗi `ADM_COURSE_CODE_EXISTS`.
- [ ] Chạy bộ Invariant Test `INV-ADM-02` đạt `OK`:
  ```bash
  python3 -m unittest discover -s tests/invariants -p "test_admission_invariants.py" -v
  ```
- [ ] Gọi API public xem danh mục khóa học không cần gửi JWT Token vẫn nhận 200 OK.

# TỔNG HỢP TÍNH NĂNG VÀ CƠ SỞ DỮ LIỆU PHÂN HỆ ĐÀO TẠO & KẾT QUẢ HỌC TẬP (LEARNING)

**Dự án:** Hệ thống Quản lý Trung tâm Anh ngữ
**Phân hệ:** Learning Service (`learning-service`, port 8083)
**Công nghệ:** Python FastAPI + Frontend HTML/JS + PostgreSQL
**Trạng thái:** Bản tổng hợp đặc tả nghiệp vụ và CSDL chính thức – Dùng để gửi duyệt và triển khai code.

---

## 1. Danh sách tính năng (Feature List)

Phân hệ Learning gồm 3 tính năng cốt lõi, xây dựng trên yêu cầu nghiệp vụ và các quy tắc bất biến (Invariant):

- **LRN-01 – Quản lý Học liệu & Slide:** Giáo viên đăng tải slide, tài liệu đọc, file audio/video; học viên xem và tải về theo lớp học.
- **LRN-02 – Nhập điểm & Đánh giá [Core V2]:** Ghi nhận điểm các bài kiểm tra (Midterm, Final, Quiz...) kèm nhận xét của giáo viên.
- **LRN-03 – Báo cáo Đánh giá Định kỳ:** Thống kê bảng xếp loại học lực và tỷ lệ đạt/trượt của lớp theo kỳ đánh giá.

**Bảng 1: Đặc tả tính năng phân hệ Learning**

| Mã CN           | Tên tính năng                        | Người dùng (Actor) | Input / Output                                                                                                                   | Quy tắc nghiệp vụ (Rules)                                                                                                                        | Giao diện (UI) | Liên kết phân hệ khác                      |
| ---------------- | --------------------------------------- | --------------------- | -------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- | --------------- | ----------------------------------------------- |
| LRN-01           | Quản lý Học liệu & Slide            | Teacher, Student      | Input: class_id, tiêu đề, loại tài liệu (DOCUMENT, VIDEO, SLIDE), link/file  Output: Tài liệu xuất hiện trong kho lớp | • Học viên chỉ xem được học liệu của lớp mình học  • File URL không được để trống                                              | materials.html  | Tuyển sinh (lấy class_id)                     |
| LRN-02 [Core V2] | Nhập điểm & Đánh giá (INV-LRN-01) | Teacher               | Input: class_id, student_id, tên bài thi (Midterm, Final), điểm số  Output: Bản ghi điểm số, màn xét                  | • Ràng buộc thang điểm: 0.0 <= score <= max_score (chặn điểm âm hoặc > 100)  • Học viên chỉ xem điểm của chính mình (INV-LRN-02) | grades.html     | Học viên (hiển thị kết quả vào học bạ) |
| LRN-03           | Báo cáo Đánh giá Định kỳ        | Staff, Teacher        | Input: class_id, chọn kỳ đánh giá  Output: Bảng xếp loại học lực, tỷ lệ đạt/trượt                                | • Điểm trung bình >= 50% tính là Đạt (Pass)                                                                                                 | grades.html     | Tuyển sinh (tư vấn khóa học tiếp theo)    |

**Quy tắc bất biến (Invariant):**

- **INV-LRN-01:** Giáo viên chỉ được nhập/sửa điểm cho học viên thuộc lớp mình phụ trách.
- **INV-LRN-02:** Học viên chỉ được xem điểm của chính mình.

---

## 2. Rà soát và điều chỉnh CSDL (schema `learning` trong init-db.sql)

### 2.1. Rà soát cấu trúc bảng hiện có

**Bảng 2: Rà soát và đề xuất điều chỉnh CSDL (Schema)**

| Tên bảng | Các cột hiện có trong init-db.sql                                            | Đánh giá (Đủ/Thiếu) | Đề xuất thêm cột mới (Tên, Kiểu, Ý nghĩa)                                                                                                        | Quan hệ khóa ngoại logic                                                           |
| ---------- | -------------------------------------------------------------------------------- | ------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| materials  | id, class_id, title, description, material_type, file_url, uploaded_at           | Đủ                      | original_filename (VARCHAR(255) – tên file gốc khi upload); file_size (BIGINT – dung lượng file theo Bytes); siết file_url NOT NULL và khác rỗng | class_id liên kết admission.classes(id)                                             |
| grades     | id, class_id, student_id, assessment_name, score, max_score, feedback, graded_at | Đủ                      | weight (NUMERIC(3,2) – hệ số điểm của đầu điểm, VD: 0.4, 0.6); bổ sung CHECK thang điểm và UNIQUE chống trùng đầu điểm                 | student_id liên kết student.students(id); class_id liên kết admission.classes(id) |

### 2.2. Ràng buộc toàn vẹn và đối tượng bổ sung

- **Ràng buộc CHECK:**
  - `learning.materials`: material_type thuộc (DOCUMENT, VIDEO, SLIDE); file_url khác rỗng.
  - `learning.grades`: score >= 0; max_score > 0; weight trong khoảng (0, 1]; score <= max_score (chk_score_max_score).
- **Ràng buộc UNIQUE:** uq_student_assessment (class_id, student_id, assessment_name) – mỗi học viên chỉ có một điểm cho một bài đánh giá trong một lớp.
- **Indexes:** idx_materials_class_id; idx_grades_class_student; idx_grades_class_assessment (tối ưu truy vấn báo cáo theo kỳ đánh giá).
- **Views báo cáo (LRN-03):**
  - `learning.v_student_grade_summary`: điểm trung bình có trọng số theo từng học viên/lớp kèm xếp loại Pass/Fail (ngưỡng 50%).
  - `learning.v_class_pass_rate`: thống kê số lượng đạt/trượt và tỷ lệ đạt theo lớp.

---

## 3. Thiết kế CSDL chính thức (schema `learning`)

**Bảng 3: Cấu trúc các đối tượng CSDL phân hệ Learning**

| STT | Tên đối tượng               | Vai trò                                | Các cột                                                                                            |
| --- | -------------------------------- | --------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| 1   | learning.materials               | Quản lý học liệu, slide bài giảng | id, class_id, title, description, material_type, file_url, original_filename, file_size, uploaded_at |
| 2   | learning.grades                  | Quản lý điểm số và đánh giá    | id, class_id, student_id, assessment_name, score, max_score, weight, feedback, graded_at             |
| 3   | learning.v_student_grade_summary | View báo cáo xếp loại học viên    | class_id, student_id, total_assessments, weighted_avg_score, average_percentage, result              |
| 4   | learning.v_class_pass_rate       | View báo cáo tỷ lệ đạt/trượt    | class_id, total_students, pass_count, fail_count, pass_rate_percentage                               |

**Lưu ý quan hệ:**

- `class_id` liên kết logic (logical FK) với `admission.classes(id)`.
- `student_id` liên kết logic (logical FK) với `student.students(id)`.
- Không tạo FK vật lý liên schema để bảo đảm tính độc lập giữa các microservice.

---

## 4. Toàn văn SQL Script Khởi tạo (Full DDL + Seed + Report)

Ghi chú triển khai: script chạy một lần cho môi trường Dev/Test, tự DROP bảng cũ (CASCADE kèm view phụ thuộc) và CREATE lại toàn bộ bảng, ràng buộc, index, view kèm dữ liệu mẫu; không cần script ALTER riêng.

```sql
-- ========================================================
-- DDL SCRIPT: LEARNING SERVICE (PostgreSQL)
-- Khởi tạo toàn bộ schema learning: bảng, ràng buộc, index, view và seed
-- Chạy độc lập: tự xóa bảng cũ (nếu có) và tạo mới (dùng cho Dev/Test)
-- ========================================================

-- 1. Khởi tạo Schema
CREATE SCHEMA IF NOT EXISTS learning;

-- 2. Xóa bảng cũ (CASCADE để xóa kèm các view phụ thuộc)
DROP TABLE IF EXISTS learning.grades CASCADE;
DROP TABLE IF EXISTS learning.materials CASCADE;

-- 3. Bảng Quản lý Học liệu (Materials) - LRN-01
CREATE TABLE learning.materials (
    id SERIAL PRIMARY KEY,
    class_id INTEGER NOT NULL,               -- Logical FK -> admission.classes(id)
    title VARCHAR(255) NOT NULL,
    description TEXT,
    material_type VARCHAR(50) NOT NULL DEFAULT 'DOCUMENT'
        CHECK (material_type IN ('DOCUMENT', 'VIDEO', 'SLIDE')),  -- Enum loại học liệu theo LRN-01; mở rộng tại đây nếu cần thêm loại khác
    file_url TEXT NOT NULL
        CHECK (btrim(file_url) <> ''),       -- Rule LRN-01: File URL không được để trống
    original_filename VARCHAR(255),          -- Tên file gốc khi upload
    file_size BIGINT CHECK (file_size >= 0), -- Dung lượng file (Bytes); BIGINT để chịu file > 2GB
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 4. Bảng Quản lý Điểm số (Grades) - LRN-02
CREATE TABLE learning.grades (
    id SERIAL PRIMARY KEY,
    class_id INTEGER NOT NULL,               -- Logical FK -> admission.classes(id)
    student_id INTEGER NOT NULL,             -- Logical FK -> student.students(id)
    assessment_name VARCHAR(255) NOT NULL,   -- Midterm, Final, Speaking, Quiz...
    score NUMERIC(5, 2) NOT NULL
        CHECK (score >= 0),                  -- Rule LRN-02: chặn điểm âm
    max_score NUMERIC(5, 2) NOT NULL DEFAULT 100.0
        CHECK (max_score > 0),               -- Tránh NULL lọt qua CHECK và lỗi chia
    weight NUMERIC(3, 2)
        CHECK (weight > 0 AND weight <= 1),  -- Hệ số điểm của đầu điểm (VD: 0.4, 0.6); NULL = chưa gán, coi như 1.0 khi tính trung bình
    feedback TEXT,
    graded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- Rule LRN-02: điểm không vượt quá max_score (chặn > 100 khi max_score = 100)
    CONSTRAINT chk_score_max_score CHECK (score <= max_score),

    -- Chống trùng: 1 học viên chỉ có 1 điểm cho 1 bài đánh giá trong 1 lớp
    CONSTRAINT uq_student_assessment UNIQUE (class_id, student_id, assessment_name)
);

-- 5. Indexes tối ưu hiệu năng
CREATE INDEX idx_materials_class_id      ON learning.materials (class_id);
CREATE INDEX idx_grades_class_student    ON learning.grades (class_id, student_id);
CREATE INDEX idx_grades_class_assessment ON learning.grades (class_id, assessment_name); -- Tối ưu lọc "chọn kỳ đánh giá" của LRN-03

-- 6. View phục vụ Báo cáo LRN-03 (Điểm trung bình >= 50% => Pass)
-- 6.1. Điểm trung bình có trọng số + xếp loại theo từng học viên trong lớp
CREATE OR REPLACE VIEW learning.v_student_grade_summary AS
SELECT
    g.class_id,
    g.student_id,
    COUNT(*)                                                  AS total_assessments,
    ROUND(SUM(g.score * COALESCE(g.weight, 1.0))
        / NULLIF(SUM(COALESCE(g.weight, 1.0)), 0), 2)         AS weighted_avg_score,
    ROUND(SUM((g.score / g.max_score * 100) * COALESCE(g.weight, 1.0))
        / NULLIF(SUM(COALESCE(g.weight, 1.0)), 0), 2)         AS average_percentage,
    CASE
        WHEN SUM((g.score / g.max_score * 100) * COALESCE(g.weight, 1.0))
             / NULLIF(SUM(COALESCE(g.weight, 1.0)), 0) >= 50
        THEN 'Pass'
        ELSE 'Fail'
    END                                                       AS result
FROM learning.grades g
GROUP BY g.class_id, g.student_id;

-- 6.2. Tỷ lệ Đạt/Trượt theo lớp
CREATE OR REPLACE VIEW learning.v_class_pass_rate AS
SELECT
    s.class_id,
    COUNT(*)                                              AS total_students,
    COUNT(*) FILTER (WHERE s.result = 'Pass')             AS pass_count,
    COUNT(*) FILTER (WHERE s.result = 'Fail')             AS fail_count,
    ROUND(100.0 * COUNT(*) FILTER (WHERE s.result = 'Pass')
        / COUNT(*), 2)                                    AS pass_rate_percentage
FROM learning.v_student_grade_summary s
GROUP BY s.class_id;

-- ========================================================
-- SEED DATA (Dữ liệu mẫu để test Frontend/Backend)
-- ========================================================
INSERT INTO learning.materials (class_id, title, description, material_type, file_url, original_filename, file_size)
VALUES
    (1, 'Giáo trình IELTS Foundation Unit 1-4', 'Slide và bài tập từ vựng chủ đề Daily Routine', 'SLIDE', 'https://example.com/materials/ielts-u1-4.pdf', 'ielts-u1-4.pdf', 2048000),
    (1, 'Audio luyện nghe Cambridge Practice Test 1', 'File nghe định dạng MP3 cho bài tập về nhà', 'DOCUMENT', 'https://example.com/materials/listening-test1.mp3', 'listening-test1.mp3', 5120000),
    (2, 'Tài liệu Reading Intensive', 'Reading Passages for Advanced', 'DOCUMENT', 'https://example.com/materials/reading-adv.pdf', 'reading-adv.pdf', 3145728);

-- class_id=1, student_id=1,2 tương ứng dữ liệu mẫu của nhóm Admission/Student
INSERT INTO learning.grades (class_id, student_id, assessment_name, score, max_score, weight, feedback)
VALUES
    (1, 1, 'Midterm Test (Reading & Listening)', 82.5, 100.0, 0.4, 'Kỹ năng nghe tốt, cần chú ý phần Matching Headings.'),
    (1, 1, 'Final Test', 78.0, 100.0, 0.6, 'Cần cải thiện từ vựng học thuật.'),
    (1, 2, 'Midterm Test (Reading & Listening)', 90.0, 100.0, 0.4, 'Xuất sắc, phát âm chuẩn.'),
    (1, 2, 'Final Test', 92.0, 100.0, 0.6, 'Giữ vững phong độ.'),
    (2, 3, 'Midterm Test (Reading & Listening)', 40.0, 100.0, 0.4, 'Cần ôn lại kỹ năng đọc.'),
    (2, 3, 'Final Test', 35.0, 100.0, 0.6, 'Dưới trung bình - cần học lại.'),  -- Case Fail để test LRN-03
    (2, 4, 'Quiz 1', 60.0, 100.0, NULL, 'Quiz nhỏ không tính hệ số.');          -- Case weight NULL, coi như 1.0

-- ========================================================
-- TRUY VẤN BÁO CÁO MẪU (LRN-03)
-- ========================================================
-- Báo cáo tổng hợp toàn lớp (xếp loại + tỷ lệ đạt/trượt)
SELECT * FROM learning.v_student_grade_summary ORDER BY class_id, average_percentage DESC;
SELECT * FROM learning.v_class_pass_rate;

-- Báo cáo theo kỳ đánh giá: chỉ tính điểm 1 kỳ (VD: Final Test) cho class_id = 1
SELECT
    class_id,
    student_id,
    ROUND(AVG(score / max_score * 100), 2) AS avg_percentage,
    CASE WHEN AVG(score / max_score * 100) >= 50 THEN 'Pass' ELSE 'Fail' END AS result
FROM learning.grades
WHERE class_id = 1
  AND assessment_name = 'Final Test'
GROUP BY class_id, student_id;
```

---

## 5. Ghi chú thực thi nghiệp vụ ở tầng ứng dụng

- **LRN-01:** API danh sách học liệu luôn lọc theo `class_id` mà học viên đang tham gia (qua enrollment).
- **INV-LRN-01:** API nhập/sửa điểm kiểm tra quyền giảng dạy của giáo viên với lớp trước khi ghi dữ liệu.
- **INV-LRN-02:** API xem điểm luôn lọc `student_id` theo user đăng nhập đối với vai trò STUDENT.
- **LRN-03:** Báo cáo sử dụng view `v_student_grade_summary` / `v_class_pass_rate`; hỗ trợ lọc theo kỳ đánh giá bằng `assessment_name`.

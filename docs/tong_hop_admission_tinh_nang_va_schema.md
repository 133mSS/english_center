# TỔNG HỢP TÍNH NĂNG VÀ CƠ SỞ DỮ LIỆU PHÂN HỆ ADMISSION & IDENTITY

**Dự án:** Hệ thống Quản lý Trung tâm Anh ngữ  
**Phân hệ:** Admission & Identity Service (`admission-service`, port 8081)  
**Công nghệ mô tả trong nguồn:** Java 21, Spring Boot 3.3.4, PostgreSQL 16  
**Trạng thái:** Bản tổng hợp từ 4 tài liệu nhóm cung cấp, dùng để điền Google Docs; không phải chứng nhận mã nguồn đã hiện thực hóa.

## 1. Danh sách các tính năng

Có **30 yêu cầu chức năng (FR)** theo 6 nhóm trong `admission-ba-bi-spec.md`. Các mục và mã được giữ theo tài liệu nguồn.

### Nhóm 1: Quản trị Định danh & Phiên làm việc (FR-IAM)

- **FR-IAM-01 — Tự động sinh tài khoản Student:** Khi học viên làm bài Placement Test hoặc nộp đơn online lần đầu, hệ thống tự động tạo bản ghi `admission.users` với `role='STUDENT'` nếu email chưa tồn tại.
- **FR-IAM-02 — Quản lý Nhân sự:** Cho phép `ADMIN` tạo tài khoản nhân sự (`role` là `STAFF` hoặc `TEACHER`), yêu cầu nhập: Email, Họ tên, Số điện thoại, Giới tính, Ngày sinh.
- **FR-IAM-03 — Xác thực JWT Kép:** Cấp phát cặp token: Access Token (15 phút, stateless) và Refresh Token (7 ngày, stateful lưu trong bảng `refresh_tokens`).
- **FR-IAM-04 — Refresh Token Rotation:** Khi gọi API làm mới token, hệ thống hủy Refresh Token hiện tại (`is_revoked = true`) và cấp phát một cặp Access/Refresh Token hoàn toàn mới.
- **FR-IAM-05 — Khóa / Mở khóa Tài khoản:** Cho phép Quản trị viên kích hoạt hoặc khóa tài khoản người dùng (`is_active = false/true`). Tài khoản bị khóa lập tức bị chặn mọi thao tác gọi API.
- **FR-IAM-06 — Quên mật khẩu qua Email:** Sinh mã token đặt lại mật khẩu ngẫu nhiên có thời hạn 15 phút lưu trong `password_reset_tokens`, gửi liên kết kích hoạt qua email để người dùng thiết lập mật khẩu mới.
- **FR-IAM-07 — Nhật ký Kiểm toán Bảo mật:** Tự động ghi nhật ký bảo mật vào `admission.auth_audit_logs` đối với các sự kiện: `LOGIN_SUCCESS`, `LOGIN_FAILED`, `REFRESH_TOKEN`, `LOGOUT`, `PASSWORD_CHANGED`, `ACCOUNT_LOCKED`.

### Nhóm 2: Cơ sở vật chất, Phòng học & Ca học (FR-FAC)

- **FR-FAC-01 — Quản lý Danh mục Phòng học:** CRUD thông tin phòng học gồm: Mã phòng (`code` unique), Tên phòng, Sức chứa tối đa (`capacity >= 1`), Chi nhánh cơ sở (`branch_name`), Trạng thái hoạt động (`is_active`).
- **FR-FAC-02 — Cấu hình Ca học Tiêu chuẩn:** Hỗ trợ các khung giờ học chuẩn (`start_time`, `end_time`) và các mẫu ngày học trong tuần (`day_pattern`: `MON_WED_FRI`, `TUE_THU_SAT`, `SAT_SUN`, `DAILY`).
- **FR-FAC-03 — Ràng buộc Sức chứa Phòng:** Bắt buộc kiểm tra `class.max_students <= room.capacity`. Nếu vượt quá, trả lỗi `ADM_ROOM_CAPACITY_EXCEEDED`.

### Nhóm 3: Khóa học, Lớp học & Chống Xung đột Lịch (FR-ACA)

- **FR-ACA-01 — Quản lý Khóa học & Lộ trình:** CRUD Khóa học chuẩn: Mã khóa (`code` unique), Tên khóa, Trình độ (`level`: *Beginner, Intermediate, Advanced*), Thời lượng (`duration_weeks`), Học phí tiêu chuẩn (`tuition_amount`), Khóa học tiên quyết (`prerequisite_course_id`).
- **FR-ACA-02 — Quản lý Lớp học:** Mở lớp học gán Khóa học, Phòng học (`room_id`), Giáo viên (`teacher_id`), Ca học & Mẫu ngày, Ngày khai giảng (`start_date`), Ngày bế giảng (`end_date`), Sĩ số tối thiểu (`min_students`), Sĩ số trần (`max_students`).
- **FR-ACA-03 — Công cụ Chống Xung đột Lịch - Conflict Engine:** Tự động phát hiện và chặn lưu lớp nếu xảy ra: - Trùng phòng học với lớp khác đang mở trong cùng khung giờ: `ADM_ROOM_CONFLICT`. - Trùng lịch dạy của giáo viên với lớp khác trong cùng khung giờ: `ADM_TEACHER_CONFLICT`.
- **FR-ACA-04 — Vòng đời Lớp học:** Quản lý trạng thái lớp: `OPEN` $\rightarrow$ `IN_PROGRESS` $\rightarrow$ `COMPLETED`, hoặc `CANCELLED` (Hủy lớp thiếu sĩ số).
- **FR-ACA-05 — Tính toán Slot Khả dụng:** Cung cấp API tính toán số chỗ còn lại theo thời gian thực: $$\text{Available Slots} = \text{max\_students} - \text{Approved Count} - \text{Active Held Count}$$

### Nhóm 4: Khảo thí Đầu vào Chuyên sâu (FR-TST)

- **FR-TST-01 — Quản lý Ngân hàng Đề thi:** Quản lý các Bộ đề thi (`test_sets`) kèm cấu hình thời gian làm bài đếm ngược (`duration_minutes`, mặc định 45 phút).
- **FR-TST-02 — Ngân hàng Câu hỏi 3 Kỹ năng:** Quản lý câu hỏi trắc nghiệm bóc tách thành 3 phần: - *Listening*: Tích hợp file nghe qua `audio_url`. - *Reading*: Tích hợp đoạn văn đọc hiểu qua `passage_text`. - *Grammar & Vocabulary*: Câu hỏi ngữ pháp trắc nghiệm 4 lựa chọn (A/B/C/D) kèm đáp án đúng và trọng số điểm (`score_weight`).
- **FR-TST-03 — Giao diện Khảo thí Countdown:** Giao diện thi trực tuyến hiển thị đồng hồ đếm ngược; tự động khóa và nộp bài khi hết giờ.
- **FR-TST-04 — Chấm điểm Tự động & Bóc tách Kỹ năng:** Tự động chấm điểm ngay khi nộp bài, tách bạch: `listening_score`, `reading_score`, `grammar_score` và tính `total_score`.
- **FR-TST-05 — Đề xuất Khóa học Tự động:** Đối chiếu `total_score` với bảng `test_recommendation_rules` để trả về khóa học phù hợp nhất kèm nút đăng ký lớp.

### Nhóm 5: Tuyển sinh, Giữ chỗ 48h & Xét duyệt Nhập học (FR-ENR)

- **FR-ENR-01 — Đăng ký Tuyển sinh Đa kênh:** Hỗ trợ học viên tự đăng ký trực tuyến hoặc Nhân viên học vụ tạo đơn trực tiếp tại quầy.
- **FR-ENR-02 — Bảo vệ Sĩ số Trần - Invariant Guard:** Chặn tiếp nhận đơn nếu lớp học không còn slot trống khả dụng (`ADM_CLASS_FULL`).
- **FR-ENR-03 — Cấp Slot Giữ chỗ 48h:** Đơn tạo mới có trạng thái `PENDING` và được gán `hold_expires_at = NOW() + 48 HOURS`.
- **FR-ENR-04 — Tự động Thu hồi Slot Quá hạn:** Scheduled Job định kỳ quét và chuyển đơn `PENDING` quá hạn sang `EXPIRED`, giải phóng slot cho học viên khác.
- **FR-ENR-05 — Gia hạn Giữ chỗ Học vụ:** Nhân viên học vụ có quyền gia hạn thêm thời gian giữ chỗ (`extend-hold`) theo yêu cầu chính đáng.
- **FR-ENR-06 — Xét duyệt Nhập học Tự động:** Chuyển đơn sang `APPROVED` khi nhận xác nhận thanh toán thành công (`invoice_status == PAID`) từ **Finance Service**.
- **FR-ENR-07 — Duyệt Tiền mặt Tại quầy:** Nhân viên học vụ có quyền duyệt đơn trực tiếp khi học viên nộp tiền mặt tại trung tâm (`approve-manual`).
- **FR-ENR-08 — Đồng bộ Hồ sơ Học vụ:** Tự động gọi API sang **Student Service** để tạo hồ sơ học viên ngay khi đơn chuyển sang `APPROVED`.

### Nhóm 6: Xuất Dữ liệu & Báo cáo Vận hành (FR-OPS)

- **FR-OPS-01 — Xuất Danh sách Lớp:** Cho phép xuất danh sách học viên đăng ký của một lớp học ra file Excel (.xlsx) hoặc CSV chuẩn.
- **FR-OPS-02 — Xuất Kết quả Khảo thí:** Cho phép xuất bảng điểm khảo thí đầu vào của học viên theo bộ đề ra file Excel/CSV.

### Báo cáo BI được mô tả bổ sung trong tài liệu

- **BI-01 — Phễu chuyển đổi tuyển sinh:** Theo dõi đăng ký test → hoàn thành test → nộp đơn giữ chỗ → đóng phí/nhập học.
- **BI-02 — Hiệu quả khóa học và doanh thu dự kiến:** Xếp hạng khóa theo số lượng đăng ký, doanh thu tiềm năng/thực thu và độ lấp đầy lớp.
- **BI-03 — Sức khỏe vận hành và an toàn tài khoản:** Thống kê hoạt động người dùng và cảnh báo đăng nhập thất bại.

> **Nguồn phần tính năng:** `admission-ba-bi-spec.md` (mục 4 và mục 7), đối chiếu `admission-tech-spec.md` và `admission-uml-spec.md` về cách hiện thực và mô hình hóa.

## 2. Các bảng trong schema `admission`

Có **12 bảng** theo `admission-schema-spec.md` (mục 3 và mục 5). Dưới đây là danh mục và tên **toàn bộ các cột** của từng bảng.

| STT | Bảng | Vai trò | Các cột |
|---:|---|---|---|
| 1 | `admission.users` | Quản lý tài khoản người dùng và phân quyền tập trung | `id`, `email`, `password_hash`, `full_name`, `role`, `phone`, `gender`, `date_of_birth`, `avatar_url`, `must_change_password`, `is_active`, `created_at`, `updated_at` |
| 2 | `admission.refresh_tokens` | Lưu refresh token, thời hạn và trạng thái thu hồi | `id`, `user_id`, `token`, `expires_at`, `is_revoked`, `created_at` |
| 3 | `admission.password_reset_tokens` | Lưu token dùng một lần để đặt lại mật khẩu | `id`, `user_id`, `token`, `expires_at`, `is_used`, `created_at` |
| 4 | `admission.auth_audit_logs` | Ghi nhận sự kiện đăng nhập và bảo mật | `id`, `user_id`, `action`, `ip_address`, `user_agent`, `details`, `created_at` |
| 5 | `admission.rooms` | Quản lý phòng học, sức chứa và cơ sở | `id`, `code`, `name`, `capacity`, `branch_name`, `is_active`, `created_at` |
| 6 | `admission.courses` | Lưu khóa học, trình độ, học phí và điều kiện tiên quyết | `id`, `code`, `name`, `description`, `level`, `target_output`, `duration_weeks`, `tuition_amount`, `prerequisite_course_id`, `is_active`, `created_at` |
| 7 | `admission.classes` | Quản lý lớp học, lịch học, giáo viên và sĩ số | `id`, `course_id`, `room_id`, `teacher_id`, `code`, `name`, `day_pattern`, `start_time`, `end_time`, `start_date`, `end_date`, `min_students`, `max_students`, `status`, `created_at` |
| 8 | `admission.enrollments` | Quản lý đơn đăng ký, giữ chỗ 48 giờ, duyệt/hủy | `id`, `student_id`, `class_id`, `status`, `hold_expires_at`, `invoice_code`, `source`, `approval_method`, `approved_by_user_id`, `note`, `enrolled_at`, `approved_at` |
| 9 | `admission.test_sets` | Lưu bộ đề thi đầu vào và thời gian làm bài | `id`, `title`, `duration_minutes`, `is_active`, `created_at` |
| 10 | `admission.test_questions` | Ngân hàng câu hỏi Listening, Reading, Grammar | `id`, `test_set_id`, `skill_type`, `order_index`, `audio_url`, `passage_text`, `question_text`, `option_a`, `option_b`, `option_c`, `option_d`, `correct_option`, `score_weight` |
| 11 | `admission.test_recommendation_rules` | Quy tắc ghép điểm đầu vào với khóa học đề xuất | `id`, `test_set_id`, `min_score`, `max_score`, `assessed_level`, `recommended_course_id`, `advice_text` |
| 12 | `admission.test_submissions` | Lưu kết quả, điểm từng kỹ năng và đáp án JSONB | `id`, `user_id`, `test_set_id`, `listening_score`, `reading_score`, `grammar_score`, `total_score`, `assessed_level`, `recommended_course_id`, `answers_detail`, `submitted_at` |

**Quy ước:** Dữ liệu của `admission` được phân tách khỏi schema `student`, `learning`, `finance`. ID dùng để tích hợp liên service cần được kiểm soát ở tầng ứng dụng.

## 3. Toàn văn SQL khởi tạo schema `admission`

Đoạn dưới đây được **trích nguyên văn** từ `admission-schema-spec.md` → mục **5. Toàn văn Kịch bản DDL PostgreSQL 16 Chuẩn Production**. Gồm `CREATE SCHEMA`, 12 lệnh `CREATE TABLE`, và các lệnh `CREATE INDEX`. Không bao gồm dữ liệu seed (mục 6) vì dữ liệu mẫu không phải cấu trúc schema.

```sql
-- ============================================================================
-- DDL SCRIPT: ADMISSION & IDENTITY SERVICE (PostgreSQL 16)
-- ============================================================================

-- 1. Khởi tạo Schema
CREATE SCHEMA IF NOT EXISTS admission;

-- 2. Bảng Người dùng & Phân quyền
CREATE TABLE admission.users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL CHECK (role IN ('ADMIN', 'STAFF', 'TEACHER', 'STUDENT')),
    phone VARCHAR(50),
    gender VARCHAR(20) CHECK (gender IN ('MALE', 'FEMALE', 'OTHER')),
    date_of_birth DATE,
    avatar_url TEXT,
    must_change_password BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 3. Bảng Refresh Token
CREATE TABLE admission.refresh_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES admission.users(id) ON DELETE CASCADE,
    token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    is_revoked BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 4. Bảng Đặt lại Mật khẩu qua Email
CREATE TABLE admission.password_reset_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES admission.users(id) ON DELETE CASCADE,
    token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    is_used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 5. Bảng Nhật ký Kiểm toán Đăng nhập & Bảo mật
CREATE TABLE admission.auth_audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES admission.users(id) ON DELETE SET NULL,
    action VARCHAR(50) NOT NULL CHECK (action IN ('LOGIN_SUCCESS', 'LOGIN_FAILED', 'REFRESH_TOKEN', 'LOGOUT', 'PASSWORD_CHANGED', 'ACCOUNT_LOCKED')),
    ip_address VARCHAR(50),
    user_agent TEXT,
    details TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 6. Bảng Danh mục Phòng học
CREATE TABLE admission.rooms (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    capacity INTEGER NOT NULL CHECK (capacity > 0),
    branch_name VARCHAR(100) DEFAULT 'Cơ sở chính',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 7. Bảng Khóa học & Lộ trình Đào tạo
CREATE TABLE admission.courses (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    level VARCHAR(50) NOT NULL CHECK (level IN ('Beginner', 'Intermediate', 'Advanced')),
    target_output VARCHAR(100),
    duration_weeks INTEGER NOT NULL CHECK (duration_weeks > 0),
    tuition_amount NUMERIC(12, 2) NOT NULL CHECK (tuition_amount >= 0),
    prerequisite_course_id INTEGER REFERENCES admission.courses(id) ON DELETE SET NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 8. Bảng Lớp học & Thời khóa biểu
CREATE TABLE admission.classes (
    id SERIAL PRIMARY KEY,
    course_id INTEGER NOT NULL REFERENCES admission.courses(id) ON DELETE RESTRICT,
    room_id INTEGER REFERENCES admission.rooms(id) ON DELETE RESTRICT,
    teacher_id INTEGER REFERENCES admission.users(id) ON DELETE RESTRICT,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    day_pattern VARCHAR(50) NOT NULL CHECK (day_pattern IN ('MON_WED_FRI', 'TUE_THU_SAT', 'SAT_SUN', 'DAILY', 'CUSTOM')),
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    min_students INTEGER DEFAULT 10 CHECK (min_students > 0),
    max_students INTEGER DEFAULT 25 CHECK (max_students >= min_students),
    status VARCHAR(50) DEFAULT 'OPEN' CHECK (status IN ('OPEN', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED')),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 9. Bảng Tuyển sinh & Giữ chỗ 48h
CREATE TABLE admission.enrollments (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES admission.users(id) ON DELETE RESTRICT,
    class_id INTEGER NOT NULL REFERENCES admission.classes(id) ON DELETE RESTRICT,
    status VARCHAR(50) DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'APPROVED', 'REJECTED', 'EXPIRED', 'CANCELLED', 'CANCELLED_REFUND_PENDING')),
    hold_expires_at TIMESTAMPTZ,
    invoice_code VARCHAR(50),
    source VARCHAR(50) DEFAULT 'ONLINE' CHECK (source IN ('ONLINE', 'WALK_IN', 'HOTLINE', 'FANPAGE', 'REFERRAL')),
    approval_method VARCHAR(50) CHECK (approval_method IN ('ONLINE_PAYMENT', 'MANUAL_CASH', 'STAFF_OVERRIDE')),
    approved_by_user_id INTEGER REFERENCES admission.users(id),
    note TEXT,
    enrolled_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    approved_at TIMESTAMPTZ
);

-- 10. Bảng Đề thi Khảo thí Đầu vào
CREATE TABLE admission.test_sets (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    duration_minutes INTEGER NOT NULL DEFAULT 45 CHECK (duration_minutes > 0),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 11. Bảng Câu hỏi Khảo thí 3 Kỹ năng
CREATE TABLE admission.test_questions (
    id SERIAL PRIMARY KEY,
    test_set_id INTEGER NOT NULL REFERENCES admission.test_sets(id) ON DELETE CASCADE,
    skill_type VARCHAR(50) NOT NULL CHECK (skill_type IN ('LISTENING', 'READING', 'GRAMMAR')),
    order_index INTEGER NOT NULL DEFAULT 1,
    audio_url TEXT,
    passage_text TEXT,
    question_text TEXT NOT NULL,
    option_a TEXT NOT NULL,
    option_b TEXT NOT NULL,
    option_c TEXT NOT NULL,
    option_d TEXT NOT NULL,
    correct_option CHAR(1) NOT NULL CHECK (correct_option IN ('A', 'B', 'C', 'D')),
    score_weight NUMERIC(4, 2) DEFAULT 1.0 CHECK (score_weight > 0)
);

-- 12. Bảng Ma trận Quy đổi Điểm sang Khóa học Khuyến nghị
CREATE TABLE admission.test_recommendation_rules (
    id SERIAL PRIMARY KEY,
    test_set_id INTEGER NOT NULL REFERENCES admission.test_sets(id) ON DELETE CASCADE,
    min_score NUMERIC(5, 2) NOT NULL,
    max_score NUMERIC(5, 2) NOT NULL,
    assessed_level VARCHAR(50) NOT NULL,
    recommended_course_id INTEGER NOT NULL REFERENCES admission.courses(id) ON DELETE CASCADE,
    advice_text TEXT
);

-- 13. Bảng Kết quả Làm bài Test Đầu vào
CREATE TABLE admission.test_submissions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES admission.users(id) ON DELETE CASCADE,
    test_set_id INTEGER NOT NULL REFERENCES admission.test_sets(id) ON DELETE RESTRICT,
    listening_score NUMERIC(5, 2) DEFAULT 0.0,
    reading_score NUMERIC(5, 2) DEFAULT 0.0,
    grammar_score NUMERIC(5, 2) DEFAULT 0.0,
    total_score NUMERIC(5, 2) NOT NULL,
    assessed_level VARCHAR(50),
    recommended_course_id INTEGER REFERENCES admission.courses(id),
    answers_detail JSONB,
    submitted_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 14. Chỉ mục Tối ưu Hiệu năng (Indexes)
CREATE INDEX idx_classes_schedule ON admission.classes (room_id, teacher_id, day_pattern, start_date, end_date);
CREATE INDEX idx_enrollments_status_hold ON admission.enrollments (class_id, status, hold_expires_at);
CREATE INDEX idx_audit_user_created ON admission.auth_audit_logs (user_id, created_at);
CREATE INDEX idx_test_questions_set_skill ON admission.test_questions (test_set_id, skill_type, order_index);
```

## 4. Tài liệu đã đối chiếu

- `admission-ba-bi-spec.md`: đặc tả nghiệp vụ, 30 yêu cầu chức năng, mô tả BI.
- `admission-schema-spec.md`: tên bảng, cột, kiểu dữ liệu và SQL DDL chuẩn của schema.
- `admission-tech-spec.md`: kiến trúc và cách hiện thực kỹ thuật.
- `admission-uml-spec.md`: use case, mô hình lớp và các luồng xử lý.

**Lưu ý sử dụng:** Đây là phần trích xuất/tổng hợp theo tài liệu thiết kế, chưa đối chiếu trực tiếp với `scripts/init-db.sql` hoặc CSDL đang chạy.

-- ========================================================
-- Database Initialization: English Center Management
-- Creates 4 isolated schemas corresponding to 4 microservices
-- ========================================================

-- 1. Create Schemas
CREATE SCHEMA IF NOT EXISTS admission;
CREATE SCHEMA IF NOT EXISTS student;
CREATE SCHEMA IF NOT EXISTS learning;
CREATE SCHEMA IF NOT EXISTS finance;

-- ========================================================
-- SCHEMA: ADMISSION
-- Quản lý tài khoản người dùng, khóa học, lớp học và tuyển sinh
-- ========================================================

CREATE TABLE IF NOT EXISTS admission.users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL CHECK (role IN ('ADMIN', 'STAFF', 'TEACHER', 'STUDENT')),
    phone VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS admission.courses (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    level VARCHAR(50), -- e.g. Beginner, Intermediate, Advanced
    duration_weeks INTEGER DEFAULT 12,
    tuition_amount NUMERIC(12, 2) DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS admission.classes (
    id SERIAL PRIMARY KEY,
    course_id INTEGER NOT NULL REFERENCES admission.courses(id) ON DELETE CASCADE,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    room VARCHAR(100),
    teacher_name VARCHAR(255),
    schedule VARCHAR(255), -- e.g. "T2-T4-T6 18:00 - 20:00"
    start_date DATE,
    end_date DATE,
    max_students INTEGER DEFAULT 25,
    status VARCHAR(50) DEFAULT 'OPEN' CHECK (status IN ('OPEN', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS admission.enrollments (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL, -- references student.students(id) logically
    class_id INTEGER NOT NULL REFERENCES admission.classes(id) ON DELETE CASCADE,
    status VARCHAR(50) DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'APPROVED', 'REJECTED', 'CANCELLED')),
    enrolled_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ========================================================
-- SCHEMA: STUDENT
-- Quản lý hồ sơ học viên, điểm danh
-- ========================================================

CREATE TABLE IF NOT EXISTS student.students (
    id SERIAL PRIMARY KEY,
    user_id INTEGER, -- Optional link to admission.users(id)
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(50),
    date_of_birth DATE,
    address TEXT,
    status VARCHAR(50) DEFAULT 'STUDYING' CHECK (status IN ('STUDYING', 'RESERVED', 'DROPPED', 'GRADUATED')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS student.attendance (
    id SERIAL PRIMARY KEY,
    class_id INTEGER NOT NULL,
    student_id INTEGER NOT NULL REFERENCES student.students(id) ON DELETE CASCADE,
    session_date DATE NOT NULL,
    status VARCHAR(50) DEFAULT 'PRESENT' CHECK (status IN ('PRESENT', 'ABSENT', 'LATE', 'EXCUSED')),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ========================================================
-- SCHEMA: LEARNING
-- Quản lý học liệu, bài tập, điểm số
-- ========================================================

CREATE TABLE IF NOT EXISTS learning.materials (
    id SERIAL PRIMARY KEY,
    class_id INTEGER NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    material_type VARCHAR(50) DEFAULT 'DOCUMENT' CHECK (material_type IN ('DOCUMENT', 'VIDEO', 'EXERCISE', 'SLIDE')),
    file_url TEXT,
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS learning.grades (
    id SERIAL PRIMARY KEY,
    class_id INTEGER NOT NULL,
    student_id INTEGER NOT NULL,
    assessment_name VARCHAR(255) NOT NULL, -- Midterm, Final, Speaking, Quiz
    score NUMERIC(5, 2) NOT NULL,
    max_score NUMERIC(5, 2) DEFAULT 100.0,
    feedback TEXT,
    graded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ========================================================
-- SCHEMA: FINANCE
-- Quản lý học phí, hóa đơn, thanh toán
-- ========================================================


CREATE SCHEMA IF NOT EXISTS finance;

CREATE TABLE IF NOT EXISTS finance.tuition_fees (
    id SERIAL PRIMARY KEY,
    course_id INTEGER NOT NULL UNIQUE,
    amount NUMERIC(12, 2) NOT NULL CHECK (amount > 0),
    currency VARCHAR(10) NOT NULL DEFAULT 'VND',
    discount_code VARCHAR(50),
    discount_amount NUMERIC(12, 2) NOT NULL DEFAULT 0 CHECK (discount_amount >= 0),
    note TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS finance.invoices (
    id SERIAL PRIMARY KEY,
    invoice_code VARCHAR(50) NOT NULL UNIQUE,
    student_id INTEGER NOT NULL,
    enrollment_id INTEGER,
    tuition_fee_id INTEGER REFERENCES finance.tuition_fees(id) ON DELETE SET NULL,
    amount NUMERIC(12, 2) NOT NULL CHECK (amount > 0),
    status VARCHAR(20) NOT NULL DEFAULT 'UNPAID' 
        CHECK (status IN ('UNPAID', 'PAID', 'CANCELLED', 'OVERDUE')),
    due_date DATE NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS finance.payments (
    id SERIAL PRIMARY KEY,
    invoice_id INTEGER NOT NULL REFERENCES finance.invoices(id) ON DELETE CASCADE,
    amount NUMERIC(12, 2) NOT NULL CHECK (amount > 0),
    payment_method VARCHAR(30) NOT NULL 
        CHECK (payment_method IN ('CASH', 'BANK_TRANSFER')),
    transaction_ref VARCHAR(100) NOT NULL UNIQUE, -- Chống lặp giao dịch (INV-FIN-03)
    paid_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
-- ========================================================
-- SEED INITIAL DATA (Dữ liệu mẫu cho Demo MVP)
-- ========================================================

-- Mật khẩu mặc định đều là '123456' hoặc tương ứng
-- (Dùng plaintext hoặc simple hash để dễ test ban đầu)
INSERT INTO admission.users (email, password_hash, full_name, role, phone)
VALUES 
    ('admin@english.edu.vn', 'admin123', 'Quản Trị Viên', 'ADMIN', '0901234567'),
    ('staff@english.edu.vn', 'staff123', 'Nguyễn Thị Học Vụ', 'STAFF', '0902345678'),
    ('teacher@english.edu.vn', 'teacher123', 'Thầy John Smith', 'TEACHER', '0903456789'),
    ('student@english.edu.vn', 'student123', 'Trần Văn Nam', 'STUDENT', '0904567890')
ON CONFLICT (email) DO NOTHING;

INSERT INTO admission.courses (code, name, description, level, duration_weeks, tuition_amount)
VALUES 
    ('ENG-IELTS-FOUND', 'IELTS Foundation 4.5 - 5.5', 'Xây dựng nền tảng ngữ pháp, từ vựng và 4 kỹ năng cơ bản.', 'Intermediate', 12, 6500000),
    ('ENG-IELTS-INT', 'IELTS Intensive 6.5+', 'Luyện đề chuyên sâu và chiến thuật làm bài thi thật.', 'Advanced', 14, 8500000),
    ('ENG-TOEIC-600', 'TOEIC Cấp Tốc 600+', 'Ôn thi TOEIC nghe đọc cấp tốc chuẩn format ETS.', 'Intermediate', 8, 4200000),
    ('ENG-COMM-BAS', 'Tiếng Anh Giao Tiếp Phản Xạ', 'Rèn luyện phát âm chuẩn IPA và tự tin giao tiếp hàng ngày.', 'Beginner', 10, 3800000)
ON CONFLICT (code) DO NOTHING;

INSERT INTO admission.classes (course_id, code, name, room, teacher_name, schedule, start_date, end_date, max_students, status)
VALUES 
    (1, 'CLS-IELTS-01', 'IELTS Foundation K28', 'Phòng 201 - Cơ sở 1', 'Mr. John Smith', 'T2-T4-T6 (18:00 - 19:30)', '2026-11-01', '2027-01-25', 20, 'OPEN'),
    (2, 'CLS-IELTS-02', 'IELTS Intensive K15', 'Phòng 302 - Cơ sở 1', 'Ms. Sarah Connor', 'T3-T5-T7 (19:30 - 21:00)', '2026-11-05', '2027-02-15', 18, 'OPEN'),
    (3, 'CLS-TOEIC-01', 'TOEIC 600+ Tối', 'Phòng 102 - Cơ sở 2', 'Thầy Lê Hoàng', 'T2-T4-T6 (19:30 - 21:00)', '2026-11-10', '2027-01-10', 25, 'OPEN')
ON CONFLICT (code) DO NOTHING;

INSERT INTO student.students (user_id, full_name, email, phone, date_of_birth, address, status)
VALUES 
    (4, 'Trần Văn Nam', 'student@english.edu.vn', '0904567890', '2004-05-15', '123 Cầu Giấy, Hà Nội', 'STUDYING'),
    (NULL, 'Lê Thị Mai', 'mai.le@gmail.com', '0912334455', '2003-08-20', '45 Đống Đa, Hà Nội', 'STUDYING'),
    (NULL, 'Phạm Quốc Bảo', 'bao.pham@gmail.com', '0987654321', '2002-11-10', '88 Hai Bà Trưng, Hà Nội', 'STUDYING')
ON CONFLICT DO NOTHING;

INSERT INTO admission.enrollments (student_id, class_id, status)
VALUES 
    (1, 1, 'APPROVED'),
    (2, 1, 'APPROVED'),
    (3, 2, 'PENDING')
ON CONFLICT DO NOTHING;

-- ========================================================
-- SCHEMA: FINANCE - SEED DATA
-- ========================================================

-- 1. Thêm dữ liệu biểu phí và voucher cho các khóa học
INSERT INTO finance.tuition_fees (course_id, amount, currency, discount_code, discount_amount, note)
VALUES 
    (1, 6500000, 'VND', 'EARLYBIRD500', 500000, 'Giảm 500k cho học viên đăng ký sớm khóa IELTS Foundation'),
    (2, 8500000, 'VND', 'VIPSTUDENT', 1000000, 'Học bổng ưu đãi khóa IELTS Intensive'),
    (3, 4200000, 'VND', NULL, 0, 'Mức học phí chuẩn TOEIC Cấp Tốc'),
    (4, 3800000, 'VND', 'SUMMER2026', 300000, 'Chương trình ưu đãi hè Tiếng Anh Giao Tiếp')
ON CONFLICT (course_id) DO NOTHING;

-- 2. Thêm dữ liệu hóa đơn (có liên kết tuition_fee_id tương ứng)
INSERT INTO finance.invoices (invoice_code, student_id, enrollment_id, tuition_fee_id, amount, status, due_date)
VALUES 
    ('INV-2026-001', 1, 1, 1, 6000000, 'PAID', '2026-11-05'),     -- Áp dụng biểu phí ID 1 (6.5tr - 500k giảm giá = 6tr)
    ('INV-2026-002', 2, 2, 1, 6000000, 'UNPAID', '2026-11-05'),   -- Áp dụng biểu phí ID 1
    ('INV-2026-003', 3, 3, 2, 7500000, 'UNPAID', '2026-11-10')    -- Áp dụng biểu phí ID 2 (8.5tr - 1tr giảm giá = 7.5tr)
ON CONFLICT (invoice_code) DO NOTHING;

-- 3. Thêm dữ liệu giao dịch thanh toán cho hóa đơn đã nộp đủ
INSERT INTO finance.payments (invoice_id, amount, payment_method, transaction_ref)
VALUES 
    (1, 6000000, 'BANK_TRANSFER', 'FT261015998811')
ON CONFLICT DO NOTHING;

INSERT INTO learning.materials (class_id, title, description, material_type, file_url)
VALUES 
    (1, 'Giáo trình IELTS Foundation Unit 1-4', 'Slide và bài tập từ vựng chủ đề Daily Routine', 'DOCUMENT', 'https://example.com/materials/ielts-u1-4.pdf'),
    (1, 'Audio luyện nghe Cambridge Practice Test 1', 'File nghe định dạng MP3 cho bài tập về nhà', 'DOCUMENT', 'https://example.com/materials/listening-test1.mp3')
ON CONFLICT DO NOTHING;

INSERT INTO learning.grades (class_id, student_id, assessment_name, score, max_score, feedback)
VALUES 
    (1, 1, 'Midterm Test (Reading & Listening)', 82.5, 100.0, 'Kỹ năng nghe tốt, cần chú ý phần Matching Headings.'),
    (1, 2, 'Midterm Test (Reading & Listening)', 78.0, 100.0, 'Cần cải thiện từ vựng học thuật.')
ON CONFLICT DO NOTHING;

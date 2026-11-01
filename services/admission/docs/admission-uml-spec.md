# ĐẶC TẢ THIẾT KẾ MÔ HÌNH HÓA UML (UML DESIGN SPECIFICATION)
## PHÂN HỆ ĐỊNH DANH, TUYỂN SINH & ĐÀO TẠO (ADMISSION & IDENTITY SERVICE)

> **Dự án**: Hệ thống Quản lý Trung tâm Anh ngữ  
> **Dịch vụ**: `admission-service` (Spring Boot 3.3.4, Java 21, PostgreSQL 16)  
> **Tài liệu căn cứ SSOT**:  
> - [admission-ba-bi-spec.md](file:///run/media/tamdae/04C8A69DC8A68C8C/Users/LENOVO/Documents/TL_Kỳ_1_năm_4/Software_Engineering/services/admission/docs/admission-ba-bi-spec.md) (Nghiệp vụ & BI)  
> - [admission-tech-spec.md](file:///run/media/tamdae/04C8A69DC8A68C8C/Users/LENOVO/Documents/TL_Kỳ_1_năm_4/Software_Engineering/services/admission/docs/admission-tech-spec.md) (Kiến trúc Kỹ thuật)  
> - [admission-schema-spec.md](file:///run/media/tamdae/04C8A69DC8A68C8C/Users/LENOVO/Documents/TL_Kỳ_1_năm_4/Software_Engineering/services/admission/docs/admission-schema-spec.md) (Cơ sở Dữ liệu)  
> **Phiên bản**: 1.0 (Master UML Modeling)  
> **Ngày phê duyệt**: 2026-10-28  

---

## MỤC LỤC
1. [Tổng quan Mô hình hóa Hệ thống (System Modeling Overview)](#1-tổng-quan-mô-hình-hóa-hệ-thống-system-modeling-overview)
2. [Biểu đồ Ca sử dụng (UML Use Case Diagrams)](#2-biểu-đồ-ca-sử-dụng-uml-use-case-diagrams)
   - 2.1. Biểu đồ Ca sử dụng Tổng quan Toàn phân hệ
   - 2.2. Phân hệ Định danh & Phân quyền (IAM Use Cases)
   - 2.3. Phân hệ Cơ sở vật chất & Lớp học (Academic & Facility Use Cases)
   - 2.4. Phân hệ Khảo thí Đầu vào (Online Placement Test Use Cases)
   - 2.5. Phân hệ Tuyển sinh & Giữ chỗ 48h (Enrollment & Slot Holding Use Cases)
   - 2.6. Đặc tả Chi tiết các Ca sử dụng Trọng yếu (Detailed Use Case Specifications)
3. [Biểu đồ Lớp (UML Class Diagrams)](#3-biểu-đồ-lớp-uml-class-diagrams)
   - 3.1. Biểu đồ Lớp Thực thể Miền Nghiệp vụ (Domain Model Class Diagram)
   - 3.2. Biểu đồ Lớp Kiến trúc 3 Tầng (Controller - Service - Repository Architecture)
   - 3.3. Biểu đồ Lớp Động cơ Chống Xung đột Lịch (Conflict Engine Class Diagram)
   - 3.4. Biểu đồ Lớp Hạ tầng Bảo mật & JWT (Security & Filter Chain Class Diagram)
4. [Biểu đồ Tuần tự (UML Sequence Diagrams)](#4-biểu-đồ-tuần-tự-uml-sequence-diagrams)
   - 4.1. Xác thực Đăng nhập & Cấp phát JWT Kép
   - 4.2. Mở Lớp học & Thuật toán Quét Xung đột Lịch
   - 4.3. Khảo thí Trực tuyến 3 Kỹ năng & Tự động Đề xuất Khóa học
   - 4.4. Đăng ký Nhập học, Giữ chỗ 48h & Bắt tay Thanh toán Liên Service
   - 4.5. Tác vụ Quét Nền Thu hồi Slot Quá hạn 48h
5. [Biểu đồ Máy Trạng thái (UML State Machine Diagrams)](#5-biểu-đồ-máy-trạng-thái-uml-state-machine-diagrams)
   - 5.1. Vòng đời Đơn Đăng ký Tuyển sinh (Enrollment Lifecycle)
   - 5.2. Vòng đời Lớp học (Class Lifecycle)
6. [Biểu đồ Hoạt động (UML Activity Diagrams)](#6-biểu-đồ-hoạt-động-uml-activity-diagrams)
   - 6.1. Hoạt động: Thuật toán Kiểm tra Xung đột Lịch Phòng học & Giáo viên
   - 6.2. Hoạt động: Chấm điểm & Quy đổi Lộ trình Khảo thí
7. [Ma trận Truy vết Yêu cầu sang Thiết kế (Requirements Traceability Matrix)](#7-ma-trận-truy-vết-yêu-cầu-sang-thiết-kế-requirements-traceability-matrix)

---

## 1. Tổng quan Mô hình hóa Hệ thống (System Modeling Overview)

Tài liệu này chuẩn hóa toàn bộ các khía cạnh phân tích và thiết kế phần mềm cho **`admission-service`** theo chuẩn ngôn ngữ mô hình hóa **UML 2.5 (Unified Modeling Language)**.

### Các tác nhân hệ thống (Actors):
- **`GUEST` (Khách vãng lai)**: Người quan tâm muốn tra cứu khóa học hoặc làm bài kiểm tra năng lực đầu vào.
- **`STUDENT` (Học viên)**: Người dùng có tài khoản, thực hiện nộp đơn đăng ký lớp học, làm bài test và theo dõi hạn đóng phí.
- **`TEACHER` (Giáo viên)**: Người dùng xem thời khóa biểu các lớp được phân công giảng dạy.
- **`STAFF` (Nhân viên Học vụ / Tuyển sinh)**: Mở lớp học, xếp phòng/giáo viên, tiếp nhận đăng ký tại quầy, duyệt tiền mặt và gia hạn giữ chỗ.
- **`ADMIN` (Quản trị viên)**: Quản trị tài khoản nhân sự, danh mục phòng học, khóa học, ngân hàng đề thi và theo dõi BI Dashboard.
- **`SYSTEM_CRON` (Bộ lập lịch hệ thống)**: Tác nhân tự động kích hoạt các Scheduled Background Jobs (quét 48h, dọn dẹp token).
- **`FINANCE_SERVICE` & `STUDENT_SERVICE`**: Các tác nhân hệ thống ngoài (External Services) giao tiếp qua REST API.

---

## 2. Biểu đồ Ca sử dụng (UML Use Case Diagrams)

### 2.1. Biểu đồ Ca sử dụng Tổng quan Toàn phân hệ

```mermaid
flowchart LR
    classDef actor fill:#f8fafc,stroke:#2563eb,stroke-width:2px;
    classDef usecase fill:#eff6ff,stroke:#1d4ed8,stroke-width:1px;
    classDef boundary fill:#ffffff,stroke:#64748b,stroke-width:2px,stroke-dasharray: 5 5;

    Guest["fa:fa-user Guest"]:::actor
    Student["fa:fa-user-graduate Student"]:::actor
    Staff["fa:fa-user-tie Staff"]:::actor
    Admin["fa:fa-user-shield Admin"]:::actor
    Cron["fa:fa-clock System Cron"]:::actor
    Finance["fa:fa-server Finance Service"]:::actor

    subgraph SystemBoundary ["Phân hệ Admission & Identity Service"]
        UC_Auth(["Quản lý Định danh & Phiên"]):::usecase
        UC_Facility(["Quản lý Phòng học & Lớp"]):::usecase
        UC_Test(["Khảo thí Năng lực Đầu vào"]):::usecase
        UC_Enroll(["Tuyển sinh & Giữ chỗ 48h"]):::usecase
        UC_BI(["Xem Báo cáo BI Tuyển sinh"]):::usecase
        UC_AutoExpire(["Quét Thu hồi Slot Quá hạn"]):::usecase
    end

    Guest --> UC_Test
    Guest --> UC_Auth

    Student --> UC_Auth
    Student --> UC_Test
    Student --> UC_Enroll

    Staff --> UC_Auth
    Staff --> UC_Facility
    Staff --> UC_Enroll
    Staff --> UC_BI

    Admin --> UC_Auth
    Admin --> UC_Facility
    Admin --> UC_Test
    Admin --> UC_Enroll
    Admin --> UC_BI

    Cron --> UC_AutoExpire
    Finance --> UC_Enroll
```

---

### 2.2. Phân hệ Định danh & Phân quyền (IAM Use Cases)

```mermaid
flowchart LR
    classDef actor fill:#f8fafc,stroke:#2563eb,stroke-width:2px;
    classDef usecase fill:#eff6ff,stroke:#1d4ed8,stroke-width:1px;

    User["Người dùng chung"]:::actor
    Admin["Quản trị viên"]:::actor

    subgraph IAM_Boundary ["Khối Quản trị Định danh & Truy cập (IAM)"]
        UC_Login(["Đăng nhập hệ thống"]):::usecase
        UC_Refresh(["Làm mới JWT Token"]):::usecase
        UC_Logout(["Đăng xuất"]):::usecase
        UC_Forgot(["Quên mật khẩu"]):::usecase
        UC_Reset(["Đặt lại mật khẩu qua Email"]):::usecase
        UC_Profile(["Xem hồ sơ cá nhân"]):::usecase
        UC_ChangePass(["Đổi mật khẩu chủ động"]):::usecase
        
        UC_ManageUser(["Quản lý Nhân sự (CRUD Staff/Teacher)"]):::usecase
        UC_LockUser(["Khóa / Mở khóa Tài khoản"]):::usecase
        UC_Audit(["Xem Nhật ký Kiểm toán (Audit Logs)"]):::usecase
        UC_RecordAudit(["Ghi nhận Vết An ninh"]):::usecase
    end

    User --> UC_Login
    User --> UC_Refresh
    User --> UC_Logout
    User --> UC_Forgot
    User --> UC_Reset
    User --> UC_Profile
    User --> UC_ChangePass

    Admin --> UC_ManageUser
    Admin --> UC_LockUser
    Admin --> UC_Audit

    UC_Login -.->|<<include>>| UC_RecordAudit
    UC_ChangePass -.->|<<include>>| UC_RecordAudit
    UC_LockUser -.->|<<include>>| UC_RecordAudit
```

---

### 2.3. Phân hệ Cơ sở vật chất & Lớp học (Academic & Facility Use Cases)

```mermaid
flowchart LR
    classDef actor fill:#f8fafc,stroke:#2563eb,stroke-width:2px;
    classDef usecase fill:#eff6ff,stroke:#1d4ed8,stroke-width:1px;

    Staff["Nhân viên Học vụ"]:::actor
    Admin["Quản trị viên"]:::actor

    subgraph Academic_Boundary ["Khối Cơ sở vật chất & Đào tạo"]
        UC_Room(["Quản lý Danh mục Phòng học"]):::usecase
        UC_Course(["Quản lý Khóa học & Lộ trình"]):::usecase
        UC_CreateClass(["Mở Lớp học mới"]):::usecase
        UC_CheckConflict(["Kiểm tra Xung đột Lịch Phòng & GV"]):::usecase
        UC_CancelClass(["Hủy lớp thiếu Sĩ số"]):::usecase
        UC_ExportClass(["Xuất danh sách học viên Lớp ra Excel/CSV"]):::usecase
    end

    Admin --> UC_Room
    Admin --> UC_Course
    Staff --> UC_CreateClass
    Staff --> UC_CancelClass
    Staff --> UC_ExportClass

    UC_CreateClass -.->|<<include>>| UC_CheckConflict
```

---

### 2.4. Phân hệ Khảo thí Đầu vào (Online Placement Test Use Cases)

```mermaid
flowchart LR
    classDef actor fill:#f8fafc,stroke:#2563eb,stroke-width:2px;
    classDef usecase fill:#eff6ff,stroke:#1d4ed8,stroke-width:1px;

    Student["Học viên / Vãng lai"]:::actor
    Staff["Nhân viên Học vụ"]:::actor
    Admin["Quản trị viên"]:::actor

    subgraph Test_Boundary ["Khối Khảo thí Trực tuyến (Placement Test)"]
        UC_ViewTest(["Xem danh sách Bộ đề thi"]):::usecase
        UC_TakeTest(["Làm bài thi trắc nghiệm (Timer đếm ngược)"]):::usecase
        UC_SubmitTest(["Nộp bài thi"]):::usecase
        UC_AutoGrade(["Chấm điểm tự động 3 kỹ năng"]):::usecase
        UC_RecommendCourse(["Tự động gợi ý Khóa học phù hợp"]):::usecase
        UC_ManageBank(["Quản lý Ngân hàng đề thi & Ma trận điểm"]):::usecase
        UC_ExportTest(["Xuất kết quả khảo thí ra Excel"]):::usecase
    end

    Student --> UC_ViewTest
    Student --> UC_TakeTest
    Student --> UC_SubmitTest

    Admin --> UC_ManageBank
    Staff --> UC_ExportTest

    UC_SubmitTest -.->|<<include>>| UC_AutoGrade
    UC_AutoGrade -.->|<<include>>| UC_RecommendCourse
```

---

### 2.5. Phân hệ Tuyển sinh & Giữ chỗ 48h (Enrollment & Slot Holding Use Cases)

```mermaid
flowchart LR
    classDef actor fill:#f8fafc,stroke:#2563eb,stroke-width:2px;
    classDef usecase fill:#eff6ff,stroke:#1d4ed8,stroke-width:1px;

    Student["Học viên"]:::actor
    Staff["Nhân viên Học vụ"]:::actor
    Finance["Finance Service"]:::actor
    Cron["System Cron"]:::actor

    subgraph Enrollment_Boundary ["Khối Tuyển sinh & Quản lý Sĩ số"]
        UC_SelfEnroll(["Đăng ký Lớp học trực tuyến"]):::usecase
        UC_StaffEnroll(["Tiếp nhận Đăng ký tại quầy"]):::usecase
        UC_Hold48h(["Giữ slot 48h & Tạo hóa đơn PENDING"]):::usecase
        UC_ExtendHold(["Gia hạn thời gian Giữ chỗ"]):::usecase
        UC_ApproveCash(["Duyệt thu Tiền mặt tại quầy"]):::usecase
        UC_CallbackPaid(["Nhận Callback Thanh toán Thành công"]):::usecase
        UC_SyncStudent(["Đồng bộ Hồ sơ sang Student Service"]):::usecase
        UC_AutoExpire(["Quét Thu hồi Slot Quá hạn"]):::usecase
    end

    Student --> UC_SelfEnroll
    Staff --> UC_StaffEnroll
    Staff --> UC_ExtendHold
    Staff --> UC_ApproveCash
    Finance --> UC_CallbackPaid
    Cron --> UC_AutoExpire

    UC_SelfEnroll -.->|<<include>>| UC_Hold48h
    UC_StaffEnroll -.->|<<include>>| UC_Hold48h
    UC_CallbackPaid -.->|<<include>>| UC_SyncStudent
    UC_ApproveCash -.->|<<include>>| UC_SyncStudent
```

---

### 2.6. Đặc tả Chi tiết các Ca sử dụng Trọng yếu (Detailed Use Case Specifications)

#### Ca sử dụng 1: `UC-ENR-01` Đăng ký Nhập học & Giữ chỗ 48h
- **Tác nhân chính**: `STUDENT` hoặc `STAFF`.
- **Tiền điều kiện**: Lớp học mục tiêu đang có `status == 'OPEN'`.
- **Luồng sự kiện chính (Main Flow)**:
  1. Người dùng chọn lớp học và gửi yêu cầu đăng ký (`class_id`, `student_id`).
  2. Hệ thống bắt đầu transaction, khóa dòng lớp học (`FOR UPDATE`).
  3. Hệ thống tính toán slot trống khả dụng:  
     $$\text{Available Slots} = \text{max\_students} - \text{approved\_count} - \text{active\_held\_count}$$
  4. Nếu $\text{Available Slots} > 0$:
     - Tạo bản ghi `admission.enrollments` với `status = 'PENDING'`.
     - Gán thời hạn `hold_expires_at = CURRENT_TIMESTAMP + 48 HOURS`.
     - Gọi sang **Finance Service** (`POST /api/finance/invoices`) với số tiền `course.tuition_amount`.
     - Nhận về `invoice_code` và cập nhật vào đơn đăng ký.
     - Trả về mã đơn kèm thông tin chuyển khoản cho học viên.
- **Luồng ngoại lệ (Alternate Flows)**:
  - **3a. Hết chỗ (`Available Slots <= 0`)**: Hệ thống từ chối tiếp nhận, ném ngoại lệ `ADM_CLASS_FULL` (HTTP 400).
  - **4a. Finance Service tạm thời gián đoạn**: Đơn vẫn lưu `PENDING`, đưa thông điệp tạo hóa đơn vào hàng đợi retry.
- **Hậu điều kiện**: Slot giữ chỗ được bảo lưu 48h, sĩ số khả dụng của lớp giảm đi 1.

---

#### Ca sử dụng 2: `UC-ACA-02` Mở Lớp học & Chống Xung đột Lịch
- **Tác nhân chính**: `STAFF` hoặc `ADMIN`.
- **Tiền điều kiện**: Phòng học và Khóa học đã tồn tại trong hệ thống.
- **Luồng sự kiện chính (Main Flow)**:
  1. Học vụ nhập thông tin lớp: Khóa học, Phòng học, Giáo viên, Mẫu ngày (`day_pattern`), Giờ bắt đầu/kết thúc, Ngày bắt đầu/kết thúc, Sĩ số tối đa (`max_students`).
  2. Hệ thống kiểm tra: `max_students <= room.capacity`.
  3. Hệ thống quét tất cả các lớp đang mở (`OPEN`, `IN_PROGRESS`) tìm các lớp giao thoa thời gian (ngày, thứ, giờ).
  4. Xác nhận không có lớp nào trùng Phòng học và không có lớp nào trùng Giáo viên.
  5. Lưu lớp học mới với `status = 'OPEN'`.
- **Luồng ngoại lệ (Alternate Flows)**:
  - **2a. Sĩ số vượt sức chứa phòng**: Báo lỗi `ADM_ROOM_CAPACITY_EXCEEDED` (HTTP 400).
  - **4a. Trùng phòng học đã có lớp**: Báo lỗi `ADM_ROOM_CONFLICT` (HTTP 400).
  - **4b. Trùng giáo viên đã có lịch dạy**: Báo lỗi `ADM_TEACHER_CONFLICT` (HTTP 400).

---

## 3. Biểu đồ Lớp (UML Class Diagrams)

### 3.1. Biểu đồ Lớp Thực thể Miền Nghiệp vụ (Domain Model Class Diagram)

```mermaid
classDiagram
    class User {
        -Integer id
        -String email
        -String passwordHash
        -String fullName
        -UserRole role
        -String phone
        -Gender gender
        -LocalDate dateOfBirth
        -Boolean mustChangePassword
        -Boolean isActive
        -OffsetDateTime createdAt
        -OffsetDateTime updatedAt
    }

    class RefreshToken {
        -Integer id
        -Integer userId
        -String token
        -OffsetDateTime expiresAt
        -Boolean isRevoked
        -OffsetDateTime createdAt
        +isExpired() Boolean
    }

    class AuthAuditLog {
        -Integer id
        -Integer userId
        -String action
        -String ipAddress
        -String userAgent
        -String details
        -OffsetDateTime createdAt
    }

    class Room {
        -Integer id
        -String code
        -String name
        -Integer capacity
        -String branchName
        -Boolean isActive
        +hasCapacity(int students) Boolean
    }

    class Course {
        -Integer id
        -String code
        -String name
        -String description
        -CourseLevel level
        -String targetOutput
        -Integer durationWeeks
        -BigDecimal tuitionAmount
        -Integer prerequisiteCourseId
        -Boolean isActive
    }

    class ClassEntity {
        -Integer id
        -Integer courseId
        -Integer roomId
        -Integer teacherId
        -String code
        -String name
        -DayPattern dayPattern
        -LocalTime startTime
        -LocalTime endTime
        -LocalDate startDate
        -LocalDate endDate
        -Integer minStudents
        -Integer maxStudents
        -ClassStatus status
        +isTimeOverlap(ClassEntity other) Boolean
    }

    class Enrollment {
        -Integer id
        -Integer studentId
        -Integer classId
        -EnrollmentStatus status
        -OffsetDateTime holdExpiresAt
        -String invoiceCode
        -EnrollmentSource source
        -ApprovalMethod approvalMethod
        -Integer approvedByUserId
        -String note
        -OffsetDateTime enrolledAt
        -OffsetDateTime approvedAt
        +isHoldExpired() Boolean
        +canApprove() Boolean
    }

    class TestSet {
        -Integer id
        -String title
        -Integer durationMinutes
        -Boolean isActive
    }

    class TestQuestion {
        -Integer id
        -Integer testSetId
        -SkillType skillType
        -Integer orderIndex
        -String audioUrl
        -String passageText
        -String questionText
        -String optionA
        -String optionB
        -String optionC
        -String optionD
        -Character correctOption
        -BigDecimal scoreWeight
    }

    class TestRecommendationRule {
        -Integer id
        -Integer testSetId
        -BigDecimal minScore
        -BigDecimal maxScore
        -String assessedLevel
        -Integer recommendedCourseId
        -String adviceText
        +matches(BigDecimal score) Boolean
    }

    class TestSubmission {
        -Integer id
        -Integer userId
        -Integer testSetId
        -BigDecimal listeningScore
        -BigDecimal readingScore
        -BigDecimal grammarScore
        -BigDecimal totalScore
        -String assessedLevel
        -Integer recommendedCourseId
        -JsonNode answersDetail
        -OffsetDateTime submittedAt
    }

    User "1" --> "*" RefreshToken : owns
    User "1" --> "*" AuthAuditLog : logs
    User "1" --> "*" Enrollment : applies
    User "1" --> "*" TestSubmission : takes
    User "1" --> "*" ClassEntity : teaches
    Room "1" --> "*" ClassEntity : hosts
    Course "1" --> "*" ClassEntity : instantiates
    Course "0..1" --> "*" Course : prerequisite
    ClassEntity "1" --> "*" Enrollment : admits
    TestSet "1" --> "*" TestQuestion : contains
    TestSet "1" --> "*" TestRecommendationRule : defines
    TestSet "1" --> "*" TestSubmission : evaluated_by
    Course "1" --> "*" TestRecommendationRule : recommended_as
```

---

### 3.2. Biểu đồ Lớp Kiến trúc 3 Tầng (Controller - Service - Repository Architecture)

Minh họa kiến trúc phân tầng chuẩn của phân hệ Admission (áp dụng cho Khối Tuyển sinh `Enrollment`):

```mermaid
classDiagram
    class EnrollmentController {
        -EnrollmentService enrollmentService
        +createEnrollment(CreateEnrollmentRequest req) ResponseEntity~ApiResponse~
        +getEnrollments(String status, Integer classId, Pageable page) ResponseEntity~ApiResponse~
        +extendHoldSlot(Integer id, ExtendHoldRequest req) ResponseEntity~ApiResponse~
        +approveManual(Integer id, ApproveManualRequest req) ResponseEntity~ApiResponse~
        +paymentCallback(PaymentCallbackRequest req) ResponseEntity~ApiResponse~
    }

    class EnrollmentService {
        <<interface>>
        +createEnrollment(CreateEnrollmentDTO dto) EnrollmentResponseDTO
        +extendHoldSlot(Integer enrollmentId, int extraHours, String reason) void
        +approveManual(Integer enrollmentId, BigDecimal amount, String note) void
        +processPaymentCallback(Integer enrollmentId, String txRef) void
        +expireOverdueEnrollments() int
    }

    class EnrollmentServiceImpl {
        -EnrollmentRepository enrollmentRepository
        -ClassRepository classRepository
        -UserRepository userRepository
        -FinanceClient financeClient
        -StudentClient studentClient
        +createEnrollment(CreateEnrollmentDTO dto) EnrollmentResponseDTO
        +extendHoldSlot(Integer enrollmentId, int extraHours, String reason) void
        +approveManual(Integer enrollmentId, BigDecimal amount, String note) void
        +processPaymentCallback(Integer enrollmentId, String txRef) void
        +expireOverdueEnrollments() int
    }

    class EnrollmentRepository {
        <<interface>>
        +countByClassIdAndStatus(Integer classId, EnrollmentStatus status) int
        +countActiveHeldSlots(Integer classId, OffsetDateTime now) int
        +findExpiredPendingEnrollments(OffsetDateTime now) List~Enrollment~
    }

    class FinanceClient {
        <<interface>>
        +createInvoice(CreateInvoiceRequest req) InvoiceResponseDTO
        +cancelInvoice(String invoiceCode, String reason) void
    }

    class StudentClient {
        <<interface>>
        +createStudentProfile(CreateStudentProfileRequest req) StudentProfileDTO
    }

    EnrollmentController --> EnrollmentService
    EnrollmentService <|.. EnrollmentServiceImpl
    EnrollmentServiceImpl --> EnrollmentRepository
    EnrollmentServiceImpl --> FinanceClient
    EnrollmentServiceImpl --> StudentClient
```

---

### 3.3. Biểu đồ Lớp Động cơ Chống Xung đột Lịch (Conflict Engine Class Diagram)

```mermaid
classDiagram
    class ClassController {
        -ClassService classService
        +createClass(CreateClassRequest req) ResponseEntity~ApiResponse~
        +updateClass(Integer id, UpdateClassRequest req) ResponseEntity~ApiResponse~
    }

    class ClassService {
        <<interface>>
        +createClass(ClassDTO dto) ClassResponseDTO
        +updateClass(Integer id, ClassDTO dto) ClassResponseDTO
    }

    class ClassServiceImpl {
        -ClassRepository classRepository
        -ConflictEngine conflictEngine
        +createClass(ClassDTO dto) ClassResponseDTO
    }

    class ConflictEngine {
        -ClassRepository classRepository
        -RoomRepository roomRepository
        +validateClassSchedule(ClassScheduleDTO schedule, Integer excludeClassId) void
        -isDateOverlapping(LocalDate s1, LocalDate e1, LocalDate s2, LocalDate e2) Boolean
        -isDayPatternOverlapping(DayPattern p1, DayPattern p2) Boolean
        -isTimeOverlapping(LocalTime s1, LocalTime e1, LocalTime s2, LocalTime e2) Boolean
    }

    ClassController --> ClassService
    ClassService <|.. ClassServiceImpl
    ClassServiceImpl --> ConflictEngine
```

---

### 3.4. Biểu đồ Lớp Hạ tầng Bảo mật & JWT (Security & Filter Chain Class Diagram)

```mermaid
classDiagram
    class SecurityFilterChain {
        <<interface>>
    }

    class JwtAuthenticationFilter {
        -JwtTokenProvider jwtTokenProvider
        -CustomUserDetailsService userDetailsService
        #doFilterInternal(HttpServletRequest req, HttpServletResponse res, FilterChain chain) void
        -extractBearerToken(HttpServletRequest req) String
    }

    class JwtTokenProvider {
        -String jwtSecret
        -long accessTokenValidityMs
        +generateAccessToken(UserPrincipal principal) String
        +generateRefreshToken() String
        +validateToken(String token) Boolean
        +getUserIdFromToken(String token) Integer
        +getRoleFromToken(String token) String
    }

    class CustomUserDetailsService {
        -UserRepository userRepository
        +loadUserByUsername(String email) UserDetails
    }

    class UserPrincipal {
        -Integer id
        -String email
        -String role
        -Collection~GrantedAuthority~ authorities
        +getAuthorities() Collection
    }

    JwtAuthenticationFilter --> JwtTokenProvider
    JwtAuthenticationFilter --> CustomUserDetailsService
    CustomUserDetailsService ..> UserPrincipal
```

---

## 4. Biểu đồ Tuần tự (UML Sequence Diagrams)

### 4.1. Xác thực Đăng nhập & Cấp phát JWT Kép

```mermaid
sequenceDiagram
    autonumber
    actor Client as Web Frontend
    participant AuthCtrl as AuthController
    participant AuthSvc as AuthService
    participant UserRepo as UserRepository
    participant TokenRepo as RefreshTokenRepository
    participant AuditSvc as AuditLogService
    participant JwtProv as JwtTokenProvider

    Client->>AuthCtrl: POST /auth/login (email, password)
    AuthCtrl->>AuthSvc: authenticate(email, password)
    AuthSvc->>UserRepo: findByEmail(email)
    
    alt Người dùng không tồn tại hoặc sai mật khẩu
        UserRepo-->>AuthSvc: null / Wrong Hash
        AuthSvc->>AuditSvc: record(null, "LOGIN_FAILED", clientIp, "Sai thông tin")
        AuthSvc-->>AuthCtrl: throw AUTH_INVALID_CREDENTIALS (401)
        AuthCtrl-->>Client: 401 Unauthorized
    else Tài khoản bị khóa (is_active == false)
        AuthSvc-->>AuthCtrl: throw AUTH_ACCOUNT_LOCKED (403)
        AuthCtrl-->>Client: 403 Forbidden
    else Đăng nhập Thành công
        AuthSvc->>JwtProv: generateAccessToken(user)
        JwtProv-->>AuthSvc: access_token (15 mins)
        AuthSvc->>JwtProv: generateRefreshToken()
        JwtProv-->>AuthSvc: refresh_token (UUID)
        AuthSvc->>TokenRepo: save(refresh_token, expiresAt=+7d, isRevoked=false)
        AuthSvc->>AuditSvc: record(userId, "LOGIN_SUCCESS", clientIp, "OK")
        AuthSvc-->>AuthCtrl: AuthResponseDTO (access_token, refresh_token, user_info)
        AuthCtrl-->>Client: 200 OK (Tokens & User Data)
    end
```

---

### 4.2. Mở Lớp học & Thuật toán Quét Xung đột Lịch

```mermaid
sequenceDiagram
    autonumber
    actor Staff as Nhân viên Học vụ
    participant ClassCtrl as ClassController
    participant ClassSvc as ClassService
    participant ConflictEng as ConflictEngine
    participant RoomRepo as RoomRepository
    participant ClassRepo as ClassRepository

    Staff->>ClassCtrl: POST /api/admission/classes (payload lớp mới)
    ClassCtrl->>ClassSvc: createClass(dto)
    ClassSvc->>ConflictEng: validateClassSchedule(dto, excludeClassId=null)
    
    ConflictEng->>RoomRepo: findById(dto.roomId)
    RoomRepo-->>ConflictEng: Room (capacity)
    
    alt max_students > room.capacity
        ConflictEng-->>ClassSvc: throw ADM_ROOM_CAPACITY_EXCEEDED
        ClassSvc-->>ClassCtrl: 400 Bad Request
        ClassCtrl-->>Staff: Báo lỗi vượt sức chứa phòng
    end

    ConflictEng->>ClassRepo: findOverlappingClasses(startDate, endDate, startTime, endTime, dayPattern)
    ClassRepo-->>ConflictEng: List<ClassEntity> đang mở

    alt Trùng room_id với lớp khác
        ConflictEng-->>ClassSvc: throw ADM_ROOM_CONFLICT
        ClassSvc-->>ClassCtrl: 400 Bad Request
        ClassCtrl-->>Staff: Báo lỗi Phòng học đã có lớp học cùng giờ
    else Trùng teacher_id với lớp khác
        ConflictEng-->>ClassSvc: throw ADM_TEACHER_CONFLICT
        ClassSvc-->>ClassCtrl: 400 Bad Request
        ClassCtrl-->>Staff: Báo lỗi Giáo viên đã có lịch dạy cùng giờ
    else Lịch học Hợp lệ 100%
        ConflictEng-->>ClassSvc: Validation OK
        ClassSvc->>ClassRepo: save(new ClassEntity(status='OPEN'))
        ClassRepo-->>ClassSvc: ClassEntity saved (id=15)
        ClassSvc-->>ClassCtrl: ClassResponseDTO
        ClassCtrl-->>Staff: 201 Created (Thông tin lớp mở thành công)
    end
```

---

### 4.3. Khảo thí Trực tuyến 3 Kỹ năng & Tự động Đề xuất Khóa học

```mermaid
sequenceDiagram
    autonumber
    actor Student as Học viên
    participant TestCtrl as PlacementTestController
    participant TestSvc as PlacementTestService
    participant QuestRepo as TestQuestionRepository
    participant RuleRepo as TestRecommendationRuleRepository
    participant SubRepo as TestSubmissionRepository

    Student->>TestCtrl: POST /api/admission/placement-tests/1/submit (answers)
    TestCtrl->>TestSvc: submitTest(userId=12, testSetId=1, answers)
    TestSvc->>QuestRepo: findAllByTestSetId(1)
    QuestRepo-->>TestSvc: List<TestQuestion> (kèm correct_option, score_weight)

    Note over TestSvc: Tự động chấm điểm bóc tách 3 kỹ năng:<br/>Listening, Reading, Grammar & Tính Total Score

    TestSvc->>RuleRepo: findMatchingRule(testSetId=1, totalScore)
    RuleRepo-->>TestSvc: Rule (assessedLevel='Intermediate', courseId=2, advice)

    TestSvc->>SubRepo: save(TestSubmission(scores, level, recommendedCourseId, answers_jsonb))
    SubRepo-->>TestSvc: Submission saved (id=101)

    TestSvc-->>TestCtrl: TestResultDTO (scores, recommended_course, advice)
    TestCtrl-->>Student: 200 OK (Hiển thị Bảng phân tích năng lực & Nút Đăng ký)
```

---

### 4.4. Đăng ký Nhập học, Giữ chỗ 48h & Bắt tay Thanh toán Liên Service

```mermaid
sequenceDiagram
    autonumber
    actor Client as Học viên / Học vụ
    participant Adm as Admission Service (:8081)
    participant DB as PostgreSQL (admission schema)
    participant Fin as Finance Service (:8084)
    participant Stu as Student Service (:8082)

    Note over Client, Adm: 1. Học viên nộp đơn đăng ký giữ chỗ
    Client->>Adm: POST /api/admission/enrollments (class_id=5, student_id=12)
    Adm->>DB: BEGIN TRANSACTION & SELECT class FOR UPDATE
    Adm->>DB: Tính Available Slots = max - approved - active_held
    
    alt Available Slots <= 0 (Lớp đã đầy)
        Adm-->>Client: 400 Bad Request (ADM_CLASS_FULL)
    else Còn chỗ trống
        Adm->>DB: INSERT INTO enrollments (status='PENDING', hold_expires_at=NOW+48h)
        Adm->>Fin: POST /api/finance/invoices (student_id, enrollment_id, amount)
        Fin-->>Adm: 201 Created (invoice_code='INV-2026-99')
        Adm->>DB: UPDATE enrollments SET invoice_code='INV-2026-99'
        Adm->>DB: COMMIT TRANSACTION
        Adm-->>Client: 201 Created (Đơn PENDING, Giữ slot 48h, Mã chuyển khoản)
    end

    Note over Client, Fin: 2. Học viên chuyển khoản học phí
    Client->>Fin: POST /api/finance/payments (invoice_id, amount, method='BANK_TRANSFER')
    Fin->>Fin: Kiểm tra tổng đóng >= giá trị hóa đơn -> Chuyển invoice sang PAID

    Note over Fin, Adm: 3. Callback xác nhận đóng tiền
    Fin->>Adm: POST /api/admission/enrollments/payment-callback (enrollment_id, status='PAID', tx_ref)
    Adm->>DB: BEGIN TRANSACTION & Kiểm tra sĩ số -> UPDATE enrollments SET status='APPROVED'
    Adm->>DB: COMMIT TRANSACTION
    Adm-->>Fin: 200 OK (Xác nhận nhập học thành công)

    Note over Adm, Stu: 4. Khởi tạo Hồ sơ Học vụ chính thức
    Adm->>Stu: POST /api/student/students (user_id=12, name, email, phone, status='STUDYING')
    Stu-->>Adm: 201 Created (student_id)
```

---

### 4.5. Tác vụ Quét Nền Thu hồi Slot Quá hạn 48h

```mermaid
sequenceDiagram
    autonumber
    participant Cron as Spring @Scheduled (Mỗi 15 phút)
    participant Job as HoldSlotExpirationJob
    participant Repo as EnrollmentRepository
    participant DB as PostgreSQL (admission schema)
    participant Fin as Finance Service (:8084)

    Cron->>Job: executeExpiredSlotsCleanup()
    Job->>Repo: findExpiredPendingEnrollments(NOW)
    Repo->>DB: SELECT * FROM enrollments WHERE status='PENDING' AND hold_expires_at < NOW()
    DB-->>Repo: List<Enrollment> quá hạn 48h (ví dụ 3 đơn)

    loop Với mỗi đơn quá hạn
        Job->>Job: enrollment.setStatus('EXPIRED')
        Job->>Job: enrollment.setNote('Hệ thống tự động thu hồi do quá hạn 48h')
        
        opt Nếu đơn có invoice_code
            Job->>Fin: PUT /api/finance/invoices/{code}/cancel (reason="Quá hạn giữ chỗ")
            Fin-->>Job: 200 OK (Hóa đơn đã hủy)
        end
    end

    Job->>Repo: saveAll(expiredEnrollments)
    Repo->>DB: UPDATE enrollments SET status='EXPIRED'
    Note over Job: Slot trống của lớp tự động tăng trở lại!
```

---

## 5. Biểu đồ Máy Trạng thái (UML State Machine Diagrams)

### 5.1. Vòng đời Đơn Đăng ký Tuyển sinh (Enrollment Lifecycle)

```mermaid
stateDiagram-v2
    [*] --> PENDING : Nộp đơn mới (Available Slots > 0)\n[hold_expires_at = NOW + 48h]

    PENDING --> APPROVED : Nhận xác nhận PAID từ Finance\nhoặc Học vụ duyệt tiền mặt (approve-manual)
    PENDING --> EXPIRED : Quá hạn 48h chưa nộp tiền\n(Scheduled Job tự động thu hồi)
    PENDING --> CANCELLED : Học viên chủ động rút đơn
    PENDING --> REJECTED : Học vụ từ chối tiếp nhận

    APPROVED --> CANCELLED_REFUND_PENDING : Lớp học bị hủy do thiếu sĩ số\n(Chuyển Finance xử lý hoàn tiền/bảo lưu)

    EXPIRED --> [*]
    CANCELLED --> [*]
    REJECTED --> [*]
    APPROVED --> [*] : Hoàn thành khóa học
    CANCELLED_REFUND_PENDING --> [*] : Hoàn phí xong

    note right of CANCELLED
        Quy tắc Bất biến INV-ADM-03:
        Tuyệt đối không cho phép chuyển
        trực tiếp từ CANCELLED sang APPROVED.
    end note
```

---

### 5.2. Vòng đời Lớp học (Class Lifecycle)

```mermaid
stateDiagram-v2
    [*] --> OPEN : Học vụ mở lớp mới\n(Kiểm tra xung đột phòng & giáo viên OK)

    OPEN --> IN_PROGRESS : Đến ngày khai giảng (start_date)\nvà đạt sĩ số tối thiểu (approved >= min_students)
    OPEN --> CANCELLED : Trước ngày khai giảng\nkhông đủ sĩ số tối thiểu (approved < min_students)

    IN_PROGRESS --> COMPLETED : Đến ngày bế giảng (end_date)\nvà hoàn tất chương trình đào tạo

    CANCELLED --> [*]
    COMPLETED --> [*]
```

---

## 6. Biểu đồ Hoạt động (UML Activity Diagrams)

### 6.1. Hoạt động: Thuật toán Kiểm tra Xung đột Lịch Phòng học & Giáo viên

```mermaid
flowchart TD
    Start([Bắt đầu Kiểm tra Lịch]) --> CheckCapacity{Sĩ số tối đa\n<= Sức chứa phòng?}
    CheckCapacity -- Không --> ErrCapacity[Ném lỗi: ADM_ROOM_CAPACITY_EXCEEDED]
    CheckCapacity -- Đạt --> QueryDB[Truy vấn các lớp OPEN/IN_PROGRESS\nkhác lớp hiện tại]

    QueryDB --> LoopClasses{Còn lớp học\ncần duyệt?}
    LoopClasses -- Hết --> ValidSuccess([Lịch hợp lệ: Cho phép Lưu lớp])

    LoopClasses -- Còn --> MatchDate{Giao thoa khoảng ngày?\nstart1 <= end2 VÀ end1 >= start2}
    MatchDate -- Không --> LoopClasses
    MatchDate -- Có --> MatchDay{Trùng mẫu ngày học?\nday_pattern có giao nhau}

    MatchDay -- Không --> LoopClasses
    MatchDay -- Có --> MatchTime{Giao thoa khung giờ?\nstart1 < end2 VÀ end1 > start2}

    MatchTime -- Không --> LoopClasses
    MatchTime -- Có --> CheckConflictType{Xung đột gì?}

    CheckConflictType -- Cùng room_id --> ErrRoom[Ném lỗi: ADM_ROOM_CONFLICT\nPhòng học đã có lớp khác học]
    CheckConflictType -- Cùng teacher_id --> ErrTeacher[Ném lỗi: ADM_TEACHER_CONFLICT\nGiáo viên đã có lịch dạy lớp khác]

    ErrCapacity --> EndFail([Kết thúc: Báo lỗi HTTP 400])
    ErrRoom --> EndFail
    ErrTeacher --> EndFail
```

---

### 6.2. Hoạt động: Chấm điểm & Quy đổi Lộ trình Khảo thí

```mermaid
flowchart TD
    Start([Bắt đầu Chấm bài]) --> InitScores[Khởi tạo: listening=0, reading=0, grammar=0]
    InitScores --> LoopAnswers{Còn câu trả lời\ncần chấm?}

    LoopAnswers -- Còn câu --> CheckCorrect{chosen_option ==\ncorrect_option?}
    CheckCorrect -- Sai --> LoopAnswers
    CheckCorrect -- Đúng --> CheckSkill{Thuộc kỹ năng nào?}

    CheckSkill -- LISTENING --> AddList[listening_score += score_weight] --> LoopAnswers
    CheckSkill -- READING --> AddRead[reading_score += score_weight] --> LoopAnswers
    CheckSkill -- GRAMMAR --> AddGram[grammar_score += score_weight] --> LoopAnswers

    LoopAnswers -- Đã chấm xong --> CalcTotal[total_score = listening + reading + grammar]
    CalcTotal --> MatchRule[Tra cứu test_recommendation_rules:\nmin_score <= total_score <= max_score]
    MatchRule --> ExtractRec[Gán: assessed_level, recommended_course_id, advice]
    ExtractRec --> SaveDB[(Lưu bản ghi test_submissions\nkèm JSONB chi tiết đáp án)]
    SaveDB --> OutputResult([Trả về kết quả & Nút Đăng ký Khóa học])
```

---

## 7. Ma trận Truy vết Yêu cầu sang Thiết kế (Requirements Traceability Matrix)

Ma trận chứng minh 100% các yêu cầu nghiệp vụ (`FR`), quy tắc bất biến (`INV`) đã được hiện thực hóa đầy đủ trong thiết kế UML:

| Mã Yêu cầu | Tên Yêu cầu Nghiệp vụ | Use Case UML | Lớp UML / Entity | Quy tắc Bất biến Bảo vệ |
|---|---|---|---|---|
| **FR-IAM-01** | Tự động tạo tài khoản Student | `UC_Auth` | `User`, `UserService` | Cách ly dữ liệu |
| **FR-IAM-03** | Xác thực JWT Token Kép | `UC_Login`, `UC_Refresh` | `JwtTokenProvider`, `JwtAuthenticationFilter` | Bảo mật phiên |
| **FR-IAM-04** | Refresh Token Rotation | `UC_Refresh` | `RefreshToken`, `AuthService` | Chống Replay attack |
| **FR-IAM-07** | Nhật ký Kiểm toán Đăng nhập | `UC_RecordAudit`, `UC_Audit` | `AuthAuditLog`, `AuditLogService` | Lưu vết kiểm toán |
| **FR-FAC-01** | Quản lý Danh mục Phòng học | `UC_Room` | `Room`, `RoomService` | Toàn vẹn cơ sở vật chất |
| **FR-FAC-03** | Ràng buộc Sức chứa Phòng | `UC_CheckConflict` | `Room.hasCapacity()`, `ConflictEngine` | Sức chứa vật lý |
| **FR-ACA-01** | CRUD Khóa học chuẩn | `UC_Course` | `Course`, `CourseService` | `INV-ADM-02` (Mã khóa duy nhất) |
| **FR-ACA-03** | Chống Xung đột Lịch Phòng & GV | `UC_CheckConflict` | `ConflictEngine`, `ClassService` | `INV-ADM-03` (Lịch không trùng) |
| **FR-TST-02** | Ngân hàng câu hỏi 3 kỹ năng | `UC_TakeTest` | `TestQuestion`, `PlacementTestService` | Đo lường năng lực chuẩn |
| **FR-TST-04** | Chấm điểm tự động & Đề xuất | `UC_AutoGrade`, `UC_Recommend` | `TestRecommendationRule`, `TestSubmission` | Khảo thí minh bạch |
| **FR-ENR-01** | Đăng ký Tuyển sinh Đa kênh | `UC_SelfEnroll`, `UC_StaffEnroll` | `EnrollmentController`, `EnrollmentService` | Trải nghiệm đa kênh |
| **FR-ENR-02** | Không bao giờ duyệt vượt sĩ số | `UC_Hold48h` | `EnrollmentService` (Pessimistic Lock) | **`INV-ADM-01`** (P0 - Zero Over-enrollment) |
| **FR-ENR-03** | Giữ chỗ 48h tự động thu hồi | `UC_Hold48h`, `UC_AutoExpire` | `HoldSlotExpirationJob`, `Enrollment` | Thu hồi tài nguyên rác |
| **FR-ENR-06** | Nhập học dựa trên thanh toán | `UC_CallbackPaid` | `EnrollmentService.processPaymentCallback` | Tính toàn vẹn thanh toán |
| **FR-ENR-08** | Đồng bộ Hồ sơ Học viên | `UC_SyncStudent` | `StudentClient`, `EnrollmentService` | Nhất quán dữ liệu liên service |

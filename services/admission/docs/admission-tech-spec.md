# ĐẶC TẢ THIẾT KẾ KỸ THUẬT & KIẾN TRÚC PHẦN MỀM (TECHNICAL SPECIFICATION)
## PHÂN HỆ ĐỊNH DANH, TUYỂN SINH & ĐÀO TẠO (ADMISSION & IDENTITY SERVICE)

> **Dự án**: Hệ thống Quản lý Trung tâm Anh ngữ  
> **Dịch vụ**: `admission-service` (Port 8081)  
> **Nền tảng công nghệ**: Java 21 (LTS), Spring Boot 3.3.4, Spring Data JPA, Spring Security 6, PostgreSQL 16  
> **Tài liệu tham chiếu SSOT**: [admission-ba-bi-spec.md](file:///run/media/tamdae/04C8A69DC8A68C8C/Users/LENOVO/Documents/TL_Kỳ_1_năm_4/Software_Engineering/services/admission/docs/admission-ba-bi-spec.md)  
> **Phiên bản**: 1.0 (Technical Blueprint)  
> **Ngày phê duyệt**: 2026-10-28  

---

## MỤC LỤC
1. [Tổng quan Kiến trúc Kỹ thuật (Technical Architecture Overview)](#1-tổng-quan-kiến-trúc-kỹ-thuật-technical-architecture-overview)
   - 1.1. Vị trí trong Hệ thống Microservices
   - 1.2. Cấu trúc Gói Mã nguồn (Package Structure)
   - 1.3. Vòng đời Xử lý Request (Request Lifecycle Flow)
2. [Thiết kế Hạ tầng Định danh & Bảo mật (Security & IAM Engine)](#2-thiết-kế-hạ-tầng-định-danh--bảo-mật-security--iam-engine)
   - 2.1. Chiến lược Token Kép (Dual-Token JWT Architecture)
   - 2.2. Chuỗi Bộ lọc Bảo mật (Spring Security 6 Filter Chain)
   - 2.3. Cơ chế Refresh Token Rotation & Thu hồi
   - 2.4. Đặt lại Mật khẩu qua Email (Password Reset Flow)
   - 2.5. Động cơ Ghi vết Kiểm toán (Audit Logging Engine)
3. [Các Động cơ Nghiệp vụ Cốt lõi (Core Business Engines & Algorithms)](#3-các-động-cơ-nghiệp-vụ-cốt-lõi-core-business-engines--algorithms)
   - 3.1. Conflict Prevention Engine (Thuật toán Ngăn chặn Xung đột Lịch)
   - 3.2. Placement Test Engine (Khảo thí 3 Kỹ năng & Tự động Đề xuất)
   - 3.3. 48-Hour Slot Holding Engine (Quản lý Sĩ số & Giữ chỗ 48h)
   - 3.4. Class Cancellation & Safeguard Engine (Hủy lớp Thiếu Sĩ số)
4. [Tác vụ Xử lý Nền (Scheduled Background Jobs)](#4-tác-vụ-xử-lý-nền-scheduled-background-jobs)
   - 4.1. Job Quét Thu hồi Đơn Quá hạn 48h (`HoldSlotExpirationJob`)
   - 4.2. Job Dọn dẹp Token Hết hạn (`TokenCleanupJob`)
5. [Đặc tả DTO, Validation & Mapping (Data Transfer Objects)](#5-đặc-tả-dto-validation--mapping-data-transfer-objects)
   - 5.1. Quy chuẩn Đặt tên Snake Case toàn cục
   - 5.2. Danh mục DTO Đầu vào & Đầu ra Chi tiết
6. [Xử lý Ngoại lệ Tập trung & Chuẩn hóa Response (Error Handling)](#6-xử-lý-ngoại-lệ-tập-trung--chuẩn-hóa-response-error-handling)
   - 6.1. Cấu trúc Chuẩn `ApiResponse<T>`
   - 6.2. Bộ Từ điển Mã Lỗi Nghiệp vụ (`ErrorCode` Enum)
   - 6.3. Global Exception Handler (`@RestControllerAdvice`)
7. [Tích hợp Liên Dịch vụ & Khả năng Chịu lỗi (Inter-Service Resilience)](#7-tích-hợp-liên-dịch-vụ--khả-năng-chịu-lỗi-inter-service-resilience)
   - 7.1. Cấu hình HTTP Client nội bộ (Spring RestClient)
   - 7.2. Giao tiếp với Finance Service (Tạo Hóa đơn & Webhook Xác nhận)
   - 7.3. Giao tiếp với Student Service (Đồng bộ Hồ sơ Học vụ)
   - 7.4. Cơ chế Idempotency & Retry Exponential Backoff
8. [Kế hoạch Kiểm thử & Bảo toàn Invariants (Testing & Quality Gate)](#8-kế-hoạch-kiểm-thử--bảo-toàn-invariants-testing--quality-gate)

---

## 1. Tổng quan Kiến trúc Kỹ thuật (Technical Architecture Overview)

### 1.1. Vị trí trong Hệ thống Microservices
`admission-service` là dịch vụ xương sống viết bằng **Java 21 / Spring Boot 3.3**, đảm nhận 2 vai trò trung tâm:
- **Centralized IAM Provider**: Quản lý tài khoản, phân quyền RBAC và phát hành JWT Token cho toàn bộ người dùng của cả 4 phân hệ.
- **Academic & Admissions Engine**: Quản lý danh mục cơ sở vật chất, khóa học, lớp học và phễu tuyển sinh giữ chỗ 48h.

```
                    ┌────────────────────────────────────────────────────────┐
                    │               Nginx API Gateway (Port 8080)            │
                    └───────────────────────────┬────────────────────────────┘
                                                │
                                    ┌───────────▼──────────┐
                                    │  ADMISSION & AUTH    │
                                    │  Spring Boot (:8081) │
                                    └─────┬───────────┬────┘
                                          │           │
                 ┌────────────────────────┘           └─────────────────────────┐
                 │ REST Sync on APPROVED                                        │ REST: Create Invoice
                 ▼                                                              ▼
     ┌───────────────────────┐                                      ┌───────────────────────┐
     │    STUDENT SERVICE    │                                      │    FINANCE SERVICE    │
     │    FastAPI (:8082)    │                                      │    FastAPI (:8084)    │
     │  (Profiles, Sổ ĐD)    │                                      │  (Invoices, Payments) │
     └───────────────────────┘                                      └───────────────────────┘
```

### 1.2. Cấu trúc Gói Mã nguồn (Package Structure)
Dự án áp dụng mô hình phân tầng nghiêm ngặt (Strict Layered Architecture):

```
services/admission/src/main/java/vn/edu/english/admission/
├── AdmissionApplication.java             # Entry point của ứng dụng
├── config/                               # Các Bean cấu hình hệ thống
│   ├── SecurityConfig.java               # Spring Security 6 & JWT Filter Chain
│   ├── JacksonConfig.java                # Cấu hình snake_case naming strategy
│   ├── RestClientConfig.java             # Cấu hình RestClient gọi inter-service
│   └── ScheduleConfig.java               # Kích hoạt Spring @EnableScheduling
├── controller/                           # Tầng tiếp nhận HTTP requests (REST Controllers)
│   ├── AuthController.java               # /auth/login, /auth/refresh, /auth/logout...
│   ├── UserController.java               # /api/admission/users...
│   ├── RoomController.java               # /api/admission/rooms...
│   ├── CourseController.java             # /api/admission/courses...
│   ├── ClassController.java              # /api/admission/classes...
│   ├── PlacementTestController.java      # /api/admission/placement-tests...
│   ├── EnrollmentController.java         # /api/admission/enrollments...
│   └── AnalyticsController.java          # /api/admission/analytics...
├── service/                              # Tầng nghiệp vụ cốt lõi (Business Interfaces & Impl)
│   ├── AuthService.java / AuthServiceImpl.java
│   ├── UserService.java / UserServiceImpl.java
│   ├── RoomService.java / RoomServiceImpl.java
│   ├── CourseService.java / CourseServiceImpl.java
│   ├── ClassService.java / ClassServiceImpl.java
│   ├── ConflictEngine.java               # Thuật toán quét xung đột phòng & giáo viên
│   ├── PlacementTestService.java / PlacementTestServiceImpl.java
│   ├── EnrollmentService.java / EnrollmentServiceImpl.java
│   └── AnalyticsService.java / AnalyticsServiceImpl.java
├── repository/                           # Tầng tương tác Cơ sở dữ liệu (Spring Data JPA)
│   ├── UserRepository.java
│   ├── RefreshTokenRepository.java
│   ├── PasswordResetTokenRepository.java
│   ├── AuthAuditLogRepository.java
│   ├── RoomRepository.java
│   ├── CourseRepository.java
│   ├── ClassRepository.java
│   ├── EnrollmentRepository.java
│   ├── TestSetRepository.java
│   ├── TestQuestionRepository.java
│   ├── TestRecommendationRuleRepository.java
│   └── TestSubmissionRepository.java
├── entity/                               # JPA Entities ánh xạ schema admission.*
│   ├── User.java
│   ├── RefreshToken.java
│   ├── PasswordResetToken.java
│   ├── AuthAuditLog.java
│   ├── Room.java
│   ├── Course.java
│   ├── ClassEntity.java
│   ├── Enrollment.java
│   ├── TestSet.java
│   ├── TestQuestion.java
│   ├── TestRecommendationRule.java
│   └── TestSubmission.java
├── dto/                                  # Data Transfer Objects & Validation
│   ├── common/                           # ApiResponse, PaginatedResponse, ApiError
│   ├── request/                          # DTO gửi lên từ Client
│   └── response/                         # DTO trả về cho Client
├── exception/                            # Quản lý lỗi & Bắt lỗi toàn cục
│   ├── BusinessException.java            # Ngoại lệ nghiệp vụ chủ động
│   ├── ErrorCode.java                    # Enum mã lỗi hệ thống
│   └── GlobalExceptionHandler.java       # @RestControllerAdvice
├── security/                             # JWT Utilities & Authentication Providers
│   ├── JwtTokenProvider.java             # Sinh, mã hóa và validate JWT token
│   ├── JwtAuthenticationFilter.java      # Trích xuất Bearer token từ Request Header
│   └── CustomUserDetailsService.java     # Nạp thông tin người dùng cho Spring Security
├── client/                               # HTTP Client giao tiếp với các microservices khác
│   ├── FinanceClient.java                # Gọi sang Finance Service (:8084)
│   └── StudentClient.java                # Gọi sang Student Service (:8082)
└── job/                                  # Scheduled Background Tasks
    ├── HoldSlotExpirationJob.java        # Quét đơn giữ chỗ quá 48h
    └── TokenCleanupJob.java              # Xóa refresh token hết hạn
```

### 1.3. Vòng đời Xử lý Request (Request Lifecycle Flow)
Mọi request gửi tới `admission-service` đều đi qua quy trình tiêu chuẩn:
1. **Nginx API Gateway**: Kiểm tra định tuyến (`/api/admission/*` hoặc `/auth/*`) ➔ Reverse Proxy chuyển tiếp tới Port 8081.
2. **JwtAuthenticationFilter**: Đọc header `Authorization: Bearer <token>`, giải mã claim (`userId`, `role`), nạp `Authentication` vào `SecurityContextHolder`.
3. **Controller**: Validate dữ liệu đầu vào qua annotation `@Valid`. Bắt lỗi `MethodArgumentNotValidException` nếu sai định dạng.
4. **Service**: Thực thi Business Rules, mở `@Transactional` khi có thao tác ghi dữ liệu. Ném `BusinessException` kèm `ErrorCode` nếu vi phạm nghiệp vụ.
5. **Repository**: Thực thi các câu lệnh SQL qua Spring Data JPA chỉ trong schema `admission`.
6. **GlobalExceptionHandler**: Bọc response thành công hoặc lỗi thành đối tượng `ApiResponse<T>` thống nhất.

---

## 2. Thiết kế Hạ tầng Định danh & Bảo mật (Security & IAM Engine)

### 2.1. Chiến lược Token Kép (Dual-Token JWT Architecture)

| Đặc tính | Access Token | Refresh Token |
|---|---|---|
| **Thời hạn (TTL)** | 15 phút (900 giây) | 7 ngày (604.800 giây) |
| **Lưu trữ** | Phía Client (Memory / HTTPOnly Cookie) | Cả Client & Database (`admission.refresh_tokens`) |
| **Tính chất** | Stateless (Không cần tra cứu Database khi verify) | Stateful (Kiểm tra trạng thái `is_revoked` trong DB) |
| **Payload Claims** | `sub` (userId), `email`, `role`, `full_name`, `iss`, `iat`, `exp` | Chuỗi mã hóa Cryptographically Secure Random UUID v4 |
| **Mục đích** | Đính kèm vào mọi request API | Chỉ dùng để gọi `POST /auth/refresh` đổi lấy Access Token mới |

### 2.2. Chuỗi Bộ lọc Bảo mật (Spring Security 6 Filter Chain)

```java
@Configuration
@EnableWebSecurity
@EnableMethodSecurity
@RequiredArgsConstructor
public class SecurityConfig {

    private final JwtAuthenticationFilter jwtAuthenticationFilter;

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http
            .csrf(AbstractHttpConfigurer::disable)
            .cors(Customizer.withDefaults())
            .sessionManagement(session -> session.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .authorizeHttpRequests(auth -> auth
                // Public endpoints
                .requestMatchers(
                    "/auth/login",
                    "/auth/refresh",
                    "/auth/forgot-password",
                    "/auth/reset-password",
                    "/api/admission/courses/**",
                    "/api/admission/classes/**",
                    "/api/admission/placement-tests/**"
                ).permitAll()
                // Internal inter-service endpoints
                .requestMatchers("/api/admission/enrollments/payment-callback").permitAll()
                // Admin-only endpoints
                .requestMatchers("/api/admission/users/**", "/api/admission/audit-logs/**").hasRole("ADMIN")
                // Staff & Admin endpoints
                .requestMatchers(HttpMethod.POST, "/api/admission/rooms/**").hasAnyRole("ADMIN", "STAFF")
                // Authenticated endpoints
                .anyRequest().authenticated()
            )
            .addFilterBefore(jwtAuthenticationFilter, UsernamePasswordAuthenticationFilter.class);

        return http.build();
    }

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder(12);
    }
}
```

### 2.3. Cơ chế Refresh Token Rotation & Thu hồi
Để chống lộ lọt Refresh Token, hệ thống áp dụng cơ chế **Refresh Token Rotation (Xoay vòng Token)**:
1. Khi Client gửi Refresh Token $R_1$ lên endpoint `POST /auth/refresh`.
2. Hệ thống kiểm tra:
   - Nếu $R_1$ không tồn tại hoặc `expires_at < NOW()` ➔ Trả lỗi `AUTH_TOKEN_EXPIRED` (HTTP 401).
   - Nếu $R_1$ có cờ `is_revoked == true` ➔ **Cảnh báo tấn công Token Reuse!** Hệ thống lập tức thu hồi toàn bộ các Refresh Token của User đó và ghi log bảo mật `SECURITY_ALERT`.
3. Nếu hợp lệ:
   - Đánh dấu $R_1$: `is_revoked = true`.
   - Sinh Refresh Token mới $R_2$ lưu vào database.
   - Sinh Access Token mới $A_2$.
   - Trả về cặp $\{A_2, R_2\}$ cho Client.

### 2.4. Đặt lại Mật khẩu qua Email (Password Reset Flow)
1. Client gửi email tới `POST /auth/forgot-password`.
2. Hệ thống kiểm tra user: Nếu tồn tại, sinh chuỗi token ngẫu nhiên độ dài 64 ký tự hex lưu vào `admission.password_reset_tokens` kèm `expires_at = NOW() + 15 phút`.
3. Gửi email chứa liên kết: `https://frontend-host/shared/reset-password.html?token={reset_token}`.
4. Khi người dùng nhập mật khẩu mới tại `POST /auth/reset-password`:
   - Xác thực token: Còn hạn và `is_used == false`.
   - Băm mật khẩu mới qua `BCryptPasswordEncoder(12)`.
   - Cập nhật `user.password_hash`, đánh dấu `token.is_used = true`.
   - Đánh dấu thu hồi tất cả các `refresh_tokens` cũ của user để bắt buộc đăng nhập lại.

### 2.5. Động cơ Ghi vết Kiểm toán (Audit Logging Engine)
Mọi hành vi liên quan tới định danh và bảo mật bắt buộc phải được ghi nhận vào `admission.auth_audit_logs` một cách bất đồng bộ (`@Async`) để không làm chậm luồng xử lý chính:

```java
@Service
@RequiredArgsConstructor
public class AuditLogService {
    private final AuthAuditLogRepository auditLogRepository;

    @Async
    public void record(Integer userId, String action, HttpServletRequest request, String details) {
        String clientIp = extractClientIp(request);
        String userAgent = request.getHeader("User-Agent");

        AuthAuditLog log = AuthAuditLog.builder()
                .userId(userId)
                .action(action)
                .ipAddress(clientIp)
                .userAgent(userAgent)
                .details(details)
                .createdAt(OffsetDateTime.now())
                .build();

        auditLogRepository.save(log);
    }
}
```

---

## 3. Các Động cơ Nghiệp vụ Cốt lõi (Core Business Engines & Algorithms)

### 3.1. Conflict Prevention Engine (Thuật toán Ngăn chặn Xung đột Lịch)

Thuật toán chịu trách nhiệm kiểm tra xem việc mở lớp hoặc cập nhật lịch lớp có gây xung đột tài nguyên hay không.

```
[Request Tạo/Sửa Lớp: room_id, teacher_id, day_pattern, start_time, end_time, start_date, end_date]
                                      │
                 ┌────────────────────┴────────────────────┐
                 ▼                                         ▼
   1. Kiểm tra Sức chứa Phòng               2. Truy vấn các Lớp Đang Mở trong Schema
   max_students <= room.capacity?           status IN ('OPEN', 'IN_PROGRESS')
   (Nếu sai: ADM_ROOM_CAPACITY_EXCEEDED)    AND id != current_class_id
                                                           │
                                                           ▼
                               3. So khớp Điều kiện Trùng Lịch (Overlapping Match):
                                  a. Giao thoa khoảng ngày: (start_date <= end_date_db) AND (end_date >= start_date_db)
                                  b. Trùng khớp mẫu thứ: day_pattern trùng hoặc có giao (VD: MON_WED_FRI)
                                  c. Giao thoa khung giờ: (start_time < end_time_db) AND (end_time > start_time_db)
                                                           │
                                 ┌─────────────────────────┴─────────────────────────┐
                                 ▼                                                   ▼
                     Có lớp cùng room_id?                                Có lớp cùng teacher_id?
                     Bắt buộc chặn:                                      Bắt buộc chặn:
                     ADM_ROOM_CONFLICT (HTTP 400)                        ADM_TEACHER_CONFLICT (HTTP 400)
```

#### Cài đặt Logic kiểm tra giao thoa trong Service:
```java
@Service
@RequiredArgsConstructor
public class ConflictEngine {
    private final ClassRepository classRepository;
    private final RoomRepository roomRepository;

    public void validateClassSchedule(ClassRequestDTO dto, Integer excludeClassId) {
        // 1. Kiểm tra sức chứa phòng học
        Room room = roomRepository.findById(dto.getRoomId())
                .orElseThrow(() -> new BusinessException(ErrorCode.ROOM_NOT_FOUND));
        if (dto.getMaxStudents() > room.getCapacity()) {
            throw new BusinessException(ErrorCode.ADM_ROOM_CAPACITY_EXCEEDED,
                    String.format("Sĩ số tối đa (%d) vượt quá sức chứa của phòng %s (%d chỗ)",
                            dto.getMaxStudents(), room.getCode(), room.getCapacity()));
        }

        // 2. Tìm tất cả các lớp có khả năng giao thoa về ngày và giờ
        List<ClassEntity> overlappingClasses = classRepository.findOverlappingClasses(
                dto.getStartDate(), dto.getEndDate(),
                dto.getStartTime(), dto.getEndTime(),
                dto.getDayPattern(),
                excludeClassId == null ? -1 : excludeClassId
        );

        // 3. Phân loại lỗi xung đột cụ thể
        for (ClassEntity activeClass : overlappingClasses) {
            if (activeClass.getRoom().getId().equals(dto.getRoomId())) {
                throw new BusinessException(ErrorCode.ADM_ROOM_CONFLICT,
                        String.format("Phòng %s đã có lớp %s học cùng khung giờ này",
                                room.getName(), activeClass.getCode()));
            }
            if (activeClass.getTeacher() != null && activeClass.getTeacher().getId().equals(dto.getTeacherId())) {
                throw new BusinessException(ErrorCode.ADM_TEACHER_CONFLICT,
                        String.format("Giáo viên đã có lịch giảng dạy lớp %s cùng khung giờ này",
                                activeClass.getCode()));
            }
        }
    }
}
```

---

### 3.2. Placement Test Engine (Khảo thí 3 Kỹ năng & Tự động Đề xuất)

Hệ thống khảo thí trắc nghiệm đầu vào được thiết kế tự động chấm điểm và cá nhân hóa lộ trình:
1. **Lấy đề thi (`GET /api/admission/placement-tests/{id}`)**:
   - Truy vấn toàn bộ câu hỏi thuộc `test_set_id` sắp xếp theo `order_index`.
   - **Bảo mật**: DTO trả về cho Client bị loại bỏ hoàn toàn trường `correct_option`.
2. **Nộp bài & Chấm điểm (`POST /api/admission/placement-tests/{id}/submit`)**:
   - Duyệt qua từng câu trả lời trong mảng `answers`.
   - So khớp `chosen_option` với `correct_option` từ database.
   - Cộng dồn điểm theo từng nhóm kỹ năng:
     $$\text{listening\_score} = \sum \text{score\_weight} \quad (\text{cho câu đúng thuộc LISTENING})$$
     $$\text{reading\_score} = \sum \text{score\_weight} \quad (\text{cho câu đúng thuộc READING})$$
     $$\text{grammar\_score} = \sum \text{score\_weight} \quad (\text{cho câu đúng thuộc GRAMMAR})$$
     $$\text{total\_score} = \text{listening\_score} + \text{reading\_score} + \text{grammar\_score}$$
3. **Đề xuất Khóa học Tự động**:
   - Thực thi truy vấn tìm kiếm quy tắc phù hợp:
     ```sql
     SELECT * FROM admission.test_recommendation_rules
     WHERE test_set_id = :testSetId
       AND :totalScore >= min_score 
       AND :totalScore <= max_score
     LIMIT 1;
     ```
   - Gán `recommended_course_id` và `assessed_level` vào bản ghi `test_submissions`.
   - Lưu trữ toàn bộ câu trả lời dạng JSONB (`answers_detail`) để phục vụ phúc khảo.

---

### 3.3. 48-Hour Slot Holding Engine (Quản lý Sĩ số & Giữ chỗ 48h)

Đây là động cơ bảo đảm **Quy tắc Bất biến Cốt lõi `INV-ADM-01`**: *Không bao giờ được duyệt quá sĩ số tối đa của lớp học*.

```
[Request Đăng ký Lớp: class_id, student_id]
                   │
                   ▼
  1. Transaction Bắt đầu & Khóa bi quan (Pessimistic Lock):
     SELECT * FROM admission.classes WHERE id = :class_id FOR UPDATE;
                   │
                   ▼
  2. Tính toán Sĩ số Khả dụng (Available Slots):
     approved_count = COUNT(*) WHERE status = 'APPROVED'
     active_held_count = COUNT(*) WHERE status = 'PENDING' AND hold_expires_at > NOW()
     available_slots = class.max_students - approved_count - active_held_count
                   │
          ┌────────┴────────┐
          ▼                 ▼
   available_slots <= 0    available_slots > 0
   Chặn ngay lập tức:      Tạo đơn PENDING
   ADM_CLASS_FULL (400)    hold_expires_at = NOW() + 48 HOURS
                           Gọi REST Finance tạo Invoice
```

---

## 4. Tác vụ Xử lý Nền (Scheduled Background Jobs)

Sử dụng Spring `@EnableScheduling` để vận hành các tác vụ tự động dọn dẹp định kỳ:

### 4.1. Job Quét Thu hồi Đơn Quá hạn 48h (`HoldSlotExpirationJob`)
- **Tần suất chạy**: Mỗi 15 phút (`cron = "0 */15 * * * *"`)
- **Nhiệm vụ**:
  1. Quét tất cả các bản ghi `admission.enrollments` thỏa mãn:
     `status = 'PENDING' AND hold_expires_at < CURRENT_TIMESTAMP`
  2. Cập nhật `status = 'EXPIRED'`.
  3. Gọi bất đồng bộ sang **Finance Service** (`PUT /api/finance/invoices/{code}/cancel`) để hủy hóa đơn chưa thanh toán.
  4. Ghi log số lượng slot được giải phóng trả về cho kho lớp học.

```java
@Component
@RequiredArgsConstructor
@Slf4j
public class HoldSlotExpirationJob {

    private final EnrollmentRepository enrollmentRepository;
    private final FinanceClient financeClient;

    @Scheduled(cron = "0 */15 * * * *")
    @Transactional
    public void executeExpiredSlotsCleanup() {
        OffsetDateTime now = OffsetDateTime.now();
        List<Enrollment> expiredEnrollments = enrollmentRepository.findExpiredPendingEnrollments(now);

        if (expiredEnrollments.isEmpty()) {
            return;
        }

        log.info("Bắt đầu thu hồi {} đơn giữ chỗ quá hạn 48h", expiredEnrollments.size());
        for (Enrollment enrollment : expiredEnrollments) {
            enrollment.setStatus("EXPIRED");
            enrollment.setNote("Hệ thống tự động thu hồi do quá hạn giữ chỗ 48h");
            
            // Thông báo sang Finance Service
            if (enrollment.getInvoiceCode() != null) {
                try {
                    financeClient.cancelInvoice(enrollment.getInvoiceCode(), "Quá hạn giữ chỗ 48h");
                } catch (Exception ex) {
                    log.error("Lỗi khi hủy hóa đơn {} bên Finance: {}", enrollment.getInvoiceCode(), ex.getMessage());
                }
            }
        }
        enrollmentRepository.saveAll(expiredEnrollments);
    }
}
```

### 4.2. Job Dọn dẹp Token Hết hạn (`TokenCleanupJob`)
- **Tần suất chạy**: Hàng ngày lúc 02:00 sáng (`cron = "0 0 2 * * *"`)
- **Nhiệm vụ**: Xóa các bản ghi trong `admission.refresh_tokens` và `admission.password_reset_tokens` có `expires_at < NOW() - 30 ngày` để tránh phình to dung lượng database.

---

## 5. Đặc tả DTO, Validation & Mapping (Data Transfer Objects)

### 5.1. Quy chuẩn Đặt tên Snake Case Toàn cục
Trong `JacksonConfig.java`:
```java
@Configuration
public class JacksonConfig {
    @Bean
    public ObjectMapper objectMapper() {
        return JsonMapper.builder()
                .propertyNamingStrategy(PropertyNamingStrategies.SNAKE_CASE)
                .findAndAddModules()
                .build();
    }
}
```

### 5.2. Danh mục DTO Đầu vào & Đầu ra Tiêu biểu

#### 1. Đăng ký Lớp học (`CreateEnrollmentRequest`):
```java
@Data
public class CreateEnrollmentRequest {
    @NotNull(message = "ID lớp học không được để trống")
    private Integer classId;

    @NotNull(message = "ID học viên không được để trống")
    private Integer studentId;

    private String source = "ONLINE"; // ONLINE, WALK_IN, HOTLINE
}
```

#### 2. Nộp bài Khảo thí (`SubmitTestRequest`):
```java
@Data
public class SubmitTestRequest {
    @NotNull(message = "ID người dùng không được để trống")
    private Integer userId;

    @NotEmpty(message = "Danh sách câu trả lời không được để trống")
    @Valid
    private List<AnswerItemDTO> answers;

    @Data
    public static class AnswerItemDTO {
        @NotNull(message = "ID câu hỏi không được để trống")
        private Integer questionId;

        @NotBlank(message = "Đáp án chọn không được để trống")
        @Pattern(regexp = "^[A-D]$", message = "Đáp án phải là A, B, C hoặc D")
        private String chosenOption;
    }
}
```

---

## 6. Xử lý Ngoại lệ Tập trung & Chuẩn hóa Response (Error Handling)

### 6.1. Cấu trúc Chuẩn `ApiResponse<T>`
```json
{
  "success": true,
  "data": { ... },
  "message": "Thao tác thành công",
  "error": null
}
```
Khi xảy ra lỗi:
```json
{
  "success": false,
  "data": null,
  "message": null,
  "error": {
    "code": "ADM_ROOM_CONFLICT",
    "message": "Phòng học P201 đã có lớp khác học cùng khung giờ này"
  }
}
```

### 6.2. Bộ Từ điển Mã Lỗi Nghiệp vụ (`ErrorCode` Enum)

```java
@Getter
@RequiredArgsConstructor
public enum ErrorCode {
    // Auth & Identity (401, 403)
    AUTH_INVALID_CREDENTIALS("AUTH_INVALID_CREDENTIALS", "Email hoặc mật khẩu không chính xác", HttpStatus.UNAUTHORIZED),
    AUTH_ACCOUNT_LOCKED("AUTH_ACCOUNT_LOCKED", "Tài khoản của bạn đã bị khóa, vui lòng liên hệ Admin", HttpStatus.FORBIDDEN),
    AUTH_TOKEN_EXPIRED("AUTH_TOKEN_EXPIRED", "Phiên làm việc đã hết hạn, vui lòng đăng nhập lại", HttpStatus.UNAUTHORIZED),
    AUTH_UNAUTHORIZED("AUTH_UNAUTHORIZED", "Bạn không có quyền thực hiện hành động này", HttpStatus.FORBIDDEN),

    // Academic & Classes (400, 404)
    ADM_COURSE_NOT_FOUND("ADM_COURSE_NOT_FOUND", "Không tìm thấy khóa học yêu cầu", HttpStatus.NOT_FOUND),
    ADM_CLASS_NOT_FOUND("ADM_CLASS_NOT_FOUND", "Không tìm thấy lớp học yêu cầu", HttpStatus.NOT_FOUND),
    ADM_ROOM_NOT_FOUND("ADM_ROOM_NOT_FOUND", "Không tìm thấy phòng học yêu cầu", HttpStatus.NOT_FOUND),
    ADM_DUPLICATE_CODE("ADM_DUPLICATE_CODE", "Mã khóa học hoặc mã lớp học đã tồn tại", HttpStatus.BAD_REQUEST),
    ADM_ROOM_CONFLICT("ADM_ROOM_CONFLICT", "Xung đột lịch: Phòng học đã có lớp khác sử dụng", HttpStatus.BAD_REQUEST),
    ADM_TEACHER_CONFLICT("ADM_TEACHER_CONFLICT", "Xung đột lịch: Giáo viên đã có lịch dạy lớp khác", HttpStatus.BAD_REQUEST),
    ADM_ROOM_CAPACITY_EXCEEDED("ADM_ROOM_CAPACITY_EXCEEDED", "Sĩ số lớp vượt quá sức chứa tối đa của phòng học", HttpStatus.BAD_REQUEST),

    // Admissions & Enrollment (400)
    ADM_CLASS_FULL("ADM_CLASS_FULL", "Lớp học đã đủ sĩ số tối đa, không thể tiếp nhận thêm", HttpStatus.BAD_REQUEST),
    ADM_ENROLLMENT_EXPIRED("ADM_ENROLLMENT_EXPIRED", "Đơn đăng ký đã hết hạn giữ chỗ 48h", HttpStatus.BAD_REQUEST),
    ADM_INVALID_STATE_TRANSITION("ADM_INVALID_STATE_TRANSITION", "Chuyển trạng thái đơn đăng ký không hợp lệ", HttpStatus.BAD_REQUEST);

    private final String code;
    private final String defaultMessage;
    private final HttpStatus httpStatus;
}
```

---

## 7. Tích hợp Liên Dịch vụ & Khả năng Chịu lỗi (Inter-Service Resilience)

### 7.1. Cấu hình HTTP Client nội bộ (Spring RestClient)
Sử dụng `RestClient` hiện đại của Spring 6 với cấu hình Connection Timeout và Read Timeout chặt chẽ:

```java
@Configuration
public class RestClientConfig {

    @Bean
    public RestClient financeRestClient(@Value("${app.services.finance-url:http://finance-service:8084}") String financeUrl) {
        SimpleClientHttpRequestFactory factory = new SimpleClientHttpRequestFactory();
        factory.setConnectTimeout(Duration.ofSeconds(3));
        factory.setReadTimeout(Duration.ofSeconds(5));

        return RestClient.builder()
                .baseUrl(financeUrl)
                .requestFactory(factory)
                .build();
    }
}
```

### 7.2. Giao tiếp với Finance Service
1. **Khi đơn `PENDING` được tạo**:
   - Admission gọi: `POST http://finance-service:8084/api/finance/invoices`
   - Payload:
     ```json
     {
       "student_id": 12,
       "enrollment_id": 105,
       "amount": 6500000,
       "due_date": "2026-10-30"
     }
     ```
   - Nhận về `invoice_code` và lưu vào `enrollments.invoice_code`.
2. **Khi học viên đóng tiền thành công**:
   - Finance gọi callback: `POST http://admission-service:8081/api/admission/enrollments/payment-callback`
   - Payload: `{"enrollment_id": 105, "status": "PAID", "transaction_ref": "TX998811"}`
   - **Cơ chế Idempotency**: Admission kiểm tra trạng thái đơn hiện tại:
     - Nếu đã là `APPROVED` ➔ Trả về HTTP 200 OK ngay lập tức (không thực hiện lại logic).
     - Nếu đang là `PENDING` ➔ Chuyển thành `APPROVED` và kích hoạt đồng bộ sang Student Service.

### 7.3. Giao tiếp với Student Service
Khi đơn đăng ký chuyển sang `APPROVED`:
- Admission gọi: `POST http://student-service:8082/api/student/students`
- Payload:
  ```json
  {
    "user_id": 12,
    "full_name": "Trần Văn Nam",
    "email": "student@english.edu.vn",
    "phone": "0904567890",
    "status": "STUDYING"
  }
  ```
- Nếu Student Service tạm thời không phản hồi (lỗi mạng): Admission ghi log cảnh báo và đưa message vào hàng đợi retry (Spring `@Retryable` với Exponential Backoff: thử lại 3 lần sau 2s, 4s, 8s).

---

## 8. Kế hoạch Kiểm thử & Bảo toàn Invariants (Testing & Quality Gate)

Mọi thay đổi trong mã nguồn `admission-service` phải đảm bảo pass toàn bộ 15 bài kiểm thử bất biến:

```bash
python3 -m unittest discover -s tests/invariants -p "test_*.py" -v
```

### Các Test Case trọng tâm gắn liền với Admission Service:
1. `test_inv_adm_01_cannot_exceed_max_students`: Giả lập lớp học có `max_students = 20`. Tạo 20 đơn `APPROVED`. Khi cố gắng gọi duyệt đơn thứ 21, hệ thống bắt buộc ném lỗi `ADM_CLASS_FULL` (HTTP 400).
2. `test_inv_adm_02_course_code_unique`: Bắt buộc ném lỗi khi cố tạo khóa học có `code` đã tồn tại.
3. `test_inv_adm_03_state_machine_transition`: Kiểm tra đơn `CANCELLED` không bao giờ được phép chuyển trực tiếp sang `APPROVED`.
4. `test_inv_sec_01_student_profile_isolation_logic`: Học viên chỉ được xem thông tin hồ sơ của chính mình.

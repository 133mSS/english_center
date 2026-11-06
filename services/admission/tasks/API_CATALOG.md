# Danh Mục Chi Tiết Các API Endpoints Dự Kiến (Admission & Identity Service)

> **Quy ước kỹ thuật bắt buộc**:
> - Toàn bộ URL đều có tiền tố chuẩn: `/api/admission/` (hoặc `/auth/` cho các API xác thực tương thích ngược).
> - Định dạng dữ liệu trao đổi (Request/Response payload, Query params) bắt buộc là **`snake_case`**.
> - Cấu trúc phản hồi đồng nhất:
>   - Thành công: `{"success": true, "data": { ... }, "message": "Thông báo"}`
>   - Lỗi nghiệp vụ: `{"success": false, "error": {"code": "MÃ_LỖI", "message": "Mô tả lỗi"}}`

---

## 1. Phân Hệ Xác Thực, Quản Trị Định Danh & Phiên (IAM)

| STT | HTTP Method | Endpoint URI | Phân Quyền (RBAC) | Tóm tắt Chức năng Nghiệp vụ | Request Body / Query Params | Mã Lỗi Chính |
|:---:|:---:|---|---|---|---|---|
| 1 | `POST` | `/api/admission/auth/login` | Public | Đăng nhập hệ thống, cấp cặp Access/Refresh Token | `{"email": "...", "password": "..."}` | `ADM_INVALID_CREDENTIALS`, `ADM_ACCOUNT_LOCKED` |
| 2 | `POST` | `/api/admission/auth/refresh` | Public | Làm mới phiên làm việc (Refresh Token Rotation) | `{"refresh_token": "..."}` | `ADM_TOKEN_INVALID`, `ADM_TOKEN_EXPIRED` |
| 3 | `POST` | `/api/admission/auth/logout` | Authenticated | Đăng xuất chủ động, hủy Refresh Token hiện hành | `{"refresh_token": "..."}` | `ADM_TOKEN_INVALID` |
| 4 | `POST` | `/api/admission/auth/forgot-password` | Public | Yêu cầu mã token đặt lại mật khẩu qua email (15m) | `{"email": "..."}` | N/A (Bảo mật enum) |
| 5 | `POST` | `/api/admission/auth/reset-password` | Public | Đặt lại mật khẩu mới bằng token xác thực | `{"token": "...", "new_password": "..."}` | `ADM_TOKEN_EXPIRED`, `ADM_TOKEN_INVALID` |
| 6 | `GET` | `/api/admission/auth/me` | Authenticated | Lấy thông tin tài khoản đang đăng nhập | Header `Authorization: Bearer <token>` | `ADM_UNAUTHORIZED` |
| 7 | `POST` | `/api/admission/auth/change-password` | Authenticated | Đổi mật khẩu chủ động của người dùng | `{"old_password": "...", "new_password": "..."}` | `ADM_INVALID_CREDENTIALS` |
| 8 | `GET` | `/api/admission/users` | ADMIN | Tìm kiếm & phân trang danh sách người dùng | `?role=TEACHER&is_active=true&page=0&size=20` | `ADM_FORBIDDEN` |
| 9 | `POST` | `/api/admission/users` | ADMIN | Tạo tài khoản nhân sự mới (Staff / Teacher) | `{"email": "...", "full_name": "...", "role": "...", "phone": "..."}` | `ADM_USER_EMAIL_EXISTS` |
| 10 | `GET` | `/api/admission/users/{id}` | ADMIN | Xem chi tiết hồ sơ người dùng | Path param `id` | `ADM_USER_NOT_FOUND` |
| 11 | `PUT` | `/api/admission/users/{id}` | ADMIN | Cập nhật thông tin hồ sơ nhân sự | `{"full_name": "...", "phone": "...", "gender": "..."}` | `ADM_USER_NOT_FOUND` |
| 12 | `PATCH`| `/api/admission/users/{id}/status` | ADMIN | Khóa hoặc mở khóa tài khoản người dùng | `{"is_active": false, "reason": "..."}` | `ADM_USER_NOT_FOUND` |
| 13 | `GET` | `/api/admission/audit-logs` | ADMIN | Truy vấn nhật ký kiểm toán bảo mật có phân trang | `?event_type=LOGIN_FAILED&from_date=...` | `ADM_FORBIDDEN` |

---

## 2. Phân Hệ Cơ Sở Vật Chất & Phòng Học (FAC)

| STT | HTTP Method | Endpoint URI | Phân Quyền (RBAC) | Tóm tắt Chức năng Nghiệp vụ | Request Body / Query Params | Mã Lỗi Chính |
|:---:|:---:|---|---|---|---|---|
| 14 | `GET` | `/api/admission/rooms` | STAFF, ADMIN | Lấy danh mục phòng học theo chi nhánh | `?branch_name=...&is_active=true` | N/A |
| 15 | `POST` | `/api/admission/rooms` | ADMIN | Tạo mới phòng học | `{"code": "ROOM-101", "name": "...", "capacity": 25, "branch_name": "..."}` | `ADM_ROOM_CODE_EXISTS` |
| 16 | `GET` | `/api/admission/rooms/{id}` | STAFF, ADMIN | Xem thông tin chi tiết phòng học | Path param `id` | `ADM_ROOM_NOT_FOUND` |
| 17 | `PUT` | `/api/admission/rooms/{id}` | ADMIN | Chỉnh sửa tên, sức chứa phòng học | `{"name": "...", "capacity": 30}` | `ADM_ROOM_NOT_FOUND` |
| 18 | `PATCH`| `/api/admission/rooms/{id}/status` | ADMIN | Tạm ngưng hoặc kích hoạt phòng học | `{"is_active": false}` | `ADM_ROOM_NOT_FOUND` |
| 19 | `GET` | `/api/admission/rooms/{id}/schedule`| STAFF, ADMIN | Lấy thời khóa biểu các ca học trong tuần của phòng | `?from_date=...&to_date=...` | `ADM_ROOM_NOT_FOUND` |

---

## 3. Phân Hệ Khóa Học & Lộ Trình Đào Tạo (ACA - Course)

| STT | HTTP Method | Endpoint URI | Phân Quyền (RBAC) | Tóm tắt Chức năng Nghiệp vụ | Request Body / Query Params | Mã Lỗi Chính |
|:---:|:---:|---|---|---|---|---|
| 20 | `GET` | `/api/admission/courses` | Public | Lấy danh mục khóa học đang mở tuyển sinh | `?level=BEGINNER&is_active=true` | N/A |
| 21 | `POST` | `/api/admission/courses` | STAFF, ADMIN | Tạo mới khóa học trong hệ thống | `{"code": "IELTS-6.5", "title": "...", "tuition_fee": 7500000, ...}` | `ADM_COURSE_CODE_EXISTS` |
| 22 | `GET` | `/api/admission/courses/{id}` | Public | Xem thông tin chi tiết và lộ trình khóa học | Path param `id` | `ADM_COURSE_NOT_FOUND` |
| 23 | `PUT` | `/api/admission/courses/{id}` | STAFF, ADMIN | Cập nhật tên, học phí, thời lượng khóa học | `{"title": "...", "tuition_fee": 8000000, ...}` | `ADM_COURSE_NOT_FOUND` |
| 24 | `DELETE`| `/api/admission/courses/{id}`| ADMIN | Xóa mềm hoặc ngưng tuyển sinh khóa học | Path param `id` | `ADM_COURSE_HAS_CLASSES` |

---

## 4. Phân Hệ Lớp Học & Điều Phối Sĩ Số (ACA - Class)

| STT | HTTP Method | Endpoint URI | Phân Quyền (RBAC) | Tóm tắt Chức năng Nghiệp vụ | Request Body / Query Params | Mã Lỗi Chính |
|:---:|:---:|---|---|---|---|---|
| 25 | `GET` | `/api/admission/classes` | Public | Danh sách lớp học kèm sĩ số và slot khả dụng | `?course_id=1&status=OPEN` | N/A |
| 26 | `POST` | `/api/admission/classes` | STAFF, ADMIN | Mở lớp học mới (Kiểm tra xung đột phòng & GV) | `{"course_id": 1, "room_id": 2, "teacher_id": "...", "max_students": 20, ...}` | `ADM_ROOM_CAPACITY_EXCEEDED`, `ADM_ROOM_CONFLICT`, `ADM_TEACHER_CONFLICT` |
| 27 | `GET` | `/api/admission/classes/{id}` | Public | Xem chi tiết thông tin lớp học và giảng viên | Path param `id` | `ADM_CLASS_NOT_FOUND` |
| 28 | `PUT` | `/api/admission/classes/{id}` | STAFF, ADMIN | Cập nhật thông tin lớp học | `{"name": "...", "room_id": 3, ...}` | `ADM_CLASS_NOT_FOUND` |
| 29 | `PATCH`| `/api/admission/classes/{id}/status`| STAFF, ADMIN | Chuyển trạng thái lớp (OPEN, IN_PROGRESS, COMPLETED, CANCELLED) | `{"status": "IN_PROGRESS"}` | `ADM_INVALID_STATE_TRANSITION` |
| 30 | `GET` | `/api/admission/classes/{id}/capacity`| Public | Lấy số chỗ khả dụng thời gian thực | Path param `id` | `ADM_CLASS_NOT_FOUND` |
| 31 | `POST` | `/api/admission/classes/check-conflict`| STAFF, ADMIN | API thử kiểm tra xung đột lịch trước khi lưu | `{"room_id": 2, "teacher_id": "...", "day_pattern": "...", "start_time": "...", ...}` | Trả về `{"has_conflict": true/false, ...}` |

---

## 5. Phân Hệ Khảo Thí Đầu Vào & Đề Xuất Lộ Trình (TST)

| STT | HTTP Method | Endpoint URI | Phân Quyền (RBAC) | Tóm tắt Chức năng Nghiệp vụ | Request Body / Query Params | Mã Lỗi Chính |
|:---:|:---:|---|---|---|---|---|
| 32 | `GET` | `/api/admission/tests/sets` | STAFF, ADMIN | Lấy danh sách các bộ đề thi khảo thí | `?is_active=true` | N/A |
| 33 | `POST` | `/api/admission/tests/sets` | STAFF, ADMIN | Tạo mới bộ đề thi khảo thí đầu vào | `{"code": "TEST-2026-A1", "title": "...", "duration_minutes": 45}` | `ADM_DUPLICATE_CODE` |
| 34 | `GET` | `/api/admission/tests/sets/{id}` | STAFF, ADMIN | Xem chi tiết bộ đề và danh sách câu hỏi gốc | Path param `id` | `ADM_TEST_NOT_FOUND` |
| 35 | `PUT` | `/api/admission/tests/sets/{id}` | STAFF, ADMIN | Cập nhật tiêu đề, thời lượng bộ đề | `{"title": "...", "duration_minutes": 60}` | `ADM_TEST_NOT_FOUND` |
| 36 | `POST` | `/api/admission/tests/sets/{id}/questions` | STAFF, ADMIN | Thêm câu hỏi 3 kỹ năng vào bộ đề | `{"skill": "LISTENING", "audio_url": "...", "correct_option": "B", ...}` | `ADM_INVALID_PAYLOAD` |
| 37 | `PUT` | `/api/admission/tests/questions/{id}`| STAFF, ADMIN | Chỉnh sửa nội dung câu hỏi, đáp án | `{"question_text": "...", "correct_option": "C"}` | `ADM_NOT_FOUND` |
| 38 | `DELETE`| `/api/admission/tests/questions/{id}`| STAFF, ADMIN | Xóa câu hỏi khỏi bộ đề | Path param `id` | `ADM_NOT_FOUND` |
| 39 | `GET` | `/api/admission/tests/public/{id}/start` | Public | Lấy đề thi để làm bài trực tuyến (ĐÃ GIẤU ĐÁP ÁN) | Path param `id` | `ADM_TEST_NOT_FOUND` |
| 40 | `POST` | `/api/admission/tests/public/submit` | Public | Nộp bài thi, tự động chấm điểm & đề xuất khóa học | `{"test_set_id": 1, "email": "...", "answers": [{"question_id": 10, "selected_option": "A"}]}` | `ADM_TEST_SUBMIT_ERROR` |
| 41 | `GET` | `/api/admission/tests/submissions/{id}` | Authed, STAFF | Xem lại kết quả bài thi chi tiết và điểm bóc tách | Path param `id` | `ADM_SUBMISSION_NOT_FOUND` |
| 42 | `GET` | `/api/admission/tests/rules` | STAFF, ADMIN | Lấy danh sách quy tắc đề xuất khóa học | `?test_set_id=1` | N/A |
| 43 | `POST` | `/api/admission/tests/rules` | STAFF, ADMIN | Cấu hình quy tắc đề xuất theo dải điểm | `{"test_set_id": 1, "min_score": 60.0, "max_score": 79.9, "recommended_course_id": 2}` | `ADM_RULE_OVERLAP` |

---

## 6. Phân Hệ Tuyển Sinh, Giữ Chỗ 48h & Webhook Xét Duyệt (ENR)

| STT | HTTP Method | Endpoint URI | Phân Quyền (RBAC) | Tóm tắt Chức năng Nghiệp vụ | Request Body / Query Params | Mã Lỗi Chính |
|:---:|:---:|---|---|---|---|---|
| 44 | `POST` | `/api/admission/enrollments` | Public, Authed | Nộp đơn tuyển sinh (Tự động cấp slot giữ chỗ 48h) | `{"class_id": 10, "email": "...", "full_name": "...", "phone": "..."}` | `ADM_CLASS_FULL`, `ADM_CLASS_NOT_OPEN` |
| 45 | `GET` | `/api/admission/enrollments` | STAFF, ADMIN | Danh sách đơn đăng ký tuyển sinh có phân trang | `?class_id=10&status=PENDING&page=0&size=20` | `ADM_FORBIDDEN` |
| 46 | `GET` | `/api/admission/enrollments/{id}` | Authed, STAFF | Xem chi tiết thông tin đơn và hạn giữ chỗ | Path param `id` | `ADM_ENROLLMENT_NOT_FOUND` |
| 47 | `POST` | `/api/admission/enrollments/{id}/extend-hold` | STAFF, ADMIN | Học vụ gia hạn thời gian giữ chỗ kèm lý do | `{"extended_hours": 24, "reason": "Chờ lương đầu tháng"}` | `ADM_INVALID_STATE_TRANSITION`, `ADM_CLASS_FULL` |
| 48 | `POST` | `/api/admission/enrollments/{id}/approve-manual`| STAFF, ADMIN | Duyệt đơn trực tiếp khi học viên nộp tiền mặt | `{"receipt_number": "PT-01", "payment_method": "CASH", "amount_received": 4500000}` | `ADM_CLASS_FULL` (INV-ADM-01), `ADM_INVALID_STATE_TRANSITION` |
| 49 | `PATCH`| `/api/admission/enrollments/{id}/cancel` | STAFF, Owner | Hủy đơn đăng ký tuyển sinh, giải phóng slot | `{"reason": "Học viên hủy lịch học"}` | `ADM_INVALID_STATE_TRANSITION` |
| 50 | `POST` | `/api/admission/webhooks/payment-success` | Internal (Finance) | Webhook nhận thanh toán PAID $\rightarrow$ Tự động duyệt đơn | `{"event_id": "...", "enrollment_id": "...", "invoice_id": "...", "amount_paid": ...}` | `ADM_CLASS_FULL`, `ADM_ENROLLMENT_NOT_FOUND` |

---

## 7. Phân Hệ Xuất Dữ Liệu & Báo Cáo Vận Hành (OPS)

| STT | HTTP Method | Endpoint URI | Phân Quyền (RBAC) | Tóm tắt Chức năng Nghiệp vụ | Request Body / Query Params | Định Dạng File Trả Về |
|:---:|:---:|---|---|---|---|---|
| 51 | `GET` | `/api/admission/exports/classes/{id}/roster` | STAFF, TEACHER, ADMIN | Xuất danh sách học viên lớp học ra file | `?format=csv` (hoặc `xlsx`) | `text/csv; charset=UTF-8` |
| 52 | `GET` | `/api/admission/exports/tests/{id}/results` | STAFF, ADMIN | Xuất bảng điểm khảo thí đầu vào | `?format=csv` (hoặc `xlsx`) | `text/csv; charset=UTF-8` |

---

## 8. Phân Hệ Báo Cáo Thông Minh BI Tuyển Sinh (BI & KPIs)

| STT | HTTP Method | Endpoint URI | Phân Quyền (RBAC) | Tóm tắt Chức năng Nghiệp vụ | Query Parameters | Response Key Metrics |
|:---:|:---:|---|---|---|---|---|
| 53 | `GET` | `/api/admission/bi/funnel` | STAFF, ADMIN | Dữ liệu phễu chuyển đổi 4 giai đoạn & 4 KPIs | `?from_date=2026-10-01&to_date=2026-10-31` | `stages[]`, `kpis: {test_completion_rate, test_to_enrollment_rate, paid_conversion_rate, expired_hold_rate}` |
| 54 | `GET` | `/api/admission/bi/courses-revenue` | STAFF, ADMIN | Báo cáo doanh thu tiềm năng 48h, thực thu & lấp đầy | `?from_date=2026-10-01&to_date=2026-10-31` | `pipeline_potential_revenue`, `realized_admission_revenue`, `average_occupancy_rate`, `top_courses[]` |
| 55 | `GET` | `/api/admission/bi/security-engagement` | ADMIN | Thống kê DAU/MAU và cảnh báo Brute-force | `?days=30` | `engagement: {dau, mau, by_role}`, `security: {failed_login_rate, suspicious_ips[]}` |

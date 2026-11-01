# TASK-ADM-01: Khởi tạo Schema PostgreSQL 12 Bảng, Ràng buộc DDL & Dữ liệu Mẫu

- **Mã nhiệm vụ**: `TASK-ADM-01`
- **Phân kỳ**: `Phase 0: Nền móng & Hạ tầng (INF)`
- **Độ ưu tiên**: `P0 (Bắt buộc)`
- **Yêu cầu chức năng liên quan**: Toàn bộ hệ thống (`admission-schema-spec.md`)
- **Quy tắc bất biến bảo vệ**: `INV-SYS-02` (Cô lập độc lập 4 schema PostgreSQL)

---

## 1. Mục tiêu Nghiệp vụ & Kỹ thuật
Thiết lập toàn bộ 12 bảng thuộc schema `admission` trong cơ sở dữ liệu PostgreSQL 16 theo tài liệu `admission-schema-spec.md`, bao gồm:
1. Tạo 12 bảng dữ liệu: `users`, `refresh_tokens`, `password_reset_tokens`, `auth_audit_logs`, `rooms`, `courses`, `classes`, `enrollments`, `test_sets`, `test_questions`, `test_recommendation_rules`, `test_submissions`.
2. Tạo các ràng buộc toàn vẹn: Khóa ngoại, `CHECK` constraint (thang điểm, số lượng, khoảng thời gian).
3. Thiết lập các chỉ mục tối ưu hóa hiệu năng truy vấn (B-Tree, Partial Index cho `is_revoked`, `hold_expires_at`).
4. Thiết lập Trigger `set_updated_at` tự động cập nhật thời gian sửa đổi cho các bảng nghiệp vụ.
5. Cập nhật Entity JPA trong Java Spring Boot phản ánh đúng schema (sử dụng `@Table(name = "...", schema = "admission")`).

---

## 2. Phạm vi File Tác động

### File tạo mới hoặc chỉnh sửa:
- `services/admission/backend/src/main/resources/db/migration/V1__init_admission_schema.sql` (hoặc cập nhật `scripts/init-db.sql`)
- Các JPA Entity tương ứng trong package `com.englishcenter.admission.entity.*`:
  - `BaseEntity.java` (`@MappedSuperclass` chứa `created_at`, `updated_at`)
  - `User.java`
  - `RefreshToken.java`
  - `PasswordResetToken.java`
  - `AuthAuditLog.java`
  - `Room.java`
  - `Course.java`
  - `ClassEntity.java` (hoặc `ClassRoom.java`)
  - `Enrollment.java`
  - `TestSet.java`
  - `TestQuestion.java`
  - `TestRecommendationRule.java`
  - `TestSubmission.java`

### File cấm sửa đổi:
- `tests/invariants/*`
- Schema của các service khác trong cơ sở dữ liệu (`student.*`, `learning.*`, `finance.*`)

---

## 3. Đặc tả 12 Bảng Thuộc Schema `admission`

```
1.  admission.users                     - Tài khoản người dùng (Admin, Staff, Teacher, Student)
2.  admission.refresh_tokens            - Phiên đăng nhập & Refresh Token stateful
3.  admission.password_reset_tokens     - Mã xác thực đặt lại mật khẩu 15 phút
4.  admission.auth_audit_logs           - Nhật ký kiểm toán an toàn thông tin
5.  admission.rooms                     - Phòng học & Chi nhánh
6.  admission.courses                   - Danh mục khóa học & Lộ trình đào tạo
7.  admission.classes                   - Lớp học mở theo khóa học & phòng học
8.  admission.enrollments               - Đơn đăng ký tuyển sinh & Giữ chỗ 48h
9.  admission.test_sets                 - Ngân hàng bộ đề khảo thí đầu vào
10. admission.test_questions            - Câu hỏi trắc nghiệm 3 kỹ năng (Listening, Reading, Grammar)
11. admission.test_recommendation_rules - Quy tắc đề xuất khóa học theo điểm số
12. admission.test_submissions          - Bài nộp khảo thí & Điểm số bóc tách
```

---

## 4. Kế hoạch Triển khai (Step-by-step)
1. Viết script DDL chuẩn trong `services/admission/backend/src/main/resources/schema.sql` hoặc Flyway migration script, định nghĩa đầy đủ 12 bảng với schema prefix `admission.`.
2. Tạo các `CHECK` constraint:
   - `users.role IN ('ADMIN', 'STAFF', 'TEACHER', 'STUDENT')`
   - `classes.status IN ('OPEN', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED')`
   - `enrollments.status IN ('PENDING', 'APPROVED', 'CANCELLED', 'EXPIRED')`
   - `test_questions.skill IN ('LISTENING', 'READING', 'GRAMMAR')`
3. Tạo các chỉ mục tối ưu:
   - `idx_enrollments_class_status` trên `enrollments(class_id, status)`
   - `idx_enrollments_pending_hold` trên `enrollments(hold_expires_at) WHERE status = 'PENDING'`
   - `idx_refresh_tokens_token` trên `refresh_tokens(token_hash)`
4. Xây dựng `BaseEntity.java` kế thừa cho các thực thể để tự động gán `created_at` và `updated_at`.
5. Tạo các JPA Entity tương ứng trong package `com.englishcenter.admission.entity`, đánh dấu `@Table(schema = "admission", name = "...")`.

---

## 5. Tiêu chí Nghiệm thu (Acceptance Criteria)
- [ ] Khởi chạy cơ sở dữ liệu PostgreSQL, schema `admission` có đủ 12 bảng.
- [ ] Cố tình chèn sai `role` hoặc `status` bị PostgreSQL chặn bởi `CHECK` constraint.
- [ ] Chạy test invariant `INV-SYS-02` đạt `OK`:
  ```bash
  python3 -m unittest discover -s tests/invariants -p "test_system_invariants.py" -v
  ```

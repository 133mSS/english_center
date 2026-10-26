# 🎓 English Center Management System (Microservices)

Dự án website quản lý đăng ký và học tập tại trung tâm Anh ngữ, phát triển theo kiến trúc Microservices Polyglot (Java Spring Boot + Python FastAPI + Vanilla JS/HTML/CSS) trên nền tảng Docker.

---

## 🚀 Khởi động nhanh (Quick Start)

Yêu cầu máy đã cài đặt [Docker](https://docs.docker.com/get-docker/) & [Docker Compose](https://docs.docker.com/compose/).

```bash
# 1. Clone repository (nếu chưa clone)
cd Software_Engineering

# 2. Tạo file môi trường từ file mẫu (đã có sẵn .env)
cp .env.example .env

# 3. Khởi chạy toàn bộ hệ thống
docker compose up -d --build
```

Sau khi các container khởi động xong (khoảng 1–2 phút cho lần build đầu tiên):

* 🌐 **Cổng thông tin tổng quan (Portal):** [http://localhost:8080](http://localhost:8080)
* 🔐 **Trang đăng nhập:** [http://localhost:8080/shared/login.html](http://localhost:8080/shared/login.html)
* 📋 **Tuyển sinh & Khóa học (Admission):** [http://localhost:8080/admission/courses.html](http://localhost:8080/admission/courses.html)
* 👤 **Học viên (Student):** [http://localhost:8080/student/students.html](http://localhost:8080/student/students.html)
* 📚 **Học tập & Học liệu (Learning):** [http://localhost:8080/learning/materials.html](http://localhost:8080/learning/materials.html)
* 💰 **Tài chính & Hóa đơn (Finance):** [http://localhost:8080/finance/invoices.html](http://localhost:8080/finance/invoices.html)

---

## 👥 Tài khoản thử nghiệm (1-Click Login)

Dữ liệu đã được nạp sẵn tự động trong cơ sở dữ liệu:

| Vai trò | Email | Mật khẩu | Phù hợp kiểm thử |
|---|---|---|---|
| **Admin** | `admin@english.edu.vn` | `admin123` | Toàn quyền quản trị |
| **Học vụ (Staff)** | `staff@english.edu.vn` | `staff123` | Quản lý khóa học, tiếp nhận học viên |
| **Giáo viên** | `teacher@english.edu.vn` | `teacher123` | Điểm danh, nhập điểm, đăng học liệu |
| **Học viên** | `student@english.edu.vn` | `student123` | Xem lớp, tra cứu học liệu, đóng học phí |

---

## 🏗️ Cấu trúc hệ thống & Port Mapping

```
English Center Monorepo
├── gateway/           # Nginx API Gateway & Static Server (Port 8080)
├── shared/            # Design System (CSS/JS) dùng chung cho tất cả giao diện
├── docs/              # Tài liệu kiến trúc, API convention, Git workflow
├── scripts/           # SQL script khởi tạo schemas & dữ liệu mẫu ban đầu
└── services/
    ├── admission/     # Service Tuyển sinh (Java Spring Boot 3.3 - Port 8081)
    ├── student/       # Service Học viên (Python FastAPI - Port 8082)
    ├── learning/      # Service Học tập (Python FastAPI - Port 8083)
    └── finance/       # Service Tài chính (Python FastAPI - Port 8084)
```

Cơ sở dữ liệu **PostgreSQL** (Port 5432) gồm 4 schema cách ly:
* `admission`: `users`, `courses`, `classes`, `enrollments`
* `student`: `students`, `attendance`
* `learning`: `materials`, `grades`
* `finance`: `tuition_fees`, `invoices`, `payments`

---

## ⚡ Hướng dẫn phát triển độc lập theo nhóm (Hot Reload)

Mỗi nhóm 2 thành viên phụ trách 1 phân hệ trong `services/{tên_service}`:

1. **Frontend (HTML/JS/CSS)**:
   * Thư mục `services/{service}/frontend/` được Nginx ánh xạ trực tiếp.
   * **Khi chỉnh sửa HTML/JS/CSS, chỉ cần lưu file và Refresh trình duyệt (F5)**, không cần build hay restart Docker!
2. **Backend**:
   * Các service FastAPI (`student`, `learning`, `finance`) được mount thư mục mã nguồn và bật chế độ `--reload`. Khi sửa code Python, server sẽ tự động restart ngay tức thì.
   * Service Spring Boot (`admission`) có thể chạy trực tiếp trong IDE (IntelliJ IDEA/Eclipse) kết nối vào PostgreSQL `localhost:5432`.

---


---

## 📋 Quy trình báo cáo tiến độ (Worklog theo Version)

Dự án áp dụng mô hình **Lặp và Tăng trưởng (Iterative & Incremental)** với các phiên bản Version 1.0, 2.0, 3.0...
* Toàn bộ tiến độ được theo dõi tập trung tại file: **[docs/worklog.md](docs/worklog.md)**.
* **Quy ước cho các nhóm:** Trong từng đợt làm việc, mỗi nhóm chịu trách nhiệm tự cập nhật 2 cột:
  * **Phần DT (Đặc tả):** Ghi rõ yêu cầu nghiệp vụ, luồng xử lý, thay đổi dữ liệu của nhóm.
  * **Phần rAI:** Ghi rõ mã nguồn, API, kiểm thử và rà soát kỹ thuật.
* **Quy ước cho Leader:** Leader sẽ nghiệm thu từng đợt, chính thức đặt tên cho từng Version và ghi nhận xét đánh giá.

## 📖 Tài liệu kỹ thuật tham khảo

Xem chi tiết trong thư mục `docs/`:
* [docs/worklog.md](docs/worklog.md): Nhật ký tiến độ các đợt Version của dự án.
* [docs/spec.md](docs/spec.md): Đặc tả nghiệp vụ PRD 4 phân hệ.
* [docs/architecture.md](docs/architecture.md): Quyền sở hữu dữ liệu, nguyên tắc giao tiếp giữa các service.
* [docs/api-conventions.md](docs/api-conventions.md): Chuẩn REST API, mã lỗi, định dạng JSON `snake_case`.
* [docs/design-system.md](docs/design-system.md): Bảng màu, typography, CSS class components chuẩn.
* [docs/git-workflow.md](docs/git-workflow.md): Quy ước đặt tên branch, commit và review Pull Request.

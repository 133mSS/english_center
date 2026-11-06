# Git Workflow - Trung tâm Anh ngữ

> Quy trình Git cho nhóm 9 người làm việc trên cùng 1 monorepo.

## 1. Branch Strategy

```
main ─────────────────────────────────── (production-ready, chỉ merge từ develop)
  │
  └── develop ────────────────────────── (nhánh tích hợp chính)
        │
        ├── feature/admission/course-crud     (team Admission)
        ├── feature/admission/enrollment-flow
        ├── feature/student/profile-crud      (team Student)
        ├── feature/student/attendance
        ├── feature/learning/material-crud    (team Learning)
        ├── feature/learning/grade-entry
        ├── feature/finance/tuition-config    (team Finance)
        ├── feature/finance/payment-flow
        └── feature/infra/docker-setup        (Infra)
```

### Branch naming convention

```
feature/{service}/{mô-tả-ngắn}     # Tính năng mới
bugfix/{service}/{mô-tả-ngắn}      # Sửa bug
hotfix/{mô-tả-ngắn}                # Fix gấp trên main
```

**Ví dụ:**
- `feature/admission/course-crud`
- `feature/finance/payment-recording`
- `bugfix/student/attendance-date-bug`
- `feature/infra/nginx-config`

**Quy tắc:**
- Tên branch dùng **tiếng Anh, lowercase, ngăn cách bằng dấu gạch ngang**
- Mỗi branch chỉ làm **1 tính năng hoặc 1 task**
- Không commit trực tiếp vào `main` hoặc `develop`

---

## 2. Workflow hàng ngày

### Bắt đầu task mới

```bash
# 1. Lấy code mới nhất
git checkout develop
git pull origin develop

# 2. Code...
# 3. Commit thường xuyên (xem quy tắc commit bên dưới)
git add .
git commit -m "feat(admission): add course CRUD API"

# 4. Push lên remote
git push origin feature/admission

# 5. Tạo Pull Request vào develop trên GitHub/GitLab
```

### Review & Merge

1. Tạo Pull Request (PR) từ feature branch → `develop`
2. Gán **ít nhất 1 reviewer** (nên là người trong team khác hoặc lead)
3. Reviewer check code, comment nếu cần sửa
4. Sau khi approve → **Squash and Merge** vào `develop`
5. Xóa feature branch sau khi merge

### Giải quyết conflict

```bash
# Khi branch của bạn bị conflict với develop
git checkout feature/admission/course-crud
git pull origin develop
# Giải quyết conflict trong editor
git add .
git commit -m "merge: resolve conflict with develop"
git push
```

---

## 3. Commit Message Convention

Sử dụng format [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <mô tả ngắn>
```

### Types

| Type | Khi nào dùng |
|---|---|
| `feat` | Thêm tính năng mới |
| `fix` | Sửa bug |
| `docs` | Cập nhật tài liệu |
| `style` | Sửa CSS, format code (không đổi logic) |
| `refactor` | Tái cấu trúc code (không thêm tính năng, không sửa bug) |
| `chore` | Cập nhật config, dependencies |

### Scopes

| Scope | Service |
|---|---|
| `admission` | Admission service |
| `student` | Student service |
| `learning` | Learning service |
| `finance` | Finance service |
| `infra` | Docker, Nginx, DB, shared assets |
| `docs` | Tài liệu |

### Ví dụ

```
feat(admission): add course CRUD API endpoints
feat(student): implement attendance marking page
fix(finance): correct payment total calculation
docs: update API conventions for pagination
chore(infra): add PostgreSQL health check to docker-compose
style(admission): fix table alignment on course list page
```

---

## 4. Quy tắc quan trọng

### ✅ NÊN

- Commit thường xuyên, mỗi commit là 1 thay đổi có ý nghĩa
- Pull `develop` vào branch của bạn ít nhất **1 lần/ngày** để tránh conflict lớn
- Viết commit message rõ ràng bằng tiếng Anh
- Tạo PR nhỏ, dễ review (< 500 dòng thay đổi)
- Test cơ bản trước khi tạo PR

### ❌ KHÔNG NÊN

- Commit file `.env` (chứa secret) → dùng `.env.example`
- Commit `node_modules/`, `__pycache__/`, `.class`, `target/`, `venv/`
- Force push lên `develop` hoặc `main`
- Merge PR mà chưa ai review
- Commit code bị lỗi syntax vào `develop`

---

## 5. Cấu trúc `.gitignore`

```gitignore
# Dependencies
node_modules/
venv/
.venv/
__pycache__/

# Java/Maven
target/
*.class
*.jar

# Environment
.env
*.env.local

# IDE
.idea/
.vscode/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Build output
dist/
build/
```

---

## 6. Protected Branches

Nếu dùng GitHub/GitLab, nên bật:

| Branch | Quy tắc |
|---|---|
| `main` | Require PR + 1 approval, no direct push |
| `develop` | Require PR + 1 approval, no direct push |

---

## 7. Release Flow

Khi chuẩn bị demo:

```
1. Tất cả feature branches → merge vào develop
2. Test trên develop
3. Tạo PR: develop → main
4. Review tổng thể
5. Merge vào main
6. Tag version: git tag v0.1.0
```

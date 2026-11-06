# ĐẶC TẢ KIẾN TRÚC & KỸ THUẬT (TECHNICAL SPECIFICATION)
## FINANCE SERVICE – PYTHON FASTAPI

> **Dự án:** Hệ thống Quản lý Trung tâm Anh ngữ  
> **Service:** `finance-service`  
> **Port nội bộ:** `8084` (theo `docs/architecture.md`)  
> **Gateway:** Nginx `8080`, prefix `/api/finance/`  
> **Backend:** Python 3.11+, FastAPI 0.115.0, SQLAlchemy 2.0.35, Pydantic 2.9.2  
> **Database:** PostgreSQL 16, schema `finance`  
> **Phiên bản:** 1.0

---

## MỤC LỤC
1. [Tổng quan Kỹ thuật](#1-tổng-quan-kỹ-thuật)
2. [Tech Stack & Cấu trúc Module](#2-tech-stack--cấu-trúc-module)
3. [Cấu hình Runtime & Database Connection](#3-cấu-hình-runtime--database-connection)
4. [Kiến trúc Backend](#4-kiến-trúc-backend)
5. [API Contract đang triển khai](#5-api-contract-đang-triển-khai)
6. [Pydantic Request Models](#6-pydantic-request-models)
7. [Luồng Xử lý & Transaction](#7-luồng-xử-lý--transaction)
8. [Frontend Integration](#8-frontend-integration)
9. [Security, Error Handling & Operational Notes](#9-security-error-handling--operational-notes)

---

## 1. Tổng quan Kỹ thuật

Finance Service chịu trách nhiệm cấu hình học phí, lập hóa đơn và ghi nhận thanh toán. Backend hiện dùng FastAPI kết hợp SQLAlchemy text query, kết nối PostgreSQL và đặt search path vào schema `finance`.

Các route được xác nhận trong `services/finance/backend/main.py`:
- `GET /api/finance/health`
- `GET /api/finance/tuition-fees`
- `POST /api/finance/tuition-fees`
- `GET /api/finance/invoices`
- `POST /api/finance/invoices`
- `GET /api/finance/payments`
- `POST /api/finance/payments`


---

## 2. Tech Stack & Cấu trúc Module

| Thành phần | Công nghệ/phiên bản | Vai trò |
|---|---|---|
| Runtime | Python 3.11+ | Runtime ứng dụng |
| API Framework | FastAPI 0.115.0 | HTTP API |
| ASGI Server | Uvicorn 0.31.0 | Chạy ứng dụng |
| Validation | Pydantic 2.9.2 | Validate request body |
| ORM/SQL Toolkit | SQLAlchemy 2.0.35 | Engine, Session và SQL execution |
| PostgreSQL Driver | psycopg2-binary 2.9.9 | Kết nối PostgreSQL |
| JWT library | python-jose 3.3.0 | Dependency được pin; route Finance trong main.py chưa sử dụng trực tiếp |
| Frontend | HTML, JavaScript, CSS | Giao diện biểu phí và hóa đơn |
| Gateway | Nginx | Routing và shared static assets |
| Container | Docker | Đóng gói service |

### Dependencies hiện tại

```text
fastapi==0.115.0
uvicorn[standard]==0.31.0
pydantic==2.9.2
psycopg2-binary==2.9.9
sqlalchemy==2.0.35
python-jose[cryptography]==3.3.0
```

---

## 3. Cấu hình Runtime & Database Connection

Backend đọc các biến môi trường:
- `DB_USER` (default trong code: `postgres`)
- `DB_PASSWORD` (default trong code: `postgres_secret_password`)
- `DB_HOST` (default: `postgres`)
- `DB_PORT` (default: `5432`)
- `DB_NAME` (default: `english_center`)

Kết nối:
- SQLAlchemy `create_engine(DATABASE_URL)`.
- `connect_args={"options": "-csearch_path=finance,public"}`.
- Session factory dùng `autocommit=False`, `autoflush=False`.

**Lưu ý cấu hình:** Không dùng password mặc định trong môi trường triển khai thật. Secret phải được truyền qua environment hoặc secret manager. CORS hiện bật wildcard cho origins/methods/headers; cần giới hạn theo môi trường.

---

## 4. Kiến trúc Backend

```text
HTTP Request
   |
   v
FastAPI Route
   |
   +--> Pydantic Request Validation
   |
   v
SQLAlchemy SessionLocal
   |
   v
SQL text statements (finance schema)
   |
   v
PostgreSQL
   |
   v
JSON response {success, data, message}
```

Trong `main.py`, các route nghiệp vụ truy cập DB qua SQLAlchemy text query. Có thể tổ chức lớp Repository/Service riêng khi mở rộng module; cần giữ contract hiện hữu hoặc cập nhật frontend đồng bộ.

---

## 5. API Contract đang triển khai

Prefix: `/api/finance`.

| Method | Endpoint | Query/Body | Hành vi |
|---|---|---|---|
| GET | `/health` | – | Trả status, service, version, framework. |
| GET | `/tuition-fees` | `course_id?` | Danh sách biểu phí hoặc lọc theo khóa học. |
| POST | `/tuition-fees` | TuitionFeeCreate | Tạo/cập nhật biểu phí theo course_id; HTTP 201. |
| GET | `/invoices` | `student_id?` | Danh sách hóa đơn; cập nhật UNPAID quá hạn thành OVERDUE; bổ sung paid_amount, remaining_amount. |
| POST | `/invoices` | InvoiceCreate | Tạo hóa đơn; HTTP 201; có thể tính số tiền từ tuition_fee_id. |
| GET | `/payments` | `invoice_id?` | Danh sách payment hoặc lọc theo hóa đơn. |
| POST | `/payments` | PaymentCreate | Ghi nhận thanh toán; khóa invoice và cập nhật PAID khi đủ tiền; HTTP 201. |

### 5.1. GET /api/finance/tuition-fees
- Query `course_id` tùy chọn.
- Không truyền filter: trả danh sách theo `created_at DESC`.
- Có `course_id`: trả biểu phí theo khóa học.
- Response có `success=true`, `data=[...]`.

### 5.2. POST /api/finance/tuition-fees

```json
{
  "course_id": 1,
  "amount": 6500000,
  "currency": "VND",
  "discount_code": "EARLYBIRD500",
  "discount_amount": 500000,
  "note": "Ưu đãi đăng ký sớm"
}
```

Quy tắc:
- amount phải > 0.
- discount_amount >= 0 và không được lớn hơn amount.
- Dùng `ON CONFLICT (course_id) DO UPDATE`.
- HTTP 201 khi lưu thành công.

### 5.3. GET /api/finance/invoices
- Query `student_id` tùy chọn.
- Trước SELECT, cập nhật invoice `UNPAID` có due_date nhỏ hơn CURRENT_DATE thành `OVERDUE`.
- LEFT JOIN tuition_fees để lấy discount_code/discount_amount.
- LEFT JOIN payments để tính `paid_amount` và `remaining_amount`.
- Không có pagination trong code hiện tại.

### 5.4. POST /api/finance/invoices

Request model:
- `invoice_code` optional.
- `student_id` bắt buộc.
- `enrollment_id` optional.
- `tuition_fee_id` optional.
- `amount` optional.
- `due_date` optional ở Pydantic model, nhưng DDL yêu cầu NOT NULL.

Quy tắc:
- Nếu có tuition_fee_id, đọc biểu phí; nếu request không truyền amount hợp lệ thì tính `amount - discount_amount`.
- Amount cuối cùng phải > 0.
- Nếu invoice_code rỗng, sinh `INV-<6 ký tự hex>`.
- Kiểm tra trùng mã trước INSERT.
- Trạng thái đầu: UNPAID; nếu due_date ở quá khứ: OVERDUE.

### 5.5. GET /api/finance/payments
- Query `invoice_id` optional.
- Trả payment theo `paid_at DESC`.

### 5.6. POST /api/finance/payments

```json
{
  "invoice_id": 1,
  "amount": 3000000,
  "payment_method": "BANK_TRANSFER",
  "transaction_ref": "FT261015998811"
}
```

Quy tắc:
- amount > 0.
- payment_method chỉ nhận CASH hoặc BANK_TRANSFER.
- transaction_ref bắt buộc, không rỗng và phải duy nhất.
- Invoice không được ở trạng thái CANCELLED.
- Row lock invoice bằng `SELECT ... FOR UPDATE`.
- Khi SUM(payments.amount) >= invoices.amount thì cập nhật invoice sang PAID.

---

## 6. Pydantic Request Models

### 6.1. TuitionFeeCreate

| Field | Type | Constraint | Default |
|---|---|---|---|
| `course_id` | int | required | – |
| `amount` | float | gt=0 | – |
| `currency` | str | – | VND |
| `discount_code` | Optional[str] | – | null |
| `discount_amount` | float | ge=0 | 0.0 |
| `note` | Optional[str] | – | null |

### 6.2. InvoiceCreate

| Field | Type | Constraint | Default |
|---|---|---|---|
| `invoice_code` | Optional[str] | – | null |
| `student_id` | int | required | – |
| `enrollment_id` | Optional[int] | – | null |
| `tuition_fee_id` | Optional[int] | – | null |
| `amount` | Optional[float] | – | null |
| `due_date` | Optional[date] | – | null |

### 6.3. PaymentCreate

| Field | Type | Constraint | Default |
|---|---|---|---|
| `invoice_id` | int | required | – |
| `amount` | float | gt=0 | – |
| `payment_method` | str | CASH hoặc BANK_TRANSFER | BANK_TRANSFER |
| `transaction_ref` | str | min_length=1 | – |

---

## 7. Luồng Xử lý & Transaction

### 7.1. Cập nhật biểu phí

```text
POST tuition-fees
  -> validate amount and discount
  -> INSERT ... ON CONFLICT(course_id) DO UPDATE
  -> COMMIT
  -> return saved tuition fee
```

### 7.2. Tạo hóa đơn

```text
POST invoices
  -> resolve tuition_fee_id (if supplied)
  -> determine amount
  -> generate/check invoice_code
  -> determine UNPAID or OVERDUE
  -> INSERT invoice
  -> COMMIT
```

### 7.3. Ghi nhận thanh toán

```text
POST payments
  -> validate amount / transaction_ref
  -> SELECT invoice FOR UPDATE
  -> reject missing or CANCELLED invoice
  -> reject duplicate transaction_ref
  -> INSERT payment
  -> SUM payments for invoice
  -> UPDATE invoice status = PAID if total_paid >= amount
  -> COMMIT
```

Row lock trên invoice giúp tuần tự hóa các thanh toán đồng thời của cùng hóa đơn trong transaction hiện tại. UNIQUE constraint trên transaction_ref là lớp bảo vệ bổ sung chống mã giao dịch trùng.

---

## 8. Frontend Integration

### 8.1. tuition.html
Frontend gọi:
- `GET /api/admission/courses` để nạp danh mục khóa học.
- `GET /api/finance/tuition-fees` để hiển thị biểu phí.
- `POST /api/finance/tuition-fees` để lưu biểu phí.

UI hiển thị học phí chuẩn, mã giảm giá, số tiền giảm, học phí sau giảm và ghi chú.

### 8.2. invoices.html
Frontend gọi:
- `GET /api/finance/tuition-fees` để nạp lựa chọn biểu phí.
- `GET /api/finance/invoices` để hiển thị danh sách.
- `POST /api/finance/invoices` để lập hóa đơn.
- `POST /api/finance/payments` để ghi nhận khoản thu.
- `GET /api/finance/payments?invoice_id=...` để xem lịch sử thu.

Frontend có thể tạo transaction_ref mặc định khi mở form; backend vẫn xác minh tính duy nhất.

---

## 9. Security, Error Handling & Operational Notes

- `main.py` hiện không thể hiện dependency xác thực JWT hoặc kiểm tra role trên route Finance. Include `auth.js` ở frontend không thay thế authorization phía server.
- `CORSMiddleware` đang cấu hình wildcard; cần giới hạn origin phù hợp.
- DB password có fallback value trong code; môi trường deployment phải override bằng secret.
- Response lỗi dùng `HTTPException` với detail string; chưa đồng nhất hoàn toàn với error envelope chung.
- GET list chưa hỗ trợ pagination.
- Tiền trong request model đang dùng float; nên cân nhắc Decimal khi chuẩn hóa xử lý tiền tệ.
- Không ghi log credential, JWT secret hoặc thông tin tài khoản ngân hàng đầy đủ.

---

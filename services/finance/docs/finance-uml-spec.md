# ĐẶC TẢ THIẾT KẾ MÔ HÌNH HÓA UML (UML DESIGN SPECIFICATION)
## PHÂN HỆ TÀI CHÍNH (FINANCE SERVICE)

> **Service:** `finance-service`  
> **Port:** `8083`  
> **Gateway:** `/api/finance/...`  
> **Schema:** `finance`  
> **Chuẩn khóa:** SERIAL / INTEGER  
> **Phiên bản thiết kế:** Finance Module 2.0

---

## MỤC LỤC
1. [Tổng quan Mô hình hóa](#1-tổng-quan-mô-hình-hóa)
2. [Sơ đồ Use Case Tổng thể](#2-sơ-đồ-use-case-tổng-thể)
3. [Sơ đồ Tuần tự: Sinh Hóa đơn và Gạch nợ VietQR](#3-sơ-đồ-tuần-tự-sinh-hóa-đơn-và-gạch-nợ-vietqr)
4. [Sơ đồ Tuần tự: Phê duyệt Hoàn tiền 3 cấp](#4-sơ-đồ-tuần-tự-phê-duyệt-hoàn-tiền-3-cấp)
5. [Sơ đồ Thực thể Liên kết ERD](#5-sơ-đồ-thực-thể-liên-kết-erd)

---

## 1. Tổng quan Mô hình hóa

Finance Service gồm các nhóm nghiệp vụ: tự động sinh hóa đơn, thiết lập Installments, thu tiền mặt, thanh toán VietQR, quản lý ví bảo lưu, xử lý hoàn tiền 3 cấp và báo cáo BI.

Các tác nhân:
- **Học viên (STUDENT):** sử dụng VietQR.
- **Tư vấn viên (STAFF):** chốt đăng ký, khởi tạo yêu cầu hoàn tiền.
- **Kế toán (STAFF):** ghi nhận tiền mặt, quản lý ví, xác minh và hoàn tất hoàn tiền.
- **Giám đốc (ADMIN):** phê duyệt hoàn tiền và xem báo cáo.
- **Cổng VietQR (Webhook):** gửi thông tin giao dịch.
- **Admission Service:** gọi Finance để sinh hóa đơn.
- **Learning Service:** cung cấp tổng số buổi và số buổi học viên tham gia.

---

## 2. Sơ đồ Use Case Tổng thể

```mermaid
flowchart LR
    Student["Học viên (STUDENT)"]
    Advisor["Tư vấn viên (STAFF)"]
    Accountant["Kế toán (STAFF)"]
    Director["Giám đốc (ADMIN)"]
    VietQR["Cổng VietQR (Webhook)"]

    subgraph Finance["Finance Service - Port 8083 - Schema finance"]
        UC01["UC01: Tự động sinh Hóa đơn khi chốt đăng ký<br/>(Gộp/Tách phí học lại, Áp mã Voucher)"]
        UC02["UC02: Thiết lập lịch đóng phí nhiều đợt (Installments)"]
        UC03["UC03: Thu tiền mặt tại quầy (CASH)"]
        UC04["UC04: Quét mã VietQR và tự động gạch nợ"]
        UC05["UC05: Quản lý Ví bảo lưu và cấn trừ khóa sau"]
        UC06["UC06: Tạo yêu cầu hoàn tiền - Cấp 1"]
        UC07["UC07: Xác minh công nợ và buổi thực học - Cấp 2"]
        UC08["UC08: Phê duyệt hoàn tiền và quản lý Voucher - Cấp 3"]
        UC09["UC09: Xem báo cáo BI doanh thu thực thu và Voucher"]
    end

    Advisor --> UC01
    Advisor --> UC02
    Advisor --> UC06
    Student --> UC04
    Accountant --> UC03
    Accountant --> UC05
    Accountant --> UC07
    Accountant --> UC09
    VietQR --> UC04
    Director --> UC08
    Director --> UC09
```

### 2.1. Danh sách Use Case

| Mã | Use Case | Tác nhân chính |
|---|---|---|
| UC01 | Tự động sinh hóa đơn khi chốt đăng ký; gộp/tách phí học lại và áp Voucher | Tư vấn viên / Admission |
| UC02 | Thiết lập lịch đóng phí nhiều đợt | Tư vấn viên / Admission |
| UC03 | Thu tiền mặt tại quầy | Kế toán |
| UC04 | Quét mã VietQR và tự động gạch nợ | Học viên, Cổng VietQR |
| UC05 | Quản lý ví bảo lưu và cấn trừ khóa sau | Kế toán |
| UC06 | Tạo yêu cầu hoàn tiền, kiểm tra số buổi học | Tư vấn viên |
| UC07 | Xác minh công nợ và buổi thực học | Kế toán |
| UC08 | Phê duyệt hoàn tiền và quản lý chiến dịch Voucher | Giám đốc |
| UC09 | Xem báo cáo BI doanh thu thực thu và Voucher | Kế toán, Giám đốc |

---

## 3. Sơ đồ Tuần tự: Sinh Hóa đơn và Gạch nợ VietQR

Sơ đồ thể hiện luồng từ lúc tư vấn viên chốt đăng ký trên Admission, Finance tự động sinh hóa đơn và lịch thanh toán, đến khi học viên thanh toán qua VietQR và hệ thống tự động gạch nợ.

```mermaid
sequenceDiagram
    autonumber
    actor Staff as Tư vấn viên (STAFF)
    participant Gw as Nginx Gateway
    participant Adm as Admission Service (:8081)
    participant Fin as Finance Service (:8083)
    participant DB as PostgreSQL (finance)
    actor Student as Học viên (STUDENT)
    participant Bank as Cổng VietQR / Ngân hàng

    Staff->>Gw: POST /api/admission/enrollments
    Gw->>Adm: Chuyển tiếp request kèm JWT (role=STAFF)
    Adm->>Fin: POST /api/finance/invoices/auto-generate
    Fin->>DB: SELECT Voucher FOR UPDATE
    Fin->>Fin: Kiểm tra điều kiện và tăng current_uses
    Fin->>DB: INSERT finance.invoices (PENDING)
    Fin->>DB: INSERT finance.invoice_items
    Fin->>DB: INSERT finance.installments
    Fin-->>Adm: 201 Created (invoice_id, final_amount, payment_ref_code)
    Adm-->>Staff: Trả kết quả chốt đăng ký và thông tin hóa đơn

    Student->>Gw: GET /api/finance/invoices/{id}/vietqr
    Gw->>Fin: Yêu cầu tạo mã QR thanh toán
    Fin-->>Student: Trả mã VietQR chứa payment_ref_code

    Student->>Bank: Quét mã QR và chuyển khoản học phí
    Bank->>Gw: POST /api/finance/webhooks/vietqr (bank_transaction_id, amount, content)
    Gw->>Fin: Chuyển tiếp Webhook
    Fin->>DB: Kiểm tra bank_transaction_id (UNIQUE)
    alt Giao dịch đã tồn tại
        Fin-->>Bank: 200 OK, không ghi nhận payment lần 2
    else Giao dịch mới
        Fin->>DB: INSERT finance.payments (VIETQR, SUCCESS)
        Fin->>DB: UPDATE installments và invoices (PARTIAL / PAID)
        Fin-->>Bank: 200 OK
    end
```

### 3.1. Các bước xử lý chính

1. Admission chốt đăng ký và gọi Finance bằng endpoint auto-generate.
2. Finance kiểm tra Voucher có khóa dòng để tránh vượt giới hạn sử dụng.
3. Finance tạo hóa đơn, chi tiết hóa đơn và các kỳ thanh toán.
4. Học viên lấy mã VietQR gắn với `payment_ref_code`.
5. Ngân hàng gửi Webhook chứa `bank_transaction_id`, `amount`, `content`.
6. Finance kiểm tra tính duy nhất của mã giao dịch; giao dịch trùng không được ghi nhận lần hai.
7. Giao dịch mới được ghi vào `finance.payments`; trạng thái kỳ và hóa đơn được cập nhật.

---

## 4. Sơ đồ Tuần tự: Phê duyệt Hoàn tiền 3 cấp

Sơ đồ thể hiện quá trình lấy dữ liệu điểm danh từ Learning Service, kiểm tra điều kiện số buổi, tính tiền hoàn và thực hiện ba cấp phê duyệt.

```mermaid
sequenceDiagram
    autonumber
    actor Advisor as Tư vấn viên (Cấp 1)
    participant Fin as Finance Service (:8083)
    participant Learn as Learning Service (:8084)
    participant DB as PostgreSQL (finance)
    actor Accountant as Kế toán (Cấp 2)
    actor Director as Giám đốc (Cấp 3)

    Advisor->>Fin: POST /api/finance/refunds (invoice_id, class_id, reason)
    Fin->>Learn: GET /api/learning/classes/{class_id}/students/{student_id}/attendance
    Learn-->>Fin: total_sessions và attended_sessions

    alt attended_sessions > max_allowed_sessions
        Fin-->>Advisor: 400 Bad Request - Chặn hoàn tiền
    else attended_sessions <= max_allowed_sessions
        Fin->>Fin: Tính số tiền hoàn (% hợp đồng sau khấu trừ)
        Fin->>DB: INSERT refund_requests (PENDING_ACCOUNTANT)
        Accountant->>Fin: PUT /api/finance/refunds/{id}/verify
        Fin->>DB: UPDATE status = PENDING_DIRECTOR
        Director->>Fin: PUT /api/finance/refunds/{id}/approve
        Fin->>DB: UPDATE status = APPROVED
        Accountant->>Fin: PUT /api/finance/refunds/{id}/complete
        Fin->>DB: UPDATE refund_requests = COMPLETED
        Fin->>DB: UPDATE invoices = REFUNDED
    end
```

### 4.1. Trình tự phê duyệt

| Cấp | Người thực hiện | Endpoint | Trạng thái |
|---|---|---|---|
| 1 | Tư vấn viên (STAFF) | POST `/api/finance/refunds` | PENDING_ACCOUNTANT |
| 2 | Kế toán (STAFF) | PUT `/api/finance/refunds/{id}/verify` | PENDING_DIRECTOR |
| 3 | Giám đốc (ADMIN) | PUT `/api/finance/refunds/{id}/approve` | APPROVED |
| Hoàn tất | Kế toán (STAFF) | PUT `/api/finance/refunds/{id}/complete` | COMPLETED |

Điều kiện tiếp nhận: `attended_sessions <= max_allowed_sessions`. Sau khi hoàn tất, yêu cầu ở trạng thái `COMPLETED` và hóa đơn liên quan chuyển sang `REFUNDED`.

---

## 5. Sơ đồ Thực thể Liên kết ERD

Sơ đồ thể hiện đầy đủ **8 bảng Finance** theo mô hình SERIAL/INTEGER; các quan hệ nội bộ dùng FK trong schema Finance. Các định danh học viên, khóa học, lớp học và đăng ký là Logical FK.

```mermaid
erDiagram
    VOUCHERS ||--o{ INVOICES : applies
    INVOICES ||--|{ INVOICE_ITEMS : contains
    INVOICES ||--|{ INSTALLMENTS : splits_into
    INVOICES ||--o{ PAYMENTS : receives
    INSTALLMENTS |o--o{ PAYMENTS : allocated_to
    STUDENT_WALLETS ||--o{ WALLET_TRANSACTIONS : records
    INVOICES |o--o{ WALLET_TRANSACTIONS : offsets
    INVOICES ||--o{ REFUND_REQUESTS : refund_for

    VOUCHERS {
        int id PK
        string code UK
        string campaign_name
        int discount_percent
        decimal discount_amount
        decimal min_order_value
        int max_uses
        int current_uses
        timestamp expires_at
        boolean is_active
    }
    INVOICES {
        int id PK
        string invoice_code UK
        int student_id "Logical FK"
        int course_id "Logical FK"
        int enrollment_id "Logical FK"
        string invoice_type
        decimal amount
        int voucher_id FK
        decimal discount_applied
        decimal final_amount
        decimal paid_amount
        decimal remaining_amount
        string status
    }
    INVOICE_ITEMS {
        int id PK
        int invoice_id FK
        int course_id
        string item_type
        string description
        int quantity
        decimal unit_price
        decimal line_total
    }
    INSTALLMENTS {
        int id PK
        int invoice_id FK
        int installment_no
        string payment_ref_code UK
        decimal amount_due
        decimal amount_paid
        date due_date
        string status
    }
    PAYMENTS {
        int id PK
        string payment_code UK
        int invoice_id FK
        int installment_id FK
        string payment_method
        decimal amount
        string bank_transaction_id UK
        string status
        timestamp paid_at
    }
    STUDENT_WALLETS {
        int id PK
        int student_id UK
        decimal balance
        boolean is_withdrawable
        string status
    }
    WALLET_TRANSACTIONS {
        int id PK
        int wallet_id FK
        string tx_type
        decimal amount
        int related_invoice_id FK
        string reason
    }
    REFUND_REQUESTS {
        int id PK
        string refund_code UK
        int invoice_id FK
        int student_id "Logical FK"
        int class_id "Logical FK"
        int total_sessions
        int attended_sessions
        int max_allowed_sessions
        int refundable_percent
        decimal requested_refund_amount
        decimal approved_refund_amount
        string status
    }
```

### 5.1. Các quan hệ dữ liệu

| Quan hệ | Ý nghĩa |
|---|---|
| `vouchers` → `invoices` | Voucher được áp dụng cho hóa đơn. |
| `invoices` → `invoice_items` | Hóa đơn gồm các khoản mục học phí/học lại. |
| `invoices` → `installments` | Hóa đơn được chia thành nhiều kỳ thanh toán. |
| `invoices` → `payments` | Hóa đơn nhận các giao dịch thanh toán. |
| `installments` → `payments` | Payment có thể gắn với một kỳ thanh toán. |
| `student_wallets` → `wallet_transactions` | Ví có lịch sử giao dịch. |
| `invoices` → `wallet_transactions` | Giao dịch ví có thể cấn trừ một hóa đơn. |
| `invoices` → `refund_requests` | Hóa đơn có thể phát sinh yêu cầu hoàn tiền. |


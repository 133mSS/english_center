# ĐẶC TẢ MÔ HÌNH HÓA UML (UML SPECIFICATION)
## FINANCE SERVICE – HỆ THỐNG QUẢN LÝ TRUNG TÂM ANH NGỮ

> **Phân hệ:** Finance Service  
> **Port nội bộ:** 8084 theo `docs/architecture.md`  
> **Schema:** `finance`  
> **Phiên bản:** 1.0

---

## MỤC LỤC
1. [Tổng quan Mô hình hóa](#1-tổng-quan-mô-hình-hóa)
2. [Biểu đồ Ca sử dụng (Use Case)](#2-biểu-đồ-ca-sử-dụng-use-case)
3. [Biểu đồ Lớp (Class Diagram)](#3-biểu-đồ-lớp-class-diagram)
4. [Biểu đồ Tuần tự (Sequence Diagrams)](#4-biểu-đồ-tuần-tự-sequence-diagrams)
5. [Biểu đồ Máy Trạng thái (State Machines)](#5-biểu-đồ-máy-trạng-thái-state-machines)
6. [Biểu đồ Hoạt động (Activity Diagrams)](#6-biểu-đồ-hoạt-động-activity-diagrams)
7. [Ma trận Truy vết Yêu cầu](#7-ma-trận-truy-vết-yêu-cầu)

---

## 1. Tổng quan Mô hình hóa

Mô hình nghiệp vụ Finance gồm các đối tượng TuitionFee, Voucher, Invoice, InvoiceItem, Installment, Payment, StudentWallet, WalletTransaction và RefundRequest.

**Actors:**
- `STUDENT`: học viên tra cứu hóa đơn/thanh toán của bản thân.
- `STAFF`: nhân viên Finance; nghiệp vụ có thể phân tách Tư vấn và Kế toán.
- `ADMIN`: quản trị/giám đốc.
- `ADMISSION_SERVICE`: gửi yêu cầu lập hóa đơn khi chốt đăng ký.
- `LEARNING_SERVICE`: cung cấp dữ liệu buổi học cho quy trình hoàn phí.
- `BANK_WEBHOOK`: gửi kết quả giao dịch VietQR trong quy trình nghiệp vụ.

---

## 2. Biểu đồ Ca sử dụng (Use Case)

### 2.1. Use Case tổng thể

```mermaid
flowchart LR
    Student[STUDENT]
    Staff[STAFF / Kế toán]
    Advisor[STAFF / Tư vấn]
    Admin[ADMIN / Giám đốc]
    Admission[Admission Service]
    Bank[Bank / VietQR Webhook]
    Learning[Learning Service]

    subgraph Finance["Finance Service"]
      UC1([Quản lý biểu phí])
      UC2([Lập và tra cứu hóa đơn])
      UC3([Ghi nhận thanh toán])
      UC4([Theo dõi công nợ])
      UC5([Quản lý Voucher Campaign])
      UC6([Quản lý Installments])
      UC7([Đối soát VietQR])
      UC8([Quản lý ví bảo lưu])
      UC9([Xử lý yêu cầu hoàn phí])
      UC10([Báo cáo BI tài chính])
    end

    Staff --> UC1
    Staff --> UC2
    Staff --> UC3
    Staff --> UC4
    Student --> UC2
    Student --> UC3
    Student --> UC8
    Admission --> UC2
    Advisor --> UC9
    Learning --> UC9
    Admin --> UC5
    Admin --> UC9
    Admin --> UC10
    Staff --> UC10
    Bank --> UC7
```

### 2.2. Lập hóa đơn và ghi nhận thanh toán

```mermaid
flowchart TD
    Start([Bắt đầu]) --> Fee{Có tuition_fee_id?}
    Fee -- Có --> LoadFee[Đọc finance.tuition_fees]
    LoadFee --> Amount{Request có amount hợp lệ?}
    Amount -- Không --> Calc[amount = tuition amount - discount amount]
    Amount -- Có --> UseInput[Dùng amount request truyền]
    Fee -- Không --> DirectAmount[Đọc amount từ request]
    Calc --> CheckAmount[Kiểm tra amount > 0]
    UseInput --> CheckAmount
    DirectAmount --> CheckAmount
    CheckAmount --> InvoiceCode[Sinh/kiểm tra invoice_code]
    InvoiceCode --> Due{due_date < CURRENT_DATE?}
    Due -- Có --> Overdue[status = OVERDUE]
    Due -- Không --> Unpaid[status = UNPAID]
    Overdue --> SaveInvoice[(INSERT invoice)]
    Unpaid --> SaveInvoice
    SaveInvoice --> Done([Trả invoice])
```

### 2.3. Quy trình hoàn tiền 3 cấp (thiết kế mục tiêu)

```mermaid
flowchart TD
    Advisor[Tư vấn viên tạo yêu cầu] --> Attendance[Finance lấy attendance từ Learning]
    Attendance --> Eligible{attended_sessions <= max_allowed_sessions?}
    Eligible -- Không --> Reject[Không tiếp nhận yêu cầu]
    Eligible -- Có --> Create[Finance tạo refund request]
    Create --> Accountant[Kế toán xác minh]
    Accountant --> Director[Giám đốc phê duyệt]
    Director --> Complete[Kế toán ghi nhận đã chi]
    Director -->|Từ chối| Rejected[REJECTED]
```

---

## 3. Biểu đồ Lớp (Class Diagram)

### 3.1. Domain Model – Hóa đơn và thanh toán

```mermaid
classDiagram
    class TuitionFee {
      +int id
      +int course_id
      +Decimal amount
      +String currency
      +String discount_code
      +Decimal discount_amount
      +String note
      +datetime created_at
    }
    class Invoice {
      +int id
      +String invoice_code
      +int student_id
      +int enrollment_id
      +int tuition_fee_id
      +Decimal amount
      +String status
      +date due_date
      +datetime created_at
      +get_paid_amount()
      +get_remaining_amount()
    }
    class Payment {
      +int id
      +int invoice_id
      +Decimal amount
      +String payment_method
      +String transaction_ref
      +datetime paid_at
    }
    TuitionFee "1" --> "0..*" Invoice : tuition_fee_id
    Invoice "1" --> "0..*" Payment : invoice_id
```

### 3.2. Domain Model – Các nghiệp vụ tài chính mở rộng

```mermaid
classDiagram
    class Voucher {
      +int id
      +String code
      +String campaign_name
      +int discount_percent
      +Decimal discount_amount
      +Decimal min_order_value
      +int max_uses
      +int current_uses
      +datetime expires_at
      +bool is_active
    }
    class Invoice {
      +int id
      +String invoice_code
      +int student_id
      +int course_id
      +int enrollment_id
      +String invoice_type
      +Decimal amount
      +Decimal discount_applied
      +Decimal final_amount
      +Decimal paid_amount
      +Decimal remaining_amount
      +String status
    }
    class InvoiceItem {
      +int id
      +int invoice_id
      +int course_id
      +String item_type
      +int quantity
      +Decimal unit_price
      +Decimal line_total
    }
    class Installment {
      +int id
      +int invoice_id
      +int installment_no
      +String payment_ref_code
      +Decimal amount_due
      +Decimal amount_paid
      +date due_date
      +String status
    }
    class Payment {
      +int id
      +int invoice_id
      +int installment_id
      +String payment_method
      +Decimal amount
      +String bank_transaction_id
      +String status
    }
    class StudentWallet {
      +int id
      +int student_id
      +Decimal balance
      +bool is_withdrawable
      +String status
    }
    class WalletTransaction {
      +int id
      +int wallet_id
      +String tx_type
      +Decimal amount
      +int related_invoice_id
    }
    class RefundRequest {
      +int id
      +int invoice_id
      +int student_id
      +int class_id
      +int total_sessions
      +int attended_sessions
      +Decimal requested_refund_amount
      +Decimal approved_refund_amount
      +String status
    }
    Voucher "1" --> "0..*" Invoice : applied_to
    Invoice "1" --> "1..*" InvoiceItem : contains
    Invoice "1" --> "1..*" Installment : split_into
    Invoice "1" --> "0..*" Payment : receives
    Installment "0..1" --> "0..*" Payment : allocated_to
    StudentWallet "1" --> "0..*" WalletTransaction : ledger
    Invoice "0..1" --> "0..*" WalletTransaction : offset
    Invoice "1" --> "0..*" RefundRequest : refund
```

---

## 4. Biểu đồ Tuần tự (Sequence Diagrams)

### 4.1. Tạo hóa đơn từ biểu phí (MVP)

```mermaid
sequenceDiagram
    autonumber
    actor User as STAFF
    participant UI as Finance Frontend
    participant API as Finance FastAPI
    participant DB as PostgreSQL finance

    User->>UI: Nhập thông tin hóa đơn
    UI->>API: POST /api/finance/invoices
    API->>API: Validate InvoiceCreate
    opt Có tuition_fee_id
      API->>DB: SELECT tuition_fees
      DB-->>API: amount, discount_amount
      API->>API: Tính amount nếu request không truyền giá hợp lệ
    end
    API->>DB: Kiểm tra invoice_code
    API->>DB: INSERT finance.invoices
    DB-->>API: Invoice row
    API-->>UI: 201 Created {success, data}
    UI-->>User: Hiển thị kết quả
```

### 4.2. Ghi nhận thanh toán và cập nhật hóa đơn (MVP)

```mermaid
sequenceDiagram
    autonumber
    actor Accountant as STAFF / Kế toán
    participant UI as Finance Frontend
    participant API as Finance FastAPI
    participant DB as PostgreSQL finance

    Accountant->>UI: Nhập số tiền, phương thức, transaction_ref
    UI->>API: POST /api/finance/payments
    API->>API: Validate amount > 0, transaction_ref
    API->>DB: SELECT invoice FOR UPDATE
    DB-->>API: Invoice amount/status
    API->>DB: Check transaction_ref duplicate
    API->>DB: INSERT payment
    API->>DB: SUM payments by invoice_id
    alt total_paid >= invoice.amount
      API->>DB: UPDATE invoice status = PAID
    else Chưa đủ
      Note over API: Giữ trạng thái invoice hiện tại
    end
    API->>DB: COMMIT
    API-->>UI: 201 Created with total_paid and invoice_status
    UI-->>Accountant: Hiển thị kết quả thanh toán
```

### 4.3. Gạch nợ VietQR

```mermaid
sequenceDiagram
    autonumber
    actor Student as Học viên
    participant Finance as Finance Service
    participant Bank as Bank / VietQR
    participant DB as PostgreSQL finance

    Student->>Finance: Yêu cầu mã QR cho invoice/installment
    Finance-->>Student: QR chứa payment_ref_code
    Student->>Bank: Quét mã và chuyển khoản
    Bank->>Finance: Webhook bank_transaction_id, amount, content
    Finance->>DB: Kiểm tra bank_transaction_id UNIQUE
    alt Giao dịch đã xử lý
      Finance-->>Bank: 200 OK, không ghi nhận lần hai
    else Giao dịch mới
      Finance->>DB: INSERT payment
      Finance->>DB: UPDATE installment/invoice balance
      Finance-->>Bank: 200 OK
    end
```

### 4.4. Quy trình phê duyệt hoàn tiền 3 cấp

```mermaid
sequenceDiagram
    autonumber
    actor Advisor as STAFF / Tư vấn
    participant Finance as Finance Service
    participant Learning as Learning Service
    participant DB as PostgreSQL finance
    actor Accountant as STAFF / Kế toán
    actor Director as ADMIN / Giám đốc

    Advisor->>Finance: POST /api/finance/refunds
    Finance->>Learning: Lấy total_sessions, attended_sessions
    Learning-->>Finance: Attendance snapshot
    alt attended_sessions > max_allowed_sessions
      Finance-->>Advisor: Từ chối tạo yêu cầu
    else Đủ điều kiện
      Finance->>DB: INSERT refund PENDING_ACCOUNTANT
      Accountant->>Finance: PUT /refunds/{id}/verify
      Finance->>DB: status = PENDING_DIRECTOR
      Director->>Finance: PUT /refunds/{id}/approve
      Finance->>DB: status = APPROVED
      Accountant->>Finance: PUT /refunds/{id}/complete
      Finance->>DB: status = COMPLETED
    end
```

---

## 5. Biểu đồ Máy Trạng thái (State Machines)

### 5.1. Vòng đời Invoice

```mermaid
stateDiagram-v2
    [*] --> UNPAID : Tạo hóa đơn
    [*] --> OVERDUE : Tạo hóa đơn với due_date quá khứ
    UNPAID --> OVERDUE : due_date < CURRENT_DATE
    UNPAID --> PAID : SUM(payments.amount) >= invoice.amount
    OVERDUE --> PAID : Thanh toán đủ
    UNPAID --> CANCELLED : Hủy theo nghiệp vụ ngoài backend hiện tại
    OVERDUE --> CANCELLED : Hủy theo nghiệp vụ ngoài backend hiện tại
    PAID --> [*]
    CANCELLED --> [*]
```

Backend hiện có logic đổi UNPAID thành OVERDUE và đổi trạng thái sang PAID khi thanh toán đủ. Route hủy hóa đơn chưa có trong file `main.py`.

### 5.2. Vòng đời Payment

Payment được ghi nhận bằng bản ghi giao dịch và thời điểm `paid_at`; vòng đời giao dịch được quản lý theo kết quả ghi nhận thanh toán.

### 5.3. Vòng đời Refund

```mermaid
stateDiagram-v2
    [*] --> PENDING_ACCOUNTANT
    PENDING_ACCOUNTANT --> PENDING_DIRECTOR : Kế toán xác minh
    PENDING_ACCOUNTANT --> REJECTED : Kế toán từ chối
    PENDING_DIRECTOR --> APPROVED : Giám đốc duyệt
    PENDING_DIRECTOR --> REJECTED : Giám đốc từ chối
    APPROVED --> COMPLETED : Kế toán ghi nhận đã hoàn
    REJECTED --> [*]
    COMPLETED --> [*]
```

---

## 6. Biểu đồ Hoạt động (Activity Diagrams)

### 6.1. Kiểm tra và ghi nhận thanh toán

```mermaid
flowchart TD
    Start([Request Payment]) --> Validate{amount > 0?}
    Validate -- No --> ErrAmount[HTTP 400]
    Validate -- Yes --> Ref{transaction_ref non-empty?}
    Ref -- No --> ErrRef[HTTP 400]
    Ref -- Yes --> Lock[SELECT invoice FOR UPDATE]
    Lock --> Exists{Invoice exists?}
    Exists -- No --> ErrNotFound[HTTP 404]
    Exists -- Yes --> Cancel{Invoice status CANCELLED?}
    Cancel -- Yes --> ErrCancelled[HTTP 400]
    Cancel -- No --> Duplicate{transaction_ref already exists?}
    Duplicate -- Yes --> ErrDuplicate[HTTP 400]
    Duplicate -- No --> Insert[INSERT payment]
    Insert --> Sum[SUM payment amounts]
    Sum --> Paid{total_paid >= invoice.amount?}
    Paid -- Yes --> Update[UPDATE invoice PAID]
    Paid -- No --> Keep[Keep current invoice status]
    Update --> Commit[COMMIT]
    Keep --> Commit
    Commit --> Done([Return 201])
```

### 6.2. Tính số dư hóa đơn

```mermaid
flowchart TD
    Start([Read invoice]) --> Load[Load invoice and payments]
    Load --> Sum["paid_amount = SUM(payment.amount)"]
    Sum --> Remaining["remaining_amount = max(invoice.amount - paid_amount, 0)"]
    Remaining --> Return([Return invoice summary])
```

---

## 7. Ma trận Truy vết Yêu cầu

| Mã yêu cầu | Use Case | Entity/Data | Luồng UML |
|---|---|---|---|
| FIN-F01 | Quản lý biểu phí | TuitionFee | Use Case biểu phí; sequence cập nhật biểu phí |
| FIN-F02 | Kiểm tra Voucher | Voucher | Use Case Voucher và Domain Model |
| FIN-F03 | Tạo hóa đơn | Invoice | Sequence tạo hóa đơn |
| FIN-F04 | Tra cứu hóa đơn | Invoice, Payment | Use Case tra cứu; query invoice |
| FIN-F05 | Ghi nhận thanh toán | Payment | Sequence thanh toán; Activity thanh toán |
| FIN-F06 | VietQR webhook | Payment, Installment | Sequence VietQR |
| FIN-F07 | Ví bảo lưu | StudentWallet, WalletTransaction | Use Case ví và Domain Model |
| FIN-F08 | Hoàn phí | RefundRequest | Sequence refund và State machine refund |
| FIN-F09 | BI tài chính | BI Views | Use Case BI |

**Quy ước:** Các sơ đồ thể hiện các thực thể dữ liệu, tác nhân và luồng nghiệp vụ thuộc phạm vi Finance Service.

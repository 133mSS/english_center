# TỔNG HỢP TÍNH NĂNG VÀ CƠ SỞ DỮ LIỆU PHÂN HỆ FINANCE

**Dự án:** Hệ thống Quản lý Trung tâm Ngoại ngữ (English Center Management System)  
**Phân hệ:** Finance Service (`finance-service`)  
**Công nghệ:** Python 3.11+ / FastAPI / PostgreSQL  
**Port nội bộ:** `8083`  
**Gateway:** `/api/finance/...`  
**Authentication:** Stateless JWT (HS256)  
**Chuẩn dữ liệu:** SERIAL/INTEGER Keys, JSON `snake_case`  
**Schema sở hữu:** `finance`  
**Phiên bản:** Finance Module 2.0

---

## 1. Danh sách các tính năng

### Nhóm 1: Biểu phí và Voucher

- **FIN-F01 – Quản lý chiến dịch Voucher:** Tạo và quản lý Voucher theo phần trăm hoặc số tiền cố định; kiểm soát số lượt sử dụng tối đa, số lượt đã sử dụng, giá trị đơn hàng tối thiểu và thời hạn hiệu lực.
- **FIN-F02 – Kiểm tra tính hợp lệ Voucher:** Kiểm tra mã giảm giá và trả về số tiền được chiết khấu dự kiến (`discount_applied`).

### Nhóm 2: Hóa đơn và lịch thanh toán

- **FIN-F03 – Tự động sinh hóa đơn:** Sinh hóa đơn khi Admission chốt đăng ký; hỗ trợ gộp hoặc tách phí học lại thông qua `invoice_items`, đồng thời tạo lịch đóng phí qua `installments`.
- **FIN-F04 – Tra cứu hóa đơn:** Tra cứu danh sách và chi tiết hóa đơn, các khoản mục học phí/học lại, lịch trả góp và lịch sử đóng tiền.

### Nhóm 3: Thanh toán và đối soát

- **FIN-F05 – Ghi nhận thanh toán tiền mặt:** Ghi nhận phiếu thu tại quầy; cập nhật `paid_amount`, trạng thái kỳ đóng và trạng thái hóa đơn (`PARTIAL` / `PAID`).
- **FIN-F06 – VietQR và Webhook:** Sinh mã VietQR động chứa `payment_ref_code`; nhận Webhook ngân hàng và tự động gạch nợ theo thời gian thực.

### Nhóm 4: Ví bảo lưu và hoàn tiền

- **FIN-F07 – Ví bảo lưu học viên:** Quản lý ví nội bộ, cộng tiền bảo lưu và cấn trừ học phí khóa học tiếp theo.
- **FIN-F08 – Quy trình hoàn tiền 3 cấp:** Kiểm tra số buổi học từ Learning Service; tính tỷ lệ hoàn sau khấu trừ; Kế toán xác nhận, Giám đốc phê duyệt và Kế toán ghi nhận giải ngân.

### Nhóm 5: Báo cáo quản trị

- **FIN-F09 – BI tài chính:** Cung cấp Dashboard doanh thu thực thu (Cash-basis), hiệu quả chiến dịch Voucher, tỷ lệ hoàn phí và quỹ bảo lưu.

### 1.1. Danh mục API và phân quyền

| Mã | Method & Endpoint | Phân quyền | Chức năng |
|---|---|---|---|
| FIN-F01 | POST `/api/finance/vouchers`<br/>GET `/api/finance/vouchers` | ADMIN, STAFF | Tạo và quản lý chiến dịch Voucher. |
| FIN-F02 | POST `/api/finance/vouchers/validate` | ADMIN, STAFF, STUDENT | Kiểm tra Voucher và tính `discount_applied`. |
| FIN-F03 | POST `/api/finance/invoices/auto-generate` | ADMIN, STAFF hoặc Internal | Sinh hóa đơn khi Admission chốt đăng ký; tạo invoice items và installments. |
| FIN-F04 | GET `/api/finance/invoices`<br/>GET `/api/finance/invoices/{id}` | ADMIN, STAFF, STUDENT | Tra cứu hóa đơn, khoản mục, lịch trả góp và lịch sử thanh toán. |
| FIN-F05 | POST `/api/finance/payments/cash` | ADMIN, STAFF | Ghi nhận thu tiền mặt. |
| FIN-F06 | GET `/api/finance/invoices/{id}/vietqr`<br/>POST `/api/finance/webhooks/vietqr` | STUDENT, STAFF / Webhook | Sinh QR và nhận Webhook ngân hàng. |
| FIN-F07 | GET `/api/finance/wallets/{student_id}`<br/>POST `/api/finance/wallets/{student_id}/reserve` | ADMIN, STAFF, STUDENT | Tra cứu ví, cộng tiền bảo lưu và cấn trừ học phí. |
| FIN-F08 | POST `/api/finance/refunds`<br/>PUT `/api/finance/refunds/{id}/verify`<br/>PUT `/api/finance/refunds/{id}/approve`<br/>PUT `/api/finance/refunds/{id}/complete` | Cấp 1: STAFF – Tư vấn<br/>Cấp 2: STAFF – Kế toán<br/>Cấp 3: ADMIN – Giám đốc | Quy trình hoàn tiền 3 cấp. |
| FIN-F09 | GET `/api/finance/bi/cash-revenue`<br/>GET `/api/finance/bi/voucher-campaigns`<br/>GET `/api/finance/bi/refund-summary` | ADMIN, STAFF | Dữ liệu BI tài chính. |

## 2. Các bảng trong schema `finance`

Có **8 bảng nghiệp vụ** và **2 BI Views** trong schema Finance.

| STT | Bảng | Vai trò | Các cột |
|---:|---|---|---|
| 1 | `finance.vouchers` | Quản lý chiến dịch Voucher, điều kiện giảm giá và giới hạn sử dụng | `id`, `code`, `campaign_name`, `discount_percent`, `discount_amount`, `min_order_value`, `max_discount_amount`, `max_uses`, `current_uses`, `valid_from`, `expires_at`, `is_active`, `created_at` |
| 2 | `finance.invoices` | Quản lý hóa đơn học phí, loại hóa đơn, Voucher, số tiền phải thu và trạng thái | `id`, `invoice_code`, `student_id`, `course_id`, `enrollment_id`, `invoice_type`, `amount`, `voucher_id`, `discount_applied`, `final_amount`, `paid_amount`, `remaining_amount`, `status`, `notes`, `created_at`, `paid_at` |
| 3 | `finance.invoice_items` | Chi tiết khoản mục gói học phí và phí học lại | `id`, `invoice_id`, `course_id`, `item_type`, `description`, `quantity`, `unit_price`, `line_total`, `created_at` |
| 4 | `finance.installments` | Lịch đóng học phí nhiều đợt/đặt cọc | `id`, `invoice_id`, `installment_no`, `payment_ref_code`, `amount_due`, `amount_paid`, `due_date`, `status`, `paid_at`, `created_at` |
| 5 | `finance.payments` | Giao dịch thu tiền mặt, VietQR và cấn trừ ví | `id`, `payment_code`, `invoice_id`, `installment_id`, `payment_method`, `amount`, `bank_transaction_id`, `qr_reference_code`, `webhook_payload`, `received_by_staff_id`, `status`, `paid_at` |
| 6 | `finance.student_wallets` | Quản lý số dư ví bảo lưu của học viên | `id`, `student_id`, `balance`, `is_withdrawable`, `status`, `updated_at` |
| 7 | `finance.wallet_transactions` | Lịch sử cộng/trừ ví và cấn trừ học phí | `id`, `wallet_id`, `tx_type`, `amount`, `related_invoice_id`, `reason`, `created_by_staff_id`, `created_at` |
| 8 | `finance.refund_requests` | Yêu cầu hoàn tiền, điều kiện số buổi và phê duyệt 3 cấp | `id`, `refund_code`, `invoice_id`, `student_id`, `class_id`, `total_sessions`, `attended_sessions`, `max_allowed_sessions`, `paid_amount_snapshot`, `refundable_percent`, `deduction_amount`, `requested_refund_amount`, `approved_refund_amount`, `reason`, `bank_name`, `bank_account_no`, `bank_account_holder`, `status`, `requested_by_staff_id`, `requested_at`, `verified_by_accountant_id`, `verified_at`, `accountant_note`, `approved_by_director_id`, `approved_at`, `director_note`, `completed_at` |

**BI Views:**
- `finance.vw_bi_cash_revenue_monthly`: báo cáo doanh thu thực thu và hoàn phí theo tháng.
- `finance.vw_bi_voucher_campaigns`: báo cáo hiệu quả chiến dịch Voucher.

**Quy ước:** Các cột `student_id`, `course_id`, `class_id` là Logical FK kiểu INTEGER; không tạo FK vật lý hoặc JOIN sang schema Admission/Learning.

## 3. Toàn văn SQL khởi tạo schema `finance`

```sql
-- ============================================================================
-- SCHEMA: finance
-- Primary Key / Logical Foreign Key: SERIAL / INTEGER
-- ============================================================================

CREATE SCHEMA IF NOT EXISTS finance;

-- 1. BẢNG CHIẾN DỊCH VOUCHER
CREATE TABLE IF NOT EXISTS finance.vouchers (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    campaign_name VARCHAR(150) NOT NULL DEFAULT 'Chiến dịch ưu đãi học phí',
    discount_percent INT DEFAULT 0 CHECK (discount_percent >= 0 AND discount_percent <= 100),
    discount_amount DECIMAL(12, 2) DEFAULT 0 CHECK (discount_amount >= 0),
    min_order_value DECIMAL(12, 2) DEFAULT 0 CHECK (min_order_value >= 0),
    max_discount_amount DECIMAL(12, 2) DEFAULT NULL,
    max_uses INT DEFAULT 100 CHECK (max_uses > 0),
    current_uses INT DEFAULT 0 CHECK (current_uses >= 0),
    valid_from TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_voucher_usage_limit CHECK (current_uses <= max_uses)
);

-- 2. BẢNG HÓA ĐƠN
CREATE TABLE IF NOT EXISTS finance.invoices (
    id SERIAL PRIMARY KEY,
    invoice_code VARCHAR(50) UNIQUE NOT NULL,
    student_id INT NOT NULL,
    course_id INT NOT NULL,
    enrollment_id INT,
    invoice_type VARCHAR(30) NOT NULL DEFAULT 'COURSE_PACKAGE'
        CHECK (invoice_type IN ('COURSE_PACKAGE', 'STANDALONE_RETAKE', 'MIXED')),
    amount DECIMAL(12, 2) NOT NULL CHECK (amount >= 0),
    voucher_id INT REFERENCES finance.vouchers(id),
    discount_applied DECIMAL(12, 2) DEFAULT 0 CHECK (discount_applied >= 0),
    final_amount DECIMAL(12, 2) NOT NULL CHECK (final_amount >= 0),
    paid_amount DECIMAL(12, 2) NOT NULL DEFAULT 0 CHECK (paid_amount >= 0),
    remaining_amount DECIMAL(12, 2) GENERATED ALWAYS AS (final_amount - paid_amount) STORED,
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING'
        CHECK (status IN ('PENDING', 'PARTIAL', 'PAID', 'CANCELLED', 'REFUNDED')),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    paid_at TIMESTAMP,
    CONSTRAINT chk_invoice_math CHECK (final_amount = amount - discount_applied),
    CONSTRAINT chk_invoice_paid_bound CHECK (paid_amount <= final_amount)
);

-- 3. BẢNG CHI TIẾT KHOẢN MỤC HÓA ĐƠN
CREATE TABLE IF NOT EXISTS finance.invoice_items (
    id SERIAL PRIMARY KEY,
    invoice_id INT NOT NULL REFERENCES finance.invoices(id) ON DELETE CASCADE,
    course_id INT,
    item_type VARCHAR(30) NOT NULL
        CHECK (item_type IN ('TUITION_PACKAGE', 'RETAKE_FEE')),
    description VARCHAR(255) NOT NULL,
    quantity INT NOT NULL DEFAULT 1 CHECK (quantity > 0),
    unit_price DECIMAL(12, 2) NOT NULL CHECK (unit_price >= 0),
    line_total DECIMAL(12, 2) NOT NULL CHECK (line_total >= 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_line_total_math CHECK (line_total = quantity * unit_price)
);

-- 4. BẢNG LỊCH ĐÓNG HỌC PHÍ NHIỀU ĐỢT / ĐẶT CỌC
CREATE TABLE IF NOT EXISTS finance.installments (
    id SERIAL PRIMARY KEY,
    invoice_id INT NOT NULL REFERENCES finance.invoices(id) ON DELETE CASCADE,
    installment_no INT NOT NULL CHECK (installment_no >= 1),
    payment_ref_code VARCHAR(50) UNIQUE NOT NULL,
    amount_due DECIMAL(12, 2) NOT NULL CHECK (amount_due > 0),
    amount_paid DECIMAL(12, 2) NOT NULL DEFAULT 0 CHECK (amount_paid >= 0),
    due_date DATE NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING'
        CHECK (status IN ('PENDING', 'PARTIAL', 'PAID', 'OVERDUE', 'CANCELLED')),
    paid_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (invoice_id, installment_no)
);

-- 5. BẢNG GIAO DỊCH THU TIỀN & GẠCH NỢ VIETQR
CREATE TABLE IF NOT EXISTS finance.payments (
    id SERIAL PRIMARY KEY,
    payment_code VARCHAR(50) UNIQUE NOT NULL,
    invoice_id INT NOT NULL REFERENCES finance.invoices(id),
    installment_id INT REFERENCES finance.installments(id),
    payment_method VARCHAR(20) NOT NULL
        CHECK (payment_method IN ('CASH', 'VIETQR', 'WALLET_OFFSET')),
    amount DECIMAL(12, 2) NOT NULL CHECK (amount > 0),
    bank_transaction_id VARCHAR(100) UNIQUE,
    qr_reference_code VARCHAR(50),
    webhook_payload JSONB,
    received_by_staff_id INT,
    status VARCHAR(20) NOT NULL DEFAULT 'SUCCESS'
        CHECK (status IN ('PENDING', 'SUCCESS', 'FAILED')),
    paid_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. BẢNG VÍ BẢO LƯU HỌC VIÊN
CREATE TABLE IF NOT EXISTS finance.student_wallets (
    id SERIAL PRIMARY KEY,
    student_id INT UNIQUE NOT NULL,
    balance DECIMAL(12, 2) NOT NULL DEFAULT 0 CHECK (balance >= 0),
    is_withdrawable BOOLEAN NOT NULL DEFAULT FALSE,
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE'
        CHECK (status IN ('ACTIVE', 'FROZEN')),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 7. BẢNG LỊCH SỬ GIAO DỊCH VÍ BẢO LƯU
CREATE TABLE IF NOT EXISTS finance.wallet_transactions (
    id SERIAL PRIMARY KEY,
    wallet_id INT NOT NULL REFERENCES finance.student_wallets(id),
    tx_type VARCHAR(30) NOT NULL
        CHECK (tx_type IN ('RESERVATION_CREDIT', 'TUITION_OFFSET', 'ADJUSTMENT')),
    amount DECIMAL(12, 2) NOT NULL CHECK (amount > 0),
    related_invoice_id INT REFERENCES finance.invoices(id),
    reason TEXT NOT NULL,
    created_by_staff_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 8. BẢNG YÊU CẦU & PHÊ DUYỆT HOÀN TIỀN 3 CẤP
CREATE TABLE IF NOT EXISTS finance.refund_requests (
    id SERIAL PRIMARY KEY,
    refund_code VARCHAR(50) UNIQUE NOT NULL,
    invoice_id INT NOT NULL REFERENCES finance.invoices(id),
    student_id INT NOT NULL,
    class_id INT,
    total_sessions INT NOT NULL CHECK (total_sessions > 0),
    attended_sessions INT NOT NULL CHECK (attended_sessions >= 0),
    max_allowed_sessions INT NOT NULL DEFAULT 3,
    paid_amount_snapshot DECIMAL(12, 2) NOT NULL,
    refundable_percent INT NOT NULL CHECK (refundable_percent BETWEEN 0 AND 100),
    deduction_amount DECIMAL(12, 2) NOT NULL DEFAULT 0,
    requested_refund_amount DECIMAL(12, 2) NOT NULL CHECK (requested_refund_amount >= 0),
    approved_refund_amount DECIMAL(12, 2) CHECK (approved_refund_amount >= 0),
    reason TEXT NOT NULL,
    bank_name VARCHAR(100),
    bank_account_no VARCHAR(50),
    bank_account_holder VARCHAR(150),
    status VARCHAR(30) NOT NULL DEFAULT 'PENDING_ACCOUNTANT'
        CHECK (status IN (
            'PENDING_ACCOUNTANT',
            'PENDING_DIRECTOR',
            'APPROVED',
            'REJECTED',
            'COMPLETED'
        )),
    requested_by_staff_id INT NOT NULL,
    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    verified_by_accountant_id INT,
    verified_at TIMESTAMP,
    accountant_note TEXT,
    approved_by_director_id INT,
    approved_at TIMESTAMP,
    director_note TEXT,
    completed_at TIMESTAMP,
    CONSTRAINT chk_valid_early_withdrawal CHECK (attended_sessions <= max_allowed_sessions)
);

-- VIEW 1: BÁO CÁO DOANH THU THỰC THU VÀ HOÀN PHÍ THEO THÁNG
CREATE OR REPLACE VIEW finance.vw_bi_cash_revenue_monthly AS
WITH cash_in AS (
    SELECT
        DATE_TRUNC('month', paid_at) AS report_month,
        SUM(CASE WHEN payment_method = 'CASH' THEN amount ELSE 0 END) AS cash_at_counter,
        SUM(CASE WHEN payment_method = 'VIETQR' THEN amount ELSE 0 END) AS vietqr_transfer,
        SUM(CASE WHEN payment_method IN ('CASH', 'VIETQR') THEN amount ELSE 0 END) AS gross_cash_in
    FROM finance.payments
    WHERE status = 'SUCCESS'
    GROUP BY DATE_TRUNC('month', paid_at)
),
cash_refund AS (
    SELECT
        DATE_TRUNC('month', completed_at) AS report_month,
        COUNT(id) AS refund_count,
        SUM(approved_refund_amount) AS total_refunded
    FROM finance.refund_requests
    WHERE status = 'COMPLETED'
    GROUP BY DATE_TRUNC('month', completed_at)
)
SELECT
    COALESCE(ci.report_month, cr.report_month) AS report_month,
    COALESCE(ci.cash_at_counter, 0) AS cash_at_counter,
    COALESCE(ci.vietqr_transfer, 0) AS vietqr_transfer,
    COALESCE(ci.gross_cash_in, 0) AS gross_cash_in,
    COALESCE(cr.refund_count, 0) AS refund_count,
    COALESCE(cr.total_refunded, 0) AS total_refunded,
    (COALESCE(ci.gross_cash_in, 0) - COALESCE(cr.total_refunded, 0)) AS net_cash_revenue,
    CASE
        WHEN COALESCE(ci.gross_cash_in, 0) > 0
        THEN ROUND((COALESCE(cr.total_refunded, 0) / ci.gross_cash_in) * 100, 2)
        ELSE 0
    END AS refund_rate_pct
FROM cash_in ci
FULL OUTER JOIN cash_refund cr ON ci.report_month = cr.report_month
ORDER BY report_month DESC;

-- VIEW 2: BÁO CÁO HIỆU QUẢ CHIẾN DỊCH VOUCHER
CREATE OR REPLACE VIEW finance.vw_bi_voucher_campaigns AS
SELECT
    v.id AS voucher_id,
    v.code,
    v.campaign_name,
    v.discount_percent,
    v.discount_amount,
    v.max_uses,
    v.current_uses,
    ROUND((v.current_uses::DECIMAL / v.max_uses) * 100, 2) AS usage_rate_pct,
    COUNT(i.id) AS total_invoices,
    COALESCE(SUM(i.discount_applied), 0) AS total_discount_given,
    COALESCE(SUM(i.paid_amount), 0) AS actual_cash_collected
FROM finance.vouchers v
LEFT JOIN finance.invoices i ON v.id = i.voucher_id AND i.status != 'CANCELLED'
GROUP BY v.id;
```

## 4. Tài liệu chuyên biệt của Finance

- `finance-ba-bi-spec.md`: phạm vi nghiệp vụ, tác nhân, yêu cầu chức năng, quy tắc bất biến và KPI/BI.
- `finance-schema-spec.md`: ERD 8 bảng, Data Dictionary, constraints, DDL và BI Views.
- `finance-tech-spec.md`: kiến trúc tích hợp, API Contract, xác thực JWT và xử lý giao dịch.
- `finance-uml-spec.md`: Use Case, Sequence Diagrams và ERD nghiệp vụ.

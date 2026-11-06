# TỔNG HỢP TÍNH NĂNG VÀ CƠ SỞ DỮ LIỆU PHÂN HỆ FINANCE

**Dự án:** Hệ thống Quản lý Trung tâm Anh ngữ  
**Phân hệ:** Finance Service (`finance-service`, port `8084`)  
**Công nghệ:** Python 3.11+ / FastAPI / SQLAlchemy / PostgreSQL 16  
**Schema:** `finance`  
**Phiên bản:** 1.0 (Master Feature & Schema Summary – chuẩn hóa theo mẫu Admission)

---

## 1. Danh sách các tính năng

Finance gồm **9 yêu cầu chức năng** theo tài liệu nghiệp vụ Finance_Module.docx. Các mã chức năng được giữ theo nguồn tài liệu.

### Nhóm 1: Biểu phí và chính sách giảm giá

- **FIN-F01 – Quản lý Biểu phí & Voucher:** Quản lý học phí theo `course_id`, đơn vị tiền, mã giảm giá, số tiền giảm và ghi chú. Trong backend hiện tại, mỗi khóa học có một biểu phí; lưu biểu phí cùng `course_id` sẽ cập nhật bản ghi hiện có. Thiết kế mở rộng Voucher Campaign độc lập được mô tả trong tài liệu BA/BI.
- **FIN-F02 – Kiểm tra tính hợp lệ Voucher:** Kiểm tra mã giảm giá, điều kiện đơn hàng, thời gian hiệu lực và hạn mức sử dụng; trả về số tiền giảm dự kiến. Chưa có endpoint validate Voucher trong backend hiện tại.

### Nhóm 2: Hóa đơn và công nợ

- **FIN-F03 – Tạo Hóa đơn:** Lập hóa đơn gắn với `student_id`, `enrollment_id`, `tuition_fee_id`; có thể tính số tiền từ biểu phí và sinh `invoice_code` nếu không truyền mã. Thiết kế mục tiêu bổ sung auto-generate, invoice items và installments.
- **FIN-F04 – Tra cứu Hóa đơn:** Tra cứu danh sách hóa đơn, lọc theo `student_id`, tính tổng đã thu và số tiền còn phải thu; tự chuyển hóa đơn UNPAID quá hạn sang OVERDUE. Backend hiện chưa có route chi tiết `/invoices/{id}`.

### Nhóm 3: Thanh toán và đối soát

- **FIN-F05 – Ghi nhận Thanh toán:** Ghi nhận khoản thu CASH hoặc BANK_TRANSFER; kiểm tra số tiền dương, mã giao dịch không trùng và cập nhật hóa đơn PAID khi tổng thanh toán đủ.
- **FIN-F06 – VietQR & Webhook Đối soát:** Thiết kế mục tiêu sinh mã QR động, nhận webhook ngân hàng và chống ghi nhận giao dịch trùng theo `bank_transaction_id`. Chưa có trong backend hiện tại.

### Nhóm 4: Bảo lưu và hoàn phí

- **FIN-F07 – Ví Bảo lưu Học viên:** Quản lý số dư bảo lưu và lịch sử biến động; mặc định không cho rút tiền mặt, chỉ dùng để cấn trừ học phí khóa sau. Chưa có trong schema/backend hiện tại.
- **FIN-F08 – Quy trình Hoàn phí 3 cấp:** Tư vấn viên tạo yêu cầu, Finance kiểm tra số buổi học từ Learning, Kế toán xác minh, Giám đốc phê duyệt và Kế toán ghi nhận hoàn tất. Chưa có trong backend hiện tại.

### Nhóm 5: Báo cáo quản trị

- **FIN-F09 – Báo cáo BI Tài chính:** Cung cấp doanh thu thực thu (Cash-basis), công nợ, hiệu quả Voucher, tỷ lệ hoàn phí và quỹ bảo lưu. Chưa có Finance BI views/endpoints trong DDL/backend hiện tại.

## 2. Các bảng trong schema `finance`

Có **3 bảng hiện tại** trong `scripts/init-db.sql`. Tài liệu Finance_Module.docx mô tả mô hình mục tiêu mở rộng thành 8 bảng; danh mục mục tiêu được liệt kê riêng để tránh nhầm với cấu trúc đang có.

### 2.1. Các bảng hiện tại trên repository

| STT | Bảng | Vai trò | Các cột |
|---:|---|---|---|
| 1 | `finance.tuition_fees` | Quản lý biểu phí theo khóa học và mã giảm giá gắn với biểu phí | `id`, `course_id`, `amount`, `currency`, `discount_code`, `discount_amount`, `note`, `created_at` |
| 2 | `finance.invoices` | Quản lý hóa đơn, học viên, đơn đăng ký, biểu phí, số tiền, hạn thanh toán và trạng thái | `id`, `invoice_code`, `student_id`, `enrollment_id`, `tuition_fee_id`, `amount`, `status`, `due_date`, `created_at` |
| 3 | `finance.payments` | Quản lý các lần thanh toán cho hóa đơn | `id`, `invoice_id`, `amount`, `payment_method`, `transaction_ref`, `paid_at` |

### 2.2. Các bảng trong mô hình mục tiêu Finance_Module.docx

| STT | Bảng | Vai trò | Các cột |
|---:|---|---|---|
| 1 | `finance.vouchers` | Quản lý chiến dịch giảm giá | `id`, `code`, `campaign_name`, `discount_percent`, `discount_amount`, `min_order_value`, `max_discount_amount`, `max_uses`, `current_uses`, `valid_from`, `expires_at`, `is_active`, `created_at` |
| 2 | `finance.invoices` | Hóa đơn mở rộng và số dư công nợ | `id`, `invoice_code`, `student_id`, `course_id`, `enrollment_id`, `invoice_type`, `amount`, `voucher_id`, `discount_applied`, `final_amount`, `paid_amount`, `remaining_amount`, `status`, `notes`, `created_at`, `paid_at` |
| 3 | `finance.invoice_items` | Chi tiết khoản mục học phí và phí học lại | `id`, `invoice_id`, `course_id`, `item_type`, `description`, `quantity`, `unit_price`, `line_total`, `created_at` |
| 4 | `finance.installments` | Lịch thanh toán nhiều đợt | `id`, `invoice_id`, `installment_no`, `payment_ref_code`, `amount_due`, `amount_paid`, `due_date`, `status`, `paid_at`, `created_at` |
| 5 | `finance.payments` | Giao dịch thu tiền đa kênh | `id`, `payment_code`, `invoice_id`, `installment_id`, `payment_method`, `amount`, `bank_transaction_id`, `qr_reference_code`, `webhook_payload`, `received_by_staff_id`, `status`, `paid_at` |
| 6 | `finance.student_wallets` | Ví bảo lưu của học viên | `id`, `student_id`, `balance`, `is_withdrawable`, `status`, `updated_at` |
| 7 | `finance.wallet_transactions` | Lịch sử giao dịch ví | `id`, `wallet_id`, `tx_type`, `amount`, `related_invoice_id`, `reason`, `created_by_staff_id`, `created_at` |
| 8 | `finance.refund_requests` | Yêu cầu và phê duyệt hoàn phí | `id`, `refund_code`, `invoice_id`, `student_id`, `class_id`, `total_sessions`, `attended_sessions`, `max_allowed_sessions`, `paid_amount_snapshot`, `refundable_percent`, `deduction_amount`, `requested_refund_amount`, `approved_refund_amount`, `reason`, thông tin tài khoản ngân hàng, các trường phê duyệt và trạng thái |

**Quy ước:** Các ID `student_id`, `course_id`, `enrollment_id`, `class_id` là logical reference liên service. Không tạo FK vật lý từ Finance sang schema Admission, Student hoặc Learning.

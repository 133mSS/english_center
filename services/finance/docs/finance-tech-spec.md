# ĐẶC TẢ THIẾT KẾ KỸ THUẬT & KIẾN TRÚC PHẦN MỀM (TECHNICAL SPECIFICATION)
## FINANCE SERVICE

> **Service:** `finance-service`  
> **Runtime:** Python 3.11 + FastAPI  
> **Port nội bộ:** `8083`  
> **Gateway:** Nginx – `/api/finance/...`  
> **Database:** PostgreSQL, schema `finance`  
> **Authentication:** Stateless JWT (HS256)  
> **JSON convention:** `snake_case`  
> **Database keys:** SERIAL / INTEGER

---

## MỤC LỤC
1. [Tổng quan Kiến trúc Kỹ thuật](#1-tổng-quan-kiến-trúc-kỹ-thuật)
2. [Thiết kế Xác thực và Phân quyền](#2-thiết-kế-xác-thực-và-phân-quyền)
3. [Kiến trúc Tích hợp Liên Phân hệ](#3-kiến-trúc-tích-hợp-liên-phân-hệ)
4. [API Contract](#4-api-contract)
5. [Xử lý Giao dịch và Đồng thời](#5-xử-lý-giao-dịch-và-đồng-thời)
6. [Quy ước Dữ liệu và Cơ sở Dữ liệu](#6-quy-ước-dữ-liệu-và-cơ-sở-dữ-liệu)

---

## 1. Tổng quan Kiến trúc Kỹ thuật

Finance Service là service tài chính trong kiến trúc Polyglot Microservices. Service chạy Python 3.11 + FastAPI, sử dụng PostgreSQL với schema riêng `finance`; request đi qua Nginx Gateway theo prefix `/api/finance/...`.

### 1.1. Thành phần kỹ thuật

| Thành phần | Công nghệ/chuẩn | Trách nhiệm |
|---|---|---|
| Backend runtime | Python 3.11 | Runtime Finance Service. |
| API framework | FastAPI | Cung cấp REST API. |
| Database | PostgreSQL | Lưu dữ liệu tài chính trong schema finance. |
| API Gateway | Nginx | Định tuyến request tới Finance Service. |
| Authentication | Stateless JWT (HS256) | Xác thực request. |
| Data format | JSON `snake_case` | Chuẩn hóa tên field giữa các service. |
| Key format | SERIAL / INTEGER | PK và Logical FK. |

### 1.2. Quy ước endpoint

Tất cả API Finance sử dụng prefix:

`/api/finance/...`

Finance Service chạy tại port nội bộ `8083`. Nginx Gateway tiếp nhận và định tuyến request theo prefix trên.

---

## 2. Thiết kế Xác thực và Phân quyền

### 2.1. Xác thực

- Sử dụng Stateless JWT.
- Thuật toán ký: HS256.
- Các API Finance được định tuyến qua Nginx Gateway.
- Payload và JSON request/response sử dụng `snake_case`.

### 2.2. Vai trò

| Role | Người dùng | Quyền nghiệp vụ chính |
|---|---|---|
| `STUDENT` | Học viên | Kiểm tra Voucher, tra cứu hóa đơn, sử dụng VietQR và xem ví bảo lưu. |
| `STAFF` – Tư vấn | Nhân viên tư vấn | Tạo yêu cầu hoàn tiền cấp 1; phối hợp quy trình chốt đăng ký. |
| `STAFF` – Kế toán | Nhân viên kế toán | Quản lý Voucher, thu tiền mặt, quản lý ví, xác minh và hoàn tất hoàn tiền. |
| `ADMIN` | Giám đốc | Quản lý Voucher, phê duyệt hoàn tiền cấp 3 và xem BI. |
| Webhook | Cổng VietQR/ngân hàng | Gửi thông báo giao dịch để đối soát. |
| Internal | Admission Service | Gọi API sinh hóa đơn sau khi chốt đăng ký. |

---

## 3. Kiến trúc Tích hợp Liên Phân hệ

### 3.1. Admission → Finance

- Admission Service chạy Java Spring Boot tại port `8081`.
- Khi chuyên viên tuyển sinh chốt đăng ký, Admission gọi REST API nội bộ sang Finance Service tại port `8083`.
- Endpoint được gọi: `POST /api/finance/invoices/auto-generate`.
- Finance kiểm tra và áp dụng Voucher, tạo invoice, invoice_items và installments.
- Finance trả `invoice_id`, `final_amount`, `payment_ref_code` cho Admission.

### 3.2. Learning → Finance

- Learning Service chạy Node.js Express tại port `8084`.
- Khi xử lý yêu cầu hoàn tiền hoặc bảo lưu, Finance gọi HTTP GET sang Learning.
- Endpoint dữ liệu buổi học: `/api/learning/classes/{class_id}/students/{student_id}/attendance`.
- Learning trả `total_sessions` và `attended_sessions`.
- Finance lưu snapshot dữ liệu này trong `finance.refund_requests`.

### 3.3. Thanh toán và Webhook VietQR

- Học viên yêu cầu mã QR từ Finance.
- Học viên thực hiện chuyển khoản qua cổng VietQR/ngân hàng.
- Ngân hàng gửi Webhook qua Gateway tới Finance.
- Finance xác minh `bank_transaction_id`, ghi payment và cập nhật installment/invoice.

---

## 4. API Contract

Tất cả endpoint và phân quyền dưới đây thuộc Finance Service.

| Mã | Method | Endpoint | Phân quyền | Mô tả |
|---|---|---|---|---|
| FIN-F01 | POST, GET | `/api/finance/vouchers` | ADMIN, STAFF | Tạo, quản lý và xem chiến dịch Voucher. |
| FIN-F02 | POST | `/api/finance/vouchers/validate` | ADMIN, STAFF, STUDENT | Kiểm tra mã Voucher và trả `discount_applied`. |
| FIN-F03 | POST | `/api/finance/invoices/auto-generate` | ADMIN, STAFF hoặc Internal | Sinh hóa đơn tự động khi Admission chốt đăng ký; hỗ trợ invoice_items và installments. |
| FIN-F04 | GET | `/api/finance/invoices`<br/>`/api/finance/invoices/{id}` | ADMIN, STAFF, STUDENT | Tra cứu danh sách và chi tiết hóa đơn. |
| FIN-F05 | POST | `/api/finance/payments/cash` | ADMIN, STAFF | Ghi nhận phiếu thu tiền mặt tại quầy. |
| FIN-F06 | GET, POST | `/api/finance/invoices/{id}/vietqr`<br/>`/api/finance/webhooks/vietqr` | STUDENT, STAFF / Webhook | Sinh mã VietQR và nhận Webhook ngân hàng. |
| FIN-F07 | GET, POST | `/api/finance/wallets/{student_id}`<br/>`/api/finance/wallets/{student_id}/reserve` | ADMIN, STAFF, STUDENT | Tra cứu ví, cộng tiền bảo lưu và cấn trừ học phí. |
| FIN-F08 | POST, PUT | `/api/finance/refunds`<br/>`/api/finance/refunds/{id}/verify`<br/>`/api/finance/refunds/{id}/approve`<br/>`/api/finance/refunds/{id}/complete` | STAFF và ADMIN theo cấp duyệt | Xử lý yêu cầu hoàn tiền 3 cấp. |
| FIN-F09 | GET | `/api/finance/bi/cash-revenue`<br/>`/api/finance/bi/voucher-campaigns`<br/>`/api/finance/bi/refund-summary` | ADMIN, STAFF | Cung cấp dữ liệu BI Dashboard. |

### 4.1. FIN-F01 – Quản lý Voucher

- `POST /api/finance/vouchers`: tạo chiến dịch Voucher.
- `GET /api/finance/vouchers`: xem/quản lý danh sách Voucher.
- Hỗ trợ `discount_percent` hoặc `discount_amount`.
- Quản lý `max_uses`, `min_order_value`, `expires_at`.

### 4.2. FIN-F02 – Kiểm tra Voucher

`POST /api/finance/vouchers/validate`

Kiểm tra tính hợp lệ của mã giảm giá và trả về số tiền dự kiến được chiết khấu trong `discount_applied`.

### 4.3. FIN-F03 – Tự động sinh hóa đơn

`POST /api/finance/invoices/auto-generate`

Được Admission gọi khi chốt đăng ký; Finance tạo:
- `invoices` với trạng thái ban đầu `PENDING`.
- `invoice_items` cho gói học phí và phí học lại.
- `installments` kèm `payment_ref_code`.

### 4.4. FIN-F04 – Tra cứu hóa đơn

- `GET /api/finance/invoices`: danh sách hóa đơn.
- `GET /api/finance/invoices/{id}`: chi tiết hóa đơn, khoản mục học phí/học lại, lịch trả góp và lịch sử đóng tiền.

### 4.5. FIN-F05 – Thu tiền mặt

`POST /api/finance/payments/cash`

Ghi nhận phiếu thu tiền mặt tại quầy; cập nhật `paid_amount`, trạng thái kỳ đóng và trạng thái hóa đơn (`PARTIAL` / `PAID`).

### 4.6. FIN-F06 – VietQR và Webhook

- `GET /api/finance/invoices/{id}/vietqr`: sinh mã QR chứa `payment_ref_code`.
- `POST /api/finance/webhooks/vietqr`: nhận Webhook ngân hàng, tự động đối soát và gạch nợ theo thời gian thực.

### 4.7. FIN-F07 – Ví bảo lưu

- `GET /api/finance/wallets/{student_id}`: tra cứu ví.
- `POST /api/finance/wallets/{student_id}/reserve`: ghi nhận tiền bảo lưu/cấn trừ học phí khóa tiếp theo.

### 4.8. FIN-F08 – Hoàn tiền 3 cấp

- `POST /api/finance/refunds`: Tư vấn viên (STAFF) tạo yêu cầu cấp 1.
- `PUT /api/finance/refunds/{id}/verify`: Kế toán (STAFF) xác minh cấp 2.
- `PUT /api/finance/refunds/{id}/approve`: Giám đốc (ADMIN) phê duyệt cấp 3.
- `PUT /api/finance/refunds/{id}/complete`: Kế toán ghi nhận giải ngân.

### 4.9. FIN-F09 – BI tài chính

- `GET /api/finance/bi/cash-revenue`: doanh thu thực thu.
- `GET /api/finance/bi/voucher-campaigns`: hiệu quả Voucher.
- `GET /api/finance/bi/refund-summary`: tỷ lệ hoàn phí và quỹ bảo lưu.

---

## 5. Xử lý Giao dịch và Đồng thời

Mọi thao tác thu tiền (`CASH`, `VIETQR`), áp dụng Voucher và duyệt hoàn tiền đều chạy trong Database Transaction (`BEGIN ... COMMIT`) kết hợp khóa bi quan (`SELECT ... FOR UPDATE`) trên dòng hóa đơn/Voucher.

### 5.1. Áp dụng Voucher

1. Khóa dòng Voucher bằng `SELECT ... FOR UPDATE`.
2. Kiểm tra `is_active = TRUE`.
3. Kiểm tra `NOW() <= expires_at`.
4. Kiểm tra `current_uses < max_uses`.
5. Ghi nhận Voucher đã sử dụng và tăng `current_uses`.

### 5.2. Gạch nợ VietQR

1. Kiểm tra `bank_transaction_id` theo ràng buộc UNIQUE.
2. Nếu giao dịch đã tồn tại, trả `200 OK` và không tạo payment lần hai.
3. Nếu giao dịch mới, tạo payment với `payment_method = 'VIETQR'`, `status = 'SUCCESS'`.
4. Cập nhật `installments` và `invoices` theo trạng thái `PARTIAL` hoặc `PAID`.

### 5.3. Hoàn tiền

1. Lấy snapshot `total_sessions`, `attended_sessions` từ Learning Service.
2. Kiểm tra điều kiện số buổi.
3. Tính số tiền hoàn tối đa theo tỷ lệ hợp đồng sau khấu trừ.
4. Xử lý tuần tự ba cấp phê duyệt và giải ngân.

---

## 6. Quy ước Dữ liệu và Cơ sở Dữ liệu

- JSON field names sử dụng `snake_case`.
- Primary key sử dụng `SERIAL`.
- Logical Foreign Key sử dụng `INTEGER`.
- Finance sở hữu schema `finance`; không tạo FK vật lý sang schema Admission/Learning.
- Hóa đơn, chi tiết hóa đơn, kỳ thanh toán, payment, ví và refund được lưu theo 8 bảng nghiệp vụ của Finance.
- Hai BI Views: `finance.vw_bi_cash_revenue_monthly` và `finance.vw_bi_voucher_campaigns`.

# ĐẶC TẢ PHÂN TÍCH NGHIỆP VỤ & BÁO CÁO THÔNG MINH (MASTER BA/BI SPECIFICATION)
## PHÂN HỆ TÀI CHÍNH (FINANCE SERVICE)

> **Dự án:** Hệ thống Quản lý Trung tâm Ngoại ngữ (English Center Management System)  
> **Service:** `finance-service`  
> **Runtime:** Python 3.11 + FastAPI  
> **Port:** `8083`  
> **Gateway:** `/api/finance/...`  
> **Chuẩn kiến trúc:** Polyglot Microservices, Schema Isolation, SERIAL/INTEGER Keys, JSON `snake_case`

---

## MỤC LỤC
1. [Tổng quan Phân hệ & Phạm vi Nghiệp vụ](#1-tổng-quan-phân-hệ--phạm-vi-nghiệp-vụ)
2. [Quy tắc Bất biến Tài chính](#2-quy-tắc-bất-biến-tài-chính)
3. [Tác nhân và Phân quyền](#3-tác-nhân-và-phân-quyền)
4. [Quy trình Nghiệp vụ Cốt lõi](#4-quy-trình-nghiệp-vụ-cốt-lõi)
5. [Danh mục Yêu cầu Chức năng](#5-danh-mục-yêu-cầu-chức-năng)
6. [Chỉ số Quản trị & BI](#6-chỉ-số-quản-trị--bi)

---

## 1. Tổng quan Phân hệ & Phạm vi Nghiệp vụ

### 1.1. Mục tiêu nghiệp vụ

Finance Service quản lý nghĩa vụ học phí và dòng tiền của học viên, từ cấu hình Voucher, lập hóa đơn, chia kỳ thanh toán, ghi nhận tiền mặt/chuyển khoản, quản lý ví bảo lưu đến xử lý hoàn phí và cung cấp chỉ số BI theo dòng tiền thực thu.

### 1.2. Phạm vi trong hệ thống (In-Scope)

- **Cấu trúc học phí trọn gói (Course Package):** Học phí được ghi nhận theo khóa học. Phí kiểm tra đầu vào và giáo trình/tài liệu được gộp chung mặc định vào gói học phí chuẩn.
- **Phụ phí học lại (Retake Fee):** Có thể gộp vào hóa đơn khóa học chính theo loại `MIXED`, hoặc tách thành hóa đơn độc lập `STANDALONE_RETAKE`.
- **Chiến dịch Voucher:** Hỗ trợ giảm theo phần trăm (`discount_percent`) hoặc số tiền cố định (`discount_amount`); quản lý `max_uses`, `current_uses`, `min_order_value` và `expires_at`.
- **Tự động phát hành hóa đơn và chia đợt đóng phí:** Hóa đơn được sinh tự động khi Admission chốt đăng ký khóa học; hỗ trợ thanh toán một lần 100%, đặt cọc giữ chỗ hoặc trả góp nhiều đợt theo `due_date`.
- **Thanh toán đa kênh và VietQR:** Thu tiền mặt tại quầy (`CASH`) và chuyển khoản qua mã VietQR động; tự động đối soát và gạch nợ qua Webhook.
- **Ví bảo lưu nội bộ:** Mặc định `is_withdrawable = FALSE`; tiền bảo lưu chỉ dùng để cấn trừ học phí cho khóa học tiếp theo.
- **Quy trình hoàn tiền 3 cấp:** Chỉ cho phép hoàn một phần học phí theo tỷ lệ hợp đồng sau khấu trừ nếu học viên mới học trong giới hạn `attended_sessions <= max_allowed_sessions`. Nếu vượt giới hạn thì chặn hoàn tiền. Quy trình duyệt: Tư vấn viên (STAFF) → Kế toán (STAFF) → Giám đốc trung tâm (ADMIN).
- **Báo cáo BI:** Ghi nhận doanh thu theo dòng tiền thực thu (Cash-basis), thống kê hiệu quả Voucher và tỷ lệ hoàn phí/bảo lưu.

### 1.3. Ngoài phạm vi (Out-of-Scope)

- Xử lý chênh lệch khi chuyển lớp/chuyển khóa.
- Chuyển nhượng học phí giữa các học viên.
- Quản lý chi phí vận hành (OpEx).
- Quản lý bảng lương nhân sự/giáo viên.

---

## 2. Quy tắc Bất biến Tài chính

| Mã | Tên quy tắc | Mô tả ràng buộc kỹ thuật và nghiệp vụ |
|---|---|---|
| **INV-FIN-01** | Bất biến hóa đơn đã thanh toán | Hóa đơn ở trạng thái `PAID` hoặc `REFUNDED` tuyệt đối không được xóa và không được sửa trực tiếp các cột tiền tệ (`amount`, `discount_applied`, `final_amount`). |
| **INV-FIN-02** | Đẳng thức toán học hóa đơn và trả góp | Luôn bảo đảm `final_amount = amount - discount_applied >= 0`; `0 <= paid_amount <= final_amount`; tổng `amount_due` của các đợt `installments` thuộc một hóa đơn phải bằng đúng `final_amount`. |
| **INV-FIN-03** | Cô lập Schema (Schema Isolation) | Finance Service chỉ truy cập schema `finance`. Các cột `student_id`, `course_id`, `class_id` lưu kiểu INTEGER (Logical FK), không JOIN hoặc tạo FK vật lý sang schema `admission` hay `learning`. |
| **INV-FIN-04** | Chống Race Condition khi dùng Voucher | Khi áp dụng Voucher, kiểm tra `is_active = TRUE`, `NOW() <= expires_at`, `current_uses < max_uses` bằng khóa dòng `SELECT ... FOR UPDATE` trước khi tăng `current_uses`. |
| **INV-FIN-05** | Idempotency gạch nợ VietQR | Mỗi giao dịch Webhook VietQR phải kiểm tra `bank_transaction_id UNIQUE`. Nếu mã giao dịch ngân hàng đã tồn tại, trả về `200 OK` nhưng không ghi nhận phiếu thu lần 2. |
| **INV-FIN-06** | Khóa rút tiền ví bảo lưu | Bảng `finance.student_wallets` luôn giữ `is_withdrawable = FALSE`; số dư ví chỉ giảm khi thực hiện giao dịch `TUITION_OFFSET` (cấn trừ hóa đơn mới). |
| **INV-FIN-07** | Chặn hoàn tiền theo số buổi thực học | Chỉ cho phép tạo yêu cầu hoàn tiền khi `attended_sessions <= max_allowed_sessions` (ví dụ tối đa 3 buổi đầu) và đi qua đủ ba cấp: `PENDING_ACCOUNTANT` → `PENDING_DIRECTOR` → `APPROVED` → `COMPLETED`. |

---

## 3. Tác nhân và Phân quyền

| Tác nhân | Vai trò nghiệp vụ | Trách nhiệm |
|---|---|---|
| **Học viên (STUDENT)** | Người sử dụng dịch vụ đào tạo | Kiểm tra Voucher; xem hóa đơn; nhận mã VietQR; xem ví bảo lưu. |
| **Tư vấn viên (STAFF)** | Cấp 1 của quy trình hoàn tiền | Phối hợp chốt đăng ký; khởi tạo yêu cầu hoàn tiền và kiểm tra điều kiện số buổi. |
| **Kế toán (STAFF)** | Nhân sự tài chính | Ghi nhận thu tiền mặt; quản lý ví; xác minh công nợ và buổi thực học; hoàn tất giải ngân. |
| **Giám đốc (ADMIN)** | Cấp phê duyệt cuối | Phê duyệt yêu cầu hoàn tiền và xem báo cáo BI. |
| **Cổng VietQR (Webhook)** | Hệ thống bên ngoài | Gửi thông báo giao dịch ngân hàng để Finance đối soát. |
| **Admission Service** | Service tích hợp | Gọi Finance để sinh hóa đơn và lịch đóng phí khi chốt đăng ký. |
| **Learning Service** | Service tích hợp | Cung cấp tổng số buổi và số buổi học viên đã tham gia để xét hoàn tiền/bảo lưu. |

### 3.1. Ma trận phân quyền theo API

| Nhóm nghiệp vụ | Vai trò được phép |
|---|---|
| Quản lý Voucher | ADMIN, STAFF |
| Kiểm tra Voucher | ADMIN, STAFF, STUDENT |
| Sinh hóa đơn tự động | ADMIN, STAFF hoặc Internal |
| Tra cứu hóa đơn | ADMIN, STAFF, STUDENT |
| Thu tiền mặt | ADMIN, STAFF |
| VietQR | STUDENT, STAFF; Webhook từ cổng ngân hàng |
| Ví bảo lưu | ADMIN, STAFF, STUDENT |
| Hoàn tiền | Cấp 1: STAFF (Tư vấn); Cấp 2: STAFF (Kế toán); Cấp 3: ADMIN (Giám đốc) |
| Báo cáo BI | ADMIN, STAFF |

---

## 4. Quy trình Nghiệp vụ Cốt lõi

### 4.1. Tự động sinh hóa đơn khi chốt đăng ký

1. Tư vấn viên chốt đăng ký khóa học trên Admission Service.
2. Admission gọi nội bộ `POST /api/finance/invoices/auto-generate`.
3. Finance kiểm tra Voucher bằng `SELECT ... FOR UPDATE`, kiểm tra điều kiện và tăng `current_uses`.
4. Finance tạo hóa đơn với trạng thái `PENDING`.
5. Finance tạo các khoản mục `invoice_items` (gói học phí và phí học lại nếu có).
6. Finance tạo các kỳ `installments` và sinh `payment_ref_code`.
7. Finance trả `invoice_id`, `final_amount` và `payment_ref_code` cho Admission.

### 4.2. Thanh toán tiền mặt

1. Kế toán ghi nhận phiếu thu qua `POST /api/finance/payments/cash`.
2. Finance ghi nhận khoản thanh toán.
3. Cập nhật `paid_amount` của hóa đơn và số tiền đã thanh toán ở kỳ liên quan.
4. Cập nhật trạng thái kỳ đóng và trạng thái hóa đơn thành `PARTIAL` hoặc `PAID` theo số tiền đã thu.

### 4.3. Thanh toán VietQR và tự động gạch nợ

1. Học viên yêu cầu mã QR qua `GET /api/finance/invoices/{id}/vietqr`.
2. Finance trả mã VietQR chứa `payment_ref_code`.
3. Học viên quét QR và chuyển khoản.
4. Ngân hàng gửi Webhook tới `POST /api/finance/webhooks/vietqr`.
5. Finance kiểm tra `bank_transaction_id` để bảo đảm idempotency.
6. Nếu giao dịch đã tồn tại, trả `200 OK` và không ghi nhận lần thứ hai.
7. Nếu là giao dịch mới, ghi nhận `payments` với `payment_method = 'VIETQR'`, `status = 'SUCCESS'`; cập nhật `installments` và `invoices` sang `PARTIAL` hoặc `PAID`.

### 4.4. Quản lý ví bảo lưu

1. Học viên/nhân viên tra cứu ví qua `GET /api/finance/wallets/{student_id}`.
2. Finance hiển thị số dư và trạng thái ví.
3. Khi ghi nhận tiền bảo lưu hoặc cấn trừ học phí, sử dụng `POST /api/finance/wallets/{student_id}/reserve`.
4. Ví luôn có `is_withdrawable = FALSE`; số dư chỉ giảm khi phát sinh `TUITION_OFFSET`.

### 4.5. Quy trình hoàn tiền 3 cấp

1. Tư vấn viên gửi `POST /api/finance/refunds` với `invoice_id`, `class_id`, `reason`.
2. Finance gọi Learning Service để lấy `total_sessions` và `attended_sessions`.
3. Nếu `attended_sessions > max_allowed_sessions`, Finance từ chối yêu cầu.
4. Nếu đủ điều kiện, Finance tính số tiền hoàn theo tỷ lệ hợp đồng và khoản khấu trừ; tạo yêu cầu trạng thái `PENDING_ACCOUNTANT`.
5. Kế toán xác minh qua `PUT /api/finance/refunds/{id}/verify`; trạng thái chuyển `PENDING_DIRECTOR`.
6. Giám đốc phê duyệt qua `PUT /api/finance/refunds/{id}/approve`; trạng thái chuyển `APPROVED`.
7. Kế toán ghi nhận giải ngân qua `PUT /api/finance/refunds/{id}/complete`; yêu cầu chuyển `COMPLETED`, hóa đơn chuyển `REFUNDED`.

---

## 5. Danh mục Yêu cầu Chức năng

| Mã | Tên chức năng | Mô tả nghiệp vụ | Đầu ra chính |
|---|---|---|---|
| **FIN-F01** | Quản lý Voucher | Tạo và quản lý chiến dịch Voucher theo phần trăm hoặc số tiền cố định; kiểm soát max_uses, min_order_value, expires_at. | Thông tin chiến dịch Voucher. |
| **FIN-F02** | Kiểm tra Voucher | Kiểm tra tính hợp lệ của mã giảm giá và tính số tiền được chiết khấu dự kiến. | `discount_applied`. |
| **FIN-F03** | Tự động sinh hóa đơn | Sinh hóa đơn khi Admission chốt đăng ký; hỗ trợ gộp/tách phí học lại và chia lịch đóng phí. | Invoice, invoice_items, installments. |
| **FIN-F04** | Tra cứu hóa đơn | Tra cứu danh sách/chi tiết hóa đơn, khoản mục, lịch trả góp và lịch sử đóng tiền. | Chi tiết hóa đơn và lịch sử thanh toán. |
| **FIN-F05** | Ghi nhận thanh toán tiền mặt | Ghi nhận phiếu thu tại quầy và cập nhật số tiền đã thanh toán. | Payment receipt, trạng thái kỳ và hóa đơn. |
| **FIN-F06** | VietQR và Webhook | Sinh QR động; nhận Webhook và tự động gạch nợ theo thời gian thực. | Payment, trạng thái kỳ và hóa đơn. |
| **FIN-F07** | Ví bảo lưu | Quản lý ví học viên, cộng tiền bảo lưu và cấn trừ học phí khóa tiếp theo. | Wallet balance và wallet transaction. |
| **FIN-F08** | Hoàn tiền 3 cấp | Kiểm tra số buổi, tính mức hoàn sau khấu trừ, xác minh, phê duyệt và giải ngân. | Refund request và trạng thái phê duyệt. |
| **FIN-F09** | BI tài chính | Cung cấp doanh thu thực thu, Voucher, tỷ lệ hoàn phí và quỹ bảo lưu. | Dữ liệu BI Dashboard. |

---

## 6. Chỉ số Quản trị & BI

### 6.1. Tổng thực thu (Gross Cash-in)

Tổng `amount` trong bảng `finance.payments` có `status = 'SUCCESS'` và `payment_method IN ('CASH', 'VIETQR')`.

Không tính giao dịch `WALLET_OFFSET` vào dòng tiền mới.

### 6.2. Doanh thu thuần thực thu (Net Cash Revenue)

`Gross Cash-in - SUM(approved_refund_amount)` của các yêu cầu hoàn phí có `status = 'COMPLETED'`.

### 6.3. Công nợ phải thu và quá hạn (Outstanding AR & Overdue AR)

- Công nợ phải thu: tổng `remaining_amount` của các hóa đơn ở trạng thái `PENDING` hoặc `PARTIAL`.
- Công nợ quá hạn: phân nhóm dựa trên `due_date < CURRENT_DATE` trong bảng `finance.installments`.

### 6.4. Hiệu quả chiến dịch Voucher (Voucher Campaign ROI)

- Tỷ lệ sử dụng: `(current_uses / max_uses) * 100%`.
- Tổng tiền giảm giá đã cấp: `SUM(discount_applied)`.
- Tổng tiền mặt thực thu mang về từ các hóa đơn áp dụng Voucher.

### 6.5. Tỷ lệ hoàn phí và quỹ bảo lưu (Refund & Retention Rate)

- Tỷ lệ hoàn phí: `(Tổng tiền hoàn / Gross Cash-in) * 100%`.
- Quỹ bảo lưu đang giữ: `SUM(balance)` trong `finance.student_wallets`.

# ĐẶC TẢ PHÂN TÍCH NGHIỆP VỤ & BÁO CÁO THÔNG MINH (MASTER BA/BI SPECIFICATION)
## PHÂN HỆ TÀI CHÍNH (FINANCE SERVICE)

> **Dự án:** Hệ thống Quản lý Trung tâm Anh ngữ  
> **Dịch vụ phụ trách:** Finance Service (`finance-service`, Python 3.11+, FastAPI)  
> **Port nội bộ:** `8084` (theo `docs/architecture.md`)  
> **Cơ sở dữ liệu:** PostgreSQL 16, schema sở hữu `finance`  
> **Phiên bản:** 1.0 – Master BA/BI Specification  

---

## MỤC LỤC
1. [Tổng quan Phân hệ & Mục tiêu Nghiệp vụ](#1-tổng-quan-phân-hệ--mục-tiêu-nghiệp-vụ)
   - 1.1. Mục tiêu Nghiệp vụ
   - 1.2. Phạm vi Trách nhiệm & Ngoài phạm vi
   - 1.3. Vị trí của Finance trong kiến trúc hệ thống
2. [Tác nhân Hệ thống & Phân quyền](#2-tác-nhân-hệ-thống--phân-quyền)
   - 2.1. Danh mục Tác nhân
   - 2.2. Ma trận Phân quyền nghiệp vụ
3. [Quy trình Nghiệp vụ Cốt lõi](#3-quy-trình-nghiệp-vụ-cốt-lõi)
   - 3.1. Cấu hình biểu phí và chính sách giảm giá
   - 3.2. Lập hóa đơn và theo dõi công nợ
   - 3.3. Ghi nhận thanh toán
   - 3.4. Quy trình mục tiêu: Voucher Campaign, Installments, VietQR, Wallet và Refund
4. [Danh mục Yêu cầu Chức năng (Functional Requirements)](#4-danh-mục-yêu-cầu-chức-năng-functional-requirements)
5. [Định nghĩa Chỉ số Quản trị & BI](#5-định-nghĩa-chỉ-số-quản-trị--bi)
6. [Quy tắc Nghiệp vụ & Ràng buộc Dữ liệu](#6-quy-tắc-nghiệp-vụ--ràng-buộc-dữ-liệu)

---

## 1. Tổng quan Phân hệ & Mục tiêu Nghiệp vụ

### 1.1. Mục tiêu Nghiệp vụ

Finance Service chịu trách nhiệm quản lý nghĩa vụ học phí và dòng tiền của học viên trong hệ thống Trung tâm Anh ngữ. Phân hệ nhận các định danh liên quan từ Admission/Student, quản lý biểu phí, lập hóa đơn, ghi nhận khoản thu, theo dõi số tiền đã thanh toán và số tiền còn phải thu.

Finance Service đáp ứng các mục tiêu nghiệp vụ sau:
- Quản lý học phí theo gói khóa học; phí kiểm tra đầu vào và giáo trình/tài liệu được gộp vào gói chuẩn theo chính sách.
- Hỗ trợ phí học lại gộp trong hóa đơn chính (`MIXED`) hoặc lập hóa đơn riêng (`STANDALONE_RETAKE`).
- Quản lý Voucher theo phần trăm hoặc số tiền cố định, giới hạn lượt dùng, giá trị đơn tối thiểu và thời hạn.
- Tự động sinh hóa đơn khi Admission chốt đăng ký; hỗ trợ thanh toán một lần hoặc nhiều đợt.
- Hỗ trợ thu tiền mặt, chuyển khoản ngân hàng và đối soát giao dịch VietQR tự động qua Webhook.
- Quản lý ví bảo lưu nội bộ, khóa rút tiền mặt tự do; dùng số dư để cấn trừ học phí sau.
- Hoàn phí theo số buổi thực học, tỷ lệ hoàn, khoản khấu trừ và quy trình phê duyệt 3 cấp.
- Cung cấp BI theo dòng tiền thực thu (cash-basis).

### 1.2. Phạm vi Trách nhiệm & Ngoài phạm vi

**Thuộc phạm vi Finance:**
- Quản lý biểu phí học phí gắn với `course_id`.
- Quản lý mã giảm giá gắn với biểu phí trong hiện trạng MVP.
- Lập và tra cứu hóa đơn, liên kết `student_id`, `enrollment_id`, `tuition_fee_id`.
- Ghi nhận thanh toán, lịch sử giao dịch và tính số tiền còn phải thu.
- Thiết kế mở rộng: Voucher Campaign, invoice items, installments, VietQR, ví bảo lưu và yêu cầu hoàn tiền.
- Báo cáo doanh thu thực thu, Voucher, hoàn phí và số dư bảo lưu.

**Ngoài phạm vi Finance:**
- Quản lý khóa học, lớp học và đơn tuyển sinh: Admission sở hữu.
- Quản lý hồ sơ học viên: Student/Identity sở hữu.
- Quản lý lịch học, điểm danh, buổi học và kết quả học tập: Student/Learning sở hữu.
- Chi phí vận hành và bảng lương nhân sự/giáo viên.
- Chuyển nhượng học phí giữa học viên; xử lý chênh lệch chuyển lớp/chuyển khóa chưa được mô tả trong phạm vi tài liệu Finance.

### 1.3. Vị trí của Finance trong kiến trúc hệ thống

Theo `docs/architecture.md`, Nginx Gateway chạy cổng 8080; Admission 8081; Student 8082; Learning 8083; Finance 8084. Finance truy cập PostgreSQL thông qua schema `finance`.

```text
Browser / Frontend
       |
       v
Nginx API Gateway (:8080)
       |
       +---- /api/finance/* ----> Finance Service (:8084)
                                      |
                                      v
                              PostgreSQL / finance
                                      |
                 +--------------------+-------------------+
                 |                    |                   |
          Admission Service     Student Service    Learning Service
```

Nguyên tắc dữ liệu:
- Finance sở hữu biểu phí, hóa đơn và thanh toán trong schema `finance`.
- Các cột `course_id`, `student_id`, `enrollment_id`, `class_id` là logical reference liên service; không tạo FK vật lý chéo schema.
- Muốn lấy thông tin chi tiết từ service khác phải gọi REST API.
- JSON dùng `snake_case`; ID nội bộ dùng integer/SERIAL.

---

## 2. Tác nhân Hệ thống & Phân quyền

### 2.1. Danh mục Tác nhân

| Tác nhân | Vai trò & Trách nhiệm trong Finance |
|---|---|
| **Học viên (`STUDENT`)** | Tra cứu hóa đơn và tình trạng thanh toán của bản thân; thực hiện thanh toán; xem ví bảo lưu khi tính năng được triển khai. |
| **Nhân viên Tư vấn/Tuyển sinh (`STAFF`)** | Khởi tạo luồng yêu cầu hóa đơn thông qua Admission; hỗ trợ học viên; tạo yêu cầu hoàn phí theo quy trình mục tiêu. |
| **Kế toán (`STAFF`)** | Quản lý biểu phí, ghi nhận tiền mặt, kiểm tra giao dịch, theo dõi công nợ; xác minh và hoàn tất hồ sơ hoàn phí. |
| **Giám đốc (`ADMIN`)** | Quản trị cấu hình tài chính, theo dõi báo cáo và phê duyệt cấp cuối đối với hoàn phí theo quy trình nghiệp vụ. |
| **Admission Service** | Gửi thông tin đăng ký/định danh để Finance lập hóa đơn; truy vấn trạng thái thanh toán theo hợp đồng tích hợp. |
| **Student Service** | Là nguồn sở hữu hồ sơ học viên; Finance chỉ lưu ID tham chiếu. |
| **Learning Service** | Nguồn dữ liệu buổi học/điểm danh khi triển khai quy trình xét hoàn phí. |
| **Ngân hàng / VietQR Webhook** | Gửi thông báo giao dịch chuyển khoản để Finance đối soát và ghi nhận thanh toán. |

### 2.2. Ma trận Phân quyền nghiệp vụ

Ma trận dưới đây mô tả phân quyền nghiệp vụ mục tiêu. Backend hiện tại chưa thể hiện middleware kiểm tra JWT/role ở các route Finance; vì vậy bảng này không phải bằng chứng authorization đã được triển khai.

| Nhóm chức năng | STUDENT | STAFF – Tư vấn | STAFF – Kế toán | ADMIN |
|---|:---:|:---:|:---:|:---:|
| Xem hóa đơn của bản thân | ✓ | – | – | ✓ |
| Quản lý biểu phí | – | – | ✓ | ✓ |
| Tạo hóa đơn theo quy trình nội bộ | – | qua Admission | ✓ | ✓ |
| Ghi nhận thanh toán | – | – | ✓ | ✓ |
| Xem lịch sử thanh toán của bản thân | ✓ | – | ✓ | ✓ |
| Quản lý chiến dịch Voucher | – | hỗ trợ | ✓ | ✓ |
| Xem ví bảo lưu của bản thân | ✓ | – | ✓ | ✓ |
| Tạo yêu cầu hoàn phí | – | ✓ | hỗ trợ | theo phân công |
| Xác minh hoàn phí cấp 2 | – | – | ✓ | – |
| Phê duyệt hoàn phí cấp cuối | – | – | – | ✓ |
| Xem BI tài chính | – | – | ✓ | ✓ |

---

## 3. Quy trình Nghiệp vụ Cốt lõi

### 3.1. Cấu hình biểu phí và chính sách giảm giá

Luồng hiện trạng theo backend:
1. Nhân viên Finance nhập `course_id`, `amount`, `currency`, `discount_code`, `discount_amount`, `note`.
2. Backend kiểm tra `amount > 0` và `discount_amount <= amount`.
3. Bản ghi được lưu vào `finance.tuition_fees`.
4. Nếu đã có biểu phí cho `course_id`, backend dùng `ON CONFLICT (course_id) DO UPDATE` để cập nhật bản ghi.
5. Frontend hiển thị học phí chuẩn, mã giảm giá, số tiền giảm và học phí sau giảm.

[
\text{Net Tuition} = \max(\text{amount} - \text{discount\_amount}, 0)
]

Giới hạn hiện trạng: `discount_code` là mã giảm giá gắn với biểu phí theo khóa học, chưa phải hệ thống Voucher Campaign độc lập có hạn mức lượt dùng và thời hạn.

### 3.2. Lập hóa đơn và theo dõi công nợ

1. Nhận `student_id`, `enrollment_id`, `tuition_fee_id`, số tiền (nếu truyền) và `due_date`.
2. Khi `tuition_fee_id` được cung cấp, Finance đọc biểu phí; nếu không truyền số tiền hợp lệ, hệ thống tính `amount - discount_amount`.
3. Nếu không truyền `invoice_code`, backend sinh mã dạng `INV-<6 ký tự>`.
4. Backend kiểm tra mã hóa đơn trùng.
5. Trạng thái ban đầu là `UNPAID`; nếu `due_date` ở quá khứ tại thời điểm tạo thì trạng thái là `OVERDUE`.
6. Khi truy vấn danh sách hóa đơn, backend cập nhật hóa đơn `UNPAID` đã quá hạn thành `OVERDUE`.
7. Backend tổng hợp các payment để trả thêm `paid_amount` và `remaining_amount`.

[
\text{Paid Amount} = \sum \text{payments.amount}
]

[
\text{Remaining Amount} = \max(\text{invoice.amount} - \text{Paid Amount}, 0)
]

### 3.3. Ghi nhận thanh toán

1. Client gửi `invoice_id`, `amount`, `payment_method`, `transaction_ref`.
2. Backend từ chối nếu `amount <= 0` hoặc mã giao dịch rỗng.
3. Backend khóa dòng hóa đơn bằng `SELECT ... FOR UPDATE`.
4. Không cho thanh toán hóa đơn `CANCELLED`.
5. Kiểm tra `transaction_ref` đã tồn tại; nếu có thì từ chối ghi nhận lần hai.
6. Tạo bản ghi `finance.payments`.
7. Tính tổng tiền đã thu. Khi tổng này lớn hơn hoặc bằng `invoice.amount`, hóa đơn chuyển sang `PAID`; nếu chưa đủ thì giữ trạng thái hiện tại.
8. Trả payment cùng `total_paid`, `invoice_amount`, `invoice_status`.


### 3.4. Quy trình mục tiêu: Voucher Campaign, Installments, VietQR, Wallet và Refund

Các quy trình nghiệp vụ của Finance bao gồm:

**Voucher Campaign**
- Voucher hỗ trợ `discount_percent` hoặc `discount_amount`.
- Điều kiện gồm `min_order_value`, `valid_from`, `expires_at`, `max_uses`, `current_uses`, `is_active`.
- Khi áp dụng, phải kiểm tra điều kiện và khóa dòng Voucher để tránh vượt số lượt sử dụng.

**Invoice Items và Installments**
- Hóa đơn có thể chứa gói học phí và phí học lại.
- Phí học lại có thể gộp vào hóa đơn chính hoặc tách riêng.
- Tổng `amount_due` của các kỳ thanh toán phải bằng `final_amount`.
- Từng kỳ có `due_date`, `amount_due`, `amount_paid`, `status`, `payment_ref_code`.

**VietQR**
- Finance tạo mã thanh toán động có tham chiếu hóa đơn/kỳ thanh toán.
- Webhook ngân hàng gửi mã giao dịch, số tiền và nội dung chuyển khoản.
- Finance xác minh và chống ghi nhận lặp bằng mã giao dịch duy nhất.

**Ví bảo lưu**
- Tiền bảo lưu được ghi tăng vào ví; mọi biến động phải có bản ghi giao dịch.
- Theo chính sách nguồn, `is_withdrawable = FALSE`; tiền chỉ dùng cấn trừ học phí khóa tiếp theo.

**Hoàn phí 3 cấp**
- Tạo yêu cầu cần snapshot tổng số buổi và số buổi đã tham gia từ Learning.
- Chỉ tiếp nhận khi `attended_sessions <= max_allowed_sessions`.
- Quy trình mục tiêu: Tư vấn viên tạo yêu cầu → Kế toán xác minh → Giám đốc duyệt → Kế toán ghi nhận hoàn tất.
- Tài liệu nêu giới hạn mặc định tối đa 3 buổi đầu; tỷ lệ hoàn và khoản khấu trừ cần được phê duyệt chính thức trước triển khai.

---

## 4. Danh mục Yêu cầu Chức năng (Functional Requirements)

### Nhóm 1: Biểu phí và chính sách giảm giá (FR-TUI)
- **FIN-F01 (Quản lý Biểu phí & Voucher)**: Quản lý mức học phí theo khóa học, đơn vị tiền tệ, mã giảm giá, số tiền giảm và ghi chú chính sách. Hỗ trợ cấu hình chiến dịch Voucher với loại giảm theo phần trăm hoặc số tiền cố định, điều kiện đơn hàng tối thiểu, thời gian hiệu lực và giới hạn lượt sử dụng.
- **FIN-F02 (Kiểm tra tính hợp lệ Voucher)**: Kiểm tra mã Voucher, trạng thái hoạt động, thời gian hiệu lực, số lượt còn lại và điều kiện giá trị đơn hàng; trả về kết quả hợp lệ cùng số tiền giảm dự kiến.

### Nhóm 2: Hóa đơn và công nợ (FR-INV)
- **FIN-F03 (Tạo Hóa đơn)**: Lập hóa đơn cho học viên theo thông tin đăng ký, khóa học và biểu phí; hỗ trợ sinh hóa đơn tự động sau khi Admission chốt đăng ký. Hóa đơn có thể bao gồm gói học phí và phí học lại, được gộp hoặc tách theo loại hóa đơn; hỗ trợ lịch thanh toán một lần hoặc nhiều đợt.
- **FIN-F04 (Tra cứu Hóa đơn)**: Cho phép tra cứu danh sách và chi tiết hóa đơn, các khoản mục, lịch thanh toán, lịch sử thu, số tiền đã thanh toán, số tiền còn phải thu và trạng thái công nợ.

### Nhóm 3: Thanh toán và đối soát (FR-PAY)
- **FIN-F05 (Ghi nhận Thanh toán)**: Ghi nhận khoản thu tiền mặt tại quầy, liên kết giao dịch với hóa đơn và kỳ thanh toán; cập nhật số tiền đã thu và trạng thái tương ứng.
- **FIN-F06 (VietQR & Webhook Đối soát)**: Sinh mã VietQR động theo hóa đơn/kỳ thanh toán; tiếp nhận webhook từ ngân hàng, xác thực nội dung giao dịch và tự động ghi nhận khoản thu. Bảo đảm một giao dịch ngân hàng chỉ được ghi nhận một lần.

### Nhóm 4: Bảo lưu và hoàn phí (FR-REF)
- **FIN-F07 (Ví Bảo lưu Học viên)**: Quản lý số dư bảo lưu của học viên và lịch sử biến động ví. Tiền bảo lưu không được rút thành tiền mặt tự do; chỉ được sử dụng để cấn trừ học phí theo quy định.
- **FIN-F08 (Quy trình Hoàn phí 3 cấp)**: Tiếp nhận yêu cầu hoàn phí, kiểm tra số buổi thực học, tính số tiền hoàn sau khấu trừ, xác minh bởi Kế toán, phê duyệt bởi Giám đốc và ghi nhận kết quả hoàn tiền.

### Nhóm 5: Báo cáo quản trị (FR-BI)
- **FIN-F09 (Báo cáo BI Tài chính)**: Cung cấp báo cáo doanh thu thực thu, công nợ phải thu/quá hạn, hiệu quả Voucher, tỷ lệ hoàn phí và số dư quỹ bảo lưu.
 
---
 
## 5. Định nghĩa Chỉ số Quản trị & BI

Các chỉ số dưới đây thống nhất cách tính và ý nghĩa quản trị cho hoạt động tài chính của trung tâm.

| Mã BI | Chỉ số | Công thức/định nghĩa | Mục đích |
|---|---|---|---|
| **BI-FIN-01** | Gross Cash-in | Tổng payment thành công CASH hoặc VIETQR; không tính WALLET_OFFSET. | Dòng tiền mới thu được. |
| **BI-FIN-02** | Net Cash Revenue | Gross Cash-in trừ tiền hoàn có trạng thái COMPLETED. | Doanh thu thuần theo dòng tiền. |
| **BI-FIN-03** | Outstanding AR | Tổng remaining_amount của hóa đơn chưa thanh toán đủ. | Đo công nợ phải thu. |
| **BI-FIN-04** | Overdue AR | Công nợ có due_date nhỏ hơn ngày hiện tại. | Theo dõi nợ quá hạn. |
| **BI-FIN-05** | Voucher Usage Rate | `current_uses / max_uses * 100%`. | Mức sử dụng chiến dịch. |
| **BI-FIN-06** | Total Discount Given | Tổng `discount_applied` trên hóa đơn dùng Voucher. | Tổng giá trị ưu đãi đã cấp. |
| **BI-FIN-07** | Refund Rate | Tổng tiền hoàn / Gross Cash-in × 100%. | Theo dõi tỷ lệ hoàn phí. |
| **BI-FIN-08** | Wallet Balance | Tổng `student_wallets.balance`. | Tổng quỹ bảo lưu đang giữ. |

### Chỉ số có thể suy ra từ MVP hiện tại
- Tổng tiền đã thu của một hóa đơn: `SUM(finance.payments.amount)`.
- Số tiền còn phải thu: `GREATEST(invoice.amount - SUM(payments.amount), 0)`.
- Trạng thái quá hạn: invoice `UNPAID` có `due_date < CURRENT_DATE` được cập nhật thành `OVERDUE` trong luồng GET invoices.

---

## 6. Quy tắc Nghiệp vụ & Ràng buộc Dữ liệu

### 6.1. Quy tắc đang có trong repository

| Mã tham chiếu | Quy tắc | Bằng chứng hiện có |
|---|---|---|
| INV-FIN-01 | Invoice amount và payment amount phải dương. | CHECK trong DDL; Pydantic gt=0; kiểm tra backend. |
| INV-FIN-02 | `transaction_ref` không được ghi nhận hai lần. | UNIQUE trong DDL; kiểm tra trước INSERT và bắt IntegrityError. |
| INV-FIN-03 | Chỉ chuyển PAID khi tổng payment >= invoice.amount. | Logic trong make_payment; được liệt kê trong docs/invariants.md. |

### 6.2. Quy tắc nghiệp vụ tài chính

| Mã quy tắc | Nội dung |
|---|---|
| INV-FIN-01 | Hóa đơn PAID/REFUNDED không được xóa hoặc sửa trực tiếp các trường tiền. |
| INV-FIN-02 | final_amount = amount - discount_applied; tổng installments bằng final_amount; paid_amount không vượt final_amount. |
| INV-FIN-03 | Schema isolation; ID liên service là logical reference. |
| INV-FIN-04 | Voucher phải khóa dòng khi kiểm tra và tăng lượt dùng. |
| INV-FIN-05 | Webhook VietQR idempotent theo bank_transaction_id. |
| INV-FIN-06 | Ví bảo lưu không cho rút tự do; chỉ cấn trừ học phí. |
| INV-FIN-07 | Chặn hoàn phí khi vượt giới hạn số buổi và bắt buộc qua luồng duyệt. |


---

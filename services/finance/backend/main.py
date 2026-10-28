import os
import uuid
from datetime import date
from typing import Optional
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres_secret_password")
DB_HOST = os.getenv("DB_HOST", "postgres")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "english_center")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"options": "-csearch_path=finance,public"}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI(title="Finance Microservice", version="2.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================
# PYDANTIC MODELS (Chuẩn snake_case)
# ==========================================

class TuitionFeeCreate(BaseModel):
    course_id: int
    amount: float = Field(..., gt=0, description="INV-FIN-01: Học phí chuẩn phải > 0")
    currency: str = "VND"
    discount_code: Optional[str] = None
    discount_amount: float = Field(default=0.0, ge=0, description="Số tiền giảm phải >= 0")
    note: Optional[str] = None


class InvoiceCreate(BaseModel):
    invoice_code: Optional[str] = None
    student_id: int
    enrollment_id: Optional[int] = None
    tuition_fee_id: Optional[int] = None  # Khóa ngoại liên kết tới bảng tuition_fees
    amount: Optional[float] = None        # Nếu truyền, có thể ghi đè; nếu không, tự động tính từ tuition_fee_id
    due_date: Optional[date] = None


class PaymentCreate(BaseModel):
    invoice_id: int
    amount: float = Field(..., gt=0, description="INV-FIN-01: Số tiền đóng phải > 0")
    payment_method: str = Field(default="BANK_TRANSFER", pattern="^(CASH|BANK_TRANSFER)$")
    transaction_ref: str = Field(..., min_length=1, description="INV-FIN-02: Mã giao dịch bắt buộc để chống trùng lặp")


# ==========================================
# HEALTH CHECK & STARTUP MIGRATION HỖ TRỢ CSDL
# ==========================================

@app.on_event("startup")
def ensure_finance_schema_and_constraints():
    """Tự động kiểm tra và thêm cột tuition_fee_id vào bảng invoices nếu chưa có."""
    with SessionLocal() as session:
        try:
            session.execute(text("""
                DO $$
                BEGIN
                    -- Thêm cột tuition_fee_id vào bảng invoices nếu chưa tồn tại
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_schema = 'finance' AND table_name = 'invoices' AND column_name = 'tuition_fee_id'
                    ) THEN
                        ALTER TABLE finance.invoices ADD COLUMN tuition_fee_id INTEGER REFERENCES finance.tuition_fees(id) ON DELETE SET NULL;
                    END IF;

                    -- Đảm bảo ràng buộc UNIQUE cho transaction_ref của payments
                    IF NOT EXISTS (
                        SELECT 1 FROM pg_constraint WHERE conname = 'payments_transaction_ref_key'
                    ) THEN
                        ALTER TABLE finance.payments ADD CONSTRAINT payments_transaction_ref_key UNIQUE (transaction_ref);
                    END IF;
                END $$;
            """))
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"Startup migration warning: {e}")


@app.get("/api/finance/health")
def health_check():
    return {
        "status": "UP",
        "service": "finance-service",
        "version": "2.1.0",
        "framework": "FastAPI (Python 3.11+)"
    }


# ==========================================
# FIN-01: QUẢN LÝ BIỂU PHÍ & VOUCHER
# ==========================================

@app.get("/api/finance/tuition-fees")
def get_tuition_fees(course_id: Optional[int] = None):
    with SessionLocal() as session:
        if course_id is not None:
            query = text("SELECT * FROM finance.tuition_fees WHERE course_id = :course_id ORDER BY created_at DESC")
            rows = session.execute(query, {"course_id": course_id}).mappings().all()
        else:
            query = text("SELECT * FROM finance.tuition_fees ORDER BY created_at DESC")
            rows = session.execute(query).mappings().all()
        return {
            "success": True,
            "data": [dict(r) for r in rows]
        }


@app.post("/api/finance/tuition-fees", status_code=status.HTTP_201_CREATED)
def create_tuition_fee(fee: TuitionFeeCreate):
    if fee.amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="INV_FIN_01_VIOLATION: Mức học phí phải lớn hơn 0"
        )
    if fee.discount_amount > fee.amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="DISCOUNT_ERROR: Số tiền giảm giá không được lớn hơn tổng học phí"
        )

    with SessionLocal() as session:
        query = text("""
            INSERT INTO finance.tuition_fees (course_id, amount, currency, discount_code, discount_amount, note)
            VALUES (:course_id, :amount, :currency, :discount_code, :discount_amount, :note)
            ON CONFLICT (course_id) DO UPDATE 
            SET amount = EXCLUDED.amount,
                currency = EXCLUDED.currency,
                discount_code = EXCLUDED.discount_code,
                discount_amount = EXCLUDED.discount_amount,
                note = EXCLUDED.note
            RETURNING id, course_id, amount, currency, discount_code, discount_amount, note, created_at
        """)
        row = session.execute(query, fee.model_dump()).mappings().first()
        session.commit()
        return {
            "success": True,
            "message": "Lưu biểu phí và mã voucher thành công",
            "data": dict(row)
        }


# ==========================================
# FIN-02: LẬP HÓA ĐƠN QUA TUITION_FEE_ID & THEO DÕI NỢ
# ==========================================

@app.get("/api/finance/invoices")
def get_invoices(student_id: Optional[int] = None):
    with SessionLocal() as session:
        # Tự động chuyển hóa đơn quá hạn sang OVERDUE
        session.execute(text("""
            UPDATE finance.invoices
            SET status = 'OVERDUE'
            WHERE status = 'UNPAID' AND due_date IS NOT NULL AND due_date < CURRENT_DATE
        """))
        session.commit()

        # Truy vấn hóa đơn JOIN sang tuition_fees để lấy thông tin voucher nếu có
        base_sql = """
            SELECT i.*, 
                   tf.discount_code AS tf_discount_code,
                   tf.discount_amount AS tf_discount_amount,
                   COALESCE(SUM(p.amount), 0) AS paid_amount,
                   GREATEST(i.amount - COALESCE(SUM(p.amount), 0), 0) AS remaining_amount
            FROM finance.invoices i
            LEFT JOIN finance.tuition_fees tf ON i.tuition_fee_id = tf.id
            LEFT JOIN finance.payments p ON p.invoice_id = i.id
        """
        if student_id is not None:
            query = text(base_sql + " WHERE i.student_id = :student_id GROUP BY i.id, tf.id ORDER BY i.created_at DESC")
            rows = session.execute(query, {"student_id": student_id}).mappings().all()
        else:
            query = text(base_sql + " GROUP BY i.id, tf.id ORDER BY i.created_at DESC")
            rows = session.execute(query).mappings().all()

        return {
            "success": True,
            "data": [dict(r) for r in rows]
        }


@app.post("/api/finance/invoices", status_code=status.HTTP_201_CREATED)
def create_invoice(inv: InvoiceCreate):
    with SessionLocal() as session:
        final_amount = inv.amount
        resolved_tuition_fee_id = inv.tuition_fee_id

        # Nếu truyền tuition_fee_id, tự động lấy amount (chuẩn trừ giảm giá) từ bảng tuition_fees
        if resolved_tuition_fee_id:
            fee_row = session.execute(
                text("SELECT id, amount, discount_amount FROM finance.tuition_fees WHERE id = :tf_id"),
                {"tf_id": resolved_tuition_fee_id}
            ).mappings().first()

            if not fee_row:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="TUITION_FEE_NOT_FOUND: Không tìm thấy biểu phí tương ứng"
                )
            
            standard_amt = float(fee_row["amount"])
            disc_amt = float(fee_row["discount_amount"] or 0.0)
            calculated_price = max(standard_amt - disc_amt, 0.0)

            if not final_amount or final_amount <= 0:
                final_amount = calculated_price

        # Ràng buộc INV-FIN-01: Số tiền hóa đơn phải > 0
        if not final_amount or final_amount <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="INV_FIN_01_VIOLATION: Giá trị hóa đơn phải lớn hơn 0"
            )

        # Sinh mã hóa đơn INV-xxxx nếu chưa có
        invoice_code = (inv.invoice_code or "").strip()
        if not invoice_code:
            invoice_code = f"INV-{uuid.uuid4().hex[:6].upper()}"

        # Kiểm tra trùng mã hóa đơn
        existing = session.execute(
            text("SELECT id FROM finance.invoices WHERE invoice_code = :code"),
            {"code": invoice_code}
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="DUPLICATE_INVOICE_CODE: Mã hóa đơn đã tồn tại"
            )

        initial_status = "UNPAID"
        if inv.due_date and inv.due_date < date.today():
            initial_status = "OVERDUE"

        query = text("""
            INSERT INTO finance.invoices (
                invoice_code, student_id, enrollment_id, tuition_fee_id, amount, status, due_date
            )
            VALUES (
                :invoice_code, :student_id, :enrollment_id, :tuition_fee_id, :amount, :status, :due_date
            )
            RETURNING id, invoice_code, student_id, enrollment_id, tuition_fee_id, amount, status, due_date, created_at
        """)
        
        row = session.execute(query, {
            "invoice_code": invoice_code,
            "student_id": inv.student_id,
            "enrollment_id": inv.enrollment_id,
            "tuition_fee_id": resolved_tuition_fee_id,
            "amount": final_amount,
            "status": initial_status,
            "due_date": inv.due_date
        }).mappings().first()
        
        session.commit()
        return {
            "success": True,
            "message": "Tạo hóa đơn liên kết biểu phí (tuition_fee_id) thành công",
            "data": dict(row)
        }


# ==========================================
# FIN-03 [Core V2]: GHI NHẬN THANH TOÁN & CHỐNG LẶP
# ==========================================

@app.get("/api/finance/payments")
def get_payments(invoice_id: Optional[int] = None):
    with SessionLocal() as session:
        if invoice_id is not None:
            query = text("SELECT * FROM finance.payments WHERE invoice_id = :invoice_id ORDER BY paid_at DESC")
            rows = session.execute(query, {"invoice_id": invoice_id}).mappings().all()
        else:
            query = text("SELECT * FROM finance.payments ORDER BY paid_at DESC")
            rows = session.execute(query).mappings().all()
        return {
            "success": True,
            "data": [dict(r) for r in rows]
        }


@app.post("/api/finance/payments", status_code=status.HTTP_201_CREATED)
def make_payment(payment: PaymentCreate):
    if payment.amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="INV_FIN_01_VIOLATION: Số tiền thanh toán phải lớn hơn 0"
        )

    tx_ref = payment.transaction_ref.strip()
    if not tx_ref:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="INV_FIN_02_VIOLATION: Mã giao dịch (transaction_ref) không được để trống"
        )

    with SessionLocal() as session:
        # Khóa dòng hóa đơn tránh tranh chấp dữ liệu (Race condition)
        inv_row = session.execute(
            text("SELECT id, amount, status FROM finance.invoices WHERE id = :id FOR UPDATE"),
            {"id": payment.invoice_id}
        ).mappings().first()

        if not inv_row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="INVOICE_NOT_FOUND: Không tìm thấy hóa đơn"
            )

        if inv_row["status"] == "CANCELLED":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="INVOICE_CANCELLED: Không thể thanh toán cho hóa đơn đã hủy"
            )

        # Chống trùng lặp transaction_ref (INV-FIN-02)
        dup_tx = session.execute(
            text("SELECT id FROM finance.payments WHERE transaction_ref = :tx_ref"),
            {"tx_ref": tx_ref}
        ).first()
        if dup_tx:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="INV_FIN_02_DUPLICATE_TX: Mã giao dịch (transaction_ref) đã tồn tại, chặn thu tiền lặp"
            )

        try:
            insert_query = text("""
                INSERT INTO finance.payments (invoice_id, amount, payment_method, transaction_ref)
                VALUES (:invoice_id, :amount, :payment_method, :transaction_ref)
                RETURNING id, invoice_id, amount, payment_method, transaction_ref, paid_at
            """)
            pay_row = session.execute(insert_query, {
                "invoice_id": payment.invoice_id,
                "amount": payment.amount,
                "payment_method": payment.payment_method,
                "transaction_ref": tx_ref
            }).mappings().first()
        except IntegrityError:
            session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="INV_FIN_02_DUPLICATE_TX: Mã giao dịch bị trùng lặp"
            )

        # Kiểm tra tổng tiền đã nộp so với tổng hóa đơn (INV-FIN-03)
        total_paid_row = session.execute(
            text("SELECT COALESCE(SUM(amount), 0) AS total_paid FROM finance.payments WHERE invoice_id = :invoice_id"),
            {"invoice_id": payment.invoice_id}
        ).mappings().first()

        total_paid = float(total_paid_row["total_paid"])
        invoice_amount = float(inv_row["amount"])
        current_status = inv_row["status"]

        if total_paid >= invoice_amount:
            current_status = "PAID"
            session.execute(
                text("UPDATE finance.invoices SET status = 'PAID' WHERE id = :invoice_id"),
                {"invoice_id": payment.invoice_id}
            )

        session.commit()

        result_data = dict(pay_row)
        result_data["total_paid"] = total_paid
        result_data["invoice_amount"] = invoice_amount
        result_data["invoice_status"] = current_status

        return {
            "success": True,
            "message": "Đã thanh toán đủ, hóa đơn chuyển sang PAID" if current_status == "PAID" else f"Đã ghi nhận thanh toán một phần ({total_paid:,.0f}/{invoice_amount:,.0f} VND)",
            "data": result_data
        }
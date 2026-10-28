"""
tests/invariants/test_finance_invariants.py
Kiểm thử các quy tắc bất biến phân hệ Tài chính & Học phí (INV-FIN-01, INV-FIN-02, INV-FIN-03).
Cập nhật hỗ trợ bảng tuition_fees và khóa ngoại tuition_fee_id trong invoices.
"""

import unittest
import sqlite3

class FinanceInvariantsTest(unittest.TestCase):

    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.cur = self.conn.cursor()
        

        self.cur.execute("""
            CREATE TABLE tuition_fees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_id INTEGER NOT NULL UNIQUE,
                amount REAL CHECK (amount > 0.0),
                currency TEXT DEFAULT 'VND',
                discount_code TEXT,
                discount_amount REAL DEFAULT 0.0 CHECK (discount_amount >= 0.0)
            )
        """)


        self.cur.execute("""
            CREATE TABLE invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_code TEXT UNIQUE NOT NULL,
                student_id INTEGER NOT NULL,
                enrollment_id INTEGER,
                tuition_fee_id INTEGER REFERENCES tuition_fees(id),
                amount REAL CHECK (amount > 0.0),
                status TEXT CHECK (status IN ('UNPAID', 'PAID', 'CANCELLED', 'OVERDUE'))
            )
        """)

        self.cur.execute("""
            CREATE TABLE payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_id INTEGER NOT NULL REFERENCES invoices(id) ON DELETE CASCADE,
                amount REAL CHECK (amount > 0.0),
                payment_method TEXT DEFAULT 'BANK_TRANSFER',
                transaction_ref TEXT UNIQUE NOT NULL,
                paid_at TEXT
            )
        """)

    def tearDown(self):
        self.conn.close()

    def test_inv_fin_01_positive_payment_and_invoice_amount(self):
        """INV-FIN-01: Số tiền học phí, thanh toán và biểu phí bắt buộc phải > 0."""
        # Kiểm tra biểu phí <= 0 bị chặn
        with self.assertRaises(sqlite3.IntegrityError):
            self.cur.execute("INSERT INTO tuition_fees (course_id, amount) VALUES (1, 0)")

        # Thêm biểu phí hợp lệ để test hóa đơn
        self.cur.execute("INSERT INTO tuition_fees (course_id, amount, discount_amount) VALUES (10, 6500000, 500000)")
        tf_id = self.cur.lastrowid
        self.conn.commit()

        # Kiểm tra hóa đơn <= 0 bị chặn
        with self.assertRaises(sqlite3.IntegrityError):
            self.cur.execute("INSERT INTO invoices (invoice_code, student_id, tuition_fee_id, amount, status) VALUES ('INV-ERR', 1, ?, 0, 'UNPAID')", (tf_id,))

        # Tạo hóa đơn hợp lệ
        self.cur.execute("INSERT INTO invoices (invoice_code, student_id, tuition_fee_id, amount, status) VALUES ('INV-01', 1, ?, 6000000, 'UNPAID')", (tf_id,))
        inv_id = self.cur.lastrowid
        self.conn.commit()

        # Không được nạp thanh toán <= 0
        with self.assertRaises(sqlite3.IntegrityError):
            self.cur.execute("INSERT INTO payments (invoice_id, amount, transaction_ref) VALUES (?, -1000, 'TX-NEG')", (inv_id,))

        with self.assertRaises(sqlite3.IntegrityError):
            self.cur.execute("INSERT INTO payments (invoice_id, amount, transaction_ref) VALUES (?, 0, 'TX-ZERO')", (inv_id,))

    def test_inv_fin_02_idempotency_transaction_ref(self):
        """INV-FIN-02: Không được ghi nhận cùng một transaction_ref 2 lần (Chống trùng lặp tiền)."""
        self.cur.execute("INSERT INTO invoices (invoice_code, student_id, amount, status) VALUES ('INV-02', 1, 3000000, 'UNPAID')")
        inv_id = self.cur.lastrowid
        self.conn.commit()
        
        # Giao dịch lần 1
        self.cur.execute("INSERT INTO payments (invoice_id, amount, transaction_ref) VALUES (?, 3000000, 'TX-UNIQUE-123')", (inv_id,))
        self.conn.commit()

        # Webhook hoặc submit lặp lại lần 2 với cùng transaction_ref phải bị chặn
        with self.assertRaises(sqlite3.IntegrityError):
            self.cur.execute("INSERT INTO payments (invoice_id, amount, transaction_ref) VALUES (?, 3000000, 'TX-UNIQUE-123')", (inv_id,))

    def test_inv_fin_03_invoice_status_matching_payments(self):
        """INV-FIN-03: Hóa đơn chỉ chuyển sang PAID khi tổng thanh toán >= giá trị hóa đơn."""
        self.cur.execute("INSERT INTO invoices (invoice_code, student_id, amount, status) VALUES ('INV-03', 1, 4000000, 'UNPAID')")
        inv_id = self.cur.lastrowid
        self.conn.commit()

        def record_payment_and_update(invoice_id, pay_amount, ref):
            self.cur.execute("INSERT INTO payments (invoice_id, amount, transaction_ref) VALUES (?, ?, ?)", (invoice_id, pay_amount, ref))
            self.cur.execute("SELECT SUM(amount) FROM payments WHERE invoice_id = ?", (invoice_id,))
            total_paid = self.cur.fetchone()[0] or 0.0

            self.cur.execute("SELECT amount FROM invoices WHERE id = ?", (invoice_id,))
            inv_total = self.cur.fetchone()[0]

            if total_paid >= inv_total:
                self.cur.execute("UPDATE invoices SET status = 'PAID' WHERE id = ?", (invoice_id,))
            self.conn.commit()

        # Đóng một phần (2.000.000 / 4.000.000) -> Chưa PAID (giữ UNPAID)
        record_payment_and_update(inv_id, 2000000, "TX-PART-1")
        self.cur.execute("SELECT status FROM invoices WHERE id = ?", (inv_id,))
        self.assertEqual(self.cur.fetchone()[0], "UNPAID")

        # Đóng nốt 2.000.000 -> Đạt tổng 4.000.000 -> Chuyển sang PAID
        record_payment_and_update(inv_id, 2000000, "TX-PART-2")
        self.cur.execute("SELECT status FROM invoices WHERE id = ?", (inv_id,))
        self.assertEqual(self.cur.fetchone()[0], "PAID")

if __name__ == "__main__":
    unittest.main()
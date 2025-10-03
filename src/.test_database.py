import sqlite3
import pandas as pd
import os
import sys
from tools import run_sql_query
# --- CONFIGURATION ---
TEST_DB_FILE = "test_sales_data.db"
TABLE_NAME = "unified_sales_data"

def setup_db():
    """Tạo database tạm thời và chèn dữ liệu mẫu."""
    conn = sqlite3.connect(TEST_DB_FILE)
    cursor = conn.cursor()

    print(f"Setting up test database: {TEST_DB_FILE}...")
    
    # 1. Tạo bảng với cấu trúc đơn giản hóa
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            id INTEGER PRIMARY KEY,
            date TEXT,
            doc_nbr TEXT,
            route TEXT,
            description TEXT,
            price REAL,
            amount REAL,
            customer_id TEXT
        );
    """)

    # 2. Dữ liệu mẫu (chuyển đổi từ 5 dòng bạn cung cấp)
    test_data = [
        (1, '2025-01-02 00:00:00', 'VJA2FQ5QR', 'HPHVJSGN', '4 PAX VU, HOANG NAM GIANG', 10812400, 10832400, 'KH05234'),
        (2, '2025-01-02 00:00:00', 'VJAS2PSWE', 'SGNVJHAN', '4 PAX VU, HOANG NAM GIANG', 11546800, 11566800, 'KH05234'),
        (3, '2025-01-02 00:00:00', 'VJAUM4QJY', 'HANVJSGNVJHAN', 'NGUYEN, NGOC MINH', 4558000, 4568000, 'KH05234'),
        (4, '2025-01-02 00:00:00', 'VJAYJZCP7', 'CXRVJHANVJCXR', 'HUYNH, THI NHI', 6674800, 6684800, 'EMP1000041'),
        (5, '2025-01-03 00:00:00', 'UNT0103/00954', None, 'VCB - 020097041501030758462025... (Bank Transaction)', 0, -60000000, None),
    ]

    cursor.executemany(f"""
        INSERT INTO {TABLE_NAME} (id, date, doc_nbr, route, description, price, amount, customer_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?);
    """, test_data)
    
    conn.commit()
    conn.close()
    print("Database setup complete.")


def cleanup_db():
    """Xóa file database tạm thời."""
    if os.path.exists(TEST_DB_FILE):
        os.remove(TEST_DB_FILE)
        print(f"Cleanup complete. Removed {TEST_DB_FILE}")

# --- TEST SUITE ---

def test_run_sql_query_functionality():
    """Chạy tất cả các kịch bản kiểm thử cho run_sql_query."""
    print("\n--- Starting run_sql_query Functionality Tests ---")

    # --- CASE 1: TRUY VẤN THÀNH CÔNG (NHIỀU HÀNG/CỘT) ---
    print("\n-- Case 1: Select Multiple Rows and Columns (DataFrame String)")
    query1 = f"SELECT id, doc_nbr, amount FROM {TABLE_NAME} WHERE id <= 3;"
    result1 = run_sql_query(query1)
    
    assert isinstance(result1, str), f"Case 1 Failed: Result type is {type(result1)}, expected str."
    assert "VJA2FQ5QR" in result1, "Case 1 Failed: Missing expected doc_nbr."
    assert "10832400.0" in result1, "Case 1 Failed: Missing expected amount."
    print("    -> Result (Case 1): Success!")

    # --- CASE 2: TRUY VẤN THÀNH CÔNG (GIÁ TRỊ ĐƠN - SCALAR) ---
    print("\n-- Case 2: Select Single Scalar Value (SUM)")
    query2 = f"SELECT SUM(amount) FROM {TABLE_NAME} WHERE id IN (1, 2);"
    result2 = run_sql_query(query2)
    # Tổng của 10832400 + 11566800 = 22399200
    expected_scalar_value = "22399200.0"
    
    assert isinstance(result2, str), f"Case 2 Failed: Result type is {type(result2)}, expected str."
    assert result2 == expected_scalar_value, f"Case 2 Failed: Expected '{expected_scalar_value}', got '{result2}'."
    print("    -> Result (Case 2): Success!")

    # --- CASE 3: TRUY VẤN THAM SỐ HÓA (PARAMETERIZED QUERY) ---
    print("\n-- Case 3: Parameterized Query (Security Check)")
    customer_id = 'EMP1000041'
    query3 = f"SELECT doc_nbr, amount FROM {TABLE_NAME} WHERE customer_id = ?;"
    params3 = (customer_id,)
    
    result3 = run_sql_query(query3, params=params3)
    
    assert 'VJAYJZCP7' in result3, "Case 3 Failed: Missing expected parameterized result."
    assert 'KH05234' not in result3, "Case 3 Failed: Parameterization failed, returned too much data."
    print("    -> Result (Case 3): Success!")

    # --- CASE 4: XỬ LÝ LỖI (LỖI CÚ PHÁP SQL) ---
    print("\n-- Case 4: Query Execution Error Handling (Invalid Column)")
    query4 = f"SELECT non_existent_column FROM {TABLE_NAME};"
    result4 = run_sql_query(query4)

    assert result4.startswith("Query execution error:"), "Case 4 Failed: Did not catch query execution error."
    assert "no such column" in result4, "Case 4 Failed: Error message incorrect."
    print("    -> Result (Case 4): Success!")

    # --- CASE 5: XỬ LÝ DỮ LIỆU ĐẶC BIỆT (NULL VÀ SỐ ÂM) ---
    print("\n-- Case 5: Handling of NULL Values and Negative Numbers")
    query5 = f"SELECT doc_nbr, amount, route FROM {TABLE_NAME} WHERE id = 5;"
    result5 = run_sql_query(query5)

    assert 'UNT0103/00954' in result5, "Case 5 Failed: Missing transaction number."
    assert '-60000000.0' in result5, "Case 5 Failed: Did not handle negative amount correctly."
    assert 'None' in result5, "Case 5 Failed: Did not handle NULL route value correctly (Pandas prints 'None')."
    print("    -> Result (Case 5): Success!")


def run_all_tests():
    """Runs the setup, tests, and cleanup."""
    try:
        setup_db()
        test_run_sql_query_functionality()
        print("\n*** ALL 5 TESTS PASSED SUCCESSFULLY! ***")
    except AssertionError as e:
        print(f"\n*** TEST FAILED! ***")
        print(f"Assertion Error: {e}")
        sys.exit(1)
    finally:
        cleanup_db()

if __name__ == '__main__':
    run_all_tests()

"""
Columnar & Relational Read Projections (Level 0 / Level 2)
Provides high-performance analytical queries over general ledgers and subledgers.
Uses DuckDB when available for SIMD vectorized execution; gracefully falls back
to Python's built-in SQLite3 engine when running in minimal environments.
"""

from typing import List, Dict, Any, Optional
from datetime import date

try:
    import duckdb
    HAS_DUCKDB = True
except ImportError:
    import sqlite3
    HAS_DUCKDB = False


class ReadProjectionsDB:
    """Manages analytical query projections with DuckDB and SQLite3 fallback."""

    def __init__(self, database_path: str = ":memory:"):
        self.db_path = database_path
        self.has_duckdb = HAS_DUCKDB
        
        if self.has_duckdb:
            self._conn = duckdb.connect(database_path)
        else:
            self._conn = sqlite3.connect(database_path)
            
        self._initialize_schema()

    def _initialize_schema(self):
        """Initializes tables with proper schema."""
        schema_sql = """
            CREATE TABLE IF NOT EXISTS gl_transactions (
                transaction_id TEXT,
                journal_entry_id TEXT,
                effective_date TEXT,
                sim_month INTEGER,
                sim_year INTEGER,
                account_number TEXT,
                account_name TEXT,
                account_category TEXT,
                debit_amount REAL,
                credit_amount REAL,
                entity_name TEXT,
                memo TEXT,
                document_ref TEXT
            );
            
            CREATE TABLE IF NOT EXISTS trial_balance_snapshots (
                period_code TEXT,
                sim_year INTEGER,
                sim_month INTEGER,
                account_number TEXT,
                account_name TEXT,
                account_category TEXT,
                total_debits REAL,
                total_credits REAL,
                net_balance REAL
            );
        """
        if self.has_duckdb:
            self._conn.execute(schema_sql)
        else:
            self._conn.executescript(schema_sql)
            self._conn.commit()

    def insert_transaction_batch(self, rows: List[tuple]):
        """Bulk inserts transactions using DuckDB Appender or SQLite executemany."""
        # Convert date objects to ISO format strings for compatibility
        formatted_rows = []
        for r in rows:
            r_list = list(r)
            if isinstance(r_list[2], date):
                r_list[2] = r_list[2].isoformat()
            formatted_rows.append(tuple(r_list))

        if self.has_duckdb:
            appender = self._conn.appender("gl_transactions")
            for row in formatted_rows:
                appender.append(row)
            appender.flush()
        else:
            insert_sql = """
                INSERT INTO gl_transactions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            self._conn.executemany(insert_sql, formatted_rows)
            self._conn.commit()

    def get_trial_balance(self, sim_year: int, sim_month: int) -> List[Dict[str, Any]]:
        """Queries aggregated account balances for a specific monthly period."""
        query = """
            SELECT 
                account_number,
                account_name,
                account_category,
                SUM(debit_amount) AS total_debits,
                SUM(credit_amount) AS total_credits,
                SUM(debit_amount - credit_amount) AS net_balance
            FROM gl_transactions
            WHERE sim_year = ? AND sim_month = ?
            GROUP BY account_number, account_name, account_category
            ORDER BY account_number;
        """
        cursor = self._conn.execute(query, [sim_year, sim_month])
        rows = cursor.fetchall()
        columns = ["account_number", "account_name", "account_category", "total_debits", "total_credits", "net_balance"]
        return [dict(zip(columns, row)) for row in rows]

    def get_monthly_revenue_and_cogs(self, start_year: int, end_year: int) -> List[Dict[str, Any]]:
        """Rolls up monthly Revenue and COGS across multiple years for EBITDA bridge analysis."""
        query = """
            SELECT 
                sim_year,
                sim_month,
                SUM(CASE WHEN account_category = 'REVENUE' THEN credit_amount - debit_amount ELSE 0 END) AS monthly_revenue,
                SUM(CASE WHEN account_category = 'COGS' THEN debit_amount - credit_amount ELSE 0 END) AS monthly_cogs,
                SUM(CASE WHEN account_category = 'OPEX' THEN debit_amount - credit_amount ELSE 0 END) AS monthly_opex
            FROM gl_transactions
            WHERE sim_year BETWEEN ? AND ?
            GROUP BY sim_year, sim_month
            ORDER BY sim_year, sim_month;
        """
        cursor = self._conn.execute(query, [start_year, end_year])
        rows = cursor.fetchall()
        columns = ["sim_year", "sim_month", "revenue", "cogs", "opex"]
        return [dict(zip(columns, row)) for row in rows]

    def close(self):
        """Closes database connection."""
        self._conn.close()

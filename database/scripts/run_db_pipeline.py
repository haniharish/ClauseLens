"""ClauseLens Database Pipeline Runner.

Executes schema creation, demonstration seed scripts, verification, and SQL
test suites against PostgreSQL using environment variables from `.env`.
No database passwords are stored in code.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys

try:
    from dotenv import load_dotenv
    import psycopg
except ImportError as exc:  # pragma: no cover - runtime dependency check
    print(
        f"Missing required Python package: {exc}. "
        "Install with: pip install -r database/requirements.txt",
        file=sys.stderr,
    )
    sys.exit(1)

DATABASE_ROOT = Path(__file__).resolve().parent.parent

SCHEMA_FILES = [
    DATABASE_ROOT / "schema" / "01_users.sql",
    DATABASE_ROOT / "schema" / "02_profiles.sql",
    DATABASE_ROOT / "schema" / "03_documents.sql",
    DATABASE_ROOT / "schema" / "04_clauses.sql",
    DATABASE_ROOT / "schema" / "05_analysis_results.sql",
    DATABASE_ROOT / "schema" / "06_personalized_risks.sql",
    DATABASE_ROOT / "schema" / "07_policy_versions.sql",
    DATABASE_ROOT / "schema" / "08_policy_changes.sql",
    DATABASE_ROOT / "schema" / "09_notifications.sql",
    DATABASE_ROOT / "schema" / "10_monitoring.sql",
]

SEED_FILES = [
    DATABASE_ROOT / "seed" / "sample_users.sql",
    DATABASE_ROOT / "seed" / "sample_documents.sql",
    DATABASE_ROOT / "seed" / "sample_clauses.sql",
    DATABASE_ROOT / "seed" / "sample_versions.sql",
]

TEST_FILES = [
    DATABASE_ROOT / "tests" / "test_constraints.sql",
    DATABASE_ROOT / "tests" / "test_relationships.sql",
    DATABASE_ROOT / "tests" / "test_queries.sql",
]


def get_connection_dsn() -> str:
    """Build PostgreSQL DSN from environment variables without hardcoded secrets."""
    load_dotenv(DATABASE_ROOT / ".env")
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return database_url

    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    dbname = os.getenv("DB_NAME", "clauselens_db")
    user = os.getenv("DB_USER", "postgres")
    password = os.getenv("DB_PASSWORD")
    if not password:
        raise RuntimeError(
            "DB_PASSWORD (or DATABASE_URL) must be set in environment or database/.env."
        )
    return f"postgresql://{user}:{password}@{host}:{port}/{dbname}"


def execute_sql_files(conn: psycopg.Connection, files: list[Path], label: str) -> None:
    """Execute a list of SQL files in order."""
    print(f"--- Running {label} ---")
    for sql_file in files:
        print(f"Executing {sql_file.relative_to(DATABASE_ROOT)} ...")
        sql_text = sql_file.read_text(encoding="utf-8")
        conn.execute(sql_text)
        conn.commit()
    print(f"Completed {label}.")


def main() -> int:
    parser = argparse.ArgumentParser(description="ClauseLens PostgreSQL Runner")
    parser.add_argument("--schema", action="store_true", help="Apply schema DDL scripts")
    parser.add_argument("--seed", action="store_true", help="Load demonstration seed data")
    parser.add_argument("--test", action="store_true", help="Run SQL validation suites")
    parser.add_argument("--all", action="store_true", help="Run schema, seed, and tests")
    args = parser.parse_args()

    if not any([args.schema, args.seed, args.test, args.all]):
        parser.print_help()
        return 1

    dsn = get_connection_dsn()
    with psycopg.connect(dsn, autocommit=False) as conn:
        if args.all or args.schema:
            execute_sql_files(conn, SCHEMA_FILES, "Schema DDL")
        if args.all or args.seed:
            execute_sql_files(conn, SEED_FILES, "Demonstration Seed Data")
        if args.all or args.test:
            execute_sql_files(conn, TEST_FILES, "SQL Validation Tests")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

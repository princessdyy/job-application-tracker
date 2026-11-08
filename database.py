import os
import json
import sqlite3
from dotenv import load_dotenv

# Optional MySQL Connector import
try:
    import mysql.connector
    from mysql.connector import Error as MySQLError
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False
    MySQLError = Exception

SQLITE_PATH = os.path.join(os.path.dirname(__file__), 'job_tracker_preview.db')


def get_db_config():
    """Dynamically loads configuration from .env or defaults to root/root."""
    load_dotenv(override=True)
    return {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': int(os.getenv('DB_PORT', 3306)),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', 'root'),
        'database': os.getenv('DB_NAME', 'job_tracker')
    }


def test_mysql_connection():
    """Verify MySQL connectivity with current credentials."""
    if not MYSQL_AVAILABLE:
        return False, "mysql-connector-python package not installed"
    cfg = get_db_config()
    try:
        conn = mysql.connector.connect(
            host=cfg['host'],
            port=cfg['port'],
            user=cfg['user'],
            password=cfg['password'],
            database=cfg['database'],
            charset='utf8mb4',
            connection_timeout=2
        )
        if conn.is_connected():
            cursor = conn.cursor()
            cursor.execute("SELECT DATABASE(), VERSION()")
            db, ver = cursor.fetchone()
            cursor.close()
            conn.close()
            return True, f"Connected to MySQL {ver} ({db})"
        return False, "MySQL connection refused."
    except Exception as e:
        return False, str(e)


def test_connection():
    """Check database status (MySQL primary, SQLite local preview fallback)."""
    is_mysql, msg = test_mysql_connection()
    if is_mysql:
        return True, msg
    if os.path.exists(SQLITE_PATH):
        return True, "Local Preview Mode (MySQL offline; using SQLite demo data)"
    return False, msg


def get_db_diagnostics():
    """Returns database diagnostic info for inspector modal."""
    cfg = get_db_config()
    is_mysql, msg = test_mysql_connection()
    if is_mysql:
        try:
            conn = mysql.connector.connect(
                host=cfg['host'], port=cfg['port'], user=cfg['user'], password=cfg['password'], database=cfg['database'], connection_timeout=2
            )
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT VERSION() AS ver, DATABASE() AS cur_db")
            info = cursor.fetchone()
            cursor.execute("SELECT (SELECT COUNT(*) FROM companies) AS companies, (SELECT COUNT(*) FROM jobs) AS jobs, (SELECT COUNT(*) FROM applications) AS applications, (SELECT COUNT(*) FROM contacts) AS contacts")
            counts = cursor.fetchone()
            cursor.close()
            conn.close()
            ver_str = info['ver'] if info and 'ver' in info else '8.0'
            return {
                'is_mysql': True,
                'engine': f"MySQL {ver_str}",
                'database': cfg['database'],
                'host': f"{cfg['host']}:{cfg['port']}",
                'user': cfg['user'],
                'status': 'Online & Healthy',
                'counts': counts or {'companies': 0, 'jobs': 0, 'applications': 0, 'contacts': 0}
            }
        except Exception:
            pass
    return {
        'is_mysql': False,
        'engine': 'SQLite Preview',
        'database': 'job_tracker_preview.db',
        'host': 'Local Disk',
        'user': 'Local User',
        'status': 'Preview Mode',
        'counts': {'companies': 4, 'jobs': 5, 'applications': 4, 'contacts': 4}
    }


def query_db(query, args=(), one=False):
    """Execute a SELECT query and return rows as dictionaries."""
    cfg = get_db_config()
    is_mysql, _ = test_mysql_connection()
    if is_mysql:
        conn = mysql.connector.connect(
            host=cfg['host'], port=cfg['port'], user=cfg['user'], password=cfg['password'], database=cfg['database'], charset='utf8mb4'
        )
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(query, args)
            rows = cursor.fetchall()
            return (rows[0] if rows else None) if one else rows
        finally:
            cursor.close()
            conn.close()
    else:
        conn = sqlite3.connect(SQLITE_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        try:
            sqlite_query = query.replace('%s', '?')
            cursor.execute(sqlite_query, args)
            rows = [dict(row) for row in cursor.fetchall()]
            return (rows[0] if rows else None) if one else rows
        finally:
            cursor.close()
            conn.close()


def execute_db(query, args=(), return_id=False):
    """Execute an INSERT, UPDATE, or DELETE query."""
    cfg = get_db_config()
    is_mysql, _ = test_mysql_connection()
    if is_mysql:
        conn = mysql.connector.connect(
            host=cfg['host'], port=cfg['port'], user=cfg['user'], password=cfg['password'], database=cfg['database'], charset='utf8mb4'
        )
        cursor = conn.cursor()
        try:
            cursor.execute(query, args)
            conn.commit()
            last_id = cursor.lastrowid
            return last_id if return_id else cursor.rowcount
        except MySQLError as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()
    else:
        conn = sqlite3.connect(SQLITE_PATH)
        cursor = conn.cursor()
        try:
            sqlite_query = query.replace('%s', '?')
            cursor.execute(sqlite_query, args)
            conn.commit()
            last_id = cursor.lastrowid
            return last_id if return_id else cursor.rowcount
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()

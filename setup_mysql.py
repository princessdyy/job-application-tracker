import os
import sys
from dotenv import load_dotenv

load_dotenv()

# Passwords to try automatically
DEFAULT_PASSWORDS_TO_TRY = [
    'root',
    os.getenv('DB_PASSWORD', 'root'),
    '',
    'password',
    'admin',
    '123456',
    'root123',
    'password123'
]

def find_mysql_connection():
    try:
        import mysql.connector
    except ImportError:
        print("[ERROR] mysql-connector-python is not installed. Please run: pip install mysql-connector-python")
        return None, None

    print("[1/3] Connecting to MySQL Server...")
    
    for pwd in DEFAULT_PASSWORDS_TO_TRY:
        try:
            conn = mysql.connector.connect(
                host='localhost',
                port=3306,
                user='root',
                password=pwd,
                connection_timeout=2
            )
            if conn.is_connected():
                print(f"[SUCCESS] Connected to MySQL as 'root' with password: '{pwd}'")
                return conn, pwd
        except Exception:
            continue

    print("\n[!] Could not connect with 'root' or default passwords.")
    custom_pwd = input("Please enter your MySQL root password: ").strip()
    try:
        conn = mysql.connector.connect(
            host='localhost',
            port=3306,
            user='root',
            password=custom_pwd,
            connection_timeout=3
        )
        if conn.is_connected():
            print("[SUCCESS] Connected to MySQL Server!")
            return conn, custom_pwd
    except Exception as e:
        print(f"[FAILED] Could not connect to MySQL: {e}")
        return None, None


def run_schema(conn, password):
    schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
    if not os.path.exists(schema_path):
        print(f"[ERROR] schema.sql not found at {schema_path}")
        return False

    print("[2/3] Reading schema.sql and creating database...")
    with open(schema_path, 'r', encoding='utf-8') as f:
        sql_content = f.read()

    # Clean out comment lines (-- ...) while preserving the actual SQL queries
    clean_lines = []
    for line in sql_content.splitlines():
        stripped_line = line.strip()
        if not stripped_line.startswith('--'):
            clean_lines.append(line)
    clean_sql = '\n'.join(clean_lines)

    # Split into individual clean statements
    statements = [stmt.strip() for stmt in clean_sql.split(';') if stmt.strip()]

    cursor = conn.cursor()
    executed_count = 0
    try:
        for stmt in statements:
            cursor.execute(stmt)
            executed_count += 1
            
        conn.commit()
        print(f"[SUCCESS] Executed all {executed_count} SQL statements successfully!")
    except Exception as e:
        print(f"[ERROR during SQL execution]: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

    # Save to .env
    print("[3/3] Saving configuration to .env...")
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    env_content = f"""# MySQL Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD={password}
DB_NAME=job_tracker

# Flask Configuration
SECRET_KEY=fiu-course-project-secret-key-2026
"""
    with open(env_path, 'w', encoding='utf-8') as f:
        f.write(env_content)

    print("\n" + "="*60)
    print("ALL DONE! Your MySQL 'job_tracker' database is 100% created!")
    print("All 4 tables (companies, jobs, applications, contacts) are seeded.")
    print("="*60 + "\n")
    return True


if __name__ == '__main__':
    conn, working_password = find_mysql_connection()
    if conn:
        success = run_schema(conn, working_password)
        if success:
            sys.exit(0)
    print("\n[!] Setup incomplete.")
    sys.exit(1)

import sqlite3
import os

DB_PATH = "ai_money_manager.db"
BACKUP_PATH = "ai_money_manager.db.backup"


def migrate():
    if not os.path.exists(DB_PATH):
        print("No existing database found. Fresh database will be created on startup.")
        return

    # Backup
    if not os.path.exists(BACKUP_PATH):
        import shutil
        shutil.copy(DB_PATH, BACKUP_PATH)
        print(f"Backup created: {BACKUP_PATH}")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Helper to check if column exists
    def column_exists(table, column):
        cursor.execute(f"PRAGMA table_info({table})")
        return any(col[1] == column for col in cursor.fetchall())

    # Helper to check if table exists
    def table_exists(table):
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
        return cursor.fetchone() is not None

    def rebuild_users_table():
        print("Rebuilding users table to match current schema...")
        desired_columns = [
            ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),
            ("email", "TEXT UNIQUE NOT NULL DEFAULT ''"),
            ("password_hash", "TEXT NOT NULL DEFAULT ''"),
            ("name", "TEXT NOT NULL"),
            ("salary", "NUMERIC(12,2) DEFAULT 0.00"),
            ("currency", "TEXT DEFAULT 'INR'"),
            ("country", "TEXT"),
            ("occupation", "TEXT"),
            ("risk_profile", "TEXT DEFAULT 'moderate'"),
            ("is_verified", "INTEGER DEFAULT 0"),
            ("onboarding_complete", "INTEGER DEFAULT 0"),
            ("reset_token", "TEXT"),
            ("reset_token_expiry", "TIMESTAMP"),
            ("created_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"),
            ("updated_at", "TIMESTAMP"),
            ("is_active", "INTEGER DEFAULT 1"),
            ("is_admin", "INTEGER DEFAULT 0"),
            ("ai_preferences", "TEXT"),
            ("ai_memory", "TEXT"),
        ]

        existing = [col[1] for col in cursor.execute("PRAGMA table_info(users)").fetchall()]
        select_list = []
        for col_name, _ in desired_columns:
            if col_name in existing:
                if col_name == "email":
                    select_list.append("COALESCE(email, 'user' || id || '@example.com') AS email")
                elif col_name == "password_hash":
                    select_list.append("COALESCE(password_hash, '') AS password_hash")
                elif col_name == "salary":
                    select_list.append("COALESCE(salary, 0.0) AS salary")
                elif col_name == "currency":
                    select_list.append("COALESCE(currency, 'INR') AS currency")
                elif col_name == "risk_profile":
                    select_list.append("COALESCE(risk_profile, 'moderate') AS risk_profile")
                elif col_name == "is_verified":
                    select_list.append("COALESCE(is_verified, 0) AS is_verified")
                elif col_name == "onboarding_complete":
                    select_list.append("COALESCE(onboarding_complete, 0) AS onboarding_complete")
                elif col_name == "is_active":
                    select_list.append("COALESCE(is_active, 1) AS is_active")
                else:
                    select_list.append(col_name)
            else:
                if col_name == "email":
                    select_list.append("'user' || id || '@example.com' AS email")
                elif col_name == "password_hash":
                    select_list.append("'' AS password_hash")
                elif col_name == "salary":
                    select_list.append("0.0 AS salary")
                elif col_name == "currency":
                    select_list.append("'INR' AS currency")
                elif col_name == "risk_profile":
                    select_list.append("'moderate' AS risk_profile")
                elif col_name == "is_verified":
                    select_list.append("0 AS is_verified")
                elif col_name == "onboarding_complete":
                    select_list.append("0 AS onboarding_complete")
                elif col_name == "is_active":
                    select_list.append("1 AS is_active")
                elif col_name == "is_admin":
                    select_list.append("0 AS is_admin")
                elif col_name == "created_at":
                    select_list.append("CURRENT_TIMESTAMP AS created_at")
                elif col_name == "updated_at":
                    select_list.append("CURRENT_TIMESTAMP AS updated_at")
                else:
                    select_list.append("NULL AS %s" % col_name)

        cursor.execute("CREATE TABLE users_new (" + ", ".join([f"{name} {col_type}" for name, col_type in desired_columns]) + ")")
        cursor.execute(
            "INSERT INTO users_new (" + ", ".join([name for name, _ in desired_columns]) + ") "
            "SELECT " + ", ".join(select_list) + " FROM users"
        )
        cursor.execute("DROP TABLE users")
        cursor.execute("ALTER TABLE users_new RENAME TO users")
        print("Rebuilt users table successfully.")

    tables = ["users", "expenses", "investments", "loans", "goals"]
    essential_user_columns = ["email", "password_hash", "is_admin"]
    if table_exists("users") and any(not column_exists("users", col) for col in essential_user_columns):
        cursor.execute("PRAGMA foreign_keys=OFF")
        rebuild_users_table()
        cursor.execute("PRAGMA foreign_keys=ON")

    new_columns = {
        "users": [
            ("email", "TEXT UNIQUE"),
            ("password_hash", "TEXT DEFAULT ''"),
            ("currency", "TEXT DEFAULT 'INR'"),
            ("country", "TEXT"),
            ("occupation", "TEXT"),
            ("risk_profile", "TEXT DEFAULT 'moderate'"),
            ("is_verified", "INTEGER DEFAULT 0"),
            ("onboarding_complete", "INTEGER DEFAULT 0"),
            ("reset_token", "TEXT"),
            ("reset_token_expiry", "TIMESTAMP"),
            ("ai_preferences", "TEXT"),
            ("ai_memory", "TEXT"),
            ("updated_at", "TIMESTAMP"),
            ("is_active", "INTEGER DEFAULT 1"),
            ("is_admin", "INTEGER DEFAULT 0"),
        ],
        "expenses": [
            ("updated_at", "TIMESTAMP"),
            ("is_deleted", "INTEGER DEFAULT 0"),
            ("deleted_at", "TIMESTAMP"),
        ],
        "investments": [
            ("updated_at", "TIMESTAMP"),
            ("is_deleted", "INTEGER DEFAULT 0"),
            ("deleted_at", "TIMESTAMP"),
        ],
        "loans": [
            ("updated_at", "TIMESTAMP"),
            ("is_deleted", "INTEGER DEFAULT 0"),
            ("deleted_at", "TIMESTAMP"),
        ],
        "goals": [
            ("updated_at", "TIMESTAMP"),
            ("is_deleted", "INTEGER DEFAULT 0"),
            ("deleted_at", "TIMESTAMP"),
        ],
    }

    for table in tables:
        if not table_exists(table):
            continue
        for col_name, col_type in new_columns.get(table, []):
            if not column_exists(table, col_name):
                try:
                    cursor.execute(f"ALTER TABLE {table} ADD COLUMN {col_name} {col_type}")
                    print(f"Added column '{col_name}' to '{table}'")
                except Exception as e:
                    print(f"Warning: Could not add '{col_name}' to '{table}': {e}")

    # Create budgets table if not exists
    if not table_exists("budgets"):
        cursor.execute("""
            CREATE TABLE budgets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                category TEXT NOT NULL,
                budget_amount NUMERIC(12,2) NOT NULL,
                month INTEGER NOT NULL,
                year INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP,
                is_deleted INTEGER DEFAULT 0,
                deleted_at TIMESTAMP
            )
        """)
        print("Created table 'budgets'")

    # Create notifications table if not exists
    if not table_exists("notifications"):
        cursor.execute("""
            CREATE TABLE notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                type TEXT NOT NULL,
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                severity TEXT DEFAULT 'info',
                is_read INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("Created table 'notifications'")

    # Set default email for existing users if email is NULL
    if table_exists("users") and column_exists("users", "email"):
        try:
            cursor.execute("UPDATE users SET email = 'user' || id || '@example.com' WHERE email IS NULL OR email = ''")
            if cursor.rowcount > 0:
                print(f"Updated {cursor.rowcount} existing users with default emails")
        except Exception as e:
            print(f"Note: Could not update user emails: {e}")

    # Set default password for existing users
    if table_exists("users") and column_exists("users", "password_hash"):
        try:
            cursor.execute("UPDATE users SET password_hash = '$2b$12$placeholder' WHERE password_hash IS NULL OR password_hash = ''")
        except Exception as e:
            print(f"Note: Could not update user passwords: {e}")

    # Update existing date strings to proper format if needed
    # SQLite is flexible, but let's ensure expense_date is parseable
    for table in ["expenses", "investments", "loans", "goals"]:
        if not table_exists(table):
            continue
        date_col = "expense_date" if table == "expenses" else "start_date" if table in ["investments", "loans"] else "target_date"
        if column_exists(table, date_col):
            try:
                cursor.execute(f"UPDATE {table} SET {date_col} = {date_col}")
            except Exception as e:
                print(f"Note: Date format in '{table}' may need manual check: {e}")

    conn.commit()
    conn.close()
    print("Migration completed successfully!")
    print("\nNext steps:")
    print("1. Review the backup at ai_money_manager.db.backup")
    print("2. Start the backend: uvicorn main:app --reload")
    print("3. Start the frontend: npm run dev")


if __name__ == "__main__":
    migrate()
